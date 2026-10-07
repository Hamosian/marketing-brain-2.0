# Ads audit report: Google and Meta (30-day refresh)

Date: 2026-06-24
Window: last 30 days (2026-05-25 to 2026-06-24)
Data source: Windsor.ai live pull (no exports)
Scope: Google Ads (Brand, Riverside.fm, YouTube) and Meta (riverside account)
Prepared by: Marketing OS agent

> This is a focused 30-day Google and Meta refresh. It complements, and does not replace, the full 90-day all-platform audit in `ADS-AUDIT-REPORT.md` (2026-06-14), which also covers LinkedIn and Microsoft/Bing.

## Two caveats carried throughout

1. **Currency.** Riverside ad accounts may bill in different currencies (some likely in ILS, roughly 3.7 to USD per the 2026-06-14 audit). Per-platform budget shares and all relative comparisons (campaign vs campaign within an account) are reliable. Absolute dollar sums and absolute CPAs are directional only until FX is verified. Do not quote absolute figures externally without confirming account currency.
2. **Scope of data.** Windsor exposes performance metrics, not account configuration. Config-level checks (Enhanced Conversions, Consent Mode, pixel and CAPI setup, EMQ, audiences, creative assets, Quality Score) are marked "needs platform-UI verification" and excluded from scoring rather than guessed. Per the scoring rules, N/A checks are removed from the denominator, so each score reflects only the data-observable subset.

Coverage this run: Google scored on 15 of 80 checks, Meta on 12 of 50. Plus one data-quality note: Windsor returns a **summed** Quality Score, not the 1 to 10 value (the brand keyword "riverside" reads 300 = 30 days x QS 10), so the Google Keywords and Quality Score category could not be scored.

## Executive summary

| Metric | Result |
|--------|--------|
| Aggregate Ads Health Score | **64.8 / 100, Grade C** (budget-weighted) |
| Google Ads | **65.0 / 100, Grade C** (Needs improvement) |
| Meta Ads | **53.5 / 100, Grade D** (Poor); foundational signal layer is F-grade (see note) |
| 30-day spend (account currency) | Google 1,188,583 (98.1%), Meta 22,409 (1.9%), total 1,210,992 |
| Business type | B2C and B2B SaaS subscription (recording, editing, AI clips, webinars) |

Meta is under 2% of paid spend, so the blended score is effectively the Google score. Both platforms are reported separately below so Meta's problems are not masked.

### What changed since the 2026-06-14 audit (10 days ago)

The most important finding of this refresh is that the prior audit's top issue is unaddressed and deteriorating.

| Item | 2026-06-14 (90d) | 2026-06-24 (30d) | Direction |
|------|------------------|------------------|-----------|
| US_B2C_Broad_Desktop CPA | $592 | $932 | Worse by 57% |
| US_B2C_Broad spend pace | ~$150k/30d | $172.5k/30d | Up |
| US_B2C_Broad bidding | Maximize Conversions, no tCPA cap | Still Maximize Conversions, no tCPA cap | Unchanged |
| Meta purchase value and Lead event | Both null | Both still null | Unchanged |
| Meta worst retargeting frequency | 24.5 | 16.7 | Improved but still failing |

The recommended 10-minute fix from the last audit (add a Target CPA cap to the runaway Maximize Conversions campaigns) does not appear to have been applied. US_B2C_Broad is now the most expensive line item in the account and its efficiency is getting worse.

### Top 5 critical issues

1. **`US_B2C_Broad_Desktop`: largest spend, worst efficiency, and worsening.** 172,512 in 30 days at a 932 cost per conversion versus 20 to 70 on strong campaigns. Search impression share 22%, so it loses most auctions while still spending heavily. Flagged 10 days ago, now worse. (Google)
2. **39% of Google spend (457,686 in 30 days) sits in 8 enabled campaigns above 200 CPA**, while comparable campaigns convert at 20 to 70. (Google)
3. **Search-term waste is 17.3%.** 102,445 over 30 days went to search terms with over 10 spend and zero conversions ("video editor", "webinar", "teleprompter online", "opus clip"). (Google)
4. **Meta cannot optimize for value or leads.** Purchase value is 0 and the website Lead event is 0 on every campaign, so Meta optimizes on a custom event with no revenue or lead signal. (Meta, Cross-platform X-PI1)
5. **Conversion value missing on roughly 99% of non-brand Google spend.** Campaigns run Maximize Conversions (volume), not value. (Google)

### Top 5 quick wins (high impact, under 15 minutes)

1. Add a Target CPA cap to `US_B2C_Broad_Desktop` and the other uncapped Maximize Conversions campaigns, or pause US_B2C_Broad pending rebuild. (10 min)
2. Add negative keywords for the top zero-conversion search terms. (10 min)
3. Switch the Target Spend competitor campaigns (Openreel, retargeting DSA) to Maximize Conversions. (5 min each)
4. Add a frequency cap or refresh creative on Meta `Remarket > Event_SignedUp` (frequency 16.7). (10 min)
5. Pause `US_PMax_Podcasting_Desktop_Clean` (28 conv, 510 CPA, IS 27%) and `UK_PMax_Podcasting_Desktop` (781 CPA, IS 19%). (2 min)

---

## Google Ads

**Score: 65.0 / 100, Grade C.** Scored on 15 of 80 observable checks. Strong account hygiene (naming, brand separation, smart bidding on most campaigns, clean keyword-level waste) is dragged down by search-term waste, missing conversion values, and a small cluster of very expensive campaigns.

### Category breakdown (observable subset)

| Category | Weight | Verdict |
|----------|--------|---------|
| Conversion tracking | 25% | Mixed. Conversions fire across all campaigns (G42 pass). Conversion value absent on ~99% of non-brand spend (G49 fail). Tag page-completeness unverified (G-CT3 warning). Enhanced Conversions, Consent Mode v2, server-side, attribution, dedup: needs UI. |
| Wasted spend and negatives | 20% | Weak. 17.3% of search-term spend on zero-conversion terms (G16 fail). At keyword level only 1 keyword has over 100 clicks and 0 conversions (G-WS1 pass), so the leak is at the search-term and broad-targeting layer. Broad match is paired with smart bidding, not manual (G17 pass). |
| Account structure | 15% | Good. Clear naming convention (G01 pass). Brand and non-brand cleanly separated via a dedicated Brand account (G05 pass). PMax present (G06 pass). Fragmentation from many tiny competitor campaigns (G04 warning). Allocation skewed toward poor performers (G08 warning). |
| Keywords and Quality Score | 15% | Not scored. Windsor returns summed Quality Score. Verify QS, expected CTR, ad relevance, landing-page experience in the UI. |
| Ads and assets | 15% | Partial. Search CTRs strong (G-AD2 pass). RSA strength, headline and description counts, PMax asset density and video: needs UI. |
| Settings and targeting | 10% | Mixed. Target Spend on some competitor and retargeting campaigns instead of conversion bidding (G36 warning). Brand on Manual CPC with high volume, defensible but flagged (G40 warning). Several high-spend campaigns budget-limited at low impression share (G39 warning). Extensions, audiences, geo method, landing pages: needs UI. |

### Spend and performance by account (30 days, account currency)

| Account | Status | Spend | Conversions | Conv value |
|---------|--------|-------|-------------|-----------|
| Riverside.fm | Enabled | 721,827 | 5,477 | 8,992 |
| YouTube | Enabled | 206,716 | 8,509 | 5,587 |
| Riverside.fm | Paused (spent in window) | 169,115 | 7,264 | 3,019 |
| YouTube | Paused (spent in window) | 67,403 | 1,056 | 1,005 |
| Brand | Enabled | 23,522 | 9,751 | 36,318 |
| Search Ads V2 | Dormant | 0 | 0 | 0 |

About 236K (20%) of Google spend in the window went to campaigns now paused, which suggests active pruning but also that a fifth of last month's spend produced results the team chose to switch off.

### The high-CPA cluster (kill or fix list)

8 enabled campaigns, 457,686 in 30 days (39% of Google spend), all above 200 CPA while comparable campaigns convert at 20 to 70:

| Spend 30d | Conv | CPA | Search IS | Campaign | Read |
|-----------|------|-----|-----------|----------|------|
| 172,512 | 185 | 932 | 22% | US_B2C_Broad_Desktop | Add tCPA or pause and rebuild. Broad B2C at ~13x peer CPA. Worsened since last audit. |
| 69,282 | 169 | 409 | 15% | US_PMax_DescriptEditing_Desktop | Budget-starved and expensive. Restructure or pause. |
| 58,827 | 266 | 222 | 56% | US_Generic_Webinar_Desktop | Has some conv value (3,051). Tighten targeting and negatives. |
| 51,987 | 67 | 781 | 19% | UK_PMax_Podcasting_Desktop | Pause. Very low volume at very high CPA. |
| 38,027 | 184 | 207 | 82% | US_Generic_Podcast_Recording_Desktop | High IS, not budget-limited. The CPA itself is the issue. |
| 36,733 | 164 | 224 | 72% | CAUKAU_B2C_Alpha_Desktop | Review targeting and bids. |
| 16,045 | 36 | 452 | 94% | TopGEOs_B2C_Alpha_Mobile | Near-full IS at high CPA. Check mobile landing page. |
| 14,274 | 28 | 510 | 27% | US_PMax_Podcasting_Desktop_Clean | Pause. Lowest volume, high CPA. |

Caveat: CPA comparison assumes a consistent conversion definition across campaigns. B2C Broad and Alpha campaigns may optimize toward a different (softer or harder) conversion, which would partly explain the gap. Confirm the primary conversion action per campaign in the UI. Even allowing for that, 932 and 781 are extreme.

### Top wasted search terms (over 10 spend, 0 conversions, 30 days)

| Spend | Clicks | Campaign | Search term |
|-------|--------|----------|-------------|
| 1,085 | 325 | US_B2C_Broad_Desktop | video editor |
| 847 | 65 | US_Generic_Webinar_Mobile | webinar |
| 776 | 47 | US_Generic_Webinar_Mobile | webinarjam |
| 521 | 163 | US_B2C_Broad_Desktop | teleprompter online |
| 478 | 25 | TopGEOs_B2C_Alpha_Mobile | best podcast hosting platform |
| 472 | 30 | US_B2C_Broad_Desktop | podcast studio |
| 452 | 73 | US_B2C_Broad_Desktop | opus clip |
| 443 | 34 | US_Generic_Webinar_Mobile | attendee gotowebinar com register |
| 443 | 21 | US_B2C_Broad_Desktop | apple podcast connect |
| 442 | 69 | TopGEOs_B2C_Alpha_Mobile | podcast software |

Higher-confidence subset: 363 terms with over 50 spend and 0 conversions = 39,020 in 30 days. US_B2C_Broad and US_Generic_Webinar_Mobile are the largest contributors. Many leaking terms are off-intent (generic "video editor", competitor webinar tools, hardware queries), which points to thin negative-keyword coverage on the broad and DSA campaigns.

---

## Meta Ads

**Score: 53.5 / 100, Grade D.** Scored on 12 of 50 observable checks. Note: the foundational signal layer is F-grade in isolation (purchase value and Lead event both dead, value-based bidding impossible), consistent with the 2026-06-14 audit that scored Meta 7/100. The higher number here reflects a narrower data-observable check set plus genuinely strong creative work on the podcasting campaign; it should not be read as "Meta is fine."

### Category breakdown (observable subset)

| Category | Weight | Verdict |
|----------|--------|---------|
| Pixel and CAPI health | 30% | Pixel firing (M01 pass). The account optimizes on a custom pixel event (9,823 custom events in 30d) while the standard website Lead event returns 0 and purchase value returns 0 (M07 fail). CAPI deployment, EMQ, dedup, domain verification, AEM: needs Events Manager. |
| Creative (diversity and fatigue) | 30% | Weak. Only 2 formats account-wide (static image and video), no carousel, several single-format ad sets (M25 fail). 9:16 vertical present on the podcasting campaign (M27 pass). Main ad sets well-stocked; App and Brand ad sets carry only 3 (M26 warning). |
| Account structure | 20% | Acceptable. 5 campaigns, above the 1 to 3 ideal but each maps to a distinct objective (M11 warning). CBO on ad sets above 100/day (M12 pass). Ad sets all spend above 10/day (M17 pass). |
| Audience and targeting | 20% | Not scored. Overlap, custom-audience freshness, lookalike quality, exclusions, first-party uploads: all UI-only. Verify purchasers are excluded from prospecting. |

### Spend and signal by campaign (30 days, account currency)

| Campaign | Objective | Spend | Custom events | Registrations | Purchases | Purchase value | Lead |
|----------|-----------|-------|---------------|---------------|-----------|----------------|------|
| CBO_Podcasting_US_17.03.26 | Sales | 7,195 | 247 | 65 | 9 | 0 | 0 |
| Remarket_Visitors_WW_Conv_Purchase | Sales | 6,289 | 9,249 | 449 | 648 | 0 | 0 |
| Newsletter_CBO | Sales | 4,488 | 315 | 16 | 0 | 0 | 0 |
| App_iOS_US | App installs | 2,402 | 8 | 93 | 0 | 0 | 0 |
| Brand_Love-Campaign_Engagement | Engagement | 2,035 | 4 | 4 | 0 | 0 | 0 |

Purchase value is 0 on every row and the Lead event is 0 on every row. The remarketing campaign reports 648 purchases with no value, so ROAS cannot be measured anywhere on Meta.

### Frequency and creative detail

| Campaign > ad set | Frequency (30d) | Read |
|-------------------|-----------------|------|
| Remarket > Event_SignedUp | 16.7 | Severe overexposure. Retargeting cap should be under 8 to 12. Improved from 24.5 at last audit but still failing. |
| Remarket > Website-Visitors | 7.2 | Acceptable for retargeting, watch it. |
| Newsletter > US_NewsletterSignup | 4.9 | Prospecting frequency over the 3.0 target (warning). |
| CBO_Podcasting > YouTubeRepurpose | 2.3 | Healthy. |
| App > AppInstalls | 1.5 | Healthy. |
| Brand_Love > Feeds-Reels | 1.1 | Healthy. |

Creative read: the `CBO_Podcasting` ad set runs 8 distinct 9:16 video concepts (Daddi Diesel, Joseph, Start A Podcast) with hook CTRs of 9% to 15%, the strongest creative in the account. The weakness is format: remarketing is static plus one video, Newsletter is image-only, App is image-only, and there is no carousel anywhere. CTR is below 1% on the remarketing Event_SignedUp ad set (0.61%) and the Brand Love campaign (0.25%).

---

## Cross-platform analysis

| Check | Verdict | Detail |
|-------|---------|--------|
| X-PI1 Privacy and signal infrastructure | **Fail (critical)** | Meta purchase value and Lead event dead. Google conversion value absent on ~99% of non-brand spend. Consent Mode v2 status unverified. Neither platform's automated bidding can optimize toward revenue. |
| X-CD1 Creative diversity | Warning (high) | Meta runs only 2 formats with no carousel. Google PMax asset density unverified. |
| X-RF1 Refresh cadence | Not scored | Creative launch dates not exposed via Windsor. Campaign name dates on Meta (21.11, 17.03.26, 27.04.26) suggest some long-running concepts; verify in platform. |

**Budget allocation.** 98.1% of paid spend is Google, 1.9% Meta. Meta's strong podcasting creative (9% to 15% hook CTR) runs on roughly 22K/month. If the Meta value and lead signal were fixed, there may be a case to test more budget there, but that should wait until measurement works.

**Tracking consistency.** The two platforms measure differently. Google tracks conversion volume (mostly without value); Meta tracks a custom event (without value or leads). Neither reports ROAS today. Downstream value lives in HubSpot last-touch plus Omni BI (see `systems/owned/hubspot.md`).

## Strategic recommendations

1. **Fix measurement before scaling anything.** Pass conversion value into Google (value rules or dynamic values per plan tier) and fix the Meta Lead event and purchase value. Until then, every bidding decision on both platforms is blind to revenue.
2. **Cap or cut the high-CPA cluster.** Adding tCPA to, or pausing, the 8 campaigns above 200 CPA addresses 39% of Google spend. Start with US_B2C_Broad (932) and UK_PMax_Podcasting (781). This was the prior audit's top recommendation and is still open.
3. **Plug the search-term leak.** Build themed negative-keyword lists (generic video editing, webinar tools, hardware, off-intent competitors) and apply at account level. Target the broad and DSA campaigns first.
4. **Run a configuration audit in the platform UIs.** This data audit covered the observable subset. Quality Score, Enhanced Conversions, Consent Mode, CAPI and EMQ, negative-keyword lists, RSA and PMax assets, audience exclusions, and landing pages still need a UI pass.

## Data appendix

Raw pulls and scripts saved under `ads-audit-data/`:
- `google_keywords_30d.json` (862 active keywords)
- `google_searchterms_30d.json` (4,390 search terms over 10)
- `analyze.py`, `score.py` (re-runnable analysis and scoring)

Owners: Raz Navon (Head of Paid Acquisition), Dor Druker (Growth Channels Lead). Slack: `#marketing-growth-ppc-team`.
