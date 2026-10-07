---
name: video-project-intake
description: The Creative Ops intake handshake for a new VIDEO project on the "Video Projects | Creative Team 2026" monday board (18426224074). Raz Messing hands over a creative video brief in Slack - a Google Doc link, pasted text, or just a rough idea - and this skill stress-tests it against the Creative Video Brief template, routes gaps back to the Brief Owner, proposes the project (name Name_YYYY_MM, Type, Creative Owner, supporters, Approver), and only after Raz explicitly confirms does it duplicate the template group and attach the brief. Confirm-before-write - nothing is created on the board until Raz says go. Trigger with "new video project", "here's the brief", "start a video project", "intake this brief", "kick off a video", "stress-test this video brief", "is this brief ready", or "/video-project-intake". Not for Marketing Ops tickets (use /pm-story), not for Design projects.
user-invocable: true
---

# Video Project Intake

The front door to the Creative Ops video pipeline. Raz Messing hands over a
brief; this skill decides whether the brief can carry a project, proposes the
project, and creates it on the board **only after Raz confirms**.

It is deliberately the *whole* front door and *nothing past it*. See
[Scope boundary](#scope-boundary).

## Load before you start

- `knowledge/board-schema.md` - the live board, its column ids, the template
  group, the exact write plan, and every place the board disagrees with the
  blueprint. Read this before proposing anything; it is the write contract.
- `knowledge/brief-stress-test.md` - the fourteen-check rubric and the verdicts.
- `references/team.md` - to resolve any name to a person before writing it.
- `references/video-creative-brief-templates.md` - readable snapshot of the
  brief template (which of the two templates applies, and what each field is for).
- **The sibling intake and QA skills, for convention** - `/pm-story` (monday
  intake, the Definition of Ready gate, batched questions), `/hubspot-workflow-qa`
  (auto-discover before asking, findings-then-sign-off), and
  `/marketing-website-page-qa` (the P0-P3 severity vocabulary). This skill is the
  same shape as theirs and should feel like it. Where it diverges, it says so and
  why - see [Boundaries with neighbouring skills](#boundaries-with-neighbouring-skills).

## The two decisions at the front door

Keep these apart; conflating them is the failure this skill exists to prevent.

- **The brief** says *what* the project is. This skill grades it.
- **Raz's go** says *whether to start now* - capacity and priority. A sound brief
  for a project the team has no capacity for still does not start.
  **Surface capacity; never decide priority.**

## Step 0 - Trigger gate

**Only Raz Messing (`raz.messing@riverside.com`, Slack `U08HMKEAYC8`, monday
`73570317`) starts a project.** Anyone may author or hand over a brief; only
Raz's go creates one.

If someone else asks for a project: stress-test the brief for them if they want
it, say plainly that the go is Raz's, and offer to hand him the brief plus the
verdict. Do not create anything, and do not treat their enthusiasm as a go.

<!-- TEMPORARY-EXCEPTION: added 2026-08-27, review by 2026-09-10 -->

### TEMPORARY - pilot exception

> **This block is temporary.** It exists to prove the Slack front door works
> while Raz is out. **To revert: delete this block, nothing else.** Step 0 above
> is the permanent rule and needs no other edit. Find it again with
> `grep -rn "TEMPORARY-EXCEPTION" .claude/`.

**Ari Kuchar** (`ari.kuchar@riverside.com`, Slack `U07R8V5L19N`, monday
`67289613`) may also trigger intake, **solely to test this skill** while the
`@marketing-os` Slack agent's capabilities are being established.

Three conditions, all required:

1. **Announce it, every single run.** Open with one line:
   *"Running under the temporary pilot exception - Ari triggering in Raz's
   place; the standing gatekeeper is Raz Messing."* A widened gate nobody can
   see is how a temporary exception quietly becomes the permanent rule.
2. **Nothing else widens.** Confirm-before-write is unchanged, the write plan is
   still its own confirmation, and the proposal still carries a preference plus
   rationale. Ari confirms his own plan - he is the trigger, so that is not
   delegation.
3. **Say what a real run would have done.** If the brief came from someone other
   than Ari, name the person a production run would have routed the go to.

This exception does **not** extend to anyone else, and it does not make Ari the
gatekeeper. Capacity and priority remain Raz's call even during the pilot: if a
project would start that Raz has not sized, say so in the report.

## Step 1 - Take the brief

Three shapes arrive, and they branch:

| What arrived | Do |
|---|---|
| A Google Doc link | Read it with the Drive connector. Note its `modifiedTime` - a brief older than something Raz just said is a gap, not a source. |
| Pasted text | Grade it as-is. Ask where the Doc lives; the board needs a pointer, not a copy. |
| A rough idea | **Interview mode.** Build the brief out with Raz through the template's sections in order, then grade what you built. Do not hand back fourteen failures. |

If the doc is unreadable or permission-denied, say so and ask for access. Never
grade a brief you could not open.

**Exhaust context before asking anything** (the `/pm-story` and
`/hubspot-workflow-qa` rule). Work out for yourself, before putting a single
question to a human:

| Determine yourself | How |
|---|---|
| Brief Owner candidate | the Doc's `Owner:` field, plus its Drive owner - then confirm which person it means, never assume |
| Type / Channel | infer from the brief's own context, distribution and success line, and bring it as a recommendation |
| Deadline, audience, channels | read them off the brief |
| Whether a project channel already exists | search Slack for the project name |
| Anyone's monday id | `list_users_and_teams`, confirming the match |

**Never ask for something the brief already answers.** Ask only for what is
genuinely undeterminable: the creative team, the effort estimate, and the
confirmations.

## Step 2 - Stress-test the brief (Gate 0)

Run the fourteen checks in `knowledge/brief-stress-test.md` and return exactly
one verdict: **Sound**, **Sound with gaps**, or **Not ready**.

Four required fields have no box in the live template - **Brief Owner, Creative
team, Type, creative-effort estimate**. Collect them conversationally here; do
not report them as the Brief Owner's omission. The Doc's single `Owner:` field is
ambiguous (owner of the brief, or of the creative?) - **always confirm which
person it names** rather than assuming.

**Label every gap P0 or P2**, matching `/marketing-website-page-qa`'s severity
vocabulary so Raz reads the same labels across every QA surface: a **hard check
failure is P0** (blocks - the project does not start), a **soft gap is P2**
(should fix, does not block). There is no P1 or P3 here; a brief gap either stops
the work or it does not.

**Ask everything in one batch** (`/pm-story`'s rule). The brief gaps and the
undeterminable fields go in a single message - never a gap round followed by a
questions round.

**Gaps route to the Brief Owner, by name - never to the creative**, who cannot
answer for the brief. On **Not ready**, stop here. Nothing is created on the
board. Saying "the brief isn't ready" and creating the project anyway is the
worst available outcome: it puts a hollow project on a clean board.

**Nothing has been written anywhere at this point.** Say so explicitly in the
verdict, so Raz knows the board is still clean.

## Step 3 - Propose the project

**Always bring a preference plus a rationale, never an open "what do you
think?" (A1.3).** Every line below is a recommendation to confirm or correct.

Post one card:

```
Proposed project
  Name             <Name>_<YYYY>_<MM>          <- YYYY_MM from the deadline month
  Type (Channel)   <one of the five labels>    - because <one line>
  Creative Owner   <name>                      - because <one line>
                                               -> Owner column + "Creative Owner" sub-item
  Supporters       <names, or "none">          -> Supporter column
  Brief Owner      <name>                      - owns any gap listed below
                                               -> Stakeholder column + "Brief Owner" sub-item
  Approver         Abel Grunfeld               -> "Approver" sub-item (standing, every type)
  Feedback pool    <names> - advisory, does not gate
  Raz pre-gate     <on / waived / n-a>
  Brief            <doc title> -> attaches to "Brief (and Scope)"
  Deadline         <date> -> Timeline on "Overall Ownership"
  Effort estimate  <high | medium | low>
  Open gaps        <list, or "none">
```

The **Type sets who is involved, not the workflow shape** - it is a light hint
whose real job is the stakeholder map. Do not let a Type imply a stage list; the
scope interview decides that later, and it is not built yet.

Default feedback pools by Type (from D1; ids in `knowledge/board-schema.md`):

| Type | Pool |
|---|---|
| Feature Release | Sivan Mazuz + the assigned PMM (Alon Livneh or Galya Nash) |
| Acquisition | Raz Navon (FYI at Script, required at Offline), Jarred Berman (red-flag reviewer). **Nir Taranto is FYI only - never gating, never chased.** |
| Brand awareness | Raz pre-gate default-**on**, waivable by Raz only |
| Website | a PMM + Sivan Mazuz |
| Other | no default pool - ask Raz |

**Never skip the Raz pre-gate on your own, and never question a waiver.** His
reason for waiving is invisible to you and that is fine.

## Step 4 - Confirm before write

Show the **exact write plan** - every call, every column, every value - and wait
for an explicit yes.

```
On confirm I will:
  1. duplicate group "Project Name_YYYY_MM (Video Project Template)" -> "<new title>"
  2. verify 32 items + their sub-items copied (incl. the 3 ownership sub-items)
  3. Overall Ownership   Owner=<Creative Owner> Supporter=<..> Stakeholder=<Brief Owner>
                         Channel=<Type> Timeline=<deadline>
  4. its 3 sub-items     Brief Owner=<..>  Creative Owner=<..>  Approver=Abel
  5. Brief (and Scope)   Link=<brief url>  Stakeholder=<Brief Owner>
  6. one update on Overall Ownership recording pool, effort estimate, pre-gate, gaps
  7. nothing written to the 7 approval items, and no Stage values set anywhere
Nothing else. Confirm?
```

Rules that make this real rather than ceremonial:

- **Silence is not consent.** No reply means no write. Nudge once, then stop.
- **"Looks good" on the proposal is not consent to write.** The write plan is
  its own confirmation.
- **A confirmation covers one plan.** If anything changes after the yes - a
  different Owner, a corrected Type - re-show the plan and re-ask.
- **Confirmation cannot be delegated.** The go is Raz's (Step 0).
- If Raz corrects a value, change it and re-show the plan. Corrections are the
  normal case, not a failure.

## Step 5 - Execute, then verify

Follow the write plan in `knowledge/board-schema.md` exactly, in order.

- **Resolve every item and sub-item by name in the newly created group.**
  `duplicate_group` mints new ids for both; the template's ids still point at the
  template, and writing to one edits the template itself.
- **`create_labels_if_missing: false` on every status write.** A typo must fail
  loudly rather than invent a label on a shared board.
- **Read the group back after writing** and report what actually landed - item
  count, the columns you set, the brief link. A write that returned 200 is not
  evidence; the read-back is.
- **If any step fails, stop and report.** Do not retry blind and do not carry on
  to the next step. A half-created project is worse than none, and it is Raz's
  call whether to fix forward or delete the group.

## Step 6 - Slack channel (optional, separately confirmed)

Offer the project channel, propose a name, and get its own yes. Creating a
channel and inviting people is a second side effect, not a rider on the first.

On confirm: create the channel, invite Raz, the Creative Owner, and the Brief
Owner, then rename the `Slack channel: #` item to carry the channel name and set
its Link column. If Raz declines, leave the item untouched and say so.

## Step 7 - Report once

One message. The blueprint's notification budget is **one high-signal update per
day**; a new project is worth one, and the intake chatter that preceded it is not.

```
<Name>_<YYYY>_<MM> is live - <board url with group anchor>
Owner <name> | Type <label> | Approver Abel | Deadline <date>
Brief attached to "Brief (and Scope)".
Stage values not set - gating is not built yet.
Open with the Brief Owner: <gaps, or "nothing">
```

If posted to Slack, end with `_Posted by the Marketing OS agent_`.

## Scope boundary

This skill is Phase 1's first slice. It ends the moment the project exists.

**Not built, and not to be improvised here:**

- **Gating and approvals (A5)** - the Request Approval workflow, the critical vs
  confirmation tiers, the silence rules, internal alignment before external
  approval. Nothing here advances a stage or asks anyone for an approval.
- **The scope interview (D6)** - it fires after Concept approval, which cannot
  happen yet.
- **Budget (A8), contracts (C1a), delay handling (A17), the daily digest, status
  pull.**

If Raz asks for any of these mid-intake, do the intake, then say plainly which
piece is not built and what it would take.

## Boundaries with neighbouring skills

Hanan and Jonathan's intake and QA skills came first; this one deliberately
matches their shape. What it borrows, and the one place it does not.

| Skill | Relationship |
|---|---|
| `/pm-story` | Owns **every** monday task creation on our own boards. This skill never creates a task - it creates a *project group* on the Video board, which `/pm-story` does not do. A task that comes out of a video project still goes through `/pm-story`. |
| `/monday-agent` | Owns generic board reads/writes. Never let it write to `18426224074` directly; project structure there is group-shaped and it does not know that. |
| `/hubspot-workflow-qa`, `/marketing-website-page-qa` | The QA pattern this skill's Gate 0 follows: auto-discover, then a checklist with severity labels, then findings, then sign-off. Same vocabulary, different subject. |
| `/data-team-request` | The other confirm-before-write intake. Same posture: assemble, show it back, wait for an explicit go. |
| `/video-project-intake` (this) | Owns the front door only. Everything downstream of project creation is unbuilt (see above). |

### The one deliberate divergence: this skill *can* refuse

`/pm-story` holds **"ready-or-flagged, never refused"** - a ticket missing its
brief still gets created, the gap goes in Open Questions, because *losing the
request is the worse failure*. That is right for a task board.

**This skill refuses instead**, and the reason is the shape of the artifact, not
a difference of philosophy:

- A hollow **task** on the MOPs board is one row that someone can fill in later.
- A hollow **project** on the Video board is a duplicated group of **32 stage
  items** with no proof sequence and no distribution. It reads as live work, it
  clutters a board Raz actually uses to see what is in flight, and cleaning it up
  means deleting a group rather than editing a row.

So the cost of the bad artifact is an order of magnitude higher here, and the
blueprint (A3.2 - "nothing is created on the board yet, keeps the board clean")
made the opposite call for that reason.

**But `/pm-story`'s underlying concern still binds: the request must not be
lost.** So a refusal is never silent. On **Not ready** the skill names every P0,
names the Brief Owner who owns each one, and hands the verdict back to whoever
brought the brief - the request lives on in the thread, it just does not get a
group on the board until it can carry one. If refusals ever start losing requests
in practice, that is the signal to revisit this and follow `/pm-story` instead.

## Hard rules

1. **Nothing is written before an explicit confirmation.** This is the default
   posture for every side effect - monday, Slack, anything. It loosens only by a
   human decision, never by this skill's own judgement.
2. **The board is the record of truth; monday holds a pointer, not a copy.** The
   brief lives in Drive. Never paste brief content into an item.
3. **Each person has exactly one home, and the homes are not interchangeable.**
   Creative Owner -> `Owner` column + `Creative Owner` sub-item. Brief Owner ->
   `Stakeholder` column + `Brief Owner` sub-item. Approver -> the `Approver`
   sub-item, and nowhere else. **`Stakeholder` on this board means Brief Owner,
   not Approver** - the blueprint reserved it for the Approver and the board does
   not. Never infer an approver from an avatar or a column position, and never
   write the Approver onto the approval items "to be helpful": seven copies is
   seven places to drift.
4. **Never invent brief content**, and never fill a gap from product docs, an
   old brief, or a plausible guess.
5. **Gaps go to the Brief Owner. The go decision is Raz's. Capacity is surfaced,
   never decided.**
6. **Board over blueprint.** Where they disagree, use the live board and record
   the disagreement in `knowledge/board-schema.md` rather than fixing either
   silently.

## Done when

The group exists on `18426224074` under the confirmed `Name_YYYY_MM` title with
32 items, the brief is linked on `Brief (and Scope)`, the three ownership
sub-items under `Overall Ownership` each name a real person, the Stakeholder
column carries the Brief Owner, the intake update is posted, and the read-back
has been reported to Raz. Any of those missing means say so - not
"created successfully".

## Worked example

> **Raz:** here's the brief for the new AI editor launch video
> https://docs.google.com/document/d/<id> - let's get it going

**Verdict: Sound with gaps.** Twelve of fourteen pass. Two open:
> - *Distribution* names YouTube and LinkedIn but no aspect ratio. Recommend
>   **16:9** - both are desktop-first placements, and the proof sequence is a
>   screen recording that crops badly to 9:16. Confirm and I'll take it as answered.
> - *References* has two links, no note on what's borrowed. Soft gap - **Galya
>   Nash** (Brief Owner) to add one line each. Not a reason to hold.
>
> Nothing on the board yet.

**Proposed:** `AIEditorLaunch_2026_10` - Type **Feature Release** (a named
capability shipping to existing users) - Owner **Ari Kuchar** - Supporter **Stav
Sobolev** (the proof sequence is motion over screen capture) - Approver **Abel** - Pool **Sivan Mazuz + Galya Nash** - Deadline **2026-10-14**.

Then the write plan, verbatim, and the wait.

> **Raz:** yes but make it Amir's, Ari's on the brand film

Owner corrected to **Amir Hemed**; write plan re-shown; second yes; execute.
