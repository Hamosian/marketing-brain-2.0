---
name: organic-dashboard
description: Generate and refresh the Riverside Organic Analytics dashboard - a self-contained, Riverside-branded 7-page artifact that blends Snowflake organic funnel data, Ahrefs rankings, Google Search Console (via Windsor.ai), and the Blog Reporting content log into one live snapshot for the SEO team. Pulls every source live, canonicalizes URLs, gates on freshness, compares MoM and QoQ, and publishes/updates a single stable artifact URL. Trigger with "organic dashboard", "SEO dashboard", "refresh the organic analytics dashboard", "organic search retrospective", "run the organic dashboard", or "/organic-dashboard". Runs on demand; a monthly scheduled refresh can be enabled separately.
---

# Organic Analytics Dashboard

Generate the Riverside **Organic Analytics dashboard** for the SEO team: a single self-contained HTML artifact that consolidates four data sources into a 7-page branded retrospective. Every run pulls the sources live, embeds the aggregated results into the page, and **updates one stable artifact URL in place**.

This is a **read + generate** workflow. It never writes to Snowflake, Ahrefs, GSC, or the sheet. The only side effect is (re)publishing the artifact.

> **Architecture, decision log, and the source-of-truth model live in [`systems/owned/seo-organic-dashboard.md`](../../../systems/owned/seo-organic-dashboard.md).** Read it once before your first run. Deep concepts, exact queries, safeguards, and the self-serve onboarding guide live in this skill's `knowledge/` folder and `ONBOARDING.md`.

## The one thing that must not change

**The dashboard is published to a single stable artifact URL and updated *in place* every run** so the SEO team's bookmark never breaks:

```text
https://claude.ai/code/artifact/20356f9e-3ecd-44ec-8fe7-d754138a6585
```

When you republish, pass this as the Artifact tool's `url` parameter (and the same `favicon` 📈). Never mint a new URL for a routine refresh.

## Operating model (confirmed with the SEO/MarOps stakeholders)

| Dimension | Decision |
|---|---|
| **Delivery** | Published claude.ai Artifact, private, shared to the SEO team via the page's share menu |
| **Storage** | **Artifact-only.** The latest snapshot is embedded in the artifact; history is claude.ai's version picker. Source systems remain the record. The artifact is *derived*, not authoritative - a lost artifact is rebuilt by one run. |
| **Refresh** | **On-demand today** (`/organic-dashboard`). A monthly scheduled refresh can be enabled separately (not yet active). Default reporting month = most recently completed calendar month. |
| **Analysis** | Hybrid - Business Impact + Content deep reads are validated against `marketing_rollover` (the table under Rivermind's `RS Snowflake` model); simple scorecards are computed directly. Route a genuinely exploratory "why" question through `/rivermind:ask`; do not drag the gated Rivermind pipeline through pre-defined dashboard aggregations. |
| **Comparison** | Every comparison metric shows **MoM and QoQ**. Partial current period is labelled MTD/QTD and never compared as complete. |

## Data sources

| Source | System | Access | ID / scope |
|---|---|---|---|
| Business funnel | Snowflake `analytics.bi.marketing_rollover` | `sql_exec_tool` MCP (read) | `channel_group IN ('organic search non brand','organic search brand','organic llm')` |
| Rankings | Ahrefs Rank Tracker | Ahrefs MCP (`rank-tracker-overview`) | project `8580037`, desktop |
| Search Console | Google Search Console via **Windsor.ai** MCP | `searchconsole` connector | `sc-domain:riverside.com` |
| Content log | Blog Reporting sheet | Drive file MCP `read_file_content` | `1uMvbqQq6g7KZpJ11EjOTqNPgxXU5zRUrPKcUZjabg1A` |
| Keyword taxonomy | SERP Domination tracking sheet | Drive file MCP | `1hJe6Wn9qFKBLlYivjP5Z7Xtv9E_rxO_du5wGVphKvt8` (491 keywords: Keyword, Topic, MSV, Priority) |

Full field-level query/endpoint reference: [`knowledge/data-dictionary.md`](knowledge/data-dictionary.md).

## Non-negotiable safeguards (full detail in [`knowledge/safeguards-and-gotchas.md`](knowledge/safeguards-and-gotchas.md))

1. **Homepage canonicalization.** The real homepage has `clean_url_path = NULL`; `/homepage` is an **A/B-test variant**; both (plus `''`) always merge into `/`. Apply at Snowflake, GSC, and the blend. Never analyze them separately.
2. **Never silently drop NULL/empty dimension keys.** A `clean_url_path IS NOT NULL` filter once hid the entire homepage - the top page. Canonicalize NULLs, don't exclude them.
3. **Brand vs non-brand:** use Snowflake `channel_group` for the funnel; for GSC use a `riverside` query regex. **Do not trust Windsor's `branded_vs_nonbranded` field** - it flags brand-token queries like "riverside" as non-brand and wrecks the split.
4. **Freshness gate before generating.** Confirm Snowflake `MAX(date_day) >= today-2` and GSC latest `>= today-4`; stamp each source's "data through" date in the footer; abort/flag if a source is stale.
5. **Partial-period fairness.** The current month/quarter is marked partial and compared MTD/QTD, never as complete.
6. **Blog sheet tab validation.** Auto-detect tabs and validate each tab's dates against its name before use (blocked on `gdrive` write/enumeration auth - until then, use the readable tab and flag the rest).
7. **General path normalization** (trailing slash, `-copy`/draft suffixes, empty→`/`) with any *other* suspected variants surfaced for human confirmation, not silently merged.

## Steps

### Step 0 - Freshness gate
Run the freshness checks in `knowledge/data-dictionary.md` (Snowflake `MAX(date_day)`, GSC latest `date`). Record each source's "data through" date for the footer. If a source is materially stale, note it prominently and either proceed with a warning banner or stop, per the user's call.

### Step 1 - Pull the data (parallel where possible)
Run the queries/calls in `knowledge/data-dictionary.md`:
- **Snowflake:** monthly funnel by channel (9 months); funnel by content_group (reporting month + prior for MoM); quarterly funnel by channel (QoQ); top URLs (reporting month, **canonicalized**).
- **Ahrefs:** rank-tracker overview - #1 count (current + 30-day-prior), AI-Overview share, top ranking movers.
- **Windsor GSC:** monthly totals + brand-filtered totals (derive non-brand = total − brand); reporting-month top non-brand queries and top pages.
- **Blog Reporting sheet:** content activity by month (new vs refreshed), net-new pages.

Apply the safeguards during transformation (canonicalization, brand regex, partial-period flags).

### Step 2 - Validate
Cross-check one anchor month against the prior baseline (the Feb 2026 retrospective reconciled within ~1%). Confirm the homepage appears as the top page (if it's missing, the NULL-drop bug has returned). Confirm the Ahrefs #1 count and GSC brand/non-brand split look sane.

### Step 3 - Generate the artifact
Build the 7-page self-contained HTML (Executive Summary, Business Impact, Top URLs, SERP & Rankings, Search Console, Content Cohorts, Per-URL Performance). Embed the aggregated data as JSON; keep it a **snapshot** (no external calls - artifacts run under a strict CSP). Rebuild from this spec: the page→data map in [`knowledge/data-dictionary.md`](knowledge/data-dictionary.md), the styling tokens below, and the **last published artifact version (claude.ai version history) as the visual reference** - no data-laden template is committed to the repo (pointers, not copies). Structure: embedded data objects → one render fn per page (`pageExec`…`pagePerUrl`) → shared chart helpers (`lineChart`/`stackChart`/`hbars`/`gbars`) + `scEl`/`scEl2` scorecards + `card()` insights → tab/control shell. Dark Riverside theme: `--bg:#0F0F14`, `--accent:#7C5CFF`. System font stack only (no external fonts). Include the "Data through" freshness strip and the data-integrity footer.

Write the file to the session scratchpad. Before publishing, validate JS with `node --check` and (optionally) run the DOM-stub harness that exercises all 7 page renders.

### Step 4 - Publish / update in place
Call the Artifact tool with the scratchpad file path **and `url` set to the stable URL above** so it updates in place. Confirm the returned URL matches. Never publish without `url` for a routine refresh (that mints a new link).

### Step 5 - Report
Summarize what changed vs last run (headline metrics, notable movers), note each source's freshness, and flag any stale source or safeguard that tripped.

## Notes and conventions

- **Artifacts can't fetch live** - the agent pulls and embeds; "refresh" = regenerate. Do not attempt runtime data fetches in the page.
- If `gdrive`, `hubspot`, `monday-api`, or `slack` MCPs are unauthorized in a run, only the sheet auto-detect is affected; Snowflake, Ahrefs, and Windsor are the load-bearing sources and are independent connectors.
- Windsor.ai is a free plan but serves full historical range for GSC; watch for row/date caps and note them if hit.
- If something non-obvious changes (a renamed sheet tab, a new channel_group value, a Windsor field change, a new URL A/B variant), capture it via `/retro` back into this skill or `knowledge/safeguards-and-gotchas.md`.
- New to this? Read [`ONBOARDING.md`](ONBOARDING.md). Extending a page or metric? See [`knowledge/extending.md`](knowledge/extending.md).
