<!-- last-reviewed: 2026-08-26 -->
# Video Projects board - live schema and write plan

Read live on **2026-08-26** from board `18426224074`
("Video Projects | Creative Team 2026", Marketing workspace `6001561`,
folder `16009154`, owner Ari Kuchar), and re-read the same day after Ari added
the three ownership sub-items. This file is the write contract for
`/video-project-intake`. **The board wins over the blueprint** - where the two
disagree, the disagreements are listed at the bottom as findings, not silently
reconciled.

## The one structural fact that changes everything

**A project is a GROUP, not an item.** The board has exactly one group today -
`group_mm654k6h` "Project Name_YYYY_MM (Video Project Template)" - holding **32
items**, and those items are the *stages* (Brief, Creative Pitch, Script,
Concept | Approval …), not projects. `item_terminology` on the board says
"project", which is misleading; ignore it.

So "create the project from the template" means **duplicate the group** and
rename it, never `create_item`.

## Who goes where (settled with Ari, 2026-08-26)

The board deliberately carries **few columns**, so the three people who matter
most at intake live in **sub-items under `Overall Ownership`**, not in columns:

| Person | Where it goes |
|---|---|
| **Creative Owner** | the `Owner` column (`person`) **and** the `Creative Owner` sub-item |
| **Brief Owner** | the `Stakeholder` column (`multiple_person_mm65ayna`) **and** the `Brief Owner` sub-item |
| **Approver** (Abel) | the `Approver` sub-item only |
| Creative supporters | the `Supporter` column |

**`Stakeholder` means Brief Owner on this board.** That is a departure from the
blueprint, which reserved Stakeholder for the Approver - the reason is that a
project only ever has one Approver and it is always Abel, so spending a column on
it buys nothing, while the Brief Owner changes every project and is who gaps
route back to. Keep the meaning consistent on every item you touch: Stakeholder
is never used for anyone but the Brief Owner.

**The Approver is recorded in exactly one place - the `Approver` sub-item.**
Never infer it from an avatar, a column position, or the fact that Abel approves
everything anyway.

## Columns (ids are what you write to)

| Column | id | Type | Notes |
|---|---|---|---|
| Name | `name` | name | |
| Owner | `person` | people | the **Creative Owner** |
| Supporter | `multiple_person_mm65wtpb` | people | the creative supporters named in the brief (A4 "Creative team") |
| **Stakeholder** | `multiple_person_mm65ayna` | people | **the Brief Owner** - see above |
| Stage | `status` | status | labels below |
| Timeline | `timerange_mm658355` | timeline | `{"from":"YYYY-MM-DD","to":"YYYY-MM-DD"}` |
| Subitems | `subtasks_mm65k73g` | subtasks | linked board `18426224380` |
| **Channel** | `color_mm65t4z3` | status | **this is the blueprint's "Type"** - see labels below |
| Priority | `color_mm65yd17` | status | `Urgent` / `Mid` / `Low` |
| Link | `link_mm65fjjs` | link | `{"url":"…","text":"…"}` - where the brief pointer goes |
| monday Doc v2 | `direct_doc_mm65yq1w` | direct_doc | |

**Stage labels (exact strings):** `Not started`, `In progress`, `In review`,
`Approved`, `Blocked`.

**Channel labels (exact strings):** `Acquisition`, `Brand awareness`,
`Feature Release`, `Website`, `Other`. Note the lowercase *a* in
"Brand awareness" - the blueprint writes "Brand Awareness". Write the live
string. There is also a blank label at index 5 (the unset state); never target it.

**Always pass `create_labels_if_missing: false`.** A typo must fail loudly, not
invent a sixth Channel label on a shared board.

**Write status/Channel values by label text** (`{"label":"Feature Release"}`),
never by index. The `id` and `index` fields in the board settings differ from
each other (e.g. `Not started` is id 3, index 0), and getting that backwards
silently sets the wrong label.

### Subitem board `18426224380`

Columns: `name`, `person` (Owner), `status` (`Stuck` / `Working on it` / `Done` -
a *different* vocabulary from the parent Stage column), `date0` (Date).

Intake writes to exactly three sub-items, all under `Overall Ownership`, and
sets only their `person` column:

| Sub-item | Template id (read-only) | `person` gets |
|---|---|---|
| `Brief Owner` | `12901731347` | the Brief Owner |
| `Creative Owner` | `12901746798` | the Creative Owner |
| `Approver` | `12901729855` | Abel (`23320016`) |

Those ids belong to the **template's** sub-items. `duplicate_group` mints new
ids for sub-items exactly as it does for items - resolve them by name inside the
new group's `Overall Ownership`.

## The template group's 32 items, in board order

`Overall Ownership` · `Brief (and Scope)` · `Slack channel: #` ·
`Creative Pitch | Create` · `Concept | Approval` · `References` ·
`Script (3 Rounds)` · `Script | Approval` · `Storyboard` · `Video Board` ·
`Video Board | Approval` · `Budget` · `Talent` · `Talent | Approval` ·
`Location` · `Production Design` · `Pre-Production Meeting` · `Production Day` ·
`Editing (3 Rounds)` · `Music Approval (if neccesary)` · `VoiceOver` ·
`Offline | Approval` · `Send Offline to Motion` · `Motion (3 Rounds)` ·
`Sound Design` · `Subtitles (if neccessary)` · `Copy Proofing` · `Color` ·
`Final Approval` · `Resize for Channels (Select Relevant)` ·
`Upload and Send Final Video Files` · `Results - Learnings (From Brief Owner)`

**Thirteen** of them carry sub-items: Overall Ownership (3), Brief (3),
Creative Pitch (2), Script (3), Budget (3), Talent (3), Location (2),
Production Day (3), Editing (3), VoiceOver (3), Sound Design (4), Resize (4),
Upload (3). Typos (`neccesary`, `neccessary`) are the board's; match them
exactly when looking an item up by name, and do not "fix" them during intake.

The seven approval items (`Concept | Approval`, `Script | Approval`,
`Video Board | Approval`, `Talent | Approval`, `Offline | Approval`,
`Music Approval (if neccesary)`, `Final Approval`) are where the gating build
will do its work. **Intake writes nothing to them** - the Approver is already
recorded once, on the `Approver` sub-item, and repeating it seven times would
create seven places for it to drift.

## Write plan (what a confirmed intake executes, in order)

> **Template ids are for reading only.** `duplicate_group` mints new ids for all
> 32 items and every sub-item. After duplicating, read the new group back and
> resolve everything **by name**. Writing to a template id would edit the
> template itself - the single most damaging mistake available here.

1. `duplicate_group(board_id: 18426224074, group_id: "group_mm654k6h", group_title: "<Name>_<YYYY>_<MM>", add_to_top: true)`
2. Read the new group back: `get_board_items_page` filtered to the new group id,
   `includeSubItems: true`. **Verify 32 items landed** and that the thirteen
   sub-item-carrying parents still have their sub-items - in particular that
   `Overall Ownership` has its three ownership sub-items. If either check fails,
   stop and report; do not paper over a partial duplicate.
3. `change_multiple_column_values` on `Overall Ownership`:
   `person` = Creative Owner, `multiple_person_mm65wtpb` = supporters,
   `multiple_person_mm65ayna` = **Brief Owner**, `color_mm65t4z3` = Type,
   `timerange_mm658355` = deadline (if the brief gives one).
4. `change_column_value` on each of the three `Overall Ownership` sub-items,
   setting `person`: `Brief Owner`, `Creative Owner`, `Approver` (Abel).
5. `change_multiple_column_values` on `Brief (and Scope)`:
   `link_mm65fjjs` = `{"url": "<brief doc url>", "text": "<doc title>"}`,
   `multiple_person_mm65ayna` = Brief Owner (gaps are theirs to fill, A2).
6. `create_update` on `Overall Ownership` with the intake record (below).
7. Optional, separately confirmed: Slack channel, then rename
   `Slack channel: #` to `Slack channel: #<name>` and set its `link_mm65fjjs`.

People columns take `{"personsAndTeams":[{"id":<monday user id>,"kind":"person"}]}`.

### Stage is deliberately left untouched

Intake sets no Stage value anywhere. Stages move under the gating model (A5),
which is not built yet, and a project whose Brief item reads "Approved" before
any gate exists would be a lie on the board. The duplicated items keep the
template's blank Stage. This is the first thing the gating build should pick up.

### The intake record (posted as an update)

The three people now have real homes on the board, so the update only carries
what still has nowhere else to live - the feedback pool, the creative-effort
estimate, the pre-gate decision, and any open brief gap:

```
Intake confirmed by Raz Messing on <date>.
Brief: <doc title> - <url>
Type: <Channel label>
Feedback pool: <names> (advisory, does not gate)
Creative-effort estimate: <high|medium|low>
Deadline: <date>
Raz pre-gate: <on|waived|n/a>
Open brief gaps routed to the Brief Owner: <list, or "none">
```

## The brief template Doc

**Default: `1CiPRkspaWJG8Ee29an88NiqeLo9WwIFXa8oWd7HZgJ0`** - "[Template]
Creative video brief", owned by raz.messing@riverside.fm, actively maintained
(last modified 2026-08-26).

`17bpQApat7n90Lt4JbjkJDZiO-bK5M6aEu8kbbBDKoJw` - "[Project] Creative video
brief", same owner - is **byte-for-byte the same structure** under a `[Project]`
title, created 2026-08-10 and untouched since. It is a per-project copy, not a
second template. Checked 2026-08-26; use the `[Template]` doc.
`references/video-creative-brief-templates.md` holds the readable snapshot and
still cites the `[Project]` id - harmless, since the content is identical.

## monday user ids (resolved live 2026-08-26)

| Person | monday id | Role at intake |
|---|---|---|
| Abel Grünfeld (`abel@riverside.fm`) | `23320016` | **Approver, every type** |
| Raz Messing | `73570317` | gatekeeper / trigger / internal pre-gate |
| Stav Sobolev | `26794898` | motion |
| Sivan Mazuz (`sivan.mazuz@riverside.fm`) | `74302414` | pool: Feature Release, Website |
| Alon Livneh | `97633439` | pool: Feature Release (PMM) |
| Galya Nash | `72323897` | pool: Feature Release (PMM) |
| Raz Navon | `97365904` | pool: Acquisition |
| Jarred Berman | `104433446` | pool: Acquisition (red-flag reviewer) |
| Nir Taranto | `66150217` | Acquisition, **FYI only - never gating, never chased** |

Resolve anyone not listed with `list_users_and_teams` by name and **confirm the
match before writing it** - the account holds several near-duplicate names
(three "Raz", two "Sivan", "Jared" vs "Jarred"). Never guess an id.

Creative Owners are **read from the project, never hardcoded** (A2). The Brand
team's candidates live in `references/team.md`.

## Blueprint-vs-board findings

Recorded so the next build does not re-derive them. None of these were changed
on the board; the board is the source of truth.

| Blueprint says | Board actually has |
|---|---|
| a **Type** column | a **Channel** column (`color_mm65t4z3`), same five values |
| the **Approver** goes in the Stakeholder column | Stakeholder holds the **Brief Owner**; the Approver has its own sub-item. A9's intent - one designated place, never inferred - is kept; the place is different. |
| status vocab `Not started / Working on it / In review / Blocked / Done` | `Not started / In progress / In review / Approved / Blocked` |
| "every work item links to where the work lives via the **Figma / Dropbox / Other** columns" | one `Link` column and a `monday Doc v2` column |
| **2** revision rounds per stage (A6) | `Script (3 Rounds)`, `Editing (3 Rounds)`, `Motion (3 Rounds)` - the A6 note about realigning these is still outstanding |
| spine stage "**Designed Storyboard**" | `Storyboard` |
| spine stage "**Concept**" | `Creative Pitch \| Create` (work) + `Concept \| Approval` (gate) |
| "the **Brief** line item" | `Brief (and Scope)` |
| brief carries **Brief Owner**, **Creative team**, **Type**, **Creative-effort estimate** | the live template Doc has none of the four - collect them at intake and write them to the sub-items, columns, and update above |
| the PMM "**Galia**" | **Galya Nash** |
| projects are rows | projects are **groups**; rows are stages |
