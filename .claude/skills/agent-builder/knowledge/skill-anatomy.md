# Skill anatomy and the Marketing OS agent taxonomy

Load this when authoring the structure of a new agent. It distils Anthropic's
Agent Skills framework and maps it onto how *this* repo builds agents.

## The three levels of progressive disclosure

A Skill is a directory. Claude loads its content in stages so only what the
task needs occupies the context window.

| Level | What | When loaded | Token cost | Where it lives |
|-------|------|-------------|-----------|----------------|
| 1. Metadata | `name` + `description` (YAML frontmatter) | Always, at startup | ~100 tokens/skill | Top of `SKILL.md` |
| 2. Instructions | The `SKILL.md` body: the workflow | When the skill triggers | Keep under ~5k tokens | `SKILL.md` |
| 3. Resources | Reference docs, templates, data | Only when the body links to them and Claude reads them | 0 until read | `knowledge/`, `references/` |
| 3. Code | Scripts run via bash | Only the *output* enters context, never the code | ~0 | `scripts/` |

**Design rule:** the body of `SKILL.md` is a lean workflow. Anything heavy -
long reference tables, big templates, API detail, per-system config - goes in a
Level-3 file that the body points to. A skill can bundle dozens of reference
files at zero context cost until one is opened. This skill (`agent-builder`) is
itself built this way: a short `SKILL.md`, this `knowledge/` directory, and a
`scripts/validate_skill.py`.

**When to use each Level-3 type:**
- **Instructions** (`.md`) → flexible guidance Claude reads and reasons over.
- **Code** (`.py`, etc.) → deterministic operations. Prefer a script over
  "have Claude do it by hand" whenever the operation is exact and repeatable
  (validation, parsing, formatting). Only the output costs tokens.
- **Resources** → factual lookup: schemas, ID tables, templates, examples.

## Frontmatter rules (hard requirements)

Every `SKILL.md` starts with YAML frontmatter. Two fields are required.

```yaml
---
name: your-skill-name
description: What it does AND when to use it, with trigger phrases.
---
```

`name`
- max 64 characters
- lowercase letters, numbers, hyphens only
- no reserved words: `anthropic`, `claude`
- no XML tags

`description`
- non-empty, max 1024 characters
- no XML tags
- **must say both what the skill does and when to use it.** This is the only
  text Claude matches a request against to decide whether to trigger the skill.
  A description that only says what it does will not fire reliably. Include the
  concrete trigger phrases users will actually type (see how the existing
  skills phrase `Triggered by "..."` / `Use when ...`).
- either a single inline value on one line (`description: <text>`) or a YAML
  folded/literal block scalar (`description: >-` with the text on indented
  lines below) - both the CI lint and `scripts/validate_skill.py` accept both forms
  (the validator folds `>` blocks into one string for the length/quality
  checks). Prefer inline for new skills - it's what most of the repo uses -
  but a block scalar is valid; many existing skills use `>-`.

Optional field this repo sets on operating/builder skills:
`user-invocable: true` - controls whether the skill shows in the `/` menu, where
it is callable as `/<directory-name>` (the command name comes from the skill's
directory, not `name:`). It **defaults to `true`**, so a valid skill is already
user-callable; set `user-invocable: false` only to hide one. Note the **hyphen** -
an underscore (`user_invocable`) is silently ignored, so it neither enables nor
disables anything.

The repo CI (`.github/workflows/team-context-lint.yml`) fails a PR if any
`.claude/skills/*/SKILL.md` is missing the `---` fence, `name:`, or
`description:`. `scripts/validate_skill.py` checks all of the above locally.

## The five agent types in this repo

"Build an agent" means one of five things here. Classify before authoring -
the type decides the directory, the template, and the deploy path.

| Type | Lives in | What it is | Live system access? | Model | Examples |
|------|----------|-----------|---------------------|-------|----------|
| **Workflow skill** | `.claude/skills/<name>/` | A repeatable job with a fixed output | Yes (via MCP tools) | Session model | `good-morning`, `nir-monthly-report`, `mops-standup` |
| **Skill-agent (router)** | `.claude/skills/<name>-agent/` | Owns a domain's live access + routing; invoked by `marketing-os` | Yes | Session model | `hubspot-agent`, `data-agent`, `slack-agent` |
| **Interview / builder skill** | `.claude/skills/<name>/` | Interviews the user, then generates an artifact | Sometimes | Session model | `granola-recipe-builder`, `setup`, `curious-intern`, this skill |
| **Specialist subagent** | `.claude/agents/**` | Deep domain persona, no live access, invoked by a skill-agent for a deep pass | No | `model: sonnet` | `SEO Specialist`, `Email Marketing Strategist` |
| **Cloud routine** | `.claude/skills/<name>/` + a schedule | A workflow skill that runs unattended on a cron | Yes | Session | `nir-mql-live-report`, `invoice-inbox-to-monday`, `p1-p2-followup` |

The two-layer model (routing skill-agents on top, specialist subagents beneath)
is documented in `.claude/agents/README.md`. Read it before building a
specialist subagent - you must add the Riverside context block and register the
subagent under its owning skill-agent.

## Adapting an existing or bundled sample skill

Sometimes the input is not a blank build but an existing skill - often a bundled
`anthropic-skills:*` sample or a skill copied from elsewhere. Treat the sample as
a **draft, not a drop-in**: samples carry generic placeholders that pass a glance
but silently misfire in this repo. Before deploying, swap every one for the
Riverside-specific truth:

- **Resource paths:** `/mnt/skills/...` (bundle paths) → repo paths
  (`.claude/skills/<name>/...`) or an `anthropic-skills:<name>` skill invocation.
- **Invented tools / channels:** placeholder trackers and channels (e.g.
  "Linear", a made-up Slack channel) → the real systems - `monday` board IDs,
  confirmed channel IDs from `references/slack.md`.
- **Wrong brand facts:** generic values (e.g. a stock font) → the verified token
  from `riverside-brand-guidelines` / `references/design-system/`.
- **Vague owners / escalation:** "the Head of X" → a named role from
  `references/team.md` (frame by role, name the current holder, so it survives
  turnover).
- **Name collision:** if the sample shares a `name` with a bundled skill, rename
  so `/list-skills` and routing are unambiguous.

Verify each swapped-in fact against the live source rather than trusting the
sample (a wrong board owner or font in a "finished" sample is exactly the trap).
Then run the same layered author → validate → register → deploy path as any new
skill. A sample that "looks done" is precisely the case the *if it only works
when its author runs it, it isn't done* rule is warning about.

## Where skills run, and how they deploy

Custom skills do **not** sync across surfaces. Build for the surface the team
actually uses, and know the others exist.

| Surface | How a custom skill gets there | Sharing scope | Network / packages |
|---------|-------------------------------|---------------|--------------------|
| **Claude Code (this repo)** | Filesystem: commit `.claude/skills/<name>/` and merge. **This is the team's primary path.** | Project-wide via git | Full network access |
| claude.ai | Upload a `.zip` in Settings → Features | Per individual user | Varies by admin setting |
| Claude API | Upload via the `/v1/skills` endpoints | Workspace-wide | No network, no runtime installs |

For this repo, "deploy" almost always means: commit to a branch, open a draft
PR, merge. On merge the Wiki + Graph Sync workflow regenerates the
wiki page and the knowledge graph automatically - you never hand-write those.
See `docs/wiki-sync-automation.md`.

**Promoting a local plugin skill into the repo.** A skill may already exist as a
local plugin skill (it shows up as `<plugin>:<name>` in the session's skill list
and lives under `~/Library/Application Support/Claude/.../skills-plugin/.../skills/<name>/`).
Those are session-local and not version-controlled, so the whole team cannot use
them. To promote one, treat it as a normal build: copy its `SKILL.md` (and any
`knowledge/`) into `.claude/skills/<name>/`, run it through Step 4 validation,
register it in `CLAUDE.md`, and open the PR. The source content is usually
already lint-clean, so the real work is the cross-linking and registration, not
re-authoring. `riverside-ux-patterns` was promoted this way as the interaction
companion to `riverside-brand-guidelines`.

A **cloud routine** deploys in two parts: (1) the skill files (same as above),
and (2) a schedule. The schedule is a recurring trigger that fires the skill's
invocation prompt on a cron. Existing routines document their own cadence in
their `SKILL.md` (e.g. "runs daily", "runs weekly"). Only wire the schedule
after the skill has been tested on real data at least once.

## Security note

Skills grant Claude new capabilities through instructions and code. Only build
from trusted intent, and never author a skill that fetches and blindly executes
instructions from an external URL, or that moves data to an external system
without an explicit confirmation step. The repo's rule stands: **any mutating
action (HubSpot/monday/Slack/ad-platform writes, sends) must ask for
confirmation unless the skill is a deliberately unattended routine.**
