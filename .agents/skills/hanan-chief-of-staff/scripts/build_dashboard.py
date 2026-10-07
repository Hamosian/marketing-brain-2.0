#!/usr/bin/env python3
"""Bake the hanan-chief-of-staff ledgers into assets/dashboard.html.

  python3 scripts/build_dashboard.py           # rebuild + stamp REFRESHED_AT
  python3 scripts/build_dashboard.py --check   # exit 1 if a rebuild would change the data

Reads (all markdown tables):
  data/today-actions.md      -> DATA.actions      (+ DATA.date from <!-- date: -->)
  data/waiting-on-me.md      -> DATA.waitingMe
  data/waiting-on-others.md  -> DATA.waitingOthers
  data/board-snapshot.md     -> DATA.board {asOf, source, rows}
  data/meetings.md           -> DATA.meetings {date, rows}
  data/1-1-packs/<latest>-jonathan.md -> DATA.pack {title, lines}
  data/sources.md            -> DATA.sources (what was read this run; written by the run)
  ../growth-marketing-team-tasks/data/mops.md -> DATA.oweNir (Owner Hanan, not Done/Watch list)

Writes the JSON between /*DATA-START*/ and /*DATA-END*/, stamps REFRESHED_AT from the
system clock in Asia/Jerusalem, bumps DATA_VERSION only when the baked data changed, and
syntax-checks the whole inline script with JavaScriptCore (osascript). Never touches
ACK_TOKEN: only a run applying a pasted SYNC_TOKEN may raise it.
"""
import argparse
import datetime
import json
import re
import subprocess
import sys
from pathlib import Path
from zoneinfo import ZoneInfo

TZ = ZoneInfo("Asia/Jerusalem")  # the stamp is Hanan's clock, whatever host runs the build

SKILL = Path(__file__).resolve().parent.parent
DATA = SKILL / "data"
HTML = SKILL / "assets" / "dashboard.html"
NIR_MOPS = SKILL.parent / "growth-marketing-team-tasks" / "data" / "mops.md"
MD_LINK = re.compile(r"\[([^\]]*)\]\(([^)\s]+)\)")


def table_rows(path, cols, optional_tail=0):
    """Rows of the first markdown table in `path`, mapped onto `cols` (header row skipped).

    A row whose width does not match `cols` is a parse error, not something to pad or trim:
    a stray pipe in a cell would otherwise shift every field after it and publish wrong
    data silently. `optional_tail` allows that many trailing columns to be absent (Nir's
    ledgers may omit the optional Answer column)."""
    if not path.exists():
        return []
    rows, seen_header = [], False
    for n, line in enumerate(path.read_text().splitlines(), 1):
        s = line.strip()
        if not s.startswith("|"):
            continue
        if s.startswith("|---") or set(s.replace("|", "").strip()) <= set("-: "):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if not seen_header:
            seen_header = True  # header row
            continue
        if not (len(cols) - optional_tail <= len(cells) <= len(cols)):
            sys.exit("%s:%d: row has %d cells, expected %d. Fix the ledger (a cell may contain a stray '|'); nothing was written."
                     % (path, n, len(cells), len(cols)))
        cells += [""] * (len(cols) - len(cells))
        rows.append({k: (v if v not in ("-", "\u2014") else "") for k, v in zip(cols, cells)})
    return rows


def comment(path, key):
    if not path.exists():
        return ""
    m = re.search(r"<!--\s*%s:\s*(.*?)\s*-->" % re.escape(key), path.read_text(), re.S)
    return m.group(1).strip() if m else ""


def plain(s):
    return MD_LINK.sub(r"\1", s or "").replace("**", "").strip()


def owe_nir():
    if not NIR_MOPS.exists():
        return []
    cols = ["task", "owner", "status", "pri", "due", "source", "added", "updated", "answer"]
    out = []
    for r in table_rows(NIR_MOPS, cols, optional_tail=1):
        owner = r["owner"].split()
        if not owner or owner[0].lower() != "hanan":
            continue
        if r["status"] in ("Done", "Watch list"):
            continue
        out.append({
            "task": plain(r["task"]), "status": r["status"], "pri": r["pri"],
            "due": r["due"] if re.match(r"\d{4}-\d{2}-\d{2}$", r["due"]) else "",
            "source": plain(r["source"]),
            "answer": plain(r["answer"].replace("<br>", " ")),
        })
    return out


def pack():
    files = sorted((DATA / "1-1-packs").glob("*-jonathan.md"))
    if not files:
        return None
    text = files[-1].read_text()
    title = text.splitlines()[0].lstrip("# ").strip()
    m = re.search(r"## Message[^\n]*\n(.*?)(?:\n## |\Z)", text, re.S)
    body = m.group(1).strip() if m else ""
    lines = [l.rstrip() for l in body.splitlines()]
    return {"title": title, "file": files[-1].name, "lines": lines}


def build_data():
    actions = table_rows(DATA / "today-actions.md",
                         ["title", "clock", "who", "link", "age", "move"])
    board_rows = table_rows(DATA / "board-snapshot.md",
                            ["board", "owner", "task", "status", "pri", "due", "link"])
    return {
        "date": comment(DATA / "today-actions.md", "date"),
        "firstMove": comment(DATA / "today-actions.md", "first-move"),
        "builtAt": comment(DATA / "today-actions.md", "built"),
        "sources": table_rows(DATA / "sources.md", ["name", "state", "note"]),
        "actions": actions,
        "waitingMe": table_rows(DATA / "waiting-on-me.md", ["who", "where", "asked", "sat", "link"]),
        "waitingOthers": table_rows(DATA / "waiting-on-others.md",
                                    ["who", "what", "since", "link", "note"]),
        "oweNir": owe_nir(),
        "board": {"asOf": comment(DATA / "board-snapshot.md", "as-of"),
                  "source": comment(DATA / "board-snapshot.md", "source"),
                  "rows": board_rows},
        "meetings": {"date": comment(DATA / "meetings.md", "date"),
                     "rows": table_rows(DATA / "meetings.md", ["time", "meeting", "with", "prep"])},
        "pack": pack(),
    }


def replace_block(html, start, end, body):
    a = html.index(start) + len(start)
    b = html.index(end, a)
    return html[:a] + "\n" + body + "\n" + html[b:]


def next_version(cur, changed, today):
    if not changed:
        return cur
    if cur.startswith(today):
        suffix = cur[len(today):] or "a"
        return today + chr(ord(suffix[-1]) + 1)
    return today + "a"


def syntax_check(html):
    """Parse the inline <script> with JavaScriptCore; node is not installed on this Mac."""
    scripts = re.findall(r"<script>(.*?)</script>", html, re.S)
    js = "\n".join(scripts)
    tmp = SKILL / "assets" / ".syntax-check.js"
    tmp.write_text(js)
    try:
        r = subprocess.run(["osascript", "-l", "JavaScript", "-e",
                            "var src = $.NSString.stringWithContentsOfFileEncodingError('%s', 4, null).js; "
                            "ObjC.import('Foundation'); new Function(src); 'OK'" % tmp],
                           capture_output=True, text=True, timeout=60)
    finally:
        tmp.unlink(missing_ok=True)
    if r.returncode != 0 or "OK" not in r.stdout:
        sys.exit("JS syntax check FAILED, not writing:\n" + (r.stderr or r.stdout))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    html = HTML.read_text()
    data = build_data()
    # Escape the three characters that could end the inline <script> or open a tag inside
    # it. These are valid JSON escapes, so JSON.parse and the JS literal read them back as
    # the original characters; without this a ledger cell containing "</script>" would break
    # the page (and the syntax check catches it, so the refresh would be blocked).
    payload = json.dumps(data, ensure_ascii=False, indent=1)
    payload = payload.replace("&", "\\u0026").replace("<", "\\u003c").replace(">", "\\u003e")
    body = "  var DATA = " + payload + ";"
    new_html = replace_block(html, "/*DATA-START*/", "/*DATA-END*/", body)
    changed = new_html != html
    if args.check:
        print("check: baked data %s" % ("DIFFERS from ledgers" if changed else "in sync"))
        sys.exit(1 if changed else 0)

    now = datetime.datetime.now(TZ)
    stamp = now.strftime("%Y-%m-%d %H:%M ") + (now.tzname() or "")
    new_html = re.sub(r'var REFRESHED_AT = "[^"]*";', 'var REFRESHED_AT = "%s";' % stamp, new_html)
    cur = re.search(r'var DATA_VERSION = "([^"]*)"', html).group(1)
    ver = next_version(cur, changed, now.strftime("%Y-%m-%d"))
    new_html = re.sub(r'var DATA_VERSION = "[^"]*";', 'var DATA_VERSION = "%s";' % ver, new_html)

    syntax_check(new_html)
    HTML.write_text(new_html)
    print("rows: %d actions, %d waiting-me, %d waiting-others, %d owe-nir, %d board, %d meetings, pack=%s"
          % (len(data["actions"]), len(data["waitingMe"]), len(data["waitingOthers"]),
             len(data["oweNir"]), len(data["board"]["rows"]), len(data["meetings"]["rows"]),
             data["pack"]["file"] if data["pack"] else "none"))
    print("REFRESHED_AT -> %s" % stamp)
    print("DATA_VERSION -> %s%s" % (ver, "" if changed else " (unchanged)"))


if __name__ == "__main__":
    main()
