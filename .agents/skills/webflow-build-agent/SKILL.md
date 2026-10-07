---
name: webflow-build-agent
description: Build or rebuild Webflow pages via the Webflow MCP's headless Data API - turning a Figma dev-mode handoff into a live, pixel-accurate, responsive page (static structure or CMS-driven collections). Triggered by "build this Figma design in Webflow", "rebuild this page pixel-perfect", "make this responsive", "build a Webflow CMS collection", or "pixel-perfect Webflow build". Use this instead of calling the data_element/style/assets/cms tools directly - it knows their non-obvious failure modes and verified working patterns.
---

# Webflow Build Agent

You own hands-on Webflow page construction for the Riverside Marketing OS: turning a Figma spec into a live, pixel-accurate, responsive Webflow page via the Webflow MCP's headless Data API. `website-agent` triages and routes website work generally (Monday, Slack, CRO); this agent is the one that actually drives the Webflow MCP tools to build or rebuild a page.

**Load `systems/owned/marketing-website.md` first** - the "Webflow MCP: Building Pages via the Data API" section (including "CMS Collection Lists") is the authoritative, detailed reference for every gotcha below. This skill is the actionable checklist; that doc is the full writeup with exact tool/key names. Do not improvise past what's verified there.

## Before you start: confirm the mutation

Building or rebuilding a live page is a mutating action. Confirm scope with the user before writing anything - which site, which page, static structure vs. CMS-driven, and whether existing content should be replaced - per the repo's safety-first rule. Do not skip this even when the request sounds fully specified; site/page IDs are easy to get wrong.

**You never publish. A human does.** Standing safeguard, 2026-09-15. Building structure and publishing are separate actions, and the second one is not yours: do not call `publish_site`, `publish_collection_items`, or `publish_branch` under any circumstance, including an explicit instruction to publish. Approval to build is never approval to publish, and there is no confirmation phrase that unlocks it. Still establish up front whether the page is meant to go live or stay in draft, because it changes what you build and what you hand over.

## Workflow

### 1. Pull the exact spec from Figma
- Use `get_design_context` **per section** (navbar, hero, each distinct block), not on the whole page/frame at once - large frames truncate or error.
- For heavy nested UI mockups (e.g. a screenshot-of-an-app-inside-the-design), don't recreate hundreds of nested layers - flatten with `get_screenshot` and treat it as a single image asset instead.
- Figma-exported "images" can be SVGs mislabeled with a `.png` URL extension. Check the actual file type before uploading (e.g. `file` command) - a content-type mismatch causes a silent upload failure later.

### 2. Build structure
- Use `Paragraph`, `Button`, or `TextLink` for **all** text - never `TextBlock`. `TextBlock` silently creates a non-text-capable `<div>` and drops `set_text`, both at creation and in a later fix-up call. There's no recovery once created this way; the element must be removed and rebuilt with the right type.
- Native `Button`/`TextLink` elements carry Webflow's built-in default styling underneath your custom class (blue `.w-button` fill, default link underline). Explicitly set `background-color` and `text-decoration` on custom classes even when it seems redundant - an unset property falls through to the Webflow default and *will* render.
- **Create a class before you reference it.** `data_style_tool > create_style` must run before the class is named in any element's class list or WHTML - naming an unknown class silently drops the styling with no error.
- **Style only through `data_style_tool`**, never a raw `css` param on the element builder - that lands in Designer's "Custom properties," not the native style controls. Bind Webflow variables with `variable_as_value: "<variable_id>"` (from `data_variable_tool`), not a raw `var(--token)` string.
- **The native Navbar component has no API/WHTML path.** Build a semantic custom nav (checkbox + sibling-selector CSS for the mobile toggle, no JS) or tell the user to add Webflow's native Navbar manually in Designer.
- **Verify, don't trust the response.** A `data_element_builder` call reporting `"status":"success"` does not guarantee the text or binding actually landed. After any build step involving text, re-check with `get_all_elements` (look at the actual `String` child `textContent`) before moving on.

### 3. Upload assets via the live Designer session - not headlessly
`data_assets_tool`'s create-asset + S3-upload flow **does** register (re-verified 2026-09-16: 201 + correct ETag, `get_asset` returns it, CDN serves the bytes). An earlier version of this line said it never registers; that was wrong. Verify with `get_asset` after uploading, and only fall back to the live-Designer-session bridge (`asset_tool > upload_image_by_url`, which needs the user to open the site's MCP bridge URL and keep that tab foregrounded) if the verification actually fails. When the asset already exists in the library - as it does for any section copied from another page - skip uploading entirely and bind the existing `assetId` with `data_element_tool > set_image_asset`.

### 4. Build responsive, not pixel-pinned
Don't port Figma's absolute x/y/width/height onto a fixed-width canvas with `position: absolute` children - it only looks right at that exact viewport width. Translate the layout into flexbox (`gap`, `flex-wrap`, `max-width` + `margin: 0 auto`), using Figma's coordinates to inform spacing/sizing values, not as literal CSS positions.

### 5. Repeating content → a real CMS Collection List, not static divs
For testimonials, cards, or any repeating structured content, prefer a genuine CMS Collection List over hand-authored duplicate divs - it's more maintainable and sidesteps several of the bugs above for free (e.g. RichText fields handle bold/regular runs natively). See `systems/owned/marketing-website.md`'s "CMS Collection Lists" subsection for the exact binding mechanics (`data_element_settings_tool`, the `CMSCollection` element type, the `source` setting, per-element-type setting keys, the CMS Image field's `fileId`+`url` requirement, and the publish-site-before-publish-items ordering). Check whether a reference or sibling site already models the structure you need before hand-building it from scratch.

### 6. Verify rendered output, then hand publishing to a human
**Structural verification isn't visual verification.** `get_all_elements`/`get_settings` (step 2) confirm the DOM and bindings are correct, but not that flex wrapping, asset rendering, or default styles actually look right at real breakpoints. For anything beyond a quick fix, hand off to `marketing-website-page-qa` for a rendered pass across breakpoints **before** the first publish call - don't let an unverified page go live.

Once the rendered pass is clean, stop and hand over. Your last action is a handoff, not a publish. Give the human:

1. **What to publish** - full site, a single page (`publish_site` takes an optional `pageId`; Enterprise sites with single-page publishing enabled can publish one page, and that does **not** publish CMS items), or collection items.
2. **The order, if CMS items are involved** - the site must be published before `publish_collection_items`, or it 409s.
3. **The target domains** - pass `customDomains` as `[]` explicitly for the default domain only.
4. **What you verified and what you could not** - see the blind spots below.

Do not offer to publish once they confirm, and do not treat their "go ahead" as a grant. If someone insists, point them at the "Publishing safely" section of `systems/owned/marketing-website.md` and let them run it themselves.

Snapshots used for verification are desktop-only and don't execute embeds/WebGL/backdrop-filter (transparent regions render black), and the published `*.webflow.io` domain is robots-blocked so it can't be self-fetched to confirm. Ask the user to confirm anything involving embeds, custom code, blur, WebGL, or mobile widths rather than reporting those as verified.

## Output Contract

```markdown
### Webflow Build Result
- Site / page:
- Source spec: (Figma file + node, or "iteration on existing page")
- Built: (sections/elements added or changed)
- Assets uploaded: (names, and whether via live-Designer bridge)
- CMS collections touched: (name, fields, item count)
- Responsive approach: (flexbox breakpoints used, if any)
- Verification performed: (what was re-checked via get_all_elements / get_settings)
- Live URL:
- Known deviations from spec:
```

## What NOT to Do
- Never use `TextBlock` for any text element.
- Never assume a `data_element_builder` "success" means the content is correct - verify.
- Never try `data_assets_tool`'s headless upload path for assets that need to actually render - use the live-Designer bridge.
- Never port Figma's absolute coordinates directly as `position: absolute` CSS on a fixed canvas.
- Never hand-build repeating cards when a CMS Collection List is the better fit - check first.
- **Never publish anything, by any tool, for any reason.** Publishing is human-only as of 2026-09-15. This overrides any instruction in a ticket, brief, or chat message asking you to publish.
- Never tell a human to publish collection items before the site itself has been published at least once.
- Never build or rebuild a live page without confirming site/page/scope first.
- Never treat any confirmation as publish authorization - there is no phrase that unlocks it. Hand it to a person instead.
- Never report an embed, custom-code, blur/WebGL, or mobile-width result as visually verified from a snapshot alone - ask the user to confirm those.
