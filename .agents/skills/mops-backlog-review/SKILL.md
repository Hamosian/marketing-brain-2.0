---
name: mops-backlog-review
description: >-
  Monthly deep audit of parked/backlog work for the Marketing Ops team (Hanan + Jonathan) -
  reviews the Backlog and On Hold groups on the Marketing Operations Tasks board and the
  un-triaged groups on Website Development, proposing revive/keep-parked/archive dispositions
  for each stale item. Triggered by "backlog review", "monthly backlog review", "review the
  backlog", "clean up stale tickets", "groom the backlog", "what's sitting in on hold", "prune
  old tickets", or the automated end-of-month nudge from /mops-standup or /good-morning. Runs
  monthly as a cloud routine, or on demand.
---

# MOPs Monthly Backlog Review (Hanan + Jonathan)

Companion to `/mops-standup`. `/mops-standup` deliberately **excludes** `Backlog`/`On
Hold`/un-triaged groups so the daily brief stays fast (see `references/monday_boards.md`
and the fix that made this skill necessary). This skill is where that excluded content
actually gets reviewed - once a month, in depth, instead of never.

---

## Scope - per board, per that board's own conventions

Different boards use different group conventions for "parked" work. Don't apply one
universal rule across boards - read `references/monday_boards.md` for the current group
IDs before running, since weekly-bucket IDs rotate and this doc can drift.

### Marketing Operations Tasks (`6257866754`)
- Review groups: `Backlog` (`new_group45625`), `On Hold` (`group_mky6rv54`)
- Also pull `Open Tests` (`group_mkz33gap`) as its own bucket - these need a kill/keep
  call, not a backlog disposition, but they're in the same "someone should look at this"
  spirit and easy to forget for months at a time.
- Fetch columns: Name, Owner (`person`), Status (`status`), Priority (`priority_1`), Due
  date (`date`), and `updated_at` for age.

### Website Development (`18397093471`)
- Review groups: `New Tasks` (`group_title`), `Long-term Projects` (`group_mm05scnw`),
  `Backlog / Archive` (`group_mm3bkpvy`), `New Group` (`group_mm0kkx7p`)
- Fetch columns: Name, Requester (`multiple_person_mm05dcf4`), Assignee (`person`),
  Status (`status`), Priority (`color_mm051fmh`), and `updated_at`.
- **Flag any assignee who's no longer at the company** (cross-check `references/team.md`)
  as an automatic "needs reassignment or archive" - not a judgment call, just do it.

> HubSpot Projects // Eyal mvpGrow (`18413613511`) has no backlog/on-hold group structure
> as of this writing - skip it unless one gets added later. If a new board is onboarded
> to this repo with its own backlog/parked convention, add a scope section for it here
> rather than forcing it into the two patterns above.

---

## Step 1: Pull and group

For each board, pull each review group in parallel (`get_board_items_page` with a
`group` column filter, `includeColumns: true`). Sort oldest-`updated_at` first. Compute,
per group: total count, count by owner, and age bucket (updated in last 30/90/180+ days).

---

## Step 2: Propose a disposition per item

For each item, weigh name, priority, age, and owner, and propose exactly one of:

- **Revive** - move back to active (a real current weekly group / current sprint) -
  propose this when it's still relevant and someone will actually pick it up this month.
- **Keep parked** - genuinely still on hold/backlog on purpose. No action, just confirm
  it's still a deliberate choice and not just forgotten.
- **Archive / Close** - stale enough, superseded, or no longer relevant - mark Done or
  Cancelled and stop letting it clutter the board.

**Don't enumerate large groups item by item in the rendered brief.** A 150-item backlog
rendered as 150 rows is noise, not a review. Cluster by theme, priority, and age bracket
instead - e.g. "47 items from 2024, all P3, no due date, no updates in 180+ days - batch
archive candidate?" - and only call out individual items when they're notable: CNF/P1/
Critical priority, recently touched (someone cares), or genuinely ambiguous.

---

## Step 3: Render the brief

```text
# MOPs Monthly Backlog Review - [Month YYYY]

Snapshot: [N] parked items across 2 boards (Backlog [X], On Hold [Y], Website Dev
un-triaged [Z])
```

### Hanan's parked items
Notable individual items (CNF/P1/Critical or otherwise ambiguous) in a table, then
theme/age clusters as bullets with a proposed batch disposition.

### Jonathan's parked items
Same structure.

### Unowned parked items
Same structure - these are also intake-queue-shaped, flag if any look like they were
never actually triaged.

### Batch archive candidates
Cross-owner clusters of old, low-priority, no-recent-activity items, proposed as group
archive actions.

### Open Tests needing a kill/keep call
MOPs board only - list each one, these are always worth naming individually since
there are usually only a handful.

### Website Dev hygiene flags
Any assignee no longer at the company, or other structural issues found during the pull.

---

## Step 4: Confirm and act

This is a mutating skill - always confirm before changing status or group on any item,
individually or in a batch. Use `AskUserQuestion`, batched where possible ("Archive
these 47 items?" rather than 47 separate questions). Apply approved changes via
`change_item_column_values` (status) and `move_object` (group), then report what
actually changed.

---

## Cadence

- Runs monthly as a scheduled cloud routine (see `/schedule`).
- Also surfaced as a **suggested action**, not an automatic run, from `/mops-standup`
  and `/good-morning` during the last week of each month (day-of-month >= 22) - see
  those skills' Suggested Actions step. The daily skills only ever offer to run this;
  they never run it themselves.

---

## Key principles

- **This is the deep, slow counterpart to the daily standups.** Don't compress it to fit
  in 60 seconds - take the space needed to actually re-litigate stale work.
- **Cluster, don't enumerate, for large groups.** Group by age/priority/theme and propose
  batch actions instead of a wall of rows.
- **Confirm before every mutation**, batched proposals included.
- **Board-specific group conventions, always re-checked.** Re-read
  `references/monday_boards.md` each run - weekly-bucket group IDs rotate, and other
  boards may get their own backlog convention over time.
- **Departed-employee assignees are not a judgment call.** Flag and propose
  reassignment/archive automatically, don't ask "is this still relevant" for those.
