---
name: moon-at-dawn-weekly-report
description: Weekly automation that posts the Moon at Dawn agency's full-funnel creator report to the shared moonatdawn-riverside Slack channel every Monday. For every live post by a Moon at Dawn creator it shows engagement, visitors, sign-ups, trials, paid, B2B leads, MQL, SQL and won, with week-over-week growth in % and totals since launch. Reads the Partnership CRM monday boards (Agencies, Deliverables), Snowflake (web visits, self-serve funnel, HubSpot contacts, SQLs, deals) and posts one channel message plus a per-post thread reply. Runs Mondays as a cloud routine, or on demand. Trigger phrases - "moon at dawn report", "run the moon at dawn report", "agency weekly funnel", "how are moon at dawn creators doing", "moon at dawn full funnel", "/moon-at-dawn-weekly-report".
---

# Moon at Dawn weekly funnel

Every Monday, one post in `#moonatdawn-riverside` (`C0ASHCWEHGA`) tells the agency how their creators' posts performed, from the post to revenue. A thread reply under it carries the full funnel for every live post since launch.

**The channel is shared with the agency** (Will Beech and team, `moonatdawn.com`). Everything posted there is read by people outside Riverside. The report carries aggregate counts only: never contact names, emails, company names, deal amounts, creator fees or cost per view.

Owner: Savion Ron Shemesh (Head of Creator Marketing, `U09340B5HCM`). Format approved by Savion on 2026-09-28.

## What this skill does not do

- **Report on other agencies or creators.** Only creators linked to the Moon at Dawn item on the Agencies board.
- **Edit the monday boards.** It reads them. Wrong post dates or statuses go to Savion in the internal note, never fixed here.
- **Rewrite the template.** The message layout is fixed (`knowledge/render.py`). Changing it is a PR, approved by Savion.

## Acts when

Every scheduled Monday run posts, including a quiet week: a week of zeros is still the report the agency expects. It does **not** post when the self-check fails or when this week's report is already in the channel.

## Steps

1. **Set the dates** (UTC). `week_end` = yesterday (Sunday). `wk_start` = the Monday before it. `prev_start` = `wk_start` minus 7 days. `end` = today. `start` = `2025-09-28` (the one-off 12-month view; Moon at Dawn's first post went live 2026-05-28, so it is also "since launch").
2. **Idempotency check.** Read the last 20 messages in `C0ASHCWEHGA`. If one already starts with `:crescent_moon: *Moon at Dawn x Riverside` and names this week's date range, stop: it was posted.
3. **Roster.** Read the Moon at Dawn item on the Agencies board (`knowledge/creators.md` has the IDs). If a linked creator is not in the slug list in `knowledge/funnel.sql`, add their slug for this run (full name, lowercased, spaces and accents removed) and flag it in the internal note.
4. **Live posts from the board.** Read the Deliverables board filtered to the roster's Creator ids, with status, Post Date, Engagement (%) and name. Keep status `Posted` or `Results`. Drop reposts (item name contains "repost").
5. **Run `knowledge/funnel.sql`** with the four dates substituted. If Snowflake times out, re-run once. It already has the prefilters that made the 12-month window finish.
6. **Apply the live-post rule** to the query rows, per creator:
   - sort the creator's link months (`mth`) by first visit;
   - the Nth month is live only if the creator has at least N live board posts (step 4);
   - a month that is not live is a pre-launch click (usually the team reviewing a draft link). Exclude it and list it in the internal note.
   - engagement for the Nth live month = the Engagement (%) of the creator's Nth live board post by Post Date; if that creator has more live posts than link months, the extra posts share the last link and the value is their average; `-` when none is logged.
7. **Self-check** (below). If it fails, do not post to the agency; send the internal note and stop.
8. **Render** with `python3 knowledge/render.py rows.json --week-start <wk_start> --week-end <week_end> --since 2026-05-28 --asof <week_end> --exclude excluded.json --eng eng.json`. Output is message 1, a `=====THREAD=====` line, then message 2.
9. **Post** message 1 to `C0ASHCWEHGA`, then message 2 as a reply in its thread (`thread_ts` from the first post). Both keep the `_Posted by the Marketing OS agent_` footer.
10. **Internal note** to Savion by DM, only when there is something to fix: pre-launch clicks, new creators without a slug, live posts whose board Post Date is in the future, links with a misspelt UTM. Three to six lines, written with `/ste`, each line one thing to fix.

The template is fixed and approved, and every line in it is a number, so the `/de-ai` and `/critique` stages have nothing to change. They apply to the internal note like any other message.

## How each stage is measured

| Stage | Source | Rule |
|-------|--------|------|
| Posts live | Deliverables board | Posted or Results, reposts excluded |
| Eng% | Deliverables board | Engagement (%), mapped per step 6 |
| Visitors | `TRF.INT_SEGMENT__PAGES_UNIONED` | unique `ANONYMOUS_ID` whose page URL carried the creator's `utm_campaign` with `utm_medium=creator`. Filter on `ORIGINAL_UTM_*`, not `UTM_*` (the visits tables backfill UTMs from the referrer, `systems/owned/omni-bi.md`) |
| Sign-ups, trials | `BI.MARKETING_FUNNEL_ANALYSIS` | by `UTM_CAMPAIGN`, anchored on sign-up date |
| Paid | `BI.MARKETING_FUNNEL_ANALYSIS` | anyone reached through the post (sign-up or HubSpot lead, matched on email) with a subscription |
| Leads, MQL, SQL | `TRF.HUBSPOT__CONTACTS` | UTM read from First Page Seen (`HS_FIRST_URL`); the contact `utm_campaign` field is usually empty. Internal domains excluded |
| Won | `FS.SQLS` then `FS.DEALS` | `IS_WON` on deals linked to the lead's SQL |

A post is creator + link month: every link carries `utm_term` like `aug2026`, so one creator's posts separate by month. Two posts sharing one link (Andrew Tindall's two June posts) are one row. Totals add up the post rows, so a person who reached Riverside through two posts counts once per post; the unique-person figure is about 10% lower.

Growth is this week against the week before, per stage. `new` when last week was zero, `flat` when both are equal.

## Self-check

Do not post if any of these holds; send the internal note instead:
- `MAX(SIGN_UP_AT)` in `MARKETING_FUNNEL_ANALYSIS` is before `week_end`, or `MAX(CREATED_AT)` in `HUBSPOT__CONTACTS` is before `week_end` (the warehouse has run up to 31 hours behind).
- Site-wide pageviews with `ORIGINAL_UTM_MEDIUM = 'creator'` last week are zero. That is broken tracking, not a bad week.
- The monday read failed or returned no live posts. Without the board, the pre-launch rule cannot run.

## Constraints (unattended)

- Idempotent via step 2. Re-running never double-posts.
- A new creator without a slug still gets counted (step 3); no question to anyone.
- Glitch (timeout): retry once. Tool down (monday, Snowflake, Slack): no agency post, internal note naming what was down. Empty week: post it. Wrong-looking number (a stage larger than the one before it, other than Paid): post, and flag it in the internal note.
- Never post contact-level data to the shared channel.

## Stop / bail-out

- Source stale or down: "no report this week, data not ready" goes to Savion only. Never post partial numbers to the agency.
- Kill switch: the routine "Moon at Dawn weekly funnel" at https://claude.ai/code/routines. Disable it when the agency contract ends.
- If the agency asks for different stages or a different cut in the channel, do not change the template on the fly. Tell Savion.

## Cadence

Mondays at 08:52 Europe/London (`CRON_TZ=Europe/London 52 8 * * 1`), the start of the agency's working week. The data moves weekly: a LinkedIn post's clicks land in its first week, and the B2B stages move over weeks, so a daily post would be mostly zeros. Runs as a cloud routine that starts a fresh session each Monday.

## Done when

Message 1 and its thread reply are in `C0ASHCWEHGA` for this week, and the internal note went to Savion if anything needed fixing. Or: the self-check failed, nothing was posted to the agency, and Savion has the note saying why.

## Knowledge

- `knowledge/creators.md`: board and item IDs, the slug aliases (misspelt UTMs), and known data quirks.
- `knowledge/funnel.sql`: the one query, one row per post.
- `knowledge/render.py`: the fixed Slack template.
