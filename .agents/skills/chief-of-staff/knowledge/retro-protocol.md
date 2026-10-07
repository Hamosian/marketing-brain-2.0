# Retro protocol - how the brief learns what Nir wants

Loaded by `/chief-of-staff` on every run (Step 8). Nir asked on 2026-09-14 for the
chief of staff to "learn what I want and expect from it", with a retro each run
that adjusts the next brief and asks questions to understand better. He left the
timing to the skill. **Decision: the retro runs at the end of each run, after the
packs, not the morning after.** At the end of a run every source is fresh, Nir is
in the chat, and his reactions to today's brief are the evidence. A morning-after
retro asks about yesterday cold.

Two files carry it. `data/retro-log.md` is the raw record: every question asked,
every answer, every implicit signal. `knowledge/nir-preferences.md` is the
distilled rulebook the brief obeys, read at the start of **every** run before
anything renders. The log is evidence; the preferences file is law.

## Signals (collected every run, no questions needed)

1. **Action rows acted on vs ignored.** Diff yesterday's `.claude/skills/growth-marketing-team-tasks/data/today-actions.md`
   against today's sources. A row Nir acted on (replied, sent, decided) confirms
   the row type. A row carried three runs with no action is a candidate for
   "drop, park, or keep?".
2. **Pack edits.** Every cut and add in `data/1-1-pack-log.md`. Owned by
   `knowledge/1-1-pack.md`; the retro only reads the totals.
3. **What he asked for by hand.** Anything Nir requested in chat during or after
   a brief that the brief did not offer ("give me the Slack link", "who is waiting
   on this", "what did I promise Hanan"). The strongest signal: it names a gap.
4. **Sections he never reacts to.** A section untouched for five runs (no reply,
   no follow-up, no reference to it later) is a candidate to shrink or drop.
5. **Corrections.** Any "no", "wrong", "that's done", "not mine" in his replies.
   Each is a row in the log the same day, with the rule it implies.

## Questions (max two per run, only with a signal behind each)

Ask at the end of the run, after the packs, in one short block. Each question is a
**concrete choice about a specific item or section**, never "how was the brief".
Examples of the right shape:

- "The Fame agreement row has sat 3 runs. Drop it, park it to a date, or keep it?"
- "You cut Erika's report line twice. Leave report numbers out of all packs, or
  only hers?"
- "You asked for the Gmail link on two rows yesterday. Make the Links column
  always carry email plus Slack when both exist?"
- "Waiting on your reply has had no reaction for a week. Fold it into the action
  table, or keep it separate?"

Rules:
- **Zero questions is a normal day.** No signal, no question. Never pad.
- **Never ask the same question twice.** An unanswered question is logged
  `unanswered` and returns once more, a week later, phrased as a default: "I will
  drop X unless you say keep."
- **Use `AskUserQuestion`** so answers are one click. Always offer "leave it as
  is". Put the recommended option first.
- **Nir can volunteer.** Anything he says about the brief itself, at any point in
  the session, is logged as a `stated` signal with his words.

## Promotion: from log to preferences

- **Stated once → rule.** If Nir says how he wants something, it is a rule today,
  quoted, dated.
- **Implicit signal twice → rule.** Two occurrences of the same implicit signal
  (two ignored rows of one type, two asks for the same missing thing) become a
  rule marked `inferred`, and the next run's retro confirms it with one question.
- **Rule proven wrong → removed**, with a dated note in the log. Never patch a
  rule into a longer rule; replace it.
- **Rule stable two weeks → promote into `SKILL.md`** as skill text, and mark the
  preferences row `promoted` with the date. The preferences file stays short by
  design; it is the queue for what becomes permanent, not a second skill.

## Rendering

At the very end of the run, after the packs and the suggested actions:

```text
## Retro
- Adjusted for tomorrow: [one line per change made to nir-preferences.md today, or "nothing new"]
- [Question 1, via AskUserQuestion]
- [Question 2, if any]
```

Under 60 words of prose plus the questions. When there is nothing adjusted and no
question, the section is one line: "Retro: nothing new today." That single line is
the one empty-section exception in this skill besides the empty Act lane, because
Nir asked for the retro to exist every run and should see that it ran.

## What the retro is not

- It is not Sharpen. Sharpen (Sunday) coaches how Nir works with the whole
  system. The retro tunes this brief and nothing else.
- It is not a satisfaction survey. No ratings, no "was this useful".
- It does not touch the team ledgers or the 1-1 rules. Those have their own loops
  (FEED mode, `knowledge/1-1-pack.md`). The retro reads their logs and can point
  at them; it does not edit them.
- It never grades Nir. The subject is the brief.
