---
name: data-team-request
description: >-
  Submit or check a request to the Data Team on their "Data requests" monday board. Use whenever
  someone wants the Data Team for an analysis, dashboard, data pull, new pipeline, data infra
  change, A/B test support, or a data spec/doc - or asks "what's the status of my data request",
  "did the data team pick up X", "has the data team started on Y". ALWAYS use this instead of
  touching the Data Team's boards directly - it applies their request-type taxonomy and priority
  scale and knows the intake-board vs ops-board status gotcha. Different board/schema than our
  own Marketing Operations Tasks board and `/pm-story` - don't confuse the two.
---

# Data Team Request

We are a **requester** on the Data Team's boards, not an owner. Load
`systems/reference/data-team.md` first - it has the full column schema, label IDs, and
workflow notes this skill relies on. Two cases:

* **New request** - file it on the intake board.
* **Status check** - find where a previously submitted request actually stands.

---

## New request

### Step 1: Gather the essentials (batch these, don't drip them one at a time)

- **Request Type** - one of: `Analysis`, `Data infra`, `Dashboard`, `Documentation`,
  `A/B test`, `Data spec`, `Pull data`, `Other`.
- **Priority** - present with the real definitions so the user picks correctly (this is a
  different scale than our own Marketing Ops P0-P4/CNF priority - don't conflate them):
  - **Show stopper** - complete blocker, no progress possible until resolved
  - **High** - major impact, real business/user risk, needs fast prioritization
  - **Medium** - meaningful improvement, can wait for normal planning
  - **Low** - nice to have, safe to defer
- **What exactly is needed** - push for specificity (the question/metric/table/dashboard,
  breakdown, time range, and why it matters). Vague requests are the ones that come back
  as "Need clarifications" - tighten it up before filing rather than after.
  Check our own side before filing (which event fires where, what our ad platforms already
  receive) and state the result as a fact. Never put "can you check X" in the request when
  X is Marketing knowledge (CLAUDE.md, "A ticket carries requirements, not research").
- **Needed-by date** - optional.
- **Spec / doc link** - optional, but recommend it for `Data infra`, `Pull data`, and
  `Dashboard` requests; these tend to need a written spec to avoid back-and-forth.
- **Data team member to pick it up** - optional. Leave unset if the user doesn't know; the
  Data Team triages it. Don't guess a name.

### Step 2: Confirm before writing

This is a mutating write to a board owned by another team - always show the assembled
request back to the user and get an explicit go-ahead before creating the item.

- **Stakeholder's team**: default `Marketing` - confirm rather than assume if the request
  is really on behalf of another team.
- **Stakeholder (requester)**: default the current user, resolved via `get_user_context`.
  If the request is on someone else's behalf, resolve their person ID via
  `list_users_and_teams` and confirm before using it.

### Step 3: Create the item

`create_item` on board `18399446834` ("📝 Data requests"), in the `Data team` monday
workspace (`1537478` - not our own Marketing workspace):

- `name`: short title, 5-10 words, same discipline as `/pm-story`
- `columnValues` (column IDs and label sets are in `systems/reference/data-team.md`):
  - `status`: `{"label": "New request"}` - always set this explicitly on new items
  - `long_text_mm0e1x8v`: the elaborated request text
  - `color_mm0e440v`: Request Type
  - `color_mm0enpkh`: Priority
  - `color_mm0edqfa`: Stakeholder's team
  - `multiple_person_mm0ew969`: Stakeholder (requester person ID)
  - `date_mm0ew99d`: needed-by date, if given
  - `linkbm9mth9s`: spec link, if given
  - `multiple_person_mm0eafd5`: Data team member, only if the user named one

If a column's label ID isn't in `systems/reference/data-team.md`, call `get_board_info`
on `18399446834` to confirm it live rather than guessing.

### Step 4: Confirm and set expectations

Return the item URL: `https://riversidefm.monday.com/boards/18399446834/pulses/{item_id}`

Tell the user:
- It lands as "New request" on the intake board. Give them the item ID with the URL: the ID
  is the one handle that survives every move.
- When the Data Team prioritizes it, the item **moves** to the Main operation board
  (`18399485085`) under the same ID and shows `Backlog` there on arrival (an automation sets
  it). Nothing stays behind on the intake board.
- After its quarter closes it can move again, to **Data group past Qs** (`18426192716`),
  where Status reads `Backlog` for every item whatever the real outcome.
- For urgent follow-ups or blockers, escalate in `#data-marketing` (`C08283QUCNM`) rather
  than DMing a Data Team member directly.

---

## Status check

Track by **item ID**, never by title. A request keeps one ID across all three boards
(Workflow in `systems/reference/data-team.md`), the Data Team renames items, and a
same-named item on another board is a separate request.

1. **Get the item ID.** Take it from the URL returned at filing or the link the user has.
   With only a title, search all three boards: `get_board_items_page` with `searchTerm` on
   `18399446834` (intake), `18399485085` (ops) and `18426192716` (past Qs), filtering
   `color_mm0edqfa` = `Marketing` (label id `7`) if it helps narrow. If that misses because
   the item was renamed, the intake board's activity log has the original name and ID on
   its `move_pulse_from_board` event.
2. **Read the item by ID**, which works whichever board it is on. With `all_api_read`:
   `items(ids: [<id>]) { id name state board { id name } group { title } updated_at column_values(ids: ["status"]) { text } }`.
   `board.id` says where it is now.
3. **Read the status according to the board:**
   - **Intake** (`18399446834`): not prioritized yet. Its status is live.
   - **Ops** (`18399485085`): status is live. `Backlog` just after prioritization means
     queued, because every item arrives as `Backlog`.
   - **Past Qs** (`18426192716`): **do not report the Status column**; it reads `Backlog`
     for every item. Get the real status from the activity log: `get_board_activity` on
     `18426192716` with `itemIds: [<id>]` and `includeData: true`. The archive move's
     status change holds the real last status in `previous_value`. For the full history,
     make the same call on `18399485085`.
   - **Empty result or `state: deleted`**: the Data Team deleted it on the ops board.
     `get_board_activity` on `18399485085` with `itemIds` shows the `delete_pulse` event
     and who did it.
4. `get_board_activity` covers only the last 30 days unless you pass `fromDate`. Set it at
   or before the item's creation date, or the history comes back empty.
5. Report the status with its source: the board it is on, or "activity log, read
   <date>" for an archived item.

---

## Safety

- Always confirm the full request with the user before creating the item - this writes to
  a board we don't own.
- Never set someone else as Stakeholder without confirming who's actually asking.
- Don't invent a Data team member assignment - leave it unset unless the user names one.
- Only ever create items on the **Data requests** board. Never create, edit, or move items
  on the **Main operation board** or **Data group past Qs**: those are the Data Team's
  execution and archive surfaces, not ours to write to.

## Writing the spec doc

Bigger requests get a spec doc attached via the intake board's `Spec` link column. The Data
Team reviews it alongside Marketing stakeholders, so it has to serve both audiences at once.
The line that keeps it useful: **Marketing owns the "what" and "why", Data Engineering owns
the "how".**

**Belongs in the spec (ours to state):**

- **Definitions, at the very top, in business language.** Marketing reviewers read the front
  of the doc and stop. If a metric is ambiguous or has competing readings, resolve it there,
  before any technical section. Take the definition from `/rivermind:ask` - the analytics team
  owns the canonical ones (see `preop-data-intelligence` for the MQL/SQL example).
- **The business rule and its rationale.** Eligibility, dedup policy, what earns money and
  what does not, stated as a rule plus a "why".
- **The contract with any external system.** Endpoint, auth model, payload shape, trigger
  semantics, ordering requirements. This is a requirement on the integration, not a data
  decision, and it must stay in the doc - the vendor's API constrains us regardless of how DE
  models the data. Use placeholders (`<lead identifier>`) rather than column names.
- **Integrity requirements that affect money or trust.** Send-once, never-retract,
  target-must-exist.
- **Open items with named owners,** split by who can actually decide.

**Does not belong (theirs to decide, or noise):**

- **Which source tables or columns to read.** Naming a model as *the* source pre-empts their
  design. State the milestone and let them find it.
- **SQL, view DDL, or query logic.** Do not write their queries. Do not restate a
  transformation they own.
- **Your own data analysis.** No volume trends, monthly counts, or funnel breakdowns to prove
  the point. Size commission or cost exposure only if a stakeholder needs it for a decision,
  and even then keep it to a sentence, not a table of months.
- **Logic the Data Team already owns.** If they maintain the definition (e.g. the
  public-vs-business email classification), name it and defer. Never restate its rules -
  restating creates a second source of truth that will drift.
- **Technical explanation aimed at teaching them their own stack.** They know it.
- **Research the requester owes.** "Can you check where X comes from" about our own
  platforms (existing ad-platform conversions, which event fires where, current config) is
  Marketing Ops knowledge. Check it before filing and state the answer, or leave it out.

Run it past the token-efficiency test before sending: every paragraph either states a
Marketing need, states a requirement on an external system, or names an open decision. If it
does none of those, cut it.

## Required Context

1. Load `systems/reference/data-team.md` for the full column/label schema before creating
   or reading any item.
2. For the requester's own identity/person ID, use `get_user_context`; for someone else,
   `list_users_and_teams`.
3. For escalation, use `slack-agent` with `#data-marketing`.
