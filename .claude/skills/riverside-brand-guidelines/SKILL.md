---
name: riverside-brand-guidelines
description: Applies Riverside.com's official brand colors, typography, tone of voice, and design philosophy to any artifact, document, presentation, or web component. Use when creating branded deliverables for Riverside, when brand colors, writing style, or tone guidelines are needed, or when applying Riverside's visual or verbal identity to content. Covers docx, pptx, HTML, React, PDF, spreadsheet, and video (MP4) outputs.
---

# Riverside.com Brand Guidelines

## Overview

Riverside's visual identity is built around a cinematic, studio-grade aesthetic. The brand palette is intentionally restrained: dark backgrounds dominate, purple serves as a precise accent (never a fill), and high contrast creates a professional "content creator" feel. No loud gradients, no playful color explosions.

**Keywords**: Riverside, branding, brand colors, visual identity, styling, corporate identity, content creator, podcast, video, recording platform, tone of voice, writing style, copy guidelines

> **Source of truth.** Colors, text-on-color pairs, type-setting, brand personality and imagery follow the **Riverside Brandbook (2026 edition)**, owned by Brand (Raz Messing's org). If this file and the brand book disagree, the brand book wins; fix this file.

> **Marketing vs. product palette.** This skill defines the marketing brand palette used for external/marketing deliverables (the main purple is `#9671FF`, the same value as the product's `primary.c600`). The full **product** design system extracted from Figma - exact color/type tokens, 66 component families, and 1301 icons - lives at `references/design-system/`. Use that when building or referencing the product UI; use this skill for marketing artifacts. Where they differ on hex values, the design system tokens are authoritative for product surfaces.

> **Companion skill: `/riverside-ux-patterns`.** This skill owns the **visual identity** (color, typography, tone). Its companion, `riverside-ux-patterns`, owns the **interaction and structure layer** - layout, spacing, hierarchy, interaction states, accessibility, component behavior, motion, and microcopy. On any request that builds or reviews something a person interacts with (HTML/React, dashboards, forms, docx, pptx, PDF), trigger both together: pull color and type from this skill, and pull how it behaves and how a person moves through it from `riverside-ux-patterns`. If the two ever disagree on a color, this branding skill wins.

## Logo

Always use the official Riverside logo (2025 version) in branded outputs:

```
https://upload.wikimedia.org/wikipedia/commons/9/99/Riverside_logo_%282025%29.png
```

Place the logo at the top of any branded HTML, React, PDF, presentation, or document output. Do not substitute a text placeholder or an older version of the logo.

**Hosted artifacts (claude.ai) cannot load this URL** - the sandbox blocks all external requests. Download the PNG (~20 KB), embed it as a base64 `data:image/png` URI, and note the artwork is near-black on transparent: on dark backgrounds apply `filter: invert(1)` (produces the correct white lockup; verified against the official variant), on light backgrounds use it as-is. Embed the fonts the same way (base64 `@font-face`; the Instrument Sans latin woff2 is ~30 KB; Sharp Grotesk Book only when its file is available and the license allows, see **Typography**) or the page silently falls back to system fonts. If a pixel-exact white logo is ever required, the official `Riverside logo - white [Desktop]` component lives in the `[Website] Marketing Web Design System_2026` Figma library.

## Brand Palette (digital: screens only)

Everything in this section is RGB/HEX for anything shown on a screen: web, HTML/React, slides,
docs, spreadsheets, social, ads and video. Print uses different values, kept apart in
**Print Colors** below; never use a CMYK or Pantone value on screen, or a HEX value for print.

"We are a dark brand, but with a color twist." The balance is roughly **90% black**, with
white, grey and purple making up the rest.

### Main Colors

| Color Name  | Hex       | Usage                                                       |
|-------------|-----------|-------------------------------------------------------------|
| Main Black  | `#1D1D1D` | Base background, hero sections; text on light surfaces       |
| Main White  | `#FFFFFF` | Text on dark backgrounds, light sections                     |
| Main Purple | `#9671FF` | CTA buttons, highlights, accents, active states, links, icons |

### Secondary Colors

Supporting colors that complete and enrich a design when needed. They are not text colors
(see **Text on Color** below).

| Color Name             | Hex       | Usage                                                   |
|------------------------|-----------|---------------------------------------------------------|
| Secondary Black 1      | `#000000` | Deepest ground, contrast bands                          |
| Secondary Black 2      | `#111111` | Deeper sections; the ground for purple text             |
| Secondary Black 3      | `#2C2C2C` | Cards and panels on Main Black; borders and dividers on dark |
| Secondary Purple 1     | `#AD98FA` | Softer purple: hover states, secondary accents, chart series |
| Secondary Grey         | `#F6F6F6` | Light surfaces: light sections, callout boxes, alternating table rows |
| Secondary Accent green | `#DFFF84` | Small accent moments only; never behind white text      |

**Retired values.** The palette before the 2026 brand book used `#7C5CFF` (now Main Purple
`#9671FF`), `#0F0F14` (now Main Black `#1D1D1D`), `#1C1C24` and `#2A2A35` (now Secondary
Black 3 `#2C2C2C`), `#E6E6EB` (no grey text any more; see below), `#8F73FF` and `#B8A5FF`
(now Secondary Purple 1 `#AD98FA`), and the tints `#EDE8FF` / `#F7F5FF` (now Secondary Grey
`#F6F6F6`). Some templates and scripts in other skills still hardcode them; when you meet one,
this section wins.

### Text on Color

For text we use the **main colors only**: Main Black, Main White, Main Purple. Riverside's
brand is black with a spark of color, so black and white carry the text; purple text is the
exception. Always keep enough contrast between text and the surface it sits on, and keep
content accessible and clear for the viewer.

| Text color  | Allowed on                                                                 |
|-------------|----------------------------------------------------------------------------|
| Main White  | Secondary Black 1 `#000000`, Main Black `#1D1D1D`, Secondary Black 3 `#2C2C2C`, Main Purple `#9671FF` |
| Main Purple | Black grounds (the brand book's example is Secondary Black 2 `#111111`)     |
| Main Black  | Main White `#FFFFFF`, Secondary Grey `#F6F6F6`, Secondary Purple 1 `#AD98FA` |

Never:
- Dark text on a black ground.
- Purple text on Secondary Purple 1 or on Secondary Grey. Purple text on any light surface
  falls under the same rule: on white it measures about 3.4:1, which fails body-text contrast,
  so on light surfaces text is Main Black and purple stays on non-text accents.
- White text on white, Secondary Grey, Secondary Purple 1 or Secondary Accent green.
- A secondary color as a text color, including a grey for "secondary" text. De-emphasize with
  size or weight instead.

### Utility Colors (Functional Only)

Used sparingly in product states, never in brand marketing:

| Role    | Color   | Usage                    |
|---------|---------|--------------------------|
| Success | Green   | Completed states         |
| Warning | Yellow  | Attention/caution states |
| Error   | Red     | Errors, destructive actions |

## Typography

Brand and marketing use two typefaces: **Sharp Grotesk** (primary) and **Instrument Sans**
(secondary). The product and app use **Inter**; in marketing, Inter appears only inside a
depicted product screen, never as marketing type.

| Role | Font | Weight |
|------|------|--------|
| Primary headline, titles, key messaging, eyebrows | Sharp Grotesk | **Book only** |
| Secondary headline, paragraphs, captions, supporting content | Instrument Sans | Regular (400) |
| CTA labels; a secondary headline that needs weight | Instrument Sans | SemiBold (600) |

Sharp Grotesk is the defining voice of the brand: a geometric sans-serif that blends Swiss
precision with the bold character of American wood type. Book is the only weight, so it reads
elegant and precise. Instrument Sans complements it with a clean, neutral character where
readability is key.

**Don'ts:**
- **Instrument Sans is never the main headline**, only secondary.
- **Sharp is never set in capital letters.** The one case the brand book shows is a short
  eyebrow label (a single word like "EDITING"); nothing longer.
- **Sharp is never paragraph text.**
- **Never change letter spacing** on Sharp or Instrument. Set tracking at the font's default.
- **No other weights.** Sharp Book only (not Medium); Instrument Regular and SemiBold only
  (not Medium, not Bold). Never pair Extra Bold with Bold, or Black with Extra Bold, on long
  text; the brand book's Extra Bold plus Light pairing is an edge case for Brand to sign off.
- **Emphasize with clear style contrast** (Sharp against Instrument, size, color), not by
  bolding.

**Getting the fonts:**
- **Instrument Sans** is free on Google Fonts. Import:
  `https://fonts.googleapis.com/css2?family=Instrument+Sans:wght@400;600&display=swap`.
  Include it in any HTML or React output produced with this skill.
- **Sharp Grotesk** is a licensed font (Sharp Type), not on Google Fonts. Brand holds the
  files. Never commit them to this repo or post them anywhere public. Rendered output (video,
  PNG, a PDF with an embedded subset) is fine; embedding the font file in a hosted web page
  needs the web license, so check with Brand first.

**When Sharp Grotesk can't be used**, set the headline role in Instrument Sans SemiBold and
tell the person the headline font is a fallback; it is a known deviation, because Instrument
is otherwise never the main headline. Office and Google formats (docx, Google Docs, pptx,
xlsx, Sheets) can't carry Sharp, so they always take this fallback. Where Instrument Sans is
missing too, use Arial.

### Type-Setting (line breaks and case)

From the brand book's typography do's and don'ts. They apply to every set line: headlines,
subheadlines, paragraphs, slides, ad frames and video supers. Check them in the rendered
output, at the size it ships, because line breaks only exist once the text is set.

- **Never split a hyphenated term across two lines** ("studio- / quality").
- **Never strand a word next to a full stop or comma.** A line does not end with the first
  word of the next sentence ("...content. Producers"), and a line does not start with the
  last word of a sentence ("workflows. Good luck...").
- **No single letter at the end of a line** ("a", "I").
- **No short word (1-2 letters) at the end of a line**, unless it deliberately helps the
  composition and hierarchy.
- **No single word alone on a line at the end of a sentence**, unless it deliberately helps
  the composition and hierarchy.
- **Short text (usually a headline) may leave one longer line on its own**, as long as the
  composition and hierarchy hold.
- **Never center-align text that runs over 2 lines or over 7-8 words per line.** Not in
  headlines, subheadlines or paragraphs; left-align it instead.
- **Capitals only at the start of a sentence and for names.** Never capitalize the first
  letter of every word in a headline ("Create podcasts & videos", not "Create Podcasts &
  Videos").

## Tone of Voice

Source of truth: the [Riverside Writing Guide](https://docs.google.com/document/d/1OVvHj8_zPaans1fusa2omtjHuaXT7XERd4-RnMijOdw/edit) (owned by Becky, Brand). This section summarizes it for applying the verbal identity to any written deliverable. For terminology definitions, use the Riverside Glossary linked from that doc. The brand book adds the personality layer below; the Writing Guide stays the source for mechanics (spelling, case, numbers, punctuation).

### What Riverside is (brand book definition)

Riverside is an end-to-end platform for creating studio-quality videos and podcasts, from
recording and live streaming to editing, repurposing and distribution, all with the help of
powerful AI.

### Brand Personality (brand book)

| Layer | What it means |
|-------|---------------|
| **Personality** | Clever, Confident, Warm, Human |
| **Sound** | Clear, Witty, Empowering, Approachable |
| **Signature moves** | Turn features into flexes. Copy worth quoting. |
| **Surprise with specificity** | Punch up, never down. Here to hype creators. |
| **Essence** | The clever creative confidante our users want to hang out with |

The line under all of it: **User first, always.**

Use it as a check on any draft: a feature stated flatly ("Records in 4K") misses the
signature move; the flex is what the feature lets the creator do or show off. A joke at the
audience's or a competitor's user's expense punches down. A claim with no specific detail in
it is not "surprise with specificity."

### Voice (who we are, never changes)

We're scrappy, smart creators, just like our users. Not stiff or corporate, we have personality (think Mailchimp, not Intuit). We're:

- **Mentors**: we give users the exact support and guidance they need to unleash their creativity, and we vouch for their success every step of the way.
- **Experts and problem solvers**: we know the tech, the world of podcasting, and what it means to be a creator.
- **Smart but not snobby**: always encouraging, never condescending.
- **Nerdy in the cool way**: we geek out on things we're passionate about.
- **Innovative and ahead of the curve**, yet grounded and down to earth.

### Tone (varies by context)

Tone is an extension of voice; dial it based on the reader's state of mind:

| Reader's state | Tone | Examples |
|----------------|------|----------|
| Creative, calm, curious | Dial up positivity, playfulness, energy, humor | Marketing pages, newsletters, community posts, clip creation moments |
| Stressed or focused | Supportive, reliable, professional | In-studio settings, error states, troubleshooting, support content |

### How we write

1. **Write like you speak.** Say it out loud; if it sounds wrong to your ears, rewrite it. Positive, eye-level language.
2. **Write like you're speaking to a person.** It's ok to sound human. We're software, but people should feel there's a team behind it vouching for their success. Humor is welcome at the right time.
3. **Use active, present voice.** Keeps readers in the flow and lets them digest info quickly.
4. **Be clear, simple, concise.** No fluff, complicated language, or jargon. (A little fluff can soften language and sound more human, so it's sometimes welcome.)
5. **Write for everyone.** Inclusive language: avoid gendered terms (use "people" or "they/their"), and be careful with slang, humor, or cultural references that aren't universally understood.

### Style rules

- **US spelling, AP style** by default, except where the rules below override it.
- **Sentence case everywhere**: titles, subtitles, section titles, and CTA buttons ("Get started", "Book a demo"), unless a capitalized feature name appears ("Create Magic Clips").
- **Capitalized feature names**: Magic Clips, Magic Audio, AI Producer, AI Voice, Mobile as Webcam, Riverside. Generic product areas stay lowercase: editor, studio, lobby, dashboard, timeline, transcripts, host/guest/producer. Plan names capitalize the name only: Free plan, Pro plan.
- **Contractions**: use them wherever you can; more conversational, less space.
- **Acronyms**: avoid them; spell the word out. Exceptions: AI, HD, URL, FAQ, FPS, and file formats (MP4, MP3, WAV).
- **Numbers and dates**: use numerals ("14 days"); dates as MON DD, YYYY (Sep 26, 2023); time as 9:00 AM EST; shorten to hr, min, sec (never mins/secs).
- **Punctuation**: no periods in titles; periods in subtitles only when a full sentence. Use the Oxford comma. Colons introduce lists when the bullets complete the sentence.
- **Emphasis**: never use ALL CAPS for importance; use bold or italics. Exclamation marks only on rare occasions, never in batches.

> **Em dash override.** The official writing guide permits em dashes (no spaces). This repo's brand skill deliberately overrides that: **never use the em dash character in deliverables produced with this skill** (Core Rule 0 below). Use a comma, period, colon, or rewrite instead. Do not "fix" this back to match the Google Doc.

### Tone by audience (marketing deliverables)

| Audience | Tone |
|----------|------|
| Creators / podcasters | Casual, outcome-focused, peer-to-peer |
| B2B / enterprise buyers | Professional, specific, proof-heavy |
| Internal team | Direct, brief, no fluff |
| Slack (team) | Energetic, emoji-friendly, never robotic |

## Design Principles

### Core Rules

0. **Never use the em dash character ( -- ).** This is a strict brand writing rule. Use a comma, period, colon, or rewrite the sentence instead.
1. **Purple is an accent, not a fill.** Never use purple as a large background area. Use it for headings (H2) and labels on dark grounds, thin accent bars, links, and interactive elements (purple text follows **Text on Color**).
2. **Dark backgrounds dominate in digital.** For web, React, and HTML artifacts, default to Main Black (`#1D1D1D`) backgrounds with white text.
3. **High contrast = "studio-grade" look.** Always maintain strong contrast between text and background.
4. **No loud gradients or playful color explosions.** The brand is restrained, cinematic, and professional.
5. **Signals creativity, quality, and modern creator energy** without being flashy or juvenile.
6. Visual Rhythm & Inversion - To prevent visual fatigue from a purely dark interface, we use **playful inversions**.
- **The "Spotlight" Inversion:** Sections requiring high readability or social trust (testimonials, press logos, detailed pricing) often flip to a **Main White / Secondary Grey (`#F6F6F6`)** background, with Main Black text.
- **Cinematic Immersion:** Hero sections or emotional "outcome" moments use **Full-Bleed Image Backgrounds** with a dark overlay to ensure text remains legible.

### Application by Output Type

#### Word Documents (docx)

- White page background (standard document page)
- All text is Main Black `#1D1D1D` (purple text is not used on a white page; see **Text on Color**)
- H1: Main Black `#1D1D1D`, Bold, followed by the purple accent bar
- H2: Main Black `#1D1D1D`, Bold, one size step below H1
- H3: Main Black `#1D1D1D`, Bold, one size step below H2
- Body text: Main Black `#1D1D1D`
- Table headers: Main Black `#1D1D1D` background, White `#FFFFFF` text
- Table alternating rows: Secondary Grey `#F6F6F6`
- Table borders: Secondary Grey `#F6F6F6` (the row shading carries the separation; use 0.5pt Secondary Black 3 `#2C2C2C` only when a dense grid needs visible rules)
- Accent bars (horizontal rules under section titles): Main Purple `#9671FF`, 2-3pt height
- Bold labels in body text: Main Black `#1D1D1D`, Bold
- Header and footer text (including page numbers): Main Black `#1D1D1D`
- Cell margins: top/bottom 60 DXA, left/right 100 DXA
- Use ShadingType.CLEAR (never SOLID) for table shading

#### Presentations (pptx)

- Slide background: Main Black `#1D1D1D`
- Title text: White `#FFFFFF`
- Subtitle/secondary: White `#FFFFFF` at a smaller size (no grey text)
- Accent elements (lines, shapes, icons): Main Purple `#9671FF`
- Content text: White on dark, Main Black on light slides
- Charts: Main Purple as the primary data color, Secondary Purple 1 `#AD98FA` and Secondary Grey `#F6F6F6` for secondary series
- Divider slides: Full Main Black with a centered purple accent line

#### HTML / React Artifacts

- Background: Main Black `#1D1D1D`; Secondary Black 2 `#111111` or Black 1 `#000000` for deeper bands
- Text: White `#FFFFFF`; secondary text is White at a smaller size or lighter weight, never a grey
- Accent/interactive: Main Purple `#9671FF`
- Cards/panels: Secondary Black 3 `#2C2C2C` on Main Black background
- Buttons (primary CTA): Main Purple `#9671FF` background, White text
- Buttons (secondary): Transparent with Purple border
- Hover states: Secondary Purple 1 `#AD98FA`
- Links: Main Purple `#9671FF` on dark grounds; Main Black, underlined, on light sections
- Borders/dividers: Secondary Black 3 `#2C2C2C`

Tailwind approximations (for React artifacts):
```
bg-[#1D1D1D]   /* Main Black background */
bg-[#111111]   /* Secondary Black 2, deeper band */
bg-[#2C2C2C]   /* Secondary Black 3 surface (cards, panels) */
text-white      /* All text on dark */
text-[#9671FF] /* Purple accent (dark grounds only) */
bg-[#9671FF]   /* Purple CTA, white text */
hover:bg-[#AD98FA] /* Secondary Purple 1 hover */
border-[#2C2C2C] /* Borders */
```

#### Spreadsheets (xlsx)

- Header row: Main Black `#1D1D1D` fill, White text, Bold
- Alternating rows: White and Secondary Grey `#F6F6F6`, Main Black text
- Borders: Secondary Grey `#F6F6F6` (0.5pt Secondary Black 3 `#2C2C2C` when a dense grid needs visible rules)
- Accent/totals row: Main Purple `#9671FF` fill, White text

Instrument Sans is not available inside Sheets or Excel - use the Arial fallback there.

#### Google Sheets (via the Drive connector)

Same palette as xlsx above. What is specific to Google Sheets is **the file format**, because
the connector will not convert an xlsx at all: `create_file` with an xlsx mime type fails with
`Invalid conversion requested`, so a workbook styled per the rules above never reaches Sheets.

**Deliver the styling as ODS.** Build the workbook as OpenDocument, put every style in
`content.xml` under `<office:automatic-styles>`, and ship **only** `mimetype`, `content.xml`,
`settings.xml` and `META-INF/manifest.xml`. Including a `styles.xml` breaks the conversion
(`Unable to convert uploaded content`), so also drop the `style:parent-style-name="Default"`
that would have pointed at it. Fills, borders, fonts, column widths, wrapping, merges,
hyperlinks, filter buttons and frozen panes all survive that path.

**CSV is the unstyled floor, not a shortcut.** `text/csv` converts cleanly and carries no
formatting whatsoever - fine for a data drop, never for a branded deliverable.

**Don't rely on conditional formatting or data validation.** Google's ODS importer drops both
silently. Bake state colours in as static fills and tell the user they won't recolour on edit.

Mechanics, the sandbox constraints, and the bisect that established all this:
`docs/platform-integration.md` → Google Drive.

#### PDF

- A PDF read on screen or printed at the desk follows the docx rules (light page) or the HTML rules (dark), using the digital palette
- A PDF sent to a commercial printer is a print job: its colors come from **Print Colors** below, never from the digital palette

#### Video (MP4)

**A request for a video, movie, film, or motion piece is a request for an MP4 file.** Send it
with `SendUserFile`. An interactive HTML page with a play button is a different deliverable:
offer it as an extra, never ship it in place of the file. (2026-09-28: an "upbeat short
animation movie" was first delivered as a hosted artifact, and the correction was "you created
artifact i wanted motion video".)

Styling follows the HTML rules above: Main Black ground, Sharp Grotesk Book for headlines and Instrument Sans for the rest (both inlined as base64),
purple as the accent, 1920x1080 at 30 fps.

**How to make one on a team Mac.** There is no ffmpeg, and you don't need it:

1. **Author the animation as a web page whose every frame is a function of time.** A fixed
   stage (1280x720 works) scaled to the viewport, with each element's opacity, position and
   text computed from `t`. Expose `window.__frame(t)`. No CSS transitions or `@keyframes`:
   they run on wall-clock time, so the capture misses them.
2. **Soundtrack (optional):** synthesize it with WebAudio and expose `window.__audio(duration)`,
   which renders through an `OfflineAudioContext` and stores a base64 WAV in `window.__wav`.
   The audio then lines up with the frames exactly.
3. **Render and encode in one command:**
   `python3 scripts/capture_frames.py page.html frames/ --duration 92 --audio --mp4 out.mp4`.
   Headless Chrome captures the frames, and `scripts/frames_to_mp4.swift` encodes through
   AVFoundation, which ships with macOS. A 92-second 1080p film took 95 s to capture and 30 s
   to encode, and came out at 26.8 MB.
4. **Open with a title card and close with the diligence slate.** The first frame is the
   thumbnail, so put the title there, not a fade from black. The last few seconds carry the
   AI diligence statement, because it is a file deliverable.
5. **Check it before you send it.** The encoder reads the file back and prints its duration and
   tracks. Pull a few frames from the MP4 and look at them. Nothing in the pipeline can hear
   the audio, so say so, and ask a person to play it once with sound before it's shared.

#### Google Docs (via the Drive connector)

Same light-mode palette as docx (white page, Main Black text and headings, Main Purple
accent bar under the title, Main Black table headers with White text, Secondary Grey `#F6F6F6`
alternating rows). What is specific to Google Docs is **how the document has to be built**.

**Build it as .docx. Do not author it as styled HTML.** The Drive importer keeps
*character-level* run styling - colour, size, weight - and table cell shading, and discards
*block-level box* styling: margins, padding, borders on `<div>`/`<p>`, and any custom `<hr>`.
A CSS-styled page therefore arrives carrying Riverside's colours and none of Riverside's
layout. Observed 2026-09-16 on a project brief and a one-pager: the purple accent bar came
through as a grey hairline, paragraph spacing vanished so the body read as a wall of text,
and a callout box flattened into what looked like highlighter pen. Every one of those looked
correct in the source and in a browser.

`.docx` converts through Word's document model instead, which has real paragraph spacing,
table borders, cell shading, keep-with-next and repeating header rows. All of it survives.

**Use `scripts/riverside_docx.py`.** It is the branded builder: `title`, `accent_bar`, `h1`,
`h2`, `h3`, `body`, `rich`, `caption`, `label_para`, `bullets`, `picture`, `callout`,
`kv_table`, `table`, `answer_box`, `link_line`, `page_break`, `brand_header`, `page_numbers`,
`diligence`, plus `slim` for packaging. `h1`-`h3` are real Heading styles, so a long document
gets a Word navigation pane and a Google Docs outline; `rich` and `bullets` take a parts list
(bold, purple label, channel name, working link) as well as a plain string. Every numbered
`bullets` list starts at 1; pass `restart=False` to carry the count on from the previous
numbered list. Run it directly (`python3 scripts/riverside_docx.py`) for a self-test that
builds one of everything, slims it, reopens it, and asserts the palette, the repeating header
rows, the hyperlinks, table-property schema order, column widths, the accent bar's row height,
the heading styles, the embedded picture and the numbered-list restarts survived.

**The builder's colors predate the 2026 brand book.** Its constants still carry the retired
palette (`#7C5CFF` purple, `#0F0F14` black, `#EDE8FF` rows) and it sets H2s and labels in
purple, which **Text on Color** no longer allows on a white page. Until it is updated, a
document it builds carries those colors: avoid the purple-label part, and tell the person the
palette is the old one when you deliver.

**Building a .docx without the builder?** Four traps it already handles. Column widths go in
`w:tblGrid` (and `w:tblW`), not only on each cell: Pages and Google Docs size columns from the
grid, so per-cell widths alone render as equal columns. `w:tblPr` children must follow the
schema order, so never append one (a `tblBorders` after `tblLook` can make Word report
unreadable content). The accent bar needs an exact row height plus a tiny paragraph-mark
size; a small run font alone leaves a slab over 15pt tall. Pages floors any table row at
12pt, so the bar is thicker there than in Word. And a second numbered list continues the
first one's count: every `List Number` paragraph inherits one `numId` from the style, so on
2026-09-29 a 4-item question list after a 6-item list rendered as 7-10 in Pages and in the
Google Doc, which broke "see question 1". Give each list its own `w:num` with a
`startOverride` of 1, on its own copy of the `abstractNum`: Pages honours the override, but
Quick Look ignores it and counts every list that shares an `abstractNum` as one.

Two routes from a local `.docx` to a Google Doc:

| Route | When | How |
|---|---|---|
| Synced Drive folder | The user has Drive for desktop | Copy into `~/Library/CloudStorage/GoogleDrive-<email>/My Drive`, wait for the sync, open at `https://docs.google.com/document/d/<fileId>/edit`, then File > Save as Google Docs. Nothing passes through the model context |
| `create_file` | No synced folder | `base64Content` plus the `.docx` content type; Drive converts on upload. Run `slim()` first - python-docx ships ~370 unused styles and a legacy `stylesWithEffects` part, and dropping them takes a typical document from ~45KB to ~19KB, which is the difference between one inline payload and three |

**Prefer the synced folder whenever it exists, and check before assuming it does not**
(`ls -d ~/Library/CloudStorage/GoogleDrive-*`). Two reasons beyond the context saving:

- **A large `base64Content` corrupts in transit.** A ~15KB `.docx` is ~20K base64 characters,
  and reproducing that opaque blob into a tool call is not reliable - one attempt on
  2026-09-23 came back `The file content is not a valid base64 string` after the payload had
  already cost a full round trip. The synced folder never puts the bytes through the model.
- **`create_file`'s filename argument is `title`.** Not `fileName`, not `name` - both are
  rejected with `Unknown name ... Cannot find field`, and each rejection costs you the whole
  payload again. `parentId` sets the folder.

**Re-copying over the same path in the synced folder updates the file in place** - same
`fileId`, same URL, a new Drive revision. That is the one route that escapes the new-URL
problem below, so for anything you expect to revise (a doc out for review), prefer it and
hand out the URL once. Confirmed 2026-09-23 across two revisions of the same document.

**Look at the rendered document before you call it done.** Reading the text back proves the
words landed; it says nothing about whether it looks like a Riverside document. Open it and
look, or the first person to open it does that for you.

`soffice` cannot convert Word documents in this sandbox either, not only spreadsheets, so there is no
local render to look at. When you genuinely cannot see it, say so and name what you did
verify structurally rather than implying you looked.

**On a Mac, render it locally before it goes anywhere.** No LibreOffice and no `pdftoppm`
are needed; Pages and PDFKit ship with macOS. Verified 2026-09-23 over five rounds of a
16-page onboarding doc, and it caught every layout defect before Drive did:

Run `scripts/render_docx.sh <file>.docx` from the repo root: Pages exports the PDF (it opens
briefly on screen, and only the file it opened gets closed), then PDFKit writes one PNG per
page. Read the pages. If Pages is busy or showing a dialog, the script exits 4 and leaves a
Quick Look render of page 1 instead.

Pages is a good proxy, not the target. It floors every table row at 12pt, so the accent bar
reads thicker there than in Word or Google Docs, and it ignores column widths that are not in
`tblGrid` (the builder writes both). Everything else it showed matched the Google Doc.

**Take cover and diagram images with `scripts/web_screenshot.sh`, not a bare headless
Chrome call.** `--screenshot` writes the file and then never exits when the page keeps network
activity alive (riverside.com does), so a foreground call times out. The script runs Chrome in
the background, polls for the file, and kills only that Chrome. An `.jpg` output is converted
for you: about 190KB instead of 700KB for a 1920px hero.

**A `<w:br/>` inside a table cell is not reliable.** Drive's own text layer drops it, so
three stacked values come back as `blogsolutionslp` - which is also what a reader may get
after the Docs conversion. Stack multi-value cells as **separate paragraphs** in the cell
instead; `add_run("a\nb")` writes a literal newline that Word ignores, so neither the raw
`\n` nor a `<w:br/>` is safe. Verified 2026-09-23.

**Two things to check that a first pass gets wrong.** A long table starting near the foot of
a page orphans two rows and continues overleaf - give it its own `page_break`. And a `☐` at
body size is too small to read as a tick box; the builder renders it at 13pt, centred.

**Every publish mints a new URL.** The Drive connector can create files but cannot update a
Doc in place. So each revision is a brand-new document, and the superseded one has to be
cleaned up separately with `trash_file`, which moves it to the user's trash (recoverable)
rather than deleting it. Ask before trashing - they are the user's files, not yours. Two
consequences: **validate before publishing**, and **do not treat publishing as a cheap
preview step** - batch the edits, then publish once. A run that publishes ten times has
created nine items of cleanup for the user.

##### If HTML is genuinely the only option

Markdown is worse still: uploading `text/markdown` renders table header rows as literal
`**Header**`. If you must use `text/html`, these are the conversion traps, and
`python3 scripts/lint_gdoc_html.py <file.html>` hard-fails on all of them (`--self-test`
proves the rules still fire):

**A table cell is a plain-text box. Never put markup inside one.** The converter emits any
markup inside `<td>`/`<th>` as literal characters. Every one of these looks correct in the
source and in a browser preview:

| Authored as | Result in the doc |
|---|---|
| `**Header**` in a markdown table | literal `**Header**` |
| `<b>` or `<strong>` inside `<td>` | literal `**text**` |
| inline `font-weight:700` on a `<th>` | literal `**text**` |
| `<a href>` inside `<td>` or `<th>` | literal `\[text\](url)`, and the link stops working |

Leave `<th>` unstyled for weight - the converter bolds header cells on its own. A link has to
leave the table entirely; no in-cell form survives.

**Never wrap inline code in bold.** A `<b>` containing a `<span>` (the pattern you get from
`**text \`code\`**`) emits stray asterisks. Split them: bold label first, code outside it.

**Never put a horizontal rule immediately before a heading.** An `<hr>` directly followed by
`<h1>`..`<h6>` is absorbed into the heading, which then reads `-----Appendix: how we know`.
An `<hr>` before a paragraph is fine.

## Code Reference (docx-js Constants)

```javascript
// Riverside Brand Colors (digital, Brandbook 2026)
const MAIN_BLACK = "1D1D1D";    // Base background / text on light
const MAIN_WHITE = "FFFFFF";    // Text on dark
const MAIN_PURPLE = "9671FF";   // Accent, CTA fill, accent bars
const BLACK_1 = "000000";       // Deepest ground
const BLACK_2 = "111111";       // Deeper band; ground for purple text
const BLACK_3 = "2C2C2C";       // Surfaces and borders on dark
const PURPLE_1 = "AD98FA";      // Softer purple, hover, chart series
const GREY = "F6F6F6";          // Light surface, alt rows
const ACCENT_GREEN = "DFFF84";  // Small accents, never behind white text
```

## Code Reference (CSS / Tailwind)

```css
:root {
  --riverside-black: #1D1D1D;
  --riverside-white: #FFFFFF;
  --riverside-purple: #9671FF;
  --riverside-black-1: #000000;
  --riverside-black-2: #111111;
  --riverside-black-3: #2C2C2C;
  --riverside-purple-1: #AD98FA;
  --riverside-grey: #F6F6F6;
  --riverside-accent-green: #DFFF84;
}
```

### Shape Language
- **Buttons**: Full pill shape (`border-radius: 9999px`).
- **Cards & Panels**: `border-radius: 12px` or `16px`.
- **Card Borders**: A Secondary Black 3 (`#2C2C2C`) card on Main Black separates by fill and needs no border. A card that shares the page fill, or sits darker on Secondary Black 2 (`#111111`), gets a 1px Secondary Black 3 border.

## Common Patterns

### Purple Accent Bar (docx)
A thin purple horizontal rule placed under each H1 section title. Implemented as a single-cell table with Purple fill, no padding, and an exact 2.5pt row height (`w:trHeight w:hRule="exact"`) with a 1pt paragraph mark. A small run font alone does not shrink the row, because an empty paragraph takes its height from the mark.


### Table Style
- Header: Main Black background, White bold text, 9pt
- Body: Alternating White / Secondary Grey rows, Main Black text, 9pt
- Borders: Secondary Grey on all sides (0.5pt Secondary Black 3 when a dense grid needs visible rules)
- Cell padding: 60 DXA top/bottom, 100 DXA left/right

### Bold Labels in Prose
When calling out key terms in paragraph text, use a Bold label followed by regular weight for the description, both in the page's text color (Main Black on light, White on dark). Example: **"Key insight: "** followed by normal text. On a dark ground the label may be Main Purple instead.

## Section Layout Patterns

### 1. The "Light Inversion" (High Contrast)
Used for breaking visual monotony, specifically for Testimonials, Logo Walls, and Pricing tiers.

| Role | Color Name | Hex | Usage |
| :--- | :--- | :--- | :--- |
| **Background** | Main White / Secondary Grey | `#FFFFFF` or `#F6F6F6` | The section container background. |
| **Text Primary** | Main Black | `#1D1D1D` | Headlines and body copy. |
| **Cards/Surfaces**| White + Shadow | `#FFFFFF` | Cards sit on the grey background with a subtle drop shadow. |
| **Accents** | Main Purple | `#9671FF` | Buttons (white text) and icons remain purple to tie it back to the brand. Purple is not a text color here. |

### 2. Cinematic Backgrounds (Full Bleed)
Used for "Hero" moments or "Outcome" showcases (e.g., "See what you can create").

* **Image Rule:** Use high-resolution photography of creators in studios or "lifestyle" recording settings, chosen per **Imagery and Product UI** below.
* **The "Readability" Overlay:** NEVER place white text directly on an image.
    * **Gradient Overlay:** Use a linear gradient from `Main Black (#1D1D1D)` at the bottom/side to `Transparent` to create a safe text area.
    * **Solid Scrim:** If text is centered, use a black background layer at **40-60% opacity** over the image.

**CSS Reference for Image Backgrounds:**
```css
.hero-section {
  background-image: url('studio-shot.jpg');
  background-size: cover;
  position: relative;
}

/* The "Scrim" to make text readable */
.hero-overlay {
  background: linear-gradient(
    180deg, 
    rgba(29, 29, 29, 0) 0%,
    rgba(29, 29, 29, 0.9) 100%
  );
}
```

## Imagery and Product UI

From the brand book. These govern any photo, video still, AI-generated image or product
screen placed in a deliverable: ads, decks, web pages, video, social.

### Photography

There is no single fixed image set; the library evolves. When choosing or creating an image,
make sure that:

- It's high quality.
- It has some depth of field.
- It resonates with our audience.
- It aims for a mix of artificial and natural light, like our best creators have.

Library: [People images and videos](https://www.dropbox.com/scl/fo/qydf89fyjdxet2qqmq33c/AEs_o_oalzFaJeVJd7Temms?rlkey=bdzfgz9ghqy0hdf1fojbdvuyr&dl=0) (Brand's Dropbox).

### People

- **Authenticity.** Characters look credible and authentic, with interesting physical
  features. If a character is AI-generated, it must look realistic, with visible skin texture.
- **Diversity.** Show a diverse range of creators in gender, ethnicity and body type.

### Art Direction

- **Angles.** Front-facing shots are the primary use. Top shots, over-the-shoulder and side
  shots are all usable when they serve the story; they add playfulness.
- **Background and props.** Design the set with care. Backgrounds and props tell the story of
  the persona and the audience type (a business persona's set is not a hobbyist's).
- **Lighting.** Put extra care into it: a balanced mix of artificial and natural light.

### Product Photography

When showing the product inside a mockup (a laptop or monitor in a room), the environment
looks engaging, the lighting feels warm, and the screen appears clean and neat. Library:
[Stock images](https://www.dropbox.com/scl/fo/4ds3jqjhdo9tk06judsrm/AFqJGTCYneocLi03FpPgwVA?rlkey=jp94ow1xdqqijhtgjysp7pb2i&dl=0).

### AI Generation and Stock Imagery

- **Ownership first.** Just like stock, confirm we own or have licensed the image before it
  ships.
- **Real-life feel or it's off-brand.** If an image looks AI-generated and loses its
  real-life feel, it does not ship.
- Use AI tools to scale, refine and work faster, but keeping the brand's DNA always comes first.

Library: [AI generated images](https://www.dropbox.com/scl/fo/phv6zbn63u4aw8re4582p/AJIJfTylzttnPmXgrVP0eYM?rlkey=w7tsdldq16v49bl0kmerp84yf&dl=0).

### Platform UI

Show the real product: its actual colors and layout. Reduce it only for a marketing need, for
example when a CTA inside the UI competes with the page's own CTA. To focus the viewer on one
area, deconstruct the product and show the one UI element that matters instead of the whole
desktop or mobile screen.

The four ways to show the UI:

1. **Full UI**, with relevant changes and color corrections as the story needs.
2. **Simplified UI, medium size**: one panel or component (for example the "Download separate
   tracks" list).
3. **Tiny floating asset**: a single control or chip floating over other content.
4. **Mockup**: the product on a device in a room (see **Product Photography**).

Do's and don'ts:

- **Crop.** Keep a clear sense of scale and enough visual cues for the viewer to understand
  what they are looking at.
- **Microcopy.** Update the UI microcopy to fit the story you're telling, and ask the product
  manager to double-check the spelling.
- **Color.** On some backgrounds the product's colors need adjusting for contrast. That's
  allowed, but take the replacement colors from the product library palette
  (`references/design-system/`), not the marketing palette, so the UI stays consistent.

## Print Colors (CMYK and Pantone): print only

**Never use these on screen**, and never use the digital HEX values for print. CMYK and
Pantone are not Riverside's main color usage. Always get a printed proof, to make sure the
colors come out accurate and follow the same logic as the digital palette.

### CMYK

| Color                  | C  | M  | Y  | K   |
|------------------------|----|----|----|-----|
| Main Black             | 0  | 0  | 0  | 100 |
| Main White             | 0  | 0  | 0  | 0   |
| Main Purple            | 46 | 61 | 0  | 0   |
| Secondary Black 3      | 0  | 0  | 0  | 93  |
| Secondary Purple 1     | 31 | 39 | 0  | 0   |
| Secondary Grey         | 0  | 0  | 0  | 5   |
| Secondary Accent green | 20 | 0  | 74 | 0   |

### Pantone

| Color                  | Coated         | Uncoated       |
|------------------------|----------------|----------------|
| Main Purple            | Pantone 2075 C | Pantone 2075 U |
| Secondary Purple       | Pantone 2086 C | Pantone 2645 U |
| Secondary Accent green | Pantone 2296 C | Pantone 2296 U |
