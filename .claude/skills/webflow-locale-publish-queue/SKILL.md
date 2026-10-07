---
name: webflow-locale-publish-queue
description: >-
  Bulk "Queue for next site publish" on localized Webflow CMS items in a non-primary locale
  (German/DE, Spanish/ES, French/FR, Portuguese/PT, or any locale) across collections (Blogs,
  Tools, Glossaries, etc.), driven through the Webflow Designer with Claude in Chrome. Trigger on
  "queue these pages for the next publish", "stage the German blog posts", "set these items to
  publish on next site publish", "push the localized items live", handing over a list or CSV of
  pages to queue in a locale, or asking why a single locale can't be published via the Webflow
  API - even if the person doesn't say "queue" but describes staging localized CMS items for a
  Webflow site publish. Browser (Claude in Chrome) task, not an API task.
---

# Webflow locale publish queue

Queue localized Webflow CMS items for the next site publish, in bulk, for a chosen
locale - the exact thing a person would otherwise do by hand in the Designer: open each
item, switch to the target-locale version, and click **Publish now → Queue for next site
publish**.

This skill is a browser playbook. It drives the real Webflow Designer through Claude in
Chrome. It is deliberately not an API integration, for the reason below.

## Who this is for

Not just website work - this is the standard path for anyone staging localized CMS
content in Webflow, including the **SEO team's localization work** (they own the
SEO-facing side of translated pages: hreflang correctness, indexing, and getting the
right locale live). Enter via `/website-agent` for general website/CMS ops, or via
`/seo-ai-search-agent` for SEO-driven localization requests (e.g. "the German
translations of these SEO pages are ready, queue them"). Both routers should invoke this
skill directly rather than going to the API.

## Why the Designer and not the API

The ask here is specifically **"Queue for next site publish"** - staging, where nothing
goes live until someone runs the site publish. Webflow's API and MCP server have no
equivalent action: you cannot queue items (let alone a single locale's versions of them)
for the next site publish programmatically. The Data API's item-publish endpoint pushes
items **live immediately**, which is exactly what this workflow must not do. On top of
that, some CMS items exist in the Designer for a locale but are **not returned by the
API's locale query** (they show a status like "Draft (visible in Designer; not returned
by API locale query)"). Those are exactly the items a naive API approach silently skips.
The Designer sees and handles them fine. So the reliable, locale-safe path is to operate
the UI. If someone asks you to do this via the API, explain this limitation and use the
Designer instead.

> **Re-verified against Webflow MCP 2.0.1 (checked 2026-08-06).** MCP 2.0 removed the
> Designer-session requirement for most operations and added a `data_localization_tool`
> (secondary-locale **content writes** for static pages and components) - useful for
> authoring translations, but still no queue-for-next-publish action and no fix for the
> Designer-only-items gap. `get_more_tools` (category PUBLISHING) confirms no such tool
> exists. Also note the adjacent gaps: there is **no locale-scoped publish** and **no way
> to publish specific CMS items to Staging only** - `data_cms_tool > publish_collection_items`
> publishes items to the **live site** immediately and takes no domain/locale/queue flag;
> staging-only targeting exists solely at the whole-site level
> (`data_sites_tool > publish_site` with `publishToWebflowSubdomain: true`,
> `customDomains: []`). The premise of this skill stands; re-check it against future
> Webflow MCP/API releases.

Queuing only **stages** items; nothing goes live until someone runs the actual site
publish. Say this to the person so expectations are clear.

**That site publish is theirs to run, not yours.** Publishing is human-only as of
2026-09-15 (see "Publishing safely" in `systems/owned/marketing-website.md`). The
publish tools named in the note above appear there to explain why queuing is needed at
all - they are not a fallback for you to reach for when queuing is awkward.

## Inputs to collect first

- **Target locale(s)** - e.g. DE / Deutsch. The primary locale (usually EN) is the one
  you search in.
- **The list of items** - accept either a pasted list (titles, slugs, or URLs) or a
  CSV/spreadsheet. Slugs are the most reliable identifier; titles are convenient but the
  search is fuzzy (see gotchas). If you get URLs, the slug is the last path segment.
- **Collection(s)** - Blogs, Tools, etc. Items in different collections require selecting
  that collection in the left sidebar. Group the worklist by collection so you do one
  collection at a time.
- **Webflow Designer URL** - the CMS workflow view. Riverside default (staging):
  `https://riversidefm-design-com-domain-staging.design.webflow.com/?workflow=cms`
- **Confirmation preference** - per item, per batch, or one upfront go-ahead. Default:
  confirm once before the first commit, then proceed and report per item.

Requirements: the person's Chrome must be signed in to Webflow with edit access to the
site. This is a side-effectful workflow (it stages content for publish), so treat the
first queue click as an action that needs a clear go-ahead.

## The core loop (per item)

The whole task is this loop repeated. It generalizes to any collection and any locale -
only the collection you select and the locale row you jump to change.

1. **Be in the primary locale (EN) list** for the right collection. Select the collection
   in the left sidebar; set the top locale selector to the primary locale (EN) so item
   names match your English search terms.
2. **Find the item.** Type a distinctive part of the title (or the slug) into the
   collection search. Wait for results to settle, then confirm you have the right item.
3. **Open it and verify identity by slug**, not just the displayed title - the fuzzy
   search and list re-renders can surface look-alikes. The open item shows its slug near
   the top; check it matches your target before doing anything.
4. **Jump to the target-locale version.** Scroll to the item's **locale status table**
   (near the bottom: Deutsch / English / Spanish / …). Click the jump arrow on the target
   locale's row. You know you're on that version when that locale is listed **first in the
   table with no jump arrow** and the header shows its name/status.
5. **Open Publish now → Queue for next site publish.** Click the caret next to "Publish
   now", then the top menu item.
6. **Verify** (see Verification), and while you're on the item, **capture the locale's
   name and live URL** for the report (see Output). The URL preview sits right under the
   Slug field on the open item - the localized slug can differ from the primary one (e.g.
   `/de/blog/so-nimmst-du-...` vs the English `how-to-...`), so read it from the item
   rather than assuming. Then move to the next item.

## Locating items reliably (this is where runs go wrong)

The Designer's search and list are laggy and fuzzy. Slow down here; a wrong click can open
the wrong item.

- **The list lags.** After typing a query, the results often keep showing the *previous*
  item for a second or two ("stale row"). Always wait ~3s and re-screenshot before
  trusting or clicking a row. If the row still shows the last item's name, wait again.
- **Search is fuzzy / token-based**, not exact-prefix. A multi-word query can return many
  partial matches ranked by relevance; the first row is not guaranteed to be your item.
  Prefer a distinctive phrase. If the exact title returns nothing, try a shorter unique
  token from it.
- **Confirm by slug after opening.** Do not queue anything until the opened item's slug
  matches your target. Titles get renamed; slugs are stable.
- **Renamed items.** If an item can't be found by its expected title (e.g. the list came
  from an old export), the English name was probably changed. Don't guess - flag it in the
  report and ask the person for its current title or slug.
- **Clearing the search box.** After switching locale, the search field sometimes keeps
  its old text and your new text appends to it. Triple-click the field to select all, then
  type, and verify the box shows exactly your query before waiting on results.

## UI gotchas learned the hard way

- **Don't hardcode pixel coordinates.** The window can be different sizes between sessions,
  which shifts every control. Use `find` / `read_page` to locate the locale jump arrow and
  buttons, and screenshots to confirm, rather than memorized coordinates.
- **The locale jump can be sticky.** Clicking the target-locale jump arrow sometimes
  changes the URL locale but leaves the panel on the previous version. Reliable recovery:
  `scroll_to` the arrow before clicking; if it still hasn't switched, click the arrow
  again (by its on-screen position) and wait ~5s. Confirm success by the target locale
  being listed first with no arrow.
- **The Publish-now menu often needs a second click** after a page transition - the first
  caret click may not open it. Screenshot; if the menu isn't open, click the caret again.
- **Never blind-double-click the caret.** A second click when the menu is already open
  closes it. Click once, screenshot, decide.
- **Returning to the list.** Use the **back arrow at the top-left of the open item**
  (just left of the item title) - that is what reliably reopens the full list *with the
  search bar*. Clicking the collection name in the left sidebar does **not** do it: it
  leaves the item open and the middle column filtered, with no top search box. If one back
  click is absorbed, click it again.
- **Typing without the search box focused fires Designer keyboard shortcuts - this will
  silently throw you into the Design/canvas view.** Single letters are tool shortcuts (A =
  Add panel, etc.), so a stray `type` after a page transition (e.g. right after the back
  arrow) executes a dozen shortcuts instead of searching. **Every time before you type a
  query: click the search box, then screenshot and confirm it's focused (blue outline) -
  and after a `triple_click`, confirm the old text is selected/highlighted - before
  sending `type`.** Recovery if it happens: click **CMS** in the top nav to return to the
  collection list; nothing is harmed as long as no element was selected (the canvas
  shortcuts don't add/delete without a selection).
- **Reading status without a screenshot (fast path).** The `find` tool, queried for
  something like *"Slug field value and the Deutsch locale row status"*, returns both the
  slug (identity check) and the target-locale status text in one call - much cheaper than
  scroll-to-table + screenshot for a batch that may already be queued. It has been
  reliable, but screenshot-confirm the locale table on any item that is **not** already
  queued (i.e. before/after you actually click Queue) and on a final spot-check.
- **The top locale selector won't open while an item is open** - you can't switch the whole
  list to the target locale to read statuses in bulk from an item view; do it from the list
  view, or just read each item's own locale table (above). `scroll` in this browser tool
  caps `scroll_amount` at 10 - use `scroll_to` a `find` ref to reach the locale table
  instead of large scrolls.
- **A dropped Chrome connection** shows "Cannot access contents of the page". Reloading the
  Webflow tab (navigate to the same Designer URL) restores access; the queued items you
  already committed persist.

## Verification

Status text lags a few seconds after you click Queue, so a single screenshot right after
often still says "Draft". Two reliable checks:

- The target locale's row changes to **"Queued to publish"** and the header shows
  **"Queued to publish"** (a brief "Item queued to publish" toast may also appear).
- Reopening the Publish-now menu now shows **"Remove from queue"** instead of "Queue for
  next site publish". This is the surest signal. Close the menu afterward (Escape) without
  clicking Remove.

Record each item's outcome as you go so the final report is accurate.

## Status cases you'll encounter

The target-locale row status tells you what to expect:

- **Draft** (never published in this locale) → Queue makes it publish on next site publish.
- **Changes in draft** / live-with-unpublished-edits → Queue stages the current edits.
- **Published** with no pending changes → the menu offers only **Unpublish**; there is
  nothing to queue. Record it as "already live, no action needed" - do not Unpublish.
- **Queued to publish** (already staged, e.g. from a prior run of this same request) →
  nothing to do; record as "already queued, no action needed" and move on. Do **not**
  re-queue or click Remove from queue. Don't assume a whole batch is done because the first
  few are already queued - verify each item, since a partial prior run can leave a mix.

## Safety

- Confirm before the first queue commit (respect the person's confirmation preference).
- Only ever click **Queue for next site publish**. Do not click Unpublish, Remove from
  queue, Delete, or Schedule unless explicitly asked.
- Never run the actual site publish yourself unless explicitly asked - queuing is the ask.
- This is browser-only; the API/MCP has no queue-for-next-site-publish action, and its
  item-publish endpoint goes live immediately (see top).

## Output: per-item report (always produce this)

End with a clear status list grouped by outcome, so the person can see exactly what
happened and act on anything left:

```
## Queued for next <locale> publish (verified)
- <collection>: <item name> - <locale live URL>
...

## Already live, no action needed
- <item name> - Published in <locale> with no pending changes - <locale live URL>

## Not completed / needs input
- <item name or slug> - <reason, e.g. couldn't locate; title appears changed; needs current title/slug>
```

Remind the person that queuing only stages the items - a site publish is still required to
take them live.

### Exported list/file with names and localized URLs

Offer to save (and by default do save, unless the person declines) a structured file
capturing each item's name and its live URL in the relevant locale(s). This is the durable
record of the run and is easy to re-share. Produce it as a CSV (best for spreadsheets) or a
markdown table - ask the person's preference, defaulting to CSV. Save it to the outputs
folder and share it.

Build it from the details you captured on each item in loop step 6. One **row per
item-and-locale** so multi-locale requests are represented fully. Columns:

```
Collection, Item name (primary/EN), Item name (locale), Locale, Locale slug, Locale live URL, Status
```

Where:
- **Item name (locale)** is the translated name if the locale has one, else the primary
  name. **Locale slug / Locale live URL** come from the URL preview under the Slug field on
  the target-locale version - read them there, since the localized slug often differs from
  the primary one.
- **Status** is one of: Queued, Already live, or Not completed (with reason).

If a request spans multiple locales, either one combined file with a Locale column, or one
file per locale - ask which the person prefers.

## Generalizing to more collections and locales

The loop is identical regardless of collection or locale. To scale:

- **More collections:** group the worklist by collection and process one collection at a
  time (select it in the sidebar). The search box, locale table, and Publish-now menu
  behave the same in every collection.
- **More locales:** the locale status table lists every configured locale. Jump to
  whichever the person wants (Spanish, French, Portuguese, …) using the same arrow. You can
  even queue the same item in several locales by jumping to each locale row in turn and
  queuing each. Search is always done in the primary locale, because non-primary item names
  are often translated and won't match your source titles.

## Practical expectations

- A run of ~20 items takes a while because it's one item at a time in the Designer, and
  the UI is laggy - expect it to be methodical rather than fast, and say so upfront.
- Best results come from giving **slugs** (most reliable) and grouping items by
  collection.
- If Chrome shows "Cannot access contents of the page", reload the Webflow tab -
  already-queued items persist.

## Example

**Input:** "Queue these 5 German blog posts for the next publish: how-to-start-a-podcast-for-free,
streaming-setup, top-podcasts, podcast-structure, most-popular-podcasts."

**Approach:** Open the Designer CMS view → select Blogs → set locale to EN → for each slug,
search a distinctive term, open the item, confirm the slug, jump to the Deutsch row, open
Publish now → Queue for next site publish, verify "Queued to publish" / "Remove from
queue". Confirm once before the first commit, then run through the rest and report each.
