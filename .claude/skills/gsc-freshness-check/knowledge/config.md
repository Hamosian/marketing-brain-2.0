# gsc-freshness-check - config

Every ID, threshold and recipient the skill needs. Change them here, not in `SKILL.md`.

## Sources

| Source | Connector / system | Identifier |
|--------|--------------------|------------|
| GSC | Windsor.ai MCP, `searchconsole` connector | `sc-domain:riverside.com` |
| Warehouse | Snowflake MCP | `marketing_rollover` |

**Windsor is the only GSC source, here and in every other skill.** Ahrefs' GSC endpoints were the second route until 2026-09-15 and were removed: they have returned nothing since 14 Aug 2026 while Google itself has served every day, so the route contributed a permanent false stale signal and, worse, a false diagnosis (see Known history). Ahrefs remains in use for Rank Tracker, Site Explorer and backlinks - this applies to Search Console data only.

**The exact call.** `get_data` on connector `searchconsole` with fields `["date","search_type","clicks","impressions"]` and filter `search_type = web`; read the newest `date` in the response.

**Never pull `["date","clicks","impressions"]` without a dimension.** A date-only pull returns collapsed multi-day buckets, or an empty array with no error, so a perfectly healthy property reads as a total outage. Any real dimension (`search_type`, `device`, `page`, `query`) restores correct daily rows. Full detail: safeguard #13 in `../../organic-dashboard/knowledge/safeguards-and-gotchas.md`.

## Thresholds

| Check | Stale when | Basis |
|-------|-----------|-------|
| GSC | newest date < today − 4 days | GSC's own ~2-day lag plus a day of slack. Matches the gate in `/weekly-seo-report` - change both together or they disagree |
| Snowflake | newest date < today − 2 days | Same gate as `/weekly-seo-report` |

Resolve "today" in **Europe/London**, explicitly.

## Recipients

| | Slack ID | When |
|---|---|---|
| Erika Varangouli | `U06R47T4ASJ` | Every stale result |
| Amir Bar-Tikva | `U0B3NM80M1N` | Optional. Off by default - he owns the weekly report, so add him once the routine has run clean for a fortnight |

Silent on green. No DM at all.

## Known history

| Date | Event |
|------|-------|
| 2026-08-14 | Last day of GSC data on both routes. Cause recorded at the time as the Google property authorisation. **This was wrong** - see 2026-09-15 |
| 2026-09-10 | Amir flags "an issue with windsor... from sep 1st" in `#seo-reports`. Real break was 14 Aug, three weeks earlier |
| 2026-09-11 | Verified via Ahrefs - data present through 14 Aug, nothing after. Skill built |
| 2026-09-15 | Windsor found serving complete daily data through 12 Sep; Ahrefs still dark. Amir exported 1 Aug - 12 Sep straight from the Search Console UI (Search type = Web): **all 43 days match Windsor exactly**, 274,139 clicks / 14,273,628 impressions on both sides, zero difference on any single day, and position agrees on every day checked. Google never stopped and the property grant was never the problem. Ahrefs route removed |
| 2026-09-15 | Separately, the date-only Windsor pull found to collapse days into buckets (1 Nov 2025 - 9 Aug 2026 as monthly lumps; 1-5 Sep 2026 as one lump with 5 Sep double-counted) and to return an empty array for a sub-bucket window. Underlying data unaffected. See safeguard #13 |

## Related

- `/weekly-seo-report` - the weekly report this protects. Its Step 0 is the freshness gate and Step 1 the GSC pull; that gate is the one that did not surface.
- `/organic-dashboard` - the monthly retrospective, same GSC dependency.
- `.claude/skills/organic-dashboard/knowledge/safeguards-and-gotchas.md` - the Windsor quirks (brand flag, numeric-filter truncation, apex hostname) that make a source swap a real piece of work rather than a config change.
