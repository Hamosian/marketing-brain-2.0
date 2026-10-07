<!-- last-reviewed: 2026-07-25 -->
# Archived specialist subagents

Personas retired from the active specialist layer. They are kept for history and are trivially restorable, but they are **out of the discovery path** - nothing routes to them and they no longer appear in the agent picker.

They live here rather than in `.claude/agents/archive/` on purpose: `.claude/agents/**` is scanned recursively, so a nested `archive/` folder would still have been loaded and still been selectable, which is the exact thing archiving is meant to stop.

## What's here

| File | Retired | Why |
|------|---------|-----|
| `marketing-book-co-author.md` | 2026-07-25 | Thought-leadership book authoring - outside the marketing operating cadence. |
| `marketing-short-video-editing-coach.md` | 2026-07-25 | Hands-on editing craft (CapCut, Premiere, Resolve) - a production skill, not a marketing function. Riverside's own product covers much of this ground. |
| `marketing-reddit-community-builder.md` | 2026-07-25 | Reddit community management - not a channel Riverside currently runs. |

All three were flagged as archive candidates in `.claude/agents/README.md` from 2026-07-19 and carried no Riverside context block, so nothing downstream depended on them. They were tool-scoped before archiving (they had been inheriting every session tool while sitting selectable in the picker).

## Restoring one

1. `git mv` the file back to `.claude/agents/marketing/`.
2. Add its `name:` to the registry table in `.claude/agents/README.md` and to the owning skill-agent's "Specialist subagents" section - the lint fails on an unregistered subagent, and routing is by display name.
3. Run `python3 scripts/harmonize_agents.py` to inject the Riverside context block and the output contract, then `python3 scripts/lint_agents.py`.

Do not re-add it to `HARMONIZE_EXEMPT` / `REGISTRY_EXEMPT` in `scripts/lint_agents.py`. Those sets are empty now, and an active subagent should meet the same bar as every other one.
