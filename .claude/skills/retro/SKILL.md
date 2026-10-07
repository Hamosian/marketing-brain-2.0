---
name: retro
description: Use this skill when the user wants to capture learnings from a completed workflow, save knowledge for next time, update a skill or system doc based on what was discovered, or reflect on what went well/poorly. Triggered by "let's retro", "capture what we learned", "save this for next time", "update the skill", "what did we learn", "document this for next time", "don't forget this", "we should remember this". Also suggest this skill proactively after completing a novel or complex workflow.
---

# Retro - Capture and Commit Learnings

This skill closes the flywheel loop: after completing a novel workflow, it captures what was learned and commits it to the repo so the whole team benefits. Without this step, knowledge stays in one person's head (or worse, in memory where only one user sees it).

**When to use retro vs curious-intern:** Retro is reactive - something just happened, capture it quick (2 min). Curious-intern is proactive - you have spare time, let Claude interview you to systematically fill gaps (15-30 min). If the user has more than a quick learning to capture, suggest `/curious-intern` instead.

**Done when:** each learning sits in exactly one file, the file the Knowledge Routing table in `CLAUDE.md` names for it; no contradicting copy survives elsewhere (Step 3.1); and the change is on a branch with a PR open, or the user has said to leave it uncommitted. A well-written summary that edits no file is not a retro.

## What this skill does not do

- **Interview for gaps nobody hit yet.** That is `/curious-intern`.
- **Improve skills in bulk.** Scoring and fixing the weakest skills across the library is `/skill-optimizer`; retro patches the one failure this run exposed.
- **Save team knowledge to memory.** Memory holds one person's preferences only (Step 2, last row).

## Step 1: Interview

Ask the user (batch these, don't drip):

1. **What broke during the run, and what fixed it?** Take this from the session's fix ledger if the skill kept one (block 7 in `references/agent-prompting.md`). For each item: which kind (glitch, tool down, empty, wrong), and whether the fix was a workaround or a real one. A workaround that worked is the thing to patch, because it will be reached for again.
2. **What did we just do?** (one sentence - which system, what workflow)
3. **What was surprising or non-obvious?** (the stuff a teammate doing this next time would trip on)
4. **What would you want Claude to know next time?** (the shortcut, the gotcha, the "don't do X")
5. **Did any existing skill or doc give wrong/stale information?** (if yes, which one)

If the conversation history makes any of these obvious, skip that question and state your assumption for confirmation.

**Ground it in the run.** For each learning, quote the moment it came from: the tool error, the user's correction, the line of the skill that was wrong. The patch goes at the exact point where the agent guessed or skipped (`references/agent-prompting.md`, "Two habits that keep the rules honest"). If you cannot point to that moment, it is a general reflection, not a learning, and it does not get written down.

## Step 2: Route the Learning

Based on the answers, determine where each piece of knowledge belongs:

| What was learned | Where it goes | Action |
|-----------------|---------------|--------|
| System behavior, API quirk, failure mode | `systems/owned/<system>.md` | Add to "Known Issues / Failure Modes" or relevant section |
| New skill workflow or improvement to existing skill | `.claude/skills/<name>/SKILL.md` or `knowledge/` | Update the skill instructions or add a knowledge file |
| Missing step in a workflow, wrong assumption | `.claude/skills/<name>/SKILL.md` | Fix the instruction |
| A failure the skill handled with a workaround | `.claude/skills/<name>/SKILL.md` | Name the failure kind and encode the matched fix as a rule, not a note (`references/agent-prompting.md` block 7) |
| Team convention or workflow rule | `CLAUDE.md` or `references/` | Add to the appropriate section |
| Stale information (wrong board ID, dead URL, renamed service) | The file that contains the stale info | Fix it directly |
| User's personal preference (style, tone, approach) | Memory | Save to memory - this is the ONLY case for memory |

**Important:** If you're tempted to save something to memory, ask yourself: "Would this help OTHER team members too?" If yes, it belongs in the repo.

## Step 3: Make the Changes

1. Read the target file(s) to understand current content, then grep for the claim you are replacing: the rest of that skill, sibling skills that keep their own copy of the template, and any ledger. A fix that lands in one place while a contradicting copy survives elsewhere has not fixed anything (`references/agent-prompting.md`, "A patch has to land everywhere the old rule lives")
2. Make the edit - add the learning in the appropriate section, following the file's existing structure
3. If adding to a system doc, update the `<!-- last-reviewed: YYYY-MM-DD -->` date
4. Ship it the way every change here ships (`references/change-control.md`): branch off `main`, run `python3 scripts/sync-codex.py` if you touched `.claude/`, run `bash scripts/preflight.sh`, then open a PR with `gh pr create`. Small fixes (a typo, a stale URL, one line) still go through a PR, just a short one
5. If the user says not to commit, leave the edit in the working tree and say "written but not landed" in Step 4

## Step 4: Confirm (output)

Show the user what was captured and where, one line per learning, then the landing state. If nothing met the bar in Step 1, say "No learnings to capture from this run" and stop.

Example, from the 2026-09-21 broken-link incident in #US Demo requests routing:

```
Captured learnings:

1. CLAUDE.md, Global Agent Directives: Slack links are always written <url|label>.
   From: a bare HubSpot URL at the end of a line swallowed the next word and 404'd.
2. .claude/skills/inbound-demo-reply/SKILL.md, handoff step: pointer to that rule,
   because its templates show bare URLs and those are what get pasted (Step 3.1).

Landing: PR #374 open, preflight green. [or: written but not landed, user asked to hold]
```

## When to Suggest This Skill Proactively

After completing any workflow where:
- You had to be guided through steps that weren't in a skill
- You discovered a system behavior that isn't documented
- An existing skill gave wrong or incomplete instructions
- The user corrected you on something that other users would also need to know

Say: "We learned some things during this workflow. Want to run `/retro` to capture them before they're lost?"

## Key Principles

- **Repo over memory.** System knowledge in memory is a bug, not a feature. Only user preferences go to memory.
- **Small, frequent updates beat big documentation pushes.** Don't wait for a "documentation sprint" - capture learnings immediately while context is fresh.
- **Update the `last-reviewed` date** on any system doc you touch. This keeps `/health-check` accurate.
- **Don't duplicate.** Before adding something, check if it's already documented elsewhere. If it is, update the existing content rather than adding a second copy.
