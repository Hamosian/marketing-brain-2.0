# Dashboard spec - SHOW mode

How `/growth-marketing-team-tasks` reads every team, counts, and renders the
interactive artifact. The per-team sources and the standard task format live in
`references/team-task-registry.md`; read that first. This file covers reading
both source types, the counts, the Monday deep-link, and the HTML template.

## The seven tiles

Order: **My tasks** first, then the six functions (MOPs, SEO, Paid, Creator,
Growth Channels, SDR). Each maps to one registry row. A tracked item whose owner
is none of the seven → a small **Other / unassigned** grouping shown only if
non-empty.

## Reading each source type

Per the registry:

- **`feed` teams** (all seven today: My tasks, MOPs, SEO, Paid, Creator, Growth
  Channels, SDR) - read the team's `data/<slug>.md` ledger. Each table row is
  already in the standard format; parse the columns directly. For My tasks,
  optionally union the MOPs `Nir's Requests` group (`group_mm1cth4j` on board
  `6257866754`) only if that supplement is explicitly enabled in the registry.
- **`board` teams** - none today. The type is retained as an option: if the
  registry ever marks a team `board`, pull it live via
  `mcp__monday-api__get_board_items_page` (never `get_sprints_metadata`), exclude
  the backlog / on-hold / un-triaged groups named in `references/monday_boards.md`,
  and map its columns (owner, status with Done, priority incl. CNF, due) onto the
  standard format at read time. Nir's task view is feed-based by design; Hanan's
  team runs the MOPs Monday board operationally, but this dashboard does not read
  it.

Normalize every source onto the standard format before counting, so a
"P1, due Friday" task counts identically regardless of where it came from.

## Count definitions (per tile)

Against "today" (the run date), over each tile's normalized tasks:

- **Open** - status is **neither `Done` nor `Watch list`** (the code's `isClosed()`
  helper). The tile's headline number.
- **Overdue** - Open **and** `Due` is before today.
- **Due soon** - Open **and** `Due` is today through today + 7 days.
- **Watch list** - status `Watch list`. Finished work Nir is still monitoring, so it
  is **closed, not open**: excluded from Open / Overdue / Due-soon and from the
  Today / This week band. Its own snapshot tile and steel-blue per-team badge
  ("N watching"). Crucially it is **exempt from Hide-done** - a `Done` row vanishes
  when Hide-done is on, a `Watch list` row never does. That exemption is the whole
  reason the status exists; do not "simplify" it into `Done`.
- **Blocked / CNF** - status `Blocked` **or** priority `CNF`. This is the
  "track CNFs" (blockers) surface Nir asked for; call it out in red.
- **No due date** - Open with `Due` = `-`. Counts as Open, not Overdue/Due-soon.

Snapshot row = org totals across all tiles: Open, In work, Need review,
Due / overdue, Watch list, Done (six tiles).

**Adding a status is not a one-line change.** `Done` and `Watch list` are compared
in ~15 places (counts, filters, focus-band membership, ETA bucketing, the row
checkbox, the strikethrough class, badges, tile click handlers, the add-form
styling). Anything meaning "work is finished" must go through `isClosed()` rather
than a bare `=== "Done"`, or the new status silently reads as open work forever.
`scripts/validate_tasks.py` pins the ledger's status vocabulary to the dashboard's
own `STATUSES` array and fails on anything else, which catches the typo case
(`"watchlist"` vs `"Watch list"`) that would otherwise be invisible.

Optional velocity: **closed last 7 days** per tile - count `Done` rows whose
`Updated` is within 7 days (ledgers), or Done board items updated within 7 days.
Secondary number only, never in the headline Open count; skip if a board read is
slow.

## Monday deep-link format (`board` items only)

```
https://riversidefm.monday.com/boards/<boardId>/pulses/<itemId>
```

Use the item's real `boardId` and `id`. `feed` items have no pulse - show their
`Source` (a doc link, a Slack permalink, or "pasted <date>") instead.

## Rendering the artifact

Before writing the page, **load the `artifact-design` skill** and honor the
Artifact contract: one self-contained HTML file (inline CSS/JS, no external
requests), theme-aware (light/dark), responsive (no horizontal body scroll;
long lists scroll inside their own container), favicon `📋`. Write to the
scratchpad, then call the Artifact tool. `<title>Growth Marketing team tasks</title>`.

### Built source (start here)

`assets/dashboard.html` is the current, working dashboard - the canonical build.
On a refresh, **start from that file**: regenerate its embedded `TASKS` array from
the current `data/*.md` ledgers (each row → `{id, team, owner, pri, due, title}`,
plus `status` and - when the ledger's `Answer` cell is non-empty - `answer` as an
HTML string, `due` as `YYYY-MM-DD` or `null`), keep the rest of the file, and
publish. Escape `&`/`<`/`>` in answer text and use `<br>`/`<b>`/`<i>` for
formatting; omit the `answer` key entirely when the cell is `-`. Do not
re-author the HTML from scratch. If you change the page's design/features, save
the new version back to `assets/dashboard.html` so it stays the source of truth.

**Validate the array before every publish: `python3 scripts/validate_tasks.py assets/dashboard.html`.**
It must print `OK`. A single malformed row takes down the *entire* page, not just
that row: the script throws, nothing renders, and Nir sees an empty board with no
error message. The failure that caused this (2026-08-03) was appending a new row
*after* the array's last element, which by definition has no trailing comma, so
the file read `} {` and the whole `TASKS` literal became a syntax error. When
appending, either insert before the final element or add the comma to the element
you are appending after. The validator catches exactly that, plus duplicate ids
and any row that does not terminate in `},`.

**`window.confirm()` / `alert()` / `prompt()` are blocked in the published artifact iframe.**
The frame is sandboxed without `allow-modals`, so `confirm()` returns `false` and the code
after it never runs. This silently made the Reset button a no-op (`if (!confirm(...)) return;`),
discovered 2026-08-03. Never gate an action on `confirm()`. Use a two-click arm/confirm on the
button itself instead (first click swaps the label to "Confirm ...", a 3s timeout disarms).
**Known latent instance:** the per-row "✕ delete added task" control still uses `confirm()`,
so it too no-ops in the published frame; convert it to the same two-click pattern next time
that code is touched.

Also: the artifact's `localStorage` lives inside the cross-origin sandboxed iframe. It cannot
be read or cleared from Claude-in-Chrome (`javascript_tool` runs in the claude.ai shell frame,
not the artifact frame). A stale local override can only be cleared from inside: the Reset
button, or the render-time `pruneRedundantOverrides()` self-heal, which drops any override
field already equal to the baked ledger value on every render.

**`REFRESHED_AT` must come from the system clock, never from an estimate.** Read
it with `TZ=Asia/Jerusalem date '+%Y-%m-%d %H:%M %Z'` and paste that exact value.
A guessed stamp (e.g. rounding to the top of the hour, or reusing the scheduled
run time) makes the page look stale or time-travelled and costs trust in every
other number on it. Nir caught a 40-minute-wrong stamp on 2026-08-03.

**Current features (preserve on any rebuild):** an **+ Add task** form (creates a
task in the browser; it appears in "Copy my changes" under "New tasks to add" so
Claude writes it to the right ledger; added tasks have a ✕ delete). The add form
carries title, team, owner, **status**, priority, and ETA - the status select
(added 2026-08-03, after Nir hunted for it inside the priority dropdown) is what
lets a row be created straight as `1-1 notes` or `Need review` instead of always
landing as `Open`; it defaults to `Open` and serializes as `status=` in the
copy-out. Also: collapsible team tiles (default
**closed**; Expand/Collapse all), per-task editable **status** (Open / In work /
Done via checkbox + dropdown), inline-**editable task title** (click to edit),
editable **priority** (CNF-P4) and **ETA** (date picker + Today / Wk / Mo
quick-set presets), **clickable snapshot tiles** that filter the list (Open /
In work / Due-overdue / Done; Hide-done defaults **on**), a **Move to team** control per task
(re-files it under another team; reported in "Copy my changes" as "moved to X";
also carries a **📚 → Read later** option that sends the task to the To-read queue -
see To-read queue below),
a **📨 Ping owner** button per task (queues a Slack nudge; surfaced in "Copy my
changes" so Claude drafts a clear, context-rich DM and confirms before sending -
see `knowledge/intake-spec.md`), top **filters** for priority and ETA
(All / Overdue / Today / This week / This month / Later / No ETA) plus Hide-done,
**sort by priority within each team**, browser-`localStorage` persistence, and a
"Copy my changes" button. "This week" = the current work week's Thursday. Every
task has a **💬 Answer / comment** toggle with a **clear yes/no badge** (Nir,
2026-08-03): a filled green **💬 Answer ✓** chip when the `Answer` column is
non-empty, a faint dashed **＋ No answer yet** outline when it is empty, so a task
that still needs a reply is obvious at a glance without expanding. It shows the
current answer (the ledger's `Answer` column) and an editable textarea to add or
edit one. Like all
other dashboard edits, a typed answer persists in `localStorage` and surfaces in
"Copy my changes" (as `answer/comment: "…"`) so it flows back to the ledger via
FEED mode; it does not write to the repo directly. Answers entered as plain text
keep their line breaks; a pre-existing rich answer (e.g. baked HTML with bold)
displays formatted but prefills the editor as plain text.

### Focus band - Today / This week (added 2026-08-03)

The band at the top of the page (above the snapshot) is Nir's morning
prioritization surface. Design rule: **it is a lens over the same tasks, never a
second list** - membership is computed fresh from each task's effective `Due` on
every render, so a task cannot be duplicated between the band and its team tile.
The same object simply renders in both places; the tile row shows a small
`▲ today` / `▲ this week` chip to make the link visible.

- **Membership (all owners, status not `Done`):** `Today` = due today or overdue.
  `This week` = due after today through the work week's Thursday (`eow()`). No
  date = not in the band; the way in is the row's Today/Wk preset or the date
  picker (or dragging, below).
- **Today is de-noised (2026-09-14, Nir: "remove a lot of noise it currently
  has").** Three rules, all in `focusSection()` / `focusMembers()`:
  1. **Agent-inferred ETAs never put a row in Today.** `isInferred(t)` is true
     when the baked answer says `inferred` or `ETA set` and Nir has not set a date
     himself (an override on `due` counts as stated). Such a row stays in its team
     tile with its days-late chip and can still land in This week; it only loses
     the Today slot. Same principle as the brief's "inferred dates never count as
     overdue" rule.
  2. **`1-1 notes` agenda cards render in This week only.** The chief-of-staff
     1-1 packs now carry that material into the meeting itself, so a Today agenda
     card was a second copy.
  3. **Actions for Nir lead the section.** See "Actions" below.
- **Actions (added 2026-09-14).** `ACTIONS` + `ACTIONS_DATE` are baked from
  `data/today-actions.md`, which `/chief-of-staff` overwrites on every run with
  the rows of its action table (Nir is the actor on each: a reply owed, an
  approval, a decision with a clock). They render first in Today as `li.fcard.action`
  cards: `ACT` chip, title (click opens the source link), meta with the clock in
  red, who is waiting, age, and a `↗` link. They are **not tasks**: no id, no drag,
  no done checkbox, no sync, never nudged. The brief closes one by leaving it out
  next run. When `ACTIONS_DATE` is not the viewer's date the header shows
  "actions from YYYY-MM-DD" instead of hiding them. The Today count reads
  "N actions + M" so the two populations stay distinguishable. Build:
  `build_actions()` in `scripts/build_dashboard.py`; a missing or empty file bakes
  an empty array, never an error.
- **`1-1 notes` aggregation:** agenda tasks would flood the band one row per
  talking point, so they render as **one non-draggable agenda card per team**
  ("1-1 agenda · SEO & AI Search - 13 items"), pinned after the real cards, in
  This week only (see above). Clicking it opens that team's tile.
- **Drag to reorder:** cards reorder within a section by drag. **Dragging a card
  across sections rewrites its ETA** (into Today = today's date; into This week =
  Thursday) - the date IS the membership, so there is no separate "pinned" state
  to sync. The ETA change flows through the normal override → copy-changes → FEED
  pipeline like any other edit.
- **Order persistence:** the manual ranking is baked into the page as
  `FOCUS_ORDER` (ids per section), regenerated each publish from
  `data/focus-order.md`. Drags override it in `localStorage`
  (`gmtt-focus-v1`) and surface in the sync panel / "Copy my changes" as a
  `Focus order (save to data/focus-order.md)` block listing ordered ids - the run
  rewrites that file from the block (confirm like any FEED write). Reconcile
  drops the local override once the baked order catches up. Members not listed in
  the order file are appended sorted by priority then due.
- **Card title must wrap, never `nowrap` (fixed 2026-08-05).** The focus sections
  are a CSS grid, and a grid item will not shrink below its content's min-content
  width. A single `white-space: nowrap` title therefore forced the whole focus
  section to the title's full width and broke the page frame (horizontal overflow,
  ~1070px in a 640px panel). The fix: `.ft` wraps and is clamped to 2 lines
  (`display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical;
  overflow-wrap:anywhere`), and `.fsec` / `ul.fcards` / `li.fcard` carry
  `min-width:0` so the grid/flex chain can actually shrink to the panel. Do not
  revert `.ft` to `nowrap`/`text-overflow:ellipsis` - it reintroduces the overflow.
- **Card anatomy:** grip, done-checkbox (marks the task Done), team color dot
  (`TEAM_COLORS`), priority chip (CNF/P0/P1 highlighted), one-line title (click
  jumps to and flashes the row in its team tile), owner + days-late on Today.
- **Task ids must stay stable across refreshes.** When regenerating `TASKS` from
  the ledgers, keep each existing row's id (match by title/history) and give new
  rows the next free sequential id for their team. Ids are what `data/focus-order.md`
  and the drag override point at; re-keying them scrambles Nir's saved order.

### To-read queue (added 2026-08-03)

A **📚 To read** collapsible section sits between the snapshot and the filter bar.
It is Nir's personal reading queue and is a **separate object type from tasks** -
reading material, never a task, never on a team ledger. Design rule: reading is
not forced into the task model. This replaced the old behaviour where a no-owner
article capture became a P0 "Review and decide" My-tasks row.

- **Data source:** baked into the page as the `READING` array from
  `data/reading-list.md` (columns: id `read-N`, Status `unread`/`read`, Title,
  URL, Note, Added, Source). Regenerate it on each publish the same way as `TASKS`.
- **Feeds:** (a) the daily `/chief-of-staff` self-DM scan now files **no-owner**
  article captures here as `unread` rows; articles with a **named owner** still
  become that team's task (unchanged). (b) the dashboard's **+ Add to read**
  button (manual URL + note).
- **Per item:** a read checkbox (marks read → struck through, sorts below unread),
  title linking to the URL, the note, source (Slack permalink + date), a
  **→ make task** button (unread only), and a ✕ delete on manually-added items.
- **→ make task:** opens a task on **My tasks** (`Open`, `P2`, title `Act on: <title>`,
  the URL + note in `Answer`) and marks the reading item read in one action - so a
  read that needs follow-up becomes a real task without living in two places.
- **Reverse - task → Read later (Nir, 2026-08-03):** the per-task **Move to team**
  dropdown has a `📚 → Read later` option that sends a task *into* the queue. It
  leaves the task world (dropped from counts and the focus band) and becomes an
  `unread` reading item (any URL in its answer is extracted; the answer becomes the
  note). In "Copy my changes" it appears under `New reading items` tagged
  `(Read later: also remove the matching task row from its ledger)` - so FEED both
  adds the reading row and deletes the task row.
- **Sync:** reading edits persist in `localStorage` (`gmtt-reading-ov-v1`,
  `gmtt-reading-add-v1`) and surface in "Copy my changes" / the sync panel as
  `New reading items`, `Reading marked read`, and `Reading items removed` blocks,
  each naming `data/reading-list.md`. `pruneRedundantOverrides` self-heals: a
  status override the ledger caught up to is dropped, and a manual add that landed
  in `READING` (matched by URL) is dropped. Reset clears reading state too.
- **Open state:** the section defaults open when unread items exist, and remembers
  the viewer's toggle within the session.

### Building the page - always use the build script

**Never hand-edit the baked `TASKS` / `READING` / `FOCUS_ORDER` arrays, and never
regenerate them with ad-hoc string surgery.** Run:

```bash
python3 scripts/build_dashboard.py && python3 scripts/test_dashboard_safety.py
```

`scripts/build_dashboard.py` regenerates all three arrays from `data/*.md`, stamps
`REFRESHED_AT` on every run, bumps `DATA_VERSION` only when the baked data
actually changed, and refuses to write unless it passes:

- **ID preservation.** Task ids are stable and historical; they are matched by
  fuzzy title across all teams (a task keeps its id when moved between teams,
  because `team` is a field and the id is not). The script **refuses to write** if
  any id would disappear, duplicate, or land on a different task. This is the gate
  that protects Nir's browser edits, which are keyed by id.
- **Declaration diff.** Every `var`/`function` in the file before the edit must
  still exist after it.
- **Syntax check.** The whole script block is parsed with JavaScriptCore.

`scripts/test_dashboard_safety.py` then runs the shipped `pruneRedundantOverrides()`
against the real baked data to confirm a dropped id quarantines rather than
destroys.

**Why this is mandatory (2026-08-09).** A hand-rolled regeneration sliced the
`TASKS` array using a literal end marker of `"\n  };"`. The array ends with `];`,
so the cut ran past `TASKS` and swallowed `TEAMS`, `READING` and `FOCUS_ORDER`
before stopping at the brace that closed `FOCUS_ORDER`. `FOCUS_ORDER` is
dereferenced on every render, so the published page threw a `ReferenceError` and
never painted - while every check that was run (task count, id uniqueness, JSON
shape of the rewritten array) passed, because they only looked at the part that
had been rewritten. Two rules fall out, and the script enforces both: **find the
end of a JS literal by matching brackets, never by string-matching**, and
**validate the whole file, not the part you changed.**

### Orphan quarantine - an edit is never destroyed

`pruneRedundantOverrides()` runs on **every render**. It used to `delete ov[id]`
for any override whose task id was missing from the baked `TASKS`, which meant a
single bad publish silently destroyed the un-synced edits attached to those ids.

Those overrides are now moved to `gmtt-orphans-v1` instead, with their edit
timestamps intact, and:

- the sync bar shows them at the top, above everything else, saying explicitly
  that nothing was deleted;
- `restoreOrphans()` reattaches them automatically if the id ever comes back,
  without Nir retyping anything;
- a newer live edit always wins over a stale quarantined value.

If Nir ever sees that quarantine banner, it means a **publish** was wrong, not
that he did anything wrong. Fix the build (usually: restore the dropped id) and
the edits reattach on his next load.

### Published artifact - update in place

There is one canonical dashboard; do not mint a new URL each run. Update the
existing artifact in place:

- **Canonical URL:** `https://claude.ai/code/artifact/21b7945e-8f4b-420a-a6ef-96be559fcbcc`
- Same conversation that published it: re-publish the same scratchpad file path.
- Any other run (including `/chief-of-staff`'s morning refresh): pass the
  canonical URL above as `url` to the Artifact tool so it overwrites that page.
- The page carries interactive status controls (Open / In work / Done) that
  persist in the viewer's browser (`localStorage`), plus a "Copy my changes"
  button. Those local edits do not write back to the ledger - Nir pastes the
  copied changes and they are applied via FEED mode (propose → confirm).

**Refreshes are non-destructive (changed 2026-07-30).** A `DATA_VERSION` bump used
to wipe the viewer's whole `localStorage`, which silently destroyed any edit Nir
had not yet sent via "Copy my changes". It no longer does. On a version change the
page runs `reconcileWithLedger()`, which compares each stored override field
against the newly baked value:

- Override **equals** the baked value → the ledger has caught up, so the override
  is redundant and gets dropped (counted as "confirmed saved").
- Override **differs** → it is an unsynced edit and **survives** the refresh.
- Override points at a task no longer in the ledger → **quarantined, never dropped**
  (changed 2026-08-09, see "Orphan quarantine" below).
- A locally-added task whose title now matches a baked task → it landed, dropped.
- `ping` flags are local-only and always preserved.

The page then shows an amber **sync bar** whenever anything is
unsynced ("N changes not yet in the ledger") with a one-click *Copy for Claude*
button, or a confirmation line when a refresh cleared edits the ledger had
absorbed. The bar sits at the **bottom** of the page (moved 2026-08-05 at Nir's
request: the board opens on the tasks, and the paste is an occasional push, not
the reason he is there). Nothing reads it by screenshot anymore, so its position
is a pure UX choice and no longer pinned to the first viewport. Unit-tested via `scripts/` style harness; the eight assertions cover
each bullet above.

**Reading Nir's pending edits (added 2026-07-30; revised 2026-08-03 and again
2026-08-04).** The hard constraint, verified 2026-08-04: **the run gets exactly one
plain screenshot of the initial viewport and cannot interact at all.** Clicks, key
presses (`End`) and scroll wheel events - over the artifact body *and* over the
claude.ai header strip - all blank the sandboxed frame, which then stays blank until
a re-navigate. So the run cannot expand, scroll to, or click anything.

There is now **one** changes surface, not two (simplified 2026-08-05 after Nir asked
why there were two), and it lives at the **bottom** of the page (moved same day):

- **Amber sync bar** - the alert, the count, *Copy for Claude*, and the
  diff inline in a `<pre>`, capped at **24 logical lines** with an "… and N more
  lines" marker. This is the only on-page view of pending changes.
- The old **bottom "pending block"** was removed. It existed only to hold the full
  untruncated diff for the screenshot-reader (capped top) and for a human who
  scrolls. Both reasons are gone: no agent reads the page (see the root-cause note
  below), and the *Copy for Claude* button copies the full text regardless of what
  the capped bar shows - so a second on-page copy of the same list was pure
  redundancy. Do not reintroduce it.

**ROOT CAUSE CORRECTION (2026-08-05): the screenshot channel does not work from a
background run, and clicks were never the main reason.** Diagnosed empirically in
Nir's own Chrome: the artifact `<iframe>` is present, correctly sized (1470x766),
same-origin-sandboxed and with its `src` set, yet paints **nothing**. The tab
reports:

```
document.visibilityState === "hidden"   document.hidden === true   document.hasFocus() === false
```

The artifact frame defers painting until its tab is actually visible (the frame
preamble's `promoted()` / `__frame_size_poke` path). Claude-in-Chrome drives tabs
inside a **background MCP tab group** that is never fronted, so the frame never
gets promoted and the capture is blank white forever. This reproduces on a clean
`navigate` → `wait 10s` → `screenshot` with **zero interaction**, and again on a
freshly created tab (`tabs_create_mcp` does not front the group either). There is
no tab-activation tool exposed for Claude-in-Chrome, so a run cannot fix this.

So the earlier note that "clicking the toggle blanked the frame" mis-attributed the
symptom: the frame was already blank. That in turn means the "never reintroduce a
collapsed `<details>` / `max-height` / inner scroller" rule below is **not** load-bearing
for the run's read path (it never had one). Keep it anyway - it is still right for
Nir, who reads the bar with his own eyes in a foreground tab, and that is the only
reader it was ever really serving.

Steps for a run:

1. **Probe visibility first, before spending calls on navigate → wait → screenshot.**
   One `javascript_tool` call on the artifact tab: `document.visibilityState`.
   (`javascript_tool` runs on the `claude.ai` top origin, so it is safe and cheap.)
2. **If it returns `"hidden"` - stop. Do not screenshot.** The capture is
   guaranteed blank. Go straight to asking Nir to hit *Copy for Claude* and paste,
   and say plainly that the frame cannot be read from a background tab rather than
   reporting it as a mysterious blank or a possible artifact bug. This is the normal
   path for every scheduled/headless run.
3. **If it returns `"visible"`** (an interactive session where Nir has the tab
   fronted), take **one screenshot** and read the amber bar.
   `computer{action:"zoom"}` on the bar's region is safe and sharpens small mono
   text; it is a crop of the capture, not an interaction. **Touch nothing else** -
   clicks still cannot reach the sandboxed frame (see below).
4. Merge what you read via FEED mode (propose → confirm).

**The paste is the primary channel, not the fallback.** Nir pastes the *Copy for
Claude* block unprompted and it round-trips perfectly, so treat the ask as routine
rather than as an apology for a failure. The non-destructive refresh means unsynced
edits survive indefinitely while they wait, so a run that cannot read them costs
nothing as long as it says so and asks.

### Paste sync protocol - the ack token (added 2026-08-05)

Nir asked for pasted edits to clear off the amber bar **without** him reloading to
verify and **without** Reset (which nukes unsent edits too). The page and the
applying run now run a handshake:

- Every edit the page stores is stamped with a per-field timestamp
  (`gmtt-ovts-v1`; added tasks / reading adds carry `ts`, the focus override
  carries `focusOv.ts`).
- **Copy for Claude appends a footer line: `SYNC_TOKEN: <ms>`** and remembers that
  moment (`gmtt-lastcopy-v1`). Everything pending at copy time is in the block.
- **When you apply a paste that carries `SYNC_TOKEN: N`, you MUST, in the same
  republish:** (1) write the changes to the ledgers as usual, (2) set
  `var ACK_TOKEN = N;` in `assets/dashboard.html` (it sits right under
  `DATA_VERSION`; **monotonic - only ever raise it**, `max(old, N)`), (3) bump
  `DATA_VERSION`, (4) validate and publish to the canonical URL.
- On Nir's next visit the page drops exactly the pending items stamped `<= ACK_TOKEN`:
  everything that was in the acked copy, nothing he edited after it. `ping` flags
  are local-only and never acked. No reload ritual, no Reset.
- A paste **without** the token (hand-typed, partial, pre-feature): apply normally
  and leave `ACK_TOKEN` alone. The soft-match self-heal below cleans up.
- **Soft matching (same change):** `pruneRedundantOverrides` / `reconcileWithLedger`
  now compare `title`/`answer` fields case-, whitespace-, punctuation- and
  `<br>`-vs-newline-insensitively (`softNorm`), so a ledger write whose text differs
  from the browser's by a stray period no longer leaves a ghost pending item
  (the 2026-08-04 "Team 1-1s rename kept showing pending" bug). Status, priority,
  due and team still compare exactly.
- The protocol functions are unit-tested by extracting them from the built page and
  running them in JavaScriptCore (`osascript -l JavaScript`, `new Function` for
  parse-only syntax checks - node is not installed on this Mac). Re-run that harness
  when touching `migrateStamps` / `pruneAcked` / `softNorm` / `fieldMatches`.

**Chrome tab hygiene (same date):** the morning run no longer opens Chrome at all -
the frame cannot paint in a background tab, so a daily tab was pure litter. Nothing
in this skill or `/chief-of-staff` should navigate Claude-in-Chrome to the artifact
on a scheduled run. In an interactive session, reuse the session's existing MCP tab
(`tabs_context_mcp` first, navigate the tab you already have) instead of creating a
new one, and close any tab you created before finishing.

**Never reintroduce:** a collapsed `<details>`, a `max-height`, or an inner
scroller on the diff. Each one reduces a reader to a bare count. On 2026-08-03/04
the morning run reported "3 changes not yet in the ledger" and nothing else; per the
root-cause correction above that was the hidden-tab blank rather than the collapse,
but the rule still stands for Nir reading the bar himself in a foreground tab.

**Change lines carry ~300 chars of answer text, not 80 (raised 2026-08-04).** The
truncation in `collectChanges` applies to `c.text`, which is the *same* string the
*Copy for Claude* button puts on the clipboard. So the old 80-char answer cap was
not a screenshot-only limitation: Nir's longer answer edits were being cut off on
the paste path too and never round-tripped into the ledger. Caps are now 300 chars
for answers and 90 for titles, both with a visible `…` when they do bite. If you
tighten them again you re-break the paste path, not just the screenshot.

**What does not work, verified 2026-07-30 - do not retry these:**
- `computer` clicks never reach the sandboxed artifact frame (`*.frame.claudeusercontent.com`).
  Clicking Theme, Expand all, and "Copy for Claude" all no-op. So the agent cannot
  press the copy button on Nir's behalf.
- `read_page` / `find` cannot see into the frame - the a11y tree stops at the iframe.
- `javascript_tool` runs on the `claude.ai` top origin; the frame's `localStorage`
  throws `SecurityError`, and navigating to the frame URL directly redirects back
  to `claude.ai`, so storage is unreachable that way too.
- No artifact runtime capability fixes this: this user has `downloads` and `mcp`
  only, no shared/persisted state.

Because clicks cannot reach the frame, the run can never expand a collapsed
section itself. That is why anything the run must read has to render expanded by
default. (The 2026-08-04 observation that clicking the collapsed "Show the N pending
items" toggle "blanked the frame" is superseded: per the 2026-08-05 diagnosis the
frame had never painted, because the tab was hidden.)

**Dedupe is exact-match, so near-duplicates survive.** `reconcileWithLedger`
matches a locally-added task to a baked one by normalized title (lowercased,
whitespace-collapsed). A typo defeats it: "elevnlabs partnership" did not match
the ledger's "ElevenLabs partnership" and stayed flagged as new. This is
deliberate - fuzzy matching risks silently dropping genuinely distinct tasks - so
when a pending item looks like something already in the ledger, say so and let Nir
clear it rather than auto-merging.

Asking him to paste remains the fallback when Chrome is not connected. Either way,
forgetting now costs nothing: the edits wait for the next run instead of vanishing.

### Branding

Pull tokens from `references/design-system/` (start at its `README.md`) for
exact values; otherwise use this documented fallback so it always renders
on-brand:
- Accent / primary: Riverside purple `#5A4FF3` (headings, tile borders, links).
- Overdue: `#E5484D` (red). Blocked/CNF: also red, with a "blocked" chip.
  Due-soon: `#F5A623` (amber). Neutral counts: accent or muted grey.
- Surface: white (light) / `#14121F` (dark); text follows the viewer's theme.

Clean and scannable - an internal ops dashboard, not a marketing page.

### Layout and interaction

- **Snapshot bar** top: four stat tiles - Open, Overdue, Due this week,
  Blocked/CNF - each with the org total.
- **Team tiles** in a responsive grid, My tasks → MOPs → SEO → Paid → Creator →
  Growth Channels → SDR (→ Other/unassigned if non-empty). Each tile: team +
  lead, the Open headline, and Overdue / Due-soon / Blocked sub-counts
  (color-coded), plus optional "closed 7d".
- **Click a tile to drill in:** expands (native `<details>`/`<summary>` or a tiny
  vanilla-JS toggle - no external library) to that team's item list. Each row:
  task name (linked to its Monday pulse for `board` items, or its source for
  `feed` items), status, priority (CNF shown as a red "blocked" chip), and the
  **ETA** (the `Due` field; "no date" if blank). Render a leading checkbox on
  each open item as a visual to-do marker (Done items shown checked +
  struck-through); note that a click in the published page does not persist -
  completion is recorded in the ledger via FEED mode, see the caveat below.
- **Empty tile:** team name + "No open tasks", greyed. Never dropped.
- **Footer:** "Live as of [run time]. Feed teams as of their last update." List
  any source not reachable this run.

### HTML skeleton (fill from live data)

```html
<main class="dash">
  <header>
    <h1>Growth Marketing team tasks</h1>
    <p class="asof">[Weekday, Month DD, YYYY]</p>
  </header>

  <section class="snapshot">
    <div class="stat"><span class="n">[open]</span><span class="l">Open</span></div>
    <div class="stat overdue"><span class="n">[overdue]</span><span class="l">Overdue</span></div>
    <div class="stat soon"><span class="n">[due7]</span><span class="l">Due this week</span></div>
    <div class="stat blocked"><span class="n">[cnf]</span><span class="l">Blocked / CNF</span></div>
  </section>

  <section class="tiles">
    <!-- one <details> per team, My tasks first -->
    <details class="tile">
      <summary>
        <span class="team">My tasks</span><span class="who">Nir Taranto</span>
        <span class="counts">
          <b class="open">[open]</b>
          <b class="overdue">[overdue] overdue</b>
          <b class="soon">[due7] due soon</b>
          <b class="blocked">[cnf] blocked</b>
        </span>
      </summary>
      <ul class="items">
        <li>
          <a href="[pulse URL or source link]">[task]</a>
          <span class="meta">[status] · [priority] · [due or "no date"] · [source/board]</span>
        </li>
      </ul>
    </details>
  </section>

  <footer>Live as of [run time]. [Unreachable sources, if any.]</footer>
</main>
```

Style inline in the page `<head>` `<style>` block. Keep JS to a tiny theme-aware
toggle only if you go beyond native `<details>`.
