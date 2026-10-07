<!-- last-reviewed: 2026-06-17 -->
# Marketing Operating Model

> How Riverside Growth actually runs in 2026: the analytics-partnered, AI-automated acquisition engine. This maps the operating rhythm, the measurement stack, the marketing data model, the live strategic bets, and who owns what. Most of the load-bearing infrastructure (metrics handbook, automated reports, the OO data model, the Analytics Hub) is built and owned by the analytics/data team and lives in their Notion workspace. We consume and co-operate it; we do not maintain it.

## Overview

Marketing operates as a data-led funnel team tightly coupled to the analytics org. Top-of-funnel is healthy (right intent, right channels); the standing challenge through H1 2026 is an end-to-end conversion problem and a shift from earned (organic) to rented (paid) new revenue after the riverside.fm to riverside.com domain migration.

The operating model has four layers:
1. **Operating rhythm** - recurring automated reports (daily, weekly) plus a monthly acquisition review.
2. **Measurement stack** - the Business Metrics Handbook (single source of truth), named dashboards, and the attribution model.
3. **Marketing data model** - an object-oriented remodel of the marketing funnel ("Marketing Objects"), parallel to the sales-side Lead/Deal model.
4. **Strategic bets** - the new 2026 growth motions (PQL in-product, mobile, non-podcast video, webinar).

This doc is a router and a set of pointers. The live numbers live in Notion and the dashboards; do not copy them here (they go stale). When a finding looks wrong or stale, route it back to the analytics team out of band, the same rule as [Rivermind](rivermind.md).

## How Claude Works With This

| Action | How |
|--------|-----|
| Answer a data/funnel question | `/rivermind:ask` (analytics team's validated Q&A); see [Rivermind](rivermind.md) |
| Pull a specific 2026 analysis | Fetch the Notion page from the Pointers table via the Notion connector |
| Understand a metric definition | Business Metrics & Definitions Handbook (Notion); Section 7 is Marketing |
| Investigate an acquisition anomaly | `measurement-agent` plus `paid-acquisition-agent`; cross-reference the weekly digest and campaign calendar |
| Touch reporting automations | Don't edit directly. These are analytics-team n8n workflows and Claude routines. Escalate to the owner (Yaniv) |
| Report a methodology/number error | Surface to the user, route to the analytics team. Never edit their `.knowledge/` or Notion specs |

## Operating Rhythm

| Report | Cadence | Contents | Automation | Consumer / Owner |
|--------|---------|----------|------------|------------------|
| Daily Self-Serve Funnel Report | Daily, 10:00 Israel time | Interactive HTML: signup-anchored, trial-end-anchored, and a Signup to Trial / Trial-End to Paid CVR matrix (1-7d and 1-14d windows). Three views: Full, period-to-date, mature-only | n8n workflow (4 parallel Snowflake queries to HTML render) publishing to the Analytics Hub at a stable URL plus a Slack DM. Error handler DMs owner; a failed day is skipped, no retry | Primary consumer: CRO. Owner: Yaniv Barel |
| Marketing Weekly Acquisition Digest | Weekly, Tuesday 10am, 13-week trailing window | Three tiers: Tier 0 deterministic snapshot (visits to signups to activated to trial to paid, WoW / vs 4w avg / vs same week LY, anomaly flags), Tier 1 light LLM interpretation, Tier 2 on-demand Claude root-cause investigation triggered from Slack | Tier 0/1 in n8n (numbers must be identical week over week); Tier 2 is an engineering-owned Claude routine in git. Posts to `#marketing-weekly` | Marketing team. Owner: Yaniv / MarkOps |
| Marketing Performance Review | Monthly (acquisition only) | 5-week matured-window review; every finding tagged by marketing-controllability (controllable / partial / context-only); per-channel efficiency, not forced cross-channel ratios. Deliverable chain: Notion notebook to storyboard to narrative to slide deck | Manual analysis (Rivermind-assisted) | Marketing team and partner stakeholders. Owner: Shir Sarusi; scoped by Eyal |

Operating principles baked into the reviews:
- Use a matured cohort window (the funnel takes about 21 days end to end) so no projections are needed.
- Lead with efficiency; treat volume as context (it tracks budget, not performance).
- A structural confound to remember: the direct-purchase option was removed, so all customers now route through trial. This reshuffles mid-funnel buckets, so **end-to-end Signup to Web Paid is the only robust period-over-period comparator**.
- The review reads acquisition through two lenses: declared **intent** (onboarding answers) and observed **usage** (a Layer 1 first-24h activity prism, plus a Layer 2 content-genre prism from `user_sessions_content_analysis`). A standing finding: the funnel does not have a top-of-funnel problem (right intent, right channels); the break is downstream conversion. Watch the large NULL/skipped-intent bucket, which converts near 1%.

## Measurement Stack

**Business Metrics & Definitions Handbook (Notion, analytics-owned).** Single source of truth, 11 sections, each metric tied to a specific Snowflake table and Omni measure. Section 7 is Marketing. North stars: ARR and Weekly Active Accounts. Marketing's branch of the metric tree is signups x CVR, plus CAC, plus reactivation.

Key durable definitions worth knowing:
- **Funnel shape:** Visit to Signup (24h) to 14-day free trial (about 2 days) to Subscription created (15d) to Paid customer (1d). Activation/aha can occur during free signup or trial.
- **Signup to Trial is about 11%** and that is expected, not a problem (free-tier exploration precedes trial). LEARN-003: roughly 89% of signups never start a trial.
- **Trial to Subscription** uses a 15-day window (7-day trial plus late auto-converts). Always state the conversion window; never default silently.
- **Day 14 trial cliff:** a majority of non-converters cancel on the final trial day, which makes that cohort more recoverable via pre-cliff nurture.
- **CAC** denominator is paying customers, not signups. Target LTV/CAC > 3x. Variants: blended, paid, B2B, self-service.
- **Channel taxonomy in the handbook is coarse** (Google Ads, Meta, Other Paid, Organic Search, Direct, Referral, Social Organic, Email, Affiliate). The performance reviews use a finer brand vs non-brand split. These two taxonomies are not yet reconciled.

**Named dashboards:** PLG Funnel 2026 Performance, MQL-to-SQL, Webinar Dashboard, Reactivation Analysis. (Owned in Omni / Preset; see [Omni BI](../owned/omni-bi.md).)

**Attribution model.** Pre-signup, visit-date-anchored, 7-day lookback. For each signup, look at the 7 days before `sign_up_at` and attribute campaigns reached via ad-driven visits. A user can attribute to multiple campaigns, once per campaign. `report_date` is the first day in the window that the campaign's ad appears for that user. All UTM standardization lives in a single dbt macro (`get_utm_standardization`), validated against an analytics-maintained expected source/medium list. Known caveat: missing first visits (incognito/cookie blockers) create synthetic `is_fake_visit` rows. See also the [Marketing Ops Automation](../owned/marketing-ops-automation.md) failure mode where product events overwrite Contact Last Touch Source.

Two attribution windows coexist, do not conflate them. The daily campaign report uses the 7-day visit-anchored lookback above. The metrics handbook's separate campaign-signup attribution (`bi.daily_campaign_signup_attribution`) assigns each user to the first campaign exposed within a 30-day pre-signup window, and there too `report_date` is the first-exposure date, not the signup date. Reconciling the two is on the gap list.

**Two scoring models, do not conflate them.** (1) The self-serve lead score (0 to 100 composite, HubSpot calculated properties) scores individual PLG signups for ad-platform signal and lifecycle nurture; this is ours, see [Self-Serve Lead Scoring](../owned/self-serve-lead-scoring.md). (2) PQL 2.0 is analytics-owned and account-level: a usage score (percentile-ranked feature usage over a rolling 4-week window, segment-normalized against same-size peers) and a job-title score (embedding similarity to titles that historically converted to BD), each 0 to 1, computed nightly in Snowflake (`MACHINE_LEARNING.PQL.PQL_2O_OUTPUT`) and synced to HubSpot company properties (`pql_score`, `pql_job_title_score`) via Hightouch. It powers the outbound BD motion today and the proposed in-product motion (see bets). Gotcha: the Notion model doc still states a 0.9 / 0.9 qualification threshold, but production runs 0.6 / 0.6. Trust the live config, not the doc.

## Marketing Data Model (Marketing Objects)

An object-oriented remodel of the marketing funnel into entities, the marketing-side parallel of the sales Lead/Deal model. Built in the analytics dbt repo under an `ent` schema; v5 spec dated 2026-05-18; v1 entities target Q3 2026.

- **Self_serve_lead** is the central new entity: one row per first-visit funnel journey, backed by `marketing_funnel_analysis`, with states anchored to `plg_funnel.funnel_stage` (traffic to signed_up to freemium/trial to subscribed/churned to reactivated). Carries first-touch and last-touch acquisition, geo/device, onboarding intent, early activity, ML predictions, and cross-funnel FKs to sales (`mql_id`, `sql_id`, `deal_id`).
- Supporting entities: User, Account, Account_Customer_Group (the financial-grain entity for active self-service; current count lives in the OO spec and dashboards), Subscription, Trial. Visitor is designed but deferred to v2.
- **Why it matters for us:** it lets AI and analysts reason about marketing leads the way they reason about sales leads, with full campaign-touchpoint history, multi-touch attribution, and one-table cross-funnel queries (self-serve leads that also went sales-led).
- Encodes tribal knowledge as `LEARN-###` / `CORR-###` references (e.g. LEARN-003 trial rate, LEARN-026 web/mobile channel split, CORR-019 always specify CVR windows).

Related: a "Product usage visibility for marketing" dashboard initiative gives marketing post-signup behavioral visibility segmented by marketing dimensions (campaign, ad, channel, landing page), closing the loop between spend and real activation (sources: `daily_users_product_activity`, the User Content Insights model).

## 2026 Strategic Bets

| Bet | Goal | Status | Owner | Pointer |
|-----|------|--------|-------|---------|
| Marketing PQL / in-product motion | Add product-native CTAs on top of the outbound PQL motion, routing qualified in-product users to a self-booked AE meeting via ChiliPiper (a high-multiple ARR upgrade motion). Attributed marketing inbound last-touch. Runs on the analytics-owned PQL 2.0 model (live threshold 0.6 / 0.6; see Measurement Stack) | Draft for alignment; plans a company-level 50/50 holdout test (cohorts A/B, 4 to 6 weeks or N=500 per arm, primary metric incremental meetings booked). Biggest risk: lower SQL conversion than the BD baseline, so RevOps must pre-agree an AE capacity ceiling and a minimum SQL-conversion floor with kill criteria | Yaniv | Marketing PQL Planning |
| Mobile as a growth pillar | Three phases: best desktop companion ("mobile as camera, web as studio"), then mobile-first creation, then AI content expansion. Probing mobile as a low-friction feeder for desktop acquisition | Active; a time-boxed Google Search learning test (mobile/iOS/US, multi-campaign). Mobile is a small share of ARR today (current figure in the campaign docs). Android is open (competitors are iOS-only) but not yet executed | Marketing | Mobile Marketing Campaigns V1/V2 |
| Non-podcast "talking video" | Test a positioning move from "podcasting" toward "talking video / conversations" for social-first creators | Research stage. Highest product-intent is caption/subtitle tooling keywords | Marketing | Search Volume Research: Non-Podcast Talking Video |
| Webinar (AI-differentiated) | Map the 8-stage webinar lifecycle; bet on Repurpose (defensible via broadcast-grade input quality), Live (biggest white space), and Registration/Attendance intelligence | Working doc / roadmap | Product + Marketing | Webinar Innovation Working Doc |

Two recurring analytical themes that drive marketing decisions:
- **The burn finding.** Organic search signups and new MRR fell (domain migration plus a Google core update) while paid backfilled the gap, holding total new MRR roughly flat but dragging blended marketing efficiency down. Revenue is being rented (paid) rather than earned (organic). A per-channel CAC/LTV analysis to quantify this does not exist yet (the project is a scaffold).
- **Discount structure beats discount depth.** Repeating-Nmonth coupons convert far better than one-time coupons at the same percentage; 20% is the sweet spot; "forever" coupons are structurally broken; yearly-plan attach is the durability lever. The discount program is net positive overall (promo redeemers convert above benchmark, roughly 62% vs 57% trial-to-paid), but the lift concentrates in partner and branded codes; several creator/influencer codes (for example AIMASTER, ThinkMedia, Collin) convert below the organic baseline, and most codes are dormant (about 128 of 193 had zero redemptions in the window). Discounts lift conversion, not spending power: average first MRR is roughly flat across coupon types. One unambiguous fix flagged: move AIMASTER off a "forever" structure to a repeating one.
- **First-payment success is its own funnel stage and a real CVR lever.** A 2026 root-cause of a web Trial-to-Paid CVR dip traced roughly half to rising US issuer-side card declines (a billing / Stripe Radar config lever, not user intent) and half to seasonal cohort reversion. Two durable takeaways: failed first payments are invisible in the MRR tables, so watch them as a separate stage; and re-baseline CVR targets to the November level, not the unusually strong January peak.

## Tooling

Snowflake (warehouse), n8n at `riverside.app.n8n.cloud` (deterministic ETL and reporting), Claude routines (deep RCA), Preset and [Omni BI](../owned/omni-bi.md) (BI surfaces), [HubSpot](../owned/hubspot.md), Hightouch (reverse ETL to HubSpot), ChiliPiper (AE booking), Mixpanel, RevenueCat (mobile), Google Ads, Slack. The split the analytics org enforces: n8n for anything that must be reproducible, Claude for reasoning. n8n is MarkOps-editable config; Claude routines are engineering-owned code in git.

## Ownership

| Layer | Owner | We |
|-------|-------|----|
| Operating cadence, campaign calendar, the strategic bets | Marketing (Growth) | Own |
| Performance reviews and acquisition narratives | Marketing analyst (Shir), scoped by Eyal | Own / co-produce |
| Metrics handbook, OO data model, attribution macro, daily/weekly automations, Analytics Hub | Analytics/data team (Yaniv Barel et al.) | Consume; escalate errors out of band |
| Rivermind plugin and bundled business context | Analytics team | Consume; see [Rivermind](rivermind.md) |

## Key People

| Person | Role in the operating model |
|--------|------------------------------|
| Yaniv Barel | Analytics/automation lead for marketing data; owns the PQL motion, the daily report, the OO modeling spec, the discount and trial-CVR work. Slack `U05CP58NCPL`, `yaniv@riverside.com` |
| Shir Sarusi | Marketing performance reviews; the (in-progress) CAC/LTV-by-channel project |
| Eyal | Scopes the monthly acquisition reviews |
| Abel, Sivan | Trial to subscription CVR analysis and web-decline RCA |
| Tal Florentin | Coupon vs regular CVR analysis |
| Jonathan Keyson | Organic vs paid revenue / burn validation |
| Nir Taranto, Savion | Attribution spec and UTM standardization |
| Ruben | Growth initiatives, Shared Context and Skills initiative |

## Related Systems

- **Upstream:** [HubSpot](../owned/hubspot.md), [Paid Acquisition](../owned/paid-acquisition.md), [Marketing Website](../owned/marketing-website.md), [Self-Serve Lead Scoring](../owned/self-serve-lead-scoring.md), [Marketing Ops Automation](../owned/marketing-ops-automation.md).
- **Adjacent:** [Rivermind](rivermind.md) (the analytics team's Snowflake-backed Q&A and the Analytics Hub that hosts the daily report), [Omni BI](../owned/omni-bi.md) (our maintained dashboards).
- **Downstream:** Sales (PQL/SQL handoff), Finance (burn, CAC, ARR).

## Pointers

Source Notion pages (analytics-team workspace; fetch via the Notion connector). Treat as living documents; the numbers move.

- Marketing PQL Planning - `37e97be2-38ae-8016-83c8-f0a210a66347`
- Marketing Performance Review (Mar-Apr 2026) - `34f97be2-38ae-8109-9c96-cf0781dd8b4b`
- Performance Report Part 1 / Hits & Misses Part 2 / Spec & Methodology / State of Acquisition - `34f97be2-38ae-81d1-9b6f-c84fb27a374f`, `34f97be2-38ae-812d-bfcb-c112e58f8b0a`, `34e97be2-38ae-81e1-b62e-d9396a4a32e0`, `35097be2-38ae-81c4-8fdb-d6aa1009729d`
- Business Metrics & Definitions Handbook (index) - `37597be2-38ae-81b7-bde8-cce5f27d26bd`; Section 7 Marketing - `37597be2-38ae-8130-a7c5-ea25780620ed`
- Marketing Funnel Automation / Weekly Acquisition Digest Spec - `37b97be2-38ae-808a-afc0-d59e40501f3d`, `37b97be2-38ae-8169-8efd-d5ce85f3694e`
- Daily Campaign Performance & Pre-Signup Attribution - `30197be2-38ae-80df-8550-e80135f34e0e`
- Marketing OO Modeling Spec v5 - `36397be2-38ae-8160-bca0-df9dbaefbb2d`
- Mobile Marketing Campaigns V1 / V2 - `2fd97be2-38ae-81a1-87db-ce994910d1ea`, `32797be2-38ae-80d8-a5d9-f50ff639e330`
- Webinar Innovation Working Doc - `35197be2-38ae-8142-bd1d-fdbb456130bf`
- Discount Analysis (summary + deep dive) - `38097be2-38ae-8106-ad45-ea40da5e439f`, `37f97be2-38ae-8060-9711-cdbbeacfeb47`
- Web Trial to Paid CVR Decline RCA - `38097be2-38ae-8110-b103-c20b94c11ce0`
- Organic vs Paid New Revenue / Burn Validation - `37a97be2-38ae-8169-8c44-dfe2f1ab31ff`
- PQL 2.0 in-house model (account-level scoring, usage + job-title) - `2bb97be2-38ae-80c5-b7f7-d09c63e0da4c`
- CAC/LTV by Acquisition Channel (Spec / Descriptive / Findings, scaffold) - `34e97be2-38ae-81eb-b4aa-e61a30f159fe`, `34e97be2-38ae-8199-8dae-cfa90ea3b405`, `34e97be2-38ae-81ff-bbf5-f7be73eb6fa6`
- Pro-Tier Coupon vs Regular Trial CVR (Mar-May 2026) - `37a97be2-38ae-81ee-bb82-cbc65aa4a345`
- Trial to Subscription CVR Analysis (spec, in progress) - `32497be2-38ae-8178-8b21-f0dea16a358f`
- Product usage visibility for marketing teams (dashboard spec) - `2f797be2-38ae-8088-9866-cc3e6b53bc1c`
- MQL-to-SQL Conversion Trend & Segment (Apr 2025-Apr 2026) - `36697be2-38ae-81aa-88ef-f56f65cdcb31`
- AE Efficiency & SQL Benchmarking (FY2025) - `37897be2-38ae-813e-90be-d5a597b4cd99`
- Shared Context & Skills Initiative - `36597be2-38ae-81f2-9c9e-da6d8d1c53e0`

**Knowledge gaps to fill:** per-channel CAC/LTV (project is still a scaffold; the actual numbers live in linked Google Sheets, not Notion); reconciliation of the handbook channel taxonomy with the brand/non-brand split used in reviews; reconciliation of the two attribution windows (7-day visit-anchored vs 30-day first-exposure); the trial-CVR driver analysis (still in descriptive phase); and no marketing calendar exists yet, which Tier 2 of the weekly digest depends on (the team has flagged this explicitly).
