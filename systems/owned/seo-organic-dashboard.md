<!-- last-reviewed: 2026-07-22 -->
# SEO Organic Analytics Dashboard

> A self-contained, Riverside-branded 7-page artifact that blends four data sources - Snowflake organic funnel, Ahrefs rankings, Google Search Console (via Windsor.ai), and the Blog Reporting content log - into one live snapshot for the SEO team. Generated and refreshed by the [`/organic-dashboard`](../../.claude/skills/organic-dashboard/SKILL.md) skill. Replaces the originally-planned n8n → Google Sheets → Looker Studio stack.

## Purpose

The SEO team needs one place to see organic search performance tied to **business outcomes**, not just traffic. Ahrefs shows rankings, GSC shows clicks, Snowflake shows the funnel - but nobody had them in a single, branded, self-refreshing view that answers "is organic growing the business, and where?"

This dashboard consolidates all four into a monthly retrospective the team reads: funnel by channel and content group, top URLs by traffic (with revenue shown alongside), SERP rankings and AI-Overview exposure, Search Console brand/non-brand trends, content activity, and a cross-source per-URL blend - with MoM and QoQ comparison and a validated insight narrative on each page.

## Scope

Organic search only (`channel_group IN ('organic search non brand','organic search brand','organic llm')`). It is a **retrospective the SEO team consumes**, not a self-serve BI tool. Ad-hoc "slice any dimension" exploration stays in Rivermind / Omni; this artifact is a designed, pre-aggregated snapshot.

## Architecture

```text
   Snowflake            Ahrefs RT           Windsor.ai (GSC)      Blog Reporting sheet
 marketing_rollover    project 8580037    sc-domain:riverside.com   (content log)
        |                    |                     |                       |
        +--------------------+----------+----------+-----------------------+
                                        |
                          marketing-brain agent (the skill)
                    pull live -> canonicalize -> gate freshness ->
                    compute MoM/QoQ -> validate vs baseline
                                        |
                                        v
                       self-contained HTML artifact (data embedded)
                       published in place to ONE stable claude.ai URL
                                        |
                                        v
                          SEO team (private shared link)
```

There is **no database and no intermediate store**. The aggregated snapshot is embedded directly in the artifact. This is the deliberate replacement for the original plan's 8-tab Google Sheet hub.

## Operating model

| Dimension | Decision | Why |
|---|---|---|
| **Delivery** | Published claude.ai Artifact, private, shared to the SEO team | Team confirmed they have claude.ai access; one stable bookmarkable link |
| **Storage** | Artifact-only; source systems are the record | The artifact is *derived*; a lost artifact is rebuilt by one run. No governance burden of a second data copy. History via claude.ai version picker. |
| **Refresh** | On-demand today; a monthly scheduled refresh can be enabled separately (not yet active) | It's a monthly retrospective; the local scheduler (runs when the app is open) is suitable once enabled |
| **Analysis** | Hybrid: deep pages validated on `marketing_rollover`; exploratory "why" via `/rivermind:ask` | Validated logic where it matters, without dragging the gated Rivermind pipeline through fixed aggregations |
| **Comparison** | MoM and QoQ on every comparison metric | Stakeholder requirement; the rollover table is purpose-built for fair QTD comparison |

## The stable artifact URL

```text
https://claude.ai/code/artifact/20356f9e-3ecd-44ec-8fe7-d754138a6585
```

Every refresh updates this URL **in place** (Artifact tool `url` parameter). Routine runs never mint a new link.

## Data sources

| Source | System | ID / scope | Freshness |
|---|---|---|---|
| Business funnel | Snowflake `analytics.bi.marketing_rollover` | organic channel groups; `new_subscription` → `first_mrr` | Daily dbt rebuild; typically through D-1 |
| Rankings | Ahrefs Rank Tracker | project `8580037`, desktop, 491 tracked keywords | 30-day comparison snapshots |
| Search Console | GSC via Windsor.ai `searchconsole` | `sc-domain:riverside.com` | ~D-2 (normal GSC lag) |
| Content log | Blog Reporting sheet | `1uMvbqQq6g7KZpJ11EjOTqNPgxXU5zRUrPKcUZjabg1A` | Manual; check `modifiedTime` |
| Keyword taxonomy | SERP Domination sheet | `1hJe6Wn9qFKBLlYivjP5Z7Xtv9E_rxO_du5wGVphKvt8` | Manual; 491 keywords w/ Topic, MSV, Priority |

## Safeguards (the rules that keep it accurate)

Full detail in the skill's [safeguards and gotchas](../../.claude/skills/organic-dashboard/knowledge/safeguards-and-gotchas.md). The load-bearing ones:

- **Homepage canonicalization:** real homepage is `clean_url_path = NULL`; `/homepage` is an A/B variant; both + `''` merge to `/` everywhere.
- **Never silently drop NULL/empty keys** - a `clean_url_path IS NOT NULL` filter once hid the homepage (the top page).
- **Brand/non-brand:** Snowflake `channel_group` for the funnel; `riverside` regex for GSC. **Windsor's `branded_vs_nonbranded` is unreliable** for this domain and must not be used.
- **Freshness gate + partial-period fairness** before every generate. For GSC via Windsor, **never pull the daily series by `date` alone**: the single-dimension rollup is defective and on 2026-09-10 returned no row for 02-04 Sep while merging 01-05 Sep into one row (exact to the click). Adding a second dimension (`date` + `device`) returns every day correctly over the identical range, and device rows reconcile exactly to the property total, so summing them is exact. Validate by rebuilding a previously published window and checking it reproduces. Not an outage and not missing data: the feed runs at its normal ~3-day lag. Detail: [`.claude/skills/weekly-seo-report/knowledge/data-dictionary.md`](../../.claude/skills/weekly-seo-report/knowledge/data-dictionary.md).
- **Blog sheet tab auto-detect + date-vs-name validation** (pending `gdrive` enumeration auth).

## Decision log

| Decision | Rationale |
|---|---|
| marketing-brain artifact **over n8n → Sheets → Looker** | Collapses three systems into one, removes the GSC-credential blocker (Windsor.ai), makes analysis AI-native, is fully reproducible and version-controlled. The original approach comparison lives in the source project's `SEO-Data-Integration-Approaches` doc. |
| GSC via **Windsor.ai**, not a provisioned GSC API credential | Windsor's `searchconsole` connector is already authorized for `sc-domain:riverside.com` - unblocked B3 (IT-provisioned GSC creds) entirely. |
| **Windsor is the only Search Console source.** Never Ahrefs | Ahrefs' GSC endpoints have returned nothing since 14 Aug 2026 while Google itself served every day, so they are not a usable route and an empty series from them says nothing about the property. Removed from `/gsc-freshness-check` on 2026-09-15. Windsor was verified the same day against a Search Console UI export for 1 Aug - 12 Sep 2026: all 43 days matched exactly, 274,139 clicks / 14,273,628 impressions on both sides. Ahrefs stays the source for Rank Tracker and backlinks. |
| **Artifact-only storage** (no Drive/Snowflake/repo snapshot) | Simplest; source systems are authoritative; the generator makes snapshots reproducible on demand. Owned history is an easy add-on later (the generator already produces the JSON). |
| Do **not** trust Windsor `branded_vs_nonbranded` | It matches the literal domain string, so brand-token queries ("riverside", 48K+ clicks) are mislabeled non-brand - would massively inflate non-brand. |
| n8n workflow JSONs (Snowflake/Ahrefs/GSC/orchestrator) **not used** | Superseded by this approach. The drafts remain out-of-repo; if a warehouse pipeline is ever wanted, they are the starting point (see migration path). |

## Migration path (if requirements change)

- **Owned data history:** add a persistence step to the generator that writes the aggregated JSON snapshot to a Drive folder or a Snowflake table. The generator already produces the JSON, so this is additive - no redesign.
- **True self-serve BI / always-on cloud cron:** move to the long-term Snowflake + Omni path (the original plan's "Approach 1"). Windsor.ai can pipe GSC/Ahrefs into the warehouse to feed Omni. This reintroduces a data-engineering dependency, so only pursue when DE capacity exists.
- **Real-time freshness:** the scheduled task runs when the app is open; for always-on refresh, a hosted cron would be needed and the connector-auth-in-headless question must be validated first.

## Pointers

- **Skill:** [`.claude/skills/organic-dashboard/SKILL.md`](../../.claude/skills/organic-dashboard/SKILL.md)
- **Weekly sibling:** [`.claude/skills/weekly-seo-report/SKILL.md`](../../.claude/skills/weekly-seo-report/SKILL.md) - the weekly conversion report: Snowflake funnel plus Search Console at 7-day grain, two tabs, its own stable URL. **Deliberately excludes Ahrefs and rank tracking**, which stay monthly. Shares this system's safeguards and adds a thin-base floor, multiple-of-7 windows with holiday checks, and the finding that `marketing_rollover` restates for at least a week after publication.
- **Onboarding (new SEO/MarOps person):** [`.claude/skills/organic-dashboard/ONBOARDING.md`](../../.claude/skills/organic-dashboard/ONBOARDING.md)
- **Snowflake table doc:** the `marketing_rollover` schema reference (source project Google Doc) - the funnel data model
- **Design reference:** the approved Looker-faithful HTML mockup + Figma file `Z8GNm2xqRLkOxiEtS3Rup1`
- **Validation baseline:** the Feb 2026 Organic Retrospective HTML (embedded ground-truth data)

## Related systems

- **Upstream:** Snowflake (dbt `marketing_rollover`), Ahrefs, Google Search Console, Blog Reporting sheet
- **Sister docs:** `systems/owned/marketing-website.md`, `systems/owned/omni-bi.md`, `systems/reference/rivermind.md`
- **Related skills:** `/seo-ai-search-agent`, `/page-cro`, `/rivermind:ask`, `/webflow-locale-publish-queue`
