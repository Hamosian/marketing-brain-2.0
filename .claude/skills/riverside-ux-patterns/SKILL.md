---
name: riverside-ux-patterns
description: "Applies Riverside.fm's interaction, layout, accessibility, and usability standards to any UI, artifact, document, presentation, or web component (HTML, React, dashboards, forms, docx, pptx, PDF). Use when building or reviewing anything a person reads or interacts with, even if they only say 'make it look good', 'clean this up', 'improve the UX', or 'design a page'. Owns HOW things behave (layout, spacing, hierarchy, interaction states, accessibility, component behavior, motion, microcopy). Companion to riverside-brand-guidelines, which is the single source of truth for color and typography - trigger both together on the same design/artifact requests."
---

# Riverside.fm UX Patterns

## Overview

Riverside's product feel is cinematic and studio-grade: calm, high-contrast, and confident, never busy or juvenile. Good UX here means the interface gets out of the way so the content (a recording, a transcript, a report) is the star. This skill defines how things are laid out, how they respond to a person, and how a person moves through them.

## Relationship to the branding skill (read this first)

This skill and `riverside-brand-guidelines` are meant to run together on the same request.

- `riverside-brand-guidelines` owns the **visual identity**: exact color hex values, typography, and the "purple is an accent, not a fill" philosophy. It is the single source of truth for color and type.
- This skill owns the **interaction and structure layer**: layout, spacing, hierarchy, states, accessibility, components, motion, and copy.

Rule: whenever a color or a font decision is needed, pull the value from `riverside-brand-guidelines` rather than inventing one here. This skill refers to colors by their brand role (Purple accent, Near Black background, White text, and so on), never by re-declaring hex codes. If the two skills ever seem to disagree on a color, the branding skill wins.

## Marketing UX vs. product UX (read this first too)

This skill and `riverside-brand-guidelines` together are the **marketing** design system - the default for anything a person outside the product reads or clicks through (decks, docs, landing pages, dashboards, artifacts). `references/design-system/` is a separate, **product** design system extracted from Figma (dark product canvas, its own component library, its own token values). The two are not interchangeable and are not meant to be blended.

Default to this skill for marketing work. Only pull from `references/design-system/` when the deliverable is showing or mimicking an actual in-app product screen (a UI mockup, a feature screenshot, a component reference for the product itself) - and in that case, the product tokens govern that screen's rendering, not this skill's patterns.

## Core UX principles

1. **One primary action per view.** Every screen or section has a single obvious next step, expressed with the Purple CTA. Everything else is quieter (secondary or text buttons). Competing primary buttons dilute the path.
2. **Content first, chrome second.** Navigation, toolbars, and decoration recede. Dark surfaces and generous space let the actual content hold attention.
3. **Restraint is the aesthetic.** If an effect (a shadow, an animation, a divider) is not helping someone understand or act, remove it. The studio-grade feel comes from what is left out.
4. **Predictable beats clever.** Standard patterns (a form that validates on blur, a modal that closes on Escape) reduce load. Reserve novelty for genuine moments, not routine interactions.
5. **Accessible by default.** High contrast is already part of the brand. Extend that to focus, keyboard use, target size, and motion so the interface works for everyone.

## Layout and spacing

- **Spacing scale:** use an 8px base grid. Steps: 4, 8, 12, 16, 24, 32, 48, 64. Pick from the scale rather than arbitrary values so rhythm stays consistent.
- **Whitespace is structural.** Group related elements with tight spacing and separate unrelated groups with larger gaps. Let sections breathe; crowding reads as cheap, and Riverside is premium.
- **Content width:** cap long-form text around 60 to 75 characters per line (roughly 640 to 720px) for readability. Full-bleed is for hero and media, not paragraphs.
- **Alignment:** establish a clear left edge and stick to it. A strong grid with consistent gutters does more for the "studio-grade" look than any decoration.
- **Density:** default to comfortable, not compact. Compact density is acceptable only in data-heavy tools (tables, editor timelines) where scanning many rows matters.

## Information hierarchy

- Lead with the single most important thing. Size, weight, and position carry the hierarchy; use the brand type scale for the levels.
- Make interfaces scannable: short headings, chunked content, clear labels. People skim before they read.
- Use progressive disclosure. Show the essential path first; tuck advanced options behind "More", accordions, or a settings surface rather than exposing everything at once.
- Limit choices in view. Long menus and dense option walls stall people; group and prioritize.

## Interaction states (the full set)

Every interactive element needs a defined state for each situation below. Colors come from the branding skill; this skill specifies which states must exist and how they should behave.

- **Default:** resting appearance.
- **Hover:** a slight lift using the brand's lightened Purple. Subtle, not a color flip.
- **Active/pressed:** immediate, obvious feedback on press.
- **Focus:** a clearly visible focus ring (see Accessibility). Never remove focus styling to make something look cleaner.
- **Disabled:** reduced emphasis using the secondary/gray brand roles, with the cursor and lack of response making it clear the control is inactive.
- **Loading:** show progress for anything over ~300ms. Use skeletons for content areas and inline spinners for buttons; keep the layout from jumping.
- **Empty:** never show a blank void. An empty state explains what goes here and offers the first action.
- **Error:** use the brand's functional Error role, place the message next to the thing that failed, say what happened and how to fix it.
- **Success:** confirm completion with the functional Success role, briefly and without blocking.

## Accessibility

Contrast is where brand and accessibility intersect, so be precise. Measured WCAG ratios for the core brand pairings:

| Pairing (brand roles) | Ratio | Small body text (needs 4.5) | Large text / UI (needs 3.0) |
|---|---|---|---|
| White text on Near Black | 19.1:1 | PASS | PASS |
| Light Gray text on Near Black | 15.4:1 | PASS | PASS |
| Purple on Near Black | 4.40:1 | FAIL | PASS |
| Purple on Dark Gray surface | 3.89:1 | FAIL | PASS |
| White on Purple (CTA fill) | 4.35:1 | borderline | PASS |
| Lightened-Purple (hover) on Near Black | 5.52:1 | PASS | PASS |

What this means in practice, and it lines up exactly with "purple is an accent, not a fill":

- **Body text is always White or Light Gray on dark surfaces.** Never set small body copy in Purple; it fails AA.
- **Purple is safe for large text and non-text UI:** headings at large sizes, thick accent bars, icons, borders, and focus rings all clear the 3.0 bar for large/UI elements.
- **Links in body copy** should not rely on Purple alone at small sizes. Pair the accent with an underline or a weight change so the link is distinguishable both to low-vision users and against the contrast shortfall.
- **CTA button labels** (white on Purple) sit just under the small-text threshold, so set them at a larger size and semibold weight, which pushes them into the passing large-text range.

Beyond contrast:

- **Visible focus:** every focusable element shows a clear focus indicator (a Purple ring works and passes as a UI element). Support full keyboard navigation and a logical tab order.
- **Target size:** interactive targets at least 44x44px, especially on touch.
- **Semantics:** use real headings, buttons, labels, and landmarks, not styled divs. Associate every form field with a label. This drives screen readers and keyboard behavior for free.
- **Motion:** honor `prefers-reduced-motion` and disable non-essential animation when it is set.
- **Do not rely on color alone** to convey meaning; pair it with text, an icon, or a shape.

## Component patterns

- **Buttons:** one primary (Purple) per view; secondary as outline; tertiary as text. Label with a verb that names the outcome ("Start recording", not "Submit").
- **Forms:** one column, labels above fields. Validate on blur, not on every keystroke. Put error text directly under the field. Keep the submit button disabled-looking only when you also explain what is missing.
- **Navigation:** keep it minimal and persistent. Show people where they are with an active state. Do not hide primary navigation behind a menu on desktop without reason.
- **Modals and dialogs:** for focused, interrupting tasks only. Close on Escape and on backdrop click, trap focus while open, and return focus to the trigger on close.
- **Tables:** align text left and numbers right, keep headers visible on scroll, and support an empty state. Use the brand's alternating-row treatment for scanability.
- **Feedback (toasts/inline):** confirm actions briefly. Use inline messages for anything tied to a specific element; reserve toasts for transient, global confirmations.

## Motion

- **Purposeful and quick.** Transitions in the 150 to 250ms range for most UI; up to ~400ms for larger surfaces like a modal entering. Faster feels responsive; slower feels sluggish.
- **Ease, do not bounce.** Use standard easing (ease-out for entrances). Playful springy motion fights the restrained, cinematic tone.
- **Motion should explain,** not decorate: reveal relationships, show where something came from, guide the eye to what changed.
- Always respect `prefers-reduced-motion`.

## Microcopy

- **Clear, calm, confident.** Match the brand voice: creator-focused and professional, never cutesy or jargon-heavy.
- **Buttons name the outcome.** "Invite guest", "Export audio", not "OK" or "Submit".
- **Errors are helpful, not blaming.** State what happened and the fix. "We couldn't reach the recording server. Check your connection and try again." Avoid "Invalid input" with no guidance.
- **Empty states teach.** One line on what this area is for, plus the first action.

## Application by output type

**HTML / React (primary surface for UX work):** apply everything above. Define all interaction states, wire keyboard support, respect reduced motion, and use semantic elements. Colors and type come from the branding skill's CSS variables and Tailwind approximations. To verify a build against the pre-ship checklist by actually driving it in the in-app Browser pane (and the non-obvious gotchas of that pane), see `knowledge/verifying-in-browser.md`.

**Presentations (pptx):** hierarchy and pacing are the UX levers. One idea per slide, a clear focal point, generous margins, and consistent alignment across slides. Sequence slides so each builds on the last.

**Documents (docx) and PDF:** UX here is readability and navigation. Enforce the content-width and spacing guidance, use real heading styles so the document is navigable, keep a consistent structure, and add a table of contents for anything long.

**Dashboards and data tools:** comfortable-to-compact density, strong table patterns, obvious empty and loading states, and one clear primary action or filter path. Do not let decoration compete with the data.

## Pre-ship checklist

Before calling any interactive deliverable done, confirm:

1. There is exactly one primary action in view, and it uses the Purple CTA.
2. Body text is White or Light Gray on dark (never small Purple text).
3. Every interactive element has hover, focus, active, and disabled states.
4. Focus is visible and the whole flow works by keyboard.
5. Empty, loading, and error states exist for anything that fetches or submits.
6. Spacing comes from the 8px scale; content columns are not overly wide.
7. Motion is quick, purposeful, and respects reduced-motion.
8. Copy names outcomes and errors tell people how to recover.
9. All color and type values were taken from `riverside-brand-guidelines`.
