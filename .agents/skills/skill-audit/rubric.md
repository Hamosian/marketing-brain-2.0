<!-- last-reviewed: 2026-08-11 -->
# Skill authoring rubric

The scoring rubric for `/skill-audit`. Loaded on demand, not at session start. Every
dimension traces to `references/agent-prompting.md` (the six building blocks and the
review principles) so an audit reflects the repo's own stated bar, not a generic one.

Score each dimension 0-2:

- **0 - absent.** The skill would misbehave or route wrong for lack of it.
- **1 - partial.** Present but weak: vague, incomplete, or stated without a fallback.
- **2 - solid.** A reader (human or downstream agent) could act on it without guessing.

Total is out of 16. Report the per-dimension score with a one-line reason, then the
sum. The score is a conversation-opener, not a grade: the value is the named cause and
the exact fix, exactly as `/skill-eval` treats a routing miss (see
`docs/skill-evals.md`, "Why the feedback channel matters more than the score").

`scripts/audit_skill.py` gives you the deterministic signals (present/absent) for most
of these. Use them as evidence; still read the skill, because presence is not quality -
an `Output` heading with nothing parseable under it is a 1, not a 2.

## Dimensions

### 1. Specification (block 1)
Does the skill define the job before the prose - inputs, outputs, constraints, and what
success looks like? A skill that starts issuing instructions with no stated goal scores 0.
Look for an explicit "done when" / acceptance bar somewhere in the file.

### 2. Description as routing surface (block 4, applied to the description)
The `description` is the single prompt the router reads and the least-tested prose in the
repo. Score 2 only if it (a) names what the skill does, (b) carries concrete trigger
phrases or an example request, and (c) is distinguishable from its siblings - a reader
could tell why a request goes here and not to a neighbour. Over the 1024-char cap is an
automatic finding. If two skills' descriptions could both plausibly claim the same
request, that is a collision to name, and it belongs to `/skill-eval` to confirm.

### 3. Structure & layering (block 2)
Named sections in a fixed order, core behaviour before higher-value logic. A wall of
undifferentiated prose scores low even if complete.

### 4. Constraints & defaults (block 3)
Explicit guardrails, and - the half authors forget - a named fallback for every "if
unclear" branch. "Don't invent items not in the source" and "if the channel is
unreadable, skip and note it" are 2s. No guardrails at all is a 0, especially for a skill
that runs unattended.

### 5. Worked examples (block 4)
At least one concrete input-to-output example that anchors tone, depth, and format.
Adjectives describing the output ("a clean summary") do not count; a shown example does.

### 6. Output schema (block 5)
Fixed section titles, mandatory sections, and fallback text ("No items today" rather than
a silently omitted section). Score against whether a downstream reader could parse the
output without guessing.

### 7. The bar / critic (block 6)
Either a stated acceptance bar for one-shot output, or, for generative skills (copy,
narrative, a report, a QA finding), a generate-evaluate-revise loop with the criteria
named in terms someone could disagree with. A data-pull skill needs only the bar, not a
loop. Missing bar *and* missing loop on a generative skill is a 0.

### 8. Grounding & systems (review principles)
Does it require citing/quoting source data and forbid inventing entities not in the
input? Does it behave like a system - work when someone other than the author runs it -
rather than relying on the author's memory? Conflicting sources should be treated as a
finding (see `references/evidence-standards.md`), not a footnote.

## Boundary - what this rubric does not judge

- **Structural validity** (frontmatter keys, tool scoping, model pinning): CI owns it -
  `scripts/lint_agents.py` + `team-context-lint`. Don't re-score it here; if CI is red,
  that is the finding.
- **Routing behaviour** (does a request actually land here): `/skill-eval` +
  `evals/routing.jsonl`. This rubric judges whether the description is *well-written*, not
  whether it currently wins the request - a well-written description can still collide.
- **Staleness / template drift**: `/health-check`.

A skill can pass all three of those and still score poorly here, and that is the whole
point: those check that a skill is valid, current, and reachable; this checks that it is
*good*.
