#!/usr/bin/env python3
"""Regenerate the dashboard's baked arrays from the ledgers, and stamp REFRESHED_AT.

The spec (knowledge/dashboard-spec.md) has documented this script since 2026-08;
until 2026-08-16 it did not exist and the arrays + REFRESHED_AT were hand-edited,
which is exactly how the timestamp drifted (stamped in the morning, forgotten on
the afternoon edit). This makes the refresh mechanical:

  python3 scripts/build_dashboard.py            # rebuild + stamp, from the skill dir
  python3 scripts/build_dashboard.py --check    # exit 1 if a rebuild would change data

What it does, in order:
  1. Parses the seven team ledgers (data/*.md) and the current baked TASKS array.
  2. Matches ledger rows to baked entries by team + normalized title (markdown
     links stripped), positionally as a fallback. Matched rows KEEP their id and
     their baked title/answer text - ids must never be renumbered (the browser's
     orphan quarantine treats a vanished id as a publishing accident), and baked
     titles are sometimes lightly edited (md link -> text), which the browser's
     soft-match sync relies on. Mechanical fields (owner, pri, due, status) are
     always taken from the ledger.
  3. A matched row whose ledger ANSWER meaningfully changed gets its answer
     re-baked mechanically (<br> -> newline, [text](url) -> url in answers,
     ** stripped). New rows are appended with the next free per-team id.
  4. Rebuilds READING from data/reading-list.md, FOCUS_ORDER from
     data/focus-order.md, and ACTIONS + ACTIONS_DATE from data/today-actions.md
     (the chief-of-staff brief's act-today rows; missing file = no actions).
  5. Stamps REFRESHED_AT with the current time (always), and bumps DATA_VERSION
     (YYYY-MM-DDx) ONLY when the baked data actually changed - a version bump
     makes every browser run reconcileWithLedger(), so a pure timestamp restamp
     must not trigger it.
  6. Runs scripts/validate_tasks.py and fails loudly if it fails.

It never touches ACK_TOKEN: that is the paste-sync handshake and only an applying
run may raise it.
"""
import argparse
import datetime
import functools
import json
import re
import subprocess
import sys
from pathlib import Path

json.dumps = functools.partial(json.dumps, ensure_ascii=False)  # keep em-dashes literal, matching the hand-baked file

SKILL = Path(__file__).resolve().parent.parent
DATA = SKILL / "data"
HTML = SKILL / "assets" / "dashboard.html"

TEAMS = [  # (ledger file, team key) - ledger order is the baked order
    ("my-tasks.md", "my"),
    ("mops.md", "mops"),
    ("seo.md", "seo"),
    ("paid.md", "paid"),
    ("creator.md", "creator"),
    ("growth-channels.md", "gc"),
    ("sdr.md", "sdr"),
]
MD_LINK = re.compile(r"\[([^\]]*)\]\(([^)\s]+)\)")


# ---------- parsing ----------

def ledger_rows(path):
    rows = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line.startswith("|") or line.startswith("|---") or line.startswith("| Task"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        cells = ["-" if c == "\u2014" else c for c in cells]  # legacy em-dash "unset" cells
        if len(cells) < 8:
            continue
        row = dict(zip(
            ["title", "owner", "status", "pri", "due", "source", "added", "updated"], cells))
        row["answer"] = cells[8] if len(cells) > 8 else "-"
        rows.append(row)
    return rows


def baked_entries(html):
    """Parse the existing TASKS array into dicts, preserving exact title/answer text."""
    start = html.index("var TASKS = [")
    end = html.index("];", start)
    entries = []
    for line in html[start:end].splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        e = {}
        for key in ("id", "team", "owner", "pri", "status", "title", "answer", "due"):
            m = re.search(r'\b%s:("(?:[^"\\]|\\.)*"|null)' % key, line)
            if m:
                e[key] = None if m.group(1) == "null" else json.loads(m.group(1))
        if e.get("id"):
            entries.append(e)
    return entries


# ---------- text transforms (ledger markdown -> baked plain text) ----------

def bake_title(t):
    return MD_LINK.sub(r"\1", t).strip()


def bake_answer(a):
    if not a or a.strip() in ("-", "\u2014", ""):
        return None
    a = a.replace("<br>", "\n")
    a = MD_LINK.sub(r"\2", a)          # answers keep the URL, not the anchor text
    a = a.replace("**", "")
    return a.strip()


def norm(s):
    """Loose comparison key: md links stripped both ways, punctuation collapsed."""
    if s is None:
        return ""
    s = MD_LINK.sub(r"\1", s)
    s = re.sub(r"https?://\S+", "", s)
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


# ---------- serialization (matches the hand-baked format exactly) ----------

def emit(e):
    parts = ["id:%s" % json.dumps(e["id"]), "team:%s" % json.dumps(e["team"]),
             "owner:%s" % json.dumps(e["owner"]), "pri:%s" % json.dumps(e["pri"]),
             "due:%s" % (json.dumps(e["due"]) if e["due"] else "null")]
    if e.get("status") and e["status"] != "Open":
        parts.append("status:%s" % json.dumps(e["status"]))
    parts.append("title:%s" % json.dumps(e["title"]))
    if e.get("answer"):
        parts.append("answer:%s" % json.dumps(e["answer"]))
    return "    { %s }," % ", ".join(parts)


def build_tasks(old):
    by_team_old = {}
    for e in old:
        by_team_old.setdefault(e["team"], []).append(e)
    max_id = {}
    for e in old:
        n = int(e["id"].split("-")[1])
        max_id[e["team"]] = max(max_id.get(e["team"], 0), n)

    out, warnings = [], []
    for fname, team in TEAMS:
        olds = list(by_team_old.get(team, []))
        used = set()
        for row in ledger_rows(DATA / fname):
            key = norm(row["title"])
            match = next((o for o in olds if id(o) not in used and norm(o["title"]) == key), None)
            if match is None and olds:
                # Positional fallback for RENAMED rows: the next unused baked entry, in
                # order, if its old title is similar enough to still be the same task
                # (a rename usually preserves most of the string). This keeps the id
                # stable through a rename instead of drop+renumber, which would strand
                # the browser's pending edits for that id in the orphan quarantine.
                candidates = [o for o in olds if id(o) not in used]
                if candidates:
                    import difflib
                    old_key = norm(candidates[0]["title"])
                    # A rename that EXTENDS the old title ("Joto retro" -> "Joto retro
                    # and the PR suggestion, ready for the meeting with Abel") is the
                    # same task by construction, but scores far below the ratio
                    # threshold because the added scope dominates the string. Without
                    # this prefix rule such a row is dropped and renumbered, which
                    # strands the browser's pending edits for the old id in the orphan
                    # quarantine. Guard the prefix with a minimum length so a two-word
                    # stub does not swallow an unrelated row. (2026-09-01)
                    prefix_extends = len(old_key) >= 8 and key.startswith(old_key)
                    ratio = difflib.SequenceMatcher(None, old_key, key).ratio()
                    if prefix_extends or ratio >= 0.55:
                        match = candidates[0]
            due = row["due"] if re.match(r"\d{4}-\d{2}-\d{2}", row["due"]) else None
            if match:
                used.add(id(match))
                renamed = norm(match["title"]) != key
                e = {"id": match["id"], "team": team, "owner": row["owner"],
                     "pri": row["pri"], "due": due, "status": row["status"],
                     # unchanged rows keep the baked (possibly editorially trimmed)
                     # title; a real rename takes the new ledger title
                     "title": bake_title(row["title"]) if renamed else match["title"]}
                if renamed:
                    warnings.append("RENAMED %s: %s" % (match["id"], e["title"][:60]))
                old_ans, new_ans = match.get("answer"), bake_answer(row["answer"])
                # keep the baked (possibly editorially trimmed) answer unless the
                # ledger answer meaningfully changed
                e["answer"] = old_ans if norm(old_ans) == norm(new_ans) else new_ans
            else:
                max_id[team] = max_id.get(team, 0) + 1
                e = {"id": "%s-%d" % (team, max_id[team]), "team": team,
                     "owner": row["owner"], "pri": row["pri"], "due": due,
                     "status": row["status"], "title": bake_title(row["title"]),
                     "answer": bake_answer(row["answer"])}
                warnings.append("NEW %s: %s" % (e["id"], e["title"][:70]))
            out.append(e)
        for o in olds:
            if id(o) not in used:
                warnings.append("DROPPED (no ledger row): %s %s" % (o["id"], o["title"][:60]))
    return out, warnings


def build_reading():
    lines = []
    for r in ledger_rows_generic(DATA / "reading-list.md",
                                 ["id", "status", "title", "url", "note", "added", "source"]):
        src = MD_LINK.search(r["source"])
        lines.append("    { %s }," % ", ".join([
            "id:%s" % json.dumps(r["id"]),
            "title:%s" % json.dumps(bake_title(r["title"])),
            "url:%s" % json.dumps(r["url"]),
            "note:%s" % json.dumps(bake_answer(r["note"]) or ""),
            "added:%s" % json.dumps(r["added"]),
            "status:%s" % json.dumps(r["status"]),
            "src:%s" % json.dumps(src.group(2) if src else r["source"]),
        ]))
    return lines


def ledger_rows_generic(path, cols):
    rows = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line.startswith("|") or line.startswith("|---") or line.startswith("| id"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) >= len(cols):
            rows.append(dict(zip(cols, cells)))
    return rows


def build_actions():
    """Bake data/today-actions.md (the chief-of-staff brief's act-today rows) into
    ACTIONS + ACTIONS_DATE. Missing file or empty table = no actions, never an error."""
    path = DATA / "today-actions.md"
    if not path.exists():
        return "", []
    text = path.read_text()
    m = re.search(r"<!--\s*date:\s*(\d{4}-\d{2}-\d{2})\s*-->", text)
    date = m.group(1) if m else ""
    lines = []
    for r in ledger_rows_generic(path, ["title", "clock", "who", "link", "age", "move"]):
        if r["title"].lower() == "action":
            continue
        link = MD_LINK.search(r["link"])
        url = link.group(2) if link else (r["link"] if r["link"].startswith("http") else "")
        lines.append("    { %s }," % ", ".join([
            "title:%s" % json.dumps(bake_title(r["title"])),
            "clock:%s" % json.dumps(r["clock"] if r["clock"] not in ("-", "\u2014") else ""),
            "who:%s" % json.dumps(r["who"] if r["who"] not in ("-", "\u2014") else ""),
            "link:%s" % json.dumps(url),
            "age:%s" % json.dumps(r["age"] if r["age"] not in ("-", "\u2014") else ""),
            "move:%s" % json.dumps(r["move"] if r["move"] not in ("-", "\u2014") else ""),
        ]))
    return date, lines


def build_focus():
    text = (DATA / "focus-order.md").read_text()
    def ids(section):
        m = re.search(r"## %s\n([^\n#]*)" % section, text)
        return [i.strip() for i in m.group(1).split(",") if i.strip()] if m else []
    return ids("Today"), ids("This week")


# ---------- assembly ----------

def replace_block(html, marker, close, new_body):
    start = html.index(marker) + len(marker)
    end = html.index(close, start)
    return html[:start] + "\n" + new_body + "\n" + html[end:]


def next_version(current, changed, today):
    if not changed:
        return current
    if current.startswith(today):
        suffix = current[len(today):] or "a"
        return today + chr(ord(suffix[-1]) + 1)
    return today + "a"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true",
                    help="exit 1 if a rebuild would change baked data; writes nothing")
    args = ap.parse_args()

    html = HTML.read_text()
    old_entries = baked_entries(html)
    tasks, warnings = build_tasks(old_entries)
    tasks_body = "\n".join(emit(e) for e in tasks)
    reading_body = "\n".join(build_reading())
    today_ids, week_ids = build_focus()
    focus_body = ("    today: [%s],\n    week: [%s]" % (
        ", ".join(json.dumps(i) for i in today_ids),
        ", ".join(json.dumps(i) for i in week_ids)))

    new_html = replace_block(html, "var TASKS = [", "  ];", tasks_body)
    new_html = replace_block(new_html, "var READING = [", "  ];", reading_body)
    new_html = replace_block(new_html, "var FOCUS_ORDER = {", "  };", focus_body)
    actions_date, actions_lines = build_actions()
    new_html = replace_block(new_html, "var ACTIONS = [", "  ];", "\n".join(actions_lines))
    new_html = re.sub(r'var ACTIONS_DATE = "[^"]*";',
                      'var ACTIONS_DATE = "%s";' % actions_date, new_html)

    changed = new_html != html
    for w in warnings:
        print("  " + w)
    if args.check:
        print("check: baked data %s" % ("DIFFERS from ledgers" if changed else "in sync"))
        sys.exit(1 if changed else 0)

    now = datetime.datetime.now().astimezone()
    stamp = now.strftime("%Y-%m-%d %H:%M ") + (now.tzname() or "")
    new_html = re.sub(r'var REFRESHED_AT = "[^"]*";',
                      'var REFRESHED_AT = "%s";' % stamp, new_html)

    cur_ver = re.search(r'var DATA_VERSION = "([^"]*)"', html).group(1)
    new_ver = next_version(cur_ver, changed, now.strftime("%Y-%m-%d"))
    new_html = re.sub(r'var DATA_VERSION = "[^"]*";',
                      'var DATA_VERSION = "%s";' % new_ver, new_html)

    HTML.write_text(new_html)
    print("REFRESHED_AT -> %s" % stamp)
    print("DATA_VERSION -> %s%s" % (new_ver, "" if changed else " (unchanged: data identical)"))

    r = subprocess.run([sys.executable, str(SKILL / "scripts" / "validate_tasks.py"), str(HTML)])
    if r.returncode != 0:
        sys.exit("validate_tasks.py FAILED - do not publish this build")


if __name__ == "__main__":
    main()
