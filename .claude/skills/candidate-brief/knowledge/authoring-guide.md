# Candidate Brief: authoring guide

This is the detailed reference for filling `template.html`. It exists because the reference
build hit three real bugs in one session; the rules below are how to not repeat them.

## Never retype the base64 logo by hand

`template.html` embeds the Riverside logo (light and dark variants) as inline `data:image/png;base64,...`
strings, tens of thousands of characters each. **Never manually retype, re-paste through a chat
tool call, or "clean up" these strings.** A single flipped character silently corrupts the PNG:
the browser may still report `naturalWidth`/`naturalHeight` correctly (from the header) while
rendering a blank image, so a visual check can miss it.

- If you need to copy the template to a new file: use `cp` (Bash) or the `Write`/`Edit` tools on
  the *surrounding* text only. Never pass the base64 payload through a manual retype.
- If a logo ever needs to be re-sourced, read it directly from
  `.claude/skills/riverside-brand-guidelines/assets/riverside-logo-{white,dark}.b64.txt` and splice
  it in with a script (Python `re.sub`, or equivalent), never by hand.
- To verify a logo wasn't corrupted, decode and load it:
  ```python
  import re, base64, io
  from PIL import Image
  html = open("your-file.html", encoding="utf-8").read()
  for cls, data in re.findall(r'<img class="(logo-light|logo-dark)" src="data:image/png;base64,([^"]+)"', html):
      im = Image.open(io.BytesIO(base64.b64decode(data)))
      im.load()  # raises if corrupted
      print(cls, "OK", im.size)
  ```
- The template shows the light-mark logo on dark backgrounds and the dark-mark logo on light
  backgrounds via `data-theme` and `prefers-color-scheme` CSS (see `.brand-row img.logo-*` rules).
  Do not simplify this to a single logo image: the white mark is invisible on a light card.

## The flexbox + overflow:hidden layout trap

The masthead card uses `overflow: hidden` (to clip the purple accent bar). `.page` is (and should
stay) `display: flex; flex-direction: column` to stack the cards; that part is not the trap.

The trap is the **ancestor** that centers `.page` on the page. In an earlier version of this
template, `body` was `display: flex; justify-content: center` with `.page` as its only child.
Because `body`'s flex direction is row, its default `align-items: stretch` controls the *cross*
axis (vertical) sizing of `.page`. A flex item's automatic minimum size on that axis collapses to
0 the moment its `overflow` isn't `visible` (see the [CSS flexbox spec on automatic minimum
size](https://www.w3.org/TR/css-flexbox-1/#min-size-auto)) - so the masthead card, the one item
with `overflow: hidden`, was the one that silently absorbed all of the stretch/shrink, collapsing
to near its padding-only height and hiding the title, role line, and status pill, even though the
DOM and computed CSS looked correct.

**Rule: keep page-level centering as plain block layout**, not a flex wrapper:
```css
body { margin: 0; padding: 40px 20px; }               /* no display: flex here */
.page { max-width: 1080px; margin: 0 auto; display: flex; flex-direction: column; gap: 20px; }
```
`.page`'s own `flex-direction: column` for stacking cards is fine and unrelated to the bug; the
fix is removing `display: flex` from whatever wraps `.page` for centering.

If you must wrap a flex container around something with `overflow: hidden` for another reason,
either set `align-items: flex-start` on that specific container (verified fix: it stops the
cross-axis stretch that triggers the collapse) or drop `overflow: hidden` in favor of a
differently-implemented accent bar (e.g. a `::before` pseudo-element sized to the border box,
which doesn't require clipping the parent).

If a section ever renders visually truncated with no console error, check `element.offsetHeight`
vs. `element.scrollHeight` in a headless browser before assuming the content itself is wrong.

## Radar chart: label wrapping and viewBox margins

The radar SVG computes label positions from `centerX`/`centerY`/`maxR`/`labelOffset`. Long
single-word labels near the horizontal axes (angle close to 0° or 180°) are the ones most likely
to clip against the card edge, because `text-anchor: end`/`start` grows the text away from the
center with no automatic clipping protection.

- The template already wraps every multi-word label onto 2-3 lines and reserves generous margin
  (`width: 520`, `centerX: 260`, `labelOffset: 40`). Do not shrink these to save space without
  re-checking the widest single-word label at the near-horizontal axes.
- If a competency label is a single long word (e.g. "Communication", "Prioritization"), consider
  shortening it in the data (not the display logic) rather than widening the canvas further.
- After any change to the radar's size constants or the data array, render the page in a headless
  browser and screenshot it (see "Layout regressions to re-check" below) rather than trusting the
  math by eye.

## Layout regressions to re-check

Any time you touch CSS (not just fill in text), re-render and screenshot at three widths before
publishing: desktop (~1200px), tablet (~820px), and mobile (~390px). A quick way to do this
(Chromium is pre-installed; do not run `playwright install`):

```python
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser = p.chromium.launch(executable_path="/opt/pw-browsers/chromium")
    for label, width in [("desktop", 1200), ("tablet", 820), ("mobile", 390)]:
        page = browser.new_page(viewport={"width": width, "height": 1600}, color_scheme="dark")
        page.goto(f"file://{path_to_html}")
        page.wait_for_timeout(300)
        page.screenshot(path=f"/tmp/{label}.png", full_page=True)
        page.close()
    browser.close()
```

Check both `color_scheme="dark"` and `"light"`. A pure text fill (no CSS/JS touched) does not need
this check; changing the card grid, the radar geometry, or the flex/overflow structure does.

## Section-by-section fill map

| Placeholder | Source | Notes |
|---|---|---|
| `<CANDIDATE_NAME>` | Assessment or CV header | Appears in `<title>`, `<h1>`, and the CV summary line |
| `<ROLE_TITLE>` | Assessment | The role being hired for, not necessarily the candidate's current title |
| `<INTERVIEWERS>` | Assessment | Names of who this brief is prepared for; join with `&amp;` |
| `<STAGE_LABEL>` | Assessment | e.g. "final interview stage", "screening stage" |
| `<RECOMMENDATION_PILL>` | Assessment | e.g. "Strong Hire, Pending Final Interview" (comma, not an em dash) |
| `<RECOMMENDATION_TONE>` | Assessment | One of `hire` / `conditional` / `no-hire`, matching the actual verdict. Used as a CSS modifier class on both the header pill and the final banner (`.pill.<tone>`, `.final-banner.<tone>`) so a negative or conditional recommendation doesn't render green. Use the same value in both places. |
| `<ASSESSMENT_FIT_SCORE>` | Assessment | Out of 5, matches the stated overall fit rating |
| CV card | CV file, if provided | Omit the whole card if no CV was given. One `.cv-role` per position, most recent first. One `.cv-edu-grid` line per credential. Drop the Languages block if the CV doesn't state languages. **Contact details (email, phone) default to omitted** - see "Contact details in the CV card" below. |
| radar `data` array | Assessment competency ratings | One entry per rated competency, 0-5 scale, in the order given |
| Executive Summary | Assessment narrative | 1-2 paragraphs, 4-8 short positive tags |
| Strengths & Risks | Assessment | One `.item` per named theme; 1-3 bullets each; don't force equal left/right counts |
| Areas to Probe | Assessment | One `.interviewer-card` per named interviewer; their specific focus tags and suggested questions |
| What We Know vs. What's Left | Assessment | `check-item done` = already confirmed; `check-item pending` = open question for the next round |
| Final recommendation banner | Assessment | Score out of 10 if the source gives one; emoji + label must match the actual verdict (never default to "🟢 Hire"); `<RECOMMENDATION_TONE>` must match too, so the color matches the words |

## No em dash, anywhere

Riverside brand rule: never use the em dash (U+2014) character. Use a comma, colon, period, or the word "to"
for date ranges (e.g. "2023 to 2025", not "2023 [em dash] 2025"). Grep the finished file for U+2014 before
publishing; it should return zero matches.

## Contact details in the CV card

The CV card's `.cv-contact` block can hold direct contact details (email, phone). **Default to
omitting them** unless the requester has told you the brief's audience is limited to people who
should have that contact info (e.g. the hiring manager and the direct interviewers) and has asked
for it to be included. When omitting, drop the whole `.cv-contact` line rather than leaving an
empty span. If asked to include contact details, still keep them out of anything that gets a
wider audience than the interview panel (a team channel, a shared dashboard, etc.).

## Escaping source-derived text

Every `<PLACEHOLDER>` gets filled by writing plain text directly into this file, not by a runtime
template engine, so there's no automatic escaping step. Two places need manual care when the
source data itself might contain HTML- or JS-significant characters (a candidate's name, a CV
line, a quoted question) - rare, but a name containing `&`, `<`, or a straight quote is enough to
break the page if left unescaped:

- **HTML text and attributes:** replace `&` with `&amp;`, `<` with `&lt;`, `>` with `&gt;`, and a
  double quote inside an attribute value with `&quot;`. This repo's existing convention of writing
  `&amp;` for "and" in headings (see the template's `<h2>Strengths &amp; Risks</h2>`) is the same
  rule applied consistently; extend it to any source text that contains these characters.
- **The radar chart's `data` array (inside `<script>`):** it's a JS object literal, not a string
  template, so escape any double quote or backslash in a label (`\"`, `\\`) the same way you would
  writing a JS string literal by hand. Do not build label text by string-concatenating raw source
  text into a template literal anywhere in the script; the tooltip and score table already render
  labels via `textContent`/DOM properties (not `innerHTML`) specifically so a label can't inject
  markup, so filled-in label text only needs valid JS-string escaping, not HTML escaping.
