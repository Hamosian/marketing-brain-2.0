---
name: ste
description: Rewrite operational, functional answers in ASD-STE100 Simplified Technical English so they read clear, direct, and unambiguous instead of like AI slop. Use for non-content output - status updates, task summaries, data answers, analysis, decisions, plans, Slack ops messages, briefs, how-to steps, and any reply where clarity beats warmth. Trigger on "/ste", "use STE", "use ASD-STE100", "deslop this", "say it plainly", "make this clearer", "cut the fluff", "just the facts", or when the user asks for a de-slopped functional answer. Do NOT use for marketing copy, LinkedIn posts, emails to prospects, creative writing, or any external-facing content - those go through brand-voice, then de-ai and critique.
---

# STE - Simplified Technical English for functional answers

This skill makes Claude answer like a technical manual writer, not a chatbot. It applies ASD-STE100 (Simplified Technical English), the international standard used for aerospace and defense documentation. The result is clear, short, and unambiguous.

It exists to fill a gap the `brand-voice` registers do not cover. Those make writing warm and human, which is correct for marketing copy. This skill does the opposite: it strips writing down to plain, controlled instructions, which is correct for operational output.

**It replaces stage 1, not the pipeline.** When the output goes to another person, run `de-ai` and then `critique` after this skill, exactly as any `brand-voice` register would. Plain does not mean exempt: a status update can read like a machine wrote it. Only output the author alone reads stops here.

## When to use it

Use STE for **non-content, functional output**:

- Status updates, standups, task summaries, ledgers
- Data answers and analysis writeups
- Decisions, trade-offs, recommendations
- Plans, runbooks, how-to steps, SOPs
- Internal Slack operations messages
- Chief-of-staff style briefs and "what needs your attention" summaries

## When NOT to use it

Do **not** use STE for anything external-facing or creative. STE reads cold. That is a feature for a runbook and a defect for a prospect email.

Route these to the normal pipeline instead (`brand-voice`, then `de-ai`, then `critique`):

- Marketing copy, landing pages, ad copy, headlines
- LinkedIn posts, social content, newsletters
- Cold or nurture emails, prospect replies
- Any creative or brand writing

If a request mixes both (for example "analyze this campaign and draft the LinkedIn post"), apply STE to the analysis and the normal pipeline to the post. Say which part got which.

## The rules

Apply these ASD-STE100 writing rules to the answer.

**Vocabulary**
1. One word, one meaning. Use each word with a single meaning across the answer.
2. One meaning, one word. Do not call the same thing by two different names.
3. Use simple, common words. Replace jargon and long words with short approved ones (use "start" not "initiate", "use" not "utilize", "about" not "approximately", "help" not "facilitate").
4. Use a word only as the part of speech it normally is. Do not verb a noun.
5. No idioms, slang, or metaphor. Say the literal thing.

**Sentences**
6. Keep instructions to a maximum of 20 words. Keep descriptive sentences to a maximum of 25 words.
7. One instruction per sentence. Do not chain steps with "and" or "then".
8. Use the active voice. Name who does the action.
9. Use the imperative for instructions ("Set the status to done", not "The status should be set to done").
10. Use simple tenses. Prefer present and past. Avoid perfect and progressive forms.
11. Do not use the -ing form to join ideas or as a noun. Split into separate sentences.
12. Do not drop words to look terse. Keep articles (a, an, the). Telegraphic text is banned.

**Structure**
13. Put the main point first. State the answer, then the support. How the support groups and orders is `minto-pyramid`; this skill writes the sentences inside that structure.
14. Use a numbered list for a sequence of steps.
15. Use a bulleted list for a set of items with no order.
16. Use a table when you compare items across the same fields.
17. Keep a paragraph to 6 sentences or fewer.
18. Be specific. Give the number, the name, the date. Do not write "several" or "soon". Take every number, name and date from the source you were given. If the source does not have it, write that it is not known. Never invent a value to obey this rule.

**Slop to cut**
19. Delete "It's not X, it's Y" constructions, meta-commentary, and hype adjectives.
20. Delete throat-clearing openers ("Great question", "Certainly", "I'd be happy to").
21. Delete filler ("in order to" -> "to", "at this point in time" -> "now").
22. No em dashes. Follow the standing house style.

## Method

1. Write or take the functional answer.
2. Pass it through the rules above.
3. Read each sentence. If it breaks a rule, rewrite it.
4. Cut every word that does not carry meaning.
5. Return the clean version only. Do not narrate the edit unless asked.

**Done when:** every sentence passes the 22 rules, the main point is the first sentence, and every figure in the text is traceable to the input. If the output goes to another person, it goes to `de-ai` next.

## Example

**Before (default):**
> Great question! So, digging into the numbers a bit, it looks like we're seeing a fairly meaningful uptick in demo requests this week - roughly speaking they're up quite a lot compared to last week, which is really encouraging and suggests our recent efforts might be starting to pay off in terms of pipeline generation.

**After (STE):**
> Demo requests rose this week. This week: 47 requests. Last week: 31 requests. That is a 52% increase. The rise started on Monday, after the new paid campaign went live.

## Where this sits in the pipeline

Graduated. `CLAUDE.md`'s content-pipeline directive now routes functional output here by default, and this skill stands in for a `brand-voice` register at stage 1.

**It is not an exit from the pipeline.** Functional output that another person reads still goes on to `de-ai` and then `critique`. Only output the author alone reads stops at this skill. The test is who reads it, not what kind of writing it is.
