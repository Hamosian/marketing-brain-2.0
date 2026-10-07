#!/usr/bin/env python3
"""Deterministic scoreboard and keep-or-revert judge for the skill optimizer loop.

`/skill-optimizer` improves skills in rounds: measure, pick the weakest, edit one,
measure again, keep the edit only if the numbers went up and nothing else went
down. This script is the "measure" and the "judge". It never calls a model and
never edits a file, so the loop cannot talk its way past it.

It reads the two signals the repo already produces:

  - scripts/audit_skill.py   authoring signals per skill (6 present/absent checks,
                             plus hard findings such as a description over the cap)
  - scripts/eval_routing.py  routing cases per skill (clear, ambiguous, weak-trigger)

and folds them into one priority number per skill (higher = fix first).

Usage:
  python3 scripts/skill_scoreboard.py                     # ranked table, worst first
  python3 scripts/skill_scoreboard.py --top 10            # just the worst 10
  python3 scripts/skill_scoreboard.py --snapshot F.json   # write the full board to a file
  python3 scripts/skill_scoreboard.py --compare BEFORE.json [AFTER.json]
      # judge a change. AFTER defaults to a fresh measurement of the working tree.
      # Prints KEEP, REVERT or NO-CHANGE with the reason.
      # Exit 0 = KEEP, 1 = REVERT (a regression), 2 = NO-CHANGE (nothing improved).

The deterministic signals are a floor, not the goal. They are regexes, so they
can be gamed (a stray "e.g." satisfies "has a worked example"). The loop's rules
in .claude/skills/skill-optimizer/SKILL.md forbid that; this script only
guarantees that nothing measurable got worse.

Stdlib only, no dependencies.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DESC_CAP = 1024
DESC_TIGHT = 950  # past this, any description edit has to cut as much as it adds

# Priority weights. A hard finding outranks everything, a routing miss outranks a
# missing authoring signal (a skill nobody reaches is worse than one written
# loosely), and a skill with no routing case at all is a small nudge.
W_HARD = 100
W_ROUTING_MISS = 8
W_MISSING_SIGNAL = 5
W_NO_CASE = 3


def _run_json(args: list[str]) -> object:
    out = subprocess.run(
        [sys.executable, *args], cwd=ROOT, capture_output=True, text=True, check=False
    )
    try:
        return json.loads(out.stdout)
    except json.JSONDecodeError:
        sys.stderr.write(out.stderr or out.stdout)
        raise SystemExit(f"could not parse JSON from {' '.join(args)}")


def measure() -> dict:
    audit = _run_json(["scripts/audit_skill.py", "--all", "--json"])
    routing = _run_json(["scripts/eval_routing.py", "--json"])

    board: dict[str, dict] = {}
    for row in audit:
        sig = row["signals"]
        board[row["skill"]] = {
            "signals": sum(1 for v in sig.values() if v),
            "missing": sorted(k for k, v in sig.items() if not v),
            "hard": list(row["hard"]),
            "description_len": row["description_len"],
            "cases": 0,
            "clear": 0,
            "misses": [],
            "steals": 0,
        }

    cases: dict[str, str] = {}
    for r in routing["results"]:
        # Keyed on the request text, not the line: adding a case shifts every line
        # below it, and a line-keyed compare would skip those cases silently.
        # eval_routing.py already fails the build on duplicate requests.
        key = r["request"]
        cases[key] = r["verdict"]
        s = board.get(r["expect"])
        if s is None:  # external target such as rivermind:ask
            continue
        s["cases"] += 1
        if r["verdict"] == "clear":
            s["clear"] += 1
        elif r["verdict"] != "external":
            s["misses"].append(r["request"])
            for rival in r.get("rivals", []):
                if rival in board:
                    board[rival]["steals"] += 1

    for s in board.values():
        s["priority"] = (
            W_HARD * len(s["hard"])
            + W_ROUTING_MISS * len(s["misses"])
            + W_MISSING_SIGNAL * len(s["missing"])
            + (W_NO_CASE if s["cases"] == 0 else 0)
        )
        s["desc_tight"] = s["description_len"] > DESC_TIGHT

    return {
        "skills": board,
        "cases": cases,
        "routing_errors": routing.get("errors", []),
        "totals": {
            "skills": len(board),
            "signals": sum(s["signals"] for s in board.values()),
            "signals_max": 6 * len(board),
            "hard": sum(len(s["hard"]) for s in board.values()),
            "cases_clear": sum(1 for v in cases.values() if v == "clear"),
            "cases_total": len(cases),
            "no_case": sum(1 for s in board.values() if s["cases"] == 0),
            "priority": sum(s["priority"] for s in board.values()),
        },
    }


def print_board(data: dict, top: int | None) -> None:
    t = data["totals"]
    print(
        f"Skill scoreboard: {t['skills']} skills | signals {t['signals']}/{t['signals_max']}"
        f" | routing clear {t['cases_clear']}/{t['cases_total']} | no case {t['no_case']}"
        f" | hard {t['hard']} | total priority {t['priority']}"
    )
    rows = sorted(data["skills"].items(), key=lambda kv: (-kv[1]["priority"], kv[0]))
    if top:
        rows = rows[:top]
    print(f"{'prio':>4}  {'sig':>3}  {'route':>5}  skill  (missing signals / notes)")
    for name, s in rows:
        route = f"{s['clear']}/{s['cases']}" if s["cases"] else "none"
        notes = list(s["missing"])
        if s["hard"]:
            notes.insert(0, "HARD: " + "; ".join(s["hard"]))
        if s["desc_tight"]:
            notes.append(f"desc {s['description_len']} (tight)")
        print(f"{s['priority']:>4}  {s['signals']:>3}  {route:>5}  {name}  ({', '.join(notes) or 'clean'})")


def judge(before: dict, after: dict) -> tuple[int, list[str], list[str]]:
    regressions: list[str] = []
    gains: list[str] = []

    if after["routing_errors"]:
        regressions.append(f"routing suite has structural errors: {after['routing_errors'][:3]}")

    for name, b in before["skills"].items():
        a = after["skills"].get(name)
        if a is None:
            regressions.append(f"{name}: skill disappeared")
            continue
        if a["signals"] < b["signals"]:
            lost = sorted(set(a["missing"]) - set(b["missing"]))
            regressions.append(f"{name}: lost signal(s) {lost}")
        elif a["signals"] > b["signals"]:
            got = sorted(set(b["missing"]) - set(a["missing"]))
            gains.append(f"{name}: gained {got}")
        new_hard = sorted(set(a["hard"]) - set(b["hard"]))
        if new_hard:
            regressions.append(f"{name}: new hard finding {new_hard}")
        if len(a["hard"]) < len(b["hard"]):
            gains.append(f"{name}: cleared a hard finding")

    for key, verdict in before["cases"].items():
        now = after["cases"].get(key)
        if now is None:
            regressions.append(f"routing case removed or reworded: {key}")
            continue
        if verdict == "clear" and now != "clear":
            regressions.append(f"routing case went {verdict} -> {now}: {key}")
        elif verdict not in ("clear", "external") and now == "clear":
            gains.append(f"routing case now clear: {key}")

    new_cases = set(after["cases"]) - set(before["cases"])
    covered = before["totals"]["no_case"] - after["totals"]["no_case"]
    if covered > 0:
        gains.append(f"{covered} skill(s) gained their first routing case")
    for key in sorted(new_cases):
        if after["cases"][key] not in ("clear", "external"):
            # A new case that lands ambiguous is honest information, not a
            # regression - but it must be named so the PR shows it.
            gains.append(f"(note) new case is {after['cases'][key]}: {key}")

    real_gains = [g for g in gains if not g.startswith("(note)")]
    if regressions:
        return 1, regressions, gains
    if not real_gains:
        return 2, regressions, gains
    return 0, regressions, gains


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--top", type=int)
    ap.add_argument("--json", action="store_true", help="print the full board as JSON")
    ap.add_argument("--snapshot", metavar="FILE", help="write the board to FILE")
    ap.add_argument("--compare", nargs="+", metavar="FILE", help="BEFORE.json [AFTER.json]")
    args = ap.parse_args()

    if args.compare:
        before = json.loads(Path(args.compare[0]).read_text())
        after = json.loads(Path(args.compare[1]).read_text()) if len(args.compare) > 1 else measure()
        code, regressions, gains = judge(before, after)
        verdict = {0: "KEEP", 1: "REVERT", 2: "NO-CHANGE"}[code]
        bt, at = before["totals"], after["totals"]
        print(f"VERDICT: {verdict}")
        print(
            f"  signals {bt['signals']} -> {at['signals']} | routing clear {bt['cases_clear']}/{bt['cases_total']}"
            f" -> {at['cases_clear']}/{at['cases_total']} | no case {bt['no_case']} -> {at['no_case']}"
            f" | priority {bt['priority']} -> {at['priority']}"
        )
        for r in regressions:
            print(f"  REGRESSION  {r}")
        for g in gains:
            print(f"  gain        {g}")
        return code

    data = measure()
    if args.snapshot:
        Path(args.snapshot).write_text(json.dumps(data, indent=1, sort_keys=True))
        print(f"wrote {args.snapshot}")
    if args.json:
        print(json.dumps(data, indent=1, sort_keys=True))
    else:
        print_board(data, args.top)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
