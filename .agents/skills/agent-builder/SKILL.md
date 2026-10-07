---
name: agent-builder
description: Use this skill when someone wants to build, create, author, scaffold, or deploy a new agent, skill, sub-agent, specialist, or cloud routine in the Riverside Marketing OS. Interviews the user, classifies what they are building, then generates a lint-clean SKILL.md (or subagent file) that follows the Agent Skills framework and this repo's conventions, validates it, registers it for routing, and opens the deploy PR. For a cloud routine it also sets the check cadence from how fast the signal moves, and the act, self-check and bail-out conditions. Triggered by "build an agent", "create a skill", "new skill", "make a skill", "author an agent", "scaffold a skill", "build a routine", "set up a recurring check or alert", "run this every week", "how often should it run", "add a sub-agent", "deploy an agent", "turn this into a skill", or "/agent-builder".
user-invocable: true
---

# Agent Builder

Turn "I keep doing this by hand" into a deployed, lint-clean agent that the
whole team can trigger. This skill interviews the user, classifies what they are
building, generates the files using the Agent Skills framework and this repo's
conventions, validates them against the CI lint, wires them into routing, and
opens the deploy PR.

**Philosophy (from `PHILOSOPHY.md`):** don't write a skill from scratch. Let the
AI interview you, generate a first draft structured for AI consumption, then
correct it. If it only works when its author runs it, it isn't done.

This skill practices what it teaches: a lean body, heavy reference in
`knowledge/`, and a deterministic validator in `scripts/`. Load the knowledge
files as you reach the steps that need them.

**Done when:** the new files pass `.claude/skills/agent-builder/scripts/validate_skill.py` with `RESULT: PASS`, the
skill has a Task Routing row in `CLAUDE.md` and at least one case in
`evals/routing.jsonl` that routes to it, `bash scripts/preflight.sh` is green, a
draft PR is open, and (for a cloud routine) one real run has been tested before
any schedule exists. A skill that is written but not routed, or routed but never
run on a real input, is not done.

## What this skill does not do

- **Improve skills that already exist.** Fixing the weakest existing skills in a
  measured loop is `/skill-optimizer`; scoring one skill's writing is
  `/skill-audit`; testing routing is `/skill-eval`.
- **Schedule a skill that is already built.** Adding a cron to an existing skill
  is `/schedule`.
- **Invent the facts the skill runs on.** Board IDs, channel IDs, people and
  thresholds come from the interview answers or from `references/` and
  `systems/`. If the user does not know one, write it as an open question in the
  PR body, never as a guessed value in the skill.

> **Ask through the `AskUserQuestion` tool, never as plain chat text.** Every
> choice this skill puts to the user - the classification, the interview, the
> name confirmation, and the deploy go-ahead - must be presented with the
> `AskUserQuestion` tool so the user gets interactive option cards. Do not type
> the questions into the chat as prose and wait for a reply: that is the exact
> failure mode this skill exists to prevent. Give every question concrete
> options; the user can always type a free-text answer via the built-in "Other"
> choice, so use that for genuinely open inputs (like the one-line job
> description) rather than dropping back to a chat question.

## Step 0: Classify what they are building

There are five agent types. The type decides the directory, template, and deploy
path. Read `knowledge/skill-anatomy.md` for the full taxonomy, then classify
from what the user said. If it is genuinely unclear, ask with an
`AskUserQuestion` call whose options are the five types below (one option per
row) - not a chat question:

| Type | It is... | Lives in |
|------|----------|----------|
| Workflow skill | a repeatable job with a fixed output (brief, report, standup) | `.claude/skills/<name>/` |
| Skill-agent (router) | a domain's live access + routing, invoked by `/marketing-brain` | `.claude/skills/<name>-agent/` |
| Interview / builder skill | interviews the user, then generates an artifact | `.claude/skills/<name>/` |
| Specialist subagent | a deep domain persona, no live access, `model: sonnet` | `.claude/agents/**` |
| Cloud routine | a workflow skill that runs unattended on a schedule | `.claude/skills/<name>/` + a schedule |

## Step 1: Interview (specification first)

Before writing anything, pin down the job. **Run the interview as
`AskUserQuestion` calls (interactive option cards), never as chat prose** - put
up to 4 question cards per call (the tool's per-call maximum) and expect about
two calls to cover everything below. Never drip one question at a time, and
never dump them as a wall of chat text. Adapt to what the user already told you
and skip what is already obvious, so you rarely need every question.

Give each question concrete options so the card is one click. Suggested options:

1. **Mutation** - options: `Read-only` / `Writes to a system (needs a
   confirmation gate)` / `Unattended routine (no human to confirm)`.
2. **Systems it touches** (multi-select; `None` is exclusive - if the user
   picks `None`, ignore any other selection) - options: `monday` / `HubSpot` /
   `Slack` / `Omni or Snowflake` / `Website or Webflow` / `Web search` / `None`.
3. **How fast does the signal change?** (only if it is a cloud routine) -
   options: `Hours to a day (inbound requests, at-risk accounts)` / `A few
   days (ad fatigue, CPA drift)` / `A week or more (rankings, funnel step
   rates, competitor pages)` / `A month or more (content decay, backlog)`.
   The answer sets the check cadence; do not offer daily/weekly/monthly as a
   preference. Then ask **Acts when** - what must be true for a run to do
   more than log "no action" - with `Other` for the threshold. Rule and
   examples: `knowledge/routine-design.md`.
4. **Tone** - options: `Team Slack style (energetic, emojis, attribution
   footer)` / `Neutral internal` / `Match an existing skill`.

For the genuinely open inputs - the one-line **job / finished output**, the
**triggers** (what users type to invoke it, which becomes the `description`),
and the **output shape / sections** - still ask through `AskUserQuestion`: give
a couple of sensible starter options and let the user type specifics via the
"Other" free-text choice. Do not fall back to a plain chat question.

Follow threads. A named recurring meeting, a specific board, or a downstream
tool changes the spec - fold it in.

## Step 2: Name and describe

Read the frontmatter rules in `knowledge/skill-anatomy.md`. Propose a `name`
(lowercase, hyphens, ≤64 chars, no `claude`/`anthropic`) and a `description`
that states **what it does and when to use it**, with the real trigger phrases
from Step 1. Skill-agents end in `-agent`; builders end in `-builder`. Confirm
the name with the user via `AskUserQuestion` before creating files (offer the
proposed name plus 1-2 alternatives as options) - it is the directory and the
`/slash` handle.

## Step 3: Author, in layers

Open `knowledge/templates.md`, copy the block for the type, and fill it in.
Follow `knowledge/authoring-checklist.md` (the five building blocks). Author in
layers, not one maximal pass:

1. **Core behavior** - the steps that do the job.
2. **Structure** - named sections in a fixed order.
3. **Constraints** - grounding ("don't invent what isn't in the source"), a
   named fallback for every "if unclear" branch, a confirmation gate for
   mutations, idempotency for routines.
4. **Output schema** - exact section titles and the fallback text for empty
   sections ("None today", never a dropped section).
5. **One example** - a concrete input→output if tone or format matters.

**Progressive disclosure:** keep `SKILL.md` lean (under ~5k tokens). Push heavy
reference tables, long templates, or per-system config into a `knowledge/` file
and link to it. Keep IDs, board numbers, and dashboard URLs in `systems/` /
`references/` / the skill's own `knowledge/`, never inlined here. Use a
`scripts/` file for any exact, repeatable operation (only its output costs
tokens).

For a **specialist subagent**, read `.claude/agents/README.md` first: add the
Riverside context block, set `model: sonnet`, and prepare the registry edits.

For a **cloud routine**, read `knowledge/routine-design.md` before filling
template 5: it holds the cadence rule and the three sections a routine cannot
ship without (Acts when, Self-check, Stop / bail-out). If the user has not
named the routine yet, `knowledge/routine-ideas.md` lists candidates already
mapped to this department's platforms and owners.

## Step 4: Validate (pre-flight gate)

Run the validator before anything else, pointing it at the target path you
classified in Step 0. It mirrors the repo CI lint (`.github/workflows/team-context-lint.yml`) plus
the framework frontmatter rules, and accepts either a skill directory or a
specialist subagent file:

```bash
# workflow skill / skill-agent / builder / cloud routine:
python3 .claude/skills/agent-builder/scripts/validate_skill.py .claude/skills/<name>

# specialist subagent:
python3 .claude/skills/agent-builder/scripts/validate_skill.py .claude/agents/<path>.md
```

Fix every `FAIL` (they will fail the PR) and consider each `WARN`. Do not
proceed to deploy until it prints `RESULT: PASS`.

## Step 5: Register for routing

A skill nobody can find will not trigger. Wire it in:

- **Any user-facing skill:** add a row to the **Task Routing** table in
  `CLAUDE.md` (and, if it is a domain agent, the **Sub-Agent Registry**).
- **Skill-agent:** also add it to the registry table in
  `.claude/skills/marketing-os/SKILL.md`.
- **Specialist subagent:** add it to the registry tables in
  `.claude/agents/README.md` and under its owning skill-agent.
- **New reference/knowledge file consumed elsewhere:** add a pointer where a
  reader would look for it.

Keep additions concise and match the density of the surrounding table.

Then prove the routing actually works, in the same PR:

1. Add at least one case to `evals/routing.jsonl` - phrased the way the user
   described the job in Step 1, not the way you worded the description. If the
   new skill has a near-identical sibling (a weekly/monthly pair, a second QA
   surface, another brief), add a case for **the sibling too**: the risk of a new
   skill is that it steals requests from an existing one, and only a case on the
   incumbent catches that.
2. Run `python3 scripts/eval_routing.py`. A structural failure means the suite is
   broken - fix it before deploying. A new *warning* on a skill you did not touch
   is the signal that matters: your description overlaps something that already
   worked. Narrow yours rather than padding theirs.
3. If a warning is ambiguous, run `/skill-eval` for the judgement call and the
   proposed description patch.

`evals/README.md` covers how to write a case that tests something; `docs/skill-evals.md`
covers why this tier exists.

## Step 6: Deploy

Show the user a summary of the new files and registry edits, then get the
go-ahead via `AskUserQuestion` with these options: `Commit and open the PR` /
`Let me review the files first` / `Change something`. Only the first proceeds to
commit:
- `Let me review the files first` - do not commit; point them at the files (or
  wait while they read), then ask this question again.
- `Change something` - do not commit; use `AskUserQuestion` to collect the
  requested edit (with an `Other` free-text option), return to Step 3, make the
  edit, re-run the Step 4 validation, then ask for approval again.

Never commit until the user picks `Commit and open the PR`. Read
`knowledge/skill-anatomy.md` ("Where skills run, and how they deploy") for the
surface details. For this repo the path is:

1. Commit the skill files + registry edits to a branch (`agent-builder/<slug>`
   or the session's designated branch).
2. Before pushing, run `python3 scripts/sync-codex.py` (the Codex port under
   `.agents/` is generated from `.claude/`, so every new skill needs it
   committed alongside) and then `bash scripts/preflight.sh`. Step 4 covers only
   the skill's own file; preflight runs every PR gate in CI's order.
3. Open a **draft PR**. It should be green on arrival because preflight passed.
4. On merge, the Wiki + Graph Sync workflow regenerates the wiki
   page and the knowledge graph automatically. You do not hand-write those.

**Cloud routine only:** deploying is two parts - the files (above) and a
schedule. Wire the recurring trigger that fires the skill's invocation prompt
**only after** one tested real run. State the cadence in the skill's
`description` and body, with the intended local time next to the UTC cron
(`references/change-control.md`, failure mode 4).

**Other surfaces (mention if the user needs them):** custom skills do not sync
across surfaces. claude.ai takes a `.zip` upload per user; the Claude API takes
an upload via `/v1/skills` (workspace-wide, no network at runtime). The repo
path above is the team default.

## Output

The run ends with this summary in chat, then the PR link:

```
Built: <name> (<type>)
Files: .claude/skills/<name>/SKILL.md [+ knowledge/..., scripts/..., tracking.md]
Validation: RESULT: PASS | preflight green
Routing: CLAUDE.md row added; eval case "<request>" -> <name> (clear | ambiguous)
Deploy: draft PR <link> | cloud routine: schedule pending first real run
Open questions: <facts the user did not know, or "none">
```

## Step 7: Test before extending, then capture

- Run the new agent on one real input. Confirm the output matches the schema and
  the constraints held. Tighten a rule if anything looked off - do not add new
  features before the core is reliable.
- Suggest `/retro` so the build itself and any non-obvious decision is captured
  for the next person.

## Key principles

- **Ask with the tool, not the chat.** Every user choice - classification,
  interview, name, deploy go-ahead - uses `AskUserQuestion` interactive cards
  with concrete options. Typing the questions into the chat as prose is the
  failure mode.
- **Classify before you write.** The five types have different homes, templates,
  and deploy paths. Getting the type right is most of the job.
- **The description is the trigger.** It must say what *and* when, in the words
  users actually type. A "what only" description will not fire.
- **Progressive disclosure by default.** Lean `SKILL.md`, heavy content in
  `knowledge/`, exact operations in `scripts/`.
- **Constraints and fallbacks over cleverness.** Every ambiguous branch names
  its default. Every mutation asks first (except deliberate routines).
- **Validate locally, deploy clean.** `scripts/validate_skill.py` before the
  PR, every time.
- **Register it or it does not exist.** Routing only finds what is wired into
  `CLAUDE.md` and the relevant registry.
- **Repo over one-off.** The finished agent lands in version control where the
  whole department benefits.
