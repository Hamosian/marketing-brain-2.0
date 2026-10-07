# Data Model & Core Concepts

The concepts you need to read the dashboard correctly. Skim this before extending anything.

## The funnel (`analytics.bi.marketing_rollover`)

One wide dbt table; each row is one user reaching one funnel **metric** (stage). The stages this dashboard uses, top to bottom:

`first_visit → sign_up → trial → new_subscription` (+ `mql`, `sql`, `won_deal` for the B2B slice).

- **First visit** = a user's first tracked visit (first-touch). This is the true **acquisition** metric. It is *not* the same as a GSC click (GSC clicks include returning/known users - that's why GSC clicks ≫ first-visits on the homepage).
- **First MRR** (`first_mrr` on `new_subscription` rows) = the monthly recurring revenue at the moment of conversion. Summed, it's the revenue attributed to organic in the period. It is *not* run-rate MRR.
- Count `first_visit`/`sign_up`/etc. as `COUNT(CASE WHEN metric = '…')` - one table, filtered per stage.

## Organic channel groups

The `channel_group` dimension splits organic into three:

| channel_group | Meaning |
|---|---|
| `organic search non brand` | Non-branded organic search - the SEO growth surface; the volume story |
| `organic search brand` | Branded organic search - people searching "riverside…"; high intent, high conversion |
| `organic llm` | Arrivals from AI/LLM answers and referrals - small but growing |

Key insight baked into the dashboard: **brand converts far harder than non-brand.** Brand is ~27% of visits but ~65% of first-MRR. So a non-brand traffic collapse can coincide with stable revenue - read the two together, never traffic alone.

## MoM vs QoQ

- **MoM** = reporting month vs prior month (from the monthly funnel).
- **QoQ** = the reporting month's quarter vs the prior quarter (from the quarterly funnel). Completed quarters compare cleanly; the current quarter is partial → QTD, using the rollover table's `day_of_quarter` fields for a fair cut.
- Both are shown because monthly moves can be noisy; the quarter view confirms whether a monthly change is a real trend.

## SERP rankings & AI Overviews (Ahrefs)

- 491 tracked keywords (the SERP Domination sheet defines the set + Topic/Priority).
- **`best_position_kind`** tells you *how* the top position is held: `organic`, `ai_overview`, `snippet`, etc.
- The dominant current reality: **~93% of Riverside's #1 positions are held inside an AI Overview**, not classic organic. This is the AEO/GEO concept - visibility increasingly lives in the AI answer box. It's both an opportunity (you can win the answer) and a risk (AIO placements are volatile and often don't drive a click). This is why the SERP page leads with the #1 count *and* its AIO share.

## GSC clicks/impressions vs the funnel

- **Impressions** = times a Riverside result was shown. The leading indicator - it collapsed ~78% before clicks did.
- **Clicks** = clicks to the site (all users, brand + non-brand).
- These describe *search visibility*, upstream of and different from the Snowflake *acquisition* funnel. The Per-URL page deliberately shows both side by side (Snowflake first-visits vs GSC clicks) so the gap (returning demand) is visible.

## Content activity (Blog Reporting)

A change-log of content published/refreshed. The signal is **new vs refreshed** volume and topical clustering (e.g. a webinar-cluster refresh). It explains *what the team did*; the funnel/GSC pages show *whether it worked*.

## Why the numbers reconcile

The Snowflake pulls were validated against the Feb 2026 retrospective baseline within ~1%, and the Ahrefs/GSC pulls were validated live. When extending, keep that discipline: cross-check any new metric against a known figure before shipping it.
