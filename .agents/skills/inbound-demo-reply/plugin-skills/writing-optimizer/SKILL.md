---
name: writing-optimizer
description: "Optimize, sharpen, and strengthen any piece of writing using proven frameworks. Use this skill whenever the user wants to improve writing - LinkedIn posts, emails, landing pages, sales copy, newsletters, memos, announcements, thought leadership, or any other content. Trigger on: 'optimize this', 'improve this', 'make this better', 'this feels flat/wordy/boring/robotic/abstract/forgettable/off', 'sharpen this', 'punch this up', 'rewrite this', 'make this more memorable/clear/concise/human/reader-focused', 'critique this', 'what's wrong with this', 'help me with this post/email/copy'. Also trigger when the user pastes a draft and asks for feedback or improvement without specifying how. This skill covers 6 deep methodologies: Made to Stick, Smart Brevity, StoryBrand, Jobs To Be Done, Gary Provost Rhythm, and Analogical Framing - it selects the right one(s) automatically."
---

# Writing Optimizer

A multi-methodology writing optimization system. It analyzes the user's content, selects the right framework(s) from 6 proven methodologies, and spawns specialist sub-agents - each expert in one methodology - to do the actual optimization work.

## How it works

**Before doing anything else**, read the router file:

```
references/router.md
```

The router contains all instructions: how to analyze content, how to select methodologies, how to spawn specialist sub-agents, and how to present results.

## The 6 methodologies

Each has a deep reference file in `references/`:

| Methodology | File | Best for |
|---|---|---|
| Made to Stick | `made-to-stick.md` | Forgettable, abstract, or flat writing that needs to be memorable |
| Smart Brevity | `smart-brevity.md` | Wordy, bloated, buried-lede writing that needs sharpening |
| StoryBrand | `storybrand.md` | Brand-centered writing that should be reader-centered |
| Jobs To Be Done | `jobs-to-be-done.md` | Feature-focused writing that should be outcome-focused |
| Gary Provost Rhythm | `gary-provost-rhythm.md` | Monotone, robotic writing that needs life and flow |
| Analogical Framing | `analogical-framing.md` | Abstract or technical writing that needs a concrete hook |

## Architecture

```
SKILL.md          ← you are here (trigger + overview)
references/
  router.md       ← routing brain (read this first)
  made-to-stick.md
  smart-brevity.md
  storybrand.md
  jobs-to-be-done.md
  gary-provost-rhythm.md
  analogical-framing.md
```

The reference files are for specialist sub-agents only. They do NOT load into the main context - each sub-agent reads only the file relevant to its methodology. This keeps the main context clean while giving each specialist full expert-level knowledge.
