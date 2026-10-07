# Onboarding - Organic Analytics Dashboard

For a new SEO or MarOps person. Read top-to-bottom and you can open, run, extend, and troubleshoot the dashboard yourself. ~15 minutes.

## 1. TL;DR

The Organic Analytics dashboard is a **single self-contained web page** the SEO team reads to see how organic search drives the business. It blends four sources - Snowflake (the funnel), Ahrefs (rankings), Google Search Console (clicks/impressions), and the Blog Reporting sheet (content log) - into 7 pages with month/quarter comparisons and a written insight on each.

- **Open it:** `https://claude.ai/code/artifact/20356f9e-3ecd-44ec-8fe7-d754138a6585` (private; ask to be added to the share).
- **Refresh it:** run `/organic-dashboard` in Claude Code. (On-demand is the supported path today; a monthly scheduled refresh can be enabled separately.)
- **It's a snapshot** - not real-time. The "Data through" strip at the top shows how fresh each source is; re-run to refresh.

## 2. The 7 pages

| Page | Answers |
|---|---|
| **Executive Summary** | Are organic visits/sign-ups/subs/MRR up or down (MoM + QoQ)? How healthy are rankings? |
| **Business Impact** | Which content groups drive traffic vs revenue? Where does organic money actually come from? |
| **Top URLs** | Which pages bring visits, sign-ups, and subscriptions? |
| **SERP & Rankings** | How many #1s do we hold, are we gaining or losing, and how much rides on AI Overviews? |
| **Search Console** | Brand vs non-brand clicks and impressions over time. |
| **Content Cohorts** | What content did we publish/refresh, and when? |
| **Per-URL Performance** | One row per URL: funnel + Search Console side by side. |

**Controls:** the **Reporting month** selector and **channel** filter (All / Non-brand / Brand / LLM) drive the Executive Summary and Business Impact pages. Other pages show a fixed reporting-month snapshot.

## 3. Core concepts (enough to read it right)

- **The funnel:** `first visit → sign-up → trial → new subscription`. *First visit* is first-touch acquisition; *first MRR* is revenue at conversion. (Full model: `knowledge/data-model.md`.)
- **Three organic channels:** non-brand (the SEO volume story), brand (high intent, high conversion), LLM (small, growing). **Brand converts far harder** - ~27% of visits but ~65% of MRR. Always read traffic and revenue together.
- **MoM vs QoQ:** monthly moves can be noisy; the quarter view confirms real trends.
- **AI Overviews:** ~93% of our #1 rankings sit *inside an AI Overview*, not classic organic. Great visibility, but volatile and often click-light - a structural risk. This is the AEO/GEO shift.

## 4. Where the data comes from (and what's authoritative)

Four live sources: Snowflake `marketing_rollover`, Ahrefs project 8580037, GSC via Windsor.ai (`sc-domain:riverside.com`), and the Blog Reporting sheet. **The source systems are the source of truth.** The dashboard is a *derived* snapshot - if the artifact were ever lost, one run rebuilds it. Nothing important lives only in the artifact.

## 5. How to refresh it

- **On-demand (supported today):** in Claude Code, run `/organic-dashboard`. It pulls every source, rebuilds the page, and updates the **same URL in place** (bookmark stays valid).
- **Scheduled (optional, when enabled):** a monthly task can be set up to run it automatically (it fires when the Claude app is open on/after the 1st - suitable for a monthly retrospective). Not active yet.
- **"Data through" strip:** shows each source's latest date. Snowflake is usually yesterday; GSC lags ~2 days. If a date looks old, the source may be stale - see troubleshooting.

## 6. Gotchas that will bite you

- **Homepage = `/` + `/homepage` combined.** The real homepage's path is NULL in Snowflake; `/homepage` is an A/B variant. They're always merged. If Top URLs ever shows a tiny "homepage" instead of the real one at #1, a NULL-drop bug is back.
- **Don't trust Windsor's brand flag.** It calls "riverside" *non-brand*. We classify brand with a `riverside` regex instead.
- **The current month/quarter is partial** - it's labelled and compared fairly (MTD/QTD), never as a complete period.
- **The page can't fetch live data** - it's a sealed snapshot. Freshness comes from re-running.

## 7. How to extend it

Common changes (add a page, a metric, a source, swap the keyword list) are documented step-by-step in `knowledge/extending.md`. The generator is one HTML file: data objects → per-page render functions → chart helpers → shell. Always re-pull from source (don't hand-edit numbers), run the syntax + render checks, and publish with the `url` parameter.

## 8. Troubleshooting

| Symptom | Check |
|---|---|
| A source shows an old "data through" date | Snowflake: `MAX(date_day)`. GSC: is Windsor's `searchconsole` still connected? Blog sheet: `modifiedTime`. |
| Content Cohorts looks thin / wrong months | Blog sheet tab enumeration needs `gdrive` auth; the run uses the readable tab and flags the rest. Authorize `gdrive` for full auto-detect. |
| Numbers look wrong | Reconcile one metric against the Feb 2026 retrospective baseline (should match ~1%). |
| Homepage missing from Top URLs | The `IS NOT NULL` NULL-drop regression - see `knowledge/safeguards-and-gotchas.md` #2. |
| A connector is unauthorized | Snowflake/Ahrefs/Windsor are load-bearing; `gdrive`/`slack`/etc. only affect the content-tab auto-detect. Re-auth via claude.ai connector settings. |

## 9. Glossary & why it's built this way

- **First visit / first MRR / channel_group / AI Overview / MoM / QoQ** - defined in `knowledge/data-model.md`.
- **Why marketing-brain (an artifact) instead of n8n → Sheets → Looker, and why artifact-only storage** - the decision log in [`systems/owned/seo-organic-dashboard.md`](../../../systems/owned/seo-organic-dashboard.md).

Questions or something drifted? Run `/retro` to capture the fix back into these docs so the next person inherits it.
