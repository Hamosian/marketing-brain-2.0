# Team task registry

The source-of-truth for where each Growth Marketing team's tasks come from, and
the standard format every task normalizes to. Read by `/growth-marketing-team-tasks`
(feed and show modes) and by `/chief-of-staff` (the Task ledger section). When a
team's source changes, edit this one file - not the skills.

Two source types per team:

- **`feed`** - free-form input (a Google Doc, pasted text, or Slack messages)
  that the agent parses into tasks and accumulates in a repo-backed ledger file.
  This is the manual, "feed information and build from it" path.
- **`board`** - a Monday board that already holds structured tasks. Read live,
  no ledger. Retained as an option, but **no team uses it today**: Nir tracks his
  curated tasks per team via `feed`, independent of any operational board. (Hanan's
  team still runs the MOPs Monday board operationally; it is not read by this task
  system.)

## Registry

| Tile | Lead | Slack ID | Source type | Source / ledger |
|------|------|----------|-------------|-----------------|
| My tasks | Nir Taranto | `U07LETHMPAP` | `feed` | `.claude/skills/growth-marketing-team-tasks/data/my-tasks.md` (optional supplement: MOPs `Nir's Requests` group `group_mm1cth4j` on board `6257866754`) |
| Marketing Operations | Hanan Amos | `U0A3HCFE90S` | `feed` | `.claude/skills/growth-marketing-team-tasks/data/mops.md` (Hanan's team also runs the MOPs Monday board `6257866754` operationally; not read here) |
| SEO & AI Search | Erika Varangouli | `U06R47T4ASJ` | `feed` | `.claude/skills/growth-marketing-team-tasks/data/seo.md` |
| Paid Acquisition | Raz Navon | `U0A31DAME0G` | `feed` | `.claude/skills/growth-marketing-team-tasks/data/paid.md` |
| Creator Marketing | Savion Ron Shemesh | `U09340B5HCM` | `feed` | `.claude/skills/growth-marketing-team-tasks/data/creator.md` |
| Growth Channels | Savion Ron Shemesh (covering since Dor Druker's departure, 2026-08-04) | `U09340B5HCM` | `feed` | `.claude/skills/growth-marketing-team-tasks/data/growth-channels.md` |
| Inbound SDR | Nir Taranto (owns directly; Ayelet Jacobson is an IC) | `U07LETHMPAP` | `feed` | `.claude/skills/growth-marketing-team-tasks/data/sdr.md` |

Resolve names/IDs from `references/team.md` if the table looks stale. To move a
team from `feed` to `board` (or point `feed` at a specific Drive doc / Slack
channel it should auto-read), edit its row here - the skills adapt.

### Optional per-team input pointer (the "optimise later" path)

A `feed` team can name a persistent input the skill reads automatically instead
of waiting for a paste. Add it in the Source column as `auto: <pointer>`:
- `auto: gdrive:<file-id-or-url>` - a Google Doc/Sheet the skill reads each run.
- `auto: slack:<channel-id>` - a Slack channel whose recent messages it mines.
Until a pointer is set, the team is fed manually (paste or point at input on the
run). None are set today - all six functions + My tasks are manual for now.

`.claude/skills/growth-marketing-team-tasks/data/reading-list.md` (same directory) is **not a team ledger** - it is Nir's
To-read queue (reading material, a distinct object type from tasks), rendered as
the dashboard's 📚 To-read section. No-owner article captures land there instead
of becoming P0 My-tasks rows; a reading item becomes a task only via the
dashboard's "→ make task". Spec: `.claude/skills/growth-marketing-team-tasks/knowledge/dashboard-spec.md`,
"To-read queue".

## The standard task format

Whatever the raw input, every task normalizes to this shape. This is the format
going forward - the dashboard and ledger both assume it.

| Field | Values | Notes |
|-------|--------|-------|
| `Task` | short imperative title | one line; the action, not a paragraph |
| `Owner` | person name | who does it; defaults to the team lead if unstated |
| `Status` | `Open` / `In work` / `Need review` / `1-1 notes` / `Watch list` / `Done` | `Need review`: awaiting Nir's or an owner's review before closing. `1-1 notes` (added 2026-08-02): agenda material Nir is parking for a specific conversation with that lead, not work in flight - it still counts as not-Done so it stays visible, and the dashboard gives it its own teal badge per team. `Watch list` (added 2026-08-04): **the work is finished but Nir is still watching the result** - shipped, now monitoring. It is a *post-Done* state, so it counts as **closed** everywhere work-in-flight is counted (never open, never overdue, never in the Today / This week band) but is **exempt from the dashboard's Hide-done**, so it stays on screen instead of disappearing like a `Done` row. Steel-blue badge, own snapshot tile. Blockers are marked via `CNF` priority. |
| `Priority` | `P0` / `P1` / `P2` / `P3` / `P4` / `CNF` / `-` | `CNF` = blocker, no progress until resolved (matches the Monday priority scheme). `-` when unstated. |
| `Due` (ETA) | `YYYY-MM-DD` / `-` | The task's **ETA / target completion date** - the field the dashboard shows as "ETA". Give every manually-added task one; `-` only if genuinely open-ended. |
| `Source` | link or short note | where it came from (doc URL, Slack permalink, "pasted 2026-07-18") |
| `Added` | `YYYY-MM-DD` | date the task first entered the ledger |
| `Updated` | `YYYY-MM-DD` | date its status/fields last changed |
| `Answer` (optional) | short prose / `-` | the task's resolution or answer, for question/decision tasks (e.g. an owner's reply Nir reviews before closing). Trailing column; `-` when none. Use `<br>` to separate lines. The dashboard renders a "💬 Answer" toggle on any task whose `Answer` is non-empty. |

`board`-type teams map their Monday columns onto these fields at read time (owner
= `person`, status from the board's status labels with Done = `1`, priority from
the board's priority column, due from the date column).

## Ledger file format (`feed` teams)

One markdown file per `feed` team under
`.claude/skills/growth-marketing-team-tasks/data/`. Human-readable and
git-diffable - git history is the "over time" record. One row per task, columns
in the exact order above:

```markdown
# Task ledger - <Team> (<Lead>)

<!-- Maintained by /growth-marketing-team-tasks feed mode. Add/edit rows freely; keep the column order. Dates are YYYY-MM-DD. -->

| Task | Owner | Status | Priority | Due | Source | Added | Updated | Answer |
|------|-------|--------|----------|-----|--------|-------|---------|--------|
| Ship the Q3 SEO cluster brief | Erika | In progress | P1 | 2026-07-25 | pasted 2026-07-18 | 2026-07-18 | 2026-07-18 | - |
```

`Answer` is the optional trailing column (see the format table above). A ledger
may omit it entirely; readers treat a missing `Answer` column as `-` for every
row, so it can be added to one team's ledger without touching the others.

Never delete a `Done` row on the next feed - keep it so the past/velocity view
and git history stay intact. Prune only on an explicit cleanup request.

## Focus order (Today / This week band)

`.claude/skills/growth-marketing-team-tasks/data/focus-order.md` (same directory as the ledgers) stores Nir's manual
ranking of the dashboard's Today / This week focus band and feeds the
chief-of-staff brief's "Today and this week" section. It holds ordered task ids
only - never task content. Membership in the band is computed from each task's
`Due` at render time (Today = due today or overdue; This week = through the work
week's Thursday), so the band can never duplicate a ledger row. Spec:
`.claude/skills/growth-marketing-team-tasks/knowledge/dashboard-spec.md`, "Focus band".
