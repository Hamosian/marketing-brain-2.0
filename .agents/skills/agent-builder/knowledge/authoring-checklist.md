# Authoring checklist

Load this while writing the body of a new agent. It turns the repo's agent
prompting principles (`references/agent-prompting.md`) into a checklist you can
verify item by item. An agent prompt is a **job description, a contract, and a
set of rules** - not a chat question.

## The five building blocks (layer in this order)

Write in layers. Get the core behavior working, then add the next layer. Do not
write the maximal prompt in one pass.

1. **Specification first.** Before prose, pin down the job: inputs, outputs,
   constraints, and what "done" looks like. In a skill this becomes the
   `description` (the contract) plus an explicit "Done when" in the body.
2. **Layer gradually.** Core behavior → named sections in a fixed order →
   higher-value logic (recommendations, gap detection, dedupe). Test each layer
   on real data before adding the next.
3. **Constraints create consistency.** Explicit guardrails prevent drift and
   hallucination: "don't invent items not in the source", "quote the source",
   "if X is unclear, default to Y". **Every ambiguous branch names its
   fallback.** Defaults for unclear cases matter as much as rules for clear ones.
4. **Multi-shot examples.** One or two concrete input→output examples anchor
   tone, depth, and format better than adjectives. Show the output; don't
   describe it.
5. **Schema the output.** Fix the exact section titles, which sections are
   mandatory, formatting rules, and the fallback text for empty sections
   ("None today", not a dropped section). A human or a downstream agent should
   parse the output without guessing.

## Constraint patterns that pull their weight

Copy the shape, fill in the specifics:

- **Grounding:** "Base every claim on the source data. Do not invent owners,
  dates, metrics, or decisions. Write 'unclear' when the input is ambiguous."
- **Named fallback:** "If reading channel X returns `channel_not_found`, do not
  treat it as an outage - skip the source, substitute a channel the runner can
  access from `references/slack.md`, and note the substitution."
- **Confirmation gate (interactive skills):** "Before any mutating call
  (HubSpot/monday/Slack write), show the change and ask for confirmation."
- **Idempotency (routines):** "Dedupe against a processed ledger / an event
  marker so re-running is safe and never double-posts."
- **Scope guard:** "Only read the boards/channels listed here. Do not widen the
  query."

## Riverside conventions any new agent must respect

Pull these from `CLAUDE.md` and the references - don't reinvent them:

- **Be concise.** Brief, direct output. Skip boilerplate.
- **Progressive disclosure.** Keep `SKILL.md` lean; push heavy detail to
  `knowledge/`. Keep IDs, board numbers, dashboard URLs in `systems/` or
  `references/` or the skill's own `knowledge/`, never inlined in `CLAUDE.md`.
- **Pointers, not copies.** Link to boards/dashboards/HubSpot views; never
  duplicate live data into the repo.
- **Rivermind first for data questions**, then `/data-agent`. Use `/pm-story`
  for monday task creation, `/data-team-request` for the Data Team's board.
- **Slack tone + attribution.** Team-sent messages are energetic, use emojis,
  reply in-thread when in a thread, and end with the footer line
  `_Posted by the Marketing OS agent_`.
- **Safety first.** Confirm before mutating anything, unless the skill is a
  deliberately unattended routine that says so.
- **Names and IDs** come from `references/team.md`, `references/slack.md`,
  `references/monday_boards.md`. Resolve people/channels/boards from there.

## Type-specific requirements

- **Skill-agent (router):** state the domain it owns and the live tools it uses.
  It pulls live data and frames Riverside context, then invokes a specialist
  subagent for the deep pass. Register it in `CLAUDE.md` Sub-Agent Registry and
  in `.claude/skills/marketing-os/SKILL.md`.
- **Specialist subagent (`.claude/agents/`):** add the `## Riverside context` +
  `## How this fits Riverside Marketing` block (copy from
  `.claude/agents/RIVERSIDE_CONTEXT.md`), set `model: sonnet` in frontmatter,
  and add it to the registry tables in `.claude/agents/README.md` and the
  owning skill-agent. No live system access.
- **Cloud routine:** must be idempotent (ledger/marker), must state its cadence
  and its "done when", and must handle its own failure modes (e.g. a source
  returning empty or erroring). It runs with nobody watching - every ambiguous
  branch needs a default, not a question. The cadence is justified against how
  fast the signal changes, and the body fills **Acts when**, **Self-check** and
  **Stop / bail-out** concretely (`routine-design.md`); a routine that cannot
  fill those three is not ready to schedule.
- **Interview / builder skill:** batch questions with `AskUserQuestion` (2-3 at
  a time, never drip one at a time, never dump ten), show a summary before
  writing files, and offer to save the result to the repo so the team benefits.

## Pre-flight gate (must pass before PR)

From the repo root, run the validator against the target you are building (the
same command `SKILL.md` Step 4 uses):

```bash
python3 .claude/skills/agent-builder/scripts/validate_skill.py <target>
```

`<target>` is the new skill directory (`.claude/skills/<name>`) or, for a
specialist subagent, its file (`.claude/agents/<path>.md`). It mirrors the CI
lint and the framework frontmatter rules. All of these must hold:

- [ ] `SKILL.md` starts with `---` and has `name:` and `description:`
- [ ] `name`: lowercase/numbers/hyphens, ≤64 chars, no `claude`/`anthropic`
- [ ] `description`: non-empty, ≤1024 chars, says what **and** when (triggers)
- [ ] No unfilled curly-brace placeholder markers (the `{{...}}` tokens) anywhere in the skill
- [ ] No binary/packaged files bundled (`.zip`, `.plugin`, `.tar.gz`, `.jar`)
- [ ] `SKILL.md` body stays within the progressive-disclosure budget (heavy
      content moved to `knowledge/`)
- [ ] Output schema is explicit; every "if unclear" branch names its fallback
- [ ] Registered in `CLAUDE.md` (and the relevant registry) so routing finds it
