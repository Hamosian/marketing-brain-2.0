#!/usr/bin/env bash
# Screenshot a web page or a local HTML file with headless Chrome, safely.
#
# Usage:  scripts/web_screenshot.sh <url-or-html-file> <out.png|out.jpg> [width] [height] [scale]
#         width x height default 1920 x 760 (a hero); scale defaults to 1 (use 2 for crisp
#         diagrams such as an org chart). An .jpg output is converted with sips (a 1920px hero
#         is ~700KB as PNG, ~190KB as JPEG, which matters inside a .docx).
#
# Why a script: `chrome --headless --screenshot` writes the file and then never exits when
# the page keeps network activity alive (riverside.com does), so a foreground call hangs
# until the tool times out. This launches Chrome in the background with its own profile,
# polls for the file, then kills only that Chrome. Found 2026-09-23.
set -euo pipefail

if [ $# -lt 2 ]; then
  echo "usage: $0 <url-or-html-file> <out.png|out.jpg> [width] [height] [scale]" >&2; exit 2
fi
target="$1"; out="$2"; w="${3:-1920}"; h="${4:-760}"; scale="${5:-1}"
chrome="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
[ -x "$chrome" ] || { echo "Google Chrome not found at $chrome" >&2; exit 3; }

if [ -f "$target" ]; then
  target="file://$(cd "$(dirname "$target")" && pwd)/$(basename "$target")"
fi
mkdir -p "$(dirname "$out")"
out_abs="$(cd "$(dirname "$out")" && pwd)/$(basename "$out")"
profile="$(mktemp -d)"
png="$profile/shot.png"
trap 'pkill -f "$profile" >/dev/null 2>&1 || true; rm -rf "$profile"' EXIT

"$chrome" --headless=new --disable-gpu --hide-scrollbars --user-data-dir="$profile" \
  --force-device-scale-factor="$scale" --window-size="$w,$h" --virtual-time-budget=8000 \
  --screenshot="$png" "$target" >/dev/null 2>&1 &

for _ in $(seq 1 60); do
  [ -s "$png" ] && break
  sleep 1
done
sleep 1
[ -s "$png" ] || { echo "no screenshot after 60s: $target" >&2; exit 1; }

case "$out_abs" in
  *.jpg|*.jpeg) sips -s format jpeg -s formatOptions 82 "$png" --out "$out_abs" >/dev/null ;;
  *) cp "$png" "$out_abs" ;;
esac
echo "$out_abs"
