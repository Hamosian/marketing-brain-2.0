#!/usr/bin/env python3
"""Deterministic tier of the skill-routing eval suite.

The repo already lints *structure* (`scripts/lint_agents.py`, the Team Context Lint
workflow) and audits *staleness* (`/health-check`). Neither one tests *behaviour*: with 61
skills routed purely on their frontmatter `description`, the failure that actually bites is
a new skill whose trigger phrases collide with an existing one, so requests quietly land on
the wrong agent. Nothing caught that before this script.

This is the cheap, offline half of the answer. It never calls a model, so it can run on
every PR:

1. **Structural checks (fail the build).** Every case in the suite names a skill that
   exists on disk, no duplicate requests, no malformed lines. A rename that orphans an eval
   case fails here rather than rotting silently.
2. **Ambiguity report (warn; fail only under `--strict`).** For each case, rank every skill
   by TF-IDF similarity between the request and the skill's `name` + `description`. If a
   skill other than the expected one ranks at or above it, the descriptions overlap on the
   vocabulary a router would key on. That is a *signal about the descriptions*, not a
   prediction of what Claude will do, so it warns by default -- a lexical proxy has no
   business failing a build on its own.
3. **Coverage (advisory).** Skills with no eval case at all, via `--coverage`.

The model-in-the-loop half -- actually asking a model to route, scoring it, and proposing a
description patch for every miss -- is `/skill-eval`. Both tiers read the same suite.
See `docs/skill-evals.md` for the design and `evals/README.md` for how to add cases.

Usage:
    python3 scripts/eval_routing.py                  # structural checks + ambiguity warnings
    python3 scripts/eval_routing.py --strict         # ambiguity fails too
    python3 scripts/eval_routing.py --coverage       # also list skills with no eval case
    python3 scripts/eval_routing.py --json           # machine-readable, for /skill-eval
    python3 scripts/eval_routing.py --descriptions   # dump name + description per skill

Exits 1 on any structural failure (and on ambiguity under `--strict`), in every output mode
including `--json`. Emits GitHub Actions `::error` / `::warning` annotations pinned to the
offending suite line. Stdlib only. Run from the repo root.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import NamedTuple

from sync_embeddings import tokenize

SKILLS_DIR = Path(".claude/skills")
SUITE = Path("evals/routing.jsonl")

# How far down the ranking the expected skill may sit before the overlap stops looking like
# a near-miss and starts looking like a description that does not describe the job at all.
TOP_N = 3

# Verdicts that are not failures even under --strict. `external` cases target a skill outside
# this repo (a plugin like `/rivermind:ask`), so there is no description here to score them
# against -- they exist to carry the routing rule to the model tier, not to be ranked.
NON_FAILING = ("clear", "external")


class EvalError(NamedTuple):
    """A structural problem with the suite, carrying its location for a pinned annotation.

    The location is kept as fields rather than interpolated into `message`, so the GitHub
    annotation can set `file=`/`line=` without parsing a path back out of prose -- which
    breaks on any path containing a colon.
    """

    message: str
    file: Path | None = None
    line: int | None = None

    def annotation(self) -> str:
        """Render as a GitHub Actions error annotation, pinned to a line where known."""
        if self.file is not None and self.line is not None:
            return f"::error file={self.file},line={self.line}::{self.message}"
        return f"::error::{self.message}"

    def as_dict(self) -> dict:
        """JSON-serializable form for `--json`."""
        return {
            "message": self.message,
            "file": str(self.file) if self.file is not None else None,
            "line": self.line,
        }


def parse_frontmatter(text: str) -> dict[str, str]:
    """Pull the flat `key: value` pairs out of a SKILL.md frontmatter block.

    Deliberately not a YAML parser: skill frontmatter is flat scalars only, and the repo's
    scripts stay stdlib-only so CI needs no install step. Handles the two shapes that
    actually occur here and that a `grep -A2` cannot: keys in any order, and values wrapping
    onto continuation lines (how the long `description:` fields are written).
    """
    if not text.startswith("---"):
        return {}
    lines = text.splitlines()
    fields: dict[str, str] = {}
    key = None
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if line and not line[0].isspace() and ":" in line:
            key, _, value = line.partition(":")
            key = key.strip()
            fields[key] = value.strip()
        elif key and line.strip():
            fields[key] = f"{fields[key]} {line.strip()}".strip()
    return fields


def load_skills() -> dict[str, str]:
    """Map skill `name:` -> the raw `description:` text a router sees.

    Keys come from the frontmatter `name:`, not the directory, because routing is by name
    and the two can drift.
    """
    skills: dict[str, str] = {}
    for path in sorted(SKILLS_DIR.glob("*/SKILL.md")):
        fields = parse_frontmatter(path.read_text(encoding="utf-8"))
        name = fields.get("name")
        if not name:
            # The Team Context Lint workflow already fails the build for this; skipping
            # keeps one missing field from cascading into dozens of eval errors.
            continue
        skills[name] = fields.get("description", "")
    return skills


def routing_text(name: str, description: str) -> str:
    """The text a router keys on for one skill: its name plus its description."""
    return f"{name} {description}"


def load_suite(path: Path) -> tuple[list[dict], list[EvalError]]:
    """Read the JSONL suite. Returns (cases, structural errors)."""
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

        # Syntactically valid JSON is not necessarily a usable case: `[]` and
        # `{"request": 42}` both parse. Type-check before touching the fields, so a
        # malformed line yields the pinned structural error this script promises rather
        # than an AttributeError traceback that names no file and no line.
        if not isinstance(case, dict):
            errors.append(
                EvalError(f"case must be a JSON object, got {type(case).__name__}", path, lineno)
            )
            continue
        request, expect = case.get("request"), case.get("expect")
        bad_field = next(
            (
                field
                for field, value in (("request", request), ("expect", expect))
                if not isinstance(value, str) or not value.strip()
            ),
            None,
        )
        if bad_field:
            errors.append(
                EvalError(f"'{bad_field}' must be a non-empty string", path, lineno)
            )
            continue
        request, expect = request.strip(), expect.strip()
        key = request.lower()
        if key in seen:
            errors.append(
                EvalError(f"duplicate request (first seen line {seen[key]})", path, lineno)
            )
            continue
        seen[key] = lineno
        case["request"] = request
        case["expect"] = expect
        case["external"] = bool(case.get("external"))
        case["line"] = lineno
        cases.append(case)
    return cases, errors


def build_index(skills: dict[str, str]) -> tuple[dict[str, dict[str, float]], dict[str, float]]:
    """L2-normalized TF-IDF vector per skill, plus the IDF table for scoring queries.

    Same tokenizer and stopword list as the semantic index (`scripts/sync_embeddings.py`),
    so "what a keyword search would match" means one thing across the repo.
    """
    token_lists = {
        name: tokenize(routing_text(name, description)) for name, description in skills.items()
    }
    total_docs = len(token_lists) or 1

    df: dict[str, int] = {}
    for tokens in token_lists.values():
        for term in set(tokens):
            df[term] = df.get(term, 0) + 1
    idf = {term: math.log(total_docs / count) + 1.0 for term, count in df.items()}

    vectors: dict[str, dict[str, float]] = {}
    for name, tokens in token_lists.items():
        tf: dict[str, int] = {}
        for term in tokens:
            tf[term] = tf.get(term, 0) + 1
        length = len(tokens) or 1
        weights = {term: (count / length) * idf[term] for term, count in tf.items()}
        norm = math.sqrt(sum(w * w for w in weights.values())) or 1.0
        vectors[name] = {term: w / norm for term, w in weights.items()}
    return vectors, idf


def rank(
    request: str, vectors: dict[str, dict[str, float]], idf: dict[str, float]
) -> list[tuple[str, float]]:
    """Skills ordered by TF-IDF cosine similarity to the request, best first."""
    tokens = [t for t in tokenize(request) if t in idf]
    tf: dict[str, int] = {}
    for term in tokens:
        tf[term] = tf.get(term, 0) + 1
    length = len(tokens) or 1
    weights = {term: (count / length) * idf[term] for term, count in tf.items()}
    norm = math.sqrt(sum(w * w for w in weights.values())) or 1.0
    query = {term: w / norm for term, w in weights.items()}

    scored = []
    for name, vector in vectors.items():
        shared = set(query) & set(vector)
        scored.append((name, sum(query[t] * vector[t] for t in shared)))
    # Tie-break by name so the report is stable across runs and the diff stays readable.
    scored.sort(key=lambda pair: (-pair[1], pair[0]))
    return scored


def evaluate(
    cases: list[dict], skills: dict[str, str], suite: Path
) -> tuple[list[dict], list[EvalError]]:
    """Score every case. Returns (results, structural errors)."""
    errors: list[EvalError] = []
    vectors, idf = build_index(skills)
    results: list[dict] = []

    for case in cases:
        base = {
            "request": case["request"],
            "expect": case["expect"],
            "why": case.get("why", ""),
            "line": case["line"],
        }

        if case["external"]:
            # `external` makes a case non-failing, so it is a coverage-removal footgun: set
            # it on a local skill and that skill's case stops being checked, silently and
            # without failing the build. Only genuinely off-repo targets may claim it.
            if case["expect"] in skills:
                errors.append(
                    EvalError(
                        f"'{case['expect']}' is a local skill, so \"external\": true would "
                        f"silently drop it from scoring -- remove the flag",
                        suite,
                        case["line"],
                    )
                )
                continue
            # Target lives outside this repo, so there is no description to rank. Carry the
            # case through unscored -- the model tier still checks it.
            results.append({**base, "verdict": "external", "position": None, "score": None,
                            "rivals": [], "top": []})
            continue

        if case["expect"] not in skills:
            errors.append(
                EvalError(
                    f"expects '{case['expect']}', which is not a skill name in "
                    f"{SKILLS_DIR}/*/SKILL.md (add \"external\": true if it is a plugin skill)",
                    suite,
                    case["line"],
                )
            )
            continue

        ranking = rank(case["request"], vectors, idf)
        names = [name for name, _ in ranking]
        scores = dict(ranking)
        position = names.index(case["expect"]) + 1
        rivals = [
            name for name, score in ranking
            if name != case["expect"] and score >= scores[case["expect"]]
        ]

        if position == 1 and not rivals:
            verdict = "clear"
        elif position <= TOP_N:
            verdict = "ambiguous"
        else:
            verdict = "weak-trigger"

        results.append(
            {
                **base,
                "position": position,
                "score": round(scores[case["expect"]], 4),
                "verdict": verdict,
                "rivals": rivals[:5],
                "top": [{"skill": n, "score": round(s, 4)} for n, s in ranking[:TOP_N]],
            }
        )
    return results, errors


def count_failures(results: list[dict], strict: bool) -> int:
    """Cases that should fail the run.

    Ambiguity is advisory by default -- a lexical proxy must not gate a merge -- so this is
    zero unless `--strict`. Shared by every output mode so `--json --strict` cannot silently
    disagree with the exit code the docstring promises.
    """
    if not strict:
        return 0
    return sum(1 for result in results if result["verdict"] not in NON_FAILING)


def report(results: list[dict], skills: dict[str, str], args: argparse.Namespace) -> None:
    """Print the human-readable summary, per-case annotations, and optional coverage list.

    Emits `::warning` (or `::error` under `--strict`) per non-clear case, pinned to its suite
    line. Returns nothing: the exit code comes from `count_failures` so every output mode
    derives it identically.
    """
    counts: dict[str, int] = {}
    for result in results:
        counts[result["verdict"]] = counts.get(result["verdict"], 0) + 1

    print(f"Routing eval: {len(results)} cases against {len(skills)} skills")
    for verdict in ("clear", "ambiguous", "weak-trigger", "external"):
        if verdict in counts:
            print(f"  {verdict:<13} {counts[verdict]}")
    print()

    for result in results:
        if result["verdict"] in NON_FAILING:
            continue
        level = "error" if args.strict else "warning"
        rivals = ", ".join(result["rivals"]) or "none"
        message = (
            f"'{result['request']}' -> expected {result['expect']} "
            f"(rank {result['position']}, score {result['score']}); "
            f"scores at or above it: {rivals}"
        )
        print(f"::{level} file={args.suite},line={result['line']}::{message}")

    if args.coverage:
        covered = {r["expect"] for r in results if r["verdict"] != "external"}
        uncovered = sorted(set(skills) - covered)
        print(f"\nCoverage: {len(covered)}/{len(skills)} skills have at least one case")
        for name in uncovered:
            print(f"  no case: {name}")


def main() -> int:
    """Parse args, run the enabled mode, and return the process exit code."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--suite", type=Path, default=SUITE)
    parser.add_argument(
        "--strict",
        action="store_true",
        help="treat ambiguity and weak triggers as failures, not warnings",
    )
    parser.add_argument("--coverage", action="store_true", help="list skills with no eval case")
    parser.add_argument("--json", action="store_true", help="emit results as JSON")
    parser.add_argument(
        "--descriptions",
        action="store_true",
        help="dump each skill's name and description as JSON (the text a router sees)",
    )
    args = parser.parse_args()

    skills = load_skills()
    if not skills:
        print(f"::error::no skills found under {SKILLS_DIR}")
        return 1

    if args.descriptions:
        print(json.dumps(skills, indent=2, sort_keys=True))
        return 0

    cases, errors = load_suite(args.suite)
    results, eval_errors = evaluate(cases, skills, args.suite)
    errors += eval_errors
    failures = count_failures(results, args.strict)

    if args.json:
        print(
            json.dumps(
                {
                    "skills": len(skills),
                    "errors": [error.as_dict() for error in errors],
                    "results": results,
                },
                indent=2,
            )
        )
        return 1 if (errors or failures) else 0

    for error in errors:
        print(error.annotation())

    report(results, skills, args)
    return 1 if (errors or failures) else 0


if __name__ == "__main__":
    sys.exit(main())
