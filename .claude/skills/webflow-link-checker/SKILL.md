---
name: webflow-link-checker
description: "Crawls riverside.com static pages and CMS collections (incl. links in Rich Text fields) for broken, insecure, or redirect-chained links via the Webflow MCP's Data API, scores link health, and can auto-fix HTTP→HTTPS upgrades and redirect-chain collapsing. Use to find broken links, check for 404s across the site, audit redirect chains (esp. the known German/DE locale 301 chains), or investigate the recurring Cloudfront-caching 404 issue in #marketing-website-monitoring. Broader-crawl complement to marketing-website-page-qa (single-page) and webflow-locale-publish-queue (catches localization link rot)."
---

# Webflow Link Checker

Site-wide (or collection-wide) link audit via the Webflow MCP Data API - finds
broken links, insecure (HTTP) links, and redirect chains, and can fix the mechanical
cases with confirmation. This is the tool for a broad sweep; `marketing-website-page-qa`
already covers link-checking for a single page's pre-launch review.

Load `systems/owned/marketing-website.md` first - the Known Issues table documents two
live, recurring problems this skill directly targets: Cloudfront-caching intermittent
404s, and DE-locale 301 redirect chains with duplicate `/de/de-*` paths.

## Steps

1. **Scope the crawl.** Static pages, one or more CMS collections, or both. Confirm
   scope before a full-site run - this can be a lot of calls.
2. **Static pages.** `data_pages_tool > list_pages`, then per page pull its link
   elements via `data_element_tool > query_elements` (`element_filter: {type: "Link"}`,
   or filter `tag: "a"`) scoped to the primary locale - this tool has no `localeId`
   param, so it always operates on the primary locale's content. For a secondary
   locale's static content, read it instead via `data_localization_tool >
   get_page_content` with that locale's `localeId`. There is no `get_static_content`
   action on `data_pages_tool` - don't reference one.
3. **CMS collections.** `data_cms_tool > list_collection_items`, checking both plain
   link fields and links embedded inside Rich Text fields - Rich Text links are easy
   to miss if you only check top-level fields. The API caps each response at 100 items
   (`limit`/`offset`) - **page through with `offset` until a response returns fewer
   than `limit` items**, don't stop after one batch; a "batch of ~50" without an
   exhaustion loop silently misses the tail of any collection over that size.
4. **Test each link.** Issue a request per URL (HEAD, falling back to GET if HEAD
   isn't supported) with a short timeout (~10s) and follow redirects up to a capped
   hop count (~10), recording every hop. **Retry a failed/timed-out request 1-2 times
   with backoff before concluding it's broken** - this skill exists specifically to
   catch *intermittent* Cloudfront 404s, so scoring one transient failure as "broken"
   on the first attempt reproduces the exact false positive it's meant to catch.
   Classify as: OK, broken (4xx/5xx or unreachable **after retries**), insecure
   (`http://` where `https://` is available), a redirect chain (more than one hop
   before the final destination - e.g. `old → temp → final`), or transient (still
   failing intermittently across retries - report separately, don't fix). For a
   chain, resolve to the **final** URL rather than just the first hop; this is the
   shape of the known DE-locale bug (redirect chains ending in a 404 duplicate path).
   If the hop cap is hit before resolving, report it as a redirect loop, not a broken
   link.
5. **Score.** Start at 100. Subtract **5 per broken link**, **2 per insecure link**,
   **1 per redirect-chain link**. Transient failures don't count against the score.
   Floor at 0.
6. **Propose fixes.** HTTP→HTTPS upgrades and redirect-chain collapses (update the
   link directly to its final destination) are mechanical - draft the exact change
   per link. **Confirm before applying anything, and never fix a link only classified
   as transient.** CMS-field fixes go through `data_cms_tool >
   update_collection_items` (this only writes a **draft** - see step 7). Primary-locale
   static-page link fixes go through `data_element_tool > set_link` on the matched
   Link/Button/TextLink element - headless, no Designer connection needed.
   Secondary-locale static content is fixed via `data_localization_tool >
   update_static_content` (pass the corrected node HTML) - this action can only write
   secondary locales; the primary locale's static content has no data-API write path
   other than `data_element_tool`.
7. **Apply, then hand publishing to a human.** `update_collection_items` only stages a
   draft, so a CMS fix is not live until someone publishes the changed items. **You do
   not publish** - publishing is human-only as of 2026-09-15 (see "Publishing safely" in
   `systems/owned/marketing-website.md`). Stage the fix, then tell the person exactly
   which collection items need `data_cms_tool > publish_collection_items` and let them
   run it. Only after they confirm it is published can you re-check a fix against the
   **live URL** - and re-check there, not against the API response, to confirm the
   update is visible to a real visitor. Until then, report the fix as staged, not fixed.

## Output Contract

```markdown
### Link Health - [scope]
- Score: [0-100] ([n] broken, [n] insecure, [n] redirect chains)

## Broken links
- [source page/item] → [broken URL] - [status/error] (confirmed after retries)

## Redirect chains
- [source page/item] → [URL] - chain: [old → temp → final] - recommend pointing directly to [final]

## Insecure (HTTP) links
- [source page/item] → [http:// URL] - https:// equivalent available: [yes/no]

## Transient (still intermittent after retries - not fixed)
- [source page/item] → [URL] - [n] attempts, [n] failures - recheck later, do not treat as confirmed broken

## Fixes applied (after confirmation)
- [n] fixes applied, published where needed, and re-verified against the live URL.
```

## Constraints

- Never apply a link fix without explicit confirmation, and never fix a link
  classified only as transient.
- Always resolve a redirect chain to its final destination before proposing a fix -
  never point a fix at an intermediate hop.
- A CMS fix isn't done until it's published and re-checked live - a draft update or an
  API-only re-check doesn't confirm a visitor sees the fix.
- Ground every finding in an actual tested response (after retries for failures);
  don't infer a link is broken from its URL shape alone or from a single attempt.

## Done when

The health score and full finding list (broken / insecure / redirect chains /
transient) are reported, confirmed fixes are applied, published where needed, and
re-verified against the live page.
