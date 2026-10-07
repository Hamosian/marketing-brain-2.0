# Data Dictionary - exact queries, endpoints, and field mappings

Everything the generator pulls, verbatim. Each block is validated live against the source. Keep the SQL, params, and field lists in sync with the dashboard pages that consume them.

All Snowflake queries filter organic channels:
`channel_group IN ('organic search non brand','organic search brand','organic llm')`.

**Parameter - `<REPORT_MONTH_START>`:** the first day of the reporting month (default = first day of the **most recently completed** calendar month, i.e. `DATE_TRUNC('month', DATEADD('month', -1, CURRENT_DATE()))`). Every windowed query below anchors to this, not to `CURRENT_DATE()` directly, so a historical reporting month can be selected and partial-period labelling stays correct. Substitute the resolved date literal at run time.

---

## Step 0 - Freshness gate

```sql
-- Snowflake latest data date (must be >= today-2)
SELECT date_day, COUNT(CASE WHEN metric='first_visit' THEN 1 END) AS organic_first_visits
FROM analytics.bi.marketing_rollover
WHERE channel_group IN ('organic search non brand','organic search brand','organic llm')
  AND date_day >= DATEADD('day', -6, CURRENT_DATE()) AND date_day <= CURRENT_DATE()
GROUP BY 1 ORDER BY 1 DESC;
```

```text
GSC latest date (Windsor searchconsole): get_data fields ["date","clicks"], date_preset "last_7dT".
Latest date returned must be >= today-4 (normal GSC lag is ~2 days).
```

Record each source's latest date → the "Data through" footer strip.

---

## Snowflake

### Query A - monthly funnel by channel (9 months; Exec trend + Exec/Business Impact scorecards)
```sql
SELECT DATE_TRUNC('month', date_day)::DATE AS report_month, channel_group,
  COUNT(CASE WHEN metric='first_visit' THEN 1 END) AS first_visits,
  COUNT(CASE WHEN metric='sign_up' THEN 1 END) AS sign_ups,
  COUNT(CASE WHEN metric='trial' THEN 1 END) AS trials,
  COUNT(CASE WHEN metric='new_subscription' THEN 1 END) AS subscriptions,
  ROUND(SUM(CASE WHEN metric='new_subscription' THEN first_mrr ELSE 0 END),0) AS total_first_mrr,
  COUNT(CASE WHEN metric='mql' THEN 1 END) AS mqls,
  COUNT(CASE WHEN metric='sql' THEN 1 END) AS sqls,
  COUNT(CASE WHEN metric='won_deal' THEN 1 END) AS won_deals
FROM analytics.bi.marketing_rollover
WHERE channel_group IN ('organic search non brand','organic search brand','organic llm')
  AND date_day >= DATEADD('month', -8, '<REPORT_MONTH_START>')
  AND date_day <  DATEADD('month',  1, '<REPORT_MONTH_START>')
GROUP BY 1,2 ORDER BY 1 DESC, 3 DESC;
```
Trailing 9 months ending at the reporting month (the trend window). The reporting month itself is the most recently completed month by default; if a partial current month is included, label it partial.

### Query B - quarterly funnel by channel (QoQ)
Same SELECT shape with `DATE_TRUNC('quarter', date_day)`, `DATEADD('quarter',-4,...)`. Completed quarters compare directly.

**Fair QTD for the current (partial) quarter.** Never compare a partial quarter against a complete one. Cap **both** the current and the comparison quarter at the **same elapsed days from quarter start**:
- Current quarter: `date_day <= CURRENT_DATE()`.
- Prior quarter: `date_day < DATEADD('day', DATEDIFF('day', DATE_TRUNC('quarter', CURRENT_DATE()), CURRENT_DATE()), DATE_TRUNC('quarter', <prior_quarter_start>))` - i.e. the same number of elapsed days.

Equivalently, use the table's built-in rollover fields (`<metric>_day_of_quarter <= today_day_of_quarter`) per metric. Label the current quarter "QTD".

### Query C - funnel by content_group (Business Impact; reporting month + prior month for MoM)
```sql
SELECT DATE_TRUNC('month', date_day)::DATE AS report_month, content_group,
  COUNT(CASE WHEN metric='first_visit' THEN 1 END) AS first_visits,
  COUNT(CASE WHEN metric='sign_up' THEN 1 END) AS sign_ups,
  COUNT(CASE WHEN metric='trial' THEN 1 END) AS trials,
  COUNT(CASE WHEN metric='new_subscription' THEN 1 END) AS subs,
  ROUND(SUM(CASE WHEN metric='new_subscription' THEN first_mrr ELSE 0 END),0) AS total_first_mrr,
  COUNT(CASE WHEN metric='mql' THEN 1 END) AS mqls,
  COUNT(CASE WHEN metric='sql' THEN 1 END) AS sqls,
  COUNT(CASE WHEN metric='won_deal' THEN 1 END) AS won_deals
FROM analytics.bi.marketing_rollover
WHERE channel_group IN ('organic search non brand','organic search brand','organic llm')
  AND date_day >= DATEADD('month', -1, '<REPORT_MONTH_START>')
  AND date_day <  DATEADD('month',  1, '<REPORT_MONTH_START>')
GROUP BY 1,2 ORDER BY 1 DESC, first_visits DESC;
```
Exactly two months - the reporting month and its prior month - so the table's MoM deltas are correct and no stray partial month leaks in.

### Query D - top URLs, HOMEPAGE-CANONICALIZED (Top URLs + Per-URL blend)
```sql
SELECT
  CASE WHEN clean_url_path IS NULL OR clean_url_path IN ('','homepage') THEN '/' ELSE clean_url_path END AS url,
  COUNT(CASE WHEN metric='first_visit' THEN 1 END) AS first_visits,
  COUNT(CASE WHEN metric='sign_up' THEN 1 END) AS sign_ups,
  COUNT(CASE WHEN metric='new_subscription' THEN 1 END) AS subs,
  ROUND(SUM(CASE WHEN metric='new_subscription' THEN first_mrr ELSE 0 END),0) AS mrr
FROM analytics.bi.marketing_rollover
WHERE channel_group IN ('organic search non brand','organic search brand','organic llm')
  AND date_day >= '<MONTH_START>' AND date_day < '<NEXT_MONTH_START>'
GROUP BY 1 ORDER BY first_visits DESC LIMIT 40;
```
**Do NOT add `clean_url_path IS NOT NULL`** - it drops the real homepage (NULL path). The CASE canonicalizes instead.

---

## Ahrefs Rank Tracker (MCP `rank-tracker-overview`, project 8580037, desktop)

- **Current #1 count + movers:** `select: keyword,position,position_prev,best_position_kind`, `date` = latest, `date_compared` = latest−30d, `order_by: position:asc`, `limit: 1000`. Count rows where `position=1` (they sort first). `best_position_kind='ai_overview'` → AI-Overview #1s (≈93% of #1s). Biggest gains = largest `position_prev - position` climbing into the top spots.
- **Prior #1 count (for the −N MoM delta):** same tool, `where: {"field":"position_prev","is":["eq",1]}`, `select: keyword,position_prev`, count rows.
- **Tracked total:** 491 (from the SERP Domination sheet).
- Response includes a `render_with` hint - ignore for generation; we embed aggregates, not the raw table.

---

## Google Search Console via Windsor.ai (`searchconsole` connector)

Key fields: `year_month`, `date`, `query`, `page`, `pagepath`, `clicks`, `impressions`, `ctr`, `position`. **Ignore `branded_vs_nonbranded`** (see safeguards).

- **Monthly totals (trend):** `fields ["year_month","clicks","impressions"]`, `date_from 2025-11-01`, `date_to <today>`.
- **Brand totals (for the split):** Windsor's filter API has **no regex operator**, so do **not** try to express the brand rule as a `contains` filter. Pull query-level rows (`fields ["query","clicks","impressions"]`, no numeric filter) and classify every row locally with `/\b(riv|rev[ei]r)/i`. Then **non-brand = property total − brand** - never non-brand summed from query rows, which under-reports badly (safeguards #12). A `contains "riverside"` filter misses 1,042 clicks of typos per week and `contains "river"` still misses 567, including `reverside`, the largest single typo (safeguards #3).
- **Top non-brand queries (reporting month):** `fields ["query","clicks","impressions","ctr","position"]`, month date range, **no numeric filter** (a `clicks > N` filter truncates per-day rows and understates totals - safeguards #11), then drop rows matching the brand regex and rank locally.
- **Top pages (reporting month):** `fields ["pagepath","clicks","impressions","ctr","position"]`, month range, **no numeric filter** (safeguards #11). Prefer `pagepath` over `page`: `page` splits a page across protocol/`www`/query-param variants. Join to Snowflake on canonical path (`/` = homepage). Exclude non-marketing subdomains and `/hc/*` help-centre paths (safeguards #12).

Brand regex (also used to reclassify GSC queries): `/\b(riv|rev[ei]r)/i` - matches the first syllable, so it catches both tail typos (`riversdie`) and first-vowel typos (`reverside`). Rationale, measured comparison against `riverside` and `river`, and the residual error: safeguards #3.

---

## Blog Reporting sheet (Drive `read_file_content`, id `1uMvbqQq6g7KZpJ11EjOTqNPgxXU5zRUrPKcUZjabg1A`)

Columns: `URL, Title, Existing/New, Page Type, Created On, Publish Date`, with month/section headers inside the tab. Aggregate to: pages touched per month, **new vs refreshed** counts, and the net-new page list. Validate that each section's Publish Dates fall in the labelled month (tab/label ↔ value check). Full tab enumeration needs `gdrive` auth; until then use the readable tab and flag the rest.

**The reader may return several tabs concatenated as stacked markdown tables in one response** (seen: 9 tables - the monthly change-log above, a full CMS export keyed by hashed Webflow item IDs, a "Q1/Q2 Reporting"-style table, a performance tab, others). Split on markdown separator rows (`^\|(\s*:-:\s*\|)+$`) first, then parse month sections only inside the table whose header matches the schema above - see `knowledge/safeguards-and-gotchas.md` #6.

---

## SERP Domination tracking sheet (Drive, id `1hJe6Wn9qFKBLlYivjP5Z7Xtv9E_rxO_du5wGVphKvt8`)

491 keywords: `Keyword, Topic, MSV, Priority` (Priority 16-32). Join key = exact lowercased keyword. Used to enrich Ahrefs rows with Topic + Priority and to define the tracked set.

---

## Page → data map

| Page | Feeds from |
|---|---|
| Executive Summary | Query A (trend + scorecards), Query B (QoQ), Ahrefs #1 counts |
| Business Impact | Query C (content_group table + MoM), Query A (channel funnel), Query B (QoQ) |
| Top URLs | Query D (canonicalized) |
| SERP & Rankings | Ahrefs (#1 counts, movers, AIO share), SERP Domination sheet (taxonomy) |
| Search Console | Windsor monthly totals + brand split, top non-brand queries |
| Content Cohorts | Blog Reporting sheet (activity by month, net-new) |
| Per-URL Performance | Query D × Windsor top pages, joined on canonical path |
