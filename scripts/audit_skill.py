#!/usr/bin/env python3
"""Deterministic authoring-quality signals for a SKILL.md.

This is the mechanical half of `/skill-audit`. It does NOT score a skill - it
surfaces the presence/absence of the things `references/agent-prompting.md` says a
reliable skill needs, so the model-in-the-loop half (see the skill's rubric.md) can
score authoring quality against real signals instead of eyeballing the file.

It is intentionally NOT a CI gate. Structure is already gated by
scripts/lint_agents.py + team-context-lint (frontmatter, tools, model pinning),
routing by scripts/eval_routing.py, and staleness by /health-check. This fills the
remaining gap: is the skill *well-written*.

    python3 scripts/audit_skill.py good-morning        # one skill by name
    python3 scripts/audit_skill.py --all               # every skill, summary table
    python3 scripts/audit_skill.py --all --json        # machine-readable

Exit code is 0 unless --strict is passed, in which case any skill missing a
hard-signal (no description, name/dir mismatch, description over the 1024 cap)
exits non-zero. Stdlib only, no dependencies.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SKILLS_DIR = Path(".claude/skills")
DESC_CAP = 1024  # matches team-context-lint; the router's only signal
DESC_NEAR = 900  # warn before the hard cap so authors trim early
BODY_OFFLOAD_LINES = 400  # a body past this with no sibling detail file is a disclosure smell

# Each signal is (key, human label, agent-prompting block it maps to, regex over the body).
# Case-insensitive, multiline. Absence is the finding; presence is not proof of quality,
# only that the author left the model something to score.
BODY_SIGNALS: list[tuple[str, str, str, str]] = [
    ("output_schema", "Output schema / contract", "block 5",
     r"^#+.*\b(output|schema|contract|format|deliverable)\b"),
    # A bare fence is not a worked example - a shell block or output template is not an
    # input-to-output example. Require an explicit example heading, "for example"/"e.g.",
    # a labelled example, a same-line input->output pairing, or separate labelled
    # Input:/Output: blocks (bounded so unrelated labels far apart do not match).
    ("examples", "Worked example", "block 4",
     r"^#+.*\bexamples?\b|\bfor example\b|\be\.g\.|\bexample (input|output|request|call|run)\b"
     r"|\binput\b[^\n]*(->|→|then)[^\n]*\boutput\b"
     r"|\binput\b\s*:[\s\S]{0,400}?\boutput\b\s*:"),
    ("constraints", "Constraints & defaults", "block 3",
     r"\b(never|do not|don't|must not|if (unclear|missing|absent)|default to|fall ?back|abort)\b"),
    ("done_when", "Stated bar / done-when", "block 1/6",
     r"\bdone when\b|\bsuccess (looks like|is)\b|\bthe bar\b|\bacceptance\b"),
    ("boundary", "Scope boundary", "review",
     r"^#+.*\b(does not|not own|out of scope|non-goals?)\b|\bthis skill does not\b"),
    ("grounding", "Grounding / anti-invention", "review",
     r"\b(cite|quote|grounded|do not invent|never invent|from the (source|input)|source of truth)\b"),
]

DESC_TRIGGER_RE = re.compile(
    r"\btrigger(ed|s)?\b|\buse (this )?(skill )?when\b|\"[^\"]+\"|/[a-z][a-z0-9-]+", re.I
)


def parse_frontmatter(text: str) -> tuple[dict[str, str], int]:
    """Return (folded key:value frontmatter, line index where the body starts).

    Folds continuation lines and strips block-scalar indicators (`>`, `>-`, `|`) the same
    way scripts/eval_routing.py does, so a folded `description: >-` value is read as its
    full content - a first-line-only read reports ~2 chars for the repo's folded
    descriptions and would misjudge the description-length and trigger signals.
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, 0
    fm: dict[str, str] = {}
    key: str | None = None
    for i in range(1, len(lines)):
        line = lines[i]
        if line.strip() == "---":
            return fm, i + 1
        if line and not line[0].isspace() and ":" in line:
            key, _, value = line.partition(":")
            key = key.strip()
            value = value.strip()
            if re.fullmatch(r"[|>][0-9]*[+-]?", value):  # lone block-scalar indicator
                value = ""
            fm[key] = value
        elif key and line.strip():
            fm[key] = f"{fm[key]} {line.strip()}".strip()
    return fm, 0  # unterminated frontmatter; treat as no body split


def audit_one(skill_dir: Path) -> dict:
    name = skill_dir.name
    md = skill_dir / "SKILL.md"
    text = md.read_text(encoding="utf-8", errors="ignore")
    fm, body_start = parse_frontmatter(text)
    body = "\n".join(text.splitlines()[body_start:])

    desc = fm.get("description", "")
    hard: list[str] = []
    warn: list[str] = []

    if "---" not in text.splitlines()[:1] and not fm:
        hard.append("no YAML frontmatter")
    if not fm.get("name"):
        hard.append("frontmatter missing name:")
    elif fm["name"] != name:
        hard.append(f"name '{fm['name']}' != directory '{name}'")
    if not desc:
        hard.append("frontmatter missing description:")
    if len(desc) > DESC_CAP:
        hard.append(f"description {len(desc)} chars over the {DESC_CAP} cap")
    elif len(desc) > DESC_NEAR:
        warn.append(f"description {len(desc)} chars, approaching the {DESC_CAP} cap")
    if desc and not DESC_TRIGGER_RE.search(desc):
        warn.append("description has no trigger phrases/examples (block 4 on the routing surface)")

    signals: dict[str, bool] = {}
    for key, label, block, pattern in BODY_SIGNALS:
        present = re.search(pattern, body, re.I | re.M) is not None
        signals[key] = present
        if not present:
            warn.append(f"no {label.lower()} ({block})")

    # Progressive disclosure: a long body with no sibling detail file to offload into.
    body_lines = len(body.splitlines())
    sibling_detail = [
        p for p in skill_dir.rglob("*")
        if p.is_file() and p.name != "SKILL.md" and p.suffix in {".md", ".py", ".json", ".csv"}
    ]
    if body_lines > BODY_OFFLOAD_LINES and not sibling_detail:
        warn.append(
            f"SKILL.md is {body_lines} lines with no knowledge/ or reference file - "
            "consider progressive disclosure (block 2)"
        )

    return {
        "skill": name,
        "description_len": len(desc),
        "body_lines": body_lines,
        "sibling_detail_files": len(sibling_detail),
        "signals": signals,
        "hard": hard,
        "warn": warn,
    }


def all_skill_dirs() -> list[Path]:
    return [p.parent for p in sorted(SKILLS_DIR.glob("*/SKILL.md"))]


def discover(names: list[str]) -> list[Path]:
    dirs = all_skill_dirs()
    if not names:
        return dirs
    # Resolve each requested name by directory, then by frontmatter `name:` identity -
    # the same routing identity eval_routing.py uses - so a skill whose name and
    # directory disagree (itself a hard finding) is still selectable by its routing name.
    by_dir = {d.name: d for d in dirs}
    by_name: dict[str, Path] = {}
    for d in dirs:
        fm, _ = parse_frontmatter((d / "SKILL.md").read_text(encoding="utf-8", errors="ignore"))
        if fm.get("name"):
            by_name.setdefault(fm["name"], d)
    resolved = []
    for n in names:
        d = by_dir.get(n) or by_name.get(n)
        if not d:
            sys.exit(f"No such skill: {n} (no directory or frontmatter name matches under {SKILLS_DIR})")
        resolved.append(d)
    return resolved


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("names", nargs="*", help="skill name(s); omit with --all")
    parser.add_argument("--all", action="store_true", help="audit every skill")
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    parser.add_argument("--strict", action="store_true", help="exit non-zero on any hard finding")
    args = parser.parse_args()

    if not args.names and not args.all:
        parser.error("pass one or more skill names, or --all")
    if args.names and args.all:
        parser.error("pass skill names or --all, not both")

    reports = [audit_one(d) for d in discover(args.names)]

    if args.json:
        print(json.dumps(reports, indent=2))
    else:
        for r in reports:
            filled = sum(r["signals"].values())
            total = len(r["signals"])
            flag = "!!" if r["hard"] else ("~" if r["warn"] else "OK")
            print(f"[{flag}] {r['skill']}  signals {filled}/{total}  "
                  f"desc {r['description_len']}  body {r['body_lines']}L")
            for h in r["hard"]:
                print(f"     HARD: {h}")
            for w in r["warn"]:
                print(f"     warn: {w}")
        if len(reports) > 1:
            hard_n = sum(1 for r in reports if r["hard"])
            clean_n = sum(1 for r in reports if not r["hard"] and not r["warn"])
            print(f"\n{len(reports)} skills - {clean_n} clean, {hard_n} with hard findings.")

    if args.strict and any(r["hard"] for r in reports):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
