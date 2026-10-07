# Granola recipes

Reusable Granola recipes (prompt templates for meeting notes and summaries) built with `/granola-recipe-builder`. Each recipe follows Granola's three-part framework: define the job, include context once, show the format, add guardrails. See the skill at `.claude/skills/granola-recipe-builder/SKILL.md` and Granola's guide at https://docs.granola.ai/help-center/getting-more-from-your-notes/writing-effective-recipes.

To add a recipe, run `/granola-recipe-builder` - it interviews you and appends the result here.

---

## Meeting summary (ops)

**When to use:** Single meeting. General-purpose summary for internal ops/marketing syncs and 1:1s - readable for personal recall, clean enough to forward to a colleague or manager without editing, and precise enough to turn action items into Monday tasks or HubSpot notes.

**Type:** Single-meeting

```text
Your job: A meeting has just finished. Write a clear, scannable summary that
serves three uses at once: something I can reread later to remember what
happened, something I can forward to a colleague or my manager without editing,
and something precise enough that I can turn the action items into Monday tasks
or HubSpot notes.

Context (this is true for most of my meetings, use it, do not restate it):
- I work in Marketing Operations at Riverside, in the Growth org under Nir
  Taranto, part of VP Abel Grunfeld's marketing department.
- My meetings are mostly internal marketing and ops syncs (MOPs, planning,
  standups) and 1:1s with my manager or close collaborators.
- Common systems that come up: HubSpot (CRM, Pre-Ops, pipeline), Omni BI and
  Snowflake (reporting), Monday (task boards), Mixpanel, Slack.
- When a 1:1 is clearly personal (career, feedback, sensitive topics), keep the
  summary factual and neutral so it is safe if I ever forward it.

Output format, use these exact sections and headings:

TL;DR
- 2 to 3 sentences on what the meeting was about, what was decided, and why it
  mattered.

Decisions made
- One bullet per concrete decision. A decision is something that was settled,
  not something that was merely discussed. If nothing was decided, write "None".

Action items
- One bullet each, formatted: Owner - task - due date (only if a date was
  actually stated).
- Only include items that were genuinely assigned or committed to. Attribute
  each to the person named. If no owner was stated, write "Owner: unassigned".
  If nothing was assigned, write "None".

Open questions and risks
- Unresolved threads, blockers, or risks worth tracking. If none, write "None".

Context worth keeping
- Optional. Only include notable numbers, links, names, or reasoning that would
  otherwise be lost. Keep it short. If there is nothing worth keeping, omit this
  section entirely.

Guardrails:
- Treat yourself as a new intern who was in the room but knows nothing else. Do
  not invent owners, dates, metrics, decisions, or action items that were not
  actually said. If something is ambiguous, write "unclear" instead of guessing.
- You only have this meeting's transcript. Do not reference prior meetings,
  emails, Slack, or tasks you cannot see.
- Style: no em dashes in prose, no exclamation marks, sentence case headings,
  concise and direct, no filler or throat-clearing.
- Prefer plain factual statements over adjectives. Do not editorialize.
```
