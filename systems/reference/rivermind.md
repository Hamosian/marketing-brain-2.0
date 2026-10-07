<!-- last-reviewed: 2026-08-23 -->
# Rivermind

> Self-serve data Q&A plugin built and maintained by Riverside's analytics team. Lets non-analyst teams (marketing, PM, ops, support) answer analytical questions against Snowflake, validated and grounded in the analytics team's curated business context.

## Overview

Rivermind is a Claude Code / Cowork plugin that turns a question into a validated, sourced answer (and optionally a chart, narrative, or slide deck). It runs descriptive and product analytics: funnels, segmentation, drivers, root cause, trends, metric definition, data-quality checks, storytelling, and experiment design.

We are a **consumer**. The analytics team owns the plugin, its skills, and the bundled business context (the `rivermind-plugin` workspace, synced via `analytics-context-manager`). We do not produce or maintain that knowledge. If a number looks wrong or a definition is stale, surface it and route it back to the analytics team out of band (Slack, ticket). The plugin refreshes on the next plugin update.

The `rivermind:*` skills are already installed in this workspace, so the team can use them today.

## How Claude Works With This

| Action | How |
|--------|-----|
| Get access | Ask the Data team. Rivermind needs Snowflake access, and the Data team grants both (Jonathan Galili, 2026-09-23; `references/other_teams.md` → Access provisioning) |
| Ask a data question | `/rivermind:ask {question}` (the mandatory entry point for any analytical question) |
| Check whether the question was already answered | Query the Notion Analyses DB first - see [Analysis Archive](#analysis-archive-notion-analyses-db) below |
| Investigate / build | Rivermind runs SQL against Snowflake via the `sql_exec_tool` MCP and reads its bundled business context |
| Make changes to the plugin | We don't. Escalate to the analytics team (`rivermind-plugin` workspace) |
| Report a context or methodology error | Tell the user, ask them to raise it with the analytics team. Never edit the plugin's `.knowledge/context/` files |

## What the Team Owns

- Nothing in the plugin itself. We consume it.
- Our own questions, scope definitions, and how we act on the answers.

## What the Team Does NOT Own

- The plugin code, its skills, helper scripts, themes, and templates.
- The bundled business context at `${CLAUDE_PLUGIN_ROOT}/.knowledge/context/` (per-domain folders: product, marketing, finance, sales, support, segment-events, experiments, feature-store, shared-models). Read-only, overwritten on sync.
- The Tier 1 metric definitions and the analysis archive (Notion, analytics-team-owned). We read the archive, we don't curate it - see [Analysis Archive](#analysis-archive-notion-analyses-db).

## Entry Points

All skills are namespaced under `rivermind:`. The ones a consumer reaches for most:

| Command | Use it for |
|---------|-----------|
| `/rivermind:ask` | Primary entry point. Any data question. Handles session init, scope clarification, complexity classification (L1 to L5), and routing |
| `/rivermind:run-pipeline` | End-to-end: business question to validated slide deck (20-step pipeline) |
| `/rivermind:resume-pipeline` | Pick up a long analysis where you left off |
| `/rivermind:explore` | Quick table preview and pattern spotting |
| `/rivermind:export` | Export a result set or deliverable |

Supporting skills the pipeline pulls in automatically (you rarely call these directly): `question-framing`, `question-router`, `data-quality-check`, `segment`, `triangulation`, `semantic-validation`, `guardrails`, `metric-spec`, `metrics`, `add-metric`, `capture-analysis`, `close-the-loop`, `visualization-patterns`, `presentation-themes`, `events-catalog`, `tracking-gaps`, `query-kb`, `knowledge-bootstrap`. Release Radar (`release-radar` plus the `monitor-*` skills) handles scheduled release-metric monitoring.

## Data Sources

| Source | How | Notes |
|--------|-----|-------|
| Snowflake | Live, via `sql_exec_tool` MCP | No local fallback. If Snowflake is unreachable, Rivermind pauses, it does not guess |
| Business context | Static, bundled with the plugin | Curated by the analytics team, synced from `analytics-context-manager`. Read-only |

## Analysis Archive (Notion Analyses DB)

Every Rivermind/analytics analysis lands as one row in the Notion **Analyses DB** (154 rows Apr-Aug 2026, growing weekly): Question, TL;DR with headline numbers, Tables Used, Tags (Funnel/Trend/Root Cause/...), Department, Status, Run Date. It is the fastest way to (a) find whether a question is already answered, (b) learn which Snowflake tables answer a class of question, and (c) pull prior methodology before re-deriving it.

- **Database:** <https://app.notion.com/p/920ae01a303541e599671692509e2f1f> (parent page "Analyses" under "Data")
- **Data source for SQL queries:** `collection://7f51e78e-12ef-4a8f-a123-a76c6cb1d494` via the Notion MCP `query-data-sources` tool, e.g. `SELECT "Analysis ID", "Analysis", "TL;DR", "Tables Used" FROM "collection://7f51e78e-12ef-4a8f-a123-a76c6cb1d494" WHERE "Question" LIKE '%webinar%' OR "TL;DR" LIKE '%webinar%'`
- **Owner:** analytics team. Read-only for us. Gaps or errors go to them out of band, same as the rest of Rivermind.

### How to use it before asking Rivermind

1. **Search the archive first** (title, Question, TL;DR, Tables Used). A prior row often answers the question outright or names the exact tables and filters, cutting a fresh `/rivermind:ask` from L4 to L1.
2. **Take the latest run on a topic.** Recurring questions get re-run with corrections; later rows supersede earlier ones and say so in the TL;DR (e.g. #160's forecast correction supersedes #157/#159; the Light Business cannibalization series runs v1→v5). Never quote an early version of a series without checking for a later one.
3. **Cite Analysis ID + Run Date** when reusing a figure - archive TL;DRs are point-in-time, and evidence standards require source + as-of date.

### Data gotchas the archive documents (pointers, not our findings)

Recurring traps that change how you read marketing/growth numbers. Each is documented in the named analysis row - read it before relying on the affected table.

| Gotcha | Archive row |
|---|---|
| `analytics.ba.webinar_user_daily_activity` stopped ingesting webinar performance data ~Apr 2026; webinar adoption undercounts and the gap widens monthly. Use `analytics.bi.webinar_registration` until fixed | #146 (Jul 2026) |
| `analytics.fs.takes` needs `is_deleted = FALSE`; without it avg duration collapses ~3x and take counts inflate ~4x | #96 (Jun 2026) |
| New SS webinar subscription counts: do **not** add `is_trial_row = FALSE` on `ba.webinar_user_daily_activity` (that filter produced a 5x undercount); corrected counts reconcile to Omni "Total Webinar Accounts Self Service" | #25/#89 (Jun 2026) |
| Trial-based MRR forecasts: size cohorts by trial **end/conversion** date (`bi.onboarding_funnel_web`), not trial start date - start-date sizing overstated an August forecast 2x | #160 (Jul 2026) |
| `analytics.bi.plg_funnel` daily grain reconciles to finance to the dollar; the monthly snapshot overstates expansion ~2x | #142 (Jul 2026) |
| Total MRR = `SUM(mrr)` over all rows of `bi.daily_customer_mrr`, not an `account_customer_group_mrr` filter | #47 (Apr 2026) |
| An SQL only fires when the intro meeting is **held**, so QTD SQL comparisons are depressed by booked-not-yet-held meetings - a timing artifact, not a funnel break | #171 (Aug 2026) |
| The Nov 2025 webinar-campaign signup spike was a Google PMax attribution artifact | #148 (Jul 2026) |
| Funnel steps marked "no event" may still be trackable: `page()` calls live in `SEGMENT_EVENTS.WEB.PAGES` and are missing from the track-event catalog; Android has no async-guest deep-link instrumentation at all | #140 (Jul 2026) |

## Rules That Affect Us as Consumers

- **Route data questions through `/rivermind:ask`.** It will not answer analytical questions outside that entry point.
- **Scope clarification is a hard gate.** Before any query, Rivermind asks for time period, user population, and key definitions if any are missing. It will not assume defaults, so have these ready to move fast.
- **Outputs land in `~/.rivermind/`, not the current project.** Final deliverables go to `~/.rivermind/outputs/`, working files to `~/.rivermind/working/`. Rivermind reports the absolute path. Override with `RIVERMIND_OUTPUTS_DIR` / `RIVERMIND_WORK_DIR` if you want outputs in your project folder.
- **It validates before it concludes.** Expect a confidence badge and "the data suggests" framing unless validation is airtight.

## What It Does NOT Do

- Predictive modeling or regression
- Dashboard building
- Infrastructure, deployment, or system design

For those, use the relevant owned system or escalate.

## Related Systems

- **Upstream:** Snowflake (live query layer), the analytics team's curated business context and Tier 1 metric store.
- **Adjacent:** [Omni BI](../owned/omni-bi.md) is our own BI surface. Rivermind is the analytics team's Snowflake-backed Q&A and storytelling layer. Use Rivermind for ad hoc analytical questions and decks; use Omni for our maintained dashboards and models.
- **Downstream:** Marketing, PM, ops, and support teams who consume answers, charts, and decks.

## Pointers

- **Investment:** Reference only. We consume, we don't contribute.
- **Owner:** Analytics team (`rivermind-plugin` workspace, synced via `analytics-context-manager`).
- **Escalation for context / methodology errors:** raise with the analytics team out of band; do not log corrections locally.
- **Full plugin extraction (source of truth, not duplicated here):** `~/Downloads/rivermind-complete.md` and the installed `rivermind:*` plugin skills.
