#!/usr/bin/env python3
"""Prove the output-lift harness fails loudly on a broken suite instead of scoring less.

    python3 scripts/test_eval_output_lift.py

WHAT THIS GUARDS
----------------
The failure mode of an eval suite is not a red build, it is a green one that stopped
checking. A typo'd check key, a regex that no longer compiles, a case pointing at a renamed
skill: each of those can quietly reduce what the suite scores while the summary keeps
printing a pass rate. `scripts/eval_output_lift.py` is written to treat every one of them as
a structural failure, and this file exercises that promise rather than asserting it.

It also pins the deterministic scorer, because those checks are the half that runs with no
model in the loop and therefore the half nobody re-reads.

Stdlib only. No network, no model calls.
"""

from __future__ import annotations

import contextlib
import io
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest import mock

import eval_output_lift as lift

PASSED: list[str] = []
FAILED: list[str] = []


def check(label: str, condition: bool, detail: str = "") -> None:
    """Record one assertion. Collected and printed by main() rather than raised, so a
    single run reports every failure instead of stopping at the first."""
    if condition:
        PASSED.append(label)
    else:
        FAILED.append(f"{label}{f'  ({detail})' if detail else ''}")


def suite_from(lines: list[str]) -> tuple[list[dict], list[lift.EvalError]]:
    """Write a throwaway suite and load it, so parser tests never touch the real file."""
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "suite.jsonl"
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return lift.load_suite(path)


def case_line(**overrides) -> str:
    """One valid suite line as JSON, with any field overridden for the test at hand."""
    base = {
        "case": "a-case",
        "skill": "ste",
        "prompt": "do a thing",
        "why": "guards a thing",
        "assertions": ["it did the thing"],
    }
    base.update(overrides)
    return json.dumps(base)


# ------------------------------------------------------------------ deterministic scoring

def test_required_and_forbidden() -> None:
    """required must match; forbidden must not. The two invert each other."""
    results = lift.run_checks(
        "VERDICT: SHIP\nThe draft leverages nothing.",
        {"required": [r"(?m)^VERDICT:\s*(SHIP|REVISE)\b"], "forbidden": [r"(?i)\bleverag"]},
    )
    verdicts = [r["verdict"] for r in results]
    check("required pattern that matches passes", verdicts[0] == "PASS", str(results[0]))
    check("forbidden pattern that matches fails", verdicts[1] == "FAIL", str(results[1]))

    results = lift.run_checks("nothing here", {"required": [r"VERDICT"], "forbidden": [r"zzz"]})
    check("required pattern that misses fails", results[0]["verdict"] == "FAIL")
    check("forbidden pattern that misses passes", results[1]["verdict"] == "PASS")


def test_length_gates() -> None:
    """max_words and max_sentence_words fail over the limit and pass under it."""
    text = "One two three four five. " + "word " * 40
    results = lift.run_checks(text, {"max_words": 10, "max_sentence_words": 25})
    check("max_words fails when over", results[0]["verdict"] == "FAIL", results[0]["evidence"])
    check("max_sentence_words fails when over",
          results[1]["verdict"] == "FAIL", results[1]["evidence"])

    results = lift.run_checks("Short and plain.", {"max_words": 10, "max_sentence_words": 25})
    check("length gates pass when under", all(r["verdict"] == "PASS" for r in results))


def test_code_fences_excluded_from_length() -> None:
    """A skill that correctly returns a code block should not trip a prose ceiling."""
    fenced = "Short prose.\n\n```\n" + "token " * 500 + "\n```\n"
    check("fenced code does not count toward word ceilings",
          lift.word_count(fenced) < 20, f"counted {lift.word_count(fenced)}")
    longest, _ = lift.longest_sentence(fenced)
    check("fenced code does not count toward sentence length", longest < 20, f"longest {longest}")


def test_unquoted_scope() -> None:
    """The run-1 finding: a de-slopping skill names the phrases it removed, and a naive
    forbidden-word scan over the whole response fails it for quoting its own work."""
    cited = 'I cut "leverage" and `robust` from the draft. Nothing was delved into.'
    forbidden = {"forbidden": [r"(?i)\bleverag", r"(?i)\brobust\b", r"(?i)\bdelv"]}

    whole = [r["verdict"] for r in lift.run_checks(cited, forbidden)]
    check("default scope flags quoted citations", whole == ["FAIL", "FAIL", "FAIL"], str(whole))

    scoped = [r["verdict"] for r in lift.run_checks(cited, {**forbidden, "scope": "unquoted"})]
    check("unquoted scope ignores quoted and backticked citations",
          scoped[:2] == ["PASS", "PASS"], str(scoped))
    check("unquoted scope still flags the skill's own unquoted slop",
          scoped[2] == "FAIL", str(scoped))


def test_unquoted_scope_survives_apostrophes() -> None:
    """The single-quote arm of QUOTED_RE must not open on an apostrophe in "don't"."""
    text = "don't use 'a quoted span' and don't stop there"
    stripped = lift.in_scope(text, "unquoted")
    check("an apostrophe cannot open a quoted span and swallow the line",
          "don't" in stripped and stripped.count("don't") == 2, repr(stripped))
    check("a genuine single-quoted span is still stripped",
          "quoted span" not in stripped, repr(stripped))


def test_deliverable_scope() -> None:
    """de-ai answers a cleanup prompt with a triage TABLE naming every tell it found, so no
    amount of quote-stripping saves a forbidden-word scan over the whole response. The block
    is the only honest target."""
    response = (
        "Triage: leverage, robust, delve all present.\n\n"
        "```deliverable\nWe use a small set of tools. We research every creator first.\n```\n\n"
        "That is what I changed."
    )
    checks = {"scope": "deliverable", "forbidden": [r"(?i)\bleverag", r"(?i)\brobust\b"]}
    verdicts = [r["verdict"] for r in lift.run_checks(response, checks)]
    check("deliverable scope ignores slop named in the analysis",
          verdicts == ["PASS", "PASS"], str(verdicts))

    dirty = response.replace("We use a small set of tools.", "We leverage robust tools.")
    verdicts = [r["verdict"] for r in lift.run_checks(dirty, checks)]
    check("deliverable scope still flags slop inside the block",
          verdicts == ["FAIL", "FAIL"], str(verdicts))


def test_missing_deliverable_block_fails_loudly() -> None:
    """Scoring an absent block as an empty string would pass every forbidden check."""
    results = lift.run_checks("no fenced block anywhere",
                              {"scope": "deliverable", "forbidden": [r"(?i)\bleverag"]})
    check("a missing deliverable block is one explicit failure, not a free pass",
          len(results) == 1 and results[0]["verdict"] == "FAIL", str(results))
    check("the failure says the block was missing",
          "no ```deliverable" in results[0]["evidence"], str(results[0]))


def test_bad_scope_fails() -> None:
    """An unrecognised scope is a structural failure, not a silent fallback."""
    cases, _ = suite_from([case_line(checks={"scope": "just-the-good-bit", "forbidden": ["x"]})])
    errors = lift.validate(cases, {"ste": "..."})
    check("an unknown scope fails the build",
          any("scope" in e.message for e in errors), str(errors))


def test_empty_checks_score_nothing() -> None:
    """No checks means no deterministic results, not a free pass."""
    check("a case with no checks produces no deterministic results",
          lift.run_checks("anything at all", {}) == [])


# ----------------------------------------------------------------------- suite structure

def test_valid_case_loads() -> None:
    """A well-formed case parses, and carries the line number an annotation needs."""
    cases, errors = suite_from(["// a comment", "", case_line()])
    check("comments and blank lines are skipped", len(cases) == 1, f"got {len(cases)}")
    check("a well-formed case loads clean", errors == [], str(errors))
    check("the source line is carried for annotations", cases and cases[0]["line"] == 3)


def test_malformed_lines_are_located() -> None:
    """A broken line yields a located EvalError, never an unpinned traceback."""
    _, errors = suite_from(["{not json"])
    check("invalid JSON is a located error",
          len(errors) == 1 and errors[0].line == 1, str(errors))

    _, errors = suite_from(["[1, 2, 3]"])
    check("a non-object case is rejected",
          any("must be a JSON object" in e.message for e in errors), str(errors))


def test_missing_required_fields() -> None:
    """Every field in REQUIRED_FIELDS is actually required, blank strings included."""
    for field in lift.REQUIRED_FIELDS:
        payload = json.loads(case_line())
        payload.pop(field)
        _, errors = suite_from([json.dumps(payload)])
        check(f"missing '{field}' is rejected",
              any(f"'{field}'" in e.message for e in errors), str(errors))

    _, errors = suite_from([case_line(why="   ")])
    check("a blank 'why' is rejected (it is what makes a failure diagnosable)",
          any("'why'" in e.message for e in errors), str(errors))


def test_case_name_and_duplicates() -> None:
    """Case names become directories under evals/runs/, so they must be safe and unique."""
    _, errors = suite_from([case_line(case="Not A Directory Name")])
    check("a case name that is not directory-safe is rejected",
          any("directory" in e.message for e in errors), str(errors))

    _, errors = suite_from([case_line(), case_line()])
    check("a duplicate case name is rejected",
          any("duplicate" in e.message for e in errors), str(errors))


# ---------------------------------------------------------------- validation against repo

def test_unknown_skill_fails() -> None:
    """A rename that orphans a case fails the build rather than rotting unnoticed."""
    cases, _ = suite_from([case_line(skill="no-such-skill-anywhere")])
    errors = lift.validate(cases, {"ste": "..."})
    check("a case naming a skill that does not exist fails the build",
          any("does not exist" in e.message for e in errors), str(errors))


def test_unknown_check_key_fails() -> None:
    """A typo'd key must fail, not silently stop gating while the suite reports green."""
    cases, _ = suite_from([case_line(checks={"max_word": 10})])
    errors = lift.validate(cases, {"ste": "..."})
    check("a typo'd check key fails instead of silently not gating",
          any("unknown check" in e.message for e in errors), str(errors))


def test_uncompilable_regex_fails() -> None:
    """A pattern that cannot compile is caught offline, not at scoring time."""
    cases, _ = suite_from([case_line(checks={"forbidden": ["(unclosed"]})])
    errors = lift.validate(cases, {"ste": "..."})
    check("a regex that does not compile fails the build",
          any("does not compile" in e.message for e in errors), str(errors))


def test_bad_length_limit_fails() -> None:
    """Zero, negative and non-integer ceilings are rejected."""
    for bad in (0, -5, "200"):
        cases, _ = suite_from([case_line(checks={"max_words": bad})])
        errors = lift.validate(cases, {"ste": "..."})
        check(f"max_words={bad!r} is rejected",
              any("positive integer" in e.message for e in errors), str(errors))


def test_case_scoring_nothing_fails() -> None:
    """A case with neither checks nor assertions measures nothing and must not pass."""
    cases, _ = suite_from([case_line(assertions=[], checks={})])
    errors = lift.validate(cases, {"ste": "..."})
    check("a case with neither checks nor assertions fails",
          any("scores nothing" in e.message for e in errors), str(errors))


# ------------------------------------------------------------------------ grader parsing

def test_grade_parsing() -> None:
    """Verdict lines are extracted even when the grader wraps them in prose."""
    raw = (
        "Here is my grading:\n"
        "PASS|1|opens with the outcome\n"
        "FAIL|2|dropped the 3.2% figure\n"
        "PASS|3|active voice throughout\n"
        "Let me know if you need more.\n"
    )
    grades = lift.parse_grades(raw, expected=3)
    check("grader prose around the verdict lines is tolerated", len(grades) == 3, str(grades))
    check("verdicts parse in order",
          [g["verdict"] for g in grades] == ["PASS", "FAIL", "PASS"], str(grades))
    check("evidence survives the split",
          grades[1]["evidence"] == "dropped the 3.2% figure", str(grades[1]))


def test_grade_parsing_always_covers_every_assertion() -> None:
    """The real failure from run 1: a duplicate verdict and a missing one, scored as fine."""
    raw = "PASS|1|first take\nFAIL|1|second take on the same one\nPASS|2|fine\nPASS|3|fine\n"
    grades = lift.parse_grades(raw, expected=4)
    check("one result per assertion regardless of what the grader emitted",
          [g["assertion"] for g in grades] == [1, 2, 3, 4], str(grades))
    check("a duplicated assertion number keeps only the first verdict",
          grades[0]["verdict"] == "PASS", str(grades[0]))
    check("an assertion the grader skipped fails rather than vanishing",
          grades[3]["verdict"] == "FAIL", str(grades[3]))
    check("the skipped assertion says why it failed",
          "no verdict" in grades[3]["evidence"], str(grades[3]))


def test_grade_parsing_ignores_out_of_range_and_junk() -> None:
    """Verdicts for assertions that do not exist, and malformed lines, are discarded."""
    raw = "PASS|9|there is no assertion 9\nMAYBE|1|not a verdict\nPASS|x|not a number\n"
    grades = lift.parse_grades(raw, expected=2)
    check("out-of-range and malformed verdict lines are ignored",
          all(g["verdict"] == "FAIL" for g in grades), str(grades))
    check("a grader that returns nothing usable fails every assertion",
          [g["verdict"] for g in lift.parse_grades("I cannot grade this.", expected=3)]
          == ["FAIL", "FAIL", "FAIL"])


# ------------------------------------------------------- falsy and mistyped scoring fields

def test_falsy_scoring_fields_are_rejected_not_normalized() -> None:
    """`.get(k) or default` would turn a malformed `false` into a valid empty collection,
    letting a case pass validation while scoring less than it claims."""
    for bad in (False, 0, ""):
        cases, _ = suite_from([case_line(checks=bad, assertions=["still valid"])])
        errors = lift.validate(cases, {"ste": "..."})
        check(f"checks={bad!r} is rejected rather than normalized to {{}}",
              any("'checks'" in e.message for e in errors), str(errors))

        cases, _ = suite_from([case_line(assertions=bad, checks={"forbidden": ["x"]})])
        errors = lift.validate(cases, {"ste": "..."})
        check(f"assertions={bad!r} is rejected rather than normalized to []",
              any("'assertions'" in e.message for e in errors), str(errors))


def test_bool_is_not_a_valid_length_limit() -> None:
    """bool subclasses int, so a bare isinstance check reads `true` as a one-word ceiling."""
    cases, _ = suite_from([case_line(checks={"max_words": True})])
    errors = lift.validate(cases, {"ste": "..."})
    check("max_words=True is rejected despite bool subclassing int",
          any("positive integer" in e.message for e in errors), str(errors))


# ------------------------------------------------------------------- model-call failures

def _fake_run(returncode: int = 0, stdout: str = "out", stderr: str = ""):
    """A stand-in for subprocess.run's CompletedProcess."""
    return mock.Mock(returncode=returncode, stdout=stdout, stderr=stderr)


def test_model_failures_raise_instead_of_returning_empty() -> None:
    """An empty response is not neutral: it PASSES every forbidden check, so a crashed CLI
    would score an arm as cleaner than a working one."""
    sandbox = Path(".")

    with mock.patch.object(lift.subprocess, "run", side_effect=FileNotFoundError):
        check("a missing claude CLI raises",
              _raises(lambda: lift.claude("p", "m", sandbox)))

    with mock.patch.object(lift.subprocess, "run",
                           side_effect=subprocess.TimeoutExpired("claude", 1)):
        check("a timeout raises", _raises(lambda: lift.claude("p", "m", sandbox)))

    with mock.patch.object(lift.subprocess, "run",
                           return_value=_fake_run(returncode=1, stderr="boom")):
        check("a nonzero exit raises instead of returning stdout",
              _raises(lambda: lift.claude("p", "m", sandbox)))

    with mock.patch.object(lift.subprocess, "run", return_value=_fake_run(stdout="   ")):
        check("empty output raises", _raises(lambda: lift.claude("p", "m", sandbox)))

    with mock.patch.object(lift.subprocess, "run", return_value=_fake_run(stdout=" hi ")):
        check("a good call still returns its stdout",
              lift.claude("p", "m", sandbox) == "hi")


def _raises(fn) -> bool:
    """True when fn() raises ModelCallError."""
    try:
        fn()
    except lift.ModelCallError:
        return True
    except Exception:
        return False
    return False


def test_empty_response_would_have_scored_clean() -> None:
    """Why the above matters, pinned as a fact about the scorer."""
    verdicts = [r["verdict"] for r in lift.run_checks("", {"forbidden": [r"(?i)leverag"]})]
    check("an empty response passes every forbidden check", verdicts == ["PASS"], str(verdicts))


def test_missing_response_is_a_failure_not_a_skip() -> None:
    """Skipping shrinks one arm's denominator while the other keeps its own, so the two pass
    rates are computed over different totals and the lift between them compares nothing."""
    cases, _ = suite_from([case_line(checks={"forbidden": ["zzz"]}, assertions=[])])
    with tempfile.TemporaryDirectory() as tmp:
        outdir = Path(tmp)
        # Only the with_skill arm produced a response.
        dest = outdir / "a-case" / "with_skill"
        dest.mkdir(parents=True)
        (dest / "response.md").write_text("a clean answer", encoding="utf-8")

        # grade() reports the missing arm on stderr; swallow it so a passing test run
        # stays quiet inside scripts/preflight.sh.
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            totals, failures = lift.grade(cases, outdir, "grader-model", outdir)

    check("the missing arm is reported as a failure",
          len(failures) == 1 and "no response.md" in failures[0], str(failures))
    check("the missing arm scores nothing at all",
          totals["baseline"] == {"pass": 0, "total": 0}, str(totals))
    check("the arm that ran is still scored",
          totals["with_skill"]["total"] == 1, str(totals))


def test_report_withholds_lift_when_a_run_is_incomplete() -> None:
    """Two arms that answered different numbers of criteria cannot be subtracted."""
    totals = {"with_skill": {"pass": 4, "total": 4}, "baseline": {"pass": 1, "total": 2}}
    with tempfile.TemporaryDirectory() as tmp:
        outdir = Path(tmp)
        with contextlib.redirect_stdout(io.StringIO()):
            summary = lift.report(totals, outdir, "grader-model", ["baseline arm died"])
        on_disk = json.loads((outdir / "summary.json").read_text())

    check("no lift is computed for an incomplete run", summary["lift_points"] is None,
          str(summary))
    check("the summary records the run as incomplete", summary["complete"] is False)
    check("the failure is persisted for later reading",
          on_disk["failures"] == ["baseline arm died"], str(on_disk))

    with tempfile.TemporaryDirectory() as tmp:
        with contextlib.redirect_stdout(io.StringIO()):
            summary = lift.report(totals, Path(tmp), "grader-model", [])
    check("a complete run still reports a lift", summary["lift_points"] is not None,
          str(summary))


# -------------------------------------------------------------------- the shipped suite

def test_shipped_suite_is_clean() -> None:
    """The committed suite itself passes every structural check."""
    cases, errors = lift.load_suite()
    errors += lift.validate(cases, lift.load_skills())
    check("the committed suite has no structural failures", errors == [],
          "; ".join(e.message for e in errors))
    check("the committed suite is not empty", len(cases) > 0)
    check("every committed case scores something",
          all(c["checks"] or c["assertions"] for c in cases))


def main() -> int:
    """Run every test_* function, print the results, and return the exit code."""
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()

    for label in PASSED:
        print(f"  PASS  {label}")
    for label in FAILED:
        print(f"  FAIL  {label}", file=sys.stderr)

    if FAILED:
        print(f"\n{len(FAILED)} check(s) FAILED.", file=sys.stderr)
        return 1
    print(f"\nAll {len(PASSED)} checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
