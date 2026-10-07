---
name: mops-standup
description: Use this skill for the shared Marketing Ops daily standup for Hanan and Jonathan Galili. Triggered by "mops standup", "our standup", "me and galili", "mops daily", "what's on our plate", "team standup", or a request to see day-to-day work across the MOPs Tasks, Website Dev, and mvpGrow boards plus the MOPs/website Slack channels. Pulls both owners' tasks, surfaces Slack asks not yet tracked, blockers, and stalled work, then splits the brief by owner.
---

# MOPs Daily Standup (Hanan + Jonathan)

A shared daily operating brief for Marketing Ops: **Hanan Amos** and **Jonathan Galili**. Jonathan Ydov (Web Developer) joins the team on 2026-09-27 but is not an owner here yet: add him to the table below once his monday name match and Slack user ID are recorded in `references/team.md`. It answers "what is on our plate today, what slipped, and what came in via Slack that we haven't tracked yet" in under a minute.

This is `/good-morning` extended to two owners and three boards, with intake-gap detection (Slack asks that aren't yet tasks).

Fetch ALL sources in parallel before rendering anything. Speed matters.

---

## Owners

| Person | Monday name match | Slack ID |
|--------|-------------------|----------|
| Hanan Amos | "Hanan" | `U0A3HCFE90S` |
| Jonathan Galili | "Galili" / "Jonathan Galili" | `U06NC1VQN7R` |

Group every task by matching the `person` (Owner) column against these names. Anything owned by neither (or unowned) goes in a **Shared / unowned** bucket - that is the team's intake queue.

---

## Step 1: Pull the boards (parallel)

Marketing Ops does **not** run sprints. Do not call `get_sprints_metadata`. Filter by status + owner + priority + due date.

Use `mcp__monday-api__get_board_items_page` for each board. Column keys and label IDs live in `references/monday_boards.md` - read it if unsure.

### Board A: Marketing Operations Tasks (`6257866754`) - PRIMARY
- Active filter: `status` (`status`) `not_any_of [1, 3, 9]` (excludes Done, Cancelled, Test is Closed).
- **Also filter by group** - this board has manual weekly groups (see `references/monday_boards.md`). Status alone is not enough: 150+ items can be non-Done but sitting in `Backlog` or `On Hold`, which are deliberately shelved, not part of today's workload.
  - Exclude `Backlog` (`new_group45625`) and `On Hold` (`group_mky6rv54`) from the main active/overdue analysis entirely.
  - Pull `Open Tests` (`group_mkz33gap`) as its own bucket - report these as "needs a kill/keep call," not as overdue work.
  - Pull `New Requests` (`topics`) as its own small "raw intake" bucket.
  - Everything else (weekly date-range groups + `Nir's Requests`) is genuinely active - this is what overdue/due-this-week/P0-P1 analysis should run against.
  - Group IDs rotate for the weekly buckets - confirm via `get_board_info` if `references/monday_boards.md` looks stale.
- Fetch columns: Name, Owner (`person`), Status (`status`), Type (`status_11`), Priority (`priority_1`), Due date (`date`), Planned? (`color_mkzt8ef8`).
- Prioritize: overdue, due today/this week, P0/P1, and items marked `Planned` (`color_mkzt8ef8` = `1`) - computed only over the genuinely-active set above. `Planned` means the item was scoped into the cycle rather than arriving in-flight, so it is a commitment signal, not a due-date signal - treat it as a tiebreaker *within* the active set, never as a reason to outrank something overdue.
  > **Use `color_mkzt8ef8`, not `color_mm08xv00`.** `color_mm08xv00` ("Weekly Planned") still exists on the board but is vestigial: it kept monday's default labels and is empty on every item (verified 2026-08-23, 300-item sample). This skill read it from launch, so the "Weekly Planned" prioritisation silently never fired. `color_mkzt8ef8` ("Planned?") is the live field - see `references/monday_boards.md`.
- **Report the planned/unplanned ratio** for the active set as one line in the snapshot. The Q1 2026 MOps retro made this a tracked weekly metric (13/87 planned at baseline, target 30/70), and this standup is where it gets read. Items with the column empty are `Unmarked` - count them separately rather than folding them into Unplanned.

### Board B: Website Development (`18397093471`) - PRIMARY
- Active filter: `status` `not_any_of [1, 8, 12]` (excludes Done, Published, Close).
- **Also filter by group.** Exclude `New Tasks` (`group_title`), `Long-term Projects` (`group_mm05scnw`), `Backlog / Archive` (`group_mm3bkpvy`), and `New Group` (`group_mm0kkx7p`) from active analysis - these are un-triaged/parked, not this sprint's work (see `references/monday_boards.md`). A Stuck item sitting in one of these groups is stale clutter, not a live blocker - don't report it as one.
- Fetch columns: Name, Requester (`multiple_person_mm05dcf4`), Assignee (`person`), Status (`status`), Priority (`color_mm051fmh`), Due Date (`date4`).
- Hanan and Jonathan are usually **requesters/owners** here, not assignees (Flow Ninja's Milutin + Dusan execute). Group by requester/owner match; flag items in Stuck or HOLD **that are in an active sprint/initiative group**.

### Board C: HubSpot Projects // Eyal mvpGrow (`18413613511`) - SECONDARY
- Hanan + Jonathan are the Riverside-side owners; mvpGrow (Eyal Katz) executes.
- Active filter: `status` `not_any_of [1]` (excludes Done).
- Fetch columns: Name, Owner (`multiple_person_mm3fvqdk`), Status (`status`), Priority (`color_mm3fs5kr`), Need-by date (`date_mm3fkez2`).
- Flag any **Stuck** item and any active item **missing a need-by date** (vendor cannot schedule it).

> The FY26 MKT Planning board (`18396740865`) is Nir's planning board, not day-to-day. Include it only if the user explicitly asks.

---

## Step 2: Pull Slack context (parallel)

Search the last **7 days** across the five channels using `slack_search_public_and_private`. Run all five in parallel.

| Channel | ID |
|---------|-----|
| #marketing-internal | `C043B7GAMPC` |
| #mops-team-internal | `C0AAQ15SVD3` |
| #mops-priority-room | `C0A9JUG9MPZ` |
| #website-dev | `C0AM2HQMY49` |
| #webflow-riverside | `C08DJ6BN3NX` |

> `#webflow-riverside` is where most website task delivery and QA actually happens (`references/slack.md`), so it carries the highest density of real website asks. It is **externally shared (Slack Connect)** - readable, but agents cannot post there. Any reply it prompts must be drafted for a human to send.

For each channel, extract:
- **Asks / requests** directed at MOPs (someone asking Hanan or Jonathan to do something).
- **Decisions** made that affect open work.
- **Unanswered questions** (no reply, or last message is a question).
- **Escalations** - anything in #mops-priority-room is high signal by default.

Keep raw message permalinks so the brief can link back.

---

## Step 3: Cross-reference (the high-value step)

This is what makes the standup worth more than two separate board views.

1. **Intake gaps** - for each Slack ask, check whether a matching task exists on Board A/B/C (fuzzy match on subject + requester). If none, flag it as **Not tracked**.
   > **Report them, do not file them.** `/ticket-hygiene` INTAKE owns Slack-to-ticket creation and keeps the permalink ledger that stops the same ask being filed twice. This skill has no visibility into that ledger, so filing from here would double-create. Hand off instead (Step 5). An ask already filed by `/ticket-hygiene` will show up as tracked here anyway, because the ticket exists by the time the standup runs.
2. **Stalled work** - tasks with no status movement and past or near due date, by owner.
3. **Blockers** - items in Stuck/HOLD, mvpGrow items missing need-by dates, and anything escalated in #mops-priority-room.
4. **Tests needing a decision** - anything in Board A's `Open Tests` group. Report as its own line under Blockers and risks ("needs a kill or keep call"), not as overdue work.

---

## Step 4: Render the brief

Keep it tight and scannable. Sentence case headings. No em dashes, no exclamation marks, no decorative emojis (team style). Use plain section dividers.

```text
# MOPs standup - [Weekday, Month DD, YYYY]

Snapshot: [N] open across 3 boards | [X] overdue | [Y] P0/P1 | [Z] Slack asks not yet tracked
Planned mix (MOps Tasks, active): [P] planned / [U] unplanned / [M] unmarked
```

### Hanan's plate
Table of Hanan's active items, sorted overdue first then by priority:

| Task | Board | Status | Priority | Due |
|------|-------|--------|----------|-----|
| [name](url) | MOPs / Web / mvpGrow | label | label | date |

One-line insight below (overdue P0/P1, too many in-progress, stale items).

### Jonathan's plate
Same table structure for Jonathan.

### Shared / unowned
Items owned by neither - the team intake queue. If empty: "Nothing unowned."

### New from Slack (not yet tracked)
One line per ask: channel, who asked, one-sentence summary, [permalink]. Mark each as **needs a task** or **needs a reply**. If empty: "No untracked asks this week."

### Blockers and risks
Bullets: stuck items, mvpGrow items missing need-by dates, priority-room escalations. If empty: "No blockers flagged."

---

## Step 5: Suggested actions

After the brief, use `AskUserQuestion` to offer 3-5 concrete next steps pulled from the data (e.g. "File the 2 untracked Slack asks", "Set need-by dates on 3 mvpGrow items", "Nudge Milutin on the stuck website item"). Include "Nothing, we're good" as the last option. If they pick one, act on it immediately - route untracked Slack asks through `/ticket-hygiene` (INTAKE mode), a single deliberate task write-up through `/pm-story`, and Slack replies through `/slack-agent`.

**End-of-month nudge:** if today's day-of-month is 22 or later, add one more option: "Run the monthly backlog review (`/mops-backlog-review`)" - this is the last week of the month, the natural time to groom `Backlog`/`On Hold`. This is a suggestion only - never run `/mops-backlog-review` automatically, just offer it. Skip this option entirely on any other day of the month.

---

## Key principles

- **Two owners, one brief.** Always split by Hanan vs Jonathan vs unowned. Never merge them into one list.
- **Speed over completeness.** Parallel fetch everything. Don't paginate Slack unless the first page is empty.
- **No sprint calls, but DO filter by group.** "MOPs doesn't run monday-native sprints" is not the same as "there's no grouping." Both MOPs Tasks and Website Dev use manual groups to separate active work from parked/backlog work - always exclude `Backlog`/`On Hold`/un-triaged groups before computing overdue or workload counts (see `references/monday_boards.md`). Skipping this makes stale, already-shelved items look like urgent live work.
- **Intake gaps are the point.** A Slack ask with no matching task is the most valuable thing this brief surfaces. Always check - but surface it, never file it. `/ticket-hygiene` owns the filing and the ledger that keeps it from happening twice.
- **One line per Slack item.** If it needs more, it is its own task.
- **Scheduled runs post to Slack.** When run on a schedule, post the brief to the configured channel and end with the Marketing OS footer (`_Posted by the Marketing OS agent_`).
