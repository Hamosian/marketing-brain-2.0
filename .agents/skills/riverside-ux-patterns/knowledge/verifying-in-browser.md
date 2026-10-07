# Verifying HTML/React artifacts in the in-app Browser pane

This skill's rules (interaction states, focus, motion, validation) are only
proven by *driving* the artifact, not by reading the code. Here is the reliable
way to preview and exercise a self-contained HTML deliverable in the in-app
Browser pane (`mcp__Claude_Browser__*`).

## Getting the page open

The Browser pane's `navigate` tool **blocks `file://` and bare `localhost`
URLs** ("blocked by policy"). Two things that do work:

1. Serve the file over HTTP from its directory, then open it with
   `preview_start` (not `navigate`):
   ```bash
   cd <dir-with-the-html> && python3 -m http.server 8731 &
   ```
   ```
   preview_start { url: "http://localhost:8731/<file>.html" }
   ```
   `preview_start` returns a `tabId` (e.g. `tab-2`); pass that `tabId` to every
   later `computer` / `read_page` / `javascript_tool` call.
2. Kill the server when done: `pkill -f "http.server 8731"`.

`navigate` also requires an explicit `tabId` argument even when only one tab is
open, or it errors on a missing field.

## Driving interaction states

- `computer` click/type coordinates are in **screenshot-pixel space (800x450)**,
  not the page viewport (often 1280x720). Clicking at raw viewport coordinates
  lands off-target and silently focuses nothing. Prefer `read_page` +
  element `ref`s, or drive state directly with `javascript_tool`.
- `javascript_tool` runs a bare expression: **no top-level `return`**. Wrap the
  body in an IIFE - `(() => { ...; return JSON.stringify(x); })()` - and read the
  returned JSON.
- To test a form: set `input.value`, dispatch the event your handler listens for
  (`new Event('blur')`, `new Event('input')`), and submit with
  `form.requestSubmit()`. Then assert on `aria-invalid`, the error node's text,
  `role`, and computed styles.

## Gotcha: computed color reads "wrong" while an element is focused

When you check an invalid field's `border-color` immediately after
`element.focus()`, it can read as the **default** color, not the error color -
even though `aria-invalid="true"` is set. Reason: `:focus-visible` has the same
specificity as the `[aria-invalid="true"]` rule and, being focused, wins. This
is not a bug in the artifact. Call `element.blur()` (or move focus elsewhere)
before reading `getComputedStyle`, and the error color resolves correctly.
Order your CSS so the invalid-state rule still reads clearly when both can apply.

## What a pass looks like

Walk the pre-ship checklist in `SKILL.md` against the live page: one primary
Purple CTA in view, body text never small-Purple, every control has
hover/focus/active/disabled, a **visible** focus ring under keyboard `Tab`,
empty/loading/error/success states that actually fire, 8px-scale spacing, quick
motion, outcome-named copy, and every color/type value traceable to
`riverside-brand-guidelines`. Confirm the brand font actually loaded (not a
silent fallback) with `document.fonts.check('700 40px "Instrument Sans"')`.
