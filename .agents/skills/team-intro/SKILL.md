---
name: team-intro
description: Use this skill when the user asks what you know about them, the team, their projects, or their systems - especially in an onboarding framing like "tell me about the team", "onboard me", "what do you know about us", "who's on the team", "what systems do we own", "what can you do for me", or any variant of "what do you know about me and the team". Also trigger when a new person is being onboarded in chat or when the user asks for a team/project overview. Answers in chat; a written onboarding doc for someone else is /onboarding-doc-builder, and the automatic repo-access welcome DM is /access-welcome.
---

# Team Intro

A chat overview of the team, its systems and what the Marketing OS can do, built live from
the repo so it is never staler than `main`.

**Done when:** the person asking can name their sub-org's head, find the system doc for the
thing they work on, and knows the one command to try first. Every fact in the answer comes
from a repo file, and each section says which file.

## What this skill does not do

- **Write an onboarding document** for a new hire (welcome letter, access checklist, first
  90 days). That is `/onboarding-doc-builder`.
- **Send the repo-access welcome DM** to new collaborators. That is `/access-welcome`, a
  scheduled routine.
- **Set up the repo** for a new team (`/setup`) or build a skill (`/agent-builder`).

## Sources

Read these, in this order:

1. `CLAUDE.md` - department table, systems list, task routing, workflow conventions
2. `references/team.md` - full roster with Slack IDs, GitHub logins, emails (the count of record)
3. `references/slack.md` - channel directory
4. `PHILOSOPHY.md` - how the team context works and why

Do not recall memories. Build the overview entirely from the repo files above. Never invent
a person, a reporting line, or a channel: if `references/team.md` does not list it, it is
not in the answer. If a file is missing or unreadable, skip its section and say which file
was missing, rather than filling it from general knowledge.

## Output

Five sections, always in this order. Scale depth to the question: "who's on the team" gets
section 1 in full and one line each for the rest.

1. **Who we are** - VP, the five sub-orgs with their heads and scope, headcount (from
   `references/team.md`). If the asker is in the roster, lead with their own sub-org.
2. **What we own** - owned systems vs reference systems, one line each, with the
   `systems/` path.
3. **How work moves** - the conventions a new person trips on first: tickets through
   `/pm-story`, data questions through `/rivermind:ask`, publishing a website is human-only,
   the three-stage writing pipeline.
4. **What Claude can do for you** - skill categories from the Task Routing table, with two
   or three commands picked for the asker's role.
5. **Start here** - `PHILOSOPHY.md`, then the system doc for their area, then the trainer
   link below.

End with a pointer to the self-guided Marketing Brain trainer for a guided, interactive
version of this overview (about 15 minutes, role-aware, ends with a routing check and your
first command): https://claude.ai/code/artifact/54f53531-5029-40bb-8cd7-d9d68943ede2
(source: `tools/marketing-brain-trainer/`).

## Example

Request: "I just joined the marketing team, what do you know about the team and the
systems we own"

Shape of the answer (content comes from the files, not from this example):

```
You are joining Abel's marketing org: five sub-orgs, <headcount> people (references/team.md).

Who we are
- Growth Marketing (Nir Taranto): SEO & AI Search, Paid, Creator, Marketing Ops, ...
- Brand (Raz Messing): ...

What we own (systems/owned/)
- hubspot - CRM and lifecycle automation
- ...

How work moves
- Need a task? /pm-story. Never call the monday API directly.
- ...

What Claude can do for you
- As a content marketer, try /nik-voice and /riverside-product-knowledge first.

Start here
1. PHILOSOPHY.md  2. systems/owned/<your area>.md  3. The trainer: <link>
```
