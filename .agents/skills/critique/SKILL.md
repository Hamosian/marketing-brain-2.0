---
name: critique
description: Final taste/quality gate for outward-facing writing. Runs LAST, after nik-voice then de-ai, and asks the question those skills do not - is this actually good? Scores a draft on whether it gets its goal with its reader, point-first, specificity, non-obviousness, economy, peer-not-pitch tone, and a slop backstop, then returns a SHIP or REVISE verdict with the specific fixes. It only critiques - it never rewrites. Use for high-stakes outward-facing content before it ships. Trigger on "/critique", "critique this", "taste check", "is this good", "is this any good before I post it", "before it ships", "would a peer respect this", "score this draft", "does this land", or "final gate". Functional and internal output is IN scope, using ste at the writing stage and then still coming here. Only output Nir alone reads skips it. NOT a rewrite tool - that is writing-optimizer.
---

# Critique - the taste gate before content ships

This skill judges whether a piece of writing is good enough to send. It runs after the content pipeline, not inside it.

- `nik-voice` makes it sound like Nik.
- `de-ai` strips the AI tells.
- `critique` asks the question neither of those asks: **would a sharp peer in the intended audience respect this, believe it, and act on it?**

It is a gate, not an editor. It returns a verdict plus what to change and why. It does **not** hand back a rewrite. A critic that rewrites stops being a check (see `references/agent-prompting.md`, Block 6).

## When to use it

Run critique as the last step on high-stakes outward-facing content:

- LinkedIn posts, thought leadership, social content
- Cold and nurture emails, prospect replies
- Landing page and ad copy, headlines
- Decks and one-pagers a customer or exec will read

## When NOT to use it

- Output **Nir alone** reads: a report to him, working notes, analysis he asked for. Nothing else is out of scope.
  - **Functional and internal output IS in scope (per Nir, 2026-09-07).** A status update, a standup post, a data answer or an ops handoff that another person reads gets scored here. `ste` is what writes it, in place of a `nik-voice` register; it does not excuse it from the verdict. The test is who reads it, not what kind of writing it is.
- When you want the draft fixed, not judged - that is `writing-optimizer`. Critique tells you what is wrong; it does not fix it.
- Every routine Slack line. This is a gate for pieces that matter, not a tax on every message.

## The bar

One question decides it: **would a sharp peer in the intended audience respect this, believe it, and act on it?** If any dimension below is flagged, the answer is no.

Score each dimension Pass or Flag. A Flag needs a one-line reason and the specific fix.

**An internal ask is scored against the same bar, with two extra flags.** A short Slack or email request to colleagues is not marketing copy, and the failure modes are different from a landing page. Flag it when the draft **adds scope Nik did not ask for** (an extra deliverable, an options menu, a rationale he never gave), and flag it when the draft **rewrites phrasing Nik already supplied** instead of keeping his words. Both read as the writer improving on the request rather than making it. Took four rounds on one three-line Slack message on 2026-09-02, every round the same shape.

1. **Point first.** The opening line states the point or the stakes. Flag if the reader has to reach line 2 or later to learn why this matters. On functional output (a summary, report, brief, answer) this is the `minto-pyramid` stop test; also flag label headings ("Findings", "Overview") and a closing line that repeats the top.
2. **Specific, not vague.** Real numbers, names, dates, examples. Flag any claim that could be pasted onto any other company's page ("boost engagement", "drive results", "in today's landscape"). Flag a feature named without the job it gets done or the pain it kills; a feature list is a spec sheet, and the reader has to do the translation the writer skipped.
3. **Non-obvious.** Says something the intended reader does not already know or would not already nod along to. Judge against the reader's row in `.claude/skills/nik-voice/readers.md`, not a generic marketer. Flag if a peer would think "no kidding" or "everyone says this."
4. **Earns its length.** Every sentence carries weight. Flag filler connectors, restated points, and any sentence that could be cut with no loss.
5. **Peer, not pitch.** One professional talking to another. Flag hype adjectives, salesy tells, hedging, and trying-too-hard cleverness. **On an internal ask this is the dimension that fails most often.** Flag a request framed as a call for volunteers ("looking for 1-2 volunteers", "who's in?"), and flag any sentence that argues why the ask benefits the reader. Colleagues do not need the benefit sold to them, and selling it is the tell that a machine wrote the request. State the fact, then ask the question.
6. **Clean (slop backstop).** No AI tells `de-ai` missed. Flag and name the specific one: "It's not X, it's Y", forced rule-of-three, "fast-paced world", em dashes, LinkedIn-broetry line breaks.
7. **Gets the goal.** Take the reader brief from `nik-voice` (reader, goal, ask). Would this reader, as briefed, do the thing? Flag a draft that informs when the goal was a decision, that buries or splits the ask, or whose polish is wrong for the reader's row in `.claude/skills/nik-voice/readers.md` (a polished multi-paragraph DM to Abel or a direct report reads as agent-written). If no brief exists, flag that first.

## Method

**This gate always runs on outward-facing writing. What scales is the pass, not whether it happens.**

| Stakes | How it runs |
|---|---|
| A short internal message, a routine reply | Inline. Score the seven dimensions in your own turn, fix, ship. No separate agent. |
| A prospect email in a batch | Inline, on every body, invoked through the `Skill` tool. It does NOT fold into `demo-reply-fact-check`'s Voice row (per Nir, 2026-09-28): the folded version let an unclear reply lede ship because nobody scored it against the lead's actual question. Score it with the lead's own words beside the draft. |
| A LinkedIn post, a board narrative, anything public or exec-facing | **Separate pass, and the verdict is binding.** REVISE means revise. An author scoring their own framing is the failure this gate exists to catch, and at these stakes the separation is the point. |

Never skip it because a draft "reads fine" to the writer who just wrote it. That judgement is exactly what is unavailable to them.

1. Take the draft (already through `nik-voice` -> `de-ai`).
2. Score all seven dimensions. Do not skip one because the draft "reads fine".
3. Return the verdict in the schema below. Do not rewrite the draft.
4. On REVISE, hand the fixes to the drafting skill, revise once, then re-run critique.
5. **On SHIP for anything that will be sent, record the exact final text** with `python3 scripts/content_gate_record.py --verdict SHIP --register <register>` (text on stdin; add `--nir-approved` when Nir approved the exact wording, so it goes out without the agent footer). The content gate hook blocks Slack and Gmail sends of any text not recorded here, so a skipped critique cannot leave the building.
6. Stop on SHIP, or after two rounds. If it still flags after two rounds, the draft and the criteria disagree - say which criterion and why, and let Nik call it. Do not loop.

## Output schema

Return exactly this, nothing before it:

```
VERDICT: SHIP | REVISE

Point first    Pass | Flag - <reason + fix>
Specific       Pass | Flag - <reason + fix>
Non-obvious    Pass | Flag - <reason + fix>
Earns length   Pass | Flag - <reason + fix>
Peer not pitch Pass | Flag - <reason + fix>
Clean          Pass | Flag - <reason + fix>
Gets the goal  Pass | Flag - <reason + fix>

Top fix: <the single most important change - only if REVISE>
```

## Example

**Draft (post-pipeline):**
> In today's fast-paced content landscape, brands need to leverage authentic video to truly stand out and drive meaningful engagement with their audiences.

**Critique output:**
```
VERDICT: REVISE

Point first    Flag - opens with scene-setting, not a point. Lead with the claim.
Specific       Flag - "meaningful engagement", "stand out" fit any brand. Name a number or a real outcome.
Non-obvious    Flag - "use authentic video" is a truism every marketer already agrees with.
Earns length   Flag - "truly", "meaningful" carry no weight. Cut.
Peer not pitch Flag - "leverage", "truly stand out" read as pitch, not peer.
Clean          Flag - "In today's fast-paced landscape" is a slop opener de-ai missed.
Gets the goal  Flag - no reader or ask. Nobody knows what to do after reading it.

Top fix: Replace the whole line with the actual insight and a real number. What did authentic video change, and by how much?
```

## Graduating this skill

Starts on-demand for a trial on high-stakes outward pieces. If it proves out, add a global directive to `CLAUDE.md` so outward-facing content runs `nik-voice` -> `de-ai` -> `critique` by default, and log it in the pipeline gate. Run `/skill-eval` after wording the description, since it shares trigger surface with `writing-optimizer`.
