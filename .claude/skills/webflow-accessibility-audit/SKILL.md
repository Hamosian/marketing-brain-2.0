---
name: webflow-accessibility-audit
description: "Headless WCAG 2.1 accessibility audit of a Webflow page or set of pages, scored 0-100, using the Webflow MCP's Data API (no Designer session or browser needed). Checks touch-target size, form labeling, link/button text, heading structure, and focus-visible states, and can apply fixes via set_attributes with confirmation. Use whenever someone wants to audit, score, or remediate accessibility issues on riverside.com pages, or asks \"check this page for accessibility issues\", \"WCAG audit\", \"a11y audit\", \"is this page accessible\", or references #website-accessibility work. Complements marketing-website-page-qa (browser-based, pre-launch QA doc) by running a fast, headless, element-level pass any time, not just before a launch."
---

# Webflow Accessibility Audit

Runs a headless WCAG 2.1 pass over a Webflow page's element tree via the Webflow MCP
Data API and returns a 0-100 score plus a prioritized issue list. No Designer
connection or browser is required for the audit or for applying fixes - only a page
ID. A Designer session is only useful afterward, for a human to visually confirm a fix.

Load `systems/owned/marketing-website.md` first for site/page context. Accessibility work
is ticketed on the Website Development board (the `#website-accessibility` channel is no
longer used, 2026-09-23).

## What this checks

- **Forms** - inputs without an associated `<label>` or `aria-label`.
- **Links and buttons** - empty link/button text, or non-descriptive text ("click
  here", "read more") with no `aria-label` fallback.
- **Headings** - missing or skipped heading levels, more than one `<h1>`.
- **Touch targets** *(approximate)* - interactive elements (buttons, links, form
  controls) whose **declared** class styles put them under **44x44px** are flagged.
  This is WCAG 2.1 **SC 2.5.5, Level AAA** (not a baseline AA requirement) - label it
  as such in findings. Treat it as a heuristic, not a certainty: the element tree and
  declared class styles don't include computed/rendered layout (responsive
  breakpoint overrides, inheritance, box-sizing), so the true rendered size can
  differ. Flag it, but recommend confirming visually (e.g. via
  `marketing-website-page-qa`'s rendered pass) before treating it as certain.
- **Focus states** *(approximate, same caveat)* - interactive elements whose declared
  styles set `outline: none` with no visible-focus replacement declared elsewhere.
  This is read from declared class styles, not the final computed/cascaded result -
  flag it, but confirm with a rendered pass before certainty.

## What this does NOT check (say so explicitly in the output - never imply full WCAG coverage)

- **Color contrast** - needs rendered pixel values, not just the element tree; out of
  scope for this headless pass.
- **Alt text quality** - flag *missing* `alt` on `Image` elements as a finding here,
  but the full alt-text rewrite pass is a separate concern (asset/SEO hygiene) owned
  by `webflow-asset-audit` - route the user there if they want that depth.
- **Motion/reduced-motion preferences, and real screen-reader behavior** - this is a
  static-tree check, not a live assistive-tech run.

## Steps

1. **Identify scope.** One page, several pages, or a whole site - confirm before a
   multi-page run since each page is a separate `get_all_elements` call.
2. **Pull the element tree.** `data_pages_tool > list_pages` to resolve the page ID if
   given a URL/slug, then `data_element_tool > get_all_elements` on each target page.
3. **Score.** Start at 100. Subtract **10 per critical** finding (e.g. a form input
   with no label at all, a link with genuinely empty text), **5 per serious** (e.g. a
   touch target under 44px, a skipped heading level), **2 per moderate** (e.g. a
   generic "click here" link with no `aria-label`). Floor at 0.
4. **Propose fixes - but don't treat missing `alt`/`role` as blindly mechanical.**
   A missing `alt` isn't a one-size-fix: an intentionally decorative image should get
   `alt=""`, not invented text, while an informative image needs real,
   human-authored descriptive text - draft a suggested description but flag it for
   the user to confirm or rewrite rather than auto-applying invented copy. Don't add
   a generic `role` that conflicts with the element's native semantics (e.g. don't add
   `role="button"` to an actual `<button>`). Reserve genuinely mechanical fixes
   (`aria-label` on an already-identified non-descriptive link/button, a missing
   `<label>` association) for auto-drafted `set_attributes` calls. **Confirm with the
   user before applying any fix** - this is a mutating call, no exceptions, per the
   repo's safety-first rule - and for alt-text/role findings, confirmation means the
   user approves the actual wording, not just "yes, fix it."
5. **Apply and re-verify.** After fixes are confirmed and applied, re-run
   `get_all_elements` on the changed elements to confirm the attribute actually landed -
 don't trust a "success" response at face value (the same discipline
   `webflow-build-agent` applies to its own builds).

## Output Contract

```markdown
### Accessibility Audit - [page name(s)]
- Scope: [page(s) audited]
- Score: [0-100] ([n] critical, [n] serious, [n] moderate)

## Findings
### [Finding title]
- Severity: Critical / Serious / Moderate
- Location: [element / section]
- Issue: [what's wrong]
- Fix: [proposed set_attributes change, or "needs Designer/human judgment"]

## Not checked (out of scope for this pass)
- Color contrast, alt-text quality/rewrite, motion preferences, live screen-reader behavior.

## Applied (after confirmation)
- [n] fixes applied and re-verified via get_all_elements.
```

## Constraints

- Never apply a `set_attributes` fix without explicit confirmation first.
- Never auto-generate alt text or add a `role` without the user confirming the actual
  content/value - these aren't mechanical fixes like a missing `aria-label`.
- Never report touch-target or focus-state findings as certain - they're read from
  declared class styles, not computed/rendered layout; always caveat and recommend a
  rendered-pass confirmation.
- Never claim color contrast, motion, or screen-reader behavior was checked - this
  pass structurally cannot check them; say so every time, not just once.
- If a page ID can't be resolved from what's given, ask rather than guessing which
  page was meant.

## Done when

The score and full finding list are reported, confirmed fixes are applied and
re-verified, and anything out of scope is named rather than silently skipped.
