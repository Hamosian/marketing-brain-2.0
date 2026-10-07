# Granola sweep - reading Nir's own meetings for commitments

Loaded by `/chief-of-staff` on every run (Step 1.D). Reads the meetings **Nir sat in**
since the last run, pulls what he committed to and what was left undecided, and diffs
that against the ledgers so a commitment made out loud cannot quietly disappear.

Added 2026-09-16, on Nir's ask, after he asked whether the brief was reading his
Granolas. It was not. The skill queried Granola only for the day's 1-1 prep line, so a
whole class of work was invisible: **five commitments Nir made to Abel in the
2026-09-14 weekly had never appeared in any brief**, and the four unresolved decisions
from the 2026-09-10 SEO Strategy H2 session were the real content underneath the
Abel-and-Erika priority argument the 2026-09-16 brief reported without them. A brief
that reads Slack and Gmail but not the room where the decision was made is reading the
echo, not the source.

## Scope: Nir's meetings only

Granola holds the whole workspace. In the week to 2026-09-16 that was 46 meetings, of
which 9 were Nir's and 37 were other people's sales calls. Reading all 46 is expensive
and produces nothing for this brief.

**Include** a meeting when either is true:
- `captured_by_me="true"` - Nir ran the recorder, so it is his meeting.
- `listed_as_participant="true"` - he was an attendee.

**Exclude** everything else, and never widen this without Nir saying so (his call,
2026-09-16: "only mine"). In particular do not sweep AE and CSM intro calls,
demos, or other teams' internals, even when they are workspace-visible and even when
they mention a Riverside system. A sales call that matters reaches this brief through
HubSpot or Slack; for call analysis the owning skill is `/gong-calls-explorer`.

One exception, narrow: a meeting Nir was invited to and did not attend still counts if
he is on the participant list, because what was committed **on his behalf** is his
problem. Say so in the line when he was absent.

## Window

Since the last run. In practice ~24h on a Mon-Thu run, and the weekend on Sunday.
`list_meetings` returns a 7-day span by default, so filter by date rather than
assuming the tool's window matches the brief's.

The sweep is **read-only**. It proposes; FEED mode writes.

## What to extract

Per meeting, at most these four, and nothing else:

1. **Commitments Nir made.** He said he would do a thing. These are the highest-value
   rows in the whole sweep and the reason it exists. They almost never appear in Slack.
2. **Commitments made to Nir**, with an owner, by a member of his org. These feed the
   ledgers and the 1-1 packs.
3. **Open decisions** that were named and not settled, with who is blocked on them.
4. **A stated date.** Only a date a person actually said. A date the agent would have
   to infer is not a date (see the inferred-metadata rule in SKILL.md Step 1.A): it
   never nudges and never counts as overdue.

Skip the narrative, the attendee list, the small talk and anything that reads as
context rather than as work. A meeting with no commitment and no open decision
produces no lines, and that is a normal result.

## Diff before rendering

Never render a raw meeting summary into the brief. Every extracted item runs through
two tests first:

1. **Is it already tracked?** Check `data/brief-state.md` and the seven ledgers in
   `.claude/skills/growth-marketing-team-tasks/data/`. A match means the item is
   context for an existing row, not a new one - at most it updates that row's state.
2. **Has it since closed?** Check Slack and Gmail the same way Step 2b does before
   calling anything unanswered. People act on what they agreed to; a commitment made
   Monday and delivered Tuesday is not a finding.

What survives both tests is genuinely new work that no system is tracking. That is
what gets surfaced.

## Where the output goes

| Extracted item | Destination |
|---|---|
| Commitment by Nir, with a clock or a blocked person | the action table |
| Commitment by Nir, no clock | one line in **Changed since yesterday**, proposed for `.claude/skills/growth-marketing-team-tasks/data/my-tasks.md` via FEED |
| Commitment by one of his leads | that lead's ledger via FEED, and their next 1-1 pack |
| Open decision only Nir can settle | the action table |
| Open decision owned elsewhere | Watch, which means it renders only when its state changes |
| Commitment Nir made to Abel | `data/abel-weekly-notes.md`, so the next Abel update carries it |

Everything except `data/abel-weekly-notes.md` is **proposed, never auto-written**. Ledger
rows go through `/growth-marketing-team-tasks` FEED mode, diff-first, on Nir's word.
`data/abel-weekly-notes.md` is this skill's own state file and is maintained every run.

## Rendering

Sweep findings do not get their own section. They land in whichever lane they belong
to, so the brief stays one list rather than becoming a meeting digest. The only
sweep-specific line is in **Changed since yesterday**, and only when something new
came out of a meeting:

```
- From Monday's Abel weekly: five commitments you made are on no ledger. Proposed below.
```

Cap the sweep's contribution at **5 lines** across the whole brief. If a single meeting
yields more than five real items, it is not a brief item, it is its own working session:
say so in one line and point at the meeting.

## Failure handling

If Granola is unreachable, say it once ("Granola was not reachable this run") and carry
on. Never infer what was probably agreed from a calendar title. A brief that guesses at
the contents of a meeting it could not read is worse than one that admits the gap.
