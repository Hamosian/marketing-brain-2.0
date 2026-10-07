---
name: skill-eval
description: Run the behavioural eval suite over this repo's skills - does a request actually route to the skill that owns it, and do specialist replies conform to the output contract. Use when someone says "run the evals", "run the skill evals", "test routing", "which skill descriptions collide", "did I break routing", "score the descriptions", "eval coverage", or "/skill-eval". Also use immediately after adding, renaming, or rewording a skill's description, and as the behavioural half of a pre-merge check that /health-check (staleness) and the CI lint (structure) do not cover. Produces a scored report plus concrete description patches for every miss.
user-invocable: true
---

# Skill Eval

You are the behavioural test harness for the Marketing OS. Structure is linted in CI and
staleness is audited by `/health-check`; nothing before this measured whether the system
*behaves* correctly. With 61 skills routed on frontmatter descriptions alone, the failure
that bites is a new or reworded description that quietly steals requests from an existing
skill - invisible to a structural lint, and only noticed when someone gets the wrong agent.

Your output is a score plus **a patch**. An eval that reports a failure and stops has done
half the job.

## Modes

| Mode | Trigger | What it does |
|------|---------|--------------|
| `routing` (default) | "run the evals", "test routing", "did I break routing" | Score every case in `evals/routing.jsonl`, propose description patches for misses |
| `coverage` | "eval coverage", "what isn't tested" | List skills with no eval case, propose cases for the important gaps |
| `contract` | "check this reply against the contract" | Score a specialist subagent reply against `.claude/agents/OUTPUT_CONTRACT.md` |

## Routing mode

### Step 1 - Run the deterministic tier first

```bash
python3 scripts/eval_routing.py --json
```

It never calls a model, so it is free and it fails fast. Read its output before doing
anything yourself:

- **Structural errors** (a case expecting a skill that no longer exists, duplicate
  requests, malformed JSON) - stop and fix these first. They mean the suite is broken, not
  that routing is broken, and every score below them is meaningless.
- **`verdict: "clear"`** - the expected skill wins on vocabulary alone. Low risk.
- **`verdict: "ambiguous"` / `"weak-trigger"`** - descriptions overlap on the terms a
  router keys on. These are your priority cases.

The lexical tier is a proxy, not an oracle. It tells you *where the vocabulary collides*;
only you can say whether a real router would be fooled.

### Step 2 - Score each case as the router would see it

For every case, decide which skill fires **using only each skill's frontmatter `name` and
`description`**. This is the whole discipline of the mode: the router sees descriptions, so
an eval that peeks at skill bodies measures your reading comprehension instead of the
system's routing. Do not open a `SKILL.md` body until Step 3, and never to justify a score.

Gather the descriptions with one pass rather than 61 reads:

```bash
python3 scripts/eval_routing.py --descriptions
```

Use this rather than grepping the frontmatter. It reuses the same parser the deterministic
tier scores with, so it handles keys in any order and descriptions that wrap onto
continuation lines - which most of the long ones do. A line-window grep silently truncates
those, and scoring a half-description is worse than not scoring it, because the miss looks
like a routing defect rather than a broken read.

Score each case:

| Score | Meaning |
|-------|---------|
| `pass` | The expected skill is the clear best match |
| `weak` | Expected skill wins, but another is a defensible read - a real session could go either way |
| `fail` | Another skill is the better match, or nothing matches well enough to route confidently |

Prioritise by the deterministic tier: score every `ambiguous` and `weak-trigger` case, and
every case whose `expect` you changed in this PR. Sampling the `clear` cases is fine when
the suite is long - say how many you sampled.

### Step 3 - Diagnose every `weak` and `fail`

Only now read the competing skills' bodies, and name the cause precisely. Almost every miss
is one of four things:

| Cause | Fix goes in |
|-------|-------------|
| Missing trigger - the description never mentions how people actually ask | the owning skill's `description` |
| Stolen trigger - another skill claims a phrase it does not own | the *other* skill's `description` |
| Overlapping scope - two skills genuinely cover the same job | scope boundary, or merge them |
| Wrong expectation - the eval case is wrong, the routing is right | `evals/routing.jsonl` |

Fixing the wrong file is the common error here: when skill B steals skill A's requests,
padding A's description is a workaround. Narrowing B is the fix.

### Step 4 - Propose the patch

For each `weak` and `fail`, write the exact replacement text - not advice about it. Both
sides of the diff, so the reviewer can judge it without opening anything:

```markdown
**`<skill>`** - `<cause>`
- Now: `<current description text>`
- Proposed: `<replacement description text>`
- Why: <what this stops routing to the wrong place, in one sentence>
```

Constraints on any description you propose:

- Says what it does **and when to use it** - triggers are the routing surface.
- ≤1024 characters, and does not exceed the current length by more than ~20%. Descriptions
  are always loaded; the budget is real. A description that grows every time a case fails
  is a scope problem being paid for in tokens.
- Adds phrases the skill genuinely owns. Claiming a rival's territory to win one eval case
  trades a passing case for a new failure elsewhere - re-run the deterministic tier after
  editing to confirm you did not.

Then re-run `python3 scripts/eval_routing.py` and report the before/after counts.

### Step 5 - Land it

Show the full patch set and **ask before writing** - descriptions are the routing layer, and
a bad edit here misroutes work silently. On approval, apply the edits, re-run
`scripts/eval_routing.py` plus `scripts/lint_agents.py`, and open a PR describing the score
delta.

## Coverage mode

```bash
python3 scripts/eval_routing.py --coverage
```

Untested is not the same as untestable. Rank the gaps by blast radius rather than reporting
them flat - a skill nobody has cased but which sits in a family of near-identical siblings
is a real gap; a one-of-a-kind skill with unmistakable vocabulary is not. Propose concrete
cases (`request` / `expect` / `why`) for the top gaps, then offer to append them.

## Contract mode

Given a specialist subagent reply, score it against the five mandatory headings in
`.claude/agents/OUTPUT_CONTRACT.md` (`## Summary`, `## Findings`, `## Recommendations`,
`## Open questions`, `## Not verified`). Check that every heading is present even when
empty (`None.`, never dropped), that findings name their evidence, that recommendations
carry effort/impact/owner, and that ungrounded claims sit under `## Not verified` rather
than being asserted mid-paragraph. Report per-heading `pass`/`fail` plus the specific line
that broke each rule.

## Output schema

Fixed sections, in this order. Keep every heading even when empty - write `None.` rather
than dropping it, so a reader can tell "nothing to report" from "forgot to check".

```markdown
## Score
| Verdict | Count |
|---------|-------|
(pass / weak / fail, plus how many cases you scored and how many you sampled)

## Misses
(one block per weak/fail: request, expected, what would actually fire, cause)

## Proposed patches
(the Step 4 blocks - exact before/after text)

## Suite fixes
(cases that were themselves wrong, with the corrected line)

## Coverage gaps
(skills with no case, ranked by blast radius)
```

## Rules

- **Descriptions only when scoring.** Reading a skill body to decide routing invalidates the
  score. Bodies are for diagnosis in Step 3.
- **Never edit a description without approval.** This is the routing layer; a silent misroute
  is worse than a failing eval.
- **Never quietly relax a case to make it pass.** Changing `expect` is a legitimate finding
  when the case was wrong - but it belongs under `## Suite fixes` where a reviewer sees it,
  never folded into the patch set.
- **Report what you did not check.** If you sampled, say the sample size. An unqualified
  "all clear" over a partial run is the one output that makes this skill worse than nothing.
- **A green suite proves the cases pass, not that routing is correct.** The suite only knows
  what someone thought to write down; treat coverage gaps as unknowns, not as passes.
- **Deterministic first, always.** Never spend model calls on what
  `scripts/eval_routing.py` already answers for free.

Full design and rationale: `docs/skill-evals.md`.
