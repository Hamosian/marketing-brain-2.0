<!-- last-reviewed: 2026-07-25 -->
# Agents directory

This directory holds the **specialist subagent layer** of the Riverside Marketing OS. These are deep-dive personas invoked via the Agent tool. They sit beneath the **routing layer** of skill-agents in `.claude/skills/` (`marketing-os` and the `*-agent` skills).

## The two-layer model

| Layer | Where | Owns | Riverside context | Model |
|-------|-------|------|-------------------|-------|
| Routing layer | `.claude/skills/marketing-os`, `.claude/skills/*-agent` | Live system access (HubSpot, Omni, monday, Slack, ad platforms), Riverside IDs, orchestration, brand enforcement | Native | The session's main-loop model - runs inline; owns planning |
| Specialist layer | `.claude/agents/` (this dir) | Deep domain expertise and frameworks | Carried via the embedded Riverside context block; no live system access | Sonnet 5 (`claude-sonnet-5`) - pinned via `model: sonnet` frontmatter; owns execution |

**Flow:** a request enters through `/marketing-os` or a skill-agent. The skill-agent pulls the live Riverside data and frames the PLG/SLG context, then invokes the relevant specialist subagent here for the deep pass, then synthesizes and surfaces any mutating action for confirmation. Specialists do not call live systems directly and do not act as the router.

## Tool scoping (enforced)

"No live system access" is a capability boundary, not a convention. A subagent with no `tools:` line inherits **every** tool in the session - which includes `mcp__HubSpot__manage_crm_objects`, `mcp__Slack__slack_send_message`, `mcp__monday_com__create_item`, Webflow publish, and `mcp__Windsor_ai__execute_action` (pauses campaigns, sets budgets). That routes around the confirm-before-mutating gate that lives in the routing layer, so every file here declares its grant explicitly.

The standard grant is read-and-author only:

```yaml
tools: Read, Write, Edit, Glob, Grep, WebFetch, WebSearch
```

`Glob` and `Grep` are part of the default because the context block instructs every specialist to ground itself in `CLAUDE.md`, `systems/`, and `references/` - it cannot do that with `Read` alone.

`Bash` is earned, not inherited. Exactly one subagent holds it - `Carousel Growth Engine`, whose core workflow drives a browser and its own publish/analytics scripts. It is enumerated in `BASH_ALLOWED` in `scripts/lint_agents.py`; adding `Bash` anywhere else fails the lint until the file is listed with a reason.

The `paid-media/*` set carried `Bash` from its upstream personas, justified by a live-API extraction workflow. That workflow contradicted the no-live-access boundary and has been removed from those files - they now analyse the snapshot `/paid-acquisition-agent` hands them - so the grant went with it. If a specialist seems to need `Bash`, check first whether it actually needs data the owning skill-agent should be passing in.

`scripts/lint_agents.py` runs in CI on every PR touching this directory and enforces:

- frontmatter carries `name`, `description`, `model`, `tools`, and `last-reviewed`
- `tools:` grants nothing outside the allowed set, and `Bash` only where earned
- `model:` is pinned to `sonnet` unless listed in `MODEL_EXCEPTIONS` with a reason, and an escalation must still name a real tier
- `last-reviewed:` is present and is a valid `YYYY-MM-DD` date
- the harmonization markers are present
- the registry table below and the files on disk agree **in both directions**

That last check matters because routing is by display name (`PR & Communications Manager`), which matches neither the filename nor a slug. Renaming a file or a `name:` field used to break six routing tables silently; now it fails the build.

Run it locally with `python3 scripts/lint_agents.py`.

**Model policy:** planning stays on the session's main-loop model (the routing layer, inline); execution runs on Sonnet 5 (the specialist layer, pinned via `model: sonnet`).

Three specialists are escalated off the Sonnet default via `MODEL_EXCEPTIONS`, because their passes weigh trade-offs and build a case rather than executing a mechanical checklist: `Paid Media Auditor` (200+ checkpoints, ranked and justified across a whole account), `Tracking & Measurement Specialist` (attribution architecture, where a wrong call is expensive and quiet), and `Conversion Psychology Specialist` (diagnostic reasoning over behavioural models). Each carries its reason in the lint. Add to that list sparingly - the default exists because most specialist work is execution.

The routing layer is described by role rather than by version. A version pinned in prose goes stale on the next model upgrade and then silently misdescribes the system, which is what happened here: these docs claimed Opus 4.8 well past the point where that was true. Full rationale in the Model Selection section of `.claude/skills/marketing-os/SKILL.md`.

Wiki synchronization is deterministic CI in `scripts/sync_wiki.py`, not an agent in this directory.

## Riverside context block

Every Riverside-aware subagent carries a concise `## Riverside context` block near the top, delimited by `<!-- riverside-harmonized -->` and `<!-- /riverside-harmonized -->`, followed by a per-agent `## How this fits Riverside Marketing` section.

The canonical copy of the embedded block lives in `RIVERSIDE_CONTEXT.md`, between `<!-- embedded-block:start -->` and `<!-- embedded-block:end -->`. **Edit it there, never in the subagents**, then run the harmonizer:

```bash
python3 scripts/harmonize_agents.py          # push the canonical blocks into every subagent
python3 scripts/harmonize_agents.py --check  # verify only (runs in CI)
```

The harmonizer replaces only the delimited block. The `## How this fits Riverside Marketing` section is intentionally different in every file and is preserved on every run. `--check` runs in CI, so a hand-edited copy fails the build instead of drifting unnoticed.

Two blocks are managed this way, both required on every subagent:

| Block | Canonical source | Markers in subagents |
|-------|------------------|----------------------|
| Riverside context | `RIVERSIDE_CONTEXT.md` | `<!-- riverside-harmonized -->` … `<!-- /riverside-harmonized -->` |
| Output contract | `OUTPUT_CONTRACT.md` | `<!-- output-contract -->` … `<!-- /output-contract -->` |

Convention for both canonical sources: the delimited region **opens** with the in-agent start marker but omits the closing one, which the harmonizer writes itself. A missing block is appended as a trailing section; a present one is replaced in place.

## Output contract

Specialist replies are consumed by a skill-agent that synthesizes across several of them, so the layer returns one fixed shape: `## Summary`, `## Findings`, `## Recommendations`, `## Open questions`, `## Not verified`. Headings are mandatory even when empty (`None.` rather than a dropped section), claims must name their evidence, and anything ungrounded goes under `## Not verified` instead of becoming a plausible-looking number.

This is `references/agent-prompting.md` block 5 ("Schema the output") applied to the specialist layer. Several subagents already had a "Technical Deliverables" or "Your Deliverable Template" section - those describe artifacts written to disk, not the reply, and both coexist: keep producing the artifacts, use the contract for the return value.

Full rationale and the canonical text: `OUTPUT_CONTRACT.md`.

## Grounding sources

The context block points every specialist at the reference layer rather than at generic best practice, split three ways:

| Layer | Source | Covers |
|-------|--------|--------|
| Verbal | `references/messaging/` | Positioning, approved phrasing, the 2026 brand story, voice-of-customer evidence (90+ community members, 70+ power-user interviews) |
| Factual | `references/product/` | Feature behavior, plan gating, the AI feature matrix, glossary |
| Visual | `references/design-system/` + `/riverside-brand-guidelines` | Tokens, components, brand assets |

Pricing, plan names, and beta availability are verify-before-publish - `references/product/README.md` explains why. And because specialists hold no live data access, they are told not to invent metrics: numbers arrive from the invoking skill-agent (Rivermind-first per `CLAUDE.md`) or go under `## Not verified`.

## Registry: which skill-agent owns which specialists

| Skill-agent (router) | Specialist subagents it invokes |
|----------------------|----------------------------------|
| `/paid-acquisition-agent` | `Paid Media Auditor`, `PPC Campaign Strategist`, `Paid Social Strategist`, `Programmatic & Display Buyer`, `Search Query Analyst`, `Ad Creative Strategist`, `Tracking & Measurement Specialist`, `Conversion Psychology Specialist` |
| `/seo-ai-search-agent` | `SEO Specialist`, `AEO Foundations Architect`, `Agentic Search Optimizer`, `AI Citation Strategist` |
| `/content-agent` | `Content Creator`, `LinkedIn Content Creator`, `TikTok Strategist`, `Instagram Curator`, `Twitter Engager`, `X/Twitter Intelligence Analyst`, `Social Media Strategist`, `Carousel Growth Engine`, `Video Optimization Specialist`, `Global Podcast Strategist`, `PR & Communications Manager`, `Brand & Design Director`, `Creator Marketing Strategist` |
| `/seo-ai-search-agent`, `/website-agent` | `Localization & International Growth Strategist` (multi-locale organic + on-page) |
| `/lifecycle-agent` | `Email Marketing Strategist` |
| `/campaign-agent` | social specialists, `Global Podcast Strategist`, `PR & Communications Manager`, `Paid Social Strategist`, `Creator Marketing Strategist`, `Growth Hacker` (for launches) |
| `/marketing-os`, `/measurement-agent`, `/data-agent` | `Growth Hacker` (experiments) |
| `/marketing-os` | `App Store Optimizer` (as-needed; Riverside ships iOS/Android apps; no standing ASO program) |

## Archived personas

Three stock subagents that did not map to how Riverside Marketing operates - `Book Co-Author`, `Short-Video Editing Coach`, `Reddit Community Builder` - were retired on 2026-07-25 and moved to `docs/archive/agents/`, which is outside the `.claude/agents/**` discovery path. Nothing routes to them and they no longer appear in the agent picker. See `docs/archive/agents/README.md` for the reasoning and for how to restore one.

They are **not** in an `archive/` subfolder here on purpose: this directory is scanned recursively, so a nested folder would still load and still be selectable - which is exactly what archiving is meant to prevent.

As a result `HARMONIZE_EXEMPT` and `REGISTRY_EXEMPT` in `scripts/lint_agents.py` are both empty. Every subagent that loads is held to the full bar: both harmonized blocks, a registry entry, and an explicit tool grant. Prefer archiving a persona over exempting it in place.

## Maintenance

New specialist subagent - five steps, the last two enforced by CI:

1. Write the persona file under `marketing/` or `paid-media/`.
2. Set frontmatter: `model: sonnet` (execution-layer default) and `tools: Read, Write, Edit, Glob, Grep, WebFetch, WebSearch`.
3. Run `python3 scripts/harmonize_agents.py` - it inserts both managed blocks (Riverside context, output contract). Move the context block up near the top afterwards if it landed at the end; the harmonizer only guarantees presence, not position.
4. Add it to the registry table above **and** to the owning skill-agent's "Specialist subagents" section, using the exact `name:` from the frontmatter.
5. Run `python3 scripts/lint_agents.py` before opening the PR.

Other conventions:

- Keep specialists generic in their domain craft; keep Riverside-specific IDs, accounts, and live data in the skill-agents and `systems/` and `references/`.
- Never add a live-system MCP tool to a specialist. If a specialist needs live data, the owning skill-agent should pull it and pass it in - that is the whole point of the two-layer split.
- Keep the prose and the tool grant honest with each other. A narrowed `tools:` line does not fix a persona whose body still instructs it to pull live data or deploy changes - that just leaves the agent holding contradictory instructions. When you scope a subagent, read its workflow sections and rewrite whatever the new grant makes impossible.
- Keep `last-reviewed:` current when you make a substantive edit. It is a frontmatter key here rather than the first-line `<!-- last-reviewed -->` comment used in `systems/` and `references/`, because line 1 must be the frontmatter delimiter. `/health-check` ages this layer off that field; the lint only validates the date format, so nothing fails a build merely for being old.

## Provenance

The eight `paid-media/*` subagents carry an `author:` field crediting their upstream author (`John Williams (@itallstartedwithaidea)`), and several `marketing/*` files began as stock personas. Those fields are **kept deliberately** - they are accurate provenance, and stripping upstream credit to make frontmatter look uniform would be the wrong trade.

What Riverside layers on top is the harmonized context block, the output contract, tool scoping, and the per-agent `## How this fits Riverside Marketing` section. When adding a subagent adapted from someone else's work, keep their `author:` line and add our context through those blocks rather than by rewriting the credit.
