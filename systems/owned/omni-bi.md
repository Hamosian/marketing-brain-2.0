<!-- last-reviewed: 2026-09-23 -->
# Omni BI

> Marketing dashboards and reporting layer. Source of truth for revenue, funnel, and channel performance.

## Overview

Omni BI is Riverside's business intelligence layer, sitting on top of Snowflake (`RS Snowflake` model). It is the source of truth for revenue (MRR), marketing funnel metrics, product usage, ad performance, and sales activity. Data comes from Stripe (billing), HubSpot (CRM), Segment/product events, and ad platforms.

**Omni instance:** `riverside.omniapp.co`
**Model:** `RS Snowflake` (ID: `48d89fd2-ce24-44e1-bfe5-f3e30334c6dc`) - the only model available.

## How Claude Works With This

| Action | How |
|--------|-----|
| Run a business question | `pickTopic` then `getData` with plain-English prompt |
| Pull raw SQL | `sql_exec_tool` (Snowflake direct) |
| Find metric definitions | `searchOmniDocs` (`docs_search` fails on a missing Snowflake grant, broken since 2026-08-26) |
| Build a campaign report | `anthropic-skills:riverside-campaign-report` |

**Always call `pickTopic` before `getData`** - never assume the topic ID. Topic IDs are stable but must be resolved per query type.

## Topics (Complete Map)

| Topic ID | What it contains | Key fields |
|----------|-----------------|------------|
| `Daily Customer MRR` | Per-customer MRR by day. Source of truth for revenue. | Pivot Day, Account ID, Product Name, Product Group, Product Type, Recurring Interval, Status, State, MRR, Delta MRR, Churned MRR, Last Touch Source, Country, Email Type, Churn Type, Acquisition Date, Monthly/Quarterly Targets |
| `MQLs to SQLs to Deals` | Full B2B funnel from form submit → Pre-Op → Deal. | MQL ID, Company Name, Company Market, Form Type, UTM fields, Last Touch Source, MQL Lead Level, Has SQL/Deal/Meeting, Intro Meeting Status, SQL Pipeline, Deal Amount, Deal MRR, Deal Is Won, Sales Territory |
| `gong_calls` | Gong calls enriched with HubSpot deal/company/contact/rep data. | Call Title, Company Name, Company Market, AE Name, BD Name, CSM Name, Deal Type, Deal Status, Stage Category, MRR, Contract Term, Region, Contact Persona, Seniority |
| `Marketing Funnel Analysis` | Website visit → sign-up → trial → subscription funnel. One row per first visit. | Visit ID, UTM fields, Channel Group, Page Name, Content Group, Country, Device, Sign Up At, Trial fields, Subscription fields, Churn fields, MQL/SQL/Deal fields, Probability scores |
| `Ad Conversion Funnel` | Ad-level performance: spend → clicks → signups → trials → subscriptions. | Ad ID, Ad Name, Channel Name, Total Cost USD, Clicks, Impressions, CTR, Sign Ups, Trials, SS Subscriptions, SS First MRR, Cost Per (click/signup/trial/subscription), MQLs, Exists In Airtable |
| `omni_dbt_bi__marketing_growth_channel_analysis` | User-level attribution from first visit through subscription. | User ID, Sign Up At, First/Last Attribution URLs + UTMs before sign-up, First Visit details, Had Trial, Has Subscription, First MRR, Submitted MQL |
| `users` | Full user profile with product usage, subscription, and attribution data. | User ID, Email, Sign Up info, Product plan, MRR, Logins, Takes/recordings/uploads (total + rolling windows), Clips created/exported, NPS, Pricing page visits, Book-a-demo clicks, Onboarding metadata, UTM attribution |
| `Daily Product Usage Per User` | Daily product activity per user. | (Times out on unfiltered queries - always filter by user ID or date range) |
| `Hubspot Companies` | Full company record with ICP scoring, BD activity, CSM data. | Company Name/Domain, Industry, Company Size, Company Market, ICP Tier (1-3), ICP Intent Signal, BD PQA workflow fields, CSM fields, Lifecycle Stage, Became Customer At, Churn Date, Stripe/Netsuite IDs |

## Key Concepts

**MRR sources:** Stripe (Self-Service PLG), HubSpot deals (B2B/Agency/Enterprise).

**Fiscal calendar:** the fiscal year starts in February. Q1 = Feb-Apr, Q2 = May-Jul, Q3 = Aug-Oct, Q4 = Nov-Jan. Omni's `Fiscal Quarter` dimensions follow it (FY2026 Q2 = May 1 to Jul 31, 2026). Derived from the GTM QBR deck dates and confirmed against Omni, 2026-09-07.

**QBR "Sales Rollover Metrics" basis:** the Sales section's tile (# SQL, # Deals, Pipeline Created, # Won Deals, Won MRR, per fiscal quarter) is the `Sales rollover` topic (`omni_dbt_bi__sales_rollover`) with `last_touch_source = Inbound`, period = `Timestamp Fiscal Quarter`. Segment it with `Sql Pipeline` (`Pre-Opp - US Agency`, `Pre-Opp - US Enterprise`, `Pre-Opp - EU Agency`, `Pre-Opp - EU Enterprise`; the deck's EU = both EU rows). Reconciled exactly to the Q1 FY26 QBR on all five measures, 2026-09-07. It is **not** the `MQLs to SQLs to Deals` topic: that topic's SQL-created cohort and deal-close-date bases run 5% to 25% under the tile, and its `Company Market` (Agency / Mid Market / Enterprise) is a different dimension from the deck's US Agency / US Enterprise / EU. Targets for the same table: `references/growth-reporting.md` → Targets.

**Funnel flow in Omni:**
```
Website Visit (Marketing Funnel Analysis)
  → Sign Up (users / omni_dbt_bi__marketing_growth_channel_analysis)
  → Trial
  → Subscription (Daily Customer MRR)
  → MQL form submit (MQLs to SQLs to Deals)
  → SQL / Pre-Op booked
  → Deal won
```

**ICP Tiers (Hubspot Companies topic):**
- Tier 1 (Strong): high-fit on country + industry + job title
- Tier 2 (Medium): mixed signals
- Tier 3 (Weak): two or more core dimensions at weakest level

**Channel Groups (Marketing Funnel Analysis):**
`organic search non brand`, `organic search brand`, `paid search`, `paid social`, `affiliate`, `direct`, `email`, `guest` (guest joins to a studio), `referral`

**QBD (Quit Before Demo) on Omni.** QBD flags a contact who submitted a demo form but never booked the meeting - a HubSpot-owned inbound re-engagement program (system of record and full field-by-field reliability audit in `systems/owned/hubspot.md` → "QBD & No-Show Program Fields"). It mirrors into Omni at the **contact grain** via `analytics.trf.hubspot__contacts` (Omni topic `Hubspot Contacts` - contact-level, distinct from the company-grain `Hubspot Companies` topic in the map above). Only `is_qbd_lead`, `first_qbd_timestamp`, `booked_after_qbd`, and `completed_after_qbd` are reliable; treat `qbd_outcome`, `qbd_owner`, and `amount_of_qbd_indicators` as broken/dead per the HubSpot audit. **Raw enum gotcha in Snowflake:** `is_qbd_lead` stores `'true'` / blank and `booked_after_qbd` / `completed_after_qbd` store `'Yes'` / blank (verified 2026-08-12) - filter on those literals, not `'True'`. Cohort: ~2,605 contacts flagged since 2025-11-02.

**Ad Conversion Funnel** links to Airtable for creative metadata (`Exists In Airtable`, `Release Name`). Not all ads are in Airtable.

**Reliable per-user timing and channel (Snowflake direct via `sql_exec_tool`).** When you need true per-user dates joined to an email list (for example, matching a HubSpot form-fill cohort), query Snowflake directly. Do not use HubSpot's product-synced `plg_*` or `hs_v2_date_entered_customer` fields, which are backfill snapshots, not event dates (see `hubspot.md`). Tables live in the `ANALYTICS` database and must be fully qualified (no default schema is set on the connection):
- `ANALYTICS.FS.USERS` - one row per user, keyed by `EMAIL` and `USER_ID`. True dates: `SIGN_UP_AT`, `FIRST_MRR_DATE` (first paid), plus `CURRENTLY_HAS_MRR`. Note `SIGN_UP_SOURCE`/`SIGN_UP_SOURCE_GROUP` here are platform (web, ios, android, macos), not marketing channel.
- `ANALYTICS.BI.MARKETING_FUNNEL_ANALYSIS` - keyed by `EMAIL`. Curated `CHANNEL_GROUP` (the real marketing channel: paid search, organic search, direct, paid social, guest, partnerships, and so on), UTMs, and precomputed `DAY_DIFF_SIGN_UP_TO_*` columns.
- `ANALYTICS.BI.SIGN_UP_TO_SUBSCRIPTION_DATA` - per-user `SIGN_UP_AT` and `SUBSCRIPTION_STARTED_AT` with conversion flags (keyed by `USER_ID`).

**Page-level tables (which page carried which UTM).** All are one row per pageview; `VISIT_ID` is a pageview ID despite the name.
- `ANALYTICS.STG.STG_SEGMENT__PAGES_WEB` (the web app's Segment source: `/register`, `/login`, `/dashboard`, `/studio`, `/editor`) and `ANALYTICS.STG.STG_SEGMENT__PAGES_MARKETING` (the Webflow site) - raw Segment pages. `CONTEXT_CAMPAIGN_*` is set only when the page's own URL has UTMs. This is the ground truth for what the browser sent.
- `ANALYTICS.TRF.INT_SEGMENT__PAGES_UNIONED` - both sources unioned, with `ORIGINAL_UTM_*` (parsed from the page URL) and `REFERRER_UTM_*` (parsed from the referrer URL) side by side.
- `ANALYTICS.TRF.INT_SEGMENT__ALL_VISITS_ENRICHED` and `ANALYTICS.MRT.FACT_VISITS` - identity-resolved (`USER_ID` backfilled) with `CHANNEL_GROUP`. Their `UTM_*` columns fall back to the referrer's UTMs when the page URL has none (see Known Issues).

Validation note: `FS.USERS.FIRST_MRR_DATE` matched HubSpot `profitwell_activated_on` to the day on spot checks, and has far better coverage than any single HubSpot field.

## Data by Role (Discoverability)

A recurring gap: stakeholders under-use Omni because they don't know which topics serve their role. When someone asks a vague or role-framed question, point them to the relevant topics below (the `data-agent` does this proactively).

<!-- Extend by adding a row per role: | Role | What they can answer | Primary topics (from the Topics map above) | Other sources (non-Omni, or - if none) |. Add a role-specific "note" block below the table only when one data domain is split across sources people don't connect (see SEO). -->

| Role | Can answer in Omni | Primary topics | Other sources |
|------|--------------------|----------------|---------------|
| SEO / Organic | Organic's *full-funnel and revenue* contribution - not just sessions/rankings. Split brand vs non-brand, by landing page and content group, through trial → subscription → MRR → MQL/SQL/deal. | `Marketing Funnel Analysis` (Channel Group = `organic search brand` / `organic search non brand`, Page Name, Content Group), `omni_dbt_bi__marketing_growth_channel_analysis` (organic-attributed users → subscription/MRR). | Search Console via Windsor.ai - see `data-agent`. |
| Growth / Paid | Spend → signup → trial → subscription with cost-per metrics; cross-channel funnel. | `Ad Conversion Funnel`, `Marketing Funnel Analysis` | - |
| PMM / Product | Feature adoption, usage depth, engagement, NPS, pricing-page and book-a-demo intent. | `users`, `Daily Product Usage Per User` (filter by user/date) | - |
| Lifecycle / Sales | B2B funnel, Pre-Ops, deal progression, ICP tiers, BD/CSM activity. | `MQLs to SQLs to Deals`, `Hubspot Companies`, `gong_calls` | - |
| Revenue / Finance | MRR, churn, expansion, by product and country. | `Daily Customer MRR` | - |

> **SEO note:** organic data lives in *two* places people rarely connect - Omni (`Marketing Funnel Analysis`, for organic's downstream revenue) and Search Console via Windsor.ai (for query/page/position). Pull from both for a complete organic picture.

## Known Issues / Failure Modes

| Issue | Symptoms | Resolution |
|-------|----------|------------|
| `Daily Product Usage Per User` times out on unfiltered queries | Query returns `timed_out: true` | Always filter by user ID or short date range before querying this topic |
| `pickTopic` returns the closest match, not an exact list | May return a different topic than intended | Verify the returned `topicId` label matches your intent before calling `getData` |
| `getData` silently answers with a *different* field when the one you asked for is not in the topic | Asking `Hubspot Contacts` for "count by self serve lead tier" returns a breakdown of **`Riverside Scoring`** (the legacy v2-era field) with a `lead_type = 'Self Service'` filter applied, and no warning that the requested field does not exist. Verified 2026-08-13. | Treat any `getData` result whose returned column name differs from what you asked for as a substitution, not an answer. This is the `references/evidence-standards.md` never-silently-pick rule failing at the tool layer, so the check has to be yours. Read the column headers in the result before quoting a number. |
| Most HubSpot contact properties are not queryable in Omni | Only ~106 of HubSpot's 1,236 contact properties survive into `TRF.HUBSPOT__CONTACTS`, which is what the `Hubspot Contacts` topic reads. Nothing errors; the field is simply absent and `getData` substitutes a near-match (see row above). | Check `systems/owned/hubspot.md` → "HubSpot to Snowflake to Omni" for the per-stage field counts. For properties that stop at the raw layer, query `HEVO.HEVO.HUBSPOT_CONTACTS` with `sql_exec_tool`. Getting a field onto a dashboard requires promoting it into the dbt models first. |
| `getData` re-interprets absolute date ranges | Asking for "2026-02-01 through 2026-07-31" came back filtered as `left_side 2026-02-01, right_side 1 month` on three of four attempts (2026-09-07), silently dropping five months | Phrase periods relatively ("last 7 months") or group by a `Fiscal Quarter` dimension and read the quarter labels in the result. Check the `query.filters` block the tool returns before quoting a number. |
| Wrong-basis pulls for the QBR Sales table | Segment or total won MRR 5% to 25% below the Sales Rollover tile; Enterprise reads "collapsed" on `Company Market` while the QBR segment shows 98% to target | Use the `Sales rollover` topic and `Sql Pipeline` dimension described under Key Concepts. Never present a `MQLs to SQLs to Deals` number as the QBR figure. |
| In-app pages carry a marketing UTM in the visits tables | `/dashboard`, `/editor`, `/verify-email` or `/login` pageviews show an affiliate or ad UTM that their own URL never had. For zaryamediabg (Impact) from 2026-06-01: 1,746 `/dashboard` and 818 `/editor` pageviews tagged this way. Raw Segment and Mixpanel show no UTM on the same pages. | Not the tracker, and not a session-wide re-stamp. `INT_SEGMENT__ALL_VISITS_ENRICHED` and `FACT_VISITS` fill `UTM_*` from the referrer URL when the page URL has none. A reload or redirect keeps the old `document.referrer`, so an in-app page can still report the tagged `/register` or landing URL. Confirm by comparing `ORIGINAL_UTM_*` with `REFERRER_UTM_*` in `INT_SEGMENT__PAGES_UNIONED`. Signup attribution (`MARKETING_FUNNEL_ANALYSIS`) uses the first visit and is not affected. Pageview and visit counts by UTM or channel are affected, so filter on `ORIGINAL_UTM_*` when you need the pages a link actually landed on. The fallback probably exists to recover UTMs that a redirect drops: a fix is a Data Team request to scope it, not to remove it. Found 2026-09-23. |
| An affiliate UTM on a user does not mean the affiliate acquired them | A user carries an affiliate `utm_source` / `utm_campaign`, but the affiliate click came after they already had an account. zaryamediabg (Impact), 2026-06-01 to 2026-09-23: 464 of 710 identified users who came through the link had signed up before the click (239 were already paying). 98% of its landing pageviews carry a Google Ads click ID (`gad_source`, `gclid`, `gbraid`), so it is a paid-search affiliate. | Before crediting an affiliate, join each user's first tagged pageview to `FS.USERS.SIGN_UP_AT` and split existing from new users. Check the landing URLs for Google Ads click IDs. A paid-search affiliate that reaches many existing users points to brand-term bidding, but our data does not show the affiliate's keywords. Whether that is allowed, and whether Impact pays on existing users who upgrade, are program questions for Growth Channels. |
| No self-serve scoring field is available in Omni | `self_serve_lead_tier`, `self_serve_composite_score`, `ss_behavior_score`, `self_serve_identity_score`, and `quality_signup` all reach Hevo raw but none reach STG/TRF. | The scoring model cannot be dashboarded today. Query `HEVO.HEVO.HUBSPOT_CONTACTS` directly, or promote the fields into dbt. Detail: `systems/owned/self-serve-lead-scoring.md`. |

## Related Systems

- **Upstream:** HubSpot (deals/contacts → MQLs to SQLs, gong_calls, Hubspot Companies), Stripe (MRR), Product/Segment (user events, usage), Ad platforms via Windsor.ai (Ad Conversion Funnel), Gong (calls)
- **Downstream:** Slack reporting (`#marketing-growth-report-updates`), exec readouts, `anthropic-skills:riverside-campaign-report`

## Pointers

- **Omni instance:** `riverside.omniapp.co`
- **Model ID:** `48d89fd2-ce24-44e1-bfe5-f3e30334c6dc`
- **Slack reporting channel:** `#marketing-growth-report-updates` (`C0ASQBR8YNR`)
- **Workbook URLs:** returned by `getData` - always share with user so they can explore further
- **Specialist skills:** `data-agent`, `measurement-agent`
