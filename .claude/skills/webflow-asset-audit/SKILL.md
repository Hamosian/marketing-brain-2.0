---
name: webflow-asset-audit
description: Site-wide audit of riverside.com's Webflow asset library for image alt text and asset naming, via the Webflow MCP's Data API. Finds missing or filename-shaped alt text and Figma-export names (Frame 67296873, Group 596477, versioned "(3)" copies, stubs like ff23.webp), drafts human-reviewable alt text, flags duplicates, and applies approved metadata via data_assets_tool (never the broken headless upload path). Trigger on "audit/fix image alt text at scale", "clean up asset names", "find duplicate assets", "images are missing alt text", "asset audit", "alt text pass", "our asset library is a mess", "rename our Webflow images". Owns the library-wide alt-text rewrite that webflow-accessibility-audit (per-page) leaves out.
---

# Webflow Asset Audit

Site-wide asset hygiene pass via the Webflow MCP Data API - audits the asset library
for missing/poor alt text, junk names, and likely duplicates, then drafts fixes and
applies approved ones as **metadata updates** (`alt_text`, `display_name`). Asset/SEO
companion to `webflow-accessibility-audit`, which audits one page's element tree and
defers the alt-text rewrite pass here.

Adapted from Webflow's own [`webflow/webflow-skills`](https://github.com/webflow/webflow-skills)
`asset-audit` and then corrected against a real run - the numbers and patterns below
are measured, not assumed. Load `systems/owned/marketing-website.md` first.

## Two facts that shape the whole workflow

**1. Renaming an asset does NOT change its public URL.** Webflow freezes the hosted
filename at upload time. Measured on 2026-07-27: 49 of 200 sampled assets had already
been renamed, and *every one* still served its original filename
(`logo MCP TIM FERRISS.svg` → `.../Vector%20(20).svg`). So renaming buys **panel
findability only - zero SEO value**. Never sell a rename as an SEO win. Alt text is
where the real accessibility and SEO value is; lead with it and treat naming as
optional cleanup.

**2. The library is too big to read.** riverside.com held **5,642 assets** (57 pages
at the 100/page maximum) as of 2026-07-27, and each page is ~110-130KB of JSON -
reading pages directly blows the context budget. Always pipe page dumps through
`scripts/classify_assets.py` and reason over its summary.

**3. The write path works, and asset alt really does flow to the page.** Verified
2026-07-27 on `movo.webp` (`685be7dcd32275d383065c79`): `update_asset` set the new
`alt_text`, an independent `get_asset` returned it, and the `/partners` page's image
element then resolved the corrected string too - confirming the inheritance model
below. Two caveats worth knowing: `lastUpdated` did **not** change on the write, so
never use that timestamp to detect whether an update landed - re-read `altText`
itself. And because the element inherits, an asset-level fix reaches **every**
placement of that asset site-wide, not just the page you were looking at; say so when
proposing the change.

**Wrong alt text is a real failure mode here, not a hypothetical.** The same run found
`movo.webp` - the MOVO wordmark logo - described as "A brown, fluffy dog lying relaxed
on a fluffy carpet next to a colorful pillow," and `pigenhole.webp` (the Pigeonhole
Live logo) described as "Pigeanhole". A screen-reader user got a confident, fluent,
entirely wrong description. So treat **existing** alt text as suspect, not as done:
always compare it against `get_asset_preview` rather than only hunting for empty
fields. Plausible-sounding alt on the wrong image is worse than none.

## Steps

1. **Scope.** Confirm before a full-library run: 57 pages is a lot of calls. Prefer a
   slice - newest N pages, one asset folder (`folder_id`), or "only assets missing alt
   text". Default to the **newest 2 pages** if the user just says "audit the assets",
   and say that's what you did.
2. **Fetch.** `data_assets_tool > list_assets` with `site_id`, `limit: 100`, and
   `offset` paging. Riverside.com's site ID is in `systems/owned/marketing-website.md`;
   resolve via `data_sites_tool > list_sites` if unsure (there are two sites - the
   marketing site and Riverside Careers - never assume which).
3. **Classify with the script, not by eye.** Always pass `--out` on a run you intend
   to fix something with - the per-asset records (asset ID, original alt text, issues)
   are what steps 4-7 need, and without them you'd have to reopen the raw dumps that
   don't fit in context.
   ```bash
   python3 .claude/skills/webflow-asset-audit/scripts/classify_assets.py \
     --out <scratchpad>/findings.ndjson <page-dump>...
   ```
   It reports alt coverage, name-pattern prevalence, the rename/URL divergence, and
   duplicate clusters. Expect roughly **55-65% of assets to have no alt text**
   (measured 52% newest, 64% mid-library) - if your run reports wildly different, say
   so rather than quietly assuming the script is right. Note it normalizes whitespace
   before classifying, so a whitespace-only `altText` counts as missing rather than
   passing as healthy; apply the same rule if you ever classify by hand.
   Slice the findings file with `jq` rather than reading it whole, e.g.
   `jq -c 'select(.issues | index("missing-alt"))' findings.ndjson | head -20`.
   **The script cannot detect *wrong* alt text** - alt that is fluent, confident, and
   describes a different image entirely scores as healthy. Only a preview comparison
   catches it, so always spot-check a sample of assets that already have alt (see fact
   3), especially any whose alt reads oddly against its filename.
4. **Draft alt text.** Call `get_asset_preview` (with `asset_id`, not a URL) to *see*
   the image before writing alt text - it returns an error for non-images and anything
   over 2MB, so skip those rather than guessing. Note **SVGs cannot be previewed**,
   which matters here: most partner/brand logos on the site are SVG. For those, draft
   from the brand name and mark the suggestion unverified rather than describing visual
   detail you cannot see. If a preview fails, either skip the asset or mark the
   suggestion "inferred from filename - preview failed"; never present unseen-image alt
   text as confident.
   - Describe what matters **in context**; an intentionally decorative image gets
     `alt_text: null` (which clears it and marks it decorative), never invented text.
   - **Do not flag alt text for length alone.** 24% of Riverside's existing alt text
     exceeds the classic 125-char guideline and is genuinely good, specific description.
     Flag *padding and redundant framing* ("image of…", "photo showing…") and alt text
     that is actually a filename or internal build label ("HP Hero Test_Mobile_2026_05"),
     which is the real defect found here.
5. **Naming (optional, panel hygiene only).** Real patterns worth fixing, in order of
   how much they cost a human hunting for an asset: meaningless stubs (`dsadw.webp`,
   `ff23.webp`), Figma export names (`Frame 67296873`, `Group 596477`, `Rectangle`,
   `Button Text`), and versioned duplicates (`… (1) 1 (6).avif`). Do **not** bother
   normalizing spaces or uppercase in bulk - that's ~75% of the library and pure churn
   for no user-visible gain. `display_name` **does not preserve the extension
   automatically**: always include it (`hero-podcast-studio.avif`), or the asset ends
   up extensionless.
6. **Confirm - the wording, not just "yes".** Present drafts numbered, with per-item
   approval (all / none / skip specific numbers). Alt text is content, not a mechanical
   fix: confirmation means the user approves the **actual wording** (same rule as
   `webflow-accessibility-audit`). The findings file already holds each asset's
   original `altText` verbatim - keep it (don't delete the scratchpad file mid-run), so
   the run can be reverted item-by-item.
7. **Apply one as a canary, then the rest.** Update a **single** approved asset with
   `data_assets_tool > update_asset`, then `get_asset` it and confirm the new value
   actually landed before touching the other 49 - a success response is not proof, and
   the write path is worth proving once per session rather than discovering a failure
   50 assets deep. If the canary doesn't land as expected, stop and report rather than
   continuing. Then apply the remainder, re-fetch, and report successes, failures, and
   skips separately.
   *(The canary is about proving the write path, not about the URL: whether a rename
   changes the hosted URL is already settled - it doesn't - so don't re-litigate that
   with a test rename.)*

## Constraints

- **Metadata only - never upload.** `create_asset` → presigned-S3 silently never
  registers (see `systems/owned/marketing-website.md` Known Issues). This skill only sets
  `alt_text` / `display_name` / `folder_id` on existing assets. Anything needing a
  true re-upload is out of scope - name it as a gap.
- **Never claim a rename helps SEO.** The hosted URL doesn't change (proven above).
  Frame renames as internal findability, or skip them.
- **Never flag alt text purely for exceeding 125 characters.** Judge padding and
  filename-shaped alt, not length.
- **Asset-level alt is a default, not an override.** A page element with its own alt
  keeps it, so fixing the library doesn't retroactively fix every placement. Say so
  in the report; the per-page check belongs to `webflow-accessibility-audit`.
- **Never delete assets, delete/create asset folders, or run `compress_assets`
  from this skill.** `delete_asset` is unrecoverable, asset folders cannot be deleted
  via the API at all, and `compress_assets` **replaces the hosted file in place and
  does not retain the original**. Duplicates are reported for a human to decide.
- Never apply any update without explicit per-item confirmation, and never auto-apply
  invented alt text.
- Ground every finding in fetched data and the script's output; don't infer an asset's
  content from its name when a preview is available.

## Output Contract

```markdown
### Asset Audit - [scope, and what was NOT covered]
- Scanned: [n] of [library total] assets ([n] pages) - [n] missing alt ([x]%), [n] poor alt, [n] junk names, [n] duplicate candidates

## Alt text (the part that matters)
[1] [asset name] - missing → proposed: "[draft]" [| inferred from filename - preview failed]
[2] [asset name] - currently "[filename-shaped alt]" → proposed: "[draft]"

## Naming (panel findability only - does not change the public URL)
[3] [current name] → [proposed-name.ext] - [pattern matched] (write "Skipped - no SEO value, low priority" if deprioritized)

## Likely duplicates (report only - no action taken)
- [asset A] / [asset B] - [same byte size / near-identical name] (write "None" if none)

## Applied (after per-item confirmation)
- [n] updated and re-verified via get_asset, [n] failed, [n] skipped. Originals recorded for revert.

## Out of scope this run
- File re-uploads/conversions/compression, element-level alt overrides, duplicate deletion, [pages not scanned].
```

## Done when

Every in-scope asset is classified through the script, approved fixes are applied and
re-verified by a fresh `get_asset`, originals are recorded for revert, and everything
out of scope - unscanned pages included - is named rather than silently skipped.
