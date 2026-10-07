---
name: referrer-lookup
description: Use this skill to check whether one named referrer (a show, podcast, creator, community or person a lead credited) is already a Riverside partner. Reads that contact's HubSpot referral source, searches the Partnership CRM on monday (Creators and Partnership Management boards), and returns a known / past / unknown verdict with the next step, plus a reply saved as a Slack draft in the thread (never sent). Triggered by a pasted partnerships post that names a referrer, a Slack link to one in the partnerships group DM, "check in our CRM", "do we work with X", "a lead said X is how they found us", "is X a partner", "is X in the partnership CRM", "who referred this lead", "run the referrer sweep", or "/referrer-lookup". Also runs Sun-Thu 10:45 Israel time as a cloud routine that sweeps new referrer alerts into one combined draft. NOT the daily demo report, HDYHAU listing or outreach drafting (inbound-demo-reply), and never creates CRM entries.
---

# Referrer Lookup

Turns a "this lead named X as their source" post into an answer Creator Marketing can act on: is X a partner we already track, one we turned down, or someone new sending us business. The finished output is a short verdict in chat and one reply saved as a Slack draft in the thread, for the user to edit and send.

## Inputs and context to load
- The trigger: a Slack permalink (usually the partnerships group DM), pasted post text, or a bare referrer name.
- `knowledge/config.md` for the board IDs, column keys and match rules. Load it at Step 3.
- `inbound-demo-reply` Step 3 (the "named person or named show" rule) only if you need to know why these posts exist.

## Steps
1. **Read the source.** For a Slack link, read the thread (parent and replies). Pull out: the referrer name verbatim, the lead's name, company, and HubSpot contact link. If a reply in the thread already answers the question, stop and say so; do not re-answer a settled thread.
2. **Read HubSpot.** Fetch the contact with the properties listed in `knowledge/config.md`. The referral domain (`hs_analytics_source_data_1` when `hs_analytics_source` is `REFERRALS`) is the strongest evidence: it names the actual site that sent the lead, which is often not what the form answer says. Note the owner, lifecycle stage and whether a meeting is booked.
3. **Search the Partnership CRM.** Run every search in `knowledge/config.md` (name variants, digit and word forms, the referral domain against the link columns) on the Creators board, then a workspace-wide item search. Board search is fuzzy: open every candidate and confirm it is the same entity before counting it as a match. A shared word ("seven", "figure", "podcast") is not a match.
4. **Check prior Slack mentions.** One Slack search on the referrer name, to catch a partner discussed but never entered on the board.
5. **Classify** using the verdict table below, then produce the output.
6. **Save the reply as a draft in the thread.** Always, with no confirmation step: create it with the Slack draft tool (`slack_send_message_draft`) on the source channel with `thread_ts` set to the parent message (standing rule per Savion, 2026-09-27). Never send it, even if asked in passing; the user sends it from Slack. If Slack returns `draft_already_exists` (one draft per channel), do not overwrite: show the draft text in chat and say an existing draft in that channel is blocking it. With no Slack thread (a bare name was given), show the draft in chat only.

## Verdicts
| Verdict | When |
|---------|------|
| Known partner | A confirmed Creators or Partnership Management item for this entity, status not "Not interested" / "Don't reach out" |
| Past or declined | A confirmed item marked "Not interested", "Don't reach out", or in Inactive Contacts |
| Unknown | No confirmed item after every search in `knowledge/config.md` |
| Unclear | A candidate that might be the same entity but you cannot confirm it. Name it and say why it is uncertain; never round it up to Known |

## Constraints
- Ground every claim in what the tools returned. Do not guess who runs a show or community, and do not research the referrer on the open web beyond one fetch of the referral domain. If that fetch is blocked, say the page could not be opened and leave the host as "not confirmed".
- Read-only on HubSpot and monday. This skill never creates or edits a CRM item; if the user wants an entry, say which fields it would need and hand off.
- The only write is the Slack draft in the thread. Never send a message, and never create a top-level draft.
- If the monday connector fails or asks for auth, try the other monday connector if one is connected; if neither works, report the HubSpot half and give a one-line action list for reconnecting monday (CLAUDE.md failure rule).
- If the thread cannot be read (`channel_not_found`), ask the user to paste the post text; do not guess its content.
- No em dashes or en dashes in anything written.

## Output schema
Chat answer, top-down:

**Verdict:** one sentence: Known / Past or declined / Unknown / Unclear, and the one fact that decides it.

**Evidence**
- HubSpot: original source and referral domain, owner, stage, meeting booked or not, with the record link.
- Partnership CRM: what was searched and what matched (item link), or "No match on Creators or Partnership Management".
- Slack: prior mentions, or "None found".

**Next step:** one line, owned by a named person where the source names one.

**Draft thread reply** (Team Slack style, 5 lines max, ends with `_Posted by the Marketing OS agent_`), plus one line saying it was saved as a draft in the thread or why it was not. The draft tool takes standard markdown, so write links as `[label](url)` there; in any sent Slack text they are `<url|label>`.

Write "None found" for an empty evidence line; never drop a line.

## Example
Input: Nir's post naming "7 Figure Podcast" for Barenda Brown, GDMJ Solutions LLC.

**Verdict:** Unknown. Not in the Partnership CRM, but HubSpot shows a real referral link from the community `my-seven-figure-podcast.mn.co`.

Draft thread reply:
```
:mag: Checked it: 7 Figure Podcast isn't in our Partnership CRM, but it's a real referral, not just a form answer. HubSpot has her original source as a link from the "My Seven Figure Podcast" community (my-seven-figure-podcast.mn.co) :tada:
Worth finding who runs it and whether we want them in as a creator/community partner.
[HubSpot record](https://app.hubspot.com/contacts/9154210/record/0-1/250063691424)
_Posted by the Marketing OS agent_
```

## Routine mode
Runs unattended Sun-Thu at 10:45 Israel time as the "Referrer lookup daily sweep" cloud routine: it sweeps Nir's new referrer alerts in the partnerships group DM and saves one combined draft. When invoked as the routine (or asked to "run the referrer sweep"), follow `knowledge/routine.md` instead of Step 6: it owns the lookback window, the combined draft, the self-check and the bail-out rules.

## Done when
The verdict, evidence and next step are in chat, and the reply is saved as a Slack draft in the source thread (or shown in chat with the reason it could not be saved).
