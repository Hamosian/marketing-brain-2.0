# Task ledger - per-person action items over time

Loaded by `/chief-of-staff` to render the **Task ledger** section: a
per-person read of open work across Nir's six leads plus Nir's own tasks, framed
as past / present / future so Nir can stay on top of what he owns and what he is
waiting on. This is the text read; the clickable version is
`/growth-marketing-team-tasks` (the two share the boards and definitions below).

Keep this out of the daily critical path if a board is slow: the decisions,
calendar, and org pulse are the required brief. The ledger is a high-value add,
not a blocker - if a board is unreachable, render the tiles you have and note
the gap.

## Who the ledger tracks, and where the data comes from

The six function leads plus Nir's own items. **`references/team-task-registry.md`
is the single source of truth** for each team's source type and location - load
it and follow it. Most teams are `feed` (a repo-backed ledger the
`/growth-marketing-team-tasks` skill maintains from docs/text/Slack); MOPs is
`board` (read live from Monday - none today, and none expected). This ledger reads
the same sources as the dashboard so the text brief and the dashboard never disagree.

**Note (updated 2026-08-05):** the whole brief is now feed-sourced. The Monday
board pulls that Step 1.A used to run for decisions, approvals, go-lives and org
pulse were dropped at Nir's instruction ("nothing to take from there"), so these
ledgers plus Slack are the entire work-state picture. Do not reintroduce a board
read here.

| Row | Person | Slack ID | Source | Read from |
|-----|--------|----------|--------|-----------|
| My tasks | Nir Taranto | `U07LETHMPAP` | `feed` | `.claude/skills/growth-marketing-team-tasks/data/my-tasks.md` (+ optional MOPs `Nir's Requests` group `group_mm1cth4j`) |
| MOPs | Hanan Amos | `U0A3HCFE90S` | `feed` | `.claude/skills/growth-marketing-team-tasks/data/mops.md` (Hanan's team also runs the MOPs Monday board operationally; not read for this ledger) |
| SEO | Erika Varangouli | `U06R47T4ASJ` | `feed` | `.claude/skills/growth-marketing-team-tasks/data/seo.md` |
| Paid | Raz Navon | `U0A31DAME0G` | `feed` | `.claude/skills/growth-marketing-team-tasks/data/paid.md` |
| Creator | Savion Ron Shemesh | `U09340B5HCM` | `feed` | `.claude/skills/growth-marketing-team-tasks/data/creator.md` |
| Growth Channels | Savion Ron Shemesh (covering since Dor Druker's departure, 2026-08-04) | `U09340B5HCM` | `feed` | `.claude/skills/growth-marketing-team-tasks/data/growth-channels.md` |
| SDR | Nir Taranto (owns directly; Ayelet IC) | `U07LETHMPAP` | `feed` | `.claude/skills/growth-marketing-team-tasks/data/sdr.md` |

## Reading each source

- **`feed` teams** - read the team's ledger file. Each row is already in the
  standard format (task, owner, status, priority, due, source, added, updated);
  use it directly. A ledger with only a header and no rows means the team has not
  been fed yet - show "no tracked tasks yet (feed via `/growth-marketing-team-tasks`)".
- **`board` teams** - none today; the type is retained as an option. If the
  registry ever marks a team `board`, reuse the relevant Step 1.A board pulls
  (do not re-query), exclude the backlog / on-hold / un-triaged groups per
  `references/monday_boards.md`, and attribute by owner.

`CNF` priority (or status `Blocked`) marks a blocker - surface these prominently;
they are the "track CNFs" signal.

## Past / present / future

Per person, against the run date ("today"):

- **Present (open now)** - active items, **neither `Done` nor `Watch list`**. The
  headline count. `Watch list` (added 2026-08-04) is finished work Nir is still
  monitoring, so it is closed: counting it as open would inflate his open numbers
  with completed work forever. Mention watch-list items only if one is relevant to
  a decision, never in the Open / Overdue / Due-this-week counts.
- **Overdue** - open **and** due date before today. Always call these out; they
  are the reminders Nir asked for.
- **Future (upcoming)** - open **and** due within the next 7 days.
- **Past (velocity, optional)** - items closed (Done, status `1`) in the last 7
  days, counted by owner. A throughput proxy for "over time". Show only if the
  extra Done pull is cheap this run; never let it block the brief. The deeper
  "over time" trend lives in the periodic reports Step 1.D already reads - link
  those, do not re-derive them here.

An open item with no due date counts as Present, never Overdue or Future; label
it "no date".

## Render format (the Task ledger section)

**Cadence (changed 2026-09-02):** the full per-person table below renders on the
**Sunday run only**. Mon-Thu the brief renders exceptions only - rows that are
overdue on a *stated* (not agent-inferred) due date, blocked/CNF, or changed since
yesterday - folded into the brief's Act / Changed / Nudges sections. The daily
standing view is the dashboard, not a re-printed table.

On Sunday: one line per person, My tasks first, then the six leads. Keep to counts
plus the single most urgent item per person - the full item list is what the
dashboard is for. **Line format, never a Markdown table:** the brief posts to Slack,
which drops table rows silently (see the "Never post a Markdown table to Slack" hard
rule in `SKILL.md`). One bold-led line per person, counts as `open/overdue/due` then
the most urgent item.

```text
### Task ledger

- *You (Nir)* - 5 open, 1 overdue, 2 due this week. [Approve Q3 paid budget](url), 2d overdue.
- *Hanan (MOPs)* - 12 open, 2 overdue, 4 due this week. [Webhook fix go-live](url), due today.
- *Erika (SEO)* - 6 open, 0 overdue, 1 due this week. [Migration ETA](url), due Fri.
- ...
```

Rules:
- Every tracked person gets a row, even at zero: write "0" and "None" rather
  than dropping the row. For a function not yet fed, write "no
  tracked tasks" in Most urgent.
- "Most urgent" = the overdue item with the highest priority, else the
  nearest-due open item. `feed` items have no Monday pulse, so cite the row's
  `Source` (a doc link, a Slack permalink, or "pasted <date>") instead of
  fabricating a board URL.
- If a board was unreachable, add a line under the table naming it, and do not
  fabricate the affected counts.
- Close the section with one line pointing to the visual:
  "Full drill-down: run `/growth-marketing-team-tasks` for the clickable
  dashboard."

## Reminders

Overdue items on stated dates are the "reminders of open tasks" Nir asked for.
They feed the nudge loop (`knowledge/nudge-protocol.md`): the owner gets the
nudge per that protocol's triggers and mode, and Nir's brief carries the outcome.
Items overdue only on an agent-inferred date never trigger a nudge and never
count in the overdue headline - they surface on the Sunday hygiene pass to get a
real date or a kill.
