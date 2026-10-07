<!-- last-reviewed: 2026-07-25 -->
# Output contract (canonical)

Every specialist subagent in `.claude/agents/` returns its deep pass in one fixed shape. This file holds the canonical text; `scripts/harmonize_agents.py` copies the delimited block below into each subagent, and `scripts/lint_agents.py` fails the build if a subagent is missing it.

## Why this exists

A specialist's reply is not a human-facing answer - it is an input to the skill-agent that invoked it, which then synthesizes across several specialists, applies the brand layer, and gates any mutation. `references/agent-prompting.md` (block 5, "Schema the output") is explicit about what that requires: exact section titles, mandatory sections, and defined fallback text so a reader - human or downstream agent - can parse the result without guessing.

Before this contract existed, the layer had no return shape at all. Several subagents carried a "Technical Deliverables" or "Your Deliverable Template" section, but those describe *artifacts the subagent writes to disk*, not what it hands back. The contract sits above those: keep producing whatever artifacts your domain calls for, and use this shape for the reply itself.

## Embedded block (canonical)

Everything between the two markers is copied verbatim into every non-exempt subagent. Edit it here, never in the subagents, then run `python3 scripts/harmonize_agents.py`.

Note the convention: the canonical region **opens** with the in-agent marker (`<!-- output-contract -->`) but does **not** include the closing one - the harmonizer writes that itself. `RIVERSIDE_CONTEXT.md` follows the same rule.

<!-- output-contract:start -->
<!-- output-contract -->
## Output contract

Your reply goes to the skill-agent that invoked you, not to a person. It synthesizes across specialists, applies the brand layer, and gates any mutation - so a predictable shape matters more than polish. Keep producing whatever artifacts your domain calls for; this governs the reply itself.

Return these sections, in this order, with these exact headings:

1. `## Summary` - 2-4 sentences carrying the actual answer. No preamble and no restatement of the request.
2. `## Findings` - what you found, most consequential first. Each finding names the evidence it rests on (the data handed to you, or the repo file you read).
3. `## Recommendations` - ranked, most valuable first. Each one carries an effort estimate (S / M / L), the expected impact, and the system or owner that would execute it.
4. `## Open questions` - **inputs and decisions you need** to go further: a missing snapshot field, an ambiguous goal, a call that is not yours to make. Each is a request, phrased so it can be answered without re-reading your whole reply.
5. `## Not verified` - **claims in this reply you could not ground** in data handed to you or in repo context. Each is a caveat, stated plainly rather than buried mid-paragraph.

The two are not alternatives, and one gap often produces an entry in both: if the snapshot omitted spend by campaign, *ask for it* under `## Open questions`, and if you still made a recommendation that leans on an assumed figure, record that assumption under `## Not verified`. Requests go in the first, unsupported claims in the second.

Rules:

- **Every heading is mandatory.** When a section is genuinely empty, keep the heading and write `None.` - a dropped section is indistinguishable from one you overlooked.
- **Ground each factual claim** in data you were given or a repo reference, and say which. An ungrounded claim belongs in `## Not verified` and a missing input belongs in `## Open questions` - never fill either with a plausible-looking number.
- **Recommendations that need a live write** name the mutation precisely and stop there. You do not execute it; the skill-agent confirms and runs it.
- **Rank by value, not by confidence.** If the highest-value recommendation rests on a shaky assumption, keep it first and record the assumption in `## Not verified`.
<!-- output-contract:end -->
