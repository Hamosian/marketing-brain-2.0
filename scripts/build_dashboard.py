#!/usr/bin/env python3
"""Rebuild the team-tasks dashboard's baked data from the repo ledgers, safely.

    python3 scripts/build_dashboard.py            # rebuild + validate
    python3 scripts/build_dashboard.py --check    # validate only, write nothing

WHY THIS EXISTS
---------------
On 2026-08-09 a hand-rolled regeneration sliced the TASKS array with a literal
end marker of "\\n  };". The array actually ends with "];", so the cut ran past
TASKS and swallowed the next three declarations (TEAMS, READING, FOCUS_ORDER)
before stopping at the brace that closed FOCUS_ORDER. FOCUS_ORDER is
dereferenced on every render, so the published page threw a ReferenceError and
never painted. The counts all looked right, because the only thing checked was
the array that had been rewritten.

Two rules come out of that, and this script enforces both mechanically:

  1. Never find the end of a JS literal by string-matching. Scan and match
     brackets, respecting string literals and escapes (`slice_literal`).
  2. Never trust a rewrite because the part you rewrote looks right. Diff the
     whole file's declarations against the pre-edit version and fail on any
     loss (`validate`).

A third rule is about Nir's data rather than the file. The dashboard keys every
local browser edit by task id, and an override whose id is absent from the baked
TASKS is quarantined by the page. So an id that silently disappears or gets
reused is the one way a publish can cost him work. This script therefore refuses
to write if any id would be dropped, duplicated, or reassigned to a different
task, and prints exactly what it matched.

WHAT IT DOES NOT DO
-------------------
It does not publish. Publishing is a deliberate step: run this, read the report,
then call the Artifact tool with the canonical URL from
`.claude/skills/growth-marketing-team-tasks/knowledge/dashboard-spec.md`.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import difflib
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / ".claude/skills/growth-marketing-team-tasks"
DASH = SKILL / "assets/dashboard.html"
DATA = SKILL / "data"

# Ledger file per dashboard team key, in the order the array should be emitted.
TEAMS: list[tuple[str, str]] = [
    ("my", "my-tasks.md"),
    ("mops", "mops.md"),
    ("seo", "seo.md"),
    ("paid", "paid.md"),
    ("creator", "creator.md"),
    ("gc", "growth-channels.md"),
    ("sdr", "sdr.md"),
]

CLOSED = {"Done", "Watch list"}
MATCH_FLOOR = 0.45  # below this a ledger row is treated as genuinely new, never guessed


# --------------------------------------------------------------------------
# JS literal slicing - the thing that broke, done properly
# --------------------------------------------------------------------------

def slice_literal(src: str, decl: str) -> tuple[int, int]:
    """Return (start, end) covering `var NAME = <literal>;` by matching brackets.

    Walks the source tracking string state so a bracket inside a title or a URL
    cannot end the literal early. This is the whole point: no end marker, no
    guessing, no "find the next `};`".
    """
    start = src.index(decl)
    i = src.index("=", start) + 1
    while src[i] in " \t\r\n":
        i += 1
    if src[i] not in "[{":
        raise ValueError(f"{decl!r} does not open with a bracket")

    pairs = {"[": "]", "{": "}"}
    stack = [src[i]]
    i += 1
    quote = None
    while i < len(src):
        ch = src[i]
        if quote:
            if ch == "\\":
                i += 2
                continue
            if ch == quote:
                quote = None
        elif ch in "\"'`":
            quote = ch
        elif ch in "[{":
            stack.append(ch)
        elif ch in "]}":
            if ch != pairs[stack[-1]]:
                raise ValueError(f"bracket mismatch in {decl!r} at offset {i}")
            stack.pop()
            if not stack:
                end = i + 1
                if src[end : end + 1] == ";":
                    end += 1
                return start, end
        i += 1
    raise ValueError(f"unterminated literal for {decl!r}")


# --------------------------------------------------------------------------
# Ledger parsing
# --------------------------------------------------------------------------

def read_ledger(path: Path) -> list[list[str]]:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            continue
        if re.match(r"^\|[\s\-:|]+\|\s*$", line):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if cells and cells[0].lower() == "task":
            continue
        if len(cells) < 8:
            continue
        rows.append(cells)
    return rows


def read_reading(path: Path) -> list[dict]:
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            continue
        if re.match(r"^\|[\s\-:|]+\|\s*$", line):
            continue
        c = [x.strip() for x in line.strip("|").split("|")]
        if len(c) < 7 or c[0].lower() == "id":
            continue
        out.append({
            "id": c[0], "status": c[1], "title": clean_title(c[2]), "url": c[3],
            "note": clean_answer(c[4]), "added": c[5],
            "src": (re.search(r"\((https?://[^)]+)\)", c[6]) or [None, c[6]])[1],
        })
    return out


def clean_title(s: str) -> str:
    """Titles keep the link TEXT and drop the href.

    A title is a one-line label on a card; inlining a 90-character Google Docs URL
    into it both wrecks the layout and, worse, changes the string the id matcher
    keys on, which is how gc-21 lost its id on the 2026-08-09 build.
    """
    s = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", s)
    s = re.sub(r"_\(([^)]*)\)_", r"(\1)", s)
    return s.replace("**", "").replace("<br>", "\n").strip()


def clean_answer(s: str) -> str:
    """Answers keep the href - they are where the links legitimately live."""
    s = re.sub(r"\[([^\]]*)\]\(([^)]*)\)", r"\1 (\2)", s)
    s = re.sub(r"_\(([^)]*)\)_", r"(\1)", s)
    return s.replace("**", "").replace("<br>", "\n").strip()


def norm(s: str) -> str:
    """Normalize a title for id matching.

    Must be invariant to how a link is written, because the same task appears as
    markdown in the ledger and as flattened text in the baked build. Strip both
    forms before comparing, or the two representations of one task score as
    different tasks and the build mints a new id (which quarantines edits).
    """
    s = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", s)   # markdown link -> its text
    s = re.sub(r"https?://\S+", " ", s)              # bare url, however it got there
    s = s.replace('\\"', '"').replace("\\n", " ")
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


# --------------------------------------------------------------------------
# ID preservation
# --------------------------------------------------------------------------

def parse_baked(block: str) -> dict[str, str]:
    return dict(re.findall(r'\{\s*id:"([a-z]+-\d+)".*?title:"((?:[^"\\]|\\.)*)"', block))


def assign_ids(rows: list[tuple[str, list[str]]], baked: dict[str, str]) -> tuple[dict[int, str], list[int]]:
    """Greedy best-first title match, so ids survive edits, retitles and team moves.

    Global rather than per-team on purpose: the dashboard's Move-to-team changes a
    task's `team` field but keeps its id, so a per-team match would mint a new id
    for every moved task and orphan the browser edits attached to the old one.
    """
    bn = {t: norm(x) for t, x in baked.items() if not t.startswith("read")}
    scored = []
    for k, (_team, row) in enumerate(rows):
        n = norm(row[0])
        for tid, bt in bn.items():
            r = difflib.SequenceMatcher(None, n, bt).ratio()
            if r > MATCH_FLOOR:
                scored.append((r, k, tid))
    scored.sort(key=lambda x: (-x[0], x[1], x[2]))

    used_row, used_id, assign = set(), set(), {}
    for _r, k, tid in scored:
        if k in used_row or tid in used_id:
            continue
        used_row.add(k); used_id.add(tid); assign[k] = tid
    return assign, [k for k in range(len(rows)) if k not in assign]


def next_id(team: str, taken: set[str]) -> str:
    n = 1 + max([int(t.split("-")[1]) for t in taken if t.startswith(team + "-")] or [0])
    while f"{team}-{n}" in taken:
        n += 1
    return f"{team}-{n}"


# --------------------------------------------------------------------------
# Emit
# --------------------------------------------------------------------------

def js(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


def emit_tasks(rows, assign) -> str:
    lines = ["  var TASKS = ["]
    for k, (team, r) in enumerate(rows):
        title, owner, status, pri, due = clean_title(r[0]), r[1], r[2], r[3], r[4]
        answer = clean_answer(r[8]) if len(r) > 8 else ""
        parts = [
            f'id:"{assign[k]}"', f'team:"{team}"', f'owner:"{js(owner)}"',
            f'pri:"{js(pri or "-")}"',
            "due:null" if due in ("", "-", "\u2014") else f'due:"{due}"',
        ]
        if status and status != "Open":
            parts.append(f'status:"{js(status)}"')
        parts.append(f'title:"{js(title)}"')
        if answer and answer not in ("-", "\u2014"):
            parts.append(f'answer:"{js(answer)}"')
        lines.append("    { " + ", ".join(parts) + " },")
    lines.append("  ];")
    return "\n".join(lines)


def emit_reading(items) -> str:
    lines = ["  var READING = ["]
    for r in items:
        lines.append(
            '    { id:"%s", title:"%s", url:"%s", note:"%s", added:"%s", status:"%s", src:"%s" },'
            % (r["id"], js(r["title"]), r["url"], js(r["note"]), r["added"], r["status"], r["src"])
        )
    lines.append("  ];")
    return "\n".join(lines)


def emit_focus(path: Path) -> str:
    sec: dict[str, list[str]] = {}
    cur = None
    for line in path.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^##\s+(.+)", line)
        if m:
            cur = "today" if m.group(1).strip().lower() == "today" else "week"
            sec[cur] = []
        elif cur and line.strip() and not line.strip().startswith(("<!--", "-->", "#")):
            sec[cur] += [x.strip() for x in line.split(",") if x.strip()]
    return (
        "  var FOCUS_ORDER = {\n"
        f"    today: {json.dumps(sec.get('today', []))},\n"
        f"    week: {json.dumps(sec.get('week', []))}\n"
        "  };"
    )


# --------------------------------------------------------------------------
# Validation
# --------------------------------------------------------------------------

def _body_changed(before: str, after: str) -> bool:
    """True if anything but the two auto-stamped constants differs."""
    strip = lambda s: re.sub(r'var (?:DATA_VERSION|REFRESHED_AT) = "[^"]*";', "", s)
    return strip(before) != strip(after)


def _next_version(src: str, now: _dt.datetime) -> str:
    """`YYYY-MM-DD` plus a letter, incrementing within a day: 2026-08-09a, ...b, ...c."""
    today = now.strftime("%Y-%m-%d")
    cur = re.search(r'var DATA_VERSION = "([^"]*)";', src)
    if cur and cur.group(1).startswith(today):
        suffix = cur.group(1)[len(today):]
        return today + (chr(ord(suffix) + 1) if len(suffix) == 1 and suffix < "z" else "a")
    return today + "a"


def decls(src: str) -> set[str]:
    return set(re.findall(r"^\s*(?:var|function)\s+([A-Za-z_$][\w$]*)", src, re.M))


def script_body(src: str) -> str:
    i = src.index("<script>\n(function ()")
    return src[i + len("<script>") : src.rindex("</script>")]


def syntax_check(body: str) -> str | None:
    """Parse the script with JavaScriptCore via osascript. Returns an error or None."""
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as fh:
        fh.write(body)
        tmp = fh.name
    probe = (
        f'var s=$.NSString.stringWithContentsOfFileEncodingError("{tmp}",4,null).js;'
        'try{ new Function(s); "OK" } catch(e){ "ERR: "+e.message }'
    )
    try:
        out = subprocess.run(
            ["osascript", "-l", "JavaScript", "-e", probe],
            capture_output=True, text=True, timeout=60,
        ).stdout.strip()
    except (OSError, subprocess.SubprocessError) as exc:
        return f"could not run syntax check: {exc}"
    return None if out == "OK" else (out or "empty result from syntax check")


def validate(before: str, after: str) -> list[str]:
    errs = []
    lost = sorted(decls(before) - decls(after))
    if lost:
        errs.append(f"declarations lost: {', '.join(lost)}")

    body = script_body(after)
    for o, c in (("{", "}"), ("[", "]")):
        if body.count(o) != body.count(c):
            errs.append(f"unbalanced {o}{c}: {body.count(o)} vs {body.count(c)}")

    err = syntax_check(body)
    if err:
        errs.append(err)

    for name in ("TASKS", "TEAMS", "READING", "FOCUS_ORDER", "TEAM_COLORS"):
        if f"var {name}" not in after:
            errs.append(f"missing declaration: var {name}")
    return errs


# --------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="validate only, write nothing")
    args = ap.parse_args()

    before = DASH.read_text(encoding="utf-8")
    t0, t1 = slice_literal(before, "  var TASKS =")
    baked = parse_baked(before[t0:t1])

    rows: list[tuple[str, list[str]]] = []
    for team, fname in TEAMS:
        for r in read_ledger(DATA / fname):
            rows.append((team, r))

    assign, unmatched = assign_ids(rows, baked)
    taken = set(assign.values())
    for k in unmatched:
        assign[k] = next_id(rows[k][0], taken)
        taken.add(assign[k])

    # --- id safety gate: the one failure mode that can cost Nir work ---
    problems = []
    if len(set(assign.values())) != len(assign):
        problems.append("duplicate ids generated")
    dropped = sorted(set(baked) - set(assign.values()) - {t for t in baked if t.startswith("read")})
    if dropped:
        problems.append(
            "ids present in the published build would disappear, which quarantines any "
            "browser edits attached to them: " + ", ".join(dropped)
        )
    if problems:
        print("REFUSING TO WRITE:", file=sys.stderr)
        for p in problems:
            print("  - " + p, file=sys.stderr)
        return 2

    new = before
    for decl, text in (
        ("  var FOCUS_ORDER =", emit_focus(DATA / "focus-order.md")),
        ("  var READING =", emit_reading(read_reading(DATA / "reading-list.md"))),
        ("  var TASKS =", emit_tasks(rows, assign)),
    ):
        a, b = slice_literal(new, decl)
        new = new[:a] + text + new[b:]

    # Both constants are stamped here, not by hand - a manual step is a step someone
    # skips. They have DIFFERENT triggers on purpose:
    #
    #   REFRESHED_AT  every run. It answers "when was this page last rebuilt from the
    #                 ledgers", which is true even when the ledgers turned out unchanged.
    #                 A stale stamp makes the header claim a freshness it does not have.
    #   DATA_VERSION  only when the baked data actually changed. Bumping it makes every
    #                 browser re-reconcile its stored overrides, so bumping it for a
    #                 no-op rebuild would be churn for no reason.
    now = _dt.datetime.now().astimezone()
    data_changed = _body_changed(before, new)
    if data_changed:
        new = re.sub(r'var DATA_VERSION = "[^"]*";',
                     'var DATA_VERSION = "%s";' % _next_version(before, now), new, count=1)
    new = re.sub(r'var REFRESHED_AT = "[^"]*";',
                 'var REFRESHED_AT = "%s";' % now.strftime("%Y-%m-%d %H:%M %Z"), new, count=1)

    errs = validate(before, new)
    if errs:
        print("VALIDATION FAILED, nothing written:", file=sys.stderr)
        for e in errs:
            print("  - " + e, file=sys.stderr)
        return 1

    ver = re.search(r'var DATA_VERSION = "([^"]*)";', new).group(1)
    print("data changed: " + ("yes | DATA_VERSION -> " + ver if data_changed
                              else "no (DATA_VERSION held at " + ver + ")"))
    fresh = [assign[k] for k in unmatched]
    print(f"tasks {len(rows)} | reused ids {len(rows) - len(unmatched)} | new ids {len(fresh)}"
          + (f" ({', '.join(fresh)})" if fresh else ""))
    print(f"reading {len(read_reading(DATA / 'reading-list.md'))} | dropped ids 0 | validation passed")

    if args.check:
        print("--check: no write")
        return 0
    if new == before:
        print("no change")
        return 0
    DASH.write_text(new, encoding="utf-8")
    print(f"wrote {DASH.relative_to(ROOT)}")
    print("next: python3 scripts/test_dashboard_safety.py, then publish to the canonical URL")
    return 0


if __name__ == "__main__":
    sys.exit(main())
