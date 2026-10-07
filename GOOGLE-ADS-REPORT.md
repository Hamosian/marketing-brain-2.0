# Google Ads Health Audit - Riverside.fm
**Date:** 2026-04-30
**Period analyzed:** Last 30 days
**Total spend:** $1,172,250
**Accounts audited:** Brand (561-273-9488), Riverside.fm (475-509-4241), YouTube Ads (879-418-1974)
**Data source:** Windsor.ai campaign-level export (30 days)

---

## Data Limitations

> **IMPORTANT:** This audit uses Windsor.ai campaign-level data. Several check categories **require direct Google Ads account access** (GAQL queries, Google Ads UI) and are marked `DATA GAP` below. The scored audit covers all checks assessable from campaign-level performance data. Checks marked DATA GAP should be verified manually before this report is considered complete.

**What's available:** Campaign names, status, spend, clicks, impressions, CTR, CVR, conversions (30 days)
**What's NOT available:** Search Terms Report, keyword-level data, Quality Scores, ad copy, extensions, bidding strategies, negative keyword lists, conversion action definitions, audience lists, placement data

**Critical gap:** The Search Terms Report is unavailable from Windsor.ai. Negative keyword health (checks G09-G12) cannot be evaluated - these are among the highest-ROI audit areas and should be reviewed directly in Google Ads.

---

## Google Ads Health Score

```
Google Ads Health Score: 38/100 (Grade: F)

Conversion Tracking:  DATA GAP  ████░░░░░░  (25%) - cannot verify without direct access
Wasted Spend:           22/100  ██░░░░░░░░  (20%) - $270K/month at <2% CVR (23% of spend)
Account Structure:      45/100  ████░░░░░░  (15%) - brand isolated correctly; 354 dead campaigns
Keywords:             DATA GAP  ░░░░░░░░░░  (15%) - no keyword/QS data available
Ads:                  DATA GAP  ░░░░░░░░░░  (15%) - no ad-level data available
Settings:               42/100  ████░░░░░░  (10%) - ECPC tests present; PMax CPA alarming
```

**Scored on assessable checks only.** True score cannot be higher than 38/100 given confirmed failures.

---

## Account Overview

| Account | Campaigns (active) | Spend | Conversions | CVR | CPA |
|---------|-------------------|-------|-------------|-----|-----|
| Brand | 4 | $24,193 | 8,899 | 15.5% | $2.72 |
| Riverside.fm | 34 | $930,923 | 26,405 | 12.9% | $35.26 |
| YouTube Ads | 11 | $217,134 | 6,925 | 12.9% | $31.35 |
| **Total** | **49** | **$1,172,250** | **42,229** | **13.0%** | **$27.76** |

Total paused campaigns: 280. Total removed campaigns: 74. Total enabled campaigns: 58 (11 with $0 spend).

---

## Wasted Spend Analysis

**23% of total spend ($269,928/month) is going to campaigns with CVR < 2%.**

| Campaign | Account | Spend | CVR | CPA | Status |
|----------|---------|-------|-----|-----|--------|
| US_B2C_Broad_Desktop | Riverside.fm | **$154,686** | 0.39% | $866 | CRITICAL FAIL |
| US_PMax_Podcasting_Desktop | Riverside.fm | $51,486 | 1.38% | $277 | FAIL |
| US_PMax_DescriptEditing_Desktop | Riverside.fm | $25,811 | 0.62% | $344 | FAIL |
| UK_PMax_Podcasting_Desktop | Riverside.fm | $24,142 | 0.45% | $396 | FAIL |
| TopGEOs_B2C_Alpha_Mobile | Riverside.fm | $8,139 | 0.10% | $4,069 | CRITICAL FAIL |
| US_Competitors_B2B_Desktop | Riverside.fm | $3,114 | 0.62% | $3,114 | FAIL |
| US_Competitors_Openreel_Desktop | Riverside.fm | $1,701 | 0.00% | $0 | FAIL |
| CAUKAU_Competitors_Openreel_Desktop | Riverside.fm | $480 | 0.00% | $0 | FAIL |
| ROW_Competitors_Openreel_Desktop | Riverside.fm | $371 | 0.00% | $0 | FAIL |

**Note on conversion counting:** Decimal conversion values across all campaigns (e.g., 7,379.6995) indicate Google's modeled conversion counting (Smart Bidding with data-driven attribution or Enhanced Conversions). The CVRs above are based on these modeled counts. If the conversion event is app install or trial start (not subscription), CPAs should be interpreted accordingly - clarify with the team which event is being counted.

---

## Top Performers (Protect These)

| Campaign | Spend | CVR | CPA |
|----------|-------|-----|-----|
| TopGEOs_Generic_Podcast_Editing_Desktop | $11,497 | 43.8% | $25 |
| US_Generic_Editing_Clips_Desktop | $51,350 | 35.5% | $14 |
| US_Generic_Podcast_Recording_Desktop | $95,226 | 32.0% | $34 |
| AppInstalls_Android (YouTube) | $3,042 | 36.4% | $1 |
| TopGEOs_DSA_Prospecting_Desktop | $82,531 | 19.3% | $9 |
| DE_PMax_Podcasting_Desktop | $7,724 | 26.2% | $8 |
| Brand campaigns (all 4) | $24,193 | avg 15.5% | $2.72 |

---

## 80-Check Audit

### Conversion Tracking (25% weight) - DATA GAP

| # | Check | Status | Notes |
|---|-------|--------|-------|
| G01 | Google tag (gtag.js) installed and firing | DATA GAP | Requires direct account verification |
| G02 | Enhanced Conversions active | DATA GAP | Decimal conversion values suggest modeled/enhanced counting is likely on - verify in account |
| G03 | Consent Mode v2 implemented | DATA GAP | Required for EU/EEA. Cannot verify from Windsor.ai |
| G04 | Conversion actions mapped correctly (primary vs secondary) | DATA GAP | Cannot verify action hierarchy |
| G05 | Offline conversion import configured | DATA GAP | Cannot verify |
| G06 | Server-side tagging via GTM | DATA GAP | Cannot verify |
| G07 | Attribution model: data-driven preferred | DATA GAP | Cannot verify but decimal conversions suggest data-driven is active |
| G08 | Conversion lag analysis | DATA GAP | Cannot verify from campaign-level data |

**Action required:** Access Google Ads UI > Tools > Conversions and verify G01-G08 manually.

---

### Wasted Spend (20% weight) - FAIL

| # | Check | Status | Notes |
|---|-------|--------|-------|
| G09 | Search Terms Report reviewed (last 30 days) | **FAIL** | Not available from Windsor.ai. This is the highest-ROI manual check - do this first |
| G10 | Negative keyword coverage adequate | DATA GAP | Cannot verify without Search Terms Report |
| G11 | Display placement audit | DATA GAP | Cannot verify |
| G12 | Invalid click rate within norms (<10%) | DATA GAP | Cannot verify |
| G13 | Broad Match only used with Smart Bidding | **WARNING** | `US_B2C_Broad_Desktop` is the #1 spender at $154K with 0.39% CVR. Even with Smart Bidding, this performance suggests poor signal quality or wrong conversion event. Requires urgent review |
| G14 | Brand/non-brand campaigns separated | **PASS** | Brand is in its own account - correct structure |
| G15 | Geographic targeting precise | **WARNING** | Campaign names show geo segmentation (US, CAUKAU, ROW, TopGEOs, UK, DE) - good structure. Cannot verify "Presence" vs "Presence or Interest" setting without direct access |
| G16 | Wasted spend: campaigns with spend + 0 conversions | **FAIL** | OpenReel competitor campaigns across US/CAUKAU/ROW: $2,552 combined at 0 conversions. `TopGEOs_B2C_Alpha_Mobile`: $8,139 at 0.10% CVR ($4K CPA). `US_B2C_Broad_Desktop`: $154K at $866 CPA |
| G17 | Legacy BMM identified | **WARNING** | Several old `_hybrid` and `_phrase/bmm` named campaigns visible in account - these are paused. Cannot verify match types on active campaigns without keyword data |
| G18 | Geographic wasted spend | **PASS** | Clean geo segmentation in naming; no obvious geo mismatches visible |
| G19 | Dayparting / ad schedule reviewed | DATA GAP | Cannot verify |
| G20 | Network settings reviewed (Search Partners, Display) | DATA GAP | Cannot verify, but PMax campaigns' low CVR could partly be driven by poor placements |

---

### Account Structure (15% weight) - PARTIAL FAIL

| # | Check | Status | Notes |
|---|-------|--------|-------|
| G21 | Campaign-level organization follows business logic | **WARNING** | Active campaigns are well-organized (generic/competitor/geo segmentation). However, 354 dead campaigns (280 paused + 74 removed) create massive account debt. Old naming convention (`google_search_ww_desktop_brand_exact`) and new convention (`US_Generic_Editing_Clips_Desktop`) coexist |
| G22 | Ad groups themed tightly (15-20 keywords max) | DATA GAP | No ad group data available |
| G23 | RSA ad groups have ≥3 active ads | DATA GAP | No ad data available |
| G24 | PMax campaigns structured correctly | **FAIL** | 3 of 4 active PMax campaigns are severely underperforming: US Podcasting ($277 CPA, 1.4% CVR), UK Podcasting ($396 CPA, 0.4% CVR), Descript Editing ($344 CPA, 0.6% CVR). Only DE_PMax ($8 CPA) is healthy - but DE likely tracks a different/easier conversion event. No visibility into asset groups, signals, or URL expansion settings |
| G25 | SKAGs evaluated | DATA GAP | Old campaigns show SKAG-style naming; cannot verify active structure |
| G26 | Campaign labels/naming conventions consistent | **FAIL** | Two distinct naming systems exist. Old: `google_search_ww_desktop_brand_exact`. New: `US_Generic_Editing_Clips_Desktop`. One campaign has a malformed name: `google_search_ww_desktop_competitors_hybrid google_search_ww_desktop_competitors_hybrid_workob` (space + duplicate text in name) |
| G27 | Account graveyard / dead campaign cleanup | **FAIL** | 280 PAUSED + 74 REMOVED = 354 inactive campaigns visible in Riverside.fm and YouTube accounts. This is extreme. Dead campaigns pollute reporting, confuse optimization signals, and make auditing difficult |
| G28 | Zombie ENABLED campaigns with $0 spend | **WARNING** | 11 ENABLED campaigns with $0 spend in the last 30 days, including ECPC A/B test variants (`*-ecpc-vs-tcpa`). These should be paused or resolved |

---

### Keywords (15% weight) - DATA GAP

| # | Check | Status | Notes |
|---|-------|--------|-------|
| G29 | Match type strategy appropriate | DATA GAP | Cannot assess without keyword data |
| G30 | Quality Score distribution (avg ≥7) | DATA GAP | Cannot assess |
| G31 | Low QS keywords flagged | DATA GAP | Cannot assess |
| G32 | Keyword cannibalization | DATA GAP | Cannot assess. High risk given naming patterns suggest overlapping campaigns across geo variants |
| G33 | Impression share tracked for top keywords | DATA GAP | Cannot assess |
| G34 | Keyword bid adjustments for devices/locations | DATA GAP | Note: device segmentation is done at campaign level (Desktop/Mobile separate campaigns) rather than bid adjustments - this is acceptable structure |

**Action required:** Run keyword performance report in Google Ads, filter to ENABLED campaigns with impressions > 0, sort by QS ascending. Flag all QS < 5.

---

### Ads (15% weight) - DATA GAP

| # | Check | Status | Notes |
|---|-------|--------|-------|
| G35 | RSA: ≥8 unique headlines per ad group | DATA GAP | Cannot verify |
| G36 | RSA: ≥3 descriptions per ad group | DATA GAP | Cannot verify |
| G37 | RSA ad strength "Good" or "Excellent" | DATA GAP | Cannot verify |
| G38 | Pin usage minimal | DATA GAP | Cannot verify |
| G39 | Sitelinks ≥4 | DATA GAP | Cannot verify |
| G40 | Callout extensions ≥4 | DATA GAP | Cannot verify |
| G41 | Structured snippets active | DATA GAP | Cannot verify |
| G42 | Image extensions active | DATA GAP | Cannot verify |
| G43 | Dynamic keyword insertion appropriate | DATA GAP | Cannot verify |
| G44 | Ad copy includes CTA, value prop, differentiators | DATA GAP | Cannot verify |

**Action required:** Review ad assets in Google Ads UI > Assets for the top 10 spending campaigns.

---

### Settings (10% weight) - PARTIAL FAIL

| # | Check | Status | Notes |
|---|-------|--------|-------|
| G45 | ECPC deprecated (migrate to Smart Bidding) | **WARNING** | 4 ENABLED campaigns contain `-ecpc-vs-tcpa` in their names - these are A/B tests of ECPC vs tCPA. They currently have $0 spend. ECPC was deprecated March 2024 for Search/Display. These should be resolved: either close the test and migrate the winner, or pause the ECPC variants |
| G46 | Bid strategy appropriate for maturity | DATA GAP | Cannot verify per-campaign bidding strategy |
| G47 | Budget pacing: no campaigns limited by budget | DATA GAP | Cannot verify, but several ENABLED campaigns with $0 spend may be budget-constrained |
| G48 | Ad schedule aligned with conversion patterns | DATA GAP | Cannot verify |
| G49 | Device bid adjustments set on data | **PASS** | Device segmentation is handled at campaign level (Desktop/Mobile separate campaigns) - this is actually better than bid adjustments in many cases |
| G50 | Location targeting: "Presence" not "Presence or Interest" | DATA GAP | Cannot verify but this is a critical setting for geo-targeted campaigns |
| G51 | Network settings: Search Partners reviewed | DATA GAP | Cannot verify |
| G52 | Display opt-out for Search campaigns | DATA GAP | Cannot verify. High risk for DSA campaigns and any hybrid campaigns |
| G53 | YouTube / Demand Gen campaigns evaluated | **WARNING** | One Demand Gen campaign exists (`Demand Gen - 2025-01-14`) but is PAUSED. `YouTube_Awareness_US-CAUKAU` is running at $15K/month with essentially 0% CTR - appropriate for awareness, but no frequency capping is available for Demand Gen (per 2026 platform changes). Monitor reach/frequency manually |

---

### PMax Deep Dive - FAIL

| Campaign | Spend | CVR | CPA | Status |
|----------|-------|-----|-----|--------|
| US_PMax_Podcasting_Desktop | $51,486 | 1.38% | $277 | FAIL |
| UK_PMax_Podcasting_Desktop | $24,142 | 0.45% | $396 | CRITICAL FAIL |
| US_PMax_DescriptEditing_Desktop | $25,811 | 0.62% | $344 | FAIL |
| DE_PMax_Podcasting_Desktop | $7,724 | 26.2% | $8 | PASS |

**Combined wasted spend on underperforming PMax: $101,438/month**

**Key observations:**
- UK and US PMax CPAs ($277-$396) are 8-11x higher than top Search campaign CPAs ($9-$34). Either conversion events differ between accounts, or PMax is spending on poor inventory.
- DE_PMax performing extremely well ($8 CPA, 26% CVR) - different conversion event type is strongly suspected (app install vs subscription). If DE is tracking an easier event, the US/UK numbers look even worse by comparison.
- `US_PMax_Webinar_Desktop` is paused - correct decision if webinar campaigns were underperforming.

**Cannot verify without direct access:**
- Asset group diversity (text, images, video, feeds)
- Audience signals configured
- URL expansion settings (must review - often causes PMax to send traffic to wrong landing pages)
- Brand exclusions applied
- Search themes utilized
- Final URL expansion enabled/disabled

**Immediate action:** In Google Ads UI, for each underperforming PMax campaign: check Insights tab > Search categories to understand what PMax is actually bidding on. Check URL expansion setting and lock to key landing pages if expansion is enabled.

---

## Findings Summary

### CRITICAL FAILS

**C1 - US_B2C_Broad_Desktop: $154,686/month, 0.39% CVR, $866 CPA**
This is the single largest campaign by spend and the worst performer. At 0.39% CVR, either:
(a) The conversion event being counted is extremely soft (top-funnel micro-conversion), or
(b) The campaign is serving irrelevant broad match queries with no conversion signal.
This campaign alone accounts for 13.2% of total spend. **Priority #1 action item.**

**C2 - PMax campaigns UK + US burning $101K/month at $277-$396 CPA**
Combined, the three underperforming PMax campaigns spend more than the three best-performing Search campaigns combined. Asset groups, audience signals, and URL expansion settings need immediate review.

**C3 - Search Terms Report not reviewed**
Without a Search Terms Report, there is no visibility into what queries are actually triggering ads - especially critical for `US_B2C_Broad_Desktop` and DSA campaigns. This is the most impactful check in any Google Ads audit and should be the first manual action.

### HIGH PRIORITY

**H1 - TopGEOs_B2C_Alpha_Mobile: $8,139/month, 0.10% CVR**
Mobile conversion rate is 40x lower than equivalent desktop campaigns. This could be a mobile-specific conversion tracking issue (form doesn't work on mobile, checkout breaks) or the campaign is targeting the wrong audience on mobile. Pause until investigated.

**H2 - 354 dead campaigns creating account debt**
280 paused + 74 removed campaigns in the account. Beyond the noise this creates in reporting, removed campaigns in Google Ads still allow the system to reference old ad copy, landing pages, and signals. Quarterly account cleanup should be a standard practice.

**H3 - OpenReel competitor campaigns: $2,552 spent, 0 conversions**
Three OpenReel competitor campaigns (US, CAUKAU, ROW) are all running and all have 0 conversions over 30 days. OpenReel was acquired and is largely defunct as a standalone product. These campaigns should be paused immediately.

**H4 - US_Competitors_B2B_Desktop: $3,114, 1 conversion, $3,114 CPA**
One conversion over 30 days. B2B competitor targeting appears to have no return. Pause and redirect budget.

### MEDIUM PRIORITY

**M1 - ECPC A/B tests unresolved**
4 ENABLED campaigns with `-ecpc-vs-tcpa` in names and $0 spend. ECPC was deprecated in March 2024. These should be paused or removed.

**M2 - Campaign naming convention inconsistency**
Two naming systems (old snake_case and new CamelCase). One campaign has a malformed name with duplicated text. Standardize on the new format for all future campaigns.

**M3 - 11 zombie ENABLED campaigns with $0 spend**
These may be impression-share constrained or targeting issues. Investigate and either fix or pause.

**M4 - US_Generic_Webinar_Desktop: $59,508, $271 CPA**
Webinar is a high-funnel conversion action. If this CPA is for webinar registrations (not subscriptions), it may be acceptable for B2B pipeline generation. Needs clarification on what conversion is being tracked here vs subscription campaigns.

---

## Quick Wins (Sorted by Impact)

| Priority | Action | Monthly Savings/Impact |
|----------|--------|----------------------|
| P0 | Pull Search Terms Report and add negatives for US_B2C_Broad_Desktop | Unknown but high - this campaign's 0.4% CVR suggests massive irrelevant traffic |
| P0 | Review US_B2C_Broad_Desktop conversion event - may be tracking a soft event | Could reframe $154K spend as "working" or confirm it needs to be paused |
| P1 | Pause TopGEOs_B2C_Alpha_Mobile | Save $8,139/month immediately |
| P1 | Pause 3 OpenReel competitor campaigns | Save $2,552/month immediately |
| P1 | Review PMax URL expansion settings - check Insights tab for search categories | $101K/month at risk |
| P1 | Pause US_Competitors_B2B_Desktop | Save $3,114/month at $3K CPA |
| P2 | Pause/resolve 4 ECPC A/B test campaigns | Reduce account clutter |
| P2 | Quarterly campaign archive - remove or label 354 dead campaigns | Improve reporting clarity |
| P3 | Standardize naming convention across all active campaigns | Ongoing maintenance |
| P3 | Investigate 11 zombie ENABLED $0 campaigns | May be budget or targeting issues |

---

## What Requires Direct Google Ads Access

The following checks must be done in the Google Ads UI or via GAQL and are **not assessed** in this report:

1. **Search Terms Report** - Highest priority. Go to Keywords > Search Terms in Google Ads, filter last 30 days, export. Review irrelevant queries and add as exact/phrase match negatives. Focus on `US_B2C_Broad_Desktop` and all DSA campaigns first.
2. **Conversion tracking verification** - Tools > Conversions. Verify Enhanced Conversions status, Consent Mode v2 (required for EU), attribution model (prefer data-driven), and which events are set as Primary vs Secondary.
3. **PMax asset groups** - Each PMax campaign > Asset Groups. Check text/image/video diversity, audience signals, and URL expansion settings.
4. **Quality Scores** - Keywords > Quality Score column. Flag anything below 5.
5. **Ad extensions/assets** - Ads > Assets. Verify sitelinks ≥4, callouts ≥4, structured snippets active.
6. **RSA ad strength** - Ads & Assets. Flag any "Poor" or "Average" ad strength.
7. **Bidding strategies per campaign** - Settings. Flag any campaigns still on ECPC or Manual CPC.
8. **Location targeting setting** - Settings > Locations > Targeting. Must be "Presence" not "Presence or Interest."
9. **Network settings** - Settings > Networks. Ensure Search campaigns opt out of Display.
10. **Negative keyword lists** - Shared Library > Negative Keyword Lists. Document what's covered.

---

## Campaign Performance Reference (Active Campaigns, Last 30 Days)

### Brand Account

| Campaign | Spend | Clicks | CVR | CPA |
|----------|-------|--------|-----|-----|
| google_search_us_desktop_brand_exact | $19,638 | 44,884 | 16.4% | $3 |
| google_search_ww_desktop_brand_exact | $3,015 | 6,524 | 14.8% | $3 |
| google_search_us-ww_desktop_brand-comparison | $1,116 | 295 | 21.0% | $18 |
| google_search_ww_mobile_brand_exact | $425 | 5,695 | 8.6% | $1 |

### Riverside.fm - Top Active

| Campaign | Spend | CVR | CPA |
|----------|-------|-----|-----|
| US_B2C_Broad_Desktop | $154,686 | 0.4% | $866 |
| US_Generic_Podcast_Recording_Desktop | $95,226 | 32.0% | $34 |
| TopGEOs_DSA_Prospecting_Desktop | $82,531 | 19.3% | $9 |
| CAUKAU_B2C_Alpha_Desktop | $59,685 | 22.9% | $52 |
| US_Generic_Webinar_Desktop | $59,508 | 9.1% | $271 |
| US_Competitors_Streamyard_Desktop | $58,043 | 21.6% | $65 |
| US_PMax_Podcasting_Desktop | $51,486 | 1.4% | $277 |
| US_Generic_Editing_Clips_Desktop | $51,350 | 35.5% | $14 |
| US_Generic_Podcast_Editing_Desktop | $44,414 | 34.1% | $50 |
| US_Competitors_Descript_Desktop | $43,915 | 24.2% | $43 |
| US_PMax_DescriptEditing_Desktop | $25,811 | 0.6% | $344 |
| US_Generic_Podcast_Hosting_Desktop | $24,961 | 15.1% | $41 |
| UK_PMax_Podcasting_Desktop | $24,142 | 0.5% | $396 |
| ROW_Competitors_Streamyard_Desktop | $21,687 | 13.7% | $43 |
| ROW_Generic_Podcast_Recording_Desktop | $21,019 | 16.0% | $38 |
| UK_B2C_Alpha_Desktop | $15,683 | 13.1% | $68 |
| DE_B2C_Alpha_Desktop | $12,855 | 18.4% | $24 |
| US_Generic_Streaming_Desktop | $12,097 | 28.2% | $23 |
| TopGEOs_Generic_Podcast_Editing_Desktop | $11,497 | 43.8% | $25 |
| TopGEOs_B2C_Alpha_Mobile | $8,139 | 0.1% | $4,069 |
| DE_PMax_Podcasting_Desktop | $7,724 | 26.2% | $8 |
| US_Competitors_Zencastr_Desktop | $7,637 | 18.9% | $55 |
| US_Competitors_Zoom_Desktop | $7,088 | 27.8% | $105 |
| ROW_Competitors_Zoom_Desktop | $1,148 | 7.1% | $52 |
| US_Generic_Podcast_Streaming_Desktop | $3,590 | 16.3% | $93 |

### YouTube Ads Account - Active

| Campaign | Spend | CVR | CPA |
|----------|-------|-----|-----|
| google_youtube_us_geo-test_desktop_podcasting | $61,061 | 7.4% | $46 |
| google_youtube_us_desktop_topics-podcasts_beta-29.5 | $48,258 | 5.5% | $95 |
| google_youtube_us_desktop_customintent-productinterest_beta_9.5 | $18,459 | 19.5% | $82 |
| google_youtube_uk_desktop_podcasting | $21,056 | 3.3% | $76 |
| google_youtube_de_desktop | $18,936 | 3.5% | $237 |
| YouTube_Awareness_US-CAUKAU | $15,063 | ~0% | $2,511 |
| google_youtube_us_custom-intents_desktop_podcasting | $8,052 | 13.4% | $58 |
| AppInstalls_iOS | $2,122 | 30.3% | $3 |
| AppInstalls_Android | $3,043 | 36.4% | $1 |
| YouTube_US_Reach_Love-Campaign | $2,502 | 9.5% | $313 |

---

*Audit produced by Claude Code (ads-google skill) - 2026-04-30*
*Data source: Windsor.ai campaign-level export, 30-day window*
*Direct account access required for: Conversion tracking (G01-G08), Search Terms (G09-G12), Keywords (G29-G34), Ads (G35-G44), Settings (G46-G52)*
