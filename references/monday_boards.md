# Monday.com Boards

> Board IDs and schemas last verified: 2026-06-12; Marketing Operations Tasks column keys and label IDs re-verified live 2026-08-23 (300-item sample)

Workspace: `riversidefm.monday.com` (Marketing workspace `6001561`)

| Board | ID | Owner | Use |
|-------|----|-------|-----|
| Marketing Operations Tasks | `6257866754` | Hanan + Jonathan | Day-to-day MOps tasks (HubSpot, attribution, reporting, data integrations). Used by `/pm-story` and `/good-morning`. |
| HubSpot Projects // Eyal mvpGrow | `18413613511` | Hanan + Jonathan | External vendor (Eyal Katz at mvpGrow) executing HubSpot work. Intake via form. |
| Website Development | `18397093471` | Jonathan Galili + Hanan (the Web Developer, Jonathan Ydov, runs it from 2026-09-27) | Marketing website pipeline (riverside.com pages, A/B tests, accessibility, localization). Executed by the Webflow agency Flow Ninja (Milutin, Dusan). |
| 2026 MKT Planning | `18396740865` | Nir + leads | Annual / quarterly planning (not a sprints-formatted board). |
| Invoices and Payments - Growth Marketing | `18390740532` | Savion (+ Nir, Erika, Raz, Hanan); created by Dor Druker, departed 2026-08-04 | Vendor invoices and payment tracking, grouped by month. Fed manually, via email intake ("Emailed items" group), and by `/invoice-inbox-to-monday`. |
| Growth Marketing Reports | `18395106969` (subitems `18395107181`) | Savion Ron Shemesh; created by Dor Druker, departed 2026-08-04 | Index for Nir's weekly/monthly per-function reports. One item per period, five subitems (Dor, Raz, Savion, Erika, Hanan) each linking a report doc and carrying a filed/outstanding status - the "Dor" subitem is now filed by Savion. Full schema and read pattern in `references/growth-reporting.md`. Consumed by `/chief-of-staff`. |
| Video Projects \| Creative Team 2026 | `18426224074` (subitems `18426224380`) | Raz Messing (Brand); board created by Ari Kuchar | Creative Ops video pipeline. **One group per project, one item per stage** - not one item per project. Fed by `/video-project-intake`. Held only its template as of 2026-10-01. |
| Design & Creative Team \| 2026 | `8162052483` (subitems `8162053021`) | Raz Messing (Brand, "the Design team"), with Abel, Ari Kuchar, Amir Hemed, Adi Alegresi, Hanan Amos; created by Noam Locker | The Design team's work board: marketing design, motion, performance video, page design, thumbnails, email and in-app visuals. Requesters file here directly; Raz triages into weekly iterations. **No agent creates items here yet** (see its section). |
| Jarred Weekly | `18426843451` | Jarred Ilan Berman | Jarred's own work board (CRO tests, ads, website, creative asks), organized into rotating weekly groups plus `Ongoing`/`Live - CRO`/`Live - Ads` initiative groups. Read by `/weekly-1-1s` for the Jarred-tab agenda; full group/column schema in `.claude/skills/weekly-1-1s/knowledge/jarred-board.md`. |

URL pattern: `https://riversidefm.monday.com/boards/<BOARD_ID>/pulses/<ITEM_ID>`

---

## Marketing Operations Tasks (`6257866754`)

Day-to-day MOps board. Hanan and Jonathan own. 918+ items, growing.

**Default view for full team picture:** [`231836282`](https://riversidefm.monday.com/boards/6257866754/views/231836282) (Table layout, no filter - shows everything).

### Column keys

| Field | Column key | Type |
|-------|------------|------|
| Name | `name` | name |
| Owner | `person` | people |
| **POC** | **`dup__of_assignee`** | people |
| POC (second column, less used) | `peopleeozmsvcu` | people |
| Created by | `creation_log` | creation_log |
| Status | `status` | status |
| Type | `status_11` | status |
| Priority | `priority_1` | status |
| Stage | `status_18` | status |
| Bucket? | `color_mkzspv3r` | status |
| Planned? | `color_mkzt8ef8` | status |
| ~~Weekly Planned~~ | ~~`color_mm08xv00`~~ | status - **vestigial, do not use** (see below) |
| Assets | `files` | **file** |
| Due date | `date` | date |
| Effort (numbers) | `numbers` | numbers |
| Duration | `numeric_mkramvy5` | numbers |
| Timeline | `timerange_mkrap0x3` | timeline |
| Tags | `tags__1` | tags |
| ~~Linked Tickets~~ | ~~`board_relation_mkrj2nbw`~~ | board_relation - **unreadable and unwritable over the API** (see below) |
| link to Marketing Operations Tasks (x2) | `board_relation_mm01n22z`, `board_relation_mm01eakw` | board_relation - works, but **empty board-wide** |
| MKT Planning link | `board_relation_mm0czzd3` | board_relation |
| Website Dev link | `board_relation_mm01eqb4` | board_relation |
| HubSpot URL | `short_text01ee10v7` | text |
| HubSpot work | `multi_selectyy1zfsn6` | dropdown |

> **Three traps in that table, all verified live 2026-08-23 against a 300-item sample.**
>
> **1. Two columns are titled `POC`.** `dup__of_assignee` (65 items populated) and
> `peopleeozmsvcu` (59). **Write and read `dup__of_assignee`** - the `dup__of_*` prefix makes
> it look like the copy, but it is the live one. Reference item `12061561370` has
> `peopleeozmsvcu` empty and `dup__of_assignee` set. This file named the wrong one until
> 2026-08-23. The board really has two; a cleanup to merge them is a separate decision.
>
> **2. `Weekly Planned` (`color_mm08xv00`) is dead.** Its labels were never renamed from the
> monday defaults (`Working on it` / `Done` / `Stuck`) and it is empty on **all 300** sampled
> items. The column that actually carries planning state is **`color_mkzt8ef8` "Planned?"**:
> `Unplanned` `0`, `Planned` `1`, `Stuck` `2` (never write `Stuck`), populated on 225 of 300
> (171 Unplanned / 54 Planned). Any skill reading `color_mm08xv00` as a planning signal is
> reading an empty column and its logic silently never fires.
>
> **3. `Assets` (`files`) is a file column that *does* accept links.** `change_column_value`
> will not touch it and it cannot be set inside `create_item`. Use:
> `update_assets_on_item(item_id, board_id, column_id: "files", files: [FileInput!]!)` where
> each entry is `{fileType: "link", linkToFile: "<url>", name: "<display text>"}`. `fileType`
> also accepts `google_drive`, `dropbox`, `box`, `onedrive`, `doc`, `asset`. Actual binary
> uploads need `add_file_to_column` with a multipart body.

> **There is no working way to link one MOPs ticket to another in a column (verified live
> 2026-10-01).** To tie a follow-up to an earlier MOPs ticket, link the earlier one inside an
> update. A reply on the brief works, and is what `13178778506` carries for `12390037705`.
>
> - **`Linked Tickets` (`board_relation_mkrj2nbw`, titled `LInked Tickets`) is a ghost
>   column.** `get_board_info` lists it and it is not archived, but `column_values` comes back
>   empty on items, and both a write and an `is_not_empty` filter fail with `missing_column`
>   ("Column not found"). A control filter on `board_relation_mm0czzd3` returns items, so this
>   is the column, not the filter. Its `boardIds` never included MOPs: Website testing roadmap
>   `8739806205`, RevOps Sprints `9782867747`, the Data team's `18399446834` and
>   `18399485085`, and `3830066160`, which no longer resolves. The write failure was first
>   logged in the ticket-hygiene ledger on 2026-09-14.
> - **The two `link to Marketing Operations Tasks` columns accept MOPs items but are empty on
>   every item**, so a link written there is invisible in every view. Using one would mean
>   picking it and adding it to the views first, which is a board-owner decision.


### Status label IDs (column `status`)

| Label | ID | Index | is_done |
|-------|----|-------|---------|
| Working on it | `0` | 0 | no |
| Waiting for approval | `7` | 1 | no |
| Pending | `2` | 2 | no |
| Done | `1` | 3 | **yes** |
| New | `6` | 4 | no |
| Cancelled | `3` | 5 | no |
| Waiting to go live | `4` | 7 | no |
| Test is Open | `8` | - | no |
| Test is Closed | `9` | - | no |
| Test paused | `10` | 8 | no |

Active filter: `status not_any_of [1, 3, 9]` (excludes Done, Cancelled, Test is Closed). Note that `Test is Open` (`8`) and `Test paused` (`10`) are intentionally included - open and paused tests are still active work that needs monitoring or a kill/revive decision.

### Priority label IDs (column `priority_1`)

| Label | ID |
|-------|----|
| Critical and time sensitive | `10` |
| P1 | `110` |
| P2 | `109` |
| P3 | `7` |
| P4 | `1` |
| CNF | `0` |

> **There is no `P0` label on this board** (verified live 2026-08-09: `create_item` with `{"label": "P0"}` fails with `ColumnValueException: missingLabel`). Id `10` is labeled `Critical and time sensitive` - map a "P0" request to that label. This differs from the Website Development board, which does have `P0`.

### Type label IDs (column `status_11`)

| Label | ID |
|-------|----|
| Website A/B test | `3` |
| Messaging | `7` |
| Issue/Bugs | `2` |
| Data integration | `19` |
| HubSpot | `6` |
| Biz Process | `8` |
| Reporting/Dashboard | `10` |
| ~~Email blast~~ | ~~`11`~~ - **dead by policy, never write** (see below) |
| Website related | `0` |
| Attribution | `4` |
| Not Set | `5` |

> **`Messaging` (`7`) is the label for *all* outbound messaging, and `Email blast` (`11`) is
> dead.** Counted live 2026-09-02: **`Messaging` 145 items, `Email blast` 5.** `Messaging`
> carries email blasts, newsletters, system and lifecycle emails, campaign QA, in-app
> messages **and** Trendemon on-site messages - e.g. `Email blast - send email to QBDs
> without outcome`, `Winback Email Blast to Control Group`, `Customer.io System Email -
> Privacy Policy Update`, dozens of `Campaign QA - BLAST:` items, and every
> `Trendemon - ...` ticket. **Write `Messaging` for any of it.**
>
> `Email blast` is dead **by policy, not by flag** - confirmed by Jonathan (board owner)
> 2026-09-02. Unlike the deactivated labels below, `is_deactivated` is `false`, so it stays
> selectable in the UI and reads like the obvious choice for an email send. That is exactly
> how it gets picked: 4 items in the board's whole history plus one agent mis-file on
> 2026-09-02. Never write `11`.
>
> A "homepage banner" is also `Messaging` on this board rather than a Website Development
> ticket; that discriminator lives in `systems/owned/trendemon.md`.
>
> **Do not read a label's meaning off a filtered sample.** An earlier version of this note
> said `Messaging` *was* the Trendemon label, generalised from 5-of-5 Trendemon tickets
> without ever asking what else carried it. That note was live for two hours and an agent
> handed an email blast reasoned correctly from it - not Trendemon, so not `Messaging` -
> and picked `Email blast`. Count the label across the whole board, or ask the owner.

> **Write Type by ID, and beware two dead labels.** `deactivated_labels` on `status_11` is
> `[14, 9, 1]` - `Documentation` (`1`), `Attribution` (`9`), `Content` (`14`). Note `9` is a
> **second** label also titled "Attribution"; the live one is `4`. Writing `9` yields a value
> that looks correct over the API and is invisible in the UI. Verified 2026-08-23.

### Bucket? label IDs (column `color_mkzspv3r`)

| Label | ID |
|-------|----|
| Bucket 1: Infrastructure Foundation | `1` |
| Bucket 2: Data, Reporting & Audits | `0` |
| Bucket 3: Campaign Execution | `2` |
| Bucket 4: Lifecycle Strategy | `3` |
| Bucket 5: Work Process &  Work Flows | `4` |
| Bucket 6: Website | `6` |

> **Write Bucket by ID, not by label string.** `Bucket 5` contains a **double space**
> (`Work Process &  Work Flows`) - a single-spaced string match fails silently. Label `5`
> exists on this column with an empty title; never write it. Fill rate 246/300 (2026-08-23),
> so this is a live, actively-maintained field.
### Planned? label IDs (column `color_mkzt8ef8`)

| Label | ID |
|-------|----|
| Unplanned | `0` |
| Planned | `1` |
| Stuck | `2` |

This is the board's **live planning signal** and the MOps-side counterpart to the Website Dev board's `Planned?` (`color_mm059cmf`) - different board, different key, same question. Populated on 225 of a 300-item sample (171 Unplanned, 54 Planned) as of 2026-08-23. `Planned` means the item maps to an initiative on `2026 MKT Planning` (`18396740865`) - the `MKT Planning link` relation (`board_relation_mm0czzd3`) is the evidence for it, so the two should always agree. `Stuck` (`2`) is an unrenamed monday default that carries no agreed planning meaning; do not write it, treat it as unmarked. Do not confuse this column with the vestigial `Weekly Planned` (`color_mm08xv00`) - see the traps note above. Adopting this field on the MOps board was recommendation #2 of the Q1 2026 MOps retro (`retros/2026-Q1-marketing-ops.md`), which also made the planned/unplanned ratio a weekly tracked metric - `/mops-standup` reports it.

> **`color_mm08xv00` ("Weekly Planned") is vestigial - never wire anything to it.** It still exists on the board but kept monday's default labels (Working on it / Done / Stuck) and is **empty on all 300 sampled items** (verified live 2026-08-23). `/mops-standup` read it from launch to prioritise "items marked Weekly Planned," so that signal silently never fired until it was repointed to `color_mkzt8ef8` on 2026-08-23. If you want planned-ness on this board, the column is `color_mkzt8ef8`.

### Tag IDs (column `tags__1`, partial)

| Tag | ID |
|-----|----|
| Hubspot | `28385917` |

Only the tag used by `hubspot-workflow-qa` is confirmed; the full tag list is a knowledge gap (tags aren't enumerable from `get_board_info` the way status labels are - capture more as they're used).

### Groups (verified 2026-07-07) - filter by these, not just status

This board has manual weekly groups the team actually uses for planning - it is easy to mistake "no monday-native sprints" (true) for "no grouping at all" (false). As of this date, 153 of 233 non-Done items sit in `Backlog` and 13 in `On Hold` - those are deliberately shelved, not neglected, and should NOT be counted as active/overdue workload. Re-verify group IDs periodically since weekly groups get created/renamed.

| Group | ID | Meaning |
|-------|----|---------|
| New Requests | `topics` | Raw intake, not yet triaged into a week |
| `DDMM - DDMM` (e.g. `0507 - 0907`) | rotating, e.g. `group_mm4rk3jf` | Weekly buckets, oldest to newest. The bucket spanning today's date is the "current week." Items in past weekly buckets that are still open are genuinely overdue/carryover - keep those in active analysis. |
| On Hold | `group_mky6rv54` | Deliberately paused - **exclude from active/overdue analysis**, note separately if relevant |
| Open Tests | `group_mkz33gap` | Live or paused A/B tests awaiting a kill/keep call - report as its own "needs a decision" bucket, not mixed into overdue work |
| Backlog | `new_group45625` | Long-tail parked work, mostly 2024-2025 legacy - **exclude from active/overdue analysis** |
| Nir's Requests | `group_mm1cth4j` | Requests from Nir Taranto - treat as active |
| Completed | `group_title` | Should already be filtered out by the status filter, but double-check if counts look off |

To filter: use a `group` column filter with `operator: any_of` / `not_any_of` and the group ID(s) above, same as any other column filter.

---

## HubSpot Projects // Eyal mvpGrow (`18413613511`)

External vendor board. mvpGrow (Eyal Katz) executes HubSpot work for Riverside. Hanan and Jonathan are Riverside-side owners. 10 items typical. Intake via form view `263409627`.

> **Item descriptions don't work here.** This is a CRM-product board, and `set_item_description_content` returns `INTERNAL_SERVER_ERROR` on it (fails even with trivial content). When a skill like `/pm-story` needs to attach a Why/What/Done When brief, post it as an item update via `create_update` (HTML body, not markdown) instead. Confirmed 2026-07-12.

### Column keys

| Field | Column key | Type |
|-------|------------|------|
| Name | `name` | name |
| Assignee | `person` | people |
| Owner (Riverside) | `multiple_person_mm3fvqdk` | people |
| Stakeholder | `multiple_person_mm471nf7` | people |
| Status | `status` | status |
| Priority | `color_mm3fs5kr` | status |
| Request Type | `single_selectco0tpty` | status |
| Date | `date4` | date |
| Need-by date | `date_mm3fkez2` | date |
| Hours | `hour_mm3fg770` | hour |
| Please Elaborate | `short_text897bazo8` | text |
| Brief/File | `file_mm3fbeqe` | file |

### Status label IDs (column `status`)

| Label | ID | Index |
|-------|----|-------|
| Planning | `3` | 0 |
| Working (mvpGrow) | `0` | 1 |
| Stuck | `2` | 2 |
| In review by Riverside | `5` | 3 |
| Done | `1` | 4 |

Active filter: `status not_any_of [1]` (excludes Done).

### Priority label IDs (column `color_mm3fs5kr`)

| Label | ID |
|-------|----|
| P1 | `110` |
| P2 | `109` |
| P3 | `7` |
| P4 | `0` |
| CNF | `10` |

### Request Type label IDs (column `single_selectco0tpty`)

| Label | ID |
|-------|----|
| Email audiences | `0` |
| Workflows creation (series) | `1` |
| Email Editor issue | `2` |
| Other | `3` |

### Notes

- **SLA derives from priority**, not from due date. Vendor needs Hanan to set `need-by date` (`date_mm3fkez2`) for proper scheduling - many items ship without one.
- Priority definitions (per the intake form):
  - **CNF** - blocker, no progress until resolved
  - **P1** - significant impact, fast prioritization
  - **P2** - meaningful improvement, standard planning cycle
  - **P3** - nice to have, safe to defer

---

## Website Development (`18397093471`)

Board owners are Jonathan Galili and Hanan Amos; the board was created by Yuval Tsabar, who has left (he is the `creator`, not an owner). The Webflow agency Flow Ninja (Milutin, Dusan; Andrija "Djura" Djuric leads) executes most work, as Flowout's Davor also did until the week of 2026-09-20; Erika is the largest requester. 293 items as of 2026-07-28. Items are grouped into bi-weekly sprints (e.g. `20.07.26 - 31.07.26`).

> Website Dev schema re-verified live 2026-07-28 via `get_board_info`.

### Column keys

| Field | Column key | Type |
|-------|------------|------|
| Name | `name` | name |
| Requester | `multiple_person_mm05dcf4` | people |
| Assignee | `person` | people |
| Content Owner | `multiple_person_mm06rm6k` | people |
| Design Owner | `multiple_person_mm06j32` | people |
| Status | `status` | status |
| Priority | `color_mm051fmh` | status |
| Planned? | `color_mm059cmf` | status |
| Impact | `color_mm0q7krw` | status |
| Website dev needed | `color_mm0qe12z` | status |
| Due Date | `date4` | date |
| Hours EST | `numeric_mm05r2x2` | numbers |
| Website est (days) | `numeric_mm0qqdks` | numbers |
| Design est (days) | `numeric_mm0qfe5r` | numbers |
| Timeline | `timerange_mm0q4s8c` | timeline |
| Order | `text_mm0621az` | text |
| Figma Design | `link_mm05q7wr` | link |
| Brief | `link_mm05cxb3` | link |
| Markup Link | `link_mm0c74hx` | link |
| Staging URL | `link_mm06h542` | link |
| Production URL | `link_mm067vh2` | link |
| Slack Thread | `link_mm5ayy5h` | link |
| QA Doc | `doc_mm5fsegr` | doc |
| Creation log 1 | `pulse_log_mm37v6jj` | creation_log |
| Creation log (legacy date) | `date_mm06bpfs` | date |
| Primary KPI | `dropdown_mm0qw8kh` | dropdown |
| Area of impact | `dropdown_mm0qtycs` | dropdown |
| Expected business impact | `dropdown_mm0qe4r3` | dropdown |
| MKT Planning link | `board_relation_mm0qwr75` | board_relation |
| Webflow pipeline link (2023-2026) | `board_relation_mm08cym8` | board_relation |
| Webflow pipeline link (2025 V2) | `board_relation_mm08f4ke` | board_relation |
| Design team link | `board_relation_mm0gnfev` | board_relation |

> **QA Doc / Slack Thread** (verified 2026-07-21, re-confirmed 2026-07-28 via `get_board_info`): the `marketing-website-page-qa` skill writes its QA doc to the **QA Doc** column (`doc_mm5fsegr`, a monday-doc column) and links the review conversation in **Slack Thread** (`link_mm5ayy5h`).

### Subitems - board `18397201974`

QA steps on this board are frequently filed as **subitems**, not as items. They live on subitem board `18397201974` and carry their own owner and status. Verified 2026-08-11: `QA - University Overview` (`12755455078`), `QA - University Inner Page` (`12755501432`), and `QA - University Getting Started Page` (`12755501714`) are all children of `Riverside University` (`11987250837`), all `Working on it`, all assigned to Galiet Shreiber and Galya Nash - and **none of them appear in a default `get_board_items_page` call**, nor can they be fetched by `itemIds` against `18397093471` (that returns an empty result).

Consequence for any skill reading this board: a plain item pull under-reports live work, and "no ticket exists for this" is unsafe unless subitems were included. Pass `includeSubItems: true`.

### The `status` column lags production - do not read it as truth

Verified 2026-08-23: of six items sampled, **five carried a status that contradicted Slack or the live site**. Delivery on this board is confirmed in a `#webflow-riverside` or `#website-dev` thread reply and the column is frequently never moved afterwards, because the people who ship (Davor, Milutin, contractors) close out in Slack and the people who read the board are elsewhere.

| Item | Column said | Actually |
|------|-------------|----------|
| `12782422367` Pricing Page Update_2026_08 | `Ready for QA` | Live in production since 2026-08-17 17:10 |
| `12837916116` fix video resizer page tab crash | `QA` | Fixed 08-19, reporter confirmed 08-20 |
| `12071776844` Riverside University - Community | `New` | In Markup review since 08-21 |

Consequence for any skill reading this board: **never state that an item is open, stuck, awaiting QA, or unshipped on the strength of the `status` column alone.** Confirm against the item's updates feed (`get_updates`, not the `Update Summary` text column, which is a generated digest carrying its own staleness date) or the linked Slack thread. Precedence table in `references/evidence-standards.md`.

This bites hardest for `/ticket-hygiene`, which pulls `status` in its intake corpus and quotes it in ticket bodies, and for sprint planning, which re-plans finished work when the column is wrong.

### Known data-quality issues (verified live 2026-08-11, 63 active items)

These are board-state facts, not schema. They affect every skill that reads this board - `/mops-standup`, `/p1-p2-followup`, `/nir-weekly-report`, `/nir-monthly-report`, `/ticket-hygiene`.

| Issue | Scale | Why it matters |
|---|---|---|
| **Assignee is a departed employee** (`yuval.tsabar@riverside.fm`) | **18 of 63 active items** | The tickets read as owned, so they are excluded from unowned/intake buckets while nobody is doing them. Any "who is this blocked on" answer computed from the Assignee column is wrong for roughly a quarter of the board. Needs a batch reassignment decision. |
| **Priority column holds a deleted label** - returns a bare `{"index": 5}` object with no label string instead of a P0-P4 value | 10 items | Unfilterable and unreadable. Distinct from the legacy-label problem below: these have no label at all, so a P0-P4 filter silently drops them. |
| **Planning residue in `Q1, 2026 MKT Planning` and `Project Polaris`** - 16 `(copy)` items plus ~15 Project Polaris / Improve Technical Health items, mostly `Stuck` since Jan-Feb 2026 | ~31 of 63 | Half the "active" board is 6-month-old planning scaffolding. It inflates every open/stuck count taken from this board. Neither group is in the un-triaged exclusion list, so they land in active analysis. |

### Unverified columns - do not populate (`mm5m*` batch)

Four columns exist on the board but are **not documented as usable**, and agents must not write to them:

| Field | Column key | Type |
|-------|------------|------|
| Project Resource Link | `text_mm5mz65y` | text |
| Update Summary | `text_mm5mkkv5` | text |
| Development Page Name | `text_mm5m8btq` | text |
| Due Date Priority | `color_mm5mdpa4` | status |

**Provenance** (from the board activity log, retrieved 2026-07-28):

- All four were created by **Hanan Amos** (monday user `97582758`) on **2026-07-26, 07:17:30-07:17:31 UTC** - all four inside a two-second window.
- Four seconds later, `Due Date Priority` had its default monday status labels (`Working on it` / `Done` / `Stuck`) rewritten to `Critical Priority` / `High Priority` / `Standard Priority`.
- Five schema mutations in five seconds is not hand-editing in the UI - something called the API under Hanan's account. It was **not** one of monday's own system actors; those appear in the same log under negative user IDs and did not touch these columns.
- Nothing in this repo or in the `marketing-knowledge` book references these columns by ID or by title, so the caller is not a skill from either repo.
- **Open question:** which tool or agent was running under Hanan's credentials. Confirm with Hanan before keeping or deleting.

**Usage** - populated on only **5 of 293 items**, and always as a *set* rather than independently: the signature of an automated writer filling its own schema, not a field people reach for.

Treat them as **necessity under review**. Do not populate them, do not treat them as required fields, and do not add them to request templates or forms.

`Due Date Priority` label IDs are recorded **only so existing values can be read** - it is not a second priority axis to fill in (the real priority column is `color_mm051fmh`): Critical Priority `0`, High Priority `1`, Standard Priority `2`.

**Decision owners:** Jonathan Galili and Hanan Amos. Once resolved, replace this block by either documenting the columns properly or deleting them from the board.

### Status label IDs (column `status`)

| Label | ID | Index |
|-------|----|-------|
| New | `6` | - |
| Working on it | `0` | 1 |
| Stuck | `2` | 2 |
| Done | `1` | 3 |
| HOLD | `3` | 4 |
| Next item | `4` | 5 |
| QA | `7` | 6 |
| Published | `8` | 7 |
| Ready for live | `10` | 8 |
| Close | `12` | 9 |
| Audit post-live | `13` | 10 |
| Ready for QA | `11` | - |

Active filter: `status not_any_of [1, 8, 12]` (excludes Done, Published, Close).

### Priority label IDs (column `color_mm051fmh`)

Mixed legacy + new schemes - this column has two sets of labels in use.

| Label | ID |
|-------|----|
| CNF | `0` |
| PO (legacy) | `10` |
| P0 | `1` |
| P1 | `110` |
| P2 | `109` |
| P3 | `7` |
| P4 | `8` |
| Mid (legacy) | `2` |
| High (legacy) | `3` |
| Low (legacy) | `4` |
| Urgent (legacy) | `6` |

**Filter caution:** the legacy and new labels coexist. When filtering, decide whether you mean the new P0-P4 scheme or the legacy Urgent/High/Mid/Low/PO scheme.

### Planned? label IDs (column `color_mm059cmf`)

| Label | ID |
|-------|----|
| Planned | `1` |
| Unplanned | `0` |

This is the **Website Development** board's Planned? column. The MOps Tasks board has its own, keyed `color_mkzt8ef8` with a different label set - don't reuse this key across boards.

### Groups (verified 2026-07-07) - filter by these, not just status

- **Bi-weekly sprint groups** - groups like `06.07.26 - 17.07.26` (id `group_mm4hjrh2`, current as of this date) define the planning cadence. **Correction:** the top group in board order is actually `New Tasks` (id `group_title`), not the current sprint - don't assume `top_group` from `get_board_info` means "current sprint."
- Non-sprint groups to treat as backlog/un-triaged, **exclude from "current work" analysis**: `New Tasks` (`group_title`), `Long-term Projects` (`group_mm05scnw`), `Backlog / Archive` (`group_mm3bkpvy`), `New Group` (`group_mm0kkx7p`). As of this date these hold 26+ active items, including some that look like live blockers (e.g. a Stuck item assigned to a departed employee) but are actually just un-triaged clutter, not things anyone is working on this sprint.
- `Project Polaris` (`group_mm133xvm`) and `Q1, 2026 MKT Planning` (`group_mm0qdwja`) are named initiative groups, not backlog - treat as active if the initiative is still live.
- View `235174510` ("Bi-weekly planned vs actual") filters to current sprint + this-week due dates - prefer this view's filter logic over guessing the current sprint group manually.
- To find the current sprint group id, read `get_board_info`'s `groups` list and match the `DD.MM.YY - DD.MM.YY` title spanning today's date - these rotate, so don't hardcode an id as "current."

### Filing a new ticket (rule set 2026-09-29)

Two rules for any agent that creates an item on this board (`/pm-story`, `/ticket-hygiene` intake):

1. **A new ticket goes to `New Tasks` (`group_title`), never to a sprint group.** Pass `groupId: "group_title"` to `create_item` explicitly rather than relying on the top-group default, which changes if someone reorders groups. The sprint groups (`DD.MM.YY - DD.MM.YY`) hold committed work, and the board owners (Jonathan Galili, Hanan Amos, Jonathan Ydov) place tickets into them at sprint planning. An agent never picks a sprint from a due date, a priority, or a "this week" answer. The one exception is a board owner naming a specific sprint in the request itself.
   - **`topics` is not the intake group here.** On this board `topics` is an old sprint, `01.02.26 - 12.02.26`. On Marketing Operations Tasks the same id is the `New Requests` intake group, so reusing the MOPs intake id here files the ticket into a February sprint. Verified live 2026-09-29.
   - **A move is not a new ticket.** A live P0-P2 that `/ticket-hygiene` moves in from Marketing Operations Tasks keeps its sprint placement (`.claude/skills/ticket-hygiene/knowledge/config.md`, "Sprint placement is part of the move").
2. **The brief goes in an update, not the description.** Post Why / What / Done When / Open Questions with `create_update` (HTML body). `set_item_description_content` on this board writes to `direct_doc_mm08wesc`, a doc column nobody has in their view, so the ticket reads as empty. Do not call it here at all: a second copy starts out identical to the update and then drifts from it, and the update is the one the team reads.

> **Why this is a rule.** On 2026-09-29 [`13159469942`](https://riversidefm.monday.com/boards/18397093471/pulses/13159469942) (Video Trimmer and TikTok Video Editor embeds) was filed into the running sprint `28.09.26 - 09.10.26` with its brief only in the description field. It looked like committed sprint work with no details. Both had to be fixed by hand: the item was moved to `New Tasks` and the brief was posted again as an update.

---

## Invoices and Payments - Growth Marketing (`18390740532`)

Growth Marketing's invoice and payment tracking board. Created by Dor Druker (departed 2026-08-04); owners include Nir, Savion, Erika, Raz, and Hanan, with Savion now also covering Dor's former Growth Channels responsibilities. 265+ items grouped by **month** (e.g. `July 2026`), plus an `Emailed items` intake group at the top (`group_mm1fdkmn`) fed by monday's email-to-board - **automations must never touch that group**.

Full column keys, group IDs, and Type label IDs are cached in `.claude/skills/invoice-inbox-to-monday/tracking.md` (verified 2026-07-06). Highlights:

| Field | Column key | Type |
|-------|------------|------|
| Company name | `text_mm4ecyyd` | text |
| Invoice number | `text_mm4ec06z` | text |
| Invoice Sum ($) | `numeric_mky9safm` | numbers |
| Invoice file | `file_mky9xwjy` | file |
| Type | `color_mm0e2221` | status |
| Payment Method | `dropdown_mky9maht` | dropdown |
| Payed by | `multiple_person_mkz6t3jw` | people |
| Date Paid | `date4` | date |
| Overview | `long_text_mm4ednzr` | long_text |

Conventions: item name = vendor short name, optionally with billing context (`Saasmart - For June`). Payment columns (Payed by, Payment Method, Date Paid, Payment Done, Invoice Uploaded) are filled by the person paying, never by automation.

---

## 2026 MKT Planning (`18396740865`)

> Named `FY26 MKT Planning` in older docs; the board's actual title is **`2026 MKT Planning`** (confirmed live 2026-08-23). 426 items. Its `Domain` column (`color_mkzv3btc`, `Marketing OPs` = `0`) is the fastest way to narrow a search to MOPs-relevant initiatives.

Annual/quarterly planning board. **Not a sprints-formatted monday board.** The `MONDAY_SPRINTS_BOARD_ID` slot in skill configs maps here, but skills should skip active-sprint lookups and pull from `Marketing Operations Tasks` (`6257866754`) filtered by status/owner/priority/due date instead.

---

## Video Projects | Creative Team 2026 (`18426224074`)

The Brand team's video pipeline board (Marketing workspace `6001561`, folder
`16009154`). Schema read live 2026-08-26.

**A project is a group, not an item.** The board's one group today,
`group_mm654k6h` "Project Name_YYYY_MM (Video Project Template)", holds **32
items which are the pipeline stages** (`Brief (and Scope)`, `Creative Pitch |
Create`, `Concept | Approval`, ... `Results - Learnings (From Brief Owner)`).
Creating a project means `duplicate_group`, never `create_item`. The board's
`item_terminology` says "project", which is misleading.

| Field | Column key | Type | Note |
|-------|------------|------|------|
| Owner | `person` | people | the **Creative Owner** - dynamic per project, never hardcoded |
| Supporter | `multiple_person_mm65wtpb` | people | the creative supporters named in the brief |
| Stakeholder | `multiple_person_mm65ayna` | people | **the Brief Owner**, not the Approver - the board keeps few columns, so the Approver lives in its own sub-item instead (below). |
| Stage | `status` | status | `Not started` / `In progress` / `In review` / `Approved` / `Blocked` |
| Timeline | `timerange_mm658355` | timeline | |
| Channel | `color_mm65t4z3` | status | this is the workflow's **Type**: `Acquisition` / `Brand awareness` / `Feature Release` / `Website` / `Other` (note the lowercase `a`) |
| Priority | `color_mm65yd17` | status | `Urgent` / `Mid` / `Low` |
| Link | `link_mm65fjjs` | link | where the brief pointer goes on `Brief (and Scope)` |
| monday Doc v2 | `direct_doc_mm65yq1w` | direct_doc | |

Subitem board `18426224380` has its own status vocabulary (`Stuck` /
`Working on it` / `Done`) - a different set from the parent Stage column.

`Overall Ownership` carries three ownership sub-items - **`Brief Owner`,
`Creative Owner`, `Approver`** - each naming its person in the sub-item's
`person` column. The **Approver (Abel, `23320016`) is recorded there and nowhere
else**; never infer an approver from an avatar or a column position, and never
copy it onto the seven `| Approval` items.

Gotchas, all of which have bitten:

- **`duplicate_group` mints new item ids.** Resolve items in the new group **by
  name**; writing to a template item id edits the template itself.
- **Write status values by label text, not index.** Label `id` and `index` differ
  on this board (`Not started` is id 3, index 0).
- **Always `create_labels_if_missing: false`** so a typo fails loudly instead of
  adding a sixth Channel label to a shared board.
- **Item names carry typos** (`Music Approval (if neccesary)`,
  `Subtitles (if neccessary)`). Match them exactly; do not tidy them.
- **No column exists for Brief Owner, feedback pool, or creative-effort
  estimate.** `/video-project-intake` records these in an update on
  `Overall Ownership` rather than adding columns to a shared board.

Full write contract, the 32-item list, resolved monday user ids, and the
blueprint-vs-board discrepancy table:
`.claude/skills/video-project-intake/knowledge/board-schema.md`.

**In use?** As of 2026-10-01 the board held only its template group and no
projects. Video projects were still being filed on Design & Creative Team | 2026
(below): the `Async_2026_09` project group and about 16 standalone video and motion
items since 2026-08-12.

---

## Design & Creative Team | 2026 (`8162052483`)

The Brand org's work board (Raz Messing; inside the department also "the Design
team"). Marketing workspace `6001561`, folder `16009154`, public. 1,079 items as of
2026-10-01; subitems on `8162053021`. The 2021-2024 predecessor is `1631573131`.
Schema and usage read live 2026-10-01.

> **No agent creates, moves or edits items on this board yet.** Filing here waits
> until Raz Messing agrees where new requests land and what a request must carry
> (Jonathan Galili, 2026-10-01). Until then an agent can read the board and draft a
> request for the requester to file themselves.

### How work flows

- **Filing.** The requester creates the item, usually in `Backlog`, with a
  descriptive name, a Due Date and (for template users) the Brief doc, then posts a
  first update tagging @Raz Messing with the copy link, deliverables and date. There
  is no intake form. 75 of 116 items created by people outside Brand between
  2026-06-01 and 2026-10-01 landed in `Backlog`; the rest went straight into an
  iteration group, which skips triage.
- **Triage.** Raz assigns the designer (Owners), sets a status (`Next Up` or a
  waiting status) and moves the item into a weekly iteration group. He often re-files
  Slack asks himself as `Topic_YYYY_MM` with the requester in Stakeholders.
- **Delivery.** Designers post the Figma or Drive link as an update and set `Done`.
  Page designs go to `Dev`, which fires the Website Development automation below.

### Column keys

| Field | Column key | Type | Note |
|-------|------------|------|------|
| Owners | `person` | people | The designer. Requesters sometimes put themselves here; they should not |
| Supporter | `multiple_person_mktrrcx3` | people | Mixed use: a second designer, or the requester |
| Stakeholders | `multiple_person_mkxrhmhy` | people | The requester or brief owner |
| Brief | `monday_doc__1` | doc | Attaches a copy of the "Brief template" doc (template objectId `8162053128`). Read an attached copy with `read_docs` by its own doc id, not the template objectId |
| Status | `status` | status | Labels below |
| Channel | `dup__of_status3` | status | Labels below |
| Priority | `dup__of_status` | status | High `0`, Mid `1`, Urgent `2`, Low `3` |
| Due Date | `date4` | date | |
| Note | `dup__of_priority` | status | |
| Figma | `link` | link | |
| Other Link | `dup__of_link_to_folder` | link | |
| Dropbox | `dup__of_link_to_figma` | link | Almost unused |
| Project | `text9` | text | Rarely used |
| Pages Project | `text_mkyft9xv` | text | |
| Timeline | `timeline` | timeline | Rarely used |
| Impact | `color_mkpefyae` | status | Unused 2026-06 to 2026-09 |
| Website Development | `board_relation_mm0g1m95` | board_relation | Links to `18397093471`; filled by the `Dev` automation |
| Creation Log | `creation_log` | creation_log | Holds the timestamp only; read `item.creator` for who filed it |
| monday Doc v2 | `direct_doc_mm4jn26e` | direct_doc | Unused |

### The Brief template's fields

Project Title, Main Goal, Background and Hypothesis, Target Audience, Platforms
(name the primary one when there are several), Key Messages, Copy (final copy, or a
link to the content doc when longer than two sentences), Deliverables (web page:
mobile/desktop; static ad and video: ratios and length; print: supplier specs),
Deadline (only when there is a real date), References & Additional Notes. Taken from
an unfilled copy attached on 2026-06-15; the template doc itself is not readable
over the API. The doc is attached on 37 of 88 requests from outside Brand
(2026-06-01 to 2026-10-01), and an attached doc is not proof of a brief: some carry
two sentences or the blank template.

### Status labels that mean a request cannot start

Read from the status history, not the current snapshot: bounced items move on, so on
2026-10-01 no item held `incomplete brief`, `Waiting for brief` or `Missing info`.

| Label | Id | Meaning |
|-------|----|---------|
| `Waiting for Content` | `8` | The requester's copy, page content, product UI or footage is not ready. The most common blocker |
| `Waiting for Kickoff` | `108` | Scope was agreed in a meeting, not on the ticket |
| `Waiting for brief` | `17` | No usable brief |
| `incomplete brief` | `19` | Brief too thin to start; set by Raz Messing at triage |
| `Missing info` | `104` | Rarely used |
| `On Hold` | `3` | Parked |
| `Cancelled` | `13` | |
| `Need our feedback` | `102` | Waiting on the requester's review of a draft. A review-loop state, not an intake bounce |
| `Dev` | `4` | Design ready to build. **Fires the Website Development automation** |
| (blank) | `5` | Untriaged |

### Channel labels (`dup__of_status3`)

Acquisition `0`, YouTube Channel `1`, Website `2`, Social `3`, Product `4`, 360°
Campaign `6`, Riverside Events `7`, Web Placements `8`, Sponsorships `9`, Events `10`,
Channel Partnerships `11`, Riverside Podcast `12`, Influencers `13`, Customer Support
`14`, SEO `15`, Creative Internal `16`, Localization `17`, Legal `18`, Google & LP's
`19`, Community `101`, HR & Internal `102`, Sales & B2B `103`, Email Marketing `104`,
Feature Release `105`, Webinar Hub `106`, Brand awareness `107`, Partnerships `108`,
Others `109`, Branding `110`, Affiliates `152`, Mobile App `153`, AI workflow `154`,
Resources & Libraries `155`. `Growth efforts` (`151`) is deactivated.

### Groups

- **Weekly iterations**, titled `Iteration D.M - D.M` (Sunday to Friday, holidays in
  the title). The top group is the upcoming week, not the current one; a new week
  first appears as "Next week" and is then renamed. Unfinished items carry into the
  next iteration. Resolve the current group from the titles; do not hardcode an id.
- **`Backlog`** (`new_group_mkkx92tj`): where requests land and where Raz triages
  from.
- **`Waiting for Dev`** (`group_mkxexraz`): designs waiting on Website Development.
- **`PAYMENTS`** (`group_mkx37064`): freelancer and vendor payments, not requests.
- **Project groups** named `Project_YYYY_MM` (for example `Async_2026_09`,
  `group_mm6zt79r`), one item per stage, duplicated from a template by Ari Kuchar.
- **Templates**: `__Video Project Template__` (`group_mkzmt4fd`) and `Pages Project
  Template` (`group_mkyfe0y5`). Never write to a template item.

### Automations

- **Active:** when Status changes to `Dev` (`4`), create an item on Website
  Development and link it through `board_relation_mm0g1m95`, mapping Name, Priority,
  Due Date, Owners (to Requester) and Figma (to Figma Design). Created by Hanan Amos,
  2026-02-12; 28 items carry the link. **So a page designed here gets its Website
  Development ticket automatically. Never also file one by hand for the same page,
  or the build is ticketed twice.**
- Deactivated or erroring: Noam Locker notifications on `Need Review` and `Done`, and
  a `Dev` move to the Webflow iteration board `5097931363`.

### Role boundary

- **Page builds are Website Development's.** Design designs the page; the build
  ticket comes from the `Dev` automation, or the item is moved to Website Development.
- **HubSpot builds are not Design's.** "We don't have access to HubSpot": Design
  delivers email visuals in Figma and the requester builds the email.
- **On-site message visuals are designed here and served by Marketing Ops.** An
  in-app banner or popup is a Design item for the visual and a Marketing Ops ticket
  for serving it (Trendemon, `systems/owned/trendemon.md`).

---

## Cross-board notes / gotchas

- **No real "sprints" board.** Marketing Ops doesn't run 2-week sprints. Work is tracked on `Marketing Operations Tasks` (day-to-day) and planned on `2026 MKT Planning` (annual / quarterly). Skills should skip `get_sprints_metadata` and filter by status, owner, priority, and due date.
- **Marketing OS state model:** use monday status and item updates to express the operating state: `intake`, `triaged`, `investigating`, `planned`, `executing`, `blocked`, `ready for review`, `shipped`, `measured`, `learned`. If exact labels do not exist on the board, state the OS state in an item update until the board schema is updated. Not in the item description: on MOPs and Website Dev that lands in a doc column nobody has in their view (`/pm-story` Step 7).
- **Filter compareValue uses label `id`, not `index`.** When filtering a status column with `mcp__monday-api__get_board_items_page`, pass the label `id` (e.g. `1` for Done on the Tasks board). The `index` shown in the Monday UI is a different number and will silently return the wrong items.
- **People-column filters need the `person-<id>` form.** To filter an owner/assignee (`person` / `multiple_person_*`) column by a specific user, pass `compareValue: ["person-<userId>"]` with operator `any_of`. The bare numeric id (`["<userId>"]`) silently returns zero items. Resolve `<userId>` at runtime from `get_user_context` (the authenticated user) or `list_users_and_teams` - do not hardcode it here, since IDs can change.
- **Response size:** the Tasks board has 1010+ items (2026-08-11) - always either filter to recent activity, restrict `columnIds`, or use `limit` and a tight filter to avoid the 25KB response cap.
- **`change_item_column_values` reports success and echoes `null` on board-relation writes.** Verified 2026-08-11 writing `board_relation_mm01eqb4`: the response said `"successfully updated"` with the column value `null`, and a follow-up `get_board_items_page` showed the link present and correct. **Always confirm a board-relation write with a read-back, and never treat the echoed `null` as a failure** - retrying on a false negative is how duplicate links get created. `{"item_ids": [<id>]}` is the format to use.
- **Subitems are invisible by default.** `get_board_items_page` omits them unless `includeSubItems: true`, and a subitem cannot be fetched by `itemIds` against its parent board - it lives on a separate subitem board and returns an empty result. Any skill that asks "does a ticket already exist for this?" must include subitems or it will miss live work and create a duplicate.
- **Not every board can link to every board.** Board-relation columns are directional and specific. `Marketing Operations Tasks` owns `Website Dev link` (`board_relation_mm01eqb4`), so MOPs → Website Dev works; **Website Development has no ticket-to-ticket relation column at all** (it links out to MKT Planning, the two Webflow pipelines, and the Design team board `8162052483`, but not to itself or back to MOPs). Two Website Dev items can only be associated with reciprocal item updates. Check the column exists before designing a workflow around linking.
