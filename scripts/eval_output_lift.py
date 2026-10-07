#!/usr/bin/env python3
"""Output-lift eval suite: does the skill that fired actually produce a better answer?

`scripts/eval_routing.py` tests *which* skill owns a request. Nothing tested what the skill
then produced, so a skill could route perfectly and still return a brief with a section
missing, or a "de-slopped" draft that baseline Claude would have written identically. That
gap is named in `docs/skill-evals.md` under "Extending the layer".

This closes it with the with-skill-vs-baseline pattern: run the same prompt twice, once with
the skill body loaded and once bare, score both against the same criteria, and report the
gap. A skill whose lift is zero is not earning the context it costs.

Adapted from the eval harness in DreambigOu/ELI5 (MIT), which is the clearest small
implementation of the pattern. Six things changed on the way in. The first four match a rule
this repo already holds; the last two are what running it taught us.

1. **An offline tier exists.** The original can only run by calling a model, so it can never
   gate a PR. Here the default mode is a stdlib-only structural check over the suite, which
   is what CI runs. Model calls happen only under `--run`.
2. **Deterministic checks run before any model call.** A case can carry regex and
   length gates that are scored offline; only the prose assertions reach a grader. That is
   `docs/skill-evals.md`, "deterministic checks first, model calls only for what
   deterministic checks cannot answer", applied literally.
3. **The grader is not the model under test.** `--run` requires `--subject-model` and
   `--grader-model` and refuses when they match. Filed in `docs/skill-evals.md` from the
   Lauren Tan agent workshop, 2026-08-29, and unimplemented until now.
4. **Run outputs are not committed.** The original versions `iteration-N/` into the repo.
   Model output is live data; this repo keeps pointers, not copies. Runs land in
   `evals/runs/`, which is gitignored.
5. **Each arm runs in its own empty sandbox** with the skill copied in, never from the repo
   root. Run from here, the baseline arm would load `CLAUDE.md` and arrive carrying most of
   what the skill was supposed to add. See `open_sandbox`.
6. **Checks declare a scope.** A forbidden-word scan over a whole response punishes a
   de-slopping skill for naming the slop it removed, which is the work. See `SCOPES`.

Usage:
    python3 scripts/eval_output_lift.py                    # structural checks (CI, offline)
    python3 scripts/eval_output_lift.py --list             # show the suite
    python3 scripts/eval_output_lift.py --json             # machine-readable
    python3 scripts/eval_output_lift.py --run \
        --subject-model claude-opus-5 --grader-model claude-sonnet-5
    python3 scripts/eval_output_lift.py --run --case ste-status-update-strips-slop
    python3 scripts/eval_output_lift.py --grade-only --grader-model claude-sonnet-5

Exits 1 on any structural failure, in every output mode, and on any failed model call or
missing response under `--run` / `--grade-only`. Emits GitHub Actions `::error` annotations
pinned to the offending suite line. Stdlib only. Run from the repo root.
"""

from __future__ import annotations

import argparse
import contextlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

from eval_routing import EvalError, load_skills

SKILLS_DIR = Path(".claude/skills")
SUITE = Path("evals/output_lift.jsonl")
RUNS_DIR = Path("evals/runs")

# Every key a `checks` block may carry. An unknown key is a structural failure rather than a
# silent no-op: a typo'd `max_word` that quietly stops gating is the worst outcome here,
# because the suite keeps reporting green while checking less than it claims.
CHECK_KEYS = {"required", "forbidden", "max_words", "max_sentence_words", "scope"}

# What a check measures. "response" is everything the model returned. "unquoted" first
# removes fenced code, backticked spans and quoted spans, so a check measures what the
# skill WROTE rather than what it CITED. Run 1 of this suite scored ste at -11.8 lift
# purely because the skill did its job and then quoted the slop it had removed in a
# change log, tripping every forbidden pattern. A de-slopping skill must not USE the
# phrase; it is allowed, and often required, to name it. "deliverable" goes further and
# scores only a fenced block tagged `deliverable`, which is the right target whenever the
# skill's analysis legitimately names the thing the check forbids: de-ai answers the same
# prompt with a triage TABLE of the tells it found, and every cell trips a forbidden-word
# scan no matter how the quoting is handled. A case using this scope must ask for the block
# in its prompt.
SCOPES = ("response", "unquoted", "deliverable")

REQUIRED_FIELDS = ("case", "skill", "prompt", "why")

# Fenced code is excluded from prose length counts. A skill that correctly returns a code
# block should not fail a word ceiling written for prose.
FENCE_RE = re.compile(r"```.*?```", re.DOTALL)

# Quoted spans, for `scope: "unquoted"`. The single-quote arm is deliberately conservative:
# it requires a non-letter on both sides so an apostrophe inside "don't" cannot open a span
# and swallow the rest of the line.
DELIVERABLE_RE = re.compile(r"```deliverable\s*\n(.*?)```", re.DOTALL | re.IGNORECASE)

QUOTED_RE = re.compile(
    r"`[^`]*`"
    r'|"[^"\n]*"'
    r"|\u201c[^\u201d]*\u201d"
    r"|(?<![A-Za-z])'[^'\n]{2,}?'(?![A-Za-z])"
)
SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")
CASE_NAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")


# --------------------------------------------------------------------------- suite loading


def load_suite(path: Path = SUITE) -> tuple[list[dict], list[EvalError]]:
    """Read the JSONL suite. Returns (cases, structural errors).

    Mirrors `eval_routing.load_suite`: `//` comments and blank lines are skipped, every case
    carries the line it came from so an annotation can pin to it, and a malformed line yields
    a located error rather than a traceback.
    """
    errors: list[EvalError] = []
    cases: list[dict] = []
    if not path.exists():
        return cases, [EvalError("suite not found", path)]

    seen: dict[str, int] = {}
    for lineno, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("//"):
            continue
        try:
            case = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(EvalError(f"not valid JSON ({exc.msg})", path, lineno))
            continue

        if not isinstance(case, dict):
            errors.append(
                EvalError(f"case must be a JSON object, got {type(case).__name__}", path, lineno)
            )
            continue

        bad = next(
            (
                field
                for field in REQUIRED_FIELDS
                if not isinstance(case.get(field), str) or not case[field].strip()
            ),
            None,
        )
        if bad:
            errors.append(EvalError(f"'{bad}' must be a non-empty string", path, lineno))
            continue

        name = case["case"].strip()
        if not CASE_NAME_RE.match(name):
            errors.append(
                EvalError(
                    f"case name '{name}' must be lowercase letters, digits and hyphens "
                    "(it becomes a directory under evals/runs/)",
                    path,
                    lineno,
                )
            )
            continue
        if name in seen:
            errors.append(
                EvalError(f"duplicate case name (first seen line {seen[name]})", path, lineno)
            )
            continue
        seen[name] = lineno

        case["case"] = name
        case["skill"] = case["skill"].strip()
        case["prompt"] = case["prompt"].strip()
        # `.get(key, default)`, never `.get(key) or default`: the `or` form silently
        # converts a malformed `false`, `0` or `""` into a valid empty collection, so a case
        # whose other scoring field is fine passes validation while scoring less than it
        # claims. That is this suite's own worst failure mode, one level up.
        case["checks"] = case.get("checks", {})
        case["assertions"] = case.get("assertions", [])
        case["line"] = lineno
        cases.append(case)
    return cases, errors


def validate(cases: list[dict], skills: dict[str, str]) -> list[EvalError]:
    """Structural problems that only show up once the suite is read against the repo."""
    errors: list[EvalError] = []
    for case in cases:
        line = case["line"]

        if case["skill"] not in skills:
            errors.append(
                EvalError(
                    f"case '{case['case']}' expects skill '{case['skill']}', which does not "
                    "exist (expects the frontmatter name:, not the directory)",
                    SUITE,
                    line,
                )
            )

        checks, assertions = case["checks"], case["assertions"]

        if not isinstance(checks, dict):
            errors.append(EvalError("'checks' must be an object", SUITE, line))
            checks = {}
        if not isinstance(assertions, list) or not all(
            isinstance(a, str) and a.strip() for a in assertions
        ):
            errors.append(EvalError("'assertions' must be a list of non-empty strings", SUITE, line))
            assertions = []

        if not checks and not assertions:
            errors.append(
                EvalError(
                    f"case '{case['case']}' has neither checks nor assertions, so it scores "
                    "nothing",
                    SUITE,
                    line,
                )
            )

        for key in set(checks) - CHECK_KEYS:
            errors.append(
                EvalError(
                    f"unknown check '{key}' (known: {', '.join(sorted(CHECK_KEYS))})", SUITE, line
                )
            )

        for key in ("required", "forbidden"):
            patterns = checks.get(key, [])
            if not isinstance(patterns, list):
                errors.append(EvalError(f"'checks.{key}' must be a list", SUITE, line))
                continue
            for pattern in patterns:
                if not isinstance(pattern, str) or not pattern:
                    errors.append(
                        EvalError(f"'checks.{key}' entries must be non-empty strings", SUITE, line)
                    )
                    continue
                try:
                    re.compile(pattern)
                except re.error as exc:
                    errors.append(
                        EvalError(f"'checks.{key}' pattern {pattern!r} does not compile: {exc}",
                                  SUITE, line)
                    )

        scope = checks.get("scope", "response")
        if scope not in SCOPES:
            errors.append(
                EvalError(f"'checks.scope' must be one of {', '.join(SCOPES)}, got {scope!r}",
                          SUITE, line)
            )

        for key in ("max_words", "max_sentence_words"):
            if key not in checks:
                continue
            limit = checks[key]
            # `bool` is a subclass of `int`, so `isinstance(True, int)` is True and a
            # `"max_words": true` would sail through as a one-word ceiling.
            if isinstance(limit, bool) or not isinstance(limit, int) or limit <= 0:
                errors.append(EvalError(f"'checks.{key}' must be a positive integer", SUITE, line))

    return errors


# ------------------------------------------------------------------- deterministic scoring


def prose_of(text: str) -> str:
    """The response with fenced code removed, for length measurement."""
    return FENCE_RE.sub(" ", text)


def in_scope(text: str, scope: str) -> str | None:
    """Narrow a response to what a check should measure. See SCOPES.

    Returns None when the scope is `deliverable` and the response carries no such block,
    which `run_checks` reports as a single located failure rather than scoring an empty
    string (where every forbidden pattern would trivially pass).
    """
    if scope == "unquoted":
        return QUOTED_RE.sub(" ", FENCE_RE.sub(" ", text))
    if scope == "deliverable":
        blocks = DELIVERABLE_RE.findall(text)
        return "\n".join(blocks) if blocks else None
    return text


def word_count(text: str) -> int:
    """Prose words in a response, fenced code excluded."""
    return len(prose_of(text).split())


def longest_sentence(text: str) -> tuple[int, str]:
    """(word count, text) of the longest prose sentence. (0, "") on empty input."""
    longest, worst = 0, ""
    for sentence in SENTENCE_SPLIT_RE.split(prose_of(text)):
        stripped = sentence.strip()
        n = len(stripped.split())
        if n > longest:
            longest, worst = n, stripped
    return longest, worst


def run_checks(text: str, checks: dict) -> list[dict]:
    """Score the deterministic gates. One result dict per gate, never a model call."""
    results: list[dict] = []
    scope = checks.get("scope", "response")
    scoped = in_scope(text, scope)
    if scoped is None:
        return [{
            "check": "scope deliverable",
            "verdict": "FAIL",
            "evidence": "response has no ```deliverable fenced block, so nothing was scored",
        }]
    text = scoped

    for pattern in checks.get("required", []):
        hit = re.search(pattern, text)
        results.append({
            "check": f"required {pattern!r}",
            "verdict": "PASS" if hit else "FAIL",
            "evidence": f"matched {hit.group(0)[:60]!r}" if hit else "no match in response",
        })

    for pattern in checks.get("forbidden", []):
        hit = re.search(pattern, text)
        results.append({
            "check": f"forbidden {pattern!r}",
            "verdict": "FAIL" if hit else "PASS",
            "evidence": f"found {hit.group(0)[:60]!r}" if hit else "absent",
        })

    if "max_words" in checks:
        n, limit = word_count(text), checks["max_words"]
        results.append({
            "check": f"max_words {limit}",
            "verdict": "PASS" if n <= limit else "FAIL",
            "evidence": f"{n} words",
        })

    if "max_sentence_words" in checks:
        n, worst = longest_sentence(text)
        limit = checks["max_sentence_words"]
        results.append({
            "check": f"max_sentence_words {limit}",
            "verdict": "PASS" if n <= limit else "FAIL",
            "evidence": f"longest is {n} words: {worst[:70]!r}" if worst else "no prose found",
        })

    return results


# ------------------------------------------------------------------------------ model tier


class ModelCallError(RuntimeError):
    """A model call did not produce usable output.

    This raises rather than returning "" because an empty response is not a neutral result
    here: it PASSES every `forbidden` check and fails only the `required` ones, so a crashed
    CLI scores an arm as cleaner than a working one. A harness that reports a lift number
    over a failed call is worse than one that reports nothing.
    """


def claude(prompt: str, model: str, cwd: Path, timeout: int = 900) -> str:
    """One headless `claude -p` call. Returns stdout, or raises ModelCallError.

    `cwd` is the arm's sandbox, never the repo root. See `open_sandbox`.
    """
    try:
        result = subprocess.run(
            ["claude", "-p", prompt, "--model", model, "--output-format", "text"],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=cwd,
        )
    except FileNotFoundError as exc:
        raise ModelCallError("claude CLI not found on PATH") from exc
    except subprocess.TimeoutExpired as exc:
        raise ModelCallError(f"claude CLI timed out after {timeout}s") from exc
    if result.returncode != 0:
        raise ModelCallError(
            f"claude CLI exited {result.returncode}: {result.stderr.strip()[:300]}"
        )
    output = result.stdout.strip()
    if not output:
        raise ModelCallError("claude CLI returned no output")
    return output


def arms(skill: str) -> list[dict]:
    """The two arms of a case: the skill body loaded, and nothing loaded.

    The with-skill arm names the skill file directly rather than letting the model route to
    it. Routing is `eval_routing.py`'s job; mixing the two would make a routing miss look
    like a quality regression.
    """
    return [
        {"label": "with skill", "dir": "with_skill", "skill": skill},
        {"label": "baseline", "dir": "baseline", "skill": None},
    ]


def open_sandbox(stack: contextlib.ExitStack, skill: str | None) -> tuple[Path, str | None]:
    """An empty scratch directory to run one arm in, plus the skill path inside it.

    Neither arm runs from the repo root. Run from the repo, both would load this repo's
    CLAUDE.md and its always-on directives, including the content pipeline the skills under
    test belong to; the baseline arm would arrive carrying most of what the skill was
    supposed to add, and the measured lift would collapse toward zero for reasons that have
    nothing to do with the skill body.

    The skill under test is COPIED in rather than read across the boundary. Reaching out of
    the working directory needs a permission the headless CLI does not have, and the first
    run of this harness scored a whole case on the model apologizing that it could not open
    the file. A copied tree also keeps any `knowledge/` the skill loads on demand reachable.
    """
    sandbox = Path(stack.enter_context(tempfile.TemporaryDirectory(prefix="output-lift-")))
    if skill is None:
        return sandbox, None
    shutil.copytree(SKILLS_DIR / skill, sandbox / "skill")
    return sandbox, "skill/SKILL.md"


def generate(case: dict, outdir: Path, model: str) -> list[str]:
    """Run both arms of one case, writing responses under outdir. Returns failure messages.

    A failed arm writes no `response.md` at all. Writing an empty one would let `grade()`
    score a crash as model behavior, and an empty response passes every `forbidden` check.
    """
    failures: list[str] = []
    print(f"--- {case['case']}  (skill: {case['skill']}) ---")
    for arm in arms(case["skill"]):
        dest = outdir / case["case"] / arm["dir"]
        dest.mkdir(parents=True, exist_ok=True)

        with contextlib.ExitStack() as stack:
            sandbox, skill_path = open_sandbox(stack, arm["skill"])
            if skill_path:
                prompt = (
                    f"Read the skill at {skill_path} and follow its instructions exactly.\n\n"
                    f"Task: {case['prompt']}"
                )
            else:
                prompt = case["prompt"]

            start = time.time()
            try:
                response = claude(prompt, model, sandbox)
            except ModelCallError as exc:
                elapsed = time.time() - start
                failures.append(f"{case['case']} [{arm['label']}]: {exc}")
                (dest / "meta.json").write_text(
                    json.dumps({"seconds": round(elapsed, 2), "model": model,
                                "failed": str(exc)}, indent=2),
                    encoding="utf-8",
                )
                (dest / "response.md").unlink(missing_ok=True)
                print(f"  [{arm['label']:>10}] {elapsed:5.1f}s  FAILED: {exc}", file=sys.stderr)
                continue
            elapsed = time.time() - start

        (dest / "response.md").write_text(response, encoding="utf-8")
        (dest / "meta.json").write_text(
            json.dumps({"seconds": round(elapsed, 2), "model": model,
                        "words": word_count(response)}, indent=2),
            encoding="utf-8",
        )
        print(f"  [{arm['label']:>10}] {elapsed:5.1f}s  {word_count(response)} words")
    print()
    return failures


GRADER_PROMPT = """You are a strict grader. Grade the response below against each assertion.

You are grading blind. You are not told how this response was produced, and you must not \
speculate about it. Judge only what the text does.

RESPONSE:
{response}

ASSERTIONS:
{assertions}

For each assertion output exactly one line, in order:
PASS|<number>|<brief evidence quoted from the response>
or
FAIL|<number>|<brief evidence quoted from the response>

Output ONLY those lines. No preamble, no summary, no other text."""


def parse_grades(output: str, expected: int) -> list[dict]:
    """Pull PASS/FAIL lines out of the grader's reply, keyed by assertion number.

    Always returns exactly `expected` results, one per assertion, in order. Graders do not
    reliably emit one line per assertion: the first full run of this suite had one return a
    duplicate verdict for assertion 1 and none for assertion 4. Collecting lines positionally
    scored that case on four lines covering three assertions, and the pass rate looked fine.

    So: index by the number the grader claims, keep the first verdict per number, ignore
    anything out of range, and fail any assertion the grader never returned a verdict for.
    An ungraded assertion is not a pass; it is a criterion nobody demonstrated.
    """
    by_number: dict[int, dict] = {}
    for line in output.splitlines():
        parts = line.strip().split("|", 2)
        if len(parts) != 3 or parts[0].strip() not in ("PASS", "FAIL"):
            continue
        number = parts[1].strip()
        if not number.isdigit():
            continue
        n = int(number)
        if 1 <= n <= expected and n not in by_number:
            by_number[n] = {
                "assertion": n,
                "verdict": parts[0].strip(),
                "evidence": parts[2].strip(),
            }
    return [
        by_number.get(
            n,
            {"assertion": n, "verdict": "FAIL",
             "evidence": "grader returned no verdict for this assertion"},
        )
        for n in range(1, expected + 1)
    ]


def grade(cases: list[dict], outdir: Path, grader_model: str,
          sandbox: Path) -> tuple[dict, list[str]]:
    """Score every stored response. Returns (totals, failures).

    A missing `response.md` is a failure, never a skip. Skipping one would shrink that arm's
    denominator while the other arm keeps its own, so the two pass rates would be computed
    over different totals and the lift between them would be meaningless while still looking
    like a number.
    """
    print("=== Grading ===\n")
    failures: list[str] = []
    totals = {arm["dir"]: {"pass": 0, "total": 0} for arm in arms("x")}

    for case in cases:
        print(f"--- {case['case']} ---")
        for arm in arms(case["skill"]):
            dest = outdir / case["case"] / arm["dir"]
            response_file = dest / "response.md"
            if not response_file.exists():
                failures.append(
                    f"{case['case']} [{arm['label']}]: no response.md to grade"
                )
                print(f"  [{arm['label']:>10}] MISSING response.md", file=sys.stderr)
                continue
            response = response_file.read_text(encoding="utf-8")
            print(f"  [{arm['label']}]")

            results = run_checks(response, case["checks"])

            if case["assertions"]:
                numbered = "\n".join(
                    f"{i + 1}. {a}" for i, a in enumerate(case["assertions"])
                )
                try:
                    raw = claude(
                        GRADER_PROMPT.format(response=response, assertions=numbered),
                        grader_model,
                        sandbox,
                    )
                except ModelCallError as exc:
                    failures.append(f"{case['case']} [{arm['label']}]: grader failed: {exc}")
                    print(f"    GRADER FAILED: {exc}", file=sys.stderr)
                    continue
                (dest / "grading_raw.txt").write_text(raw, encoding="utf-8")
                for g in parse_grades(raw, len(case["assertions"])):
                    results.append({
                        "check": case["assertions"][g["assertion"] - 1],
                        "verdict": g["verdict"],
                        "evidence": g["evidence"],
                    })

            for r in results:
                print(f"    {r['verdict']}  {r['check'][:70]}  |  {r['evidence'][:60]}")
                totals[arm["dir"]]["total"] += 1
                if r["verdict"] == "PASS":
                    totals[arm["dir"]]["pass"] += 1

            (dest / "grading.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
        print()

    return totals, failures


def report(totals: dict, outdir: Path, grader_model: str, failures: list[str]) -> dict:
    """Print and persist the pass-rate table. The delta is the number that matters.

    When any arm failed, the counts still print (they cost real model calls) but the lift is
    withheld: the two arms no longer answered the same number of criteria, so subtracting
    their rates compares nothing.
    """
    rates: dict[str, float] = {}
    print("=" * 47)
    print(f"  OUTPUT LIFT - {outdir.name}")
    print("=" * 47)
    for arm in arms("x"):
        t = totals[arm["dir"]]
        if t["total"]:
            rates[arm["dir"]] = t["pass"] * 100 / t["total"]
            print(f"  {arm['label']:<12} {t['pass']:>3}/{t['total']:<3} "
                  f"({rates[arm['dir']]:5.1f}%)")
    lift = None
    if failures:
        print(f"  {'lift':<12} WITHHELD, {len(failures)} failure(s)")
    elif len(rates) == 2:
        lift = rates["with_skill"] - rates["baseline"]
        print(f"  {'lift':<12} {lift:+.1f} points")
    print("=" * 47)
    if failures:
        print(f"  This run is INCOMPLETE. Do not quote its numbers:")
        for f in failures:
            print(f"    - {f}")
    if lift is not None and lift <= 0:
        print("  Zero or negative lift: the skill is not earning its context cost on")
        print("  these cases. Either the cases are wrong, or the skill body is.")

    summary = {
        "run": outdir.name,
        "at": datetime.now(timezone.utc).isoformat(),
        "grader_model": grader_model,
        "totals": totals,
        "rates": rates,
        "lift_points": lift,
        "complete": not failures,
        "failures": failures,
    }
    (outdir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"\n  Per-case detail: {outdir}/<case>/<arm>/grading.json")
    return summary


def next_run_dir(reuse_latest: bool) -> Path:
    """evals/runs/lift-N. `reuse_latest` returns the newest existing run instead of a new one."""
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    existing = sorted(
        (p for p in RUNS_DIR.glob("lift-*") if p.is_dir() and p.name[5:].isdigit()),
        key=lambda p: int(p.name[5:]),
    )
    if reuse_latest:
        if not existing:
            sys.exit("No run to grade. Run without --grade-only first.")
        return existing[-1]
    n = int(existing[-1].name[5:]) + 1 if existing else 1
    return RUNS_DIR / f"lift-{n}"


# ----------------------------------------------------------------------------------- main


def main() -> int:
    """Parse arguments, run the requested tier, and return the process exit code."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    # Mutually exclusive: with both, --grade-only sends next_run_dir() to the newest run and
    # --run then regenerates into it, overwriting the very responses --grade-only exists to
    # re-score.
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--run", action="store_true",
                      help="generate responses for both arms, then grade (costs model calls)")
    mode.add_argument("--grade-only", action="store_true",
                      help="re-grade the most recent run's stored responses")
    parser.add_argument("--case", metavar="NAME", help="limit to one case by name")
    parser.add_argument("--subject-model", metavar="MODEL",
                        help="model under test; required with --run")
    parser.add_argument("--grader-model", metavar="MODEL",
                        help="model that grades; required with --run or --grade-only, and must "
                             "differ from --subject-model")
    parser.add_argument("--list", action="store_true", help="print the suite and exit")
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    args = parser.parse_args()

    cases, errors = load_suite()
    skills = load_skills()
    errors += validate(cases, skills)

    if args.case:
        matched = [c for c in cases if c["case"] == args.case]
        if not matched:
            print(f"No case named '{args.case}'. Known: {', '.join(c['case'] for c in cases)}")
            return 1
        cases = matched

    if errors:
        if args.json:
            print(json.dumps({"ok": False, "errors": [e.as_dict() for e in errors]}, indent=2))
        else:
            for e in errors:
                print(e.annotation())
            print(f"\n{len(errors)} structural failure(s) in {SUITE}.")
        return 1

    if args.json:
        print(json.dumps({"ok": True, "cases": [
            {k: v for k, v in c.items() if k != "line"} for c in cases
        ]}, indent=2))
        return 0

    if args.list:
        print(f"{SUITE}: {len(cases)} case(s)\n")
        for c in cases:
            checks = c["checks"]
            n_det = (len(checks.get("required", [])) + len(checks.get("forbidden", []))
                     + sum(1 for k in ("max_words", "max_sentence_words") if k in checks))
            scope = checks.get("scope", "response")
            print(f"  {c['case']}")
            print(f"    skill       {c['skill']}")
            print(f"    scored by   {n_det} deterministic ({scope}), "
                  f"{len(c['assertions'])} model-graded")
            print(f"    why         {c['why']}")
            print()
        return 0

    if not (args.run or args.grade_only):
        by_skill: dict[str, int] = {}
        for c in cases:
            by_skill[c["skill"]] = by_skill.get(c["skill"], 0) + 1
        print(f"{SUITE}: {len(cases)} case(s) across {len(by_skill)} skill(s), all resolve.")
        for skill, n in sorted(by_skill.items()):
            print(f"  {skill}: {n}")
        print("\nStructural checks only. To measure lift:")
        print("  python3 scripts/eval_output_lift.py --run \\")
        print("      --subject-model <model> --grader-model <a different model>")
        return 0

    if not args.grader_model:
        return int(bool(sys.stderr.write(
            "--grader-model is required. The grader must not be the model under test:\n"
            "same-model grading shares the blind spot it exists to catch.\n"
            "See docs/skill-evals.md, 'The judge should not be the model under test'.\n"
        )) or 1)

    if args.run:
        if not args.subject_model:
            sys.stderr.write("--subject-model is required with --run.\n")
            return 1
        if args.subject_model == args.grader_model:
            sys.stderr.write(
                f"--grader-model must differ from --subject-model (both are "
                f"'{args.subject_model}'). See docs/skill-evals.md.\n"
            )
            return 1

    outdir = next_run_dir(reuse_latest=args.grade_only)
    outdir.mkdir(parents=True, exist_ok=True)
    print(f"=== Output lift: {outdir} ===")
    print(f"  cases        {len(cases)}")
    if args.run:
        print(f"  subject      {args.subject_model}")
    print(f"  grader       {args.grader_model}\n")

    failures: list[str] = []
    if args.run:
        for case in cases:
            failures += generate(case, outdir, args.subject_model)

    with contextlib.ExitStack() as stack:
        # The grader gets a bare sandbox too: it must judge the text in front of it, with no
        # skill body and no repo conventions to pattern-match the "right" answer against.
        grader_sandbox, _ = open_sandbox(stack, None)
        totals, grade_failures = grade(cases, outdir, args.grader_model, grader_sandbox)
    failures += grade_failures

    report(totals, outdir, args.grader_model, failures)
    # Non-zero on any failed call or missing response: a run that could not produce one of
    # its arms has no lift to report, and a caller scripting this must be able to tell.
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
