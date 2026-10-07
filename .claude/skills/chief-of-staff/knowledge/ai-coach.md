# Sharpen - the weekly AI coach pass

Runs on the **Sunday** brief only. Adapted from Kieran Flanagan's "AI Coach"
idea (The AI Marketing Generalist, 2026-08-21), which Nir asked for on
2026-09-07 with the framing "I want to get better."

## What it is for

Every other section of the brief is about the org. This one is about how Nir
works with the system. The rest of the brief tells him what to do; Sharpen tells
him what to stop doing by hand.

It is coaching, not a status report. Three findings maximum, one habit. A
Sharpen section that lists everything is the failure mode - Nir already has a
brief for that.

## Evidence sources, in priority order

Use what is available in this run. Never fabricate a pattern to fill the section.

| Source | What it tells you |
|--------|-------------------|
| `data/coach-log.md` | What was already coached, and whether it stuck. **Read this first.** |
| The session transcript history, where the runner exposes it | The strongest signal - what Nir actually asked for, in his words, repeatedly. If unavailable, say nothing about it and work from the sources below |
| `git log --since="7 days ago"` on this repo | What got built by hand. Repeated manual edits to the same kind of file are an unpromoted skill |
| `data/article-index.md`, `data/slack-later-index.md`, the reading list | What Nir keeps saving. A cluster on one topic means the intelligence layer is missing that topic |
| The team ledgers, `data/patterns.md`, `data/brief-state.md` | Recurring task shapes. The same task title recurring across weeks is a candidate skill |
| `references/team-context/`, `systems/reference/marketing-operating-model.md`, `references/messaging/` | Intelligence files. Compare against this week's reports and Slack to find the ones reality has moved past |
| `CLAUDE.md` Task Routing plus `/list-skills` | The registry. The gap between what exists and what Nir used is the highest-value finding |

## The four questions

Answer at most three in any given week. Pick the ones with real evidence.

**1. What did Nir do by hand that should be a skill?**
Threshold: the same shape of work three or more times, or twice if it took real
effort each time. Name the work, cite the evidence (dates, permalinks, commits),
and say which of the five agent types it would be. If Nir bites, hand to
`/agent-builder`.

**2. Which intelligence file has reality moved past?**
A file is stale when something this week contradicted it, not when it is merely
old - `/health-check` already owns date-based staleness, so do not duplicate it.
Name the file, the contradicting evidence, and the specific line to change.

**3. What already exists that he did not use?**
The registry runs to 80+ skills and nobody holds that in their head. Find work
done manually this week that a registered skill covers. This is usually the
highest-value finding and the cheapest to act on - it costs one sentence, not a
build.

**4. What capability fits how he works that he is not using?**
New platform features, a connector that is authorized but idle, a scheduled run
that would remove a recurring manual trigger. Only raise this with a concrete
tie to work he actually did.

## The habit

Close with exactly one behavior change for the coming week, phrased as a single
sentence Nir can act on without deciding anything. Not a project. "Pin the three
things you want tracked instead of typing them into the brief" is a habit;
"improve your intelligence layer" is not.

Repeat the same habit at most twice. If it has not stuck after two weeks, log it
as `not-landed` in the coach log and pick a different one - the habit was
probably wrong, not Nir.

## Rendering

Place Sharpen **last** in the Sunday brief, after Patterns review. It is
reflective; it should not compete with the day's Act items.

```
## Sharpen

**1. <finding, as a claim>**
<one or two lines: the evidence with dates, and the specific move>

**2. <finding>**
<evidence and move>

**3. <finding>**
<evidence and move>

**Habit this week:** <one sentence>
```

Fallbacks, in order of preference:
- Fewer than three findings with real evidence: render the ones you have. Two is
  a normal week.
- No findings at all: `**Sharpen** - nothing new this week. Last week's habit:
  <habit> - <landed / not landed>.` Never pad, and never re-raise a finding
  logged as `acted` just to fill the section.
- Evidence sources unavailable (no transcript access, git unreadable): say which
  source was missing in one clause. Do not silently score the week on less.

## The coach log - `data/coach-log.md`

One row per finding. Update it on every Sunday run.

| Column | Contents |
|--------|----------|
| `date` | The Sunday it was raised |
| `type` | `promote` / `stale-context` / `unused-skill` / `capability` / `habit` |
| `finding` | One line |
| `evidence` | Dates, commits, or permalinks |
| `status` | `raised` / `acted` / `declined` / `not-landed` |

Rules that make the log worth keeping:

- **Never raise the same finding twice while it is `raised`.** Escalate instead:
  second appearance gets one line noting it is the second ask, third appearance
  gets proposed as a decision ("build it or drop it").
- **`declined` is permanent.** If Nir says no, it does not come back. A declined
  finding that reappears is the bug this log exists to prevent.
- **Mark `acted` when the thing actually shipped**, not when Nir said yes. A
  skill that was agreed and never built stays `raised`.

## Constraints

- **Three findings, one habit, hard cap.** Under 120 words.
- **Every finding carries dated evidence.** "You seem to do this a lot" is not a
  finding. Per `references/evidence-standards.md`.
- **Coach the system, not the person.** The subject is the workflow and the
  tooling. Never grade Nir's judgement, priorities, or output quality - that is
  not what he asked for and not what this section can see.
- **Read-only.** Sharpen proposes; it never builds a skill, edits an
  intelligence file, or opens a PR on its own. Acting happens through the
  brief's Suggested actions, with Nir's pick.
- **No transcript access is not a failure.** Repo signals alone support findings
  2 and 3 perfectly well. Say what was unavailable and move on.
