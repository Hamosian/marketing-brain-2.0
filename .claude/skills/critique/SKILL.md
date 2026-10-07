---
name: critique
description: "Judge a finished draft without rewriting it. Return SHIP or REVISE based on clarity, specificity, insight, length, tone, evidence, and the intended reader action."
---

# Critique

Run after `brand-voice` and `de-ai` on writing that needs an independent quality pass.
This is a verdict, not a rewrite and not permission to publish.

## Method

Read the audience, goal, ask, approved claims, and finished draft.
Score every dimension Pass or Flag. Each Flag needs a reason and a specific fix.

1. **Point first.** Does the opening answer the reader's question?
2. **Specific.** Are claims concrete and supported by evidence?
3. **Non-obvious.** Does it add useful information for this audience?
4. **Earns length.** Does each sentence contribute?
5. **Peer not pitch.** Is the tone appropriate without hype or forced familiarity?
6. **Clean.** Does it avoid the vague wording and stock phrases covered by `de-ai`?
7. **Gets the goal.** Is the requested action clear and within the original scope?

Do not add scope, invent proof, or replace a supplied voice with someone's personal style.
Return the fixes to the drafting workflow. After two unsuccessful rounds, identify the
remaining disagreement and ask the human to decide.

## Output

```text
VERDICT: SHIP | REVISE

Point first    Pass | Flag - reason and fix
Specific       Pass | Flag - reason and fix
Non-obvious    Pass | Flag - reason and fix
Earns length   Pass | Flag - reason and fix
Peer not pitch Pass | Flag - reason and fix
Clean          Pass | Flag - reason and fix
Gets the goal  Pass | Flag - reason and fix

Top fix: the most important change, if REVISE
```

SHIP means the draft passed this review. It does not authorize external delivery.
