---
name: p1-p2-followup
description: Weekly follow-up and calendar scheduler for Hanan. Pulls his own items and every P1/P2 task he's accountable for across the MOPs Tasks, Website Dev, and mvpGrow boards, then books 20-minute focus slots for work he does himself, nudges for P1/P2 items others execute, and posts a summary. Runs weekly as a cloud routine. Trigger phrases - "p1 p2 follow up", "follow up on my tasks", "book my focus time", "schedule my week", "plan my week", "put my tasks on my calendar", "run the followup agent", "nudge my team on my P1s".
---

# P1/P2 follow-up + calendar scheduler

A personal, once-a-week operating agent for **Hanan Amos**. It answers "what do I owe
this week, and when am I actually doing it" by turning board state into calendar time.

Two jobs:
1. **My work** - the tasks Hanan does himself get **short 20-minute focus slots**.
2. **Nudge** - the P1/P2 tasks other people execute (Flow Ninja's Milutin/Dusan on the website, Eyal at
   mvpGrow, teammates) that are stalled, blocked, or slipping get **short nudges**
   so Hanan can push them along.

This is `/mops-standup` taken one step further: instead of only reporting the work, it
schedules it. It reuses that skill's exact board filters - they are the tested source of
truth. The new muscle is the calendar write and the idempotency that makes an unattended
weekly run safe.

Read `.claude/skills/p1-p2-followup/knowledge/config.md` first - all board IDs, column
keys, priority/status label IDs, and calendar conventions live there.

---

## Run modes

- **Scheduled (primary).** Runs weekly (Sunday morning, the start of the Israeli work week).
  Auto-books the calendar and posts
  the summary to Hanan's Slack DM. No prompt - it is an automation skill, so the CLAUDE.md
  "confirm mutating calls" rule is satisfied by the skill being explicitly scheduled.
- **Manual.** When Hanan invokes it by hand, render the proposed schedule (Steps 1-4 as a
  preview) and confirm with `AskUserQuestion` **before** writing any calendar events. Then
  proceed to Step 4/5. This keeps ad-hoc runs from silently mutating the calendar.

"This week" = the coming **Sunday-Thursday** (the Israeli work week). On a Sunday run, that
is today through Thursday; on a mid-week manual run, it is the rest of this week (today
through Thursday). Never Friday or Saturday.

---

## Step 1: Pull the three boards (parallel)

Marketing Ops does **not** run sprints - do not call `get_sprints_metadata`. Use
`mcp__monday-api__get_board_items_page` for each board with the active-status filter, the
group exclusions, and the restricted `columnIds` from `knowledge/config.md`. Fetch all three in
parallel. Filter values compare against label **id**, not index.

Keep it tight - the MOPs board is 900+ items. Filter server-side and restrict columns so
you stay under the 25KB response cap; paginate only if a page is truncated.

---

## Step 2: Classify each item into one track

For every item pulled, decide Track A, Track B, or ignore:

**Track A - My work (gets focus time).** Include if it is actionable work Hanan does
himself:
- MOPs Tasks with Owner (`person`) matching `Hanan`, in an active status, not blocked.
- Any P1/P2 item on any board where Hanan is the assignee/doer (rare outside MOPs).
Exclude anything Stuck/HOLD/Pending-and-blocked (that is a nudge, not focus work).

**Track B - Nudge (gets a reminder).** Include a P1/P2 item that someone else executes and
Hanan is accountable for, when it needs pushing:
- Website Dev items where Hanan is Requester (`multiple_person_mm05dcf4`) and the item is
  P1/P2 and is Stuck (`2`) / HOLD (`3`), or overdue, or due this week.
- mvpGrow items where Hanan is Owner and the item is P1/P2 and is Stuck (`2`), **or is
  missing a need-by date** (`date_mm3fkez2` empty - the vendor cannot schedule it), or is
  due/overdue.
- Teammate-owned P1/P2 MOPs items that are overdue or Pending with a past due date, where
  Hanan is the accountable owner.

**Needs an owner (report only, never booked).** P1/P2 items in an active status with **no
owner/assignee** on any board. These are not Hanan's to schedule, but an unowned P1/P2 is a
risk worth surfacing - collect them for a summary line, do not book time for them.

**Ignore** everything else (P3+ owned by others, done, parked-group items already excluded
in Step 1).

Track A slots are a fixed 20 min each (see `knowledge/config.md`) - no effort computation needed.
Note the P1/P2 label and due date on each item for sorting and the event description.

---

## Step 3: Read the calendar - the idempotency guard

This is what makes a weekly auto-booker safe. Do it before writing anything.

1. `list_calendars` -> resolve Hanan's primary calendar id and its **timezone**. Use that
   timezone for every event; never hardcode.
2. `list_events` for the target Sun-Thu window (`startTime`/`endTime` = that week, the
   calendar's timezone) to (a) find free slots and (b) read existing markers.
3. Every event this skill creates carries the marker from `knowledge/config.md` on the last line of
   its description: `[p1p2-followup v1 | item:<itemId> | week:<isoWeek>]`. Parse the
   `item:<itemId>` values out of the marked events found in step 2, then:
   - **Skip** any task whose marker already exists in this week's window (already scheduled
     on a prior run - do not duplicate).
   - **Re-fetch the current status of those marked item IDs directly** via
     `get_board_items_page` with `itemIds` (Step 1's active-only filter drops items that
     have since gone Done/Cancelled, so a completed item would otherwise disappear rather
     than be reported). If a marked item is now Done/Cancelled, note it in the summary as
     "completed since last run" and leave its stale event for Hanan to delete - do not
     touch non-marked or already-past events.
4. Treat all existing non-marked events as immovable busy time - schedule around them,
   never over them.

---

## Step 4: Write the calendar events

Sunday-Thursday only (the Israeli work week - never Friday/Saturday), inside the working
window from `knowledge/config.md` (default 09:00-18:00 in the calendar timezone). Use `list_events`
gaps to place events; fall back to `suggest_time` only if gap-finding is ambiguous. On a
same-day run, never place a block earlier than the current time. Set the marker and
`colorId` on every event.

**Track A -> short 20-min focus slots (one task each).**
- Sort Track A by priority (P0/P1 before P2) then due date (soonest first).
- Give each task its own slot, **20 minutes maximum** (Hanan's preference). Never batch
  multiple tasks into one event and never exceed 20 min. Fill the earliest free Sun-Thu
  gaps first; several slots can share a day.
- `create_event`: title `Focus: [P1] <task name>`; `availability: AVAILABILITY_BUSY`;
  `colorId` per config (`9`). Description: `- [P1] <task name> - <monday url>` then a blank
  line then the marker line.
- **Overflow:** if the Track A tasks do not fit in the week's free Sun-Thu gaps, stop
  booking and report the unscheduled items in the summary. Never silently drop them.

**Track B -> short nudges.** A nudge is 15 min to ping the owner, not time to do the work
yourself, so a nudge event is always 15 min regardless of how many items it covers.
- 1-4 nudge items: one 15 min event each. `colorId` per config (`6`),
  `availability: AVAILABILITY_FREE`. Title `Nudge: <executor> - <task name>`; description:
  the monday url, a one-line reason (`Stuck since ...` / `Overdue` /
  `No need-by date - vendor blocked`), then the marker.
- 5+ nudge items: one single 15 min "Nudges" event for the day, its description listing
  every item (one line + one marker each) so each is still de-duplicated on re-run. It
  stays 15 min - it is a prompt to run through the list, not to resolve it.
- Counting: the nudge count reported in Step 5 is the number of nudge **items** (reminders),
  not the number of calendar events.

---

## Step 5: Post the summary

Send a Slack DM to Hanan (`U0A3HCFE90S`) via `/slack-agent`. Team style: sentence case, no
em dashes, no exclamation marks, no decorative emojis. Structure:

```text
Weekly follow-up - week of [Sun DD]

Booked: [X] focus slots (20 min each) | [C] nudges
Left unscheduled: [U] (no free time this week)

Focus slots (20 min each)
- Sun 14:00-14:20 - [P1] task
- Mon 10:45-11:05 - [P1] task
...

Nudges
- [executor] task - reason - [monday link]
...

Needs an owner (unowned P1/P2)
- [P1] task - [monday link]
...

Unscheduled (carrying to next week)
- [P1] task - [monday link]
```

On scheduled runs, end with the footer as the last line: `_Posted by the Marketing OS agent_`.

If run manually, print the same summary in chat instead of (or in addition to) the DM.

---

## Key principles

- **Idempotent by marker.** Re-running the same week must create zero duplicates. The
  `item:<itemId>` marker in the event description is the dedupe key. Always read the
  calendar (Step 3) before writing.
- **Never touch un-marked events.** Real meetings and anything the skill did not create are
  immovable. Schedule around them; do not move, edit, or delete them.
- **Two tracks, never merged.** Focus time is only for work Hanan does himself. Everything
  someone else executes is a nudge, never a focus block.
- **Focus slots are 20 min max**, one task each (Hanan's preference) - never longer, never
  batched.
- **Sun-Thu work week and working window only.** No evenings, no Friday/Saturday.
- **Overflow is surfaced, never dropped.** If the week is full, the summary lists what did
  not fit so it carries forward.
- **Source of truth is the references.** `knowledge/config.md` is a cache of `references/monday_boards.md`
  and `references/team.md`; if a filter returns nothing or looks wrong, re-verify IDs there
  and with `get_board_info` (weekly group IDs rotate) and update `knowledge/config.md`.

---

## Scheduling this as a weekly routine

Set up with `/schedule` to run Sunday ~08:00 in Hanan's timezone (start of the Israeli work
week), invoking this skill in scheduled mode. Because it books the calendar and DMs Slack unattended, confirm two things
on the first scheduled fire:
- The Google Calendar, monday, and Slack MCP connectors are authorized in the scheduled
  cloud context. Interactively-authenticated connectors can be absent in a headless cron
  run - if the first fire fails to reach a connector, that is why.
- The idempotency guard (Step 3) worked - the run should not have doubled up any event a
  prior run created.
