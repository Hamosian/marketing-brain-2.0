# Data Dictionary - the weekly pulls, verbatim

Two sources, and only two: Snowflake for the funnel, Google Search Console via
Windsor.ai for search. **No Ahrefs, no Omni, no rank tracking.** Rankings are a
monthly question and belong to `/organic-dashboard`; a week of rank movement is
mostly crawl-schedule noise and it crowded out the funnel when it was tried.

The monthly sibling documents the same two sources at monthly grain in
[`../../organic-dashboard/knowledge/data-dictionary.md`](../../organic-dashboard/knowledge/data-dictionary.md).
This file carries what differs for a 7-day window.

## Parameters

`scripts/resolve_week.py` resolves every window. Never compute dates inline.

| Token | Meaning |
|---|---|
| `<CUR_START>` / `<CUR_END>` | the 7 complete days ending yesterday, inclusive |
| `<PRI_START>` / `<PRI_END>` | the 7 days before that, inclusive |

Ranges below are **inclusive** on both ends (`BETWEEN`), matching how the script
reports them.

---

## Step 0 - Freshness

```sql
SELECT MAX(date_day) FROM analytics.bi.marketing_rollover
WHERE channel_group IN ('organic search non brand','organic search brand','organic llm');
```
Must be >= `<CUR_END>`. Snowflake rebuilds daily and normally reaches D-1.

**GSC is checked separately and never blocks the funnel tab** - see the
two-window rule below.

---

## Snowflake - one query shape, pivoted on the window

Every funnel table comes from the same CTE, which tags each row's window and
pivots. This is what keeps the tables cross-footing to each other.

```sql
WITH p AS (
  SELECT
    CASE WHEN clean_url_path IS NULL OR clean_url_path IN ('','homepage')
         THEN '/' ELSE '/'||clean_url_path END AS url,
    CASE WHEN date_day >= '<CUR_START>' THEN 'c' ELSE 'p' END AS w,
    channel_group, metric, first_mrr
  FROM analytics.bi.marketing_rollover
  WHERE channel_group IN ('organic search non brand','organic search brand','organic llm')
    AND date_day BETWEEN '<PRI_START>' AND '<CUR_END>'
)
```

Then aggregate with the standard five, per whatever dimension the table needs
(`channel_group`, `url`, or nothing for the totals):

```sql
  COUNT(CASE WHEN w='c' AND metric='first_visit'      THEN 1 END) AS fv_c,
  COUNT(CASE WHEN w='c' AND metric='sign_up'          THEN 1 END) AS su_c,
  COUNT(CASE WHEN w='c' AND metric='trial'            THEN 1 END) AS tr_c,
  COUNT(CASE WHEN w='c' AND metric='new_subscription' THEN 1 END) AS sub_c,
  ROUND(SUM(CASE WHEN w='c' AND metric='new_subscription' THEN first_mrr ELSE 0 END),2) AS mrr_c
```
plus the `w='p'` mirror of each.

**`first_mrr` must be filtered to `new_subscription` rows.** It is populated on
rows that are not subscriptions: the unfiltered organic sum was $72,923.98
against a correct $16,374.12 for the week of Sep 3, a 4.5x difference that runs
without error and looks plausible.

### The tables

| Table | Dimension | Order | Cut |
|---|---|---|---|
| Overall | none | n/a | n/a |
| Split by channel | `channel_group` | fixed: non-brand, brand, LLM | all 3 |
| Top landing pages | `url` | `su_c DESC` | 25 |
| Sign-up movers | `url` | `su_c - su_p`, both directions | 10 each |
| Top pages by subscriptions | `url` | `sub_c DESC, mrr_c DESC` | 20 |

**Ranking pitfall.** `ORDER BY window DESC, metric DESC LIMIT n` returns `n`
rows of the newest window only and no prior rows at all, so every WoW column
comes back empty. Pivot per URL as above, or rank inside each window with
`QUALIFY ROW_NUMBER() OVER (PARTITION BY window ORDER BY ... ) <= n`.

**Movers rank on absolute change across all pages**, not the top 25, and not on
percentage. A percentage ranking fills both lists with pages going from 1
sign-up to 4.

### Coverage figures the leads cite

Compute these rather than eyeballing them: pages with any sign-up, the top-25
sign-up subtotal (it must equal an independently computed `SUM` of the top 25),
pages with 2+ subscriptions, and the NULL-path share of subscription rows.

---

## Google Search Console via Windsor.ai (`searchconsole`)

### The two-window rule

Windsor lags roughly 3 days, so **the Search Console tab runs on its own window
and is labelled as such on every table.** The two tabs overlap and must never be
read as the same period. This is the design, not a defect: it is better than
holding the funnel back three days.

### The single-dimension `date` rollup is defective, so never use it

Verified 2026-09-10. Pulling `["date","clicks","impressions"]` over early
September returned **no row at all for Sep 2, 3 and 4**, and a Sep 1 row of
34,507 clicks on 1,619,417 impressions.

Adding one field, `["date","device","clicks","impressions"]`, returned **every
day complete** over the identical range with the identical credentials. The data
was never missing; the rollup was wrong.

The merge is exact: Sep 1 to 5 summed from device rows is 34,507 clicks and
1,619,417 impressions, the Sep 1 row to the unit. So the rollup buckets five
days into the first, emits Sep 5 again on its own, and drops Sep 2 to 4.

It is the dimension, not the range: `date` alone over Sep 2 to 4 returns an
empty result, while `date` + `device` over Sep 2 to 4 returns all nine rows.

**Always request `date` with a second dimension and aggregate locally.** Device
is the right choice because device rows reconcile exactly to the property total
(see the reconciliation table below), so the sum is exact.

**The standing check:** rebuild the *prior* window from device rows and confirm
it reproduces the figures the last edition published. On 2026-09-10 that gave
46,892 clicks on 2,205,401 impressions at impression-weighted position 14.94,
matching the Sep 3 edition exactly, which is what makes the method trustworthy
rather than merely different. Impression-weight `position` when aggregating;
a naive mean of device rows is wrong.

Do not describe this as an outage or as missing data. The feed is current at the
normal ~3-day lag, and Ahrefs holds an independent GSC connection to the same
property whose overlapping days agree to the click.

### Never use a numeric filter

A `clicks > N` clause does not just hide small rows, it **changes the totals of
the rows it returns.** Same window, `pagepath` dimension: `/pricing` came back
as 1,271 clicks unfiltered and 886 under `clicks > 150`; `/de` 1,121 against
832. The largest page barely moved, so the error hits low-volume rows hardest
and is invisible without a control pull. It is also dimension-dependent, so it
cannot be predicted, only avoided.

**Pull the dimension unfiltered, let the response spill to a file, rank
locally.** Dimension filters (`["pagepath","eq","/de"]`) are safe.

Confirmed on `query` too, 2026-09-17, and it is worse there. At `clicks >= 25`:
`streaming setup` 68 against a true 151, `ai transcription free` 30 against a
true 103 - 3.4× understated. Lowering the threshold to 4 made the large values
exact (`clipper video` 63 = 63) but left small ones short (`transcribe` 4
against a true 12). A filtered pull also renders a row that falls below the
threshold as **absent**, which a movers table reads as a zero:
`transcribe audio to text free online` looked like a collapse to 0 and was
actually 23.

When the unfiltered pull is too large to be practical, use the two-stage
method: a low-threshold pass to pick candidates, then re-pull exactly those
keys with `["query","in",[...]]` / `["pagepath","in",[...]]` and no metric
filter, for both windows. Publish only the second pass. Full worked example in
[`build-and-render.md`](build-and-render.md).

### Dimension rows never reconcile to the property total

| Pull | vs property total |
|---|---|
| Summed query rows | clicks -23.5%, impressions -42.7% (Google withholds the long tail) |
| Summed page rows | clicks +2.6%, impressions +27.7% (one impression, several pages) |
| Summed **device** rows, and `date` + `device` rows | exact |

So a share computed inside query rows cannot be applied to the property total.
Use **`date` + `device`** whenever a breakdown has to add up. Note the pairing:
`date` rows reconcile arithmetically, but a single-dimension `date` pull cannot
be trusted to return every day in the first place (see the defect above), which
is why the second dimension is not optional.

### Brand classification

```text
/\b(riv|rev[ei]r)/i
```
Matches the first syllable, so it catches tail typos (`riversdie`) and
first-vowel typos (`reverside`, the largest single typo). A `riverside`
substring catches neither; a `river` substring misses `reverside`.

**Non-brand = property total minus brand.** Never sum non-brand from query rows,
which under-reports it by more than half (15.1% against a true 35.0%).

The rule is Latin-only, so brand queries in Cyrillic, Japanese, Arabic and
Ukrainian land in non-brand: about 52 queries and 68 clicks, 1.3% of non-brand.
Flag them in movers lists rather than pretending the rule is complete.

### Segments

`pagepath` (not `page`) merges protocol, `www` and query-param variants. The
`/blog` segment **excludes** `/de/blog/*`, which would otherwise double-count 45
pages; German blog pages are counted once, under `/de`. `sc-domain:riverside.com`
spans ~178 hosts including support, careers and ~170 customer podcast
microsites, so the `/` row is not only the marketing homepage.

---

## Not pulled weekly

Ahrefs Rank Tracker, the Blog Reporting sheet, and the SERP Domination taxonomy.
None of them move meaningfully in a week, and the sheet parsing is the monthly's
most fragile step. Route those questions to `/organic-dashboard`.
