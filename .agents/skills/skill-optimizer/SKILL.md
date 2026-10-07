---
name: skill-optimizer
description: "Closed-loop optimizer for the skill library. Measures every skill (authoring signals plus routing eval), picks the weakest, makes one targeted edit per skill, re-measures, and keeps a change only if the scoreboard improves with no regression anywhere; otherwise it reverts. Bounded rounds, a ledger so it never retries a failed attempt, and one PR at the end for a human to review. Use when someone says \"optimize our skills\", \"improve or fix our weakest skills\", \"run the skill optimizer\", \"tighten up the agents\", \"which skills need work, fix them\", \"run the optimization loop\", or \"/skill-optimizer\". Owns the edit-and-verify loop; /skill-audit scores one skill's writing, /skill-eval tests routing, /health-check finds stale docs."
---

# Skill optimizer

The evaluator-optimizer loop (`references/agent-prompting.md`, block 6) applied to the
skill library itself. `/skill-audit`, `/skill-eval` and `/health-check` each *measure*
one thing and propose a fix. This skill closes the loop: it applies the fix, measures
again, and keeps only what measurably helped. In the Claude Code taxonomy it is a
**goal-based loop**: a measurable target, a try limit, and a check before it stops. The loop
design and the other loops in the repo: `docs/loop-engineering.md`.

**Done when:** the batch is finished, every attempt is in the ledger, the final scoreboard
compare prints `VERDICT: KEEP` against the run's baseline, `bash scripts/preflight.sh`
passes, and one PR is open with the before/after numbers. A run that kept nothing is also
done: it reports NO-CHANGE and opens no PR.

## The loop contract

| Field | This loop |
|---|---|
| Signal | `python3 scripts/skill_scoreboard.py`: authoring signals from `scripts/audit_skill.py` plus routing verdicts from `scripts/eval_routing.py`, folded into one priority per skill |
| Step | One targeted edit to one skill, aimed at its highest-priority gap |
| Judge | Two, in order. Per edit: `skill_scoreboard.py --compare` against the snapshot taken before it (KEEP, REVERT or NO-CHANGE; deterministic, never a model). Per batch: a fresh-context reviewer agent that did not write the edits reads the diff against the rubric |
| Budget | Default batch of 5 skills, at most 2 attempts per skill, at most 12 edits per run |
| Memory | `tracking.md` in this folder: every attempt, verdict and reason |
| Exit | A human merges the PR. This skill never merges and never writes to `main` |

## Hard rules

1. **Never game the signal.** The audit signals are regexes. Adding "e.g." to satisfy
   "has a worked example", or the words "done when" with no bar after them, is a
   fabricated gain and a worse skill. Every fix must be real content a reader would act on:
   a shown input-to-output example, a bar someone could disagree with, a boundary that names
   the sibling skill that owns the neighbouring request. If you cannot write the real thing
   from what is in the skill and the repo, skip that gap and log it as `skipped: needs owner`.
2. **Ground every fix in the repo.** Examples, boundaries and output sections come from the
   skill's own workflow, its `knowledge/` files, `CLAUDE.md` routing, or real past output
   (ledgers, tracking files). Do not invent board IDs, channels, people or metrics. If a fix
   needs a fact the repo does not hold, it is out of scope for this run.
3. **One skill, one edit, one judgement.** Snapshot, edit one skill, compare. Never batch two
   skills under one comparison: a gain on one would hide a regression on the other.
4. **A regression is always reverted.** `VERDICT: REVERT` means `git checkout -- <files>` for
   that edit, no arguing with the judge. `NO-CHANGE` is also reverted unless the edit fixed
   something the scoreboard cannot see (a factual error, a dead path); say which in the ledger.
5. **Two attempts, then stop.** After two non-KEEP attempts on the same skill, log
   `escalated` and move on. If it has not converged in two rounds the gap needs the skill's
   owner, not a third rewrite (block 6: stop after two rounds).
6. **Descriptions are the routing surface.** Editing a `description:` can move requests
   between skills. After any description edit, run the full routing compare (the judge does)
   and keep the value under the 1024 cap. Past 950 chars, a description edit has to cut as
   much as it adds.
7. **Read the ledger before picking.** A skill with a `KEEP` in the last 30 days, or any
   `escalated` row not yet cleared by a human, is skipped this run.
8. **Stay in scope.** Edit only `.claude/skills/<name>/` files and `evals/routing.jsonl`. No
   edits to `CLAUDE.md`, `systems/`, `references/` or scripts from inside the loop; if a fix
   belongs there, list it in the PR as a follow-up.

## What it does not do

This skill does not own scoring one skill's writing in depth (that is `/skill-audit`),
running the model-in-the-loop routing test (`/skill-eval`), finding stale docs
(`/health-check`), or building a new skill (`/agent-builder`). It calls on their outputs
and rubrics. It also does not merge, publish, or touch any live system.

## Steps

### 1. Load state and baseline

```bash
S=<scratchpad>   # the session scratchpad; never commit snapshots
python3 scripts/skill_scoreboard.py --snapshot $S/run-baseline.json --top 20
```

Read `tracking.md`. Build the skip set (rule 7). Start the in-session fix ledger
(`references/agent-prompting.md`, block 7).

### 2. Pick the batch

Take the top of the board by priority, minus the skip set, up to the batch size. If the
user named skills, use those instead. Prefer variety: when three skills share one failure
(for example "no routing case"), one pass over all three in a single edit to
`evals/routing.jsonl` counts as one attempt per skill but still one comparison per skill.

### 3. For each skill: diagnose, edit, judge

1. **Snapshot** the current state: `--snapshot $S/before-<skill>.json`.
2. **Read** the SKILL.md and any file it loads. Score it against
   `.claude/skills/skill-audit/rubric.md` in your head: the scoreboard tells you what is
   missing, the rubric tells you what good looks like.
3. **Pick the gap** with the highest weight: hard finding, then routing miss, then missing
   signal. For a routing miss, read the rival skills' descriptions first; the fix is usually
   a sharper boundary sentence on one side, not more trigger phrases on both.
4. **Edit** with real content (rules 1 and 2). Keep the skill's existing voice and section
   order. Match the repo's style: no em or en dashes, sentence-case headings.
5. **Judge:** `python3 scripts/skill_scoreboard.py --compare $S/before-<skill>.json`.
   KEEP stays. REVERT or NO-CHANGE is reverted (rule 4), then one more attempt is allowed
   (rule 5).
6. **Log** the attempt in the in-session ledger: skill, gap, what changed, verdict, reason.

### 4. Close the run

1. Final judge against the run baseline: `--compare $S/run-baseline.json`. It must print KEEP.
   If it prints REVERT, a later edit broke an earlier gain: find it with the per-skill
   snapshots and revert that edit.
2. **Fresh-context review.** Spawn a reviewer agent that has not seen this session. Give it
   the diff (`git diff -- .claude/skills evals`), `.claude/skills/skill-audit/rubric.md` and
   rule 1 and 2 above as the primary evidence, and ask for a calibrated verdict per skill:
   `keep`, `narrow` (with the exact line to change), or `revert` (with the reason). Do not tell
   it to default to revert when unsure (`references/agent-prompting.md`, block 6). Apply
   `narrow` and `revert` verdicts, re-run the scoreboard judge on anything you changed, and
   log each verdict in the ledger. The script checks that nothing measurable got worse; the
   reviewer checks that what got better is real.
3. Run the gates: `python3 scripts/sync-codex.py`, then `bash scripts/preflight.sh`.
4. Append the ledger rows to `tracking.md`.
5. Open one PR (branch first if on `main`). Title: `skill-optimizer: <n> skills improved
   (priority <before> -> <after>)`. Body: the scoreboard compare output, one line per kept
   edit, the escalations, and any follow-ups rule 8 kept out of scope.

## Output

The run ends with this report in chat (and the same body in the PR). Example, the first
run on 2026-09-27:

```
VERDICT: KEEP
Scoreboard: signals 293 -> 314 | routing clear 134/152 -> 134/153 | no case 9 -> 8 | priority 1668 -> 1568

Kept (5)
- team-intro: boundary vs onboarding-doc-builder and access-welcome, fixed output sections, example
- gsc-freshness-check: done-when bar, boundary, dates quoted from the query; first routing case
- marketing-psychology: output format, grounding rule, example; removed 3 dead skill pointers
- retro: replaced the missing /pr-ship with the repo's PR path; real example from PR #374
- agent-builder: done-when, output, stale /marketing-os fixed, preflight added to deploy

Reverted (1)
- gsc-freshness-check: "feed" in the description stole a paid-acquisition case (REVERT)

Escalated (3)
- team-intro: "onboard a new marketer onto this repo" still goes to access-welcome; needs the owner
- gsc-freshness-check, skill-optimizer: new cases land weak-trigger; confirm with /skill-eval

Follow-ups outside the loop's scope
- curious-intern also points at /pr-ship

Fix ledger
- Judge keyed cases on line number, so inserted cases hid shifts (wrong). Fixed: key on request text.
```

Every section always appears. An empty one says so ("Reverted (0) - none") rather than
disappearing.

## Cadence

**Weekly cloud routine: Sundays 07:00 Asia/Jerusalem during IDT (cron `0 4 * * 0`, UTC).** After the clocks change on Oct 25 it fires at 06:00 local; to keep 07:00, change the cron to `0 5 * * 0` (`references/change-control.md`, cloud routines failure mode 4). Model: `claude-opus-5-5`. Routine `trig_017mMQa45aijvnMdxCT16yvv` (https://claude.ai/code/routines/trig_017mMQa45aijvnMdxCT16yvv), created 2026-09-28 by Hanan with no connectors attached: the loop needs only the repo, `git`, `gh` and Python. It also runs on demand; with `/goal` available a run can be stated as a goal, for example `/goal run /skill-optimizer until total priority is below 1400, stop after 12 edits`.

### Unattended runs

A scheduled run has nobody to ask, so four rules apply on top of the hard rules:

1. **One open optimizer PR at a time.** Before step 1, run `gh pr list --repo riversidefm/marketing-brain --state open --search "skill-optimizer in:title"`. If one is open, stop without editing anything: an unmerged run means this week's baseline is stale and its ledger rows would conflict. Report "skipped: PR #<n> still open" and end.
2. **No questions, no connectors.** Pick the batch from the board (step 2) without asking. The loop needs only the repo, `git`, `gh` and Python; if any of those fails, stop and put the failure in the PR body or the run's final message rather than working around it.
3. **Open the PR and stop.** Never merge, never arm a check-in or `send_later`, never come back to watch the PR (`references/change-control.md`, cloud routines failure mode 7). A red CI check is `/pr-doctor`'s job, not this run's.
4. **The fresh-context reviewer still runs.** Spawn it as a subagent exactly as in step 4.2. Skipping it because nobody is watching is the failure it exists to prevent.
