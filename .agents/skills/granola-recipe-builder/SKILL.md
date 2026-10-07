---
name: granola-recipe-builder
description: Use this skill when the user wants to create, craft, or improve a Granola recipe (a reusable prompt template for meeting notes/summaries in Granola AI). Interviews the user with structured questions, classifies the recipe type, then generates a recipe name plus a ready-to-paste recipe prompt built on Granola's own three-part framework. Triggered by "granola recipe", "build a granola recipe", "make me a meeting summary recipe", "craft a granola recipe", "new granola recipe", "granola recipe classifier", or any request to turn a meeting-notes need into a reusable Granola prompt.
---

# Granola Recipe Builder

Turn a vague "I want better meeting notes" into a named, ready-to-paste Granola recipe. A Granola recipe is a reusable prompt template that processes meeting data (transcript + notes) to produce a consistent output without re-explaining context each time. This skill interviews the user, classifies what they need, and generates the recipe using Granola's own best-practice framework.

**Source of truth for the framework:** Granola's "Writing effective recipes" guide (https://docs.granola.ai/help-center/getting-more-from-your-notes/writing-effective-recipes). The principles below are distilled from it - you do not need to fetch the page each run, but you may if you want to confirm current guidance.

## The framework this skill applies (from Granola)

Every recipe you generate must follow Granola's three-part structure:

1. **Define the job (jobs-to-be-done).** Open by stating why the request exists and what the output is for. Example: "A meeting has just finished and I need to send a follow-up email. Your job is to write a professional follow-up that summarizes decisions and next steps."
2. **Add guardrails (treat the AI like an intern).** Spell out the rules. Do not assume unstated knowledge. Tell it what not to invent and what to do when something is ambiguous.
3. **Include context once.** Embed the reusable facts - company, role, colleagues, systems, projects - so they never have to be retyped per meeting.

Plus these best practices:

- **Show the format.** If output consistency matters, give the exact sections/headings or an example template. Don't describe the format in the abstract.
- **Longer beats shorter.** Detailed prompts produce more consistent results. Do not over-trim a recipe to look clean.
- **Iterate with preview.** Tell the user to run it on 2-3 real meetings using Granola's preview, then report what looked wrong so a rule can be tightened.
- **Model choice.** Standard models for quick tasks (follow-ups, to-do lists); thinking models for complex documents (PRDs, strategic analysis).
- **Granola only sees meeting data.** No email, Slack, tasks, or prior meetings unless it is a multi-meeting recipe scanning a folder/person view. Always add a guardrail forbidding reference to context it cannot see.

## Recipe types (classify first)

- **Single-meeting recipe** - runs on one meeting. Use for summaries, follow-up emails, "what did I miss", action-item extraction, bug reports.
- **Multi-meeting recipe** - runs across a folder or a person view. Use for weekly rollups, "all my 1:1s with X", cross-meeting pattern/theme analysis, pipeline or project status across calls.

## Step 1: Interview the user

Use `AskUserQuestion` to run a short structured interview. Ask in one or two batches - do not drip questions one at a time. Adapt the options to what the user already told you (if they already said "weekly rollup", you know it's multi-meeting - skip that question).

Ask these dimensions:

1. **Scope** - single meeting or multiple meetings? (skip if already obvious from their request)
2. **Purpose** - personal recall / forward to colleagues as-is / feed into a downstream tool (Monday, HubSpot, email) / all of the above. This drives how strict the structure and owner/date precision must be.
3. **Meeting types** - which meetings this recipe assumes (internal ops/marketing syncs, cross-functional, 1:1s, external/vendor). This shapes the embedded context and any privacy handling for 1:1s.
4. **Sections / output shape** - which sections they want (e.g. TL;DR, Decisions, Action items, Open questions/risks, Context worth keeping) OR, for non-summary recipes, what the single output is (follow-up email, to-do list, PRD, etc.).
5. **Length / detail** - tight / balanced / thorough. Reference Granola's note that longer prompts are more consistent, so "tight" still means complete, just terse.
6. **Tone / audience** - default to the user's saved style if known (for Hanan: no em dashes, no exclamation marks, sentence case headings, concise, Riverside brand). Confirm rather than assume if it's a new user.

Follow threads. If an answer reveals something specific (a named recurring meeting, a downstream board, a boss who receives the notes), fold it into the embedded context.

## Step 2: Gather the "include once" context

Before generating, assemble the reusable context block. Pull from what you know about the user and the repo:

- Read `references/team.md` for the user's role, manager, and org placement if you need names/titles.
- Common Riverside systems that surface in meetings: HubSpot (CRM, Pre-Ops, pipeline), Omni BI + Snowflake (reporting), Monday (task boards), Mixpanel, Slack.
- If the recipe feeds a downstream tool, name it in the context so owner/date formatting matches (e.g. "action items may become Monday tasks, so format each as Owner - task - due date").

Only embed context that is stable and reusable. Do not embed this-meeting specifics.

## Step 3: Generate the recipe

Produce two things:

### A. A name

Short, describes the output, reads well in Granola's recipe list. Patterns that work:
- `Meeting summary (ops)`
- `Ops meeting summary`
- `Weekly 1:1 rollup`
- `Follow-up email`
- `Action items to Monday`

Suggest one primary name and 2-3 alternatives, then let the user pick or override.

### B. The recipe prompt

Assemble it in the three-part order (job -> context -> format -> guardrails). Deliver it in a fenced code block so the user can copy it straight into Granola. Rules for the body:

- Start with "Your job:" and the jobs-to-be-done framing.
- Include the reusable context as a labeled block the model is told to use but not restate.
- If the output is a structured summary, specify the **exact section headings** the user chose and one line on what each contains. Tell it to write "None" for empty sections rather than padding.
- For action items, when the recipe feeds a tool, mandate `Owner - task - due date (only if a date was stated)` and `Owner: unassigned` when none was named.
- Always include the core guardrails: do not invent owners/dates/metrics/decisions; write "unclear" when ambiguous; only use this meeting's data; obey the user's style rules (for Hanan: no em dashes, no exclamation marks, sentence case headings, concise, no editorializing).
- For multi-meeting recipes, adjust: the job references scanning a collection, and add a rule to group or attribute findings by meeting/person and to surface cross-meeting patterns.

## Step 4: Explain the key choices and how to test

After the recipe, add 3-4 short notes:
- Why the guardrails / do-not-invent rule matter (Granola will otherwise fill gaps with plausible fiction, which breaks anything you forward or paste into a task).
- The "Granola only sees the meeting" limitation and how the recipe handles it.
- Tell them to run it on 2-3 recent meetings via preview and report what looked off so a rule can be tightened.
- Note model choice if the recipe is complex (suggest a thinking model).

## Step 5: Document it in the repo (and let the wiki auto-sync)

Recipes the user builds are worth keeping so the team can reuse and improve them.

1. Append the finished recipe to `references/granola-recipes.md` (create the file with a short intro if it does not exist). Each entry: a `##` heading with the recipe name, a one-line "when to use", the recipe type (single/multi), and the recipe prompt in a fenced code block.
2. If this is the first recipe, add a row to the Reference Files table in `CLAUDE.md` pointing to `references/granola-recipes.md`.
3. Open a PR (branch `granola-recipe/<slug>`). On merge, the Wiki + Graph Sync workflow regenerates the wiki page automatically - you do not hand-write the wiki (see `docs/wiki-sync-automation.md`).

Ask the user before committing/opening the PR. If they only wanted the recipe text for personal use, skip the repo step and just hand them the copy-paste block.

## Key principles

- **Classify before you write.** Single vs multi meeting changes the whole prompt. Purpose changes how strict the structure is.
- **Framework, not vibes.** Every recipe follows Granola's job -> context -> format -> guardrails order. That's what makes them consistent.
- **Guardrails are the highest-leverage part.** The do-not-invent rule is what separates a forwardable summary from confident fiction.
- **Show the format, don't describe it.** Exact headings beat adjectives.
- **Reuse the user's style.** Never emit em dashes or exclamation marks for Hanan; keep headings sentence case.
- **Repo over one-off.** Offer to save every recipe to `references/granola-recipes.md` so the whole team benefits.
