#!/usr/bin/env python3
"""Prove the dashboard cannot silently destroy Nir's un-synced browser edits.

    python3 scripts/test_dashboard_safety.py

WHAT THIS GUARDS
----------------
Every local edit on the team-tasks dashboard lives in browser localStorage keyed
by task id. Until 2026-08-09 an override whose id was absent from the baked TASKS
array was DELETED on sight, inside pruneRedundantOverrides() - which runs on every
render, not only on a version bump. So any publishing mistake that dropped or
renumbered an id destroyed the pending edits attached to it: no warning, no
recovery, and Nir would only find out by noticing his edit was gone.

That is not hypothetical. A bad build that morning cut three declarations out of
the file and came one mistake away from triggering exactly this.

Orphans are now quarantined in their own localStorage key and reattached if the id
returns. This test extracts the SHIPPED pruneRedundantOverrides() and the real
baked TASKS array straight out of dashboard.html and runs them, so the guarantee
is exercised rather than asserted. Re-run it after touching the override, orphan,
or reconcile paths, and before any publish that changes ids.

Requires macOS: uses JavaScriptCore via osascript, the same engine
build_dashboard.py uses for its syntax check.
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from build_dashboard import slice_literal  # noqa: E402  (shared bracket-matching slicer)

DASH = ROOT / ".claude/skills/growth-marketing-team-tasks/assets/dashboard.html"

STUBS = """
var _s={}; var localStorage={getItem:function(k){return k in _s?_s[k]:null;},
  setItem:function(k,v){_s[k]=String(v);},removeItem:function(k){delete _s[k];}};
var ov={}, ovTs={}, readOv={}, readAdded=[], added=[];
function saveOv(){localStorage.setItem("gmtt-ov-v2",JSON.stringify(ov));}
function saveOvTs(){localStorage.setItem("gmtt-ovts-v1",JSON.stringify(ovTs));}
function saveReadOv(){} function saveReadAdded(){}
"""

CASES = """
var out=[]; function check(n,c){out.push((c?"PASS  ":"FAIL  ")+n);}

// Nir has two un-synced edits. One is on a live task; one is on an id that a bad
// build has dropped from TASKS. Timestamps are far in the future so the ack-token
// path cannot be what clears them - this isolates the orphan branch.
ov["mops-5"]={pri:"P1"}; ovTs["mops-5"]={pri:9e12};
ov["ghost-99"]={status:"In work",pri:"P0",due:"2026-08-30"};
ovTs["ghost-99"]={status:9e12,pri:9e12,due:9e12};

pruneRedundantOverrides();   // the SHIPPED function, on the REAL baked TASKS

check("real build carries its full task set", TASKS.length > 0);
check("dropped-id edit is quarantined, not deleted", !!orphans["ghost-99"]);
check("every edited field survives",
  orphans["ghost-99"].fields.status==="In work" && orphans["ghost-99"].fields.pri==="P0"
  && orphans["ghost-99"].fields.due==="2026-08-30");
check("quarantine is persisted, not just in memory",
  !!JSON.parse(localStorage.getItem("gmtt-orphans-v1")||"{}")["ghost-99"]);
check("edits on live tasks are untouched", !!ov["mops-5"] && ov["mops-5"].pri==="P1");
check("orphan is cleared from the active override store", !ov["ghost-99"]);

// The publish is fixed and the id comes back.
TASKS.push({id:"ghost-99",team:"my",owner:"Nir",pri:"P2",due:null,title:"restored task"});
pruneRedundantOverrides();
check("edits reattach when the id returns",
  !!ov["ghost-99"] && ov["ghost-99"].status==="In work" && ov["ghost-99"].due==="2026-08-30");
check("quarantine empties once reattached", !orphans["ghost-99"]);

// A newer live edit must never be clobbered by a stale quarantined value.
orphans["seo-14"]={fields:{pri:"P3"},ts:{pri:1},at:1};
ov["seo-14"]={pri:"P0"};
pruneRedundantOverrides();
check("a live edit wins over a stale quarantined one", ov["seo-14"].pri==="P0");

// REGRESSION (Nir, 2026-08-09: "I can't change anything on the board").
// A task added in the browser lives in `added`, not TASKS, and carries a "new-<ts>"
// id. Building the baked map from TASKS alone made every edit on it look orphaned:
// it used to be deleted outright, and once quarantine landed it hijacked the sync
// bar and hid "Copy for Claude", stranding every pending edit on the page.
added.push({id:"new-1786000000000", ts:1786000000000, team:"my", owner:"Nir", pri:"P2",
            due:null, status:"Open", title:"a task Nir just added", _added:true});
ov["new-1786000000000"]={status:"In work"};
ovTs["new-1786000000000"]={status:9e12};
pruneRedundantOverrides();
check("an edit on a locally-added task is NOT quarantined", !orphans["new-1786000000000"]);
check("an edit on a locally-added task survives", !!ov["new-1786000000000"]
      && ov["new-1786000000000"].status==="In work");
out.join("\\n");
"""


def between(src: str, start: str, end: str, include_end: bool = True) -> str:
    a = src.index(start)
    b = src.index(end, a)
    return src[a : b + len(end)] if include_end else src[a:b]


def build_harness(src: str) -> str:
    t0, t1 = slice_literal(src, "  var TASKS =")
    r0, r1 = slice_literal(src, "  var READING =")
    orphan = between(src, '  var LS_ORPHAN = "gmtt-orphans-v1";', "    return back;\n  }\n")
    prune = between(src, "  function pruneRedundantOverrides() {", "\n  function normUrl", False)
    helpers = "\n".join([
        between(src, "  function normTitle(s)", "\n", False),
        between(src, "  function softNorm(s)", "\n", False),
        between(src, "  function fieldMatches(f, mine, theirs) {", "\n  }\n"),
        between(src, "  function normUrl(u)", "\n", False),
    ])
    return "\n".join([STUBS, src[t0:t1], src[r0:r1], orphan, helpers, prune, CASES])


def main() -> int:
    src = DASH.read_text(encoding="utf-8")
    try:
        harness = build_harness(src)
    except ValueError as exc:
        print(f"Could not extract the code under test: {exc}", file=sys.stderr)
        print("If dashboard.html was refactored, update the markers in build_harness().", file=sys.stderr)
        return 2

    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as fh:
        fh.write(harness)
        tmp = fh.name

    probe = f'var s=$.NSString.stringWithContentsOfFileEncodingError("{tmp}",4,null).js; eval(s)'
    res = subprocess.run(["osascript", "-l", "JavaScript", "-e", probe],
                         capture_output=True, text=True, timeout=60)
    out = res.stdout.strip()
    if not out:
        print("harness produced no output:", res.stderr.strip(), file=sys.stderr)
        return 2

    print(out)
    failed = [l for l in out.splitlines() if l.startswith("FAIL")]
    if failed:
        print(f"\n{len(failed)} check(s) FAILED - do not publish.", file=sys.stderr)
        return 1
    print(f"\nAll {len(out.splitlines())} checks passed. Un-synced edits cannot be silently lost.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
