# The payload `render_report.py` reads

The renderer holds no figures. Everything it draws comes from this one file, so the weekly run is: pull, write this payload, render, publish. A structurally complete copy with synthetic values ships as [`../report-data.example.json`](../report-data.example.json), which also smoke-tests the renderer. Live values are deliberately not committed - per `CLAUDE.md`'s content boundary this repo carries pointers, not copies of live data.

All two-element arrays are `[current, prior]` in that order.

## Top level

| Key | Shape | Notes |
|---|---|---|
| `_meta` | object | Windows and data-through dates. Drives every date label in the page. |
| `METRICS` | 5 strings | Funnel stage labels, in funnel order. |
| `CH` | `{channel_group: {cur: [5], prv: [5]}}` | Values ordered as `METRICS`. Fifth element is first MRR. |
| `TOT` | `{cur: [5], prv: [5]}` | Organic totals. Must equal the sum of `CH` on all five metrics. |
| `SHORT` | `{channel_group: label}` | Short labels so table rows stay on one line. |
| `RAILS` | `{channel_group: hex}` | Colour rail per channel. |
| `PAGES` | 25 rows | Top 25 by sign-ups. Row: `[path, fv_cur, fv_prv, su_cur, su_prv, tr_cur, tr_prv, sub_cur, sub_prv, mrr_cur, mrr_prv]`. |
| `SUBPAGES` | 20 rows | Top 20 by new subscriptions, same row shape. |
| `GAIN` / `DROP` | 10 rows each | Sign-up movers. Row: `[path, su_cur, su_prv, fv_cur, fv_prv]`. |
| `AUTH` | strings | Paths to flag as authentication or in-product funnel steps, not acquisition pages. |
| `TOP25_SU`, `TOP25_SUBS` | int | Subtotals for the top-25 table, used in its footer and coverage sentence. |
| `PAGES_WITH_SU` | int | How many pages had any sign-up, for the coverage sentence. |
| `ZERO_SUB_PAGES`, `ZERO_SUB_SU` | int | Pages in the top 25 with zero subscriptions, and their sign-ups. |
| `PAGES_2PLUS_SUBS`, `PAGES_1_SUB` | int | Distribution around the top-20 cut, so the page can say whether the cut is clean. |
| `FINDINGS` | list of objects | The funnel tab's data-notes section. Each is `{sev (1-3), sevlabel, title, blocks: [html, ...], color?}`, ordered by how much each would change a decision. **Written fresh every edition** - a hardcoded finding republishes a stale week's figures. Omit the key entirely and the section is not rendered. |
| `FINDINGS_LEDE` | string | Optional replacement for the default one-line intro above the findings. |
| `GSC` | object | The Search Console tab. See below. |

## `_meta`

```json
{"funnel_window": {"cur": ["2026-08-27", "2026-09-02"], "prv": ["2026-08-20", "2026-08-26"]},
 "funnel_window_note": "Both windows run Thursday to Wednesday and contain exactly 2 weekend days, so the comparison is calendar-matched.",
 "gsc_window":    {"cur": ["2026-08-25", "2026-08-31"], "prv": ["2026-08-18", "2026-08-24"]},
 "snowflake_through": "2026-09-02", "gsc_through": "2026-08-31", "pulled": "2026-09-03"}
```

Both window pairs must be 7 days each and a whole number of weeks apart from the previous run, or the weekend-mix safeguard is violated.

## `GSC`

| Key | Shape | Notes |
|---|---|---|
| `window` | object | `cur` / `prv` label strings, `through`, `lag` in days, and optional `note` for the day-of-week sentence in the window banner. Drives the amber banner. |
| `overall` | `{clicks, impressions, ctr, position}` each `[cur, prv]` | `position` is impression-weighted. |
| `queries_top25` | 25 rows | `[query, clicks_cur, clicks_prv]`. |
| `nb_query_movers` | `{up: 10 rows, down: 10 rows}` | Non-brand only, ranked on absolute click change, same row shape. |
| `pages_top25` | 25 rows | `[path, clicks_cur, clicks_prv]`. |
| `page_movers` | `{up: 10 rows, down: 10 rows}` | Same row shape, ranked on absolute click change. |
| `countries` | 10 rows | `[name, clicks_cur, impr_cur, clicks_prv, impr_prv]`. |
| `ledes` | `{section_key: html}` | Optional one-paragraph reading of each table. Keys: `overview`, `queries_top25`, `nb_up`, `nb_down`, `pages_top25`, `pages_up`, `pages_down`, `countries`. A missing key renders no paragraph, which is correct when a table says nothing worth saying. |
| `read_clicks_note` | html | Optional amber banner in the method notes, for a live caveat such as an unexplained impression step change. |
| `footer_note` | html | Optional replacement for the Search Console paragraph in the page footer. The default states the source, the through-date and the `date` + `device` aggregation, all derived from `_meta`. |
| `method_notes` | list of html | The method-notes prose. Connector defects, why query and page rows do not foot to the property total, and any two-stage pull used to get exact values all go here as paragraphs. |

**The seven table sections are fixed and ordered**, set by Amir on 2026-09-17: top 25 queries, non-brand improved, non-brand declined, top 25 pages, pages increased, pages decreased, countries. Earlier editions also carried brand/non-brand, device, `/blog` and `/de` breakdowns; those payload keys are gone and the renderer no longer reads them. Full spec and the rules that go with it (rank ties at the cut, the two-stage pull): [`build-and-render.md`](build-and-render.md).

## Known gap

The brand rule is Latin-only, so Riverside in Cyrillic, Japanese, Arabic and Ukrainian, plus keyboard-layout garble, classify as non-brand. Last measured at 52 queries and 68 clicks, about 1.3% of non-brand. Closing it needs a transliteration list, not a regex change. It still matters for `nb_query_movers`, which is the only place non-brand classification is now load-bearing.
