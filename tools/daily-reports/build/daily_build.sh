#!/usr/bin/env bash
# Deterministic build wrapper for the two Riverside daily reports.
# Exists so the scheduled routine calls ONE stable command with the date as an
# argument, instead of a `cd ... && python3 ... && cp ...` compound. That compound
# (a) trips the "cd with write operation" safety prompt every run, and (b) embeds
# the changing date, so "Always allow" never matches the next day. This wrapper is
# allow-once-forever: `bash .../daily_build.sh <mode> <ANCHOR>`.
#
# Usage:
#   daily_build.sh plan  <ANCHOR>   # print date windows for the queries (read-only)
#   daily_build.sh build <ANCHOR>   # build both HTML artifacts + stage dated ROI copy
#
# Reads/writes only inside this build dir. Value JSONs (report_values.json,
# roi_report_values.json) must already be written before `build`.
set -euo pipefail
cd "$(dirname "$0")"

MODE="${1:-}"
ANCHOR="${2:-}"
if [ -z "$MODE" ] || [ -z "$ANCHOR" ]; then
  echo "usage: daily_build.sh plan|build <ANCHOR:YYYY-MM-DD>" >&2
  exit 2
fi

case "$MODE" in
  plan)
    echo "=== channel plan ($ANCHOR) ==="
    python3 build_artifact.py     --plan "$ANCHOR"
    echo "=== roi plan ($ANCHOR) ==="
    python3 build_roi_artifact.py --plan "$ANCHOR"
    ;;
  build)
    python3 build_artifact.py
    python3 build_roi_artifact.py
    STAGED="Riverside_ROI_Report_${ANCHOR}.html"
    cp roi_daily_snapshot.html "$STAGED"
    echo "=== built html ==="
    ls -la *.html
    # Anchor sanity - assert the anchor the caller asked for is the one the builders
    # actually rendered. Neither builder writes an ISO date into the HTML: both render
    # the long form ("August 18, 2026") in the header and the short form ("Aug 18") in
    # the MTD-through label. The previous check grepped for YYYY-MM-DD, which matches
    # neither, so it could never fail. The expected strings are derived in Python 3 (a
    # hard dependency of this build already) rather than with `date`, because the flags
    # differ between macOS (`date -j -f`) and the Linux cloud routine (`date -d`). Month
    # names are hardcoded to match the builders' own tables, which are English whatever
    # the locale.
    echo "=== anchor sanity ($ANCHOR) ==="
    python3 - "$ANCHOR" "$STAGED" plg_daily_snapshot.html roi_daily_snapshot.html <<'PYCHECK'
import os
import sys
from datetime import date

LONG = {1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June",
        7: "July", 8: "August", 9: "September", 10: "October", 11: "November",
        12: "December"}
SHORT = {1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun", 7: "Jul",
         8: "Aug", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec"}

anchor = date.fromisoformat(sys.argv[1])
staged = sys.argv[2]
expected = [f"{LONG[anchor.month]} {anchor.day}, {anchor.year}",  # header date
            f"{SHORT[anchor.month]} {anchor.day}"]                # MTD-through label

failed = False
for path in sys.argv[3:]:
    html = open(path, encoding="utf-8").read()
    missing = [s for s in expected if s not in html]
    if missing:
        failed = True
        print(f"FAIL {path}: missing {missing}")
    else:
        print(f"ok   {path}: found {expected}")

if failed:
    # The dated ROI copy is made before this check runs, so a failed build has already
    # overwritten it with the wrong-anchor HTML. Delete it rather than leave a deploy-ready
    # filename holding content we just rejected - Step 7 uploads that file by name, and a
    # correct-looking name over bad content is exactly how a bad build ships. Removing it
    # destroys nothing recoverable: whatever was there was clobbered by the copy above.
    unstaged = ""
    if os.path.exists(staged):
        try:
            os.remove(staged)
            unstaged = f" Removed the staged {staged}; rebuild before deploying."
        except OSError as exc:
            # Fail closed and say so plainly. The rejected file is still sitting there
            # under a deploy-ready name, so the operator has to delete it by hand.
            unstaged = (f" COULD NOT remove the staged {staged} ({exc}) - it still holds"
                        f" the rejected build. Delete it manually before any rebuild.")
    sys.exit(f"ANCHOR SANITY FAILED - a built report does not carry anchor "
             f"{anchor.isoformat()}. Do NOT deploy either surface.{unstaged}")
PYCHECK
    ;;
  *)
    echo "unknown mode: $MODE (expected plan|build)" >&2
    exit 2
    ;;
esac
