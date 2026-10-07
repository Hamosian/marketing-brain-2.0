# Jarred Weekly board (`18426843451`)

Jarred Ilan Berman's own monday board (workspace `6001561`, folder `16009167`), created by Jarred. 132 items as of 2026-09-16. Schema read live 2026-09-16 via `get_board_info`.

Not owner-filtered when pulling for `/weekly-1-1s` - the board is already scoped to Jarred's work, so pull by group membership only.

## Column keys (partial - only what this skill reads)

| Field | Column key | Type |
|-------|------------|------|
| Name | `name` | name |
| Owner | `project_owner` | people |
| Collaborators | `people` | people |
| Status | `project_status` | status |
| Priority | `color_mm5h1rer` | status |
| Type | `color_mm5gg7tz` | status |
| Due Date | `date_mm5hs73q` (subitems) | date |

**Do not filter on `project_status`'s `is_done` flag.** It's unreliable on this board: label `Live - CRO` (id `1`) is marked `is_done: true` even though it's an active/live state, not a completed one, while `Done` (id `3`) is `is_done: false`. Group membership (below) is the clean signal - use it instead of this column.

## Groups (verified live 2026-09-16)

| Group | ID | `/weekly-1-1s` treatment |
|-------|----|--------------------------|
| `13-19 September 2026` (current week as of 2026-09-16) | `group_mm761pmh` | **Tasks** |
| `Ongoing` | `group_mm6bfkpx` | **Ongoing Projects** |
| `Live - CRO` | `group_mm50tegx` | **Ongoing Projects** |
| `Live - Ads` | `group_mm5p6zrb` | **Ongoing Projects** |
| `In Progress` | `group_mm6bqkj` | **Tasks** |
| `Reports` | `group_mm6bva1g` | excluded |
| `Backlog` | `group_mm6awtgp` | excluded |
| `CRO Backlog` | `group_mm5p95mv` | excluded |
| `Paused - CRO` | `group_mm5psprk` | excluded |
| `Paused - Ads` | `group_mm5mchz6` | excluded |
| `Done` | `new_group43041` | excluded |
| `On Hold` | `group_mm5hc272` | excluded |
| `No Longer Relevant` | `group_mm5qqg37` | excluded |
| `16-22 August 2026`, `23-29 August 2026`, `30 August-5 September 2026`, `6-12 September 2026` | `new_group29179`, `group_mm6gw3x7`, `group_mm6ra9v3`, `group_mm6yh98m` | **older weekly buckets** - a still-open item here is carryover: fold into **Tasks**, flagged overdue with its original week |

**Rotating weekly groups.** Like the Marketing Operations Tasks board's own weekly buckets, these are titled `DD Month - DD Month YYYY` and rotate. Match the group spanning today's date to find "current week" - don't hardcode an ID as current. Re-verify the group list via `get_board_info` if this table looks stale (new weeks get added, old ones may get renamed or archived).

## People

- Jarred Ilan Berman - monday user id `104433446` (board creator/owner).
- Raz Navon - monday user id `97365904` (confirmed in `.claude/skills/raz-ops/SKILL.md`).
