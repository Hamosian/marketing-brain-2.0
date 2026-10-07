#!/usr/bin/env python3
"""Fail branded HTML before the Drive connector turns it into a broken Google Doc.

This exists because of a real incident. On 2026-09-16 a project brief and a
one-pager were published to Google Docs via the Drive connector. Both rendered
correctly in a browser and both came out of the conversion with visible defects:

  * The brief's ticket link, authored as a normal `<a href>` inside a `<td>`,
    appeared in the finished doc as the literal text `\\[Promo Code
    Architecture...\\](https://...)`. The same link outside the table converted
    to a real hyperlink.
  * The one-pager's `<hr>` immediately before an `<h2>` was absorbed into the
    heading, which read `-----Appendix: how we know`.

Neither was in the brand skill's Google Docs rules, which at the time covered
only bold inside table cells and bold wrapping inline code. Both were caught by
reading the published doc back, which is one round trip too late: the connector
cannot update a Doc in place, so every fix mints a new URL and leaves a dead
document behind. Two documents were republished and trashed to fix four lines.

The rule this enforces: assert the guards on the HTML, before the upload, so a
known-bad conversion can never reach a doc someone has to read.

A table cell is the sharp edge. The converter treats `<td>`/`<th>` content as
plain text, so any markup inside one is emitted as literal characters. Bold
becomes `**text**` and a link becomes `\\[text\\](url)`. Both look completely
fine in the source and in any browser preview.

Usage:
    python3 scripts/lint_gdoc_html.py FILE [FILE ...]   # gate, before publishing
    python3 scripts/lint_gdoc_html.py --self-test       # prove the rules fire
Exit 0 clean (warnings do not fail), 1 on any error.

Not wired into scripts/preflight.sh on purpose: the HTML this checks is
generated per deliverable and is not committed, so there is nothing for CI to
scan. It is a tool the author runs, not a repo gate.
"""

import re
import sys

# Acronyms the writing guide explicitly permits (riverside-brand-guidelines,
# "Style rules"), plus the ones that show up in our own technical prose. Anything
# else in all caps is probably ALL-CAPS-for-emphasis, which the guide forbids.
CAPS_OK = {
    "AI", "HD", "URL", "FAQ", "FPS", "MP4", "MP3", "WAV",
    "SQL", "HTML", "CSS", "API", "CRM", "MRR", "ARR", "CVR", "GRR", "NRR",
    "SEO", "QBR", "ICP", "MQL", "PQL", "B2B", "B2C", "UTM", "CTA",
    "BI", "ID", "IDS", "US", "UK", "EU", "CSV", "PDF", "QA", "KPI", "ROI",
    "DOCTYPE", "UTF",
}

CELL = re.compile(r"<(td|th)\b([^>]*)>(.*?)</\1>", re.S | re.I)


def _line(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def check(path: str, text: str):
    """Return (errors, warnings) as lists of 'path:line  message' strings."""
    errors, warnings = [], []

    def err(offset, msg):
        errors.append(f"{path}:{_line(text, offset)}  {msg}")

    def warn(offset, msg):
        warnings.append(f"{path}:{_line(text, offset)}  {msg}")

    # 1. Em dash. Strict brand rule, no exceptions (Core Rule 0).
    for m in re.finditer("\u2014", text):
        err(m.start(), "em dash - use a comma, period, colon, or rewrite")

    # 2/3. A table cell is a plain-text box. Markup inside one is emitted
    #      literally by the converter.
    for m in CELL.finditer(text):
        tag, attrs, cell = m.group(1), m.group(2), m.group(3)
        if re.search(r"<a\b", cell, re.I):
            err(m.start(), f"link inside <{tag}> - renders as literal \\[text\\](url); "
                           "move the link out of the table")
        if re.search(r"<(b|strong)\b", cell, re.I):
            err(m.start(), f"<b>/<strong> inside <{tag}> - renders as literal **text**")
        if re.search(r"font-weight", cell, re.I):
            err(m.start(), f"font-weight inside <{tag}> content - renders as literal **text**")
        if re.search(r"font-weight", attrs, re.I):
            err(m.start(), f"font-weight on the <{tag}> tag - renders as literal **text**; "
                           "leave <th> unstyled for weight, the converter bolds it")
        if "**" in cell:
            err(m.start(), f"literal ** inside <{tag}>")

    # 4. A rule immediately before a heading is swallowed into the heading text.
    for m in re.finditer(r"<hr\b[^>]*>\s*<h[1-6]\b", text, re.I):
        err(m.start(), "<hr> immediately before a heading - the rule is absorbed into the "
                       "heading text; drop it and use the heading's top margin instead")

    # 5. Bold wrapping inline code emits stray asterisks.
    for m in re.finditer(r"<(b|strong)\b[^>]*>(?:(?!</\1>).)*?<code\b", text, re.S | re.I):
        err(m.start(), "<code> wrapped in bold - split them, bold label first, code outside")

    # 6. Stray markdown. Author in HTML; markdown survives as literal text.
    for m in re.finditer(r"\*\*", text):
        err(m.start(), "literal ** - author in HTML, not markdown")
    for m in re.finditer(r"^#{1,6}\s", text, re.M):
        err(m.start(), "markdown heading - use <h1>..<h6>")

    # 7. ALL CAPS for emphasis (warning: acronyms are legitimate). Reported once
    #    per distinct word with a count - tag-stripping moves every offset, so a
    #    line number here would be a confident lie.
    prose = re.sub(r"<[^>]+>", " ", text)
    seen = {}
    for m in re.finditer(r"\b[A-Z]{2,}\b", prose):
        if m.group(0) not in CAPS_OK:
            seen[m.group(0)] = seen.get(m.group(0), 0) + 1
    for word, count in sorted(seen.items()):
        times = "" if count == 1 else f" ({count}x)"
        warnings.append(f"{path}  all-caps word {word!r}{times} - "
                        "use bold or italics for emphasis, or add it to CAPS_OK")

    return errors, warnings


SELF_TEST = [
    ("link in cell", "<table><tr><td><a href='u'>x</a></td></tr></table>", True),
    ("bold in cell", "<table><tr><td><b>x</b></td></tr></table>", True),
    ("font-weight on th", '<table><tr><th style="font-weight:700">x</th></tr></table>', True),
    ("hr before heading", "<hr><h2>x</h2>", True),
    ("hr before heading, spaced", '<hr style="border:none">\n<h2>x</h2>', True),
    ("bold wrapping code", "<b>label <code>x</code></b>", True),
    ("em dash", "<p>a \u2014 b</p>", True),
    ("literal asterisks", "<p>**x**</p>", True),
    ("markdown heading", "## x\n", True),
    ("clean: link outside a table", "<p><a href='u'>x</a></p>", False),
    ("clean: styled th, no weight", '<table><tr><th style="color:#FFF">x</th></tr></table>', False),
    ("clean: hr before a paragraph", "<hr><p>x</p>", False),
    ("clean: permitted acronym", "<p>without writing SQL or using the API</p>", False),
]


def self_test() -> int:
    failures = 0
    for name, html, should_error in SELF_TEST:
        errors, _ = check("<fixture>", html)
        caught = bool(errors)
        if caught != should_error:
            failures += 1
            want = "an error" if should_error else "no error"
            print(f"  FAIL  {name}: expected {want}, got {len(errors)}")
        else:
            print(f"  ok    {name}")
    print()
    if failures:
        print(f"{failures} self-test(s) failed.")
        return 1
    print(f"All {len(SELF_TEST)} self-tests passed.")
    return 0


def main(argv) -> int:
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    if argv[0] == "--self-test":
        return self_test()

    all_errors, all_warnings = [], []
    for path in argv:
        try:
            with open(path, encoding="utf-8") as fh:
                text = fh.read()
        except OSError as exc:
            print(f"{path}: cannot read - {exc}")
            return 1
        errors, warnings = check(path, text)
        all_errors += errors
        all_warnings += warnings

    for w in all_warnings:
        print(f"WARN  {w}")
    for e in all_errors:
        print(f"ERROR {e}")

    if all_errors:
        print(f"\n{len(all_errors)} error(s). Fix before publishing - every republish "
              "mints a new URL and leaves a dead doc behind.")
        return 1
    print(f"\nClean. {len(argv)} file(s) checked"
          + (f", {len(all_warnings)} warning(s)." if all_warnings else "."))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
