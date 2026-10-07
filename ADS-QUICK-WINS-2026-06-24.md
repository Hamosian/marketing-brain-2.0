# Ads quick wins: Google and Meta (30-day refresh)

Date: 2026-06-24
Companion to `ADS-AUDIT-REPORT-2026-06-24.md`

Criteria: severity Critical or High, and fix time under 15 minutes. Sorted by severity then estimated impact. Figures are in account currency and directional until FX is confirmed.

| Rank | Fix | Platform | Severity | Time | Why it matters |
|------|-----|----------|----------|------|----------------|
| 1 | Add a Target CPA cap to `US_B2C_Broad_Desktop` (start 60 to 90), or pause it | Google | Critical | 10 min | Largest line item, 172,512/30d at 932 CPA versus 20 to 70 peers. Flagged 10 days ago and now worse. Single biggest lever in the account |
| 2 | Add negative keywords for the top zero-conversion search terms | Google | Critical | 10 min | Addresses the 102,445/30d search-term leak. Start with "video editor", "webinar", "webinarjam", "teleprompter online", "opus clip", "apple podcast connect", "gotowebinar" |
| 3 | Add tCPA caps to the other uncapped high-CPA campaigns | Google | Critical | 15 min | UK_PMax_Podcasting (781), US_PMax_DescriptEditing (409), US_PMax_Podcasting_Clean (510). Part of the 457,686/30d high-CPA cluster |
| 4 | Pause `UK_PMax_Podcasting_Desktop` and `US_PMax_Podcasting_Desktop_Clean` | Google | High | 2 min | 781 and 510 CPA at 19% and 27% IS, low volume. Stop the bleed immediately |
| 5 | Switch Target Spend competitor and retargeting campaigns to Maximize Conversions | Google | High | 5 min each | Openreel campaigns and WW_DSA_Retargeting maximize clicks, not conversions, despite tracking conversions |
| 6 | Add a frequency cap (8 to 12) on Meta Remarket > Event_SignedUp | Meta | High | 10 min | Frequency 16.7 with 0.61% CTR. Audience exhaustion burning remarketing budget |
| 7 | Confirm Enhanced Conversions is enabled and verified | Google | High | 5 min | Free, ~10% measurement uplift, improves Smart Bidding across all automated campaigns. Just needs a settings check |

## Not quick wins, but highest value (need more time or developer work)

These are critical but do not fit the under-15-minute bar. They belong at the top of the action plan.

- Fix the Meta website Lead event (firing 0). Developer task.
- Pass purchase value into the Meta pixel and CAPI (0 across all campaigns). Developer task.
- Add conversion value to Google non-brand campaigns (value rules or per-plan-tier dynamic values). 1 to 2 hours.

Until these three land, both platforms are optimizing without a revenue signal, which caps the value of every quick win above.
