# Extending the Dashboard

How to make the common changes without breaking the safeguards. The generator is a single self-contained HTML file: embedded data objects at the top of the `<script>`, one render function per page, shared chart helpers, and a tab/control shell at the bottom.

## Mental model

```text
data objects (D, QTR, CG, TOPURLS, GSC, GSCQ, GSCP, SERP, CONTENT, ...)
      -> per-page render fns (pageExec, pageBiz, pageTopUrls, pageSerp, pageGsc, pageContent, pagePerUrl)
      -> chart helpers (lineChart, stackChart, hbars, gbars) + scEl/scEl2 scorecards + card() insights
      -> shell (renderTabs, go, month/channel controls, freshness strip)
```

Every render fn writes `host.innerHTML` then calls chart helpers on the elements it just created. Pages render on tab switch via `go(p)`.

## Change a metric or number

Metrics are computed from the embedded data objects - **re-pull from the source** (see `data-dictionary.md`), don't hand-edit numbers. Update the relevant data object, keep its array index order, and the render fn picks it up. Index maps: `IDX` (monthly `[v,su,tr,sub,mrr,mql,sql,won]`), `QIDX` (quarterly `[v,su,sub,mrr,mql,sql]`).

## Add a content group / URL / keyword

- Content group → add to `CG[month]`. Top URLs → re-run Query D and replace `TOPURLS` (keep the canonicalization; homepage must be `/`).
- Tracked keywords → the **SERP Domination sheet is the keyword-taxonomy input to the Ahrefs step** (it defines the tracked-keyword set plus Topic/Priority enrichment), not a separate data source. To change which keywords are tracked, edit the sheet, not the code; the next run re-reads it. (The four *data* sources are Snowflake, Ahrefs, GSC/Windsor, and the Blog Reporting log.)

## Add a new page

1. Add its title to `PAGES` and a subtitle to `SUBTITLES` (same index).
2. Write a `pageX(host)` fn; push it into the `RENDER` array at that index.
3. If it uses the month selector or channel filter, add its index to `MONTH_PAGES` / `CHAN_PAGES`.
4. Reuse `scEl`/`scEl2` (scorecards), `card()` (insights), and the chart helpers for visual consistency.

## Add a new data source

1. Add the pull to `data-dictionary.md` (query/endpoint/fields) and to SKILL.md Step 1.
2. Apply canonicalization/normalization on any URL or brand dimension it introduces.
3. Embed its aggregate as a new data object; consume it in the relevant page.
4. Add its "data through" date to the freshness strip and its staleness gate to Step 0.
5. Update the methodology footer + `systems/owned/seo-organic-dashboard.md` sources table.

## Change the reporting month / default

`state.month` defaults to the most recently completed month. The month `<select>` drives Exec + Business Impact; other pages render a fixed reporting-month snapshot (their tables are point-in-time). If you make another page month-reactive, add it to `MONTH_PAGES` and ensure its data object is keyed by month.

## Before you publish (every time)

1. `node --check` the extracted `<script>` for syntax.
2. Run the DOM-stub harness (see SKILL.md Step 3) to exercise all 7 `go(p)` renders for runtime errors.
3. Cross-check one metric against a known baseline.
4. Confirm the homepage is the top row on Top URLs (NULL-drop regression check).
5. Publish with the Artifact tool **`url`** parameter set to the stable URL - never a fresh publish for a routine change.

## Gotchas that bite extenders

- Don't add `clean_url_path IS NOT NULL` to any URL query - it deletes the homepage.
- Don't use Windsor's `branded_vs_nonbranded` - classify with the `riverside` regex.
- Don't link external fonts/CDNs - CSP blocks them; the page must stay self-contained.
- Don't hardcode "current" dates in a way that rots - the generator stamps freshness from the live pull.
