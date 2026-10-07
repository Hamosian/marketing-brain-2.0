---
name: nir-ask-responder
description: "Drafts Hanan Amos's replies to the messages Nir Taranto's agent sends him in their Slack DM (the CRM, HubSpot, Chili Piper and routing issues from Nir's demo runs). Checks the DM four times a day Sun-Thu, investigates each new ask read-only (HubSpot, Chili Piper public endpoints, monday, the repo's systems docs), and saves a reply in Hanan's own voice as a Slack draft in the thread for him to review and send. Never sends to Nir, never changes a record: fixes are proposed, not made. Skips the messages Nir types himself. Dedupes via a committed ledger. Runs as a cloud routine, or on demand. Trigger phrases - \"draft my replies to Nir\", \"answer Nir's agent messages\", \"what did Nir's agent send me\", \"reply to Nir's demo-run issues\", \"run the nir ask responder\", \"/nir-ask-responder\"."
user-invocable: true
---

# Nir ask responder

Nir's demo-run agent DMs Hanan about CRM problems it finds: a missing pre-opp, a wrong
`booking_status_cp__c`, a mis-enriched company, a Chili Piper link that offers no slots.
This skill does Hanan's first pass on each one. It investigates read-only and writes the reply
Hanan would write, in his voice. It saves that reply as a **Slack draft in Nir's thread**, so
Hanan reads it, edits if needed, does any fix himself, and presses send.

Owner and only user: Hanan Amos (`U0A3HCFE90S`). The DM with Nir is `D0A4W65A80J`; Nir is
`U07LETHMPAP` (`references/team.md`). Every Slack call runs as Hanan, so nothing here may
reach Nir without Hanan pressing send.

## Acts when

A run does something only when the DM holds an **agent-written** message from Nir that
Hanan has not answered and the ledger does not list. Agent-written means the message text
carries `Sent using` with the Claude app mention (`<@U0ACB1BDNPK|Claude>`) or ends with
`Posted by the Marketing OS agent`. On 9 Sep to 2 Oct that was 25 messages, on 16 working days.
Nir's own typed messages (short, often Hebrew, mid-conversation) are **out of scope**: skip
them, never draft them. Most runs find nothing and end with "no new asks".

## Steps

1. **Load state.** Read `data/ledger.md` (processed message `ts` values and the last run time).
2. **Read the DM.** `slack_read_channel` on `D0A4W65A80J`, `oldest` = the earlier of last run
   minus 2 hours and the oldest open ledger row (`failed` or `deferred`), so a carried-over ask
   is always re-read (first run or empty ledger: last 24 hours). `response_format: "detailed"`.
3. **Pick the asks.** Keep a message only if it is (a) from `U07LETHMPAP`, (b) agent-written
   per *Acts when*, (c) not in the ledger with a terminal outcome (`failed` and `deferred` rows stay eligible),
   and (d) unanswered: `slack_read_thread` on it and
   drop it if Hanan (`U0A3HCFE90S`) has replied after it. A thread whose newest message is a
   new agent-written follow-up from Nir after Hanan's last reply counts as a new ask (key it
   by that follow-up's `ts`).
4. **Self-check** (below). If it fails, write the reason to the run report and stop.
5. **Investigate each ask, read-only.** Split the message into its numbered items. For each
   item, find the cause and the evidence:
   - HubSpot records, lists, properties: through `/hubspot-agent` (reads only). Load
     `systems/owned/hubspot.md` first.
   - Chili Piper links, ranges, hosts: `systems/owned/chilipiper.md`, and its public
     `slots/span` endpoint with `curl` for the live range. Never trust a URL theory over it.
   - Tasks and tickets: `/monday-agent` reads only. Prior decisions: search the DM and
     the repo (`systems/`, `.claude/skills/*/data/`) before calling something new.
   - Figures: `/rivermind:ask` first, per `CLAUDE.md`, with the source and as-of date.
   Record per item: what you checked, what you found, the cause if known, the fix you
   would propose, and who decides it. When you cannot reach a cause, say exactly what you
   checked and what is still open. Never fill the gap with a guess.
6. **Write the reply in Hanan's voice.** Follow `knowledge/hanan-voice.md` (stage 1, it stands
   in for a `nik-voice` register). Then `/de-ai` (stage 2), then `/critique` (stage 3). On
   REVISE apply its fixes once; if it still says REVISE, keep the draft and flag it in the
   run report. No em dashes or en dashes. Wrap every link as `<url|label>`. End with the
   `_Posted by the Marketing OS agent_` footer (repo rule; Hanan may delete it before sending).
7. **Save the draft.** `slack_send_message_draft` with `channel_id: D0A4W65A80J`,
   `thread_ts` = the ask's thread root. If it returns `draft_already_exists`, send the
   finished reply to **Hanan's self-DM** (`slack_send_message`, `channel_id: U0A3HCFE90S`)
   headed `Draft for Nir's <thread permalink|message about X>:` so he can copy it. The self-DM
   is the only place this skill may send; it never sends into the DM with Nir.
8. **Tell Hanan.** If anything was drafted, send one short self-DM: a line per ask (topic,
   thread link, where the draft is, any fix that needs his OK, any critique flag), with the
   footer. Nothing drafted: no message.
9. **Persist.** Append each handled `ts` with date, topic, and outcome (`drafted`,
   `drafted-selfdm`, `skipped-answered`, `skipped-no-ask`, `failed`, `deferred`) to
   `data/ledger.md`, updating the row in place when the `ts` is already there. `failed` and
   `deferred` are open: the next run retries them. On a third `failed` for the same `ts`,
   record `failed-final` (terminal) and name it in the self-DM. Count retries in the
   row's `Attempts` column. All other outcomes are terminal. Then update the last-run line, then commit straight to `main` (run state, not code, same as
   `invoice-inbox-to-monday`). Commit only when something changed:
   ```bash
   git add .claude/skills/nir-ask-responder/data/ledger.md
   git commit -m "nir-ask-responder: <n> drafts"
   git pull --rebase origin main && git push origin HEAD:main
   ```

## Self-check

- **Slack reads work.** If `slack_read_channel` errors or returns `channel_not_found`, that is a
  connector problem, not an empty inbox. Report it and stop: never log "no new asks" from a
  failed read.
- **The ask is real.** Sender is `U07LETHMPAP` and the agent marker is present. A message
  that only quotes or forwards one does not count.
- **Not already handled.** Ledger and thread both say unanswered. If either is unsure, skip
  and list it in the run report.

## Constraints (unattended, no human to ask)

- **Read-only on every system but two Slack surfaces:** the draft in Nir's thread and
  Hanan's self-DM. No HubSpot, Chili Piper, monday, or workflow writes, even when the fix is
  one click. The reply proposes the fix in Hanan's words ("I can set it back to Scheduled")
  and never claims it is done.
- **Idempotent.** The ledger plus the "Hanan replied" check mean a rerun never drafts the same
  ask twice. Never overwrite or delete an existing Slack draft.
- **Grounded.** Every record, number, date and name in a reply comes from a source read this
  run. Unknown stays unknown ("I can't see where the 26 came from").
- **Failure kinds.** Glitch: retry the call once. Tool down (HubSpot, monday, Chili Piper):
  draft from what you could check, name what you could not, and flag it. Empty: no message.
  Wrong (sources disagree): say both values and which you trust, per
  `references/evidence-standards.md`.

## Stop / bail-out

- **Slack unreachable:** report "Slack not connected, no run" and exit. No ledger write.
- **Escalate instead of drafting a fix** (draft the findings, leave the decision to Hanan in
  the self-DM line) when the fix would touch many records at once, change a live workflow or
  routing rule, affect spend or an invoice, or concerns a Tier-1 or open-deal account.
- **More than 5 new asks in one run:** draft the 5 newest, record the rest as `deferred` (the
  next run drafts them first), and list them in the self-DM.
- **Unread drafts:** if Hanan leaves drafts unsent for two days running, say so once in the
  self-DM and ask whether to keep going.
- **Kill switch:** pause or delete the routine named *Nir ask responder* in
  [claude.ai/code/routines](https://claude.ai/code/routines).

## Cadence

`CRON_TZ=Asia/Jerusalem 27 12,14,18,20 * * 0-4`: 12:27, 14:27, 18:27 and 20:27 Israel time,
Sunday to Thursday (the routine has a time zone, so DST does not shift it). Chosen from the
DM itself: of Nir's 25 agent messages, 14 landed 10:00-12:00 and 6 landed 16:00-18:00, so
these four checks catch nearly every ask within about two hours. Hourly would mostly find
nothing. Runs from Hanan's own claude.ai account so his Slack, HubSpot and monday connectors
are attached; confirm on the created routine that they are.

## Done when

Every new agent-written ask from Nir has a draft in its thread (or in the self-DM), Hanan has
one self-DM line per draft, and the ledger is committed. Or: "no new asks", logged and exited.

## Run report (the routine's final message)

```
Nir ask responder, <date> <time> Israel
New asks: <n>  Drafted: <n> (in thread <n>, self-DM <n>)  Skipped: <n>
- <topic>: <outcome>, <what Hanan must decide or do>
Not reached: <system or "none">
```
