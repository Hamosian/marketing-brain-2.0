# Marketing Brain trainer

A self-guided, role-aware trainer for the whole Marketing department. It has three goals: trust the Brain for the right reasons, know where to send a request, and run one real command this week. The same page doubles as the show-and-tell deck (Presenter mode).

- **Live artifact:** https://claude.ai/artifact/BVUaXpG3oTh5uao5ZwVop5 (shared with the organization; the older link https://claude.ai/code/artifact/54f53531-5029-40bb-8cd7-d9d68943ede2 opens the same page)
- **Source of truth:** `src/`. `index.html` is generated, never edit it by hand.

## What is in it

13 core slides (about 15 minutes) and an optional appendix:

- **Path picker.** Team, function, and experience drive the worked example, the practice requests, and the first command.
- **Trust story.** A prediction moment (what plain Claude says versus the Brain), real receipts, one rule and three habits, and what it does alone versus when it asks, with two checkpoints.
- **Worked example.** One real request replayed step by step for the viewer's role, true to that skill's file.
- **Router.** The same TF-IDF method as `scripts/eval_routing.py`, run in the page over all skills. It shows the top 3 matches, the Rivermind-first data rule, a fallback to `/marketing-brain`, and tags on person-owned skills.
- **Practice.** Five requests from `evals/routing.jsonl`, weighted to the role, with near-miss distractors.
- **Get set up.** Access, Claude Code on the web or locally, connector approvals, and the "tell me about the team" check.
- **Final check.** Six situations (pass at 5).
- **Commitment.** A role-aware first command, a day, and a check-in on the next visit.
- **Appendix.** How context loads, a searchable skill catalog, the real wiring graph, how the repo maintains itself, and where the Brain shows up in Slack.

## Generated at build time

`build.py` pulls these from the repo, so they never drift:

- The skill catalog (name and description of every `.claude/skills/*/SKILL.md`).
- The wiring graph (skill-to-skill and skill-to-doc links stated in the skill files).
- The routing test cases (`evals/routing.jsonl`).
- The routing score (it runs `scripts/eval_routing.py`).
- The build date.

## Capabilities (declared at publish)

The page works fully without any of these. They are only extras.

- `db`: `funnel/<viewer>` saves each viewer's progress stages (not quiz answers). Only the owner can read other viewers' records, in the "Team progress" panel on the commit slide. `live/state` powers "Follow the presenter". `flags/<viewer>` holds "This looks wrong" reports. Rules: `funnel` and `flags` are read and write for the owner only; `funnel/{self}` and `flags/{self}` are read and write at interact level; `live` is read at view level and written at admin level.
- `user` with the `profile` scope: viewer id, owner check, and names in the owner panel.
- `sample`: an optional "Ask Claude to route this" button on the router.

## Edit, build, check

```bash
cd tools/marketing-brain-trainer
python3 build.py                        # writes index.html
python3 validate.py index.html          # full check (needs Node and Python Playwright with Chrome)
python3 validate.py index.html --static-only
python3 build.py --check                # exit 1 if index.html is stale
```

- **Layout.** Slides live in `src/slides/NN-*.html` (one `<section class="slide" data-id=...>` each, with speaker notes in `aside.notes`). Styles live in `src/css/NN-*.css`, scripts in `src/js/NN-*.js` (`00-core.js` exposes `window.MBT`), and the page shell in `src/index.template.html`.
- **What the validator fails on:** script errors, em or en dashes, product-palette colors, taught Slack syntax, external requests, duplicate ids, a missing AI diligence statement, runtime errors, horizontal overflow at desktop or phone width, Space on a focused button changing the slide, focus reaching hidden slides, and router accuracy under 80%.
- **Rules to keep.** Everything is inline, because the artifact runtime blocks external requests. Use the marketing palette from `riverside-brand-guidelines`, not the product design system. No em or en dashes, no exclamation marks, sentence case headings.

## Republish

Build, then publish `index.html` to the artifact URL above with the Artifact tool, keeping the stored capabilities. Update this README if the URL changes.
