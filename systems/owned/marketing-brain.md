<!-- last-reviewed: 2026-09-28 -->
# Marketing Brain (Team Context + Marketing OS)

> This repo. The team's AI-first knowledge base plus the Marketing OS agent layer that runs on top of it. Turns Claude from an isolated tool into an operating partner that knows our systems, boards, channels, conventions, and workflows.

## Overview

The Marketing Brain is the system this repo *is*: a version-controlled context base structured for progressive disclosure, a registry of skills and sub-agents that act on that context, and the automation that keeps it healthy. `CLAUDE.md` is always loaded and acts as the map; everything else loads on demand when a task needs it. The Marketing OS (`/marketing-brain`) is the top-level agent that classifies a request, loads the right context, delegates to specialist sub-agents, synthesizes a recommendation, and closes the loop. We own and maintain this system end to end.

The philosophy behind it (pointers not copies, let the AI interview you, force the AI to update itself, treat the AI as a UI, keep it clean) lives in `PHILOSOPHY.md`.

## How Claude Works With This

| Action | How |
|--------|-----|
| Run broad / cross-system work | `/marketing-brain` routes to sub-agents, tracks operating state, closes the loop |
| Add or change knowledge | Edit the relevant file (`systems/`, `references/`, `CLAUDE.md`, or a skill), open a PR |
| Capture a learning | `/retro` writes the durable learning to the right file and opens a PR |
| Extract knowledge from a person | `/curious-intern` interviews the user and commits the result |
| Check the brain's health | `/health-check` finds stale docs, unfilled placeholders, and template drift |
| See what the brain can do | `/list-skills` reads the skills directory live |
| Deploy | Merge to `main`. No build. CI lint runs on PR; deterministic wiki and graph synchronization runs on merge |

## Repos / Data Sources

| Repo / location | What it contains |
|------|-----------------|
| This repo (`marketing-brain`) | The whole system: `CLAUDE.md`, `systems/`, `references/`, `.claude/skills/`, `.claude/agents/`, `docs/`, CI workflows |
| GitHub Wiki | Generated, browsable mirror of the repo, kept in sync by deterministic automation on every merge. The repo is the source of truth, the wiki is read-only output |

## Architecture

```text
CLAUDE.md (always loaded - the map)
  |
  +-- marketing-brain         top-level router for broad / cross-system work
  +-- references/          on demand - stable lookup data: IDs, contacts, boards
  +-- systems/             on demand - architecture maps (owned/ and reference/)
  +-- .claude/skills/      on trigger - routing-layer sub-agents and workflows
  |     +-- knowledge/     on demand within a skill - heavy reference content
  +-- .claude/agents/      specialist subagent layer (see its README)
  +-- .github/workflows/   CI lint + wiki sync automation
```

Three layers:

1. **Context** (passive): `CLAUDE.md`, `references/`, `systems/`. Loaded progressively so a session starts instant and only pulls what the task needs.
2. **Agents** (active), itself two layers that work together:
   - **Routing layer** - the skills in `.claude/skills/`. `/marketing-brain` is the router; the `*-agent` skills are specialist sub-agents that own live system access and Riverside IDs; the rest are standalone workflows.
   - **Specialist layer** - the deep-dive subagents in `.claude/agents/` (paid media, SEO/AI-search, content/social, email, podcast, PR, growth). They carry a shared Riverside context block (canonical: `.claude/agents/RIVERSIDE_CONTEXT.md`) but have no live system access. A routing-layer skill-agent pulls the live data, then invokes the relevant specialist for the deep pass, then synthesizes. The full router-to-specialist map and the rule for adding new specialists live in `.claude/agents/README.md`.
3. **Automation** (autonomous): CI lint on PR, deterministic wiki sync and incremental Graphify refresh on merge.

The full routing and operating-state diagram is in `docs/marketing-os-diagram.md`.

### Why the layered routing exists (design rationale)

Agent research consistently finds that tool-selection accuracy degrades once an agent sees more than ~10-15 tools at once (context bloat, "lost in the middle"), and that narrowing what the model sees before it decides beats using a bigger model. The brain is already well past that threshold (27+ skills, plus MCP tools), which is why the architecture is a stack of narrowing filters rather than a flat catalog:

| Standard technique | Our implementation |
|--------------------|--------------------|
| Retrieval-based selection (expose only relevant tools per query) | Progressive disclosure: `CLAUDE.md` is the map; `systems/`, `references/`, and skill `knowledge/` load on demand |
| Semantic routing (group tools into toolboxes, route by category) | Task Routing + Sub-Agent Registry tables in `CLAUDE.md`; `/marketing-brain` routes to a domain skill, never a flat list |
| Planning-based selection (decompose, load tools per step) | `/marketing-brain` classifies and delegates; skill-agents pull live data, then invoke specialist subagents for the deep pass |
| Gating (is a tool needed at all?) | Skill trigger descriptions + directives like "Rivermind first for data questions" |
| Fallback logic (confident act / reformulate / escalate) | Rivermind → `/data-agent` fallback with note-the-gap rule; `/list-skills` as catch-all. Only the data path has an explicit chain today |
| Benchmarking (measure routing accuracy) | **Not implemented** - see Known Issues |

Reference: ["The Complete Guide to Tool Selection in AI Agents"](https://machinelearningmastery.com/the-complete-guide-to-tool-selection-in-ai-agents/) (MachineLearningMastery), which matches this design and is where the technique names above come from. Keep this table in mind when adding skills: every new skill must earn its trigger description, or it degrades routing for everything else.

## Key Entry Points

**Operating / daily:**
- `/marketing-brain` - top-level operating brief, routes to the sub-agent registry, closes the loop
- `/good-morning` - daily brief: Monday tasks, team updates, Slack highlights, risks
- `/team-intro` - what the brain knows about the team, systems, and projects

**Maintaining the brain (the flywheel):**
- `/retro` - capture a learning after a novel workflow, route it to the right file, open a PR
- `/curious-intern` - interview-driven knowledge extraction to fill gaps
- `/health-check` - staleness and template-compliance audit
- `/list-skills` - live skill inventory

**Sub-agent registry** (called by `/marketing-brain` or directly): data, measurement, HubSpot, lifecycle, Monday, Slack, content, paid-acquisition, website, SEO/AI-search, marketing-ops-automation, campaign. Plus task intake via `/pm-story`. See the Sub-Agent Registry and Task Routing tables in `CLAUDE.md` for the authoritative list, and `/list-skills` for the live count (27 skills as of last review).

**Knowledge routing** (where a new learning goes) is the table in `CLAUDE.md` under "Knowledge Routing". The rule: team / system knowledge goes in the repo so the whole team benefits; only individual user preferences go to memory.

## Automation

| Workflow | File | Trigger | What it does |
|----------|------|---------|--------------|
| Team Context Lint | `.github/workflows/team-context-lint.yml` | PR touching `systems/`, `references/`, `.claude/skills/`, or `CLAUDE.md` | Fails the PR if a skill lacks `name`/`description` frontmatter, if any unfilled template placeholder remains, or if a binary/packaged file sits in the repo root |
| Wiki + Graph Sync | `.github/workflows/doc-agent-on-merge.yml` | PR merged into `main`, or manual dispatch (skippable with `skip-wiki` / `skip-graph`) | Deterministically mirrors source files to the wiki and incrementally refreshes Graphify code/document structure. No model credential is required; richer model-assisted graph refreshes are optional. Details in `docs/wiki-sync-automation.md` |
| gitleaks pre-commit | `.githooks/pre-commit` | Local commit (opt-in via `git config core.hooksPath .githooks`) | Secret scanning before commit |

## Conventions That Keep It Healthy

- **Pointers, not copies.** Link to dashboards, boards, and live data. Never duplicate them. If content breaks when the platform changes, it belongs in that platform's source of truth, not here.
- **Progressive disclosure.** Keep `CLAUDE.md` lean. System-specific detail (board IDs, dashboard URLs, account IDs) lives in `systems/` or a skill's `knowledge/`.
- **Every system doc** starts with `<!-- last-reviewed: YYYY-MM-DD -->` on line 1 and follows a template in `systems/README.md` (full or light). `/health-check` enforces this.
- **Every skill** has YAML frontmatter with `name` and `description`. CI enforces this.
- **Skill prompts are contracts, not questions.** When writing or reviewing a skill, agent persona, or routine prompt, follow `references/agent-prompting.md` (spec first, layered build-up, explicit constraints with defaults, examples, fixed output schema).
- **The flywheel is non-negotiable.** After a novel workflow, run `/retro` so tribal knowledge becomes shared, reviewable repo content.

## Known Issues / Failure Modes

| Issue | Symptoms | Resolution |
|-------|----------|------------|
| Stale or contradictory docs | Claude answers confidently but wrong; `last-reviewed` dates are old | Run `/health-check`, prune or refresh. A messy brain is worse than none |
| `CLAUDE.md` bloat | Context window wasted on every task | Move detail into `systems/` or skill `knowledge/`; keep the map thin |
| System knowledge saved to memory | Only one person benefits, can't be reviewed | Move it into the repo via PR. Memory is for individual user preferences only |
| Skill rot | Wrong routing, stale actions | Prune dead skills; don't leave them to pollute the registry |
| Routing accuracy unmeasured | No way to know how often a request lands on the wrong skill (e.g. `/pm-story` vs `/data-team-request`, or direct API calls bypassing a skill) | Open gap. Candidate fix: a small labeled set of "request → correct skill" cases run periodically (extend `/health-check` or a standalone check). Until then, report misroutes via `/retro` so trigger descriptions get sharpened |
| Wiki or graph sync fails | Generated views drift from repo | Check the merge workflow and confirm Actions has repository write permission for the commit jobs. The repo remains the source of truth |
| Hosted artifact loses logo/fonts | Published claude.ai artifact shows fallback fonts and a broken or missing logo image while local preview looks fine | The artifact sandbox (CSP) blocks **all** external requests - CDN fonts, Google Fonts, remote images. Inline everything: `@font-face` with a base64 `data:` URI for Instrument Sans, logo as a base64 `data:image/png` (see the Logo section in `riverside-brand-guidelines`) |
| Republished artifact renders blank | After republishing to the same URL, the viewer shows an empty dark frame; easy to misread as a layout bug and "fix" phantom issues | Viewer-side frame cache lag, not a page defect (verified 2026-08-10: four republish cycles chased a phantom). Confirm the file passes static checks, then re-open with a cache-busting query param (`?cb=N`) and wait a few seconds before diagnosing further |
| Local preview pane pins a file URL to cache | After overwriting an HTML file, the Claude Code preview pane keeps serving the old bytes; even renaming and re-navigating can fail | Do not burn time fighting it. Verify the page by static analysis (markup balance, payload reconciliation) plus the published artifact with a cache-buster, or open the file in the user's real Chrome |
| An animated or time-based page cannot be checked in a browser | The built-in browser pane refuses local files ("This tab shows a local file") and is not signed in to claude.ai. In the Claude-in-Chrome tab, the published artifact painted once, then ignored clicks and never repainted, so every screenshot showed the opening frame (2026-09-28) | Make the page seekable: in a local debug copy, read `?t=<seconds>` and jump the timeline there. Render the moments you need with `scripts/web_screenshot.sh` at 1280x720 and look at them tiled. On 2026-09-28 this caught a crash at 1:16 that no viewer showed. For a video, `scripts/capture_frames.py` renders every frame and fails if the page throws. Headless Chrome will not lay out narrower than about 500 px, so a 390 px "phone" shot is a cropped 500 px layout, not a phone check |

## Related Systems

- **Upstream:** the platforms the brain reads and writes through its sub-agents (HubSpot, Omni BI, Monday, Slack, ad platforms, Snowflake, Mixpanel). Each has its own doc in `systems/`.
- **Downstream:** the GitHub Wiki (generated mirror) and every teammate's Claude Code session, which loads `CLAUDE.md` as its operating context.
- **Adjacent:** Agent Flow (`systems/reference/agent-flow.md`), an optional local visualizer for Claude Code sessions. Nothing in the brain depends on it.

## Pointers

- **Investment:** Active. Core operating system for Riverside Growth.
- **Philosophy:** `PHILOSOPHY.md`
- **Architecture diagram:** `docs/marketing-os-diagram.md`, `architecture.html`
- **Activation (new teammates):** `docs/ACTIVATE.md`
- **Adoption playbook:** `docs/QUICKSTART.md`
- **Doc templates:** `systems/README.md`
- **Wiki automation:** `docs/wiki-sync-automation.md`
- **Live skill list:** `/list-skills`
