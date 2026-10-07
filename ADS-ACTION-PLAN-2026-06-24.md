# Ads action plan: Google and Meta (30-day refresh)

Date: 2026-06-24
Companion to `ADS-AUDIT-REPORT-2026-06-24.md`
Priority order: Critical, then High, then Medium, then Low

Currency note: figures are in account-reported currency and are directional until FX is confirmed (some accounts may bill in ILS). Relative comparisons hold regardless.

## Critical (fix immediately, revenue or data-loss risk)

| # | Action | Platform | Evidence | Effort |
|---|--------|----------|----------|--------|
| C1 | Add a Target CPA cap to `US_B2C_Broad_Desktop`, or pause it pending rebuild | Google | 172,512/30d, 185 conv, 932 CPA, 22% IS. Maximize Conversions with no cap. Flagged 2026-06-14 at 592 CPA, now worse. Suggested starting tCPA 60 to 90 (1.5x best peers), then tighten weekly | 10 min |
| C2 | Add Target CPA caps to the other uncapped Maximize Conversions campaigns above 200 CPA | Google | US_PMax_DescriptEditing (409), UK_PMax_Podcasting (781), US_Generic_Webinar (222), US_Generic_Podcast_Recording (207), CAUKAU_B2C_Alpha (224), TopGEOs_B2C_Alpha_Mobile (452), US_PMax_Podcasting_Clean (510). Combined 457,686/30d | 30 min |
| C3 | Build and apply themed negative-keyword lists at account level | Google | 17.3% of search-term spend (102,445/30d) on zero-conversion terms. Themes: generic video editing, webinar tools (webinarjam, gotowebinar), hardware, off-intent competitors | 30 min |
| C4 | Fix the Meta website Lead event (currently firing 0) | Meta | Lead is a standard event returning 0 on every campaign. Needs pixel and CAPI event configuration with developer support | Dev task |
| C5 | Pass purchase value into the Meta pixel and CAPI | Meta | Purchase value 0 across all campaigns despite 648 reported purchases. Blocks value-based bidding and ROAS measurement | Dev task |
| C6 | Add conversion value to Google for non-brand campaigns | Google | Conversion value absent on ~99% of non-brand spend. Use value rules or dynamic values per plan tier so Smart Bidding can optimize toward worth, not just volume | 1 to 2 hrs |

## High (fix within 7 days)

| # | Action | Platform | Evidence | Effort |
|---|--------|----------|----------|--------|
| H1 | Switch Target Spend competitor and retargeting campaigns to Maximize Conversions | Google | US/ROW/CAUKAU/DE Openreel, WW_DSA_Retargeting use Target Spend (maximize clicks) despite tracking conversions. Example: US_Competitors_Openreel 1,607 spend, 1.4 conv | 5 min each |
| H2 | Add frequency cap or refresh creative on Meta Remarket > Event_SignedUp | Meta | Frequency 16.7, CTR 0.61%. Audience exhaustion. Cap to 8 to 12 and rotate creative | 10 min |
| H3 | Review and rebalance budget toward efficient, throttled campaigns | Google | Strong campaigns budget-limited (for example WW brand exact at low IS), while US_B2C_Broad runs uncapped at 932. Move budget to peers converting at 20 to 70 | 30 min |
| H4 | Verify Consent Mode v2 (Advanced) for UK and DE campaigns | Google | EU and EEA enforcement active since July 2025. Unverifiable from Windsor. Affects modeled conversion recovery on European spend | 60 min |
| H5 | Confirm Enhanced Conversions enabled and verified | Google | Not visible in Windsor. ~10% measurement uplift, free, improves Smart Bidding across all automated campaigns | 5 min check |
| H6 | Add a third creative format (carousel) to image-only and static-only Meta ad sets | Meta | Only 2 formats account-wide. Newsletter and App are image-only, remarketing is static plus one video | 1 hr |

## Medium (fix within 30 days)

| # | Action | Platform | Evidence | Effort |
|---|--------|----------|----------|--------|
| M1 | Consolidate tiny competitor campaigns | Google | Many sub-500 campaigns (DE_Competitors_Openreel 27, CAUKAU_Competitors_Openreel 421). Fragmentation adds management overhead without volume | 1 hr |
| M2 | Pull a full Quality Score review from the Google Ads UI | Google | Windsor returns summed QS (unusable). Verify account-wide QS, expected CTR, ad relevance, landing-page experience | 30 min |
| M3 | Audit conversion actions for micro vs macro and duplicate counting | Google | Several campaigns report very high conversion counts with no value, suggesting soft or micro events may be set as primary. Verify primary conversion per campaign | 45 min |
| M4 | Lower Newsletter prospecting frequency | Meta | Newsletter ad set frequency 4.9, above the 3.0 prospecting target | 15 min |
| M5 | Review Meta audience exclusions | Meta | Confirm purchasers and recent converters are excluded from prospecting and remarketing entry. Not verifiable from Windsor | 30 min |

## Low (backlog)

| # | Action | Platform | Evidence | Effort |
|---|--------|----------|----------|--------|
| L1 | Evaluate the YouTube awareness and Love campaigns on the right KPI | Google | TARGET_CPV and TARGET_CPM campaigns should be judged on view-rate and reach, not CPA. Exclude from CPA-averaged reporting | 15 min |
| L2 | Verify UTM coverage on Meta ad URLs | Meta | Needed for GA4 and HubSpot attribution consistency. Not visible in Windsor | 30 min |
| L3 | Review whether paused-but-recently-spending campaigns should be deleted or revived | Google | ~236K of 30-day spend went to now-paused campaigns. Confirm intentional | 20 min |

## Kill list (pause now)

- `US_PMax_Podcasting_Desktop_Clean`: 28 conv, 510 CPA, 27% IS
- `UK_PMax_Podcasting_Desktop`: 67 conv, 781 CPA, 19% IS
- `US_B2C_Broad_Desktop`: pause unless a tCPA cap is applied today (932 CPA)

## Scale candidates (once measurement is fixed)

- Brand campaigns: 2 to 2.50 CPA, currently budget-limited on the worldwide brand exact campaign. Strong, cheap conversions being throttled.
- `TopGEOs_Generic_Podcast_Editing_Desktop`: 22 CPA at 99% IS, efficient and near-saturated in current geos. Test geo expansion.
- Meta `CBO_Podcasting_US`: 9% to 15% hook CTR on native vertical video. The best creative in the account. Worth more budget after the Meta value and lead signal is fixed.
