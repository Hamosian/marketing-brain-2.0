---
name: pm-story
description: "ALWAYS use this skill - do not call Monday MCP tools directly - when the user wants to write, document, update, or create a product story, task, or ticket. Triggered by ANY of these: \"pm-story\", \"write a story\", \"document this task\", \"update this task\", \"fill in this task\", \"write up this task\", \"log this idea\", \"track this\", \"add this to the board\", \"open a task for X\", \"create a task\", \"add a task\", \"create a ticket\", \"open a ticket for X\", \"create a Marketing Ops ticket\", \"log an issue\", \"I found a bug\", \"track this issue\", \"add this to the sprint\", a request to ticket a banner, top bar, popup or other on-site message, or any message that includes a Monday task URL with intent to document or fill in product context. Creating or documenting ONE ticket is this skill; auditing, sweeping or de-duplicating the queues is /ticket-hygiene."
user-invocable: true
---

# PM Story

Two cases - detect from the user's message:

* **New task:** User has an idea with no Monday item yet. Create one.
* **Existing task:** User points to a URL or name. The item exists but may only have a title.

In both cases, the output is always the same: a Why / What / Done When / Open Questions brief, grounded in actual system context, not guesswork, **posted as an item update** (`create_update`, in HTML). Never as the item description: on our boards that lands in a hidden doc column and the ticket reads as empty (Step 7, "Why the update and not the description").

The goal is to exhaust every available context source before asking the user anything.

---

## Step 1: Load the Task (existing tasks only)

If the user gives a URL or name, load the full Monday context in parallel:

* **Item detail** - `get_board_items_page(6257866754)` with the item ID, `includeItemDescription: true`, `includeColumns: true`
* **Item comments** - `get_updates` on the item ID
* **Linked epic** - if `task_epic` has a linked item, fetch it with `includeItemDescription: true`. Also fetch other tasks in the same epic (gives scope and what's being built around this).

If it's a new task, note what the user described and move to Step 2.

---

## Step 2: Identify the System

Keyword-match the task name and any description against the systems table in CLAUDE.md. Read the matching system file - this is mandatory. It contains repo names, service paths, and architecture context needed to ground the brief.

The Systems Reference table in `CLAUDE.md` is the live map - use it rather than any list cached here, since owned systems get added and renamed. Typical matches: HubSpot / workflows / lifecycle to `systems/owned/hubspot.md`, pages / Webflow / CMS to `systems/owned/marketing-website.md`, banners / popups / on-site messages to `systems/owned/trendemon.md`, routing / scoring / syncs to `systems/owned/marketing-ops-automation.md`, dashboards / metrics to `systems/owned/omni-bi.md`.

If the task spans multiple systems, read all relevant files. If nothing matches, read `README.md` and use the systems table there.

---

## Step 3: Saturate Context (all in parallel)

Use the system doc to find repos, service paths, and Slack channels. Then run all of these at once:

### 3a. Deep context (domain-specific)

**If the matching system doc has a `Repos` section** (engineering/data teams):
Use `Glob` and `Grep` on the local repo path (from the system doc) to find files related to the task. Read 2-4 relevant files. You are looking for **product understanding**, not implementation details:
* What does the feature currently do? What can users configure, see, or trigger?
* What are the current entry points / user-facing surfaces?
* Are there any comments, open flags, or notes that hint at known gaps or planned changes?

Do NOT surface file names, function names, or code-level details in the brief. Translate what you find into product/user language.

**If the system doc has NO `Repos` section** (non-engineering teams):
Skip code search. Instead, increase the weight on:
* Monday board history: search for related items on the tasks board
* System doc content: extract more context from the "Known Issues", "Architecture", and "Key Entry Points" sections
* The goal is the same: exhaust available context before asking the user

### 3b. Git history (engineering/data teams only)

Skip this step if the system doc has no `Repos` section.

On the relevant files, run:
```bash
git -C <repo-path> log --oneline -20 -- <relevant-file-paths>
```
Use commit messages to understand what has changed recently. Translate into product context (e.g. "a new creation wizard was recently introduced"), not commit hashes.

### 3c. Slack
Search the relevant system channel and `#growth-marketing-leaders` for recent discussions about the task topic. Use `slack_search_public_and_private` with keywords from the task name.

This surfaces product decisions, user feedback, and open debates that aren't in code or Monday.

---

## Step 4: Section Walkthrough

Walk through each section with the user - one at a time. Don't dump a full draft upfront. For each section:
1. Share your read based on context
2. Ask if it's right and if anything is missing
3. Wait for confirmation or correction before moving on

Do this for **Why**, then **What**, then **Done When** - in that order.

Keep each message short. One section at a time. Use casual language throughout.

Example flow:

```
**Why - here's my read:**
[1-2 sentences from your research]

Sound right, or is there a different pain point driving this?
```

Wait for response, then:

```
**What - here's my read:**
[1-3 sentences on what changes]

Anything missing or different from what you had in mind?
```

Wait for response, then:

```
**Done When - draft:**
- [ ] [scenario]
- [ ] [scenario]
- [ ] [scenario]

Anything missing or wrong here?
```

Once all three sections are confirmed, move to Step 5 (write to Monday). Do NOT ask the user to confirm again - just write it.

---

## Step 5: Draft the Final Brief

Assemble the confirmed sections into the final brief. No need to show it again - go straight to writing to Monday.

---

## Step 6: Task Metadata (new items only, run in parallel with Step 4)

Skip if updating an existing item.

Marketing Ops does not run a sprint board. Do not call `get_sprints_metadata`.

1. **Select the board by who implements it, not by the surface it appears on.** The
   question is *does a Webflow developer have to touch this?*
   - **Yes** - a page, template, component, layout, or in-page element gets built or
     changed in Webflow → Website Development (`18397093471`).
   - **No** - it ships through a platform Marketing Ops operates (Trendemon, GTM, HubSpot,
     CookieHub, any third-party script) → Marketing Operations Tasks (`6257866754`).
   - Genuinely ambiguous **between these two boards** → MOPs, and name the ambiguity in Open Questions.
   - **Neither** - the ask is a commercial decision (a partnership or affiliate proposal, a
     sponsorship, a custom deal) that someone must approve before anything is built → stop and
     tell the user it belongs to the team that owns the decision, before creating anything. Do not
     file it because the follow-on work (a promo code, a PartnerStack link) could run from MOPs;
     the lead cancelled `13101389324` on exactly that reasoning (`/ticket-hygiene` Step 4).

   > **The trap this exists to stop.** "Homepage banner" reads as website work and usually
   > is not. Site-wide **messages** - top bars, banners, popups, slide-ins, in-app messages -
   > are served by **Trendemon**, operated by Marketing Ops, and no Webflow developer is
   > involved (`systems/owned/trendemon.md`). A banner *built into the page* in Webflow - a
   > footer banner, an in-text CRO banner, hard-coded promo HTML - is Website Dev. The word
   > "banner" does not settle it; the delivery mechanism does, and both boards legitimately
   > carry tickets with "banner" in the title. On 2026-09-02 the absence of this rule put a
   > Trendemon homepage banner onto Website Dev, in a sprint group, with an open question
   > asking which contractor would execute it - none of them have Trendemon access.
2. Read `references/monday_boards.md` for board IDs and known column keys.
3. Ask ALL of the following in a single question batch:

**Board** (default inferred from system):
- Marketing Operations Tasks
- Website Development
- 2026 MKT Planning

**Planning bucket** (skip on Website Development: a new item there always goes to `New Tasks`, Step 7):
- This week
- This month / quarter
- Backlog
- Unplanned urgent

**Owner** (default = me):
- Me (default)
- Unassigned
- Someone else

**Priority** (default = Medium):
- Medium
- High
- Critical
- Best Effort

**System / Area** (optional - reads from the Systems Reference table in CLAUDE.md):
- Other / None

**POC** - who is this being done *for* (default = the person asking):
- The requester (default)
- Someone else
- Nobody specific

4. If owner or POC = "Someone else": follow up with `list_users_and_teams` to look up their ID.
5. If owner = "Me": resolve the current user ID at write time via `get_user_context`.

### 6a. Search the planning board (MOPs and Website Dev only)

Before writing, search **2026 MKT Planning** (`18396740865`, 426 items) for the initiative
this task belongs to. Narrow with its `Domain` column (`color_mkzv3btc`; `Marketing OPs` = `0`).

One search drives two fields, so never compute them separately:
- Match found → `Planned?` = `Planned`, and link the planning item.
- No match → `Planned?` = `Unplanned`. That is a real answer, not a gap.

Unlike the unattended intake path, **you have a human here - show them the candidate match
and let them confirm or reject it before linking.** Three mirror columns hang off that
relation, so a wrong link displays another initiative's status, priority and timeline on
this ticket.

Only set system, priority, type, and owner columns when the exact monday column keys or label IDs are documented in `references/monday_boards.md`. If they are not documented, omit those fields and report the missing schema after item creation.

---

## Step 6.5: Definition of Ready gate

Runs for **both** new and existing items, right before the write. A ticket that reaches the
board without a brief or a Figma looks active for three weeks and then turns out to have
never been startable. Catch it here, at the one moment someone is already thinking about
this ticket.

Read the required-field matrix in
`.claude/skills/ticket-hygiene/knowledge/config.md` ("Definition of Ready") - it is the
single source of truth for what each board requires, and `/ticket-hygiene` Pass C applies
the identical matrix to tickets already open. Do not restate the matrix here; it will drift.

The short version of what it demands:

| Board | Blockers - work cannot start without these |
|-------|--------------------------------------------|
| Website Development | A **Figma**, *or* a brief in either Brief column (`link_mm05cxb3` / `doc_mm77q17p`) - a brief alone only for a crystal-clear text change; plus a Design Owner when design-dependent and the Figma is empty |
| Marketing Operations Tasks | Owner, Type (exempt in the `New Requests` intake group) |
| HubSpot Projects // mvpGrow | Need-by date - the vendor literally cannot schedule without one |

**Design-dependent** means the ticket creates or changes a visual surface (new page,
section, component, redesign, landing page, template). Copy swaps, redirects, tracking
changes, SEO metadata, and link fixes are not. When it is genuinely ambiguous, treat it as
design-dependent - a false Figma prompt costs a click, a missing one costs a sprint.

Then:

1. **Fold the gaps into the Step 6 question batch.** Do not ask twice. If the board is
   Website Dev and you have no brief link, that question belongs in the same batch as
   owner and priority.
2. **Never refuse to create.** If a blocker is still unfilled after asking, write the
   ticket anyway - a lost request is worse than an incomplete one. Add every unfilled
   blocker to **Open Questions** as an explicit line (`Blocker: no Figma link - needs a
   design owner before this can start`), and say in your confirmation message that the
   ticket is on the board but not ready to start.
3. **Warnings are reported, not asked.** Mention missing due dates or priorities in the
   confirmation, do not add a round of questions for them.

---

## Step 7: Write to Monday

**Task name (new items):** Generate a short, human-sounding name - 5-8 words max, lowercase except proper nouns. Infer it from the description; do NOT ask the user. Examples: `"fix widget sync failures"`, `"add metadata filters to API"`, `"move token generation outside settings page"`.

**New item** - call `create_item`:
* `boardId`: selected board ID from Step 6
* `name`: inferred short task name (see above)
* `groupId` on **Website Development**: always `"group_title"` (`New Tasks`). Never a sprint group, even when the ask is urgent or due this week: the board owners place tickets into sprints at sprint planning. Only a board owner naming a specific sprint in the request overrides this. Never `topics` either, which is an old February sprint on this board, not an intake group. Rule and reason: `references/monday_boards.md`, "Filing a new ticket".
* `columnValues`: only set fields whose column keys are documented in `references/monday_boards.md`. On the Marketing Operations Tasks board (verified 2026-07-12):
  * `status_11` (Type): status column, use `{"label": "..."}` with a best-fit label from the Type table in `references/monday_boards.md` (e.g. `{"label": "HubSpot"}`, `{"label": "Data integration"}`)
  * `status` (Status): `{"label": "New"}` - there is no "Ready to start" label on this board
  * `person` (Owner): `{"personsAndTeams": [{"id": OWNER_ID, "kind": "person"}]}` where `OWNER_ID` is the numeric user ID resolved in Step 6 (omit the whole key if Unassigned). The `person-<id>` string form is for **filters only** - passing it to `create_item` fails with "User with email = person-... was not found".
  * `priority_1` (Priority): status column, use `{"label": "..."}` with a priority label from `references/monday_boards.md` (e.g. `{"label": "P2"}`)
  * `dup__of_assignee` (**POC**): `{"personsAndTeams": [{"id": POC_ID, "kind": "person"}]}`. **This is the right POC column** - the board has two people-columns both titled `POC`, and `peopleeozmsvcu` is the less-used one. Verified 2026-08-23; see `references/monday_boards.md`.
  * `color_mkzt8ef8` (**Planned?**): `{"label": "Planned"}` or `{"label": "Unplanned"}`, from the Step 6a search. Never `Stuck`. Do **not** confuse this with `color_mm08xv00` ("Weekly Planned"), which is unused board-wide.
  * `color_mkzspv3r` (**Bucket?**): write by **ID** (`{"index": 0}`), never by label - `Bucket 5: Work Process &  Work Flows` has a double space that fails a string match. Because a human is present, just ask which bucket rather than inferring: outside three narrow Type→Bucket priors the board's own history only supports a guess at ~60% (`.claude/skills/ticket-hygiene/knowledge/config.md`, "Bucket? - the evidence envelope"). Asking costs one question and beats a silent mis-file.

**Two fields need their own call after `create_item`**, each with a read-back:

* **`board_relation_mm0czzd3` (MKT Planning)** - set via `change_item_column_values` with `{"item_ids": [<planning item id>]}`, only if the user confirmed the Step 6a match. The response **echoes `null` even on success**, so confirm with a `get_board_items_page` read-back and never retry on the echo alone.
* **`files` (Assets)** - any links the task references (Figma, briefs, dashboards, staging URLs). It is a file column, so `change_column_value` will not work; use `update_assets_on_item` with `files: [{"fileType": "link", "linkToFile": "<url>", "name": "<display text>"}]`. Give each a human label, not the bare URL.

If required column keys are not documented, create the item with the title only, post the brief as an update (below), then report which metadata could not be set.

**Existing item** - use the existing item ID. No column changes needed.

**Post the brief as an item update.** `create_update` is the **primary** write, not a
fallback. Convert the Why/What/Done When/Open Questions template to **HTML** first - this is
not optional, markdown passed to `create_update` renders as literal text:

- Headings `## Why` → `<h2>Why</h2>`
- Bullets/checkboxes `- [ ] scenario` → `<ul><li>scenario</li></ul>`
- Paragraphs → `<p>...</p>`, italics `*x*` → `<em>x</em>`

Pass the HTML as the `body` argument. **Tell the user the brief landed only after
`create_update` returns an `id` and the Step 7.5 read-back of its body passes;** if either
fails, surface the failure instead of reporting success.

> **Why the update and not the description - verified live 2026-09-02.**
> `set_item_description_content` does not write anything a person reads on these boards. On
> Marketing Operations Tasks it lands in **`direct_doc_mm6r4pxs`, a normal board column of
> type `direct_doc` titled "monday Doc v2"** - not monday's item description. A `direct_doc`
> column is invisible until someone adds it to their view, so the brief is there over the API
> and absent on the ticket. Website Development behaves the same way
> (`direct_doc_mm08wesc`).
>
> This produced two "the agent filed a ticket with no details" reports in one day
> ([`12955444145`](https://riversidefm.monday.com/boards/18397093471/pulses/12955444145) and
> [`12958379709`](https://riversidefm.monday.com/boards/6257866754/pulses/12958379709)). Both
> times the mutation returned `success: true` and both tickets read as empty to the team.
> **`success: true` from that mutation is not evidence anyone can see the brief.**
>
> Nor is there a description column to fall back on: MOPs `long_text` is titled *"Write the
> objective of the test"* and `doc_mm28cnj8` ("Doc") is unused board-wide. **On these boards
> the update is the only surface a brief belongs on.**

**Never on Website Development.** Post the update only and do not call
`set_item_description_content` there: a second copy in the doc column drifts from the update,
and on 2026-09-29 a brief that went *only* there left
[`13159469942`](https://riversidefm.monday.com/boards/18397093471/pulses/13159469942) reading
as empty.

**Optionally**, on other boards, also call `set_item_description_content` for the API-side copy. If you do,
never describe it to the user as "the description" - say the doc column, or say nothing. It
also fails outright with `INTERNAL_SERVER_ERROR` on freshly-created items (the description
document does not exist yet and `create_doc` cannot initialize it - it only supports
board/workspace locations) and on monday CRM-product boards such as HubSpot Projects //
Eyal mvpGrow (`18413613511`), observed 2026-07-12. A failure there is not worth reporting
as a problem once the update has landed.

### The verbatim request always gets its own update

The brief is a *restatement*. Whoever executes needs the **raw ask** - the exact copy
string, the exact destination URL, the exact targeting words the requester used. A
paraphrase inside Why/What is not a substitute, because someone is going to paste those
strings into a tool, and a silently reworded CTA is a defect that ships.

So post the raw material verbatim too, **whenever the request carries anything that will be
used as-is**: message copy, a subject line, an email body, a CTA, a headline, a destination
URL, targeting rules, or any specific string or value. Omit it only when there genuinely is
none - "fix the typo on the pricing page" carries nothing to preserve, and restating it is
noise. When in doubt, include it: a redundant block costs a scroll, a lost CTA costs a
re-ship. `/ticket-hygiene` Step 5d applies the same test to its own filings.

**"The request" means everything you gathered, not the message that triggered you.** The
trigger is often a bare instruction - `@agent please open a Marketing ops ticket` and
nothing else - while the copy, the sheet, and the approvals sit in the surrounding channel
or thread you read in Step 3. Material found there is still request material and still gets
preserved. Scoping this to the trigger message is how a ticket ends up saying "copy is
approved by Gil" while containing no copy.

**Name it or paste it - never just reference it.** A line like "the approved subject line and
body" is not the copy; it sends the executor back to Slack to find what the ticket was
supposed to carry. If the material is too long to paste (a full HTML email, a 200-row
sheet), paste what identifies it exactly - the subject line verbatim, the sheet URL **and**
the tab name, the merge-field names - and say where the rest lives. Verified 2026-09-02 on
[`12958379709`](https://riversidefm.monday.com/boards/6257866754/pulses/12958379709), where
the send could not be built from the ticket alone.

```html
<h2>Request (verbatim)</h2><p>{the requester's own words - copy, CTA, links, targeting, unedited}</p>
<h2>Source</h2><p>{#channel, or "asked directly"} - {requester} - {date}{ - <a href="{permalink}">thread</a> when there is one}</p>
```

Do not tidy, shorten, or correct the requester's wording inside that block - preserving it
exactly is the entire point. Interpretation and corrections belong in the brief above it.

**Escape the markup, never the wording.** `create_update` takes HTML, so replace `&`, `<`
and `>` with `&amp;`, `&lt;` and `&gt;` in the requester's text (and in the permalink, which
sits in an attribute) before inserting it. Copy routinely contains `&` and `->`; an
unescaped one either corrupts the update or silently drops part of the ask. Escaping
changes how it renders, not what it says - that is not a rewrite.

**Escape the requester's text, never your own tags.** The body *is* HTML, so `<h2>` and
`<ul>` must go in as real tags. Escaping them yourself posts `&lt;h2&gt;...` as visible
characters and the update renders as a fragment of source. On 2026-09-23 that shipped a
near-empty update onto a live ticket. Recovery is
`mutation { delete_update(id: <update_id>) { id } }`, then repost - `create_update` has no
edit, so a bad update is deleted and replaced, not fixed in place.

**Confirm it landed.** Only tell the user the request was preserved after `create_update`
returns an `id`. If it does not, say the update failed and surface the error - a ticket
whose raw ask silently never posted is the exact defect this rule exists to prevent.

**Where this goes.** Simplest is one update carrying the brief and then the verbatim block;
two updates are equally fine. What is not fine is the brief landing without the raw material
next to it.

> **Why this is a rule.** Two Slack-filed tickets on 2026-09-02 each got a clean
> Why/What/Done When body and an **empty Updates tab**, and in both the exact copy survived
> only as prose inside *What* - or not at all. The twin ticket a human created carried the
> copy as an update, which is where MOPs actually reads the ask from. `/ticket-hygiene`
> intake already posts an update on every ticket it files (its Step 5d), but that one leads
> with a *one-sentence restatement*, so on its own it would not have preserved the copy
> either.

Template:

```markdown
## Why
{1-2 sentences max}

## What
{1-3 sentences max}

## Done When
- [ ] {scenario in plain language}
- [ ] {scenario}
- [ ] {scenario - 2-4 max}

## Open Questions
- {one line per question}
(omit if none)

---
*Documented via Claude Code on {today's date}*
```

---

## Step 7.5: Read the ticket back before you report it

Silent field misses are the most common way a filed ticket looks fine and is not. Do one
`get_board_items_page` on the item you just created (`includeColumns: true`) and confirm each
of these actually carries a value. Do not infer it from the `create_item` response - column
writes can be dropped or land in the wrong column while the call still returns success.

| Check | Column | If it is empty or wrong |
|---|---|---|
| **Brief posted as an update** | `get_updates` returns an update with an `id` | Post it. A brief in the doc column only does not count - see the note in Step 7 |
| **Update renders** | that update's `body` starts with a real tag (`<h2>`), never `&lt;h2&gt;` | Delete and repost (Step 7 recovery). An escaped body shows raw source on the ticket; an `id` alone does not catch it. `13056979737` carried one for a week (found 2026-09-23) |
| **Group** (Website Dev) | the item's `group.id` is `group_title` (`New Tasks`) | Move it with `mutation { move_item_to_group(item_id: <id>, group_id: "group_title") { id } }`, unless a board owner named a sprint in the request |
| **Type** | `status_11` | Set it. Never `Email blast` (`11`) - that label is dead by policy; outbound messaging of every kind is `Messaging` (`7`) |
| **POC** | `dup__of_assignee` | Set it there. If the value landed in `peopleeozmsvcu` instead, that is the second same-titled column and the POC reads as empty in the board's views - move it |
| **Planned?** | `color_mkzt8ef8` | Set it from the Step 6a search. `Unplanned` is the answer when nothing matched - empty is not |
| **Owner** | `person` | MOPs blocker outside the intake group (`.claude/skills/ticket-hygiene/knowledge/config.md`) |

Report any field you deliberately left empty **and why**, in the same message as the ticket
link. A field left blank on purpose with its reason stated is a triage instruction; a field
left blank silently is a defect.

> **Verified 2026-09-02.** On [`12958379709`](https://riversidefm.monday.com/boards/6257866754/pulses/12958379709)
> the board and the brief content were right, and four things were silently wrong: no update,
> `Planned?` empty, POC written to `peopleeozmsvcu`, and Type `Email blast`. Every one of
> those was already documented somewhere in this repo. Documentation alone did not catch
> them; a read-back does.

---

## Step 8: Confirm

Return the item URL: `https://riversidefm.monday.com/boards/{board_id}/pulses/{item_id}`

---

## Key Principles

* **Exhaust context before asking.** Monday, epic, siblings, system doc, code, git history, Slack - use all of it. The user should only fill what you genuinely can't find.
* **Open Questions is not homework for the assignee.** Anything the requester owns or can easily find gets checked during Step 3 and stated in What or Done When as a fact. What stays in Open Questions is a gap the requester still owes (flagged, per Ready-or-flagged) or a question inside the assignee's expertise. Rule of record: CLAUDE.md, "A ticket carries requirements, not research".
* **This is a product skill, not an engineering skill.** Read the code to understand what users experience today. Never surface file names, function names, component names, or technical internals in the brief. Translate everything into user-facing, business-facing language.
* **One output format, always.** Why / What / Done When / Open Questions. Nothing else.
* **Section walkthrough, not a full draft.** Walk through Why, What, Done When one at a time. Share your read, confirm with the user, then move on. Write to Monday only after all three are confirmed.
* **Casual tone, plain words.** Write like a teammate, not a spec writer. "Clean up" not "purge", "pick" not "configure". Short sentences.
* **Done When = checklist, not BDD.** Use `- [ ]` format. Plain language scenarios, no "Given/When/Then".
* **Batch questions, not drip questions.** Ask everything at once. The readiness gaps from Step 6.5 go in the same batch as owner and priority - never a second round.
* **Ready-or-flagged, never refused.** A ticket missing its brief still gets created; the gap is named in Open Questions and called out in the confirmation. Losing the request is the worse failure.
