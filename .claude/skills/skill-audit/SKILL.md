---
name: skill-audit
description: Score how well a SKILL.md is authored against the repo's own agent-prompting principles, and propose the exact fix per gap. Use when the user wants to audit, review, grade, or improve the quality of a skill's writing - "audit this skill", "is this skill well written", "review the skill authoring", "score my SKILL.md", "how good is the good-morning skill", "which skills are poorly written", "improve this skill's description". The authoring-quality tier beside /health-check (staleness) and /skill-eval (routing) - it judges whether a skill is written well, not whether it is valid, current, or reachable. Run after writing a new skill or reworking an existing one.
---

# Skill audit

Scores a skill's **authoring quality** - is it written like a reliable system - against
the rubric in `rubric.md`, which is derived from `references/agent-prompting.md` (the six
building blocks and the review principles). Produces a scored report with a named cause
and an exact fix per gap, the same feedback-first shape `/skill-eval` uses for routing.

This is the tier the repo was missing. CI checks a skill is *valid* (`scripts/lint_agents.py`,
`team-context-lint`), `/skill-eval` checks it is *reachable*, `/health-check` checks it is
*current*. None of them check it is *good*. This does.

## Workflow

1. **Scope.** Ask which skill(s) unless named. `--all` is fine for a sweep.

2. **Run the deterministic pass** to get the mechanical signals (present/absent) before
   reading anything:

   ```bash
   python3 scripts/audit_skill.py <skill-name>        # or --all, or --json for many
   ```

   `HARD` findings (no description, name/dir mismatch, over the 1024-char cap) are
   authoring defects to fix first. `warn` lines point at the rubric dimension they map to.

3. **Read the SKILL.md** (and any `knowledge/` or reference files it loads). The script
   tells you what is *present*; only reading tells you if it is *good*. An `Output`
   heading with nothing parseable under it is a partial, not a pass.

4. **Score against `rubric.md`.** Load it now. Eight dimensions, 0-2 each, out of 16.
   Give a one-line reason per dimension, grounded in a quote or line reference from the
   skill - do not invent gaps the file does not have.

5. **Report** in the format below.

6. **Offer, don't auto-apply.** Propose the exact edits (a tightened description, a
   missing fallback line, an output schema); let the user choose. If a description
   collision surfaces, hand it to `/skill-eval` to confirm rather than guessing.

## Output format

```text
## Skill audit: <name>   Score: N/16

| # | Dimension | Score | Reason |
|---|-----------|-------|--------|
| 1 | Specification | 2 | "Done When" block present, inputs named |
| 2 | Description (routing) | 1 | Names the job but no trigger phrases; collides with <sibling> |
| ... | | | |

### Fix first
- [HARD findings and 0-scored dimensions, each with the exact edit]

### Worth tightening
- [1-scored dimensions, each with the specific change]

### Solid
- [2-scored dimensions, one line]
```

For `--all`, lead with a ranked table (skill, score, top gap) and expand only the skills
that scored low or carry a HARD finding.

## What this skill does not do

- It does **not** re-check structural validity (frontmatter keys, tool scoping, model
  pinning) - that is CI (`scripts/lint_agents.py` + `team-context-lint`). If CI is red,
  that is the finding; fix it there.
- It does **not** judge routing - whether a request actually lands here. That is
  `/skill-eval` + `evals/routing.jsonl` (design: `docs/skill-evals.md`). A well-written
  description can still collide, so when this audit flags a collision, confirm it there.
- It does **not** check staleness or template drift - that is `/health-check`.

A skill can pass all three of those and still score poorly here. Those check that a skill
is valid, current, and reachable; this checks that it is written well. Close the report by
naming that boundary rather than implying full coverage.
