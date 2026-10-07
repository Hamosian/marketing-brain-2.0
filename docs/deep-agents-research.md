<!-- last-reviewed: 2026-09-16 -->
# Deep Agents: research and what the Marketing OS should adopt

> **Audience:** anyone deciding how the Marketing OS agent stack should evolve. **Thesis:** "deep agents" is a named pattern for long-horizon, multi-step agent work. The Marketing OS already implements three of its four pillars. The gap is explicit, persisted planning, and the under-used lever is parallel sub-agent fan-out. Both are now buildable with primitives the harness already gives us, at low cost. Companion to `docs/marketing-os-technical-architecture.md`.

---

## 1. What a "deep agent" is

A **deep agent** is a tool-calling agent hardened for tasks that run across dozens of steps and outgrow a single context window, as opposed to a **shallow agent** that loops "call tool, read result, call next tool" and loses the thread on anything long. The pattern was popularised by LangChain's open-source Deep Agents harness (first released July 2025) but the shape is general and matches how Claude Code itself is built.

It rests on **four pillars**, layered on top of an ordinary tool loop:

| Pillar | What it does | The failure it prevents |
|--------|--------------|-------------------------|
| **Planning tool** | An explicit `write_todos` / task-list tool. The agent writes a plan before acting, tracks each step's status, and revises the plan when a step reveals something new. | The agent forgetting the goal, or skipping steps, once the conversation is long. |
| **Sub-agents** | A `task` dispatcher spawns ephemeral child agents, each with a **fresh, isolated context**, that run to completion and return a compressed result. | One giant context filling with raw tool output ("context pollution") until the agent degrades. |
| **Virtual filesystem** | `read_file` / `write_file` / `edit_file` over a working store. Large results and intermediate notes are written to files, not kept inline; skills and long-term memory are read from files on demand. | Losing work when history is summarised, and paying to re-read the same large blob every turn. |
| **Detailed prompt + skills** | A rich system prompt plus domain **skills** (knowledge and procedure) loaded **on demand**, not all at once. | A thin prompt that cannot carry a real workflow, or a bloated one that drowns the model in irrelevant instructions. |

Supporting **middleware** ties them together: automatic history summarisation, offloading large tool results to the filesystem, prompt caching for the static system content, and **human-in-the-loop interrupts** that pause on sensitive actions (a file write, an expensive or mutating call) for approval. Newer versions add **asynchronous sub-agents**, where the dispatcher returns a task ID immediately and the parent keeps planning while children stream results back, and **cross-run long-term memory**, so an agent does not start from zero on every deployment.

Sources at the end of this document.

---

## 2. The Marketing OS is already a deep agent system, on three of four pillars

Mapped against our own stack (see `docs/marketing-os-technical-architecture.md` and `.claude/agents/README.md`), the correspondence is close enough that most of the pattern is already shipping:

| Deep agent pillar | Marketing OS today | State |
|-------------------|--------------------|-------|
| **Sub-agents (isolated context)** | The **two-layer split**: routing skill-agents delegate a deep pass to specialist sub-agents in `.claude/agents/`, each invoked with fresh context and no live-system tools, returning the fixed `Summary / Findings / Recommendations / Open questions / Not verified` contract. | **Strong.** This is textbook context isolation, plus a governance property the stock pattern lacks: specialists physically cannot mutate live systems. |
| **Virtual filesystem / long-term memory** | **Git is the brain.** Durable knowledge lives in `CLAUDE.md`, `references/`, `systems/`, skill `knowledge/`, versioned and attributable. Routines persist idempotency ledgers (the per-skill tracking.md files) committed back. A per-session scratchpad exists for working files. | **Strong for long-term, thin for within-run.** Git covers cross-run memory better than a stock `AGENTS.md`. What is not yet a convention: writing intermediate results to the scratchpad mid-run to keep context lean. |
| **Detailed prompt + on-demand skills** | **Progressive disclosure** is the core rule. `CLAUDE.md` is a lean always-loaded map, everything else (30+ skills, `systems/`, `references/`) loads only when the task names it. `graphify` gives scoped retrieval without a vector store. | **Strong.** This is a mature, deliberate implementation of the "skills loaded on demand" pillar. |
| **Planning tool** | No persisted planning discipline. The router classifies a request into one of seven intents and delegates, but there is no explicit, tracked, revisable plan that survives context compaction within a long run. | **Gap.** This is the missing pillar. |

The human-in-the-loop middleware also already exists as our **confirm-before-mutate gate** plus the **PR + CI gate** for changes to the brain. So the conclusion is not "adopt deep agents" wholesale. It is: close the one gap, and start using the one pattern we have the primitives for but rarely exploit.

The technical architecture doc names both weaknesses itself: "no owned durable engine ... the clearest candidate for convergence," and specialists that run synchronously, one data-in-analysis-out pass at a time.

---

## 3. Recommendations

Four, ordered by impact-to-effort. All are buildable with primitives already in the harness (the `TaskCreate` / `TaskUpdate` task list, the `Workflow` tool's `pipeline` / `parallel` / `agent` calls, `Agent` with `run_in_background`, and the session scratchpad), so none requires new infrastructure.

### 3.1 Add a planning-tool discipline to the long-horizon skills (highest impact, lowest cost)

The one missing pillar. For any skill whose run is genuinely multi-step, require an explicit plan before execution and track it to completion, the same way this very research task should.

- **Where:** the router `/marketing-brain` first, then `/chief-of-staff`, `/campaign-agent`, `/pr-doctor`, and the heavier reports (`/win-loss-pricing-analyzer`, `/organic-dashboard`). Short skills (a single Slack answer, one lookup) should **not** get this; a plan for a one-step task is overhead.
- **How:** interactive runs use the harness task list (`TaskCreate` / `TaskUpdate`, `in_progress` / `completed`). Unattended routines, which cannot rely on in-memory state across firings, write a plan file to the scratchpad or, where it should survive the run, a committed ledger next to the existing per-skill tracking.md pattern. This extends the durability-at-the-edges model already documented, rather than inventing a new one.
- **Why it pays:** the classify-then-delegate router loses the plan the moment context compacts on a long investigation. An explicit, revisable to-do list is exactly what keeps a deep agent coherent across dozens of steps, and it makes a run auditable after the fact.

### 3.2 Parallelise sub-agent fan-out for the orchestration and reporting skills

Our specialists run one at a time. Several skills fan out to **independent** sub-tasks that have no reason to be sequential.

- **Where:** `/chief-of-staff` builds a 1-1 pack for every direct report plus Abel; those packs are independent and can be built concurrently. `/good-morning` pulls several independent sources. `/marketing-brain` on a broad request often needs several specialists whose passes do not depend on each other. Competitive and research sweeps (see 3.3) fan out per source.
- **How:** the `Workflow` tool expresses this directly (`parallel([...])`, or `pipeline` when a later stage depends on an earlier one), and `Agent` supports `run_in_background` for the same fan-out in an interactive session. This is the deep agent "asynchronous sub-agents" capability, available to us without waiting for a durable engine.
- **Guardrail:** fan-out is for **read and analysis** passes. It does not loosen the confirm-before-mutate gate. Parallel specialists gather; the router still serialises and gates every write. Multi-agent workflows also consume tokens fast, so reserve the `Workflow` tool for cases the user has opted into, per its usage rules.
- **Why it pays:** wall-clock. A chief-of-staff brief that builds six packs in parallel instead of in series is the difference between a brief that is ready when Nir opens his laptop and one that is not.

### 3.3 Stand up a dedicated deep-research skill

Open-ended marketing research, competitive landscape, market sizing, voice-of-customer synthesis across many interviews, is the canonical deep agent task, and we route it ad hoc today. This document is an instance of the need.

- **Shape:** a skill that runs the full loop. Plan the questions (3.1), fan out one research sub-agent per source or sub-question (3.2), have each write its findings to a notes file in the scratchpad rather than back into the main context (the filesystem pillar, keeping the synthesis context lean), then a final synthesis pass under the existing evidence contract (`references/evidence-standards.md`: source plus as-of date, never silently pick a number).
- **Relationship to what exists:** this is `/marketing-brain`'s "investigate" intent made into a first-class, repeatable workflow, reusing the specialist layer as its research sub-agents. It is not a new agent tier.
- **Why it pays:** it turns our best-fit deep agent use case from an improvised sequence into a graded, evidence-clean, repeatable skill, and it is the most direct proof of the pattern's value on our own work.

### 3.4 Make the within-run scratchpad an explicit convention

We do cross-run memory (git) better than the stock pattern. We do not yet have a stated convention for within-run working memory.

- **How:** for any long skill, write large intermediate results (a raw HubSpot export, a full crawl, a long transcript) to the scratchpad and carry a pointer, rather than holding the blob inline across turns. This is the "offload large tool results to the filesystem" middleware, done by convention.
- **Why it pays:** lower cost and less context degradation on exactly the long runs where it matters, and it composes with 3.3, where sub-agents write notes to files the synthesis pass reads.

---

## 4. What not to do

- **Do not import LangChain's Deep Agents harness.** It is a Python framework for building agents from scratch. We do not own our runtime; we ride managed Claude infrastructure and already have the four pillars' primitives natively. Adopt the **patterns**, not the framework.
- **Do not add planning ceremony to short skills.** A tracked plan for a one-step task is pure overhead. The pattern earns its keep only on long-horizon work.
- **Do not let fan-out route around the gate.** Parallelism is a read-and-analyse optimisation. Every mutating action still serialises through confirm-before-mutate, and every change to the brain still ships as a reviewed PR.

---

## 5. One-line summary

The Marketing OS is already a deep agent system missing one pillar (explicit planning) and under-using one pattern (parallel sub-agent fan-out). Close the gap in the long-horizon skills, parallelise the orchestration and reporting skills, and make deep-research a first-class skill, all with primitives we already have.

---

## Sources

- [Deep Agents overview, LangChain docs](https://docs.langchain.com/oss/python/deepagents/overview)
- [Deep Agents: Open Source Agent Harness, LangChain](https://www.langchain.com/deep-agents)
- [LangChain's Deep Agents: A Guide With Demo Project, DataCamp](https://www.datacamp.com/tutorial/deep-agents)
- [Deep Agents Pattern: Planner, Files, Subagents, Particula](https://particula.tech/blog/deep-agents-pattern-planner-filesystem-subagents-architecture)
- [Deep Agent use cases that work in production, 10Clouds](https://10clouds.com/blog/a-i/deep-agent-ai-use-cases-where-deep-agents-actually-deliver-value/)
- Internal: `docs/marketing-os-technical-architecture.md`, `.claude/agents/README.md`, `references/evidence-standards.md`
