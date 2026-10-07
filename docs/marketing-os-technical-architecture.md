# Riverside Marketing OS - Technical Architecture

> **Audience:** the AI architecture review. Written in the register of the ATA v2 (`daemonside`) execution plan and mapped onto what the Marketing OS actually is. Companion to `docs/platform-integration.md` (the full connector/system/ID reference); this document is the architecture argument.

**Thesis.** The Marketing OS is the marketing department's agent platform - a version-controlled context repo plus a two-layer agent stack that turns Claude into an operating partner over Riverside's live systems. It runs the **same one-lifecycle model ATA v2 formalizes** (`identity → policy → load → execute → persist → deliver`), but as the **assistive instantiation**: it rides **managed Claude infrastructure** instead of an owned runtime, keeps **git as the state store**, and uses **PR-review + CI as the governance gate**. In ATA's own terms, the Marketing OS is the documented *PR-per-thread* governance path - running in production today, department-wide.

**Scale:** 30+ skills · 29 specialist subagents · 17 MCP connectors · 11 systems mapped · 5 cloud routines · org = Riverside Marketing.

---

## 01 · North star - one loop; nothing bypasses the gate

Every request - a morning brief, a paid-spend investigation, a task write, a scheduled routine - runs the same loop. The brain, the session, and the permission chain are facets of it, not features.

```text
identity → policy → load → execute → persist → deliver
operator+   classify  map +   skill-  gated     decision
connectors  + scope   docs    agent+  write/PR  + evidence
                              specialist
```

- **Invariant - gate before mutate.** No write to a live system (HubSpot, monday, Slack, ad platforms) and no change to the brain reaches a durable state without a gate: a human confirmation at run time, or - for the brain - a reviewed pull request. The only exception is a named automation skill carrying an explicit unattended-write grant (§10).
- **Invariant - Rivermind first.** Every data question resolves against the analytics team's validated Q&A layer (`/rivermind:ask`) before any direct Omni/Snowflake/Mixpanel query; a direct fallback is allowed only when Rivermind lacks coverage, and the gap is reported.

---

## 02 · Terms this document reuses

| Term | Meaning | ATA analog |
|------|---------|-----------|
| the brain | the `marketing-brain` git repo - context + agents + automation | the *store* (but files, not Mongo) |
| skill-agent | routing-layer agent that owns live MCP access + Riverside IDs; runs on the session main-loop model | Managers |
| specialist | deep-domain subagent, no live access; runs on Sonnet; data in, analysis out | sub-run, chain-narrowed |
| connector | an MCP server to a live platform - the swappable I/O boundary | ResourceAccess port + driver |
| canonical | merged to `main` - permanent, reviewed knowledge | canonical |
| uncertain | a captured-but-unmerged learning - a `/retro` draft in an open PR | uncertain memory, pre-gate |
| the gate | PR review + `team-context-lint` CI | ApprovalEngine, PR-shaped |
| progressive disclosure | load the map first; pull depth only when the task needs it | retrieval discipline (no vector store) |
| narrowing | access only shrinks down the chain (operator → skill-agent → specialist) | permission-narrowing |
| routine | a skill graduated to a schedule - unattended, idempotent | the autonomous end of the arc |

---

## 03 · Architecture - two planes over one brain, on infra we don't own

Like ATA, the system serves two caller classes over one shared brain. Unlike ATA, the runtime beneath is **managed Claude infrastructure** (Claude Code, claude.ai/Cowork, Claude-in-Chrome) - not a bespoke daemonside runtime. We own the brain and the agent logic; Anthropic owns the execution plane.

| Plane | What it is | Medium |
|-------|-----------|--------|
| **Entry surfaces** (callers) | Where a marketer or a schedule enters | Claude Code (first-class) · Cowork · Claude-in-Chrome |
| **The brain** (context) | Always-loaded map + on-demand depth | git - `CLAUDE.md`, `references/`, `systems/`, skill `knowledge/` |
| **The agents** (execution core) | Router + skill-agents, then specialists | Main-loop routing layer → Sonnet specialist layer |
| **Live systems** (integration) | Every platform, reached only via MCP | 17 MCP connectors, read / gated write |

**Why this shape.** Tool-selection accuracy collapses past ~10-15 visible tools; the brain is far past that (30+ skills, hundreds of MCP tools). So the architecture is a stack of narrowing filters - progressive disclosure, semantic routing tables, planning-based delegation, gating - not a flat catalog. Same "one core, thin adapters" principle as ATA-001, expressed as layers of a prompt-and-repo system rather than services.

---

## 04 · The core - organized by rate-of-change; vendors behind connectors

The core is layered by what changes and how often - the same instinct as ATA's IDesign split. The most-likely-to-change part, the live vendor, is the most deeply isolated: behind an MCP connector.

| Layer | Holds | Model / medium | ATA analog |
|-------|-------|----------------|-----------|
| Context | Identity, routing tables, system maps, IDs, conventions | git · progressive disclosure | the store (docs) |
| Routing (skill-agents) | Classify, load, delegate, pull live data, synthesize, gate writes | Session main-loop model · inline | Managers |
| Specialist | Pure domain reasoning, no I/O | Sonnet 5 · `model: sonnet` | Engines / sub-runs |
| Connectors | Every live system as a stable tool contract - the swap boundary | MCP servers | ResourceAccess ports + drivers |

**The swap seam.** MCP is our port/driver seam. The routing layer depends on a connector's *tool contract*, not its vendor: Windsor.ai fronts Google/Meta/LinkedIn/Bing/GA4/Search-Console behind one interface; Omni + Snowflake are two drivers over the same "query the warehouse" intent; a Webflow write falls back from API to Claude-in-Chrome when the API can't express it. The agent logic never learns which driver answered.

---

## 05 · The state store - git is the brain

ATA's north star names what git really provided - *gate, versions, attribution, browsability* - and moves state off git while preserving those as platform properties. The Marketing OS makes the opposite, deliberate bet for the assistive tier: **keep git**, because those four properties come for free and the brain is human-readable prose, not high-write agent memory.

| Kind | Path | Role | Lifecycle |
|------|------|------|-----------|
| map | `CLAUDE.md` | Always-loaded identity, routing tables, directives, pointers | PR-gated |
| reference | `references/**` | Stable lookup: team, boards, Slack IDs, design system, messaging | PR-gated |
| system | `systems/owned·reference/**` | Architecture maps of what we own / depend on | PR-gated · `last-reviewed` stamp |
| skill | `.claude/skills/*/SKILL.md` | Router, skill-agents, workflows, routines - the def + behavior | PR-gated · lint-enforced frontmatter |
| knowledge | `.claude/skills/*/knowledge · tracking · config` | Heavy reference + routine ledgers, loaded mid-run | PR-gated · ledgers auto-committed |
| persona | `.claude/agents/**` | Specialist definitions + shared Riverside context block | PR-gated |

**Versioning, attribution, as-of - for free.** Every change is an immutable commit; `main` is the current pointer; a revert is a new commit, never a mutation; `git blame` is the attribution spine; any past state is an as-of checkout. Browsability is the GitHub UI plus an auto-synced wiki and a `graphify` knowledge graph. These are exactly ATA's four preserved properties - here they are the substrate, not something re-implemented.

**A record, concretely** - a skill def is frontmatter + body:

```markdown
# .claude/skills/nir-mql-live-report/SKILL.md
---
name: nir-mql-live-report
description: Daily DM of new high-quality inbound demo-booked MQLs…
user-invocable: true
---
# body: the contract - inputs, MCP calls (HubSpot search), the dedupe
# ledger (tracking.md, committed), the Slack output schema, and the
# unattended-write grant that exempts it from the run-time gate.
```

**Δ vs ATA - state storage.** ATA migrates git → Mongo Atlas + S3 behind ResourceAccess ports (ADR-002), because agent memory is high-write, multi-tenant, and needs vector retrieval. The Marketing OS brain is low-write human prose read by one org; git's gate/versions/attribution/browsability suffice and are free. **We are, by design, the git-driver stage ATA keeps as its S1 read-path and cutover fallback** - running in production, not as a migration waypoint.

---

## 06 · Retrieval - progressive disclosure + a knowledge graph, not a vector store

ATA retrieves with Titan-v2 embeddings and an Atlas vector index that RBAC-prefilters before ranking. The Marketing OS has no vector store; retrieval is **structural**: a session loads the map, then pulls only the files the task names.

```text
ALWAYS  CLAUDE.md map
  → ON DEMAND  systems/ · references/
    → ON TRIGGER  skills/ · agents/
      → DEEP  skills/*/knowledge/
```

The `graphify` layer indexes the whole repo into a queryable knowledge graph (god nodes, community structure) that regenerates on every merge at zero API cost - the analog of ATA's embed-at-write. It answers scoped subgraph queries instead of loading the whole repo.

**The RBAC-prefilter analog.** ATA's rule - restricted content never enters the candidate set - has a structural echo here: private surfaces gate at the source. A non-member operator reading `#growth-marketing-leaders` gets `channel_not_found`, so restricted context is *unreachable, not merely unranked*. The boundary is the connector's own auth, not a post-hoc scrub.

---

## 07 · The integration plane - MCP is the default door to live state

Nearly every live system is reached through an MCP connector - the direct analog of ATA's "MCP is the agent's only door" (ADR-001/011). Auth is the operator's own connector grant; a connector the operator can't authenticate simply isn't reachable that session. Two approved non-MCP exceptions exist, both where the MCP surface can't express the action and both kept under the same gate: **Webflow locale publishing** runs through Claude-in-Chrome (browser-driven, on the operator's own authenticated Webflow session, gated like any website write - an exception narrowed but not closed by Webflow MCP 2.0 in July 2026, which dropped the Designer-session requirement for most operations yet still has no queue-for-next-publish action), and **GitHub** is reached via `gh`/`git` (token/OAuth, with every write still landing as a PR through the CI + review gate).

| Connector | Auth | Posture | Primary consumers |
|-----------|------|---------|-------------------|
| HubSpot | OAuth | read + gated write | hubspot · lifecycle · ops-automation · preop · nir-mql · workflow-qa |
| Omni BI | connector | read | data · measurement · gong-explorer |
| Snowflake | connector | read · no write SQL | data · Rivermind |
| Mixpanel | connector | read | data |
| Windsor.ai | connector | read | data · paid-acquisition · measurement |
| monday.com | OAuth | read + gated write | monday · pm-story · standups · chief-of-staff · data-team-request + more |
| Slack | connector | read + gated write | slack + nearly every workflow & routine |
| Gmail · Calendar · Drive | OAuth | read + write | invoice-inbox · p1-p2-followup · chief-of-staff · reporting |
| Granola · Notion | connector | read | chief-of-staff · operating-model context |
| Webflow · Figma | connector | read + write | website · seo · design-system |
| GitHub · Claude Code Remote | token / session | write · PRs · triggers; deterministic CI sync | agent-builder · retro · routines · PR-watch · wiki/graph sync |

Windsor.ai is itself a fan-out driver - one connector fronting Google Ads, Meta, LinkedIn, Bing, GA4, and Search Console. Paid channels, GA4, Ahrefs, Stripe/Segment, Hightouch, ChiliPiper, n8n and RevenueCat are reached indirectly (via Windsor, Snowflake/Omni, or as documented pointers), never as first-class connectors.

**Δ vs ATA - the plane.** ATA runs one hosted `daemonside-mcp` endpoint with double-auth (human bounds which agents; agent key bounds permissions) and its own store behind it. The Marketing OS consumes *many* third-party MCP endpoints and holds no store behind them - the "core" is the repo + prompt, and identity is the operator's own connector auth rather than a minted per-agent scoped key.

---

## 08 · Sessions & durable execution - managed sessions; schedules for durability

A session is a Claude Code / Cowork conversation on managed infrastructure. We don't own a Temporal-style durable engine; durability across time comes from **scheduled cloud routines** and **triggers** (the Claude Code Remote MCP: `send_later`, `create_trigger`), and from state committed back to the repo.

**The turn** - load the map, never run blind: `load → classify → delegate → gate → deliver → capture (/retro if novel)`.

**Durability & idempotency for unattended runs.** A routine can't rely on in-memory state across firings, so each carries an explicit idempotency mechanism: a per-skill tracking.md dedupe ledger committed back to git (access-welcome, nir-mql, invoice-inbox), or in-target markers (p1-p2-followup writes a calendar-event marker keyed by item + ISO week). Re-running never double-acts - the ledger is the durable memory a managed session lacks.

**Δ vs ATA - sessions.** ATA models a thread as a durable Temporal workflow-per-thread with a re-read-to-confirm invariant and idle-TTL. The Marketing OS has no owned durable engine; a managed session is ephemeral, and durability is reconstructed at the edges - schedules for time, committed ledgers for state. The "never silent-fresh" guarantee is weaker here, and is the clearest candidate for convergence onto a daemonside session engine.

---

## 09 · Access & identity - narrowing by construction

Effective access narrows down the chain, never grows - the same law as ATA's permission-narrowing. Here it is enforced **structurally**: the specialist layer is defined without live-system tools, so a deep pass physically cannot call HubSpot, monday, or Slack.

```text
operator (own connector grants) ⊇ skill-agent (live access + IDs) ⊇ specialist (no live access)
```

| Level | Bounds | Mechanism |
|-------|--------|-----------|
| Operator | Which systems are reachable at all this session | The operator's own OAuth/connector grants - a private Slack channel is `channel_not_found` for non-members |
| Skill-agent | Which live systems + IDs a domain may touch; read vs gated-write | Declared in the SKILL.md contract; writes pause for confirmation |
| Specialist | Reasoning only - no I/O | Agent def carries a restricted toolset; no live-system tools in scope |

**Invariant - the safety gate.** Never mutate HubSpot, monday, Slack, ad platforms, or production workflows without user confirmation. Draft outbound content before sending. Create tasks via `/pm-story`, never a raw board write. The one carve-out is a named automation skill (a cloud routine) that carries an explicit unattended-write grant in its contract - the assistive→autonomous graduation, made per-skill and reviewable.

**Δ vs ATA - identity.** ATA derives a canonical OKTA subject at every hop, mints per-agent scoped keys, and enforces a seven-capability RBAC grant (a-g) with secrets-by-tier. The Marketing OS has no per-agent key or capability matrix; identity is the operator's connector auth, and narrowing is enforced by *construction* (specialists lack tools) plus the run-time gate - coarser, but the same "can only subtract" law.

---

## 10 · Governance - the gate is PR review + CI + merge-sync

One gate governs every change to the brain. A learning is captured as *uncertain* (a `/retro` draft), routed to the right file, and reaches *canonical* only through a reviewed pull request - the human gate - with CI enforcing structure. This is precisely what ATA calls the PR-per-thread flow it keeps as a cutover fallback; for the assistive tier it is the primary, sufficient mechanism.

```text
run (a task teaches something) → uncertain (/retro routes it) → gate (PR review + lint) → canonical (merge) → sync (wiki + graph)
```

| Job | Trigger | Enforces |
|-----|---------|----------|
| `team-context-lint` | PR touching brain files | Skill frontmatter present; no unfilled placeholder tokens; no binaries in root |
| deterministic wiki sync | merge to `main` | Regenerates the browsable wiki mirror from repository source |
| graphify · graph refresh | merge to `main` | Incremental code/document structure re-index + rebuilds the explorer |

**Merge-sync security model - no code from data, least privilege.** Wiki and graph extraction are deterministic and run with `contents: read`, without model credentials. Separate commit jobs hold the only write tokens; checkouts use `persist-credentials: false`; PR titles are commit-message data, never shell code; source coverage is validated before replacement; and the graph commit rejects any patch outside `graphify-out/`. This is the Marketing OS's version of ATA's execution-plane hardening - applied to CI rather than a gVisor sandbox.

---

## 11 · Orchestration - classify, delegate, synthesize, close the loop

Every request is classified into one of seven intents: **brief · triage · investigate · plan · execute · measure · learn**. Every sub-agent result is normalized before it reaches the user; every loop ends in a decision and, when something was learned, a `/retro`.

| Concern | Contract |
|---------|----------|
| Model policy | Planning + judgment on the **session main-loop model** (router + skill-agents, inline); execution on **Sonnet 5** (specialists, pinned). Escalate back up when a pass turns out to need judgment. |
| Delegation contract | Every result normalizes to: Intent · Context loaded · Evidence · Recommendation · Owner · Operating state · Approval needed · Risks/gaps. |
| Operating state | intake → triaged → planned → executing → (blocked) → ready-for-review → shipped → measured → learned; investigating branch when evidence is needed. |
| State ownership | monday = work state · Slack = discussion/outbound · HubSpot + Omni = funnel/attribution evidence · the repo = durable knowledge. |

**The autonomy arc - assistive → autonomous.** A workflow is proven with a human at the keyboard, then graduated to a schedule. Five routines run unattended today (access-welcome, nir-mql-live-report, invoice-inbox-to-monday, p1-p2-followup, mops-backlog-review), each carrying an explicit unattended-write grant and an idempotency ledger. Same arc ATA formalizes - on managed Claude schedules instead of an owned runtime.

---

## 12 · Δ vs ATA - the mapping and the convergence path

| ATA v2 concept | Marketing OS today | Delta / convergence |
|----------------|--------------------|--------------------|
| State store - Mongo Atlas + S3 behind ports | git repo (files) | We are ATA's git-driver stage, in prod. Converge: import brains as canonical v1 records. |
| Versions / attribution / as-of | git history · blame · checkout | Same four properties ATA preserves - here native, not re-built. |
| ApprovalEngine + Slack `#brain-changes` | PR review + CI lint | This *is* ATA's PR-per-thread fallback. Converge: move to the store-native gate. |
| Sessions - Temporal workflow-per-thread | managed session + schedules | No owned durable engine; durability via routines + committed ledgers. Clearest convergence target. |
| Retrieval - Titan v2 + Atlas vector, RBAC-prefilter | progressive disclosure + graphify graph | Structural, not vector. Restricted content gated at the connector source. |
| RBAC caps a-g · per-agent scoped keys | operator auth + structural narrowing + gate | Coarser; same "only subtract" law. Converge: register agents, adopt caps. |
| MCP - one hosted door, double-auth | many third-party MCP connectors | We consume MCP, don't host it. Converge: a skill-agent becomes a registered daemonside agent. |
| Sandbox / gVisor / egress allowlist | managed Claude infra + agent proxy | Execution plane is Anthropic-owned; CI hardening is our owned-surface analog. |
| Multi-org · `org_id` on every record | single org (marketing dept) | Cross-team boundaries via separate workspaces. Converge: seed as an org tenant. |
| Autonomy - assistive → autonomous | 5 scheduled cloud routines | Same arc, running now on managed schedules. |

**The one-line thesis.** The Marketing OS validates the ATA thesis from the demand side: it proves the one-lifecycle model, the two-layer agent split, permission-narrowing, and the assistive→autonomous arc are correct - using git + PR + managed Claude infra. When daemonside v2 lands, the Marketing OS is a ready-made `org-1` tenant whose defs, skills, and PR-gated knowledge map directly onto the store's kinds and the store-native gate.

---

## 13 · Appendix - source map

| Concern | Path |
|---------|------|
| Always-loaded map + directives | `CLAUDE.md` |
| Full integration + system-design reference | `docs/platform-integration.md` |
| Owned / reference system maps | `systems/owned/**` · `systems/reference/**` |
| Router, skill-agents, workflows, routines | `.claude/skills/*/SKILL.md` |
| Specialist layer + shared context + registry | `.claude/agents/**` · `.claude/agents/RIVERSIDE_CONTEXT.md` · `README.md` |
| Two-layer model + model policy | `.claude/agents/README.md` · `.claude/skills/marketing-os/SKILL.md` |
| Governance CI + merge-sync security | `.github/workflows/**` · `docs/wiki-sync-automation.md` |
| Knowledge graph (generated) | `graphify-out/` |

*Written in the register of the ATA v2 execution plan for the architecture review. The repo is the source of truth.*
