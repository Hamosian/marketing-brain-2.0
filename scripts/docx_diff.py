"""Diff two .docx files: what did a person change in the document you sent them?

Compares paragraph by paragraph and table row by table row, in document order, plus the set
of hyperlink targets and the image count. Use it when someone edits a deliverable (for example
in Google Docs) and asks you to pick up their changes: it gives an exact change list, and each
change is then either an edit for that document only or a fact to route into the repo
(CLAUDE.md, Knowledge Routing).

Read the real file, not Drive's text export. `read_file_content` flattens a .docx: cell text
merges across line breaks and header rows can come back shifted a column. With Drive for
desktop the edited file is already on disk under
~/Library/CloudStorage/GoogleDrive-<email>/My Drive/.

Usage:
    python3 scripts/docx_diff.py <sent.docx> <edited.docx> [--context N]

Exit status is 0 when the documents match, 1 when they differ.
"""
import argparse
import difflib
import sys

import docx
from docx.table import Table
from docx.text.paragraph import Paragraph


def extract(path):
    """Document-order lines (paragraphs, then one line per table row), links, image count."""
    d = docx.Document(path)
    lines = []
    for child in d.element.body.iterchildren():
        tag = child.tag.split("}")[1]
        if tag == "p":
            text = Paragraph(child, d).text.strip()
            if text:
                lines.append(text)
        elif tag == "tbl":
            for row in Table(child, d).rows:
                cells = []
                for cell in row.cells:
                    text = cell.text.strip().replace("\n", " / ")
                    if not cells or cells[-1] != text:  # merged cells repeat; keep one
                        cells.append(text)
                joined = " | ".join(cells)
                if joined.strip(" |"):
                    lines.append(joined)
    links = {r.target_ref for r in d.part.rels.values() if "hyperlink" in r.reltype}
    return lines, links, len(d.inline_shapes)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("sent")
    ap.add_argument("edited")
    ap.add_argument("--context", type=int, default=0, help="unchanged lines to show around each change")
    args = ap.parse_args()

    a, links_a, img_a = extract(args.sent)
    b, links_b, img_b = extract(args.edited)
    diff = list(difflib.unified_diff(a, b, "sent", "edited", n=args.context, lineterm=""))

    print(f"lines {len(a)} -> {len(b)} | images {img_a} -> {img_b}")
    changed = sum(1 for l in diff if l.startswith(("+", "-")) and not l.startswith(("+++", "---")))
    print(f"changed lines: {changed}")
    for line in diff:
        print(line)
    removed, added = sorted(links_a - links_b), sorted(links_b - links_a)
    print(f"links removed: {removed or 'none'}")
    print(f"links added: {added or 'none'}")
    return 0 if not diff and not removed and not added and img_a == img_b else 1


if __name__ == "__main__":
    sys.exit(main())
