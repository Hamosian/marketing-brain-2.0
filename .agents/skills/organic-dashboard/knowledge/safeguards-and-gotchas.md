# Safeguards & Gotchas - the rules that keep the dashboard accurate

Each of these was learned the hard way. Skipping one produces a plausible-looking but wrong dashboard. The *why* matters as much as the *what*.

## 1. Homepage canonicalization (`/` + `/homepage` + NULL)

- The **real homepage** has `clean_url_path = NULL` in `marketing_rollover` (renders as `""`).
- **`/homepage` is an A/B-test variant** of the homepage (recent test). In isolation it looks tiny and converts terribly (June: 4,488 visits, **2** subs) - because it's a variant slice, not the whole homepage.
- **Always merge `NULL` + `''` + `homepage` → `/`.** Combined June homepage: 36,811 visits, 1,266 subs, $39,089 MRR - the #1 page.
- Apply at **every layer**: Snowflake (the `CASE` in Query D), the GSC join (GSC calls the homepage `/`), and the per-URL blend.

## 2. Never silently drop NULL / empty dimension keys

The first Top-URLs query used `WHERE clean_url_path IS NOT NULL`. Because the real homepage's path is NULL, that filter **deleted the single most important page** and the dashboard showed the A/B variant (4,488) as "the homepage." **Canonicalize NULLs into a real bucket; never exclude them.** If the homepage isn't the top row on Top URLs, this bug is back.

## 3. Brand vs non-brand - do NOT trust Windsor's flag

- **Funnel (Snowflake):** use `channel_group` (`organic search non brand` / `brand` / `llm`). Reliable.
- **GSC (Windsor):** Windsor's `branded_vs_nonbranded` field keys on whether the **literal domain string** appears in the query. So `riverside`, `riverside fm`, `riverside transcription` (tens of thousands of clicks) are labelled **non-brand**, while only `riverside.com` is brand. Using it inflates non-brand with pure brand traffic.
- **Correct approach:** classify GSC query rows with the **first-syllable** regex `/\b(riv|rev[ei]r)/i`, then derive **non-brand = property total − brand**.
- **Match on the first syllable, not on `riverside`.** Brand typos overwhelmingly mangle the tail (`riversdie`, `riverisde`, `riversid`, `riversite`) *or* the first vowel (`reverside`, `riveside`, `revirside`, `roverside`). A `riverside` substring catches neither group, and plain `river` catches only the first - it cannot match `reverside`, which is the single largest typo. Measured over Aug 25-31 2026 (12,916 query rows, 35,880 clicks):

| Brand rule | Brand clicks | Typo clicks missed | False positives |
|---|---|---|---|
| `contains "riverside"` (retired) | 29,461 | 1,042 | 0 |
| `contains "river"` | 30,010 | 567 | 74 |
| **`/\b(riv\|rev[ei]r)/i`** (current) | **30,454** | **143** | **94** |

  The 94 false-positive clicks are almost all brand-intent anyway (`river transcription`, `river podcast`, `river fm`); only `reverse side` / `reverseside` (16 clicks) are genuinely unrelated. The 143 remaining misses are single-letter substitutions on the first character (`riberside`, `roverside`, `tiverside`, `iverside`) and need edit-distance matching to catch - not worth the complexity at 0.5% of brand.
- **The rule change moves the headline number.** Switching from `riverside` to `/\b(riv|rev[ei]r)/i` cut reported non-brand clicks by **5.7%** (17,431 → 16,438 for Aug 25-31). Apply the same rule to both sides of any comparison, or the delta is an artifact of the classifier.

## 4. Freshness gate before generating

- Snowflake rebuilds daily (dbt); expect data through **D-1**. Gate: `MAX(date_day) >= today-2`.
- GSC has a **~2-day lag** (Windsor served through D-2 at last check). Gate: latest `date >= today-4`.
- Stamp each source's "data through" date in the footer strip so consumers always see freshness.
- If a source is materially stale, flag it prominently (banner) or stop - never let stale data masquerade as current.

## 5. Partial-period fairness

- The current calendar month/quarter is incomplete. Label it "(partial)" / QTD / MTD and **never compare it to a full prior period as if complete**.
- `marketing_rollover` has built-in `*_day_of_quarter` / `today_day_of_quarter` fields for fair QTD comparison - use them for current-quarter QoQ.

## 6. Blog Reporting sheet - tab relevance

- The sheet has (or had) multiple tabs; the file reader has surfaced anywhere from one to **all of them concatenated into a single markdown response** (observed August 2026: one read returned 9 stacked tables with different schemas - the monthly change-log, a full CMS export with hashed Webflow item IDs, a "Q1/Q2 Reporting"-style table, a performance tab with subs/clicks/trend columns, and others). Don't assume the reader still surfaces just one tab - check every time.
- **Validate tab name ↔ contents ↔ timeframe**: a "June" section must actually contain June `Publish Date`s; a "Q1" tab must contain Jan-Mar. Select tabs by validated content, not by name.
- **Detect table boundaries before parsing month sections.** Each stacked table is preceded by a markdown alignment-separator row matching `^\|(\s*:-:\s*\|)+$`. Split the raw content on those rows first, identify which resulting table matches the documented `URL | Title | Existing/New | Page Type | Created On | Publish Date` schema (its header row names those columns), and parse month-header sections (`| Month Year |` rows) only within that table. Parsing month headers across the *unsplit* blob silently drips rows from the next table (e.g. CMS-export rows with hashed IDs and full GMT timestamps) into whichever month section was still "open" when the schema changed - producing plausible-looking but wrong per-month counts. This is a NULL-drop-shaped bug: it doesn't error, it just quietly mixes schemas.
- Full tab **enumeration** (naming/ordering all tabs, not just whatever the reader concatenates) still needs `gdrive` authorization. Until then: use only the table(s) matching the documented schema, validate their internal dates, and flag in the output that any other stacked tables were present but not used.

## 7. General path normalization

Beyond the homepage: normalize trailing slashes, strip obvious draft/`-copy`/`homepage-draft` suffixes, and map empty → `/`. **Do not silently merge** anything else that *looks* like a variant - surface suspected variants (e.g. `/de/home` vs `/de`) for human confirmation. The `/homepage` rule is confirmed tribal knowledge; new variants are hypotheses until confirmed.

## 8. Artifacts can't fetch live (CSP)

A published artifact runs under a strict CSP - no `fetch`, no external hosts, no CDN. The agent pulls data at generate time and **embeds** it. "Refresh" = regenerate + republish. Never write runtime data-fetch code into the page; never link external fonts (use the system font stack).

## 9. Update the artifact in place

Routine refreshes must reuse the stable URL (`https://claude.ai/code/artifact/20356f9e-3ecd-44ec-8fe7-d754138a6585`) via the Artifact tool's `url` parameter. Publishing a different file path without `url` mints a **new** URL and breaks the SEO team's bookmark.

## 10. Connector auth reality

- Load-bearing sources - Snowflake, Ahrefs, Windsor.ai - are independent connectors; a run needs those three (+ Drive for the content page).
- `gdrive`, `hubspot`, `monday-api`, `slack` may show unauthorized in a given session; only the sheet **tab auto-detect** depends on `gdrive`. The core funnel/rankings/GSC pull is unaffected.
- The scheduled task runs **in the local app when open** (not a headless cloud sandbox), so it inherits the same connector auth as an interactive session - the "headless can't reach connectors" risk does not apply to the monthly local schedule.

## 11. Windsor numeric filters truncate BEFORE aggregation

A `clicks`/`impressions` threshold in a Windsor `filters` clause does not simply hide small rows: it **changes the totals of the rows it does return**, silently and downward. No error, no warning.

Measured with the dimension held constant at `pagepath`, Aug 25-31 2026, unfiltered against `[["clicks","gt",150]]`:

| Page | No filter | `clicks > 150` | Error |
|---|---|---|---|
| `/pricing` | 1,271 | 886 | −30% |
| `/tools/audio-transcriber` | 1,187 | 778 | −34% |
| `/de` | 1,121 | 832 | −26% |
| `/login` | 1,596 | 1,440 | −10% |
| `/transcription` | 11,471 | 11,470 | −0.01% |

The error scales inversely with row volume: the largest page is untouched while mid-volume pages lose a quarter to a third. That pattern points at the filter being applied to rows finer-grained than the returned aggregate (the long tail of low-click date/query/page combinations), but **the mechanism is not confirmed and the behaviour is dimension-dependent**: the same style of threshold on a `countryname` pull returned totals identical to the unfiltered run, down to a country with 440 clicks over the week. Do not reason about which pulls are safe; treat all numeric filters as unsafe.

**Never use a numeric filter to build a top-N table.** Pull the dimension (`query`, `page`, `pagepath`) with no numeric filter, let the response spill to a file, and rank locally. Dimension filters (`["pagepath","eq","/de"]`) are safe; only numeric ones truncate.

## 12. GSC dimension rows never reconcile to the property total

Breaking GSC down by a dimension does not sum back to the site total, and the error runs in **opposite directions** depending on which dimension:

| Pull | vs property total (Aug 25-31 2026) |
|---|---|
| Property total | 46,892 clicks / 2,205,401 impressions |
| Summed **query** rows | −23.5% clicks / −42.7% impressions (Google anonymizes long-tail queries) |
| Summed **page** rows | +2.6% clicks / +27.7% impressions (one impression can credit several pages) |
| Summed **device** rows | exact match, both metrics |

Two consequences. **Never compute a share from query rows and apply it to the property total** - a brand/non-brand split taken *within* query rows gives non-brand 15.1%, where `total − brand` gives 35.0%, because the withheld long tail is almost entirely non-brand. And use `device` when you need a breakdown that has to add up - not a bare `date` pull, which has its own failure mode (safeguard #13).

**The property also includes non-marketing subdomains.** `sc-domain:riverside.com` covers 178 distinct hosts - `support.riverside.com` (637 clicks), `careers.riverside.com` (175), `api.riverside.com` (7 clicks on 10,328 impressions) and ~170 customer-owned podcast microsites - totalling 863 clicks, 1.8% of the property. Windsor's `hostname` field returns the **apex domain** for every row, so it cannot separate them; parse the full `page` URL instead. Help-centre content on the apex (`/hc/...`) is separate again and also not marketing.

## 13. A date-only Windsor GSC pull collapses days, or returns nothing

Asking Windsor's `searchconsole` connector for `["date","clicks","impressions"]` - date plus metrics, no other dimension - does not reliably return one row per day. It returns multi-day buckets labelled with the bucket's first date, or an empty array. No error either way.

Measured 2026-09-15 against `sc-domain:riverside.com`:

| Requested range | Date-only pull returns |
|---|---|
| 13 Sep - 31 Oct 2025 | correct daily rows |
| **1 Nov 2025 - 9 Aug 2026** | ten monthly buckets; a window shorter than a bucket returns `[]` |
| 10 Aug - 31 Aug 2026 | correct daily rows |
| **1 - 5 Sep 2026** | one bucket on 1 Sep, and 5 Sep returned a second time as its own row |
| 6 Sep - 12 Sep 2026 | correct daily rows |

The bucket arithmetic is exact, which is how the boundaries above were fixed: the 1 Nov row (449,931 clicks) equals 1 Nov-1 Dec summed to the unit, 2 Dec equals 2 Dec-1 Jan, 2 Mar equals 2 Mar-1 Apr, 2 Aug equals 2-9 Aug, 1 Sep equals 1-5 Sep.

**Add any real dimension and every day comes back correctly** - `search_type`, `device`, `page`, `query`, `pathlevel1` all work, across the whole range including the bucketed periods. It is not `search_type` that is special; it is having a dimension at all. A pull with *no* dimension and no date (bare `["clicks","impressions"]` for a window) fails the same way.

Two consequences worth naming separately:

- **The empty result is the dangerous one.** `["date","clicks","impressions"]` for 10-16 Mar 2026 returns `[]`. A report builds that as zero or a blank chart, not as an error. Treat an empty GSC response as a query-shape bug to rule out *before* treating it as an outage.
- **Windows containing a bucket start are inflated.** 30 Aug - 5 Sep 2026 read 51,931 clicks / 2,547,240 impressions against a true 47,489 / 2,235,289 - **+9.4% and +14.0%** - entirely from 5 Sep being counted twice.

**The underlying data is not affected.** Verified 2026-09-15: a Search Console UI export for 1 Aug - 12 Sep 2026 (Search type = Web) matched a dimension-carrying Windsor pull on **all 43 days**, both metrics, zero difference - 274,139 clicks / 14,273,628 impressions on both sides. Windsor serves Google's numbers exactly; only the date-only query shape is broken.

`/weekly-seo-report` pulls every Search Console figure as `date` + `device` for this reason - date-only and no-dimension shapes must never be used. Dimension pulls (device, country, pagepath, query) are safe, and device rows reconcile exactly to the property total, so they are the reliable way to derive a window total.
