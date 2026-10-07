<!-- last-reviewed: 2026-09-24 (two habits: a patch has to land everywhere the old rule lives) -->
# Agent Prompting Principles

How to write prompts for agents (skills, sub-agents, cloud routines) so they behave like reliable systems, not one-off chat replies. Distilled from ClickUp's agent prompting guide (https://clickup.com/blog/agent-prompting-guide/), mapped to how this repo authors `.claude/skills/` and scheduled routines.

**Use this when:** writing or reviewing a `SKILL.md`, a `.claude/agents/` persona, or a cloud-routine prompt.

## The core distinction

| | Generative prompting | Agent prompting |
|---|---|---|
| Goal | Exploration, creativity | Reliability, structure |
| Mindset | "Give me something" | "Do this job every time" |
| Output | Flexible, open-ended | Repeatable, structured |

An agent prompt is a **job description, a contract, and a set of rules** - not a question. Every skill in this repo that runs unattended (routines like `/nir-mql-live-report`, `/invoice-inbox-to-monday`, `/p1-p2-followup`) lives on the agent side of this table.

## Five building blocks

Layer these in order when authoring a skill:

1. **Specification first.** Before writing the prompt, define the job: inputs, expected outputs, constraints, and what success looks like. (In this repo: the skill's frontmatter `description` + an explicit "done when" in the workflow.)
2. **Layer gradually.** Start with core behavior, then add structure (named sections, fixed order), then higher-value logic (recommendations, gap detection). Don't write the maximal prompt in one pass - each layer should be tested before the next is added.
3. **Constraints create consistency.** Explicit guardrails prevent hallucination and drift: "don't invent items not found in the source", "if X is unclear, default to Y", "keep reasoning grounded strictly in the input". Defaults for ambiguous cases matter as much as rules for clear ones. (Repo examples: the `/good-morning` `channel_not_found` fallback rule, "Marketing Ops doesn't run sprints", dedupe ledgers on routines.)
4. **Multi-shot examples.** One or two concrete input-to-output examples anchor tone, depth, and format better than adjectives do. Show the expected output, don't just describe it.
5. **Schema the output.** Fix exact section titles, mandatory sections, formatting rules, and fallback text ("No items today" instead of omitting the section). A reader - human or downstream agent - should be able to parse the output without guessing.

## Block 6: build the critic into the loop

The five blocks above come from the ClickUp guide. This one is added from the
evaluator-optimizer pattern in Anthropic's
[claude-cookbooks](https://github.com/anthropics/claude-cookbooks)
(`patterns/agents/evaluator_optimizer.ipynb`), because blocks 1-5 all describe how to write
a prompt and none of them tells you how to know it worked.

**Where a generator and a critic beat one careful pass.** Two conditions, both required:
the criteria can be stated explicitly, and a reviewer's feedback would demonstrably improve
the output. Deck copy, page copy, a report narrative, a QA finding, a task story all qualify.
A data pull does not - there is nothing to iterate toward that a correct query doesn't
already give you.

The shape, when it applies:

1. **Generate** against the spec (block 1).
2. **Evaluate** against explicit criteria, as a separate pass that is only allowed to
   critique - a critic that starts rewriting stops being a check. Return a verdict plus
   *what to change and why*, not a rewrite.
3. **Revise** with the previous attempt and the feedback both in view, so it fixes the gap
   instead of regenerating a different draft with new gaps.
4. **Stop** on a pass, or after two rounds. If it hasn't converged by then the criteria are
   the problem, not the draft - say so rather than looping.

Three ways this goes wrong: criteria vague enough that everything passes on the first round
(the loop cost you a pass and told you nothing), a critic that keeps finding new
objections forever (no stated bar, so nothing can clear it), and a critic told to assume the
worst - the one that looks rigorous and is not. Name the bar, in the prompt, in
terms someone could disagree with.

**Do not instruct a verifier to "default to refuted if uncertain".** It reads as healthy
scepticism and it destroys the signal. On 2026-09-09 an adversarial panel carrying that line
refuted 33 of 34 findings, and nearly every kill was a wording quibble against a claim whose
substance held. A verdict set that rejects almost everything is as useless as one that rejects
nothing, because neither ranks anything. Ask for a calibrated verdict instead - confirmed /
needs-narrowing / refuted, with the corrected claim when it is nearly right - and read a
near-total refutation rate as a defect in your prompt, not a finding about the work.

**Give a verifier the primary evidence, not just the claim.** A refuter without the source will
correctly report that nothing supports the claim, which is a fact about its context and not
about the claim. In that same run one agent "refuted" an id-to-name mapping that was sitting
verbatim in an API response the parent had already read. Pass the response body, the file
excerpt or the measurement, or accept that you are testing recall rather than truth.

**A skill that ships one-shot output should say what its bar is** even when it runs no loop.
"Done when" from block 1 is that bar; if it can't be stated, the spec isn't finished.

**Test the routing surface too.** A skill's `description` is a prompt - the one the router
reads - and it is the least tested prose in the repo. Reword one and requests silently move
between skills. `evals/routing.jsonl` plus `/skill-eval` is block 6 applied to that surface:
scored cases, a named cause per miss, and a proposed patch. Run it after touching any
description. Design: `docs/skill-evals.md`.

## Block 7: name the failure, match the fix, keep a fix ledger

Filed 2026-09-08 from Greg Isenberg's "self-healing agents" post on X. Most of it was
already here in pieces (block 3 fallbacks, the abort-without-writing rule in
`references/change-control.md`, maximal-payload-then-ablate in
`references/integration-debugging.md`). What was missing is the taxonomy that ties them
together and the in-session log.

**A prompt that says "if X fails, do Y" has handled one failure. Four kinds exist**, and
each wants a different fix:

| Failure | What it looks like | The matched fix |
|---|---|---|
| Glitch | Timeout, rate limit, transient 5xx | Retry once, then treat as "tool down" |
| Tool down | Auth error, `channel_not_found`, connector unreachable | Switch to the named backup source, or skip the section with a stated substitution. Never a browser/screenshot workaround on your own |
| Empty | Call succeeded, returned nothing | Say "no items" in the schema slot (block 5). Do not re-query with looser filters to make data appear |
| Wrong | Call succeeded, answer fails the check | Break the task smaller and re-verify each part. If two sources disagree, that is a finding (`references/evidence-standards.md`) |

Two rules sit on top of the table. **Anything risky stops and asks**: a write to HubSpot,
monday, Slack, Gmail, or a deletion is never the retry path. **The agent can only fix a
failure it can see**: a skill that calls a tool should say what error text comes back and
where it goes, not just "handle errors".

**Check each step before the next one.** After a step, the prompt should ask "is this what
the spec expected?" rather than assume success and continue. The routine that fired six
times on one PR in `references/change-control.md` failed this way: each run assumed the
previous had not happened.

**Keep an in-session fix ledger.** Any skill that runs more than a couple of tool calls,
and every cloud routine, keeps a short running list during the run: what broke, which of
the four kinds, what fixed it. Inside the run, the agent checks the ledger before retrying,
so it stops repeating a fix that already failed. After the run, the ledger is the first
input to `/retro` (its Step 1 asks for it), which patches the exact failure instead of
reflecting on the run in general. A routine's output should end with that ledger, or the
line "No failures this run".

**How to read this against blocks 1-6.** Block 3 says name the fallback. Block 7 says name
the failure first, because the right fallback depends on which kind it was.

## Principles worth enforcing in reviews

- **Build systems, not text.** If a skill only works when the author runs it, it isn't done.
- **Grounding beats cleverness.** Require the agent to cite or quote its source data; forbid inventing entities that aren't in the input.
- **Ambiguity needs a default, not a guess.** Every "if unclear" branch should name its fallback.
- **Test before extending.** Run the skill on real data after each layer, not once at the end.
- **Every "if it fails" branch names which failure it handles.** Glitch, tool down, empty, or wrong (block 7). A skill with tool calls and no fix ledger isn't finished.
- **Conflicting sources are a finding, not a footnote.** Grounding (block 3) covers "don't invent"; `references/evidence-standards.md` covers what to do when two systems disagree.

These align with `/health-check`, `/skill-eval`, and `/retro`: when a skill misbehaves, the fix is usually a missing constraint (block 3) or a missing schema/fallback (block 5), not a rewrite. The three cover different failures - stale docs, wrong routing, lost learning - so a skill that behaves oddly is worth checking against all three before rewriting anything.

## Two habits that keep the rules honest

Filed from the Lauren Tan agent workshop, 2026-08-29. Both are about the gap between a rule
being written down and a rule being followed.

**A retro should patch the specific failure, not reflect generally.** `/retro` tends to
produce a well-written summary of what happened, which reads as insight and changes nothing.
The step that actually moves the needle is narrower: find the exact point where the agent
*guessed* or *skipped* - the field it invented, the source it did not open, the confirmation
it did not wait for - and encode that one failure as a hard rule in the skill that owns it.
"Be more careful with dates" is a reflection. "Never write a `Due` the input does not state;
use `-`" is a patch. Only the second one survives into the next session.

**Audit for convenient wrong paths.** This repo is full of rules shaped "never do X, always
use `/skill`" - never call the monday API directly, never read Monday in the chief-of-staff
brief, never create a task outside `/pm-story`. A rule like that is a losing bet whenever the
forbidden path is still the *easiest* one available, because the agent under context pressure
takes the short path and reads the rule as advice. So the fix is structural, not rhetorical:
make the sanctioned path shorter than the forbidden one, or remove the forbidden one from
reach. Worth a standing pass over every "never do X" in `CLAUDE.md` and the skills, asking
which of them are still the path of least resistance.

**A patch has to land everywhere the old rule lives, not only where the failure showed up.**
Before calling a fix done, grep for the claim you are replacing, in three places:

1. **The rest of the same skill.** A fix added lower down does not overrule a contradicting
   line higher up; the agent follows whichever it reads first. `/pm-story` got "post the brief
   as an update, never the description" on 2026-09-02, but line 14 still said the output is
   "a Monday item description". On 2026-09-16 an agent followed line 14, and the ticket looked
   empty to everyone.
2. **Sibling skills that keep their own copy.** `/ticket-hygiene` has its own update template
   and only points at `/pm-story` for context. The 2026-09-23 escaping fix went into
   `/pm-story` alone, so the template that had actually produced the escaped update stayed
   broken.
3. **Run logs and ledgers.** A lesson written only into a routine's ledger (e.g. `.claude/skills/ticket-hygiene/data/ledger.md`)
   is history, not an instruction. On 2026-09-23 the `/ticket-hygiene` ledger recorded that
   commercial proposals are not Marketing Ops work, while Step 4 still sent ambiguous asks to
   MOPs. If a run learns a rule, it changes the `SKILL.md` or flags that the `SKILL.md` needs a
   PR. Fixed in `#390`.
