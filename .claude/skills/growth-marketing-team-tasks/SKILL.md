---
name: growth-marketing-team-tasks
description: Manage Nir Taranto's team tasks. FEED mode - paste text, a Google Doc, or Slack messages for a team; it extracts action items into that team's repo-backed ledger (confirms before writing). SHOW mode - a Riverside-branded interactive dashboard of open work across the six functions plus Nir's own tasks, one clickable tile per team (open/overdue/due-soon/blockers). Visual companion to /chief-of-staff. Triggered by "team tasks dashboard", "growth marketing team tasks", "feed tasks for [team]", "update [team]'s tasks", "add these tasks", "show me open tasks by team", "task dashboard", "who has what open", "what's blocked", or "/growth-marketing-team-tasks".
user-invocable: true
---

# Growth Marketing team tasks

Manage the task ledger for Nir Taranto's six functions plus his own tasks. You do
not require a Monday board for every team: most teams are **fed** (you paste a
doc, text, or Slack messages and the skill extracts the action items), while
teams that already run a board are read live. Everything normalizes to one
standard format defined in `references/team-task-registry.md`.

Two modes, auto-detected from the request:
- **FEED** - the user provides task material for a team (or says "feed / update /
  add tasks for [team]"). Extract, merge into the ledger, confirm, write.
- **SHOW** - the user wants to see the board ("show", "dashboard", "what's open",
  "what's blocked", or a bare invocation with no input). Render the artifact.

If it is ambiguous, ask which mode with one `AskUserQuestion`. Read-only for
`board` teams always; the only writes are to the repo ledger files in FEED mode,
always behind a confirmation.

## Inputs and context to load

- Start from `CLAUDE.md`. Load `references/team-task-registry.md` every run - it
  maps each team to its source (`feed` or `board`), its ledger file, and the
  standard task format. Load `references/monday_boards.md` only for `board`-team
  column keys/filters if the registry pointer looks stale.
- `knowledge/intake-spec.md` - FEED mode: how to extract tasks from free-form
  input and merge them into a ledger (dedupe, status transitions, confirmation).
- `knowledge/dashboard-spec.md` - SHOW mode: how to read both source types,
  compute counts, and render the interactive artifact.
- Ledger files live in `data/<team-slug>.md`. `board` teams read Monday via
  `mcp__monday-api__get_board_items_page` (never `get_sprints_metadata`).

## FEED mode

1. **Identify the team.** Match the request to one registry row (My tasks, MOPs,
   SEO, Paid, Creator, Growth Channels, SDR - all `feed` today). If unclear, ask.
   If a team is ever marked `board` in the registry, it is not fed (its tasks live
   on Monday); say so and stop.
2. **Ingest the input.** Accept pasted text, a Google Doc/Sheet link (read it),
   or Slack messages/permalinks (read them). Only read a source the user names
   this run - do not go hunting.
3. **Extract** action items into the standard format (see `knowledge/intake-spec.md`):
   task, owner (default the team lead if unstated), status, priority (`CNF` =
   blocker), due, source. Do not invent tasks, owners, or dates the input does
   not support - leave `-` when unstated. **Resolve terse/ambiguous tasks against
   context** (team-context digests, prior tasks, `references/team.md`, memory) and
   expand them; if confidence is still low, **ask Nir rather than guess**
   (`knowledge/intake-spec.md`).
4. **Merge** with the team's current `data/<slug>.md`: dedupe against existing
   rows, apply status transitions, carry forward untouched rows, and never
   delete `Done` rows. Set `Added`/`Updated` using today's date. If the input
   (usually a pasted "Copy my changes" block or the sync panel) contains a
   **`Focus order`** block, rewrite `data/focus-order.md` from it - it stores
   Nir's manual ranking of the dashboard's Today / This week band (ordered task
   ids per section; see `knowledge/dashboard-spec.md`, Focus band).
5. **Confirm, then write.** Show the diff (new / updated / unchanged / newly
   done) and get an explicit yes before writing the ledger file. This is the one
   mutating step.

## SHOW mode

1. **Fetch (parallel).** For each registry team read its `feed` ledger file (all
   seven are `feed` today). If a team is ever marked `board`, pull its Monday
   board per `references/monday_boards.md`, excluding the backlog / on-hold /
   un-triaged groups. Normalize every source onto the standard format. Also read
   `data/focus-order.md` - Nir's manual ranking for the dashboard's Today / This
   week focus band - and bake it into the page as `FOCUS_ORDER` (see
   `knowledge/dashboard-spec.md`, Focus band). And read `data/reading-list.md` -
   Nir's To-read queue - and bake it into the page as `READING` (see
   `knowledge/dashboard-spec.md`, To-read queue).
2. **Count.** Per team: **open** (not Done), **overdue** (open and due before
   today), **due soon** (open and due within 7 days), **blocked / CNF** (status
   Blocked or priority CNF). Attribute each task by owner.
3. **Render the artifact.** **Before publishing over the live dashboard, first
   remind Nir to hit "Copy my changes" and paste them** - a deploy bumps
   `DATA_VERSION` and clears any unsaved browser edits (see the pre-publish
   safeguard in `knowledge/dashboard-spec.md`). Only publish once he has pasted
   or confirms he has nothing unsaved. Then load the `artifact-design` skill,
   build the HTML from `knowledge/dashboard-spec.md`, write to scratchpad, and
   publish with the Artifact tool (update the canonical URL in place). Tiles
   ordered My tasks → the six functions; each expands to its items, `board`-team
   items deep-linking to their Monday pulse and `feed`-team items showing their
   source. Return a one-line summary + the artifact link.

## Constraints

- **Ground everything in the source.** FEED: extract only what the input
  supports. SHOW: a count is the number of real rows behind it. Never invent
  tasks, owners, dates, or counts. Leave `-` when unstated.
- **Confirmation gate.** The only writes are ledger files in FEED mode, and only
  after the user approves the diff. `board` teams are never written.
- **Never lose history.** Do not delete `Done` rows on a feed; git history is the
  "over time" record. Prune only on an explicit cleanup request.
- **Empty team:** SHOW renders the tile with "No open tasks" (never dropped). A
  board-light team (often SDR before it is fed) shows the same.
- **Source unreachable:** if a ledger file or a board is unreachable, render the
  rest and note the gap on the affected tile; do not fabricate its counts.
- **Deep links must be real** for `board` items:
  `https://riversidefm.monday.com/boards/<boardId>/pulses/<itemId>` from the
  item's actual ids - never guessed.

## Output schema

**FEED mode:** a diff summary (added / updated / unchanged / newly done, with
counts) and, after confirmation, the written ledger path. If nothing changed,
say so and write nothing.

**SHOW mode:**
1. The artifact - titled "Growth Marketing team tasks - [Weekday, Month DD,
   YYYY]" - with a snapshot row (open | overdue | due this week | blocked/CNF),
   seven team tiles (My tasks + six functions) each showing counts and expanding
   to items, and a footer noting data freshness and any unreachable source.
2. A one-line chat summary: totals plus the artifact link.

## Done when

FEED: the ledger diff is confirmed and written (or "no changes"). SHOW: the
artifact is published with all tiles populated (or cleanly noted as unreachable)
and the one-line summary with the link is returned.
