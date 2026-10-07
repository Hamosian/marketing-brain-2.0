# Referrer Lookup: routine mode

The unattended daily sweep. It finds Nir's "A demo request yesterday named ..." alerts in the partnerships group DM, runs the normal lookup on each one, and saves **one combined Slack draft** in the thread of the first alert. It never sends anything and never asks a question, because nobody is watching.

## Acts when
At least one parent message in `C0C0UNPKMHN` in the lookback window:
- is from Nir Taranto (`U07LETHMPAP`), and
- starts with `A demo request yesterday named`, and
- has **no thread replies** yet. A reply means a person already picked it up.

Anything else logs "No new referrer alerts" and exits. Most runs should end there.

## Lookback window
From the previous scheduled run to now: 1 day on Mon-Thu, 3 days on Sunday (covers Thu after the run, Fri and Sat). The window is the idempotency: a run never looks at an alert an earlier run already covered. The no-replies rule and Slack's one-draft-per-channel limit are the second and third guards, so a re-run on the same day cannot double up.

## Steps
1. Read `C0C0UNPKMHN` for the window. Keep only the alerts that pass **Acts when**. Parse each: referrer name (the words between `named` and `as how they heard`, with a leading "the" dropped: "named the 7 Figure Podcast" is `7 Figure Podcast`), lead name, company, HubSpot record link.
2. Run the self-check below. If it fails, stop as it says.
3. For each alert, run SKILL.md Steps 2-5 (HubSpot, Partnership CRM search set, Slack mentions, verdict). Cap: 8 alerts per run. Beyond that, list the rest by name as "not checked, over the daily cap" at the bottom of the draft.
4. Build **one combined draft** (format below) and save it with `slack_send_message_draft` in `C0C0UNPKMHN`, `thread_ts` = the earliest alert in this run.
5. Print the run summary to the session log: alerts found, verdict per referrer, and whether the draft saved.

## Draft format
Team Slack style, one line per referrer, links as `[label](url)` (the draft tool takes markdown):
```
:mag: Checked today's referrers against the Partnership CRM:
• *Ty Bledsoe* (Bill Fotsch, Economic Engagement): not in the CRM. Came in via Google brand search, so likely word of mouth. [thread](<alert permalink>) · [HubSpot](<record>)
• *7 Figure Podcast* (Barenda Brown, GDMJ Solutions): not in the CRM, but a real referral link from the community my-seven-figure-podcast.mn.co. [thread](<alert permalink>) · [HubSpot](<record>)
_Posted by the Marketing OS agent_
```
A single alert gets the normal one-referrer reply from SKILL.md instead. Run the draft text through the `de-ai` rules before saving.

## Self-check
- **Source breakage:** if reading the channel errors or returns `channel_not_found`, that is the tool down, not an empty day. Stop (see bail-out).
- **Parse check:** if an alert matches the opening phrase but no referrer name, lead or HubSpot link can be parsed, do not guess. Include it in the draft as "could not read this alert, check it by hand" with its thread link.
- **Partial tools:** if HubSpot works but monday does not (or the reverse), still draft, and mark each affected line "CRM not checked" or "HubSpot not checked". A verdict of Unknown needs the monday search set to have actually run.

## Stop / bail-out
- **Slack unreadable:** no draft, log "Slack unreadable, no run", exit. Nothing is written from partial data.
- **Both HubSpot and monday down:** no draft. Log which connector failed and the reconnect steps (plain language, CLAUDE.md failure rule), exit.
- **`draft_already_exists`:** an unsent draft is already sitting in the channel (maybe yesterday's). Never overwrite it. Log the full draft text in the run output with "draft slot taken, copy from here", exit.
- **Never escalate by sending.** No DMs, no posts, no CRM writes, whatever the finding.
- **Unread check:** if the channel draft slot has been blocked by an unsent draft on two consecutive runs, the drafts are going unread. Log "two runs blocked by an unsent draft: is this routine still wanted?" and keep skipping writes until the slot clears.
- **Kill switch:** the schedule. Routine name "Referrer lookup daily sweep" at https://claude.ai/code/routines. Disable it there.

## Cadence
`CRON_TZ=Asia/Jerusalem 45 10 * * 0-4`: Sunday to Thursday at 10:45 Israel time, about 40 minutes after Nir's alerts (they post around 10:07). Daily because inbound demo referrals move daily and the lead already has a sales call booked, so the partner context is only useful before that call. The `CRON_TZ` prefix keeps it at 10:45 local across the IDT/IST switch.

## Done when
Either "No new referrer alerts" is logged, or the combined draft is saved in the first alert's thread (or logged in full with the reason it could not be saved).
