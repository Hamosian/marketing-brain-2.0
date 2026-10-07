<!-- last-reviewed: 2026-09-07 -->
# Paid Acquisition

> Google, Meta, LinkedIn (and other) ad accounts plus the reporting layer on top of them.

## Overview

Raz Navon owns Paid Acquisition. Savion Ron Shemesh covers Growth Channels, an adjacent function, since Dor Druker's departure on 2026-08-04. Riverside runs ads across Google, Meta, LinkedIn, and Bing. Cross-platform performance data is centralized through Windsor.ai (MCP connector available in Claude).

## How Claude Works With This

| Action | How |
|--------|-----|
| Pull cross-platform metrics | Windsor.ai MCP connector (`mcp__d2d9c91e-*`) via the data-agent |
| Investigate performance | Windsor.ai `get_data` with platform + fields + date range |
| Make changes | Platform UIs directly (Google Ads, Meta Ads Manager, LinkedIn Campaign Manager) |
| Attribution | HubSpot + Omni BI (see `systems/owned/hubspot.md`) |

## Windsor.ai Connector

Windsor.ai aggregates ad data from all active platforms into a single MCP interface. Use `data-agent` skill to query it.

**MCP connector ID:** `mcp__d2d9c91e-04a3-4128-b98e-5d252640ee02`

**Key tools:**
- `get_connectors` - list connected platforms and account IDs
- `get_fields` - list all available dimensions and metrics for a platform
- `get_options` - list available field values (e.g. campaign names) for a field
- `get_data` - pull actual metrics (specify connector, fields, date range, filters)

## Connected Platforms & Accounts

| Platform | Account | Account ID | Windsor Connector |
|----------|---------|------------|-------------------|
| Google Ads | Brand | 561-273-9488 | `google_ads` |
| Google Ads | Riverside.com | 475-509-4241 | `google_ads` |
| Google Ads | YouTube Ads | 879-418-1974 | `google_ads` |
| Google Ads | Search Ads Account V2 (dormant) | 228-244-5778 | `google_ads` |
| Meta (Facebook/Instagram) | Riverside | 250675469352903 | `facebook` |
| Meta (Facebook/Instagram) | Riverside 2.0 (dormant) | 697387924928899 | `facebook` |
| LinkedIn | Nadav's Ad Account | 506910541 | `linkedin` |
| Bing (Microsoft) | Riverside.com | (see connector) | `bing` |
| GA4 | riverside.com | 329843929 | `google_analytics` |
| Search Console | 7 properties | (see connector) | `google_search_console` |

> **Dormant accounts** (`Search Ads Account V2`, `Riverside 2.0`): connected in Windsor but $0 spend in the trailing 90 days as of the 2026-06-14 audit. Exclude them from active-spend comparisons.

**Owner:** Raz Navon

## Key Fields by Platform

> Some fields below are platform-native but renamed or not exposed via Windsor (e.g. LinkedIn audience breakdowns, Bing Quality Score / Impression Share). Check **Windsor.ai field gotchas** under Known Issues before querying.

### Google Ads
Core metrics: `Clicks`, `Impressions`, `Cost`, `CTR`, `Avg CPC`, `Conversions`, `Conversion Rate`, `Cost per Conversion`, `ROAS`
Dimensions: `Campaign`, `Ad Group`, `Keyword`, `Date`, `Account Name`, `Device`, `Match Type`
Quality: `Quality Score`, `Expected CTR`, `Ad Relevance`, `Landing Page Experience`, `Impression Share`
Bidding: `Bidding Strategy`, `Target CPA`, `Target ROAS`

### Meta (Facebook/Instagram)
Core metrics: `Total Cost` (spend), `Impressions`, `Clicks`, `Link Clicks`, `Reach`, `Frequency`, `CTR`, `CPC`, `CPM`, `Purchase ROAS`
Dimensions: `Campaign`, `Ad Set Name`, `Ad Name`, `Date`, `Device (Impression)`, `Ad Placement`
Conversions (Riverside custom): `Paid Conversion`, `New Trial Sign Up`, `Finished Onboarding`, `Subscription Payment Succeeded`, `User Payment - [plan]` (per plan tier: $9/mo, $19/mo, $29/mo, $180/y, $288/y, $349/y, $39/mo, $49/mo, $468/y)
Funnel signals: `Start trial conversions`, `firstRecordingCreated`, `studioRecordingStarted`, `recordingDownloaded`, `clipDownloaded`
B2B signals: `Enterprise Lead`, `Enterprise Lead Form Submission`, `webflowEnterpriseFormSubmitted`, `webflowWebinarFormSubmitted`

### LinkedIn
Core metrics: `Spend`, `Clicks`, `Impressions`, `CTR`, `CPC`, `CPM`, `Conversions`, `Cost per Conversion`
Dimensions: `Campaign`, `Campaign Group`, `Ad`, `Date`
Audience breakdowns: `Company Name`, `Company Industry`, `Company Size`, `Job Title`, `Job Seniority`, `Job Function`, `Member Country`, `Member Region`
Video: `Video Views`, `Video Completions`, `Video Completion Rate`

### Bing (Microsoft Ads)
Core metrics: `Spend`, `Clicks`, `Impressions`, `CTR`, `CPC`, `Conversions`, `Cost per Conversion`
Dimensions: `Campaign`, `Ad Group`, `Keyword`, `Date`
Quality: `Quality Score`, `Expected CTR`, `Ad Relevance`, `Impression Share`

## Reporting

- **Cross-platform view:** Windsor.ai via Claude (data-agent)
- **Attribution:** HubSpot (Last Touch Source) + Omni BI
- **Source of truth for spend:** Platform-native + Windsor.ai aggregated
- **Slack channel:** `#marketing-growth-ppc-team`

## Common Windsor.ai Query Patterns

```
# Cross-platform spend last 30 days
connector: all platforms
fields: [platform, campaign, spend, clicks, conversions, cost_per_conversion]
date_range: last 30 days

# Meta trial conversions by campaign
connector: facebook
fields: [campaign, spend, start_trial_conversions, paid_conversion_count, cost_per_paid_conversion]
date_range: last 7 days

# Google keyword performance
connector: google_ads
fields: [keyword, campaign, ad_group, clicks, impressions, ctr, avg_cpc, conversions, quality_score]
date_range: last 30 days
```

## Meta Conversions API via Segment

Server-side conversion events can reach Meta without touching the lifecycle, by having a HubSpot workflow POST a Segment `track` call to an HTTP source and letting Segment's Facebook Conversions API destination forward it. Chosen 2026-09-06 (Jonathan + Hanan) for the Typeform Webinar Benchmark Report quiz, specifically to avoid adding logic to the lifecycle. Reference implementation: HubSpot workflow `1878717070`.

Four things this path gets wrong if nobody checks them:

- **`fbc` needs reformatting.** HubSpot stores the bare `fbclid` in `hs_facebook_click_id` (capture mechanics: `hubspot.md` -> "Click-ID Capture on Third-Party-Hosted Forms"). Meta CAPI expects `fbc` in the cookie format `fb.1.<click_timestamp_ms>.<fbclid>`, and Segment passes a mapped `fbc` through as-is rather than synthesising the prefix. Reformat in the sending code or in the destination mapping, or Meta ignores the click id and match quality drops to email-only.
- **Property names do not auto-map.** A click id sent as `properties.hs_facebook_click_id` needs an explicit mapping to `fbc` in the destination. Nothing errors if it is missing - the event simply arrives without it.
- **Destination mappings key on event name, so the event name must be unique to the thing being measured.** A generic name collides with whatever else already emits it: `visitFormSubmitted` fires ~1,700 times per 30 days from the website pipeline, so mapping that name to a Meta conversion would drown the intended signal. Either send a purpose-specific event name, or confirm the destination is scoped to the one source and add a destination filter on a discriminating property (`properties.source`). Riverside's convention is to rename to a **custom** Meta event in the destination rather than consuming a Meta standard-event slot (Dudi, 2026-09-03).
- **Volume has to clear the learning phase.** Meta needs roughly 50 conversions per ad set per week to optimise. A conversion event firing a handful of times a week gives Meta nothing to work with - check expected volume against that bar *before* building the pipe, not after.

Backfilling is not an option: Meta rejects conversions older than 7 days, so bulk-enrolling historical contacts on turn-on wastes the events rather than seeding the model.

## Known Issues / Failure Modes

| Issue | Symptoms | Resolution |
|-------|----------|------------|
| Windsor field lists are very large | `get_fields` returns 500k+ chars for Google Ads | Use `get_options` for specific values; use data-agent to handle |
| Multiple Google Ads accounts | Queries may blend Brand + Riverside.com + YouTube accounts | Always filter by Account ID when comparing |

### Windsor.ai field gotchas

Field-mapping quirks verified during the 2026-06-14 audit. Easy to rediscover the hard way, so check here first.

_Last verified 2026-06-14; Google `keyword_text`, `get_fields` overflow, the new `quality_score` quirk, and the Meta value/lead nulls re-confirmed live on 2026-06-24. Platform APIs and Windsor field mappings drift over time, so re-verify before relying on this section for a new audit._

**Google Ads**
- Keyword text field id is `keyword_text`, **not** `keyword`. Search term is `search_term`.
- `get_fields` with no field filter returns ~250k chars and overflows context. Always pass a targeted field list.
- `quality_score` is **summed over the period, not the 1-10 score**. Over a 30-day pull the brand keyword "riverside" reads `300` (≈ 30 days × QS 10), with other values from 0 to 580. Do **not** treat it as a 1-10 Quality Score. There is no reliable per-day count to divide by, so QS-based checks (account-wide QS, % keywords QS ≤3, expected CTR / ad relevance / landing-page-experience components) are **not scoreable via Windsor**. Pull Quality Score from the Google Ads UI instead.
- A keyword/search-term pull (e.g. `clicks ≥ 1` across the search accounts) overflows the tool-result limit (the 2026-06-24 run returned 862 keywords / 4,390 search terms as files). Expect to process these with jq or Python from the saved file rather than inline.

**Meta (`facebook`)**
- There is **no** generic `conversions` or `cost_per_conversion` field. Use the action fields:
  - `actions_offsite_conversion_fb_pixel_custom`: Riverside custom pixel conversions (the primary signal)
  - `actions_complete_registration`
  - `actions_offsite_conversion_fb_pixel_purchase`
- `action_values_offsite_conversion_fb_pixel_purchase` (purchase value) returns NULL on every row. This is an instrumentation gap, not a Windsor field quirk: no revenue value is being passed to the Meta pixel. Needs follow-up with the Meta pixel/CAPI owner, not just a documented workaround.
- `actions_offsite_conversion_fb_pixel_lead` returns NULL. Same class of issue: the website Lead event is not firing (pixel/event configuration). Track both together and escalate for investigation rather than treating them as stable API behavior.
- Requesting `frequency` or `reach` forces ad-set-grain rows. Omit them for clean campaign-level aggregation.

**LinkedIn**
- Windsor lacks audience-breakdown fields (`company_industry`, `job_function`, `job_seniority`) and `cost_per_conversion`. The audience breakdowns under Key Fields are LinkedIn-native but not exposed via Windsor.
- `conversions` here means post-view "share conversions" (weak signal).
- `member_country` cannot be combined with other aggregation fields.

**Bing (Microsoft)**
- Legacy `conversions` is deprecated and returns 0. Use `conversions_qualified`.
- No `quality_score` or `impression_share` available via Windsor; verify those in the Microsoft Ads UI.

## Related Systems

- **Upstream:** Brand, creative pipeline, landing pages (`systems/owned/marketing-website.md`)
- **Downstream:** HubSpot (lead capture), Omni BI (reporting), Windsor.ai (cross-platform aggregation)

## Pointers

- **Windsor.ai MCP:** `mcp__d2d9c91e-04a3-4128-b98e-5d252640ee02`
- **Slack:** `#marketing-growth-ppc-team`
- **Paid Acquisition owner:** Raz Navon (Head)
- **Growth Channels owner:** Savion Ron Shemesh (covering since Dor Druker's departure, 2026-08-04)
- **Specialist skills:** `paid-acquisition-agent`, `data-agent`, `measurement-agent`
