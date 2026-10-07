# Riverside paid ads - quick wins

Critical/High severity, fixable in under 15 minutes. Sorted by severity then speed. Some require in-platform config access.

| # | Platform | Severity | Min | Action | Est. impact |
|--:|---|:--:|--:|---|---|
| 1 | Google | Critical | 5 | Enhanced Conversions status unverified  -  potential 10% conversion measurement uplift unclaimed | ~10% improvement in conversion measurement accuracy; improved Smart Bidding signal quality across all 34 automated campaigns |
| 2 | Google | Critical | 10 | MAXIMIZE_CONVERSIONS without tCPA cap on 4 campaigns running at 3-60x target CPA | $400k-$600k in waste reduction over next 90d if tCPA constrains bidding to peer-level CPA |
| 3 | Google | Critical | 10 | US_B2C_Broad_Desktop: $452k at $592 CPA with 80% rank-lost IS  -  largest single waste source | $429k excess spend identified in 90d period; tCPA cap implementation is a 10-min fix |
| 4 | Google | Critical | 10 | Off-intent search terms active in podcast recording campaigns  -  OBS Studio, voice recorder | $7-10k in direct savings from visible off-intent terms; likely much more in the 83% non-visible spend |
| 5 | LinkedIn | Critical | 10 | Insight Tag firing status requires manual verification | Foundation for all LinkedIn optimization. If broken, all conversion data is invalid. |
| 6 | Microsoft | Critical | 10 | UET tag installation and firing rate requires manual verification | Foundation for all Microsoft Ads optimization. Required before scaling budget. |
| 7 | Google | Critical | 15 | High-performing brand and generic campaigns budget-throttled while poor campaigns run uncapped | Potentially 3-4x more brand conversions for same or lower brand budget; $50-100k incremental efficient conversions per 90d |
| 8 | Google | High | 2 | US_Generic_Webinar_Mobile: $16k at $1,797 CPA with 9 conversions in 90 days | $16k saved in 90d from pause; webinar desktop also warrants tCPA cap review |
| 9 | Google | High | 5 | Openreel competitor campaigns ($8.2k) and US_Competitors_B2B ($6.4k) generating near-zero conversions | $16,500 in 90d from pausing zero/near-zero conversion competitor campaigns |
| 10 | Google | High | 5 | TopGEOs_B2C_Alpha_Mobile: $29k at $416 CPA, 1.1% CVR across 5,985 clicks | $27k in excess spend recoverable in 90d (conv at $57 peer CPA would cost ~$3,900 for same 69 conversions) |
| 11 | Google | High | 5 | WW brand exact campaign throttled at 81%  -  cheapest conversions in the account being rationed | ~20,000 additional brand conversions per 90d at ~$2 CPA; estimated additional spend of ~$38k for $40k equivalent value vs current |
| 12 | Meta | High | 5 | Three campaigns with CTR below 0.50% fail threshold | Pausing OrganicPromotion ($1,467) and redirecting Brand_Love spend ($28,963) to OUTCOME_SALES campaigns could recover 31% of Meta budget currently generating near-zero conversions. |
| 13 | Meta | High | 5 | Campaign-level frequency unmonitored on Brand_Love Engagement campaign | Frequency cap prevents further audience burnout and wasted impressions. Could also reduce CPM by improving ad quality signal to Meta's delivery system. |
| 14 | LinkedIn | High | 5 | US_Webinar InMail campaign: $3,098 spent with 0 clicks and 0 impressions | Confirms $3,098 potential waste. If delivery failed, budget should be reallocated immediately. |
| 15 | LinkedIn | High | 5 | Six zero-conversion campaigns consuming $6,183  -  3x Kill Rule triggered | Stopping $6,183 of zero-return spend. Monthly run-rate ~$2,061 redirected to performing campaigns. |
| 16 | Microsoft | High | 5 | LinkedIn profile targeting status unverified  -  high-value B2B differentiator | 64% CVR improvement on B2B-targeted Microsoft campaigns could reduce CPA from $7.41 to $4.52 on targeted segments  -  further improving already best-in-portfolio efficiency. |
| 17 | Microsoft | High | 5 | Scheduled Google Ads import status unknown  -  risk of silent campaign re-enablement | Prevents unexpected spend events as budget scales. Particularly important before implementing the recommended budget increase. |
| 18 | Google | High | 10 | Manual CPC on brand campaigns generating 30,000 conversions per 90 days | Improved IS capture; estimated 15-25% more brand conversions at similar or lower CPA |
| 19 | Meta | High | 10 | Newsletter_CBO and CBO_Podcasting have unsustainable cost-per-purchase | Newsletter_CBO pause frees $149/day. CBO_Podcasting requires diagnostic before decision. Combined potential recovery: $13,412+ in wasted spend per equivalent future period. |
| 20 | Meta | High | 10 | Purchaser exclusion from prospecting campaigns unverified | Excluding existing customers from prospecting reduces wasted impressions and improves prospecting CPP by ensuring budget reaches only unconverted users. |
| 21 | LinkedIn | High | 10 | No Thought Leader Ads active  -  missing the most cost-efficient LinkedIn format | Shifting $20K/month of standard sponsored content to TLAs could reduce blended CPC from ~$6 to $3, doubling click volume at the same budget. |
| 22 | Microsoft | High | 10 | Microsoft Ads critically underfunded  -  10x below minimum recommended allocation | Scaling Bing from $43K to $200K over 90 days (using $7.41 CPA) projects ~21,000 additional conversions vs ~3,500 from equivalent Google spend at $44 CPA. Net conversion uplift: 17,500 incremental conversions for same $157K reallocation. |
| 23 | Microsoft | High | 10 | Brand campaign syndication control unverified  -  Critical budget waste risk | Protects $12,809 of brand campaign spend from quality degradation. Brand campaigns are the highest-ROAS campaigns in the account  -  preserving their efficiency is critical. |
| 24 | Microsoft | High | 10 | Audience Network status unverified  -  B2B CPA risk if enabled | Disabling Audience Network on non-brand campaigns could reduce CPA by 50-75% on affected campaigns by eliminating low-quality traffic. |
| 25 | Meta | High | 15 | Three campaigns have objective misalignment with business goals | Switching Winback to OUTCOME_SALES should improve purchase volume at equivalent spend. Pausing/redirecting App_iOS_US ($6,806) and Brand_Love ($28,963) to OUTCOME_SALES recovers $35,769 for performance optimization. |
| 26 | LinkedIn | High | 15 | LinkedIn CRM Revenue Attribution not confirmed (HubSpot, June 2025 feature) | Enables true LinkedIn ROI measurement for SLG pipeline. Without it, $93K/quarter of spend has no revenue attribution. |
| 27 | Cross-platform | High | 15 | LinkedIn InMail campaign zero delivery  -  potential EU targeting compliance failure | Recovering $3.1K in wasted LinkedIn budget. More importantly, ensures compliance with LinkedIn's EU Conversation Ad restriction to avoid account-level policy risk. |

## Detail

**1. [Google] Enhanced Conversions status unverified  -  potential 10% conversion measurement uplift unclaimed** (5 min)  
Check Google Ads > Measurement > Conversions > Settings > Enhanced conversions. If not enabled: turn on Enhanced Conversions for web and configure GTM/global site tag to pass hashed user data. Free to implement, 5-minute configuration, ~10% conversion measurement improvement.  
_Evidence: Cannot verify from Windsor export whether Enhanced Conversions (EC) are active. At $3.44M/90d Google spend with 114k tracked conversions, a 10% uplift in conversion signal from EC would meaningfully improve Smart Bidding accuracy across all MAXIMIZE_CONVERSIONS campaigns._

**2. [Google] MAXIMIZE_CONVERSIONS without tCPA cap on 4 campaigns running at 3-60x target CPA** (10 min)  
Add a Target CPA to each MAXIMIZE_CONVERSIONS campaign. Start at 1.5x the best comparable campaign's CPA to avoid restricting delivery, then tighten weekly. For US_B2C_Broad suggest starting tCPA at $45-60 based on peer campaigns (US_Generic_Podcast_Recording: $44, US_Generic_Editing_Clips: $15). Evaluate pausing Webinar Mobile ($1,797 CPA) immediately.  
_Evidence: US_B2C_Broad_Desktop: $452,396 / 764 conv = $592 CPA. US_Generic_Webinar_Desktop: $172,287 / 807 conv = $214 CPA. US_Generic_Webinar_Mobile: $16,172 / 9 conv = $1,797 CPA. TopGEOs_B2C_Alpha_Mobile: $28,610 / 69 conv = $416 CPA. Combined $669k in 90d with no automated CPA ceiling._

**3. [Google] US_B2C_Broad_Desktop: $452k at $592 CPA with 80% rank-lost IS  -  largest single waste source** (10 min)  
Immediate options in priority order: (1) Add tCPA cap at $50 to stop runaway bidding  -  implement today. (2) Audit search terms for off-intent queries that are wasting impressions and depressing QS. (3) If broad match is intentional, ensure STAG (Single Theme Ad Groups) with strong negative lists; current structure suggests loose broad match across too many themes. (4) Consider pausing and restructuring into tighter intent clusters aligned with proven campaigns.  
_Evidence: US_B2C_Broad_Desktop: $452,396 spend, 763 conv, $592 CPA, 0.64% CVR, 79.8% rank-lost IS, 5.0% budget-lost IS. Bidding: MAXIMIZE_CONVERSIONS (no tCPA cap). The 80% rank-lost IS with MAXIMIZE_CONVERSIONS indicates the campaign is bidding but losing almost all auctions  -  the algorithm has insufficient signal to compete effectively. Peer campaign US_Generic_Podcast_Recording achieves $44 CPA at 30.8% CVR on the same intent. Estimated excess spend vs $30 peer CPA: $429k._

**4. [Google] Off-intent search terms active in podcast recording campaigns  -  OBS Studio, voice recorder** (10 min)  
Add negatives immediately: [obs studio], [obs download], [voice recorder], [audio recorder], [free recorder] to the podcast recording campaign and account-level negative lists. Also review full search term report for the 83% of spend that is not visible  -  this level of broad match opacity likely hides significant additional off-intent spend.  
_Evidence: US_Generic_Podcast_Recording_Desktop search terms include: 'obs download' ($585, 8 conv, $73 CPA), 'obs studio download' ($745, 13.5 conv, $55 CPA), 'voice recorder' ($6,610, 309 conv, $21 CPA), 'recording' ($591, 9 conv, $66 CPA), 'podcast' ($551, 4 conv, $138 CPA). 'voice recorder' alone is $6.6k/90d and unlikely to target Riverside's B2B/creator SaaS audience. OBS users are typically free-tool-seekers with very low intent for a paid SaaS product._

**5. [LinkedIn] Insight Tag firing status requires manual verification** (10 min)  
Use LinkedIn Insight Tag Helper browser extension or check Campaign Manager > Account Assets > Insight Tag to verify domain verification and firing status. Confirm firing on homepage, pricing, trial signup, and post-signup confirmation pages.  
_Evidence: Windsor provides metrics only; Insight Tag installation and firing rate cannot be confirmed. If the tag is not firing on all pages, conversion tracking, retargeting pool builds, and demographic data are all compromised._

**6. [Microsoft] UET tag installation and firing rate requires manual verification** (10 min)  
Install Microsoft Clarity + UET Helper extension. In Microsoft Ads, check Tools > UET Tag and verify 'Active' status and no error flags. Confirm firing on homepage, pricing, trial start, and post-signup pages.  
_Evidence: Windsor provides campaign metrics only. Universal Event Tracking (UET) tag status, firing rate, and page coverage cannot be confirmed. Without a fully firing UET tag, conversion data is incomplete and Smart Bidding algorithms are operating on partial signal._

**7. [Google] High-performing brand and generic campaigns budget-throttled while poor campaigns run uncapped** (15 min)  
Reallocate budget immediately: increase brand WW desktop budget to capture the 81% of missed auctions (cheap brand conversions at $2 CPA). Increase US_Generic_Streaming and Editing_Clips budgets. Offset by adding tCPA caps or pausing underperformers. Brand budget increase of $10-15k/mo should be ROI-positive given $2 CPA.  
_Evidence: google_search_ww_desktop_brand_exact: 81.2% budget-lost IS, $2.35 CPA, 18.6% CVR  -  losing 4 out of 5 auctions due to budget cap. US_Generic_Streaming_Desktop: 55.5% budget-lost IS, $15 CPA, 33.1% CVR. US_Generic_Editing_Clips_Desktop: 27.3% budget-lost IS, $15 CPA, 33.0% CVR. Simultaneously, US_B2C_Broad_Desktop runs $452k at $592 CPA with no cap. Budget is flowing to the wrong campaigns._

**8. [Google] US_Generic_Webinar_Mobile: $16k at $1,797 CPA with 9 conversions in 90 days** (2 min)  
Pause the mobile webinar campaign immediately. Root cause is likely a non-mobile-optimized webinar landing page. Before re-enabling: (1) verify mobile LCP <2.5s on webinar landing page, (2) test mobile conversion flow, (3) reconsider if webinar signups should be served on mobile at all. Also evaluate whether desktop webinar at $214 CPA is justified given B2B SaaS benchmarks  -  this may require HubSpot/Omni data to assess lead quality.  
_Evidence: US_Generic_Webinar_Mobile: $16,172 spend, 993 clicks, 9 conversions, $1,797 CPA, 0.91% CVR, 37.2% rank-lost IS. Desktop counterpart US_Generic_Webinar_Desktop: $172,287, $214 CPA (also high but 8x more efficient than mobile). Webinar content likely has poor mobile experience or the landing page fails on mobile._

**9. [Google] Openreel competitor campaigns ($8.2k) and US_Competitors_B2B ($6.4k) generating near-zero conversions** (5 min)  
Pause all Openreel competitor campaigns immediately (OpenReel is a niche enterprise product; Riverside's PLG audience is unlikely to be searching for it as a consideration-stage competitor). Pause US_Competitors_B2B_Desktop or restructure with tCPA targeting the B2B demo-booking conversion specifically. Combined saves $16k+ in 90d.  
_Evidence: US_Competitors_Openreel_Desktop: $6,677, 343 clicks, 0 conversions. CAUKAU_Competitors_Openreel_Desktop: $1,494, 97 clicks, 0 conversions. ROW_Competitors_Openreel_Desktop: $2,460, 334 clicks, 1 conversion ($2,460 CPA). DE_Competitors_Openreel: $75, 0 conv. US_Competitors_B2B_Desktop: $6,367, 306 clicks, 3 conversions ($2,122 CPA). All running TARGET_SPEND (Openreel) or MAXIMIZE_CONVERSIONS (B2B) with no conversion data to optimize against._

**10. [Google] TopGEOs_B2C_Alpha_Mobile: $29k at $416 CPA, 1.1% CVR across 5,985 clicks** (5 min)  
Pause mobile alpha or add aggressive bid adjustment to drastically reduce mobile bids (-80% to -90%). Investigate mobile landing page conversion flow  -  Riverside's app may require desktop for signup. If mobile is purely top-of-funnel, reframe the conversion action for mobile behavior.  
_Evidence: TopGEOs_B2C_Alpha_Mobile: $28,610, 5,985 clicks, 68.8 conversions, $416 CPA, 1.15% CVR. Desktop equivalent CAUKAU_B2C_Alpha_Desktop: $178,590, $57 CPA, 21.1% CVR. Mobile CVR is 19x lower than desktop for the same audience, suggesting mobile landing page failure or the conversion action is not mobile-optimized._

**11. [Google] WW brand exact campaign throttled at 81%  -  cheapest conversions in the account being rationed** (5 min)  
Increase daily budget for WW brand desktop. Set budget to capture 90-95% impression share (estimate: 5-6x current daily budget). This is the highest ROI budget change available  -  $2 CPA conversions are being turned away. Monitor for 7 days and adjust.  
_Evidence: google_search_ww_desktop_brand_exact: 81.2% budget-lost IS, $8,961 spend in 90d, $2.35 CPA, 18.6% CVR. If IS were 100%, estimated spend would be $47k/90d for ~20k additional conversions at $2 CPA. This campaign is capturing only 14.6% of available impressions._

**12. [Meta] Three campaigns with CTR below 0.50% fail threshold** (5 min)  
Brand_Love: Either introduce direct-response creative with strong CTAs or pause and redirect budget to performance campaigns (see kill_list). OrganicPromotion: Pause immediately - BELOW_AVERAGE_35 quality ranking means Meta's own system rates this in the bottom 35% of competing ads. B2C-to-B2B: Test new creative angles; current CTR suggests the ad concept is not resonating with the target audience.  
_Evidence: Brand_Love-Campaign_Engagement: CTR 0.40% (fail threshold <0.50%), $28,963 spend. OrganicPromotion_Awareness: CTR 0.12%, $1,467 spend, quality_ranking BELOW_AVERAGE_35. B2C-to-B2B_LeadGeneration: CTR 0.44%, $3,046 spend. Meta Traffic objective benchmark CTR is 1.71%; these campaigns are at 23%, 7%, and 26% of benchmark respectively._

**13. [Meta] Campaign-level frequency unmonitored on Brand_Love Engagement campaign** (5 min)  
If Brand_Love is retained, implement a frequency cap of 3-4 per week at campaign level. Review audience definition - if this is a broad prospecting audience, the 0.40% CTR suggests creative or audience mismatch. Consider reach and frequency buying type with explicit frequency cap instead of auction.  
_Evidence: Brand_Love-Campaign_Engagement: 4,593,094 impressions on $28,963 spend. CPM $6.31 suggests broad audience but CTR of 0.40% (vs 1.71% benchmark) indicates audience rejection/fatigue rather than organic resonance. 18,397 clicks on 4.59M impressions = users are seeing and ignoring the ad. No frequency cap evidence in campaign configuration._

**14. [LinkedIn] US_Webinar InMail campaign: $3,098 spent with 0 clicks and 0 impressions** (5 min)  
Immediately open LinkedIn Campaign Manager and check this campaign's delivery status. If it ran and LinkedIn is showing impressions, the Windsor connector has a gap for InMail impression reporting. If it shows 0 impressions in LinkedIn UI, pause immediately and investigate audience eligibility (EU Sponsored Messaging ban, audience size below 300 minimum, or targeting mismatch).  
_Evidence: campaign: 'US_Webinar_UpsellAudience_InMail_Conversation', spend: $3,098.14, clicks: 0, impressions: 0, ctr: null. This is either a delivery failure (audience too narrow, EU compliance issue, or paused mid-flight) or a Windsor/reporting gap._

**15. [LinkedIn] Six zero-conversion campaigns consuming $6,183  -  3x Kill Rule triggered** (5 min)  
Pause all six campaigns immediately. For winback campaigns, audit audience match rate in Campaign Manager before relaunching. For webinar campaigns, verify the webinar is still live and landing page is functional. For InMail, investigate delivery failure before any relaunch.  
_Evidence: WW_Winback_UseCases ($645, 0 conv), US_Podcasting-Marketing_SingleImage_20.05.26 ($1,000, 0 conv), WW_Winback_Fomo ($634, 0 conv), WW_Winback_AllInOne ($304, 0 conv), US_Marketers_Webinars_SingleImage_13.04.26 ($500, 0 conv), US_Webinar_UpsellAudience_InMail_Conversation ($3,098, 0 conv/clicks/impressions). All exceed $300 spend with zero conversions. 3x Kill Rule applies (spend > 3x target CPA, 0 conversions)._

**16. [Microsoft] LinkedIn profile targeting status unverified  -  high-value B2B differentiator** (5 min)  
In Microsoft Ads, navigate to campaign > Audiences > Add audience > LinkedIn Profile. Apply to brand and competitor campaigns in Observation mode first (bid-only, no exclusion). Monitor CTR and CVR lift over 2 weeks. If lift confirmed, apply to generic podcast campaigns in Targeting mode.  
_Evidence: LinkedIn profile targeting on Microsoft Ads delivers 16% greater CTR and 64% greater CVR than non-audience-targeted ads. CPCs are 30-70% cheaper than LinkedIn direct. This is especially relevant for Riverside.fm's SLG enterprise segment targeting podcast creators, marketers, and media producers  -  all job functions available in Microsoft's LinkedIn audience dimensions (148 industries, 26 job functions, 80,000+ companies)._

**17. [Microsoft] Scheduled Google Ads import status unknown  -  risk of silent campaign re-enablement** (5 min)  
In Microsoft Ads, navigate to Import > Google Ads Import > Scheduled Imports. Disable any active scheduled imports. Switch to manual import-on-demand only. Document which campaigns were imported vs created natively.  
_Evidence: Windsor cannot reveal whether scheduled auto-imports are active. Scheduled imports are a common source of billing surprises: they can re-enable paused campaigns, overwrite manual bid/budget changes, and reset conversion goals. This risk scales significantly if Bing budget is increased._

**18. [Google] Manual CPC on brand campaigns generating 30,000 conversions per 90 days** (10 min)  
Migrate brand campaigns to MAXIMIZE_CONVERSIONS or tCPA. Recommended: set tCPA at $5-8 for brand campaigns (2-3x current $2.40 CPA to avoid restricting delivery). Test one brand campaign first, monitor for 2 weeks, then roll out. This will also allow the algorithm to manage budget more efficiently and reduce the 81% budget-lost IS.  
_Evidence: google_search_us_desktop_brand_exact: MANUAL_CPC, 23,866 conv/90d, $2.43 CPA. google_search_ww_desktop_brand_exact: MANUAL_CPC, 3,813 conv/90d, $2.35 CPA. google_search_ww_mobile_brand_exact: MANUAL_CPC, 2,183 conv/90d, $0.66 CPA. Threshold for automated bidding is 15 conversions/month; these campaigns are 500x above threshold. Manual CPC is also contributing to the 81% budget-lost IS on WW desktop  -  the algorithm cannot dynamically allocate bids to capture all available impression share._

**19. [Meta] Newsletter_CBO and CBO_Podcasting have unsustainable cost-per-purchase** (10 min)  
Newsletter_CBO: Define the economic model for newsletter subscribers. If newsletter-to-paid CVR is not measured and tracked, this campaign has no defensible ROI. Pause until newsletter attribution is established. CBO_Podcasting: Audit audience targeting - $20.64 CPM suggests broad reach but 5.59% CTR (anomalously high) with only 68 purchases over $25K suggests click quality issue (possibly low-intent broad match). Check if LINK_CLICKS or engagement is being miscounted as conversion.  
_Evidence: Newsletter_CBO: $13,412 spend, 4 purchases = $3,353 CPP. 1,214 custom conversions at $11.05 each - likely newsletter signups, not commercial intent. CBO_Podcasting_US: $25,641 spend, 68 purchases = $377 CPP. For a SaaS trial-to-paid funnel, a $377 CPP only makes economic sense if LTV is very high and paid conversion rate from trial is very low. Registration CPA account-wide is $45.75, making these outliers._

**20. [Meta] Purchaser exclusion from prospecting campaigns unverified** (10 min)  
Create a Custom Audience of all purchasers (pixel-based, 180-day window) and CRM customer list upload. Exclude from all OUTCOME_SALES prospecting campaigns. This is a 10-minute fix in Ads Manager with immediate budget efficiency improvement.  
_Evidence: Cannot confirm from Windsor data whether existing customers/purchasers are excluded from CBO_Podcasting_US ($25,641) or B2C-to-B2B_LeadGeneration ($3,046) prospecting campaigns. With 2,342 purchases in the account over 90 days and no visible exclusion audience data, there is meaningful risk of re-advertising to existing paid users._

**21. [LinkedIn] No Thought Leader Ads active  -  missing the most cost-efficient LinkedIn format** (10 min)  
Create TLAs from existing employee or customer LinkedIn posts. Allocate ≥30% of brand content budget to TLAs. For Riverside.fm, leverage podcast creator or customer testimonials as TLA source content.  
_Evidence: Zero campaigns use TLA campaign type. TLAs deliver $2.29-4.14 CPC vs $13.23 for standard ads (3-5x cheaper). Multiple brand awareness campaigns with CPCs of $9.44-$19.71 could be replaced or supplemented with TLAs. TLAs expanded to non-employee members in March 2025, enabling customer testimonial UGC._

**22. [Microsoft] Microsoft Ads critically underfunded  -  10x below minimum recommended allocation** (10 min)  
Increase Bing budget incrementally using the 20% Rule: first increase to $60K/90 days, evaluate CPA stability over 2 weeks, then escalate toward $120K, $200K, $400K in stages. Fund increases by reallocating from Google campaigns with CPA >3x target (especially Google Video $115/conv and Google PMax $65/conv). Monitor Bing CPA for diminishing returns signals  -  the channel likely saturates before $400K but has significant headroom.  
_Evidence: Bing spend: $43,051 (90 days). Google total: $3,444,660 (1.25% ratio). Google search alone: $2,394,530. Microsoft guidance: Bing = 20-30% of Google. Minimum recommended Bing budget: $478,906/90 days. Actual: $43,051  -  9% of minimum. Bing CPA: $7.41. Google estimated CPA: ~$44. The channel delivers 5.9x more conversions per dollar spent._

**23. [Microsoft] Brand campaign syndication control unverified  -  Critical budget waste risk** (10 min)  
In Microsoft Ads, check campaign settings > Networks for both brand campaigns. Ensure 'Microsoft sites, apps, and select traffic' only (exclude Audience Network). Run a Publisher URL report for syndicated partners and exclude any site with >$5 spend and 0 conversions.  
_Evidence: bing_search_us_desktop_brand_exact ($7,401) and bing_search_ww_desktop_brand_exact ($5,408) are Riverside's lowest CPA campaigns ($2.43 and $3.61). If these are running on the Microsoft Audience Network or low-quality syndicated partners without exclusions, brand CPA will inflate and impression quality will drop. Windsor cannot confirm partner network settings._

**24. [Microsoft] Audience Network status unverified  -  B2B CPA risk if enabled** (10 min)  
Check each campaign's network settings. For performance campaigns (competitors, generic), disable Audience Network. If Audience Network is enabled for testing, set a separate campaign to isolate its performance, run publisher URL reports weekly, and build an exclusion list.  
_Evidence: Microsoft Audience Network is enabled by default on all campaigns. B2B advertisers (Seer Interactive data) see CPA 2-4x higher from Audience Network than search alone. Riverside.fm is B2B SaaS. If Audience Network is ON across all 9 campaigns, it is likely inflating CPAs on generic and competitor campaigns._

**25. [Meta] Three campaigns have objective misalignment with business goals** (15 min)  
Winback: Change objective to OUTCOME_SALES with Purchase optimization. App_iOS_US: Evaluate whether mobile app is a strategic priority; if yes, move to dedicated app campaign account; if no, pause. Brand_Love: Either define a measurable brand KPI (CPM, reach frequency) with a capped budget, or convert to OUTCOME_SALES with brand awareness creative and measure halo effect via incrementality test.  
_Evidence: 1) Winback_Traffic_WW_24.03.26: LINK_CLICKS objective, $4,451 spend, 53 purchases - a winback campaign should use OUTCOME_SALES to optimize for purchases, not clicks. 2) App_iOS_US: APP_INSTALLS objective, $6,806 spend, 0 purchases - app install objective inside a web conversion account; Riverside's primary product is web-based, making this objective questionable. 3) Brand_Love-Campaign_Engagement: OUTCOME_ENGAGEMENT, $28,963 spend, 1 purchase, 6 custom conversions - engagement objective at this scale generates social metrics, not business outcomes._

**26. [LinkedIn] LinkedIn CRM Revenue Attribution not confirmed (HubSpot, June 2025 feature)** (15 min)  
In LinkedIn Campaign Manager, go to Account Assets > Integrations and verify HubSpot connection. If not active, connect HubSpot CRM to enable closed-loop reporting from LinkedIn ad impressions to HubSpot contacts, deals, and revenue.  
_Evidence: LinkedIn launched closed-loop CRM integration with Salesforce/HubSpot in June 2025, enabling impression-to-revenue attribution. Riverside uses HubSpot (account ID 9154210). Windsor cannot verify if this integration is active. Without it, LinkedIn ROI is unmeasurable beyond post-view Share Conversions._

**27. [Cross-platform] LinkedIn InMail campaign zero delivery  -  potential EU targeting compliance failure** (15 min)  
1. Open LinkedIn Campaign Manager  -  check campaign status, ad review status, and audience definition. 2. If audience includes EU/EEA members, the campaign will fail delivery for those segments per ePrivacy Directive rules. Replace with Sponsored Content or Lead Gen Form targeting the same audience. 3. If audience is non-EU, investigate ad review rejection or audience size floor (<300 members = no delivery).  
_Evidence: US_Webinar_UpsellAudience_InMail_Conversation: 0 impressions, 0 clicks, 0 conversions, $3,098 spend. Zero delivery with non-zero spend may indicate budget consumed without ad serving, or budget allocated but paused. LinkedIn Message/Conversation Ads cannot deliver to EU members since January 2022._
