# p1-p2-followup config

Stable lookup cache so the skill body stays readable and a scheduled cloud run needs only
this file. Source of truth is `references/monday_boards.md` and `references/team.md` - if
anything here looks stale (weekly group IDs rotate, columns get added), re-verify against
those and against `get_board_info`, then update this file.

> Board schemas last copied from `references/monday_boards.md`: 2026-07-12.

---

## Owner (single owner - this is a personal agent)

| Field | Value |
|-------|-------|
| Name | Hanan Amos |
| Monday name match | `Hanan` |
| Monday user id | `97582758` |
| Slack ID | `U0A3HCFE90S` |
| Work email | `hanan.amos@riverside.com` |
| Google Calendar id | `hanan.amos@riverside.fm` (note: `.fm`, not the `.com` work email; timezone `Asia/Gaza`, verified via `list_calendars` 2026-07-12). Always re-resolve via `list_calendars` at runtime rather than trusting this. |

Teammate / executor names used to route Track B (nudge) items:

| Person | Role | Monday match |
|--------|------|--------------|
| Jonathan Galili | MOPs engineering | `Galili` / `Jonathan Galili` |
| Milutin | Website developer, Flow Ninja (executes) | `Milutin` |
| Dusan | Website developer, Flow Ninja (executes) | `Dusan` |

Davor (Flowout) finished the week of 2026-09-20. An item still assigned to him needs reassigning, not a nudge: flag it to Hanan.
| Eyal Katz (mvpGrow) | HubSpot vendor (executes) | `Eyal` / `mvpGrow` |

---

## Boards

### A. Marketing Operations Tasks - `6257866754` (primary)
- Active filter: `status` `not_any_of [1, 3, 9]` (excludes Done, Cancelled, Test is Closed).
- Group filter: exclude `Backlog` (`new_group45625`) and `On Hold` (`group_mky6rv54`).
  Everything else (weekly date-range groups, `New Requests` `topics`, `Open Tests`
  `group_mkz33gap`, `Nir's Requests` `group_mm1cth4j`) counts as active.
- Columns to fetch: Name `name`, Owner `person`, Status `status`, Priority `priority_1`,
  Due `date`, Effort `numbers`, Duration `numeric_mkramvy5`.

### B. Website Development - `18397093471`
- Active filter: `status` `not_any_of [1, 8, 12]` (excludes Done, Published, Close).
- Group filter: exclude `New Tasks` (`group_title`), `Long-term Projects`
  (`group_mm05scnw`), `Backlog / Archive` (`group_mm3bkpvy`), `New Group`
  (`group_mm0kkx7p`).
- Columns: Name `name`, Requester `multiple_person_mm05dcf4`, Assignee `person`,
  Status `status`, Priority `color_mm051fmh`, Due `date4`, Hours EST `numeric_mm05r2x2`.
- Hanan is usually the **requester** here; Flow Ninja (Milutin/Dusan) execute. So Website Dev items are
  almost always Track B (nudge), not Track A.
- Priority column mixes legacy + new labels - only match the new P0-P4 scheme (see IDs
  below). Ignore legacy Urgent/High/Mid/Low/PO for the P1/P2 test.

### C. HubSpot Projects // Eyal mvpGrow - `18413613511`
- Active filter: `status` `not_any_of [1]` (excludes Done).
- Columns: Name `name`, Owner (Riverside) `multiple_person_mm3fvqdk`, Status `status`,
  Priority `color_mm3fs5kr`, Need-by `date_mm3fkez2`, Hours `hour_mm3fg770`.
- Eyal/mvpGrow executes; Hanan is Riverside-side owner. So these are Track B (nudge),
  and a P1/P2 item **missing a need-by date** is a nudge-worthy blocker (vendor can't
  schedule it).

URL pattern for descriptions: `https://riversidefm.monday.com/boards/<BOARD_ID>/pulses/<ITEM_ID>`

---

## Priority label IDs (P1/P2 only - the qualifying set)

| Board | Priority column | P1 id | P2 id |
|-------|-----------------|-------|-------|
| MOPs Tasks `6257866754` | `priority_1` | `110` | `109` |
| Website Dev `18397093471` | `color_mm051fmh` | `110` | `109` |
| mvpGrow `18413613511` | `color_mm3fs5kr` | `110` | `109` |

(For reference, MOPs P0=`10`, P3=`7`. mvpGrow has no P0; CNF=`10`.)

## Blocked / stalled status IDs (nudge triggers)

| Board | "Stuck / hold" status ids |
|-------|---------------------------|
| Website Dev `18397093471` | Stuck `2`, HOLD `3` |
| mvpGrow `18413613511` | Stuck `2` |
| MOPs Tasks `6257866754` | no dedicated stuck label - use `Pending` `2` + past due as the stalled signal |

**Filter note:** `get_board_items_page` status/priority/group filters compare against the
label **`id`**, not the UI index. Restrict `columnIds` and use a tight filter - the MOPs
board is 900+ items and will blow the 25KB response cap otherwise.

**People-column filter format:** filter an owner (`person`) column with `compareValue:
["person-<id>"]` and operator `any_of` (the bare numeric id returns zero items). So
Hanan-owned MOPs items = `person` `any_of ["person-97582758"]`. Full note in
`references/monday_boards.md` cross-board gotchas.

---

## Calendar

- Calendar: Hanan's primary is the `.fm` account (`hanan.amos@riverside.fm`), not his `.com`
  work email. Always resolve the id and its timezone at runtime via `list_calendars`; never
  hardcode a timezone, use the calendar's own.
- Working window (default): **Sunday-Thursday** (the Israeli work week - Riverside is Tel
  Aviv based; Friday/Saturday are the weekend), `09:00`-`18:00` in the calendar's timezone.
  "This week" = the coming Sun-Thu. Never book Friday or Saturday.
- Event marker (put in every created event's `description`, on its own last line):
  `[p1p2-followup v1 | item:<itemId> | week:<isoWeek>]`
  where `<isoWeek>` is the ISO year-week of the target week, e.g. `2026-W29`.
- `colorId`: focus blocks `9` (Blueberry), nudges `6` (Tangerine). These make the
  agent's events visually distinct and easy to spot/clean up.
- `availability: AVAILABILITY_BUSY` for focus blocks; nudges may use
  `AVAILABILITY_FREE` so they don't block the calendar.

### Sizing focus slots (Track A)
- Each focus task gets its own slot, **20 minutes maximum** (Hanan's preference - short,
  frequent touchpoints, not long blocks). Never batch multiple tasks into one slot and
  never exceed 20 min, regardless of any effort/duration column value.
- Place each 20-min slot in the earliest free Sun-Thu gap; several slots can sit on the
  same day, spaced around meetings.
- Nudges are fixed 15 min each.
