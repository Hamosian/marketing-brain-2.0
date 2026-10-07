---
name: minto-pyramid
description: The repo-wide structure standard for every answer, summary, report, brief, recommendation, status update, and analysis a person reads. Applies Barbara Minto's Pyramid Principle - open with the governing thought (the answer or the so-what), then 2-5 grouped supporting points of the same kind, logically ordered and MECE, each level answering the question the level above raises. Always on via the root file (CLAUDE.md, or AGENTS.md for Codex). Invoke directly to restructure a draft, check whether a summary buries the lead, build an executive summary or SCQA intro (situation, complication, question), or turn notes into a top-down argument. Trigger on "/minto-pyramid", "minto", "pyramid principle", "answer first", "bottom line up front", "BLUF", "buries the lead", "restructure this summary", "make this top-down", "exec summary structure", "SCQA", "MECE this", or "group these points". Sets the ORDER and GROUPING of ideas only - how sentences sound stays with nik-voice or ste, the verdict with critique.
---

# Minto Pyramid - answer first, then the support

Every answer in this repo is built as a pyramid. The top is one governing thought: the answer to the reader's question, or the so-what of the material. Beneath it sit a few supporting points. Each point is itself a small summary of what sits beneath it. The reader can stop at any level and still leave with the right conclusion.

This is Barbara Minto's Pyramid Principle (McKinsey, 1960s; *The Pyramid Principle: Logic in Writing and Thinking*). The deep reference, with the SCQA patterns, the ordering rules and the sources, is in `knowledge/pyramid-reference.md`. Load it when you build a long document, an executive summary, or a restructure the rules below do not settle.

## Why the repo runs on it

A reader takes in ideas one at a time and tries to find the relationship between them. Bottom-up writing (context, then data, then analysis, then the point) makes the reader hold every fact in memory and guess the conclusion. Top-down writing hands them the conclusion first, so every later sentence has a slot to land in. Busy readers (Abel, Nir, the leads, a colleague in a Slack thread) often read only the first line. The first line has to be the answer.

## Where it sits

This skill is always on. The always-loaded root file (`CLAUDE.md`, or `AGENTS.md` for Codex) carries the short rule; this file carries the method.

| Layer | Owner | Decides |
|---|---|---|
| Structure | `minto-pyramid` | Which idea goes first, how the rest group, in what order |
| Sound | `nik-voice` register, or `ste` for functional output | How each sentence reads |
| Clean | `de-ai` | AI tells removed |
| Verdict | `critique` | SHIP or REVISE. Its "Point first" dimension checks the top of the pyramid |

Minto is not a fourth pipeline stage. It is the skeleton the stage-1 writer fills. Build the pyramid, then write it in the right register.

## When it applies

Every piece of output where a person has to understand, decide, or act:

- An answer to any question asked in this repo, in chat or Slack
- Summaries: meeting notes, thread recaps, research, a link read, a document digest
- Reports, briefs, standups, status updates, 1-1 packs
- Recommendations, decision memos, trade-off analysis, budget asks
- Data answers (the governing thought is the finding, not the query)
- PR descriptions, handoffs, incident and failure write-ups

## When it does not apply, or bends

- **Creative and persuasive copy** (ad headlines, LinkedIn posts, landing pages, video scripts). Their register or skill owns the structure (`nik-voice`, `page-cro`, `script-doctor`, the `*-copytemplates` skills). A hook is not a governing thought.
- **Prospect email.** `inbound-demo-reply` PART 3 keeps its own rules. Do not restructure a prospect reply around this skill.
- **A skill with a fixed output schema** (`/chief-of-staff`, `/nir-mql-live-report`, `/mops-standup`, `/critique`, and the like). The schema keeps its section order. Apply the pyramid inside each section: every section opens with its own point. Where the schema has room above the first section, put a one-line bottom line there.
- **The user asks for a specific format** (a table only, raw steps, a verbatim quote). Give that format. Still open with one line that says what it shows, unless they asked for nothing else.
- **Code, config, and commit messages.** Out of scope, except that a PR description follows the pyramid.

## The three rules

Every pyramid must pass all three. They come straight from Minto.

1. **Ideas at any level summarize the ideas grouped below them.** A parent point states what its children add up to. "There are three problems with the funnel" is not a summary; it is a count (Minto calls this an "intellectually blank" statement). "The funnel leaks at demo booking, not at signup" is a summary. The fix depends on the group: for a group of actions, state the result they achieve together; for a group of facts or findings, state the inference they support.
2. **Ideas in each group are the same kind of idea.** All reasons, or all steps, or all problems, or all recommendations. If one item could not share a plural noun with its siblings ("three reasons", "four steps"), it belongs somewhere else.
3. **Ideas in each group are in a logical order.** Minto says there are only four, and you should be able to name which one you used. The order follows from how the group was made:
   - **Time** (chronological): steps in a process, sequences, cause then effect.
   - **Structure** (spatial): the parts of an existing whole, such as a funnel stage by stage, or team by team.
   - **Degree** (comparative, ranking): like things classed together, most important or largest first.
   - **Deduction** (argument): statement, comment, therefore. Use it sparingly (see below).

## The two directions of logic

**Vertical: the question-answer dialogue.** Every statement raises a question in the reader's head: Why? How? How do you know? What should we do? The level directly below answers exactly that question, and nothing else. If a child point answers a question the parent did not raise, it is in the wrong place.

**Horizontal: how siblings relate.** A group is either:

- **Inductive** (preferred for the key line): parallel points of the same kind that together support the parent. Each stands alone. The reader can accept two of three and still move. At the key line, present the action before the argument.
- **Deductive**: a chain (this is true; this is also true; therefore). The reader must hold every link to reach the end, and one broken link breaks the conclusion. Keep a deductive chain to about four steps, and prefer to put it lower in the pyramid, not at the top.

**MECE.** Every group should be Mutually Exclusive (no overlap between points) and Collectively Exhaustive (together they fully answer the question the parent raised, with no gap). Overlap means you are counting one idea twice. A gap means the parent claims more than the children prove.

**Size.** Two to five points per group. One point is not a group: merge it into the parent. More than five usually means two groups mixed together, or the list has not yet been thought through into a summary. The limit comes from working memory: readers can hold only a handful of separate items, so they need the grouping done for them.

**Parallel form.** Siblings share a grammatical shape: all full-sentence claims, or all verb-first actions. A list that mixes "Raise the bid cap", "CPC trends" and "We should test video" is three kinds of idea wearing three shapes.

## Method

Run this before writing any answer longer than one sentence. For a short reply it takes seconds and happens in your head.

1. **Name the reader and their question.** Who reads this, and what do they need to know or decide? If the question is not explicit, infer it from the situation (a status request asks "are we on track, and what do you need from me?").
2. **Write the governing thought first.** One or two sentences that answer that question. It must be a claim someone could disagree with, not a topic. "Q3 paid search is on track, but brand CPC rose 18% and needs a bid cap this week" is a governing thought. "An update on paid search" is a label.
3. **Decide whether the reader needs an introduction.** For most chat and Slack answers, no. For a document or memo, write a short SCQ lead-in (Situation, Complication, Question) when the reader needs context, ending on the question the governing thought answers. For an upward brief (Abel, Nir, a decision memo), put the governing thought first and add SCQ context after it only if needed: the Direct order (A, S, C). Either way, the context holds only what the reader already accepts as true, plus the change that makes the question live. No new facts, no data, no argument. Patterns in `knowledge/pyramid-reference.md`.
4. **Write the key line.** The 2-5 points that directly support the governing thought. Check them against the three rules: each summarizes its own support, all are the same kind, and they sit in a nameable order. Check MECE against the question the governing thought raises.
5. **Fill each point's support the same way.** Evidence, figures, examples, links. Figures carry their source and as-of date (`references/evidence-standards.md`). Stop at the level of detail the reader needs to act.
6. **End on the ask or the next step, if there is one.** Who does what by when. If nothing is needed from the reader, say nothing: no closing summary that repeats the top.
7. **Run the tests below.** Fix and ship. Do not narrate the structure to the reader ("First, I will cover...").

**When the answer is not known yet**, the governing thought still comes first. State what is known, what is missing, and how to get it. "We cannot say yet whether the new form lifted demos: the change went live Tuesday and we need 14 days of data. First read on 2026-10-09." is a pyramid. A page of partial findings with no top is not.

**Top-down or bottom-up.** If you know the answer, build top-down: governing thought, then the question it raises, then the key line. If you only have material (notes, a transcript, a data dump), build bottom-up: list every point, group the ones that are the same kind, write what each group adds up to, then ask what those summaries add up to. That last summary is the governing thought. Either way, the reader sees the result top-down.

## Output shape by size

Scale the pyramid to the output. The structure is the same at every size; only the depth changes.

| Size | Shape |
|---|---|
| **One fact** | The answer in one sentence. Add one line of support only if the reader would otherwise ask "how do you know?". |
| **Chat or Slack reply** (about 5 lines) | Line 1 is the governing thought. Lines 2-4 are the key line, one short sentence each, or a 2-4 item list. Last line is the ask or the link. No headers. The Slack-brevity rule in the root file still holds: depth goes to a DM. |
| **Summary, brief, report** | A bold bottom line (1-2 sentences) at the very top. Optional 2-3 line SCQ context if the reader needs it. Then one section per key-line point, each headed by the point itself as a full sentence, with its support beneath. Close with decisions needed or next steps. |
| **Long document or deck** | SCQA introduction, governing thought, then each key-line point as a section that is its own mini-pyramid. The executive summary is the top two levels of the pyramid and nothing else. On a deck, each slide title is the point of that slide. |

## Headings are ideas, not labels

A heading or a slide title states the point of the section, so a reader who skims only the headings gets the argument.

| Label (never) | Idea (always) |
|---|---|
| Findings | Demo bookings fell because the calendar step loses 40% of visitors |
| Background | We moved the form to Chili Piper in August |
| Key takeaways | Two fixes recover most of the drop |
| Next steps | Hanan ships the calendar fix by Friday; Nir approves the test budget |
| Summary / Overview | (delete it: the top of the page is already the summary) |

Figures in the examples above are illustrations of the pattern, not data.

## Tests before it ships

Run these on the draft. One failure means restructure, not reword.

1. **Stop test.** If the reader reads only the first sentence, do they have the answer? If not, move the answer up.
2. **Question test.** For each point, what question does it raise? Does the level below answer that question, and only that one?
3. **Summary test.** Does each parent state what its children add up to, rather than announce that they exist ("There are three issues")?
4. **Same-kind test.** Can the siblings share one plural noun (reasons, steps, risks, options)?
5. **Order test.** Can you name the order: time, structure, degree, or deduction?
6. **MECE test.** Any overlap between siblings? Any gap between the siblings and the parent's claim?
7. **Count test.** Between 2 and 5 points per group?
8. **Heading test.** Would the headings alone tell the story?
9. **No-repeat test.** Nothing at the end restates the top. The end is the ask, or it is nothing.

## Example

**Question from Nir:** "How did the webinar do?"

**Before (bottom-up):**
> We ran the webinar on Tuesday with two speakers. Registration opened three weeks ago and we promoted it in two newsletters and on LinkedIn. 412 people registered and 171 attended, which is 42%. Our usual rate is about 35%. 23 attendees booked a demo afterwards. The LinkedIn posts drove most registrations. Overall it seems like it went well and we could consider doing more.

**After (pyramid):**
> **The webinar beat our benchmarks, and LinkedIn is the channel to scale for the next one.**
> - **Attendance was above normal:** 171 of 412 registrants attended (42%, against our usual 35%).
> - **It produced pipeline:** 23 attendees booked a demo within the week.
> - **LinkedIn drove most registrations,** ahead of both newsletter sends.
>
> Ask: approve a LinkedIn-first promo plan for the October session by Thursday.

The figures are illustrative. In a real answer each one carries its source and as-of date.

What changed: the verdict moved to line 1. The support became three points of the same kind (results), in degree order. The vague close ("we could consider doing more") became a specific ask.

## Done when

- The first sentence answers the reader's question or states the so-what.
- Every group passes the three rules and the MECE check, with 2-5 points.
- Every heading states an idea.
- The output ends on an ask or next step, or ends cleanly with no repeated summary.
- A fixed skill schema, a requested format, and the creative-copy and prospect-email carve-outs above were respected.
