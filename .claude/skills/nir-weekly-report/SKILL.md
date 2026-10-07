---
name: nir-weekly-report
description: Build the weekly Marketing Operations + Website Development report for Nir Taranto as a clean Riverside-branded Google Doc, then file it on the Growth Marketing Reports board. Weekly sibling of /nir-monthly-report. Pulls the most recently completed work week from the MOPs and Website Dev monday boards plus four Slack channels, renders What We Delivered / What Is In Progress / Next Week Priorities, and (after confirmation) creates the week's board item and Hanan's subitem linking the doc. Triggered by "nir weekly report", "Nir's weekly report", "weekly task report", "MOPs weekly report", "run the weekly report", or "/nir-weekly-report".
---

# Nir Weekly Task Report

Generate the weekly task report for Nir Taranto (Hanan's manager, Senior
Director, Growth Marketing) as a Riverside-branded Google Doc, and file it as
Hanan's subitem on the Growth Marketing Reports board. It is a quick read: three
sections, task name and owner, no metrics. This is the weekly narrative Hanan
files as one of five reporting leads (`references/growth-reporting.md`), distinct
from the monthly task report (`/nir-monthly-report`, which moved to a monthly
cadence on 2026-07-05). Both coexist.

All IDs, group-resolution rules, board schema, brand tokens, and the doc-build
method live in `knowledge/config.md` - load it before Step 1. Run the data pulls
in parallel where possible. Confirm nothing with the user until the write gate
in Step 4, unless a source is unreachable.

## Step 1: Resolve the week and pull the boards

1. Determine the report week: the most recently completed Sun-Thu work week
   (unless the user names another). Note its Sun-Fri label and its Thursday
   `DD.MM.YY` name (see `knowledge/config.md`).
2. `get_board_info` on the MOPs (`6257866754`) and DEV (`18397093471`) boards to
   resolve group ids dynamically. Pull the report week's MOPs group, the DEV
   current sprint, the DEV next sprint, and the MOPs `Nir's Requests` / `Open
   Tests` groups - each group in its **own** call so group membership stays
   clean. Restrict columns to `name`, `person`, `status` (add `date4` for DEV).

## Step 2: Enrich from Slack

Search the four channels in `knowledge/config.md` for the report week. Use Slack
to confirm go-lives, prod deploys, launches, and blockers, and to pick up
Hanan's own active P1s from the `#mops-team-internal` standups. Enrich the board
data; do not duplicate it.

## Step 3: Draft the report (three sections)

Assemble the content and show it to the user first (plain text is fine for
review). Sections, in order, each split into **Marketing Ops** and **Website
Dev** except the last:

1. **What We Delivered** - every item completed *this week*. Bullet = task name
   and owner only.
2. **What Is In Progress** - active items; add a short parenthetical for
   QA / Ready for live / Pending / Waiting for approval / Stuck / overdue.
3. **Next Week Priorities** - one unified list, 6-8 action bullets with owner and
   any known target date. Draw from next-week / next-sprint groups, upcoming
   go-lives in Slack, and carried-forward threads from last week's report.

## Step 4: Publish (confirmation gate)

Show the drafted report and the two writes you are about to make, then **ask for
confirmation** before any write:

1. Build the **Riverside-branded Google Doc** (HTML -> Google Doc, brand tokens
   and method in `knowledge/config.md`) in the correct Weekly Drive folder, and
   verify the styling survived.
2. **File on the Growth Marketing Reports board** (`18395106969`): create the
   week's `DD.MM.YY` item in the Weekly Summary group and Hanan's subitem with
   person, status Done, the doc link, and the Thursday date. If the item or
   subitem already exists, reuse and update in place - never duplicate.

Return the doc link and the board item link.

## Constraints

- **Ground every line in the source.** Do not invent owners, dates, or statuses;
  write the status you actually read.
- **Dedup against last week.** Do not re-list items last week's report already
  marked delivered; read the previous week's Hanan doc (linked on the prior
  board subitem) to check.
- **Brand is required.** The doc must use the Riverside tokens and Instrument
  Sans (see `knowledge/config.md`); a plain unstyled doc is not acceptable.
- **Confirm before writing.** Both the Drive doc creation and the board filing
  are mutations - gate them in Step 4. (If later deployed as a scheduled cloud
  routine, that routine is the deliberate exception.)
- **Idempotent filing.** Re-running updates the existing item/subitem link
  instead of creating duplicates.
- **Scope.** Only the boards, groups, and channels in `knowledge/config.md`.
  Keep Brand/PMM launches out of this MOPs+Website function report.
- **If a source is unreachable,** render its sub-section as a single line
  ("No items this week.") rather than dropping it, and note the gap.

## Output schema

Doc title block: `Weekly Task Report` / `Week of <Mon D> to <Mon D>, <Year>` /
`Marketing Operations + Website Development`, then:

## What We Delivered
### Marketing Ops
- task (owner)   (write "No items this week." when empty)
### Website Dev
- task (owner)

## What Is In Progress
### Marketing Ops
- task (owner) (status parenthetical)
### Website Dev
- task (owner) (status parenthetical)

## Next Week Priorities
- action, owner, target date

## Done when

The branded Google Doc exists in the Weekly Drive folder with the styling
verified, the `DD.MM.YY` board item and Hanan subitem are filed (Done, doc
linked), and both links are returned to the user.
