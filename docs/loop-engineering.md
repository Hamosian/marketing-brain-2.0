<!-- last-reviewed: 2026-09-27 -->
# Loop engineering

The Marketing OS improves through loops, not one-off edits. A loop is only real if you can
name six things about it; anything missing is where it silently stops working. This page is
the inventory of every loop in the repo, the contract each one must meet, and the loops we
do not have yet.

## Four kinds of loop, by what starts them

A loop is an agent repeating a cycle of work until a stop condition is met. The Claude Code
team's [getting started with loops](https://claude.com/blog/getting-started-with-loops)
sorts them by trigger, and that is the first choice to make:

| Kind | Started by | Stops when | Use it when | Primitive |
|---|---|---|---|---|
| Turn-based | A prompt | The agent judges the task done | You can write the check into a skill | A skill with a verification step |
| Goal-based | A prompt with a target | The target is met, or the try limit is hit | "Done" is measurable | `/goal`, or a skill with a script judge |
| Time-based | An interval | Cancelled, or the work runs out | Work arrives on a schedule, or you are watching an external system | `/loop` (local), `/schedule` (cloud) |
| Proactive | An event or schedule, nobody watching | Each task completes; the routine runs until disabled | The work is recurring and well defined | `/schedule` plus a goal and a skill |

Pick the lightest kind that fits. Match the interval to how fast the signal really moves
(`.claude/skills/agent-builder/knowledge/routine-design.md`), and the model and effort to
the task: those are the main cost levers.

## Every loop names six things

| Field | The question it answers | What breaks without it |
|---|---|---|
| Signal | What do we measure, and where does the number come from? | The loop optimizes a feeling |
| Step | What single change does one round make? | Many changes at once, and no way to tell which one helped |
| Judge | Who decides keep or revert, and against what bar? | The author grades their own work, and everything passes |
| Budget | How many rounds before it stops? | Infinite polishing, or a critic that never clears anything |
| Memory | Where is each attempt recorded? | The same failed fix gets retried every run |
| Exit | Who or what lets the result reach `main`? | An agent changes shared state with no human gate |

Two design rules sit on top, both from `references/agent-prompting.md` (blocks 6 and 7):

- **The judge is separate from the step.** A critic that rewrites is not a check. Where the
  signal can be computed, compute it (a script beats a model grading itself).
- **The reviewer gets fresh context.** A reviewer that shares the author's context shares
  its blind spots. Where the work is judgement rather than a number, hand the diff to a
  separate agent that did not write it.
- **Stop after two rounds.** If a loop has not converged by then, the criteria are the
  problem. Escalate to the owner rather than looping.

## The loops we run

| Loop | Kind | Signal | Step | Judge | Budget | Memory | Exit |
|---|---|---|---|---|---|---|---|
| Knowledge flywheel (`/retro`) | Turn | A non-obvious learning in a run | Route it to the right file | PR review | One per learning | Git history | Human merge |
| Writing quality (`nik-voice` > `de-ai` > `critique`) | Turn | Critique score on six dimensions | One revision | `critique` SHIP/REVISE | One revise, then re-run | In-session | SHIP verdict |
| Preference loop (`/chief-of-staff`) | Proactive | What Nir says about the brief | Rule into `.claude/skills/chief-of-staff/knowledge/nir-preferences.md` | Nir | Per brief | That file | Promotion into SKILL.md |
| Skill optimizer (`/skill-optimizer`) | Goal, run weekly (proactive) | `scripts/skill_scoreboard.py` | One edit to one skill | `skill_scoreboard.py --compare`, then a fresh-context reviewer on the batch | 5 skills, 2 attempts each | `.claude/skills/skill-optimizer/tracking.md` | Human merge |
| Routing eval (`/skill-eval`) | Turn | `evals/routing.jsonl` | Description patch | Deterministic tier in CI, model tier on demand | Per miss | The suite | Human merge |
| Red PR repair (`/pr-doctor`) | Proactive | Failing required check | One playbook fix | Re-run the failed gate | One attempt per head SHA | `.claude/skills/pr-doctor/tracking.md` | Human merge |
| Build gate (`/agent-builder`) | Goal | `.claude/skills/agent-builder/scripts/validate_skill.py` | Fix each FAIL | `RESULT: PASS` | Until pass | None | Deploy step |
| Maintenance (RALPH, `/health-check`) | Time | Staleness, trigger accuracy | Review, audit, learn, prune, hand off | Owner | Quarterly | Health reports | Human merge |

The skill optimizer is the only loop that applies its own fixes and then judges them. It
uses two judges because each misses what the other sees: the script cannot be argued with
but only checks what regexes can detect, and the fresh-context reviewer reads for quality
but is a model. The result still goes through PR review. Its rules against gaming the signal
are in its SKILL.md.

Our scheduled routines (`/pr-doctor`, `/gsc-freshness-check`, `/invoice-inbox-to-monday`,
`/chief-of-staff`, and the rest) are proactive loops. Each one's contract lives in its own
SKILL.md and ledger file; the table lists only the loops that improve the brain itself.

## The loops we do not have yet

Every loop above is closed by a human or by a check on the repo. None of them is closed by
a **business outcome**. Three candidates, in order of how cheap the signal is:

1. **Draft acceptance.** For skills that draft for a person (`/inbound-demo-reply`,
   `/chief-of-staff` packs, `/nir-weekly-report`), record whether the draft was sent as-is,
   edited, or dropped. A draft that is always rewritten is a skill with a gap. The signal
   already exists in the sent message; nothing captures it.
2. **Routine usefulness.** For scheduled routines, whether the output was opened or acted
   on. A routine nobody reads is a candidate for `/health-check` pruning.
3. **Metric movement.** For changes that should move a number (page CRO, lifecycle, paid),
   the before/after figure from `/rivermind:ask`, recorded against the change. This needs
   the evidence rules in `references/evidence-standards.md` and a waiting period, so it is
   the most expensive.

When one of these gets built, add it to the table above with all six fields filled in.
