<!-- last-reviewed: 2026-08-26 -->
# Brief stress-test (Gate 0)

The rubric `/video-project-intake` runs before anything is proposed. Source:
Part A4 of the Creative Ops Video Workflow blueprint, reconciled against the
live template Doc `1CiPRkspaWJG8Ee29an88NiqeLo9WwIFXa8oWd7HZgJ0`
("[Template] Creative video brief", owned by raz.messing@riverside.fm).

The Doc opens with a bare **`Owner:`** field that does not say owner *of what*.
Treat it as the **Brief Owner** by default, but confirm it at intake - on a brief
authored by a PMM it usually is, and on one authored by a creative it usually is
not.

Structure of the live Doc, in order: **Owner · Context · Deadline · Who are we
talking to? · What is their problem? / Why does that problem suck?! · How can we
help them? · What do we want them to think & feel? · Why should they believe us?
· Distribution (paid or organic / main channel / aspect ratio) · References
(marked optional) · What success looks like · What this is NOT.**

## The two jobs, kept apart

Grading and building are different modes and the brief tells you which one you
are in:

- **A drafted brief** → grade it. Run the fourteen checks, return the verdict,
  route gaps to the Brief Owner.
- **A rough idea** ("we should do something for the new editor") → **build it
  out by interview** (A3.1). Do not hand back a scorecard of fourteen failures;
  that is technically correct and useless. Ask through the sections in Doc
  order, one short pass, writing down the answers. Then grade what you built.

## The fourteen checks

Four of them (marked ✱) have **no field in the live Doc** - the blueprint
requires them but the template never asked. Three of the four now have a home on
the board (`board-schema.md`): Brief Owner and Creative Owner each get a column
*and* a sub-item, the Approver gets a sub-item. Type is the Channel column; the
effort estimate goes in the intake update. Collect them conversationally at
intake and record them in the intake update; do not report them as the Brief
Owner's failure to fill in a box that does not exist.

| # | Check | Passes when | Fails when |
|---|---|---|---|
| 1 ✱ | **Brief Owner** | a named person who can answer for the brief | absent, or "Brand", or the creative's name |
| 2 ✱ | **Creative team** | Creative Owner named, supporters named or explicitly none | "TBD" |
| 3 ✱ | **Type** | one of the five Channel labels | absent, or two at once |
| 4 ✱ | **Creative-effort estimate** | high / medium / low, stated | absent |
| 5 | **Context + why now** | a specific trigger (launch, campaign, competitive moment) | "we need a video" |
| 6 | **Deadline** | a real date | "ASAP", "end of quarter", empty |
| 7 | **Audience** | intent, experience, and awareness level all present | "creators", "our users" |
| 8 | **Their problem, and why it hurts** | both halves answered; the second is not a restatement of the first | only the what, not the sting |
| 9 | **How we help** | ties to a real capability | a slogan |
| 10 | **Think & feel** | both named, and distinguishable | one word covering both |
| 11 | **Why they should believe us** | an ordered sequence of specific product moments / features | "show the product" |
| 12 | **Distribution** | paid-or-organic, main channel, **and** aspect ratio / specs | channel with no specs |
| 13 | **References** | 2-3, each stating exactly what is borrowed | "vibes like this", or a bare link |
| 14 | **Success + What this is NOT** | success is one line naming a metric, behaviour, or feeling; guardrails present | success is a paragraph; guardrails empty |

### Two judgement calls, not rules

**Specs (12).** Aspect ratio is *a judgement call with defaults*, not a fixed
matrix. A Feature Release going to X and LinkedIn desktop is 16:9 even where
mobile logic would argue 4:5 or 9:16. When the brief names a channel but no
ratio, propose the default with its reason and let Raz confirm - that is a
recommendation, not a gap.

**References (13).** The Doc marks References optional; the blueprint requires
2-3. Treat a missing reference section as a **soft** gap: worth raising, never
on its own a reason to hold the project.

## Verdicts

Label each failing check **P0** (hard - blocks) or **P2** (soft - does not block),
matching `/marketing-website-page-qa`'s severity vocabulary. Checks 1-12 and 14 are
P0 when they fail outright; check 13, and a spec default that only needs
confirming, are P2.

Return exactly one verdict:

- **Sound** - every hard check passes. Proceed to the proposal.
- **Sound with gaps** - the failures are soft (13, or a spec default that just
  needs confirming). Proceed to the proposal *and* list the gaps.
- **Not ready** - one or more hard checks fail. Name each gap, say who owns it
  (the Brief Owner, by name), and stop. **Nothing is created on the board.**

Two hard checks have no soft version: **6 (Deadline)** and **11 (Why they should
believe us)**. A brief with no date cannot be scheduled and a brief with no proof
sequence cannot be storyboarded.

## Rules that govern the whole pass

- **Gaps route to the Brief Owner, never the creative.** The Creative Owner
  cannot answer for the brief. If the Brief Owner is the gap (check 1), that
  question goes to Raz.
- **Quote, don't paraphrase, when you fail a section.** "Audience reads
  'podcasters' - no intent or awareness level" is actionable; "audience is vague"
  is not.
- **Never fill a gap yourself.** Not from the product docs, not from a previous
  brief, not from a plausible guess. An invented audience survives all the way
  into a shot list.
- **A stale brief is a gap.** If the Doc's `modifiedTime` predates a change Raz
  mentions in the handover, say so and ask which is current.
- **The verdict is not the go decision.** A sound brief for a project the team
  has no capacity for still does not start (A3). Surface capacity; never decide
  priority.
