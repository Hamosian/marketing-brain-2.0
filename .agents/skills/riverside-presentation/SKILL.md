---
name: riverside-presentation
description: Creates and edits Riverside.com branded presentations (.pptx) that match the official Riverside visual identity. Use this skill any time a Riverside slide deck, pitch deck, or presentation is involved - including creating from scratch, editing existing slides, or applying Riverside brand guidelines to any .pptx file. Trigger whenever the user mentions "Riverside deck", "Riverside slides", "our presentation", "slide template", or any request to build slides for Riverside.com. This skill should also trigger if the user uploads or references a .pptx file and mentions Riverside, marketing, team, or internal use.
---

# Riverside Presentation Skill

Produces slide decks that match Riverside's official visual identity: cinematic dark backgrounds, restrained purple accents, Instrument Sans typography, and studio-grade aesthetics.

Always read `/mnt/skills/public/pptx/SKILL.md` for the underlying pptx mechanics (creating, editing, QA workflow). This skill layers Riverside's brand on top of those mechanics.

---

## Brand Identity at a Glance

| Token | Hex | Use in Slides |
|---|---|---|
| Near Black | `#0F0F14` | Slide background (primary) |
| Riverside Purple | `#7C5CFF` | Accents, active lines, H2 labels, CTAs |
| White | `#FFFFFF` | Title text, primary body |
| Dark Gray | `#1C1C24` | Cards, section divider backgrounds |
| Mid Gray | `#2A2A35` | Alt panels, subtle surfaces |
| Light Gray | `#E6E6EB` | Secondary text, captions, dividers |

**Typography**: Instrument Sans (weights 400-700; no Extra Bold). Use SemiBold/Bold (600-700) for titles, Regular/Medium (400-500) for body. Tighten letter-spacing slightly on headings 24pt+.

**Purple is an accent, not a fill.** Never use it as a large background area - only for thin bars, icon circles, highlight text, and active state lines.

**No em dashes** anywhere. Use commas, colons, or rewrite the sentence.

---

## Slide Layouts

### Title / Cover Slide
- Background: Near Black `#0F0F14`
- Riverside logo top-left: `https://upload.wikimedia.org/wikipedia/commons/9/99/Riverside_logo_%282025%29.png`
- Title: White, Instrument Sans Bold, 44pt
- Subtitle: Light Gray `#E6E6EB`, Instrument Sans Regular, 20pt
- Optional: thin 2px Purple horizontal rule between title and subtitle
- Optional: full-bleed background image with a dark scrim overlay (`rgba(15,15,20,0.7)`)

### Section Divider Slide
- Full Near Black background
- Centered section title: White, Instrument Sans Bold, 36pt
- Thin Purple horizontal accent line above the title (width ~120px, centered)
- No other content

### Content Slide (Dark)
- Background: Near Black `#0F0F14`
- Slide title: White, Instrument Sans SemiBold, 28-32pt, top-left
- Optional thin Purple left-border accent beside the title
- Body text: White `#FFFFFF`, Instrument Sans Regular, 14-16pt
- Secondary/caption text: Light Gray `#E6E6EB`, 12pt
- Cards/callout boxes: Dark Gray `#1C1C24` fill, 1px Mid Gray border, 12px radius

### Content Slide (Light Inversion)
Used for testimonials, logo walls, pricing, and social proof sections where readability is critical.
- Background: White `#FFFFFF` or Purple Mist `#F7F5FF`
- Title: Near Black `#0F0F14`, Instrument Sans Bold
- Body text: Near Black `#0F0F14`
- Cards: White with subtle drop shadow
- Accents: Purple `#7C5CFF` remains consistent

### Stats / Data Callout Slide
- Background: Near Black
- Large stat number: White or Purple, Instrument Sans Bold, 60-72pt
- Stat label below: Light Gray, 14pt
- Use 2- or 3-column grid for multiple stats
- Optional: thin Purple underline per stat block

### Two-Column Slide
- Background: Near Black
- Left: text content (title + body)
- Right: visual (image, chart, icon grid, screenshot)
- Maintain 0.5" margins; 0.3" gutter between columns

### Quote / Testimonial Slide
- Prefer Light Inversion layout
- Large quotation mark: Purple `#7C5CFF`, decorative
- Quote text: Near Black, Instrument Sans Regular, 18-22pt
- Attribution: Light Gray, 12pt italic

---

## Visual Motifs (Pick One Per Deck, Stay Consistent)

1. **Thin left-border accent**: 3px Purple vertical bar beside each slide title
2. **Pill labels**: Small Purple `#7C5CFF` pill (rounded tag) before section names
3. **Icon circles**: Icons inside small Dark Gray circles with a Purple border
4. **Corner dot**: Single Purple dot top-right corner of every content slide

---

## Charts and Data

- Primary data series: Purple `#7C5CFF`
- Secondary series: Light Gray `#E6E6EB`
- Tertiary / background: Dark Gray `#1C1C24`
- Chart background: transparent (inherits slide background)
- Gridlines: Mid Gray `#2A2A35`, 0.5pt
- Axis labels: Light Gray `#E6E6EB`, 10pt
- Legend: Light Gray text, 10pt

---

## pptxgenjs Color Constants

When building slides with pptxgenjs:

```javascript
const PURPLE      = "7C5CFF";  // Primary accent
const NEAR_BLACK  = "0F0F14";  // Slide background
const WHITE       = "FFFFFF";  // Primary text
const DARK_GRAY   = "1C1C24";  // Cards / surfaces
const MID_GRAY    = "2A2A35";  // Alt panels
const LIGHT_GRAY  = "E6E6EB";  // Secondary text

// Slide defaults
pptx.defineLayout({ name: "RIVERSIDE", width: 13.33, height: 7.5 });
pptx.layout = "RIVERSIDE";
```

---

## Logo Placement

Always include the Riverside logo on the cover slide and optionally on every slide (top-left, small).

```
Logo URL: https://upload.wikimedia.org/wikipedia/commons/9/99/Riverside_logo_%282025%29.png
Cover slide: width ~2.5", top-left, ~0.4" from edges
Per-slide (optional): width ~1.2", top-left corner
```

---

## Common Slide Patterns

### Cover Slide (pptxgenjs)

```javascript
let slide = pptx.addSlide();
slide.background = { color: NEAR_BLACK };

// Logo
slide.addImage({ path: "https://upload.wikimedia.org/wikipedia/commons/9/99/Riverside_logo_%282025%29.png", x: 0.4, y: 0.35, w: 2.0, h: 0.5 });

// Accent line
slide.addShape(pptx.ShapeType.rect, { x: 0.5, y: 3.2, w: 1.5, h: 0.03, fill: { color: PURPLE } });

// Title
slide.addText("Presentation Title", { x: 0.5, y: 2.5, w: 9, h: 0.8, fontSize: 44, bold: true, color: WHITE, fontFace: "Instrument Sans" });

// Subtitle
slide.addText("Subtitle or date", { x: 0.5, y: 3.4, w: 9, h: 0.4, fontSize: 20, color: LIGHT_GRAY, fontFace: "Instrument Sans" });
```

### Section Divider (pptxgenjs)

```javascript
let slide = pptx.addSlide();
slide.background = { color: NEAR_BLACK };

// Purple accent line above title
slide.addShape(pptx.ShapeType.rect, { x: 5.4, y: 3.0, w: 2.5, h: 0.04, fill: { color: PURPLE } });

// Section title centered
slide.addText("Section Name", { x: 1.5, y: 3.2, w: 10.3, h: 0.9, fontSize: 36, bold: true, color: WHITE, fontFace: "Instrument Sans", align: "center" });
```

---

## Workflow

1. Clarify deck purpose, audience, number of slides, and any content provided
2. Read `/mnt/skills/public/pptx/SKILL.md` for pptx mechanics
3. Read `/mnt/skills/public/pptx/pptxgenjs.md` for creating from scratch
4. Build the deck using the patterns above, with consistent layout per slide type
5. QA: convert to images and inspect visually (see SKILL.md QA section)
6. Fix any overlaps, overflows, contrast issues, or brand violations
7. Deliver via `present_files`

---

## Environment and Delivery

**Check the toolchain before promising a format.** This skill's mechanics assume the cloud sandbox (claude.ai / Cowork), where `pptxgenjs`, LibreOffice and `/mnt/skills/public/pptx` exist. A local Claude Code session on a Mac may have none of them (verified 2026-09-08: no `node`, no `soffice`, no `pdftoppm`, Python 3.9). Probe first:

```bash
node -e "require('pptxgenjs')" ; which soffice pdftoppm ; python3 -c "import pptx; print(pptx.__version__)"
```

- **No Node:** build with `python-pptx` (present on the Mac). Same brand rules apply. Set `slide_width`/`slide_height` to 13.333 x 7.5 in and build from a blank layout.
- **No LibreOffice:** you cannot render the `.pptx`. Generate the deck and an HTML mirror from **one shared spec** (px at 96 dpi, inches = px/96) so they cannot drift, open the mirror in the browser pane, and measure with JavaScript: off-slide elements, `scrollHeight > clientHeight` clipping, card overlaps, top and bottom margins. Full-width centred text boxes report as touching the card edge by design; that is not overflow. Local files render in the pane but screenshots only work while the pane is displayed, so prefer the geometry check.
- **Lean file:** strip the unused slide layouts (python-pptx's default template ships 11), `printerSettings*.bin` and `docProps/thumbnail.jpeg`, then re-zip at compresslevel 9. A 4-slide deck went 40 KB → 24 KB. Validate afterwards: every part parses as XML, every `.rels` target exists, one `<p:sldLayoutId>` per surviving layout.
- **Google Slides delivery:** there is no Slides API connector and the Drive connector cannot take binary content (`docs/platform-integration.md` → Google Drive). Send the `.pptx` with `SendUserFile` and tell the user: drag into Drive, open with Google Slides. Instrument Sans and IBM Plex Mono are Google Fonts, so Slides renders them natively. Do **not** attempt a base64 upload; it corrupts.
- **Cross-account viewers:** colleagues on another Claude org cannot open claude.ai artifact links. A deck for them is the `.pptx` file, not the artifact.

## Brand Rules Summary (Quick Reference)

- Dark background on every digital slide (Near Black `#0F0F14`)
- Purple is accent only, never a large fill
- Instrument Sans font throughout, no substitutions
- No em dashes anywhere
- No loud gradients
- No underline accent lines below titles (use whitespace or background contrast instead)
- Logo on cover slide always
- High contrast: light text on dark, dark text on light inversions
