#!/usr/bin/env bash
# Render a .docx to one PNG per page on macOS, so you can look at a document before it
# reaches Drive. No LibreOffice or pdftoppm needed: Pages exports the PDF, PDFKit rasterizes.
#
# Usage:  scripts/render_docx.sh <file.docx> [out_dir] [scale]
#         out_dir defaults to <file>-pages/ next to the input; scale defaults to 1.6.
# Prints: the PDF path and "pages N". Then Read the PNGs (p01.png, p02.png, ...).
# Exit 4: Pages could not export (a dialog open, or busy); a Quick Look page-1 PNG is left instead.
#
# Needs macOS with Pages (it opens on screen for a few seconds) and swift (Xcode command
# line tools). Pages is a proxy, not the target: it floors every table row at 12pt, so the
# brand accent bar reads thicker than in Word or Google Docs, and it sizes columns only from
# tblGrid (scripts/riverside_docx.py writes both). Everything else it shows matched Google
# Docs on 2026-09-23.
set -euo pipefail

if [ $# -lt 1 ] || [ ! -f "$1" ]; then
  echo "usage: $0 <file.docx> [out_dir] [scale]" >&2; exit 2
fi
if [ ! -d "/Applications/Pages.app" ]; then
  echo "Pages is not installed; no local render on this machine. Say so and verify structurally." >&2; exit 3
fi

in="$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"
base="$(basename "${in%.*}")"
out="${2:-$(dirname "$in")/${base}-pages}"
scale="${3:-1.6}"
mkdir -p "$out"
out="$(cd "$out" && pwd)"
pdf="$out/${base}.pdf"
rm -f "$pdf" "$out"/p[0-9][0-9].png

# Pages may already hold the user's own documents: this opens only the given file and closes
# only that one. If Pages is showing a dialog or is busy, the AppleEvent times out; then fall back
# to a Quick Look render of page 1 (Apple's Word importer) so there is still something to look at.
if ! osascript - "$in" "$pdf" <<'APPLESCRIPT'
on run argv
  set inPath to item 1 of argv
  set pdfPath to item 2 of argv
  with timeout of 90 seconds
    tell application "Pages"
      set d to open (POSIX file inPath)
      delay 3
      export d to (POSIX file pdfPath) as PDF
      close d saving no
    end tell
  end timeout
end run
APPLESCRIPT
then
  echo "Pages did not export the file (a dialog may be open in Pages, or it is busy)." >&2
  echo "Clear it and rerun for every page. Page 1 only, from Quick Look:" >&2
  qlmanage -t -s 1400 -o "$out" "$in" >/dev/null 2>&1 || true
  ls "$out"/*.png 2>/dev/null >&2 || echo "Quick Look produced nothing either; verify structurally." >&2
  exit 4
fi

tmpdir="$(mktemp -d)"
trap 'rm -rf "$tmpdir"' EXIT
cat > "$tmpdir/render.swift" <<'SWIFT'
import PDFKit
import AppKit
let args = CommandLine.arguments
guard let doc = PDFDocument(url: URL(fileURLWithPath: args[1])) else { print("cannot open PDF"); exit(1) }
let scale = CGFloat(Double(args[3]) ?? 1.6)
for i in 0..<doc.pageCount {
  let page = doc.page(at: i)!
  let r = page.bounds(for: .mediaBox)
  let img = page.thumbnail(of: NSSize(width: r.width * scale, height: r.height * scale), for: .mediaBox)
  let png = NSBitmapImageRep(data: img.tiffRepresentation!)!.representation(using: .png, properties: [:])!
  try! png.write(to: URL(fileURLWithPath: "\(args[2])/p\(String(format: "%02d", i + 1)).png"))
}
print("pages", doc.pageCount)
SWIFT

echo "$pdf"
swift "$tmpdir/render.swift" "$pdf" "$out" "$scale"
