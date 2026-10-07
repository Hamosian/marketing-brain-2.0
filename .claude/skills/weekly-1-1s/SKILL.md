---
name: weekly-1-1s
description: Use when Raz Navon wants to prep his weekly 1:1 with Jarred Ilan Berman or his weekly 1:1 with Nir Taranto - two separate meetings, not one sync. Builds a two-tab artifact (Jarred tab, Nir tab) covering ongoing projects, open tasks pulled live from each meeting's own board (Jarred Weekly board 18426843451; Raz's items on Marketing Operations Tasks 6257866754 for the Nir tab), and notes logged during the week - checkboxes persist across reopens. Also logs ad-hoc reminders via "remember for Jarred weekly - ..." or "remember for Nir weekly - ...". Triggered by "prep my weekly with Jarred", "prep my 1:1 with Nir", "Jarred weekly", "Nir weekly", or "/weekly-1-1s". Distinct from raz-ops (his own report notes) and growth-marketing-team-tasks' paid.md (Nir's tracking of Raz's team) - reads paid.md's "1-1 notes" rows read-only, never writes to it.
---

# Weekly 1:1s (Raz Navon)

Raz Navon's prep for two distinct recurring meetings: his 1:1 with **Jarred Ilan Berman** (his report, Creative Growth Manager) and his 1:1 with **Nir Taranto** (his manager). One artifact, two tabs - never merge them into a single agenda, they are different meetings with different boards and different audiences.

## Inputs and context to load
- Always start from CLAUDE.md.
- `references/team.md` to confirm Raz / Jarred / Nir's identities if a lookup is needed.
- `references/monday_boards.md` for the Marketing Operations Tasks board conventions (Nir tab).
- `knowledge/jarred-board.md` for the Jarred Weekly board's groups and columns (Jarred tab) - load before any pull from board `18426843451`.
- `data/notes.md` - this skill's own ledger of logged reminders, one table per meeting.
- `data/artifact-url.md` - the currently published artifact URL, if one exists yet.

## Two modes

**LOG mode** - a freeform reminder during the week ("remember for Jarred weekly: follow up on creative testing budget", "add to Nir weekly: discuss the LinkedIn strategy doc").
1. Classify which meeting it's for from the phrasing. If neither "Jarred" nor "Nir" is named and it's genuinely ambiguous, ask once - never guess and file it under the wrong meeting.
2. Classify `Type`: `Project` only if Raz explicitly frames it as an ongoing initiative to track ("track as an ongoing project", "add as a project"); default `Type` is `Note` (a one-off item to raise once, then done).
3. Append a row to the matching table in `data/notes.md` (`Note`, `Type`, `Added` = today, `Status` = `Pending`, `Discussed` = empty). Commit and push.
4. Confirm back plainly: "Logged for the Jarred/Nir weekly: <note>." No approval gate needed - this is a low-stakes repo-only write to Raz's own ledger, not a live-system mutation.

**PREP mode** - build or refresh the agenda artifact before the meeting ("prep my weekly with Jarred", "prep my 1:1 with Nir", bare "/weekly-1-1s" with no further text - default to refreshing **both** tabs, since that is the most useful reading of an unqualified request).

1. **Reconcile prior state.** If `data/artifact-url.md` holds a URL, read the published artifact first. For any `Note`-type row that shows as checked, set its `Status` to `Discussed` and `Discussed` to today in `data/notes.md`. For any `Project`-type row shown checked, remove it from the Ongoing list (checking a project off means "wrap it up"; Raz can re-log it if that was wrong). Commit the ledger update. Also carry forward, by matching `id`, anything local to a monday-sourced card (Ongoing/Tasks) that the fresh pull would otherwise wipe out - since that card is fully re-derived from monday on every prep: an `edited: true` title, and any accumulated `item.updates` (the per-entry Updates dropdown). Keep those, but still refresh the item's other live fields (due/launched/background/status/overdue) from the fresh pull. Ledger-sourced items (Notes to raise, the tab-level Updates log) don't need this - they aren't re-derived, so an edit or a per-entry update there already persists on its own.
2. **Pull the Jarred tab, live:**
   - Board `18426843451` ("Jarred Weekly"). Resolve the current week's rotating group by matching today's date against the `DD Month - DD Month YYYY` group titles (see `knowledge/jarred-board.md`).
   - **Ongoing Projects** = items in the `Ongoing`, `Live - CRO`, and `Live - Ads` groups.
   - **Tasks** = items in the current week's rotating group + `In Progress`, plus any still-open item sitting in an *older* rotating week group (carryover - flag it as overdue with its original week).
   - Exclude `Backlog`, `CRO Backlog`, `Paused - CRO`, `Paused - Ads`, `On Hold`, `Done`, `No Longer Relevant`, `Reports` from both sections.
   - Surface each item's own date consistently: a future/target date renders as `due <date>`; a date that has already passed (e.g. Launch Date on a live/shipped item) renders as `launched <date>` instead - never label a past date "due".
3. **Pull the Nir tab, live:**
   - Board `6257866754` ("Marketing Operations Tasks"), filtered to Raz Navon (monday user `97365904`) on either the Owner (`person`) or POC (`dup__of_assignee`) column, `status not_any_of [1, 3, 9]`, excluding the `Backlog` and `On Hold` groups (see `references/monday_boards.md`).
   - This is the **Tasks** section for the Nir tab.
   - **Ongoing Projects** for the Nir tab = `Project`-type rows Raz has logged himself (there is no dedicated "ongoing initiatives" board on Raz's side the way Jarred's board has one).
4. **Background, read-only.** For every item pulled in steps 2-3, fetch that board's Updates (`get_updates`, `objectType: Board`, `includeItemUpdates: true`, a `fromDate`/`toDate` window wide enough to cover the pulled items) and attach the single most recent update (by `created_at`) per `item_id` as that card's background line. An item with no update in the window simply shows no background line - don't fabricate one. This is a comments/activity pull, never a write.
5. **Cross-check, read-only.** Read `.claude/skills/growth-marketing-team-tasks/data/paid.md` and pull any row with `Status = 1-1 notes` into the Nir tab's Notes section, labeled "(from Nir's task ledger)" so Raz doesn't re-log a duplicate. Never write to this file - it belongs to `/growth-marketing-team-tasks`.
6. **Assemble Notes to raise** for each tab from the `Pending` rows in `data/notes.md`, plus step 5's cross-check items for the Nir tab.
7. **Build the artifact.** Load the `artifact-design` skill, then `artifact-capabilities` before writing any code. Declare both the `artifact` and `sample` runtime capabilities:
   - `artifact` - lets a checked box **persist and be read back by this skill on the next prep**. Do not use `localStorage` for this: it is per-browser and invisible to Claude, so a checked item would never make it back into `data/notes.md`.
   - `sample` - powers a free-text scratchpad in a collapsible ("Add a note") dropdown under each tab's Notes to raise section. Raz types a raw thought and a button calls `sample()` in the browser to rewrite it as 1-3 short, direct bullets before it's added to that tab's notes - degrade gracefully (add the raw text as-is) if `sample` resolves `null` or the call fails.
   Also give each tab a standing **Updates** box (a textarea + "Add update" button, always visible, not tucked in a dropdown) above the three groups - raw text Raz leaves gets appended as-is, timestamped, to a chronological log (`STATE[tab].updates`, newest first) shown right below the box. This is a plain append-only journal local to the artifact: no AI formalizing, and never a write to monday.com or anywhere else - draw the line there even if a future ask sounds like it wants a live board comment.
   Every card in every section (Ongoing Projects, Tasks, Notes to raise) and every Updates log entry gets a small edit button next to its text: click it to turn the text into an inline field, Save/Cancel (Enter saves a single-line title, Escape cancels, Ctrl/Cmd+Enter saves a multi-line Updates entry). Saving sets `edited: true` on that item/entry so step 1's reconcile knows to preserve it next prep.
   Every card also gets its own small collapsible "Updates (N)" dropdown, separate from editing its title - a per-entry log (`item.updates`, newest first) plus its own textarea and "Add update" button, so Raz can leave a running commentary on one specific task/project/note without touching its title. Same rule as the tab-level Updates box: plain append-only text, no AI formalizing, never a write to monday.com. Preserve `item.updates` across reconcile the same way as `edited` titles, by id.
   Two tabs (Jarred / Nir), each with the Updates box, `## Ongoing Projects`, `## Tasks`, `## Notes to raise` - empty section reads "None right now", never dropped.
8. **Publish.** If `data/artifact-url.md` already has a URL, update that artifact in place (read it first if this session hasn't already, to avoid a stale-version conflict). Otherwise publish new and save the URL to `data/artifact-url.md`; commit either way.
9. Give Raz the link.

## Constraints
- Ground every item in its source - a monday item name/id or a logged ledger row. Never invent a task, project, or note.
- Two distinct meetings, always. Never merge Jarred's and Nir's content into one shared section.
- Read-only against every monday board (`18426843451`, `6257866754`) and against `.claude/skills/growth-marketing-team-tasks/data/paid.md`. A real task edit still goes through `monday-agent` / `/pm-story`, never this skill.
- The only writes this skill makes are to its own `data/notes.md` ledger and the published artifact.
- If a monday pull errors or returns empty, say so plainly rather than treating it as "no open work," and don't silently publish a stale artifact over it - per CLAUDE.md's standing failure-handling rule.
- Never delete a `Discussed` row from `data/notes.md` - it's the week-over-week record. Prune only on an explicit request.

## Output schema (per tab)
## Updates
- a standing textarea + "Add update" button; entries append as-is with a timestamp, newest first (or "No updates logged yet")
## Ongoing Projects
- ... each item may carry a `due` or `launched` date and a background line (the source item's latest board update) (or "None right now")
## Tasks
- ... each item may carry a `due` date and a background line (or "None right now")
## Notes to raise
- a collapsible "Add a note" scratchpad (raw text formalized by Claude on submit) sits above the list
- ... (or "None right now")

## Done when
The artifact is published (or updated in place) with both tabs current against live monday data and the ledger, checked-off items from the prior version have been reconciled into `data/notes.md`, and Raz has the link.
