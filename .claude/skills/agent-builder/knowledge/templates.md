# Starter templates

Copy the block that matches the agent type (see `skill-anatomy.md` for the
taxonomy), then fill it in. These are scaffolds, not finished agents - delete
sections that don't apply and add the specifics.

**Every `<...>` angle-bracket marker below is a fill-in - replace all of them.**
Do not leave any `<...>` marker, `[bracketed]` guidance, or curly-brace
placeholder (the `{{...}}` tokens `/setup` uses) in the final file. Note what
each check catches: the CI lint fails on unfilled `{{...}}` markers, and
`../scripts/validate_skill.py` also rejects an unfilled `<...>` marker left in the
frontmatter `name` or `description` (both must be clean of `< >`). A `<...>`
marker left in the *body* is not caught automatically, so re-read the body
before you commit.

---

## 1. Workflow skill

A repeatable job with a fixed, schema'd output.

```markdown
---
name: <verb-or-noun-slug>
description: Use this skill when <who> wants to <job>. Produces <output>. Triggered by "<phrase 1>", "<phrase 2>", "<phrase 3>".
---

# <Title>

<One or two sentences: the job this does and what the finished output is.>

## Inputs and context to load
- Always start from CLAUDE.md.
- Load <references/... or systems/...> only when <condition>.
- <MCP tool / board / channel this reads>.

## Steps
1. <Gather> - <what to read, from where>.
2. <Process> - <how to filter/analyze; name the constraint that keeps it grounded>.
3. <Produce> - assemble the output in the schema below.

## Constraints
- Base every claim on the source; do not invent <owners/dates/metrics>.
- If <ambiguous case>, default to <fallback> rather than guessing.
- Confirm before any mutating call (this skill is interactive).

## Output schema
## <Section A>
- ...
## <Section B>
- ... (write "None" when empty, never drop the section)

## Done when
<The concrete condition that means this run is finished.>
```

---

## 2. Skill-agent (domain router)

Owns a domain's live access and routing. Invoked by `/marketing-os`.

```markdown
---
name: <domain>-agent
description: Specialist sub-agent for <domain>. Use when any skill needs to <the live operations it owns>. Invoke this agent instead of calling <MCP> tools directly - it knows Riverside's <IDs / structure / conventions>.
---

# <Domain> Agent

You own <domain> for the Riverside Marketing OS. You pull live data via <tools>,
frame it in Riverside's context, then invoke <specialist subagent> for the deep
pass, and return a recommendation - not raw data.

## What you own
- <live systems, IDs, conventions>

## How you work
1. Load <systems/owned/....md> and the relevant references.
2. Pull the live data (<tools>).
3. For a deep pass, invoke <specialist subagent> (`.claude/agents/...`).
4. Synthesize into a recommendation. Surface any mutating action for confirmation.

## Constraints
- Never mutate <system> without confirmation.
- Ground every claim in the pulled data.
```

Then register it: add a row to the Sub-Agent Registry in `CLAUDE.md` and the
registry table in `.claude/skills/marketing-os/SKILL.md`.

---

## 3. Interview / builder skill

Interviews the user, then generates an artifact. Model the flow on
`granola-recipe-builder` and `curious-intern`.

```markdown
---
name: <thing>-builder
description: Use this skill when the user wants to create/craft/improve a <thing>. Interviews the user, then generates <artifact>. Triggered by "<phrase>", "build a <thing>", "new <thing>".
---

# <Thing> Builder

Turn a vague "<I want X>" into a finished <artifact>, built on <the framework
this applies>.

## Step 1: Interview
Use AskUserQuestion, batched (2-3 questions at a time). Ask: <the dimensions
that change the output>. Follow threads; adapt to what they already said.

## Step 2: Gather reusable context
<What to read from the repo / what the user gave you.>

## Step 3: Generate
<Assemble the artifact in the framework's order. Show the format, don't
describe it. Deliver copy-paste-ready if it goes into another tool.>

## Step 4: Explain and test
<Explain the key choices; tell them how to try it on real input and report back.>

## Step 5: Save to the repo (ask first)
<Where it gets committed so the team benefits; open a PR.>
```

---

## 4. Specialist subagent (`.claude/agents/`)

Deep domain persona, no live system access. Read `.claude/agents/README.md`
first.

```markdown
---
name: <Display Name>
description: <Deep-domain one-liner: what this specialist masters.>
model: sonnet
tools: Read, Write, Edit, Grep, Glob, WebSearch, WebFetch
---

# <Display Name>

<!-- riverside-harmonized -->
## Riverside context
<Copy the concise block from .claude/agents/RIVERSIDE_CONTEXT.md>

## How this fits Riverside Marketing
<How this specialist is used and by which skill-agent.>

## <Domain expertise>
<Frameworks, methods, and craft. Keep it generic in the domain; keep Riverside
IDs/accounts/live data in the owning skill-agent and systems/references.>
```

**Scope the `tools` field to a non-live allowlist** (the craft tools above are a
sensible default; add `Bash` only if the specialist genuinely needs it). Do not
grant `All tools` or any live-system MCP tool (HubSpot, monday, Slack, ad
platforms) - specialists have no live system access by design; that access
stays in the owning skill-agent, which pulls the data and hands it to the
specialist for the deep pass.

Then register it in the tables in `.claude/agents/README.md` and under the
owning skill-agent's "Specialist subagents" section.

---

## 5. Cloud routine

A workflow skill that runs unattended on a schedule. Must be idempotent. Read
`routine-design.md` first: the cadence comes from how fast the signal changes,
and the three sections marked *required* below are what separates a routine
from a way to do the wrong thing on a schedule.

```markdown
---
name: <name>
description: <Cadence> automation that <job>. <What it reads> ... <what it produces>. Dedupes via <ledger/marker>. Runs <daily/weekly> as a cloud routine, or on demand. Trigger phrases - "<phrase>", "run the <name> agent".
---

# <Title>

<The job, and the exact output - usually a Slack DM or a monday/HubSpot write.>

## Acts when
<Required. The condition that makes a run do more than log "no action": a
threshold crossed, a record not in the ledger, a delta vs baseline. Most runs
should find nothing and say so.>

## Steps
1. Load the ledger/marker of what was already processed.
2. <Query the source> for <the window, e.g. "yesterday">.
3. Filter to <the precise criteria>. Dedupe against the ledger.
4. Run the self-check below. If it fails, log why and stop.
5. <Produce the output> (respect Slack tone + attribution footer if posting).
6. Update the ledger with what was processed this run.

## Self-check
<Required. What the run rules out before acting: tracking or source breakage,
seasonality, a sample too small to read. Name the minimum count.>

## Constraints (unattended - no human to ask)
- Idempotent: re-running never double-posts.
- Every ambiguous branch has a default, not a question.
- <Named fallback for each failure kind: glitch, tool down, empty, wrong.>

## Stop / bail-out
<Required. Source outage: report "stale data, no run" and exit. Escalate to a
person instead of acting on: <revenue or spend anomaly, strategic account,
anything public or bulk>. If the output goes unread for two cycles, ask once
whether to continue, then pause. The schedule is the kill switch; name the
trigger.>

## Cadence
Runs <cron cadence> (<intended local time>, cron is UTC). Chosen because <the
signal moves on this timescale>. Deployed as a recurring trigger that fires the
invocation prompt. Wire the schedule only after one tested real run.

## Done when
<Condition, e.g. "the summary is posted and the ledger is updated", or "no
action: logged and exited".>
```
