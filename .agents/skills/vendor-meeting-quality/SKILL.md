---
name: vendor-meeting-quality
description: >
  Scores every appointment-setting vendor brief (Ziff Davis / SWZD lead handover today,
  MemoryBlue and Boscia later) against Riverside's qualification gates before the meeting,
  reads the outcome after it, and turns the gap between the two into feedback the vendor can
  act on. Four verbs: `score` a new brief (0-100, Green / Amber / Red, hard flags, the one
  question the vendor should have asked), `outcome` the first morning after the meeting
  (Gong brief plus Pre-Op stage, was the score right), `digest` on Fridays (the week's table,
  drafted for Nir to send), `calibrate` monthly (precision of each verdict, reweight in batches
  of 20, renewal numbers). Called from `inbound-demo-reply` Step 3.5; also on demand.
  Trigger on: "score this Ziff lead", "score the LHO", "is this vendor meeting worth taking",
  "Ziff lead quality", "vendor meeting quality", "was the Ziff score right", "Ziff feedback
  for Charles", "Ziff Friday digest", "calibrate the Ziff rubric", or "/vendor-meeting-quality".
---

# Vendor meeting quality

A vendor bills $750 for a held meeting, not a qualified one. The only levers we hold are the mix of who gets booked and the case we bring to the renewal. Both need the same thing: a score written **before** the meeting, an outcome written **after** it, and the difference sent back to the vendor in a form they can act on.

**Done when:** every new brief has a ledger row with a score and a verdict on the day it arrives, every held meeting has a next-day label within one working day, the Friday digest is drafted for Nir by the Friday morning run, and the monthly calibration says whether the rubric is getting better at predicting the next-day label, with numbers.

## Rollout, in two phases (set by Nir, 2026-09-19)

**Phase 1, now: Nir only.** The flag, the reasons and the score print in the daily report (section 6) for every new brief, and the next-day outcome and right/miss print there as they land. Nothing goes to the vendor or the AE. This holds for the first 20 new-format briefs (18 September onward), so Nir can watch the flag against real outcomes and tweak the rules. The ledger's `feedback_status` stays `phase 1: Nir only` on every row.

**Phase 2, on Nir's word only.** Once he says the flag is good enough, each new brief gets a reply on its LHO thread **to Charles Green with the Ziff cc (Simon Potton, Andrew Rourke), never to the AE**, carrying the flag, the reasons quoted from the brief, and the score. Drafted through `nik-voice` (internal-ask register), `de-ai`, `critique`, shown to Nir, sent by Nir unless he says otherwise. Phase 2 does not start on a date or a count; it starts when Nir says so, and the switch is recorded here.

## Who reads what

- **Nir only:** the score, the reasoning, the ledger, the calibration memo. Plain language, `ste` register.
- **The vendor (Charles Green, cc Andrew Rourke, Simon Potton):** only what Nir asks to have written, and only he sends it. The run never drafts vendor messages on its own initiative. When asked: `nik-voice` (internal-ask register: state the fact, ask the question, stop) then `de-ai` then `critique`.
- **Not the AE, not HubSpot, for now.** Extending the audience is a Nir decision after the first calibration batch.

## Sources, and the one that is not available

| Input | Where | Notes |
|---|---|---|
| The brief | LHO email body from `charles.green@swzd.com` (subject `Lead Handover Information for the meeting with …` since 2026-09-18; `LHO for the meeting with …` before) | The body is the brief. Charles sends every handover in the email body. A brief that arrives only as an attachment is not scored: flag it to Nir in section 6 as `brief not in body` so the ask goes back to Charles. |
| Contact, tags, meeting record, prior opps | HubSpot, already pulled by `inbound-demo-reply` Step 3.5 | Do not re-pull. Take the contact id, meeting date, AE and verdict from the LHO Log row. |
| Next-day outcome | Gong `SPOTLIGHT_BRIEF` in `ANALYTICS.STG.STG_GONG__CALLS`, found by the prospect's email in `STG_GONG__CONVERSATION_PARTICIPANTS`; Pre-Op `dealstage` on the deal associated with the contact | Query pattern in `gong-calls-explorer`. Pull the brief, never the transcript, unless the label is genuinely unclear from the brief. |
| Day-30 and final outcome | Pre-Op stage, and any sales-pipeline deal on the contact or company | Stage classes in `knowledge/baseline-2026-09.md`. |
| Rubric | `rubric.md` in this directory | The only place weights live. |
| Ledger | `data/ziff-scores.csv` | One row per brief. Append on `score`, update in place on `outcome`. |
| Changes to the rubric | `data/calibration-log.md` | Every reweight, with the batch that justified it. |

## `score` - run on every new brief, the morning it arrives

1. **Read the whole body.** Extract: company, size, country, prospect name and title, meeting date, AE, and the answers to the three agreed questions (what they record now or within 90 days; what they use today and whether they've looked at Riverside; who owns the tools and how many people produce). Quote the brief, do not paraphrase it into what you expected to find.
2. **Check brief compliance, for briefs dated 18 September 2026 or later only.** The three agreed questions did not exist before that, so older briefs are history to learn from, never compliance to grade. Any of the three answers missing is noted as `the brief did not say`, and it is the cheapest thing for the vendor to fix. It does not by itself change the score.
3. **Apply the flag rules** (Output schema below): buyer title, owner and team named, off-fit problem, self-serve profile. Quote the line of the brief that fired each one.
4. **Score the five components** per `rubric.md` as supporting detail: programme fit 35, incumbent 20, owner and team 25, budget 10, persona and size 10. Write the sub-scores.
5. **Write the one question.** The single question the vendor should have asked, or the answer that would have changed the verdict. One sentence. This is what the vendor feedback is built from, so it names a behaviour, not a company type ("when they say planning, get the first date and the host" beats "don't book print companies").
6. **Append the ledger row** with `flag`, `flag_reasons`, `score`, `verdict`, sub-scores, `missing_question`, and the meeting date. Leave the outcome columns empty.
7. **Return** the block in the schema below to the caller. Do not draft anything for the vendor; feedback is produced by `digest` and `calibrate` only when Nir asks for it.

**Defaults when the brief is silent.** Unknown incumbent = 10 of 20. Unknown team size = 5 of 10. Unknown budget = 4 of 10. Silence is not a pass and not a fail; it is the vendor's job to fill, and it goes into the feedback.

**Do not score from the tracker, the contact record, or the Gong call.** The score measures what the vendor knew and told us before the meeting. Anything learned on the call belongs in `outcome`.

## `outcome` - first morning run after the meeting date

Runs for every ledger row whose meeting date has passed and whose `next_day_label` is empty. A meeting on the run date is not due; it is due the next morning (same rule as the LHO re-surface hold).

1. **Meeting status** from the HubSpot meeting record: held, no-show, rescheduled, cancelled. No-show or cancelled: write it, leave the label empty, stop. Rescheduled: move the meeting date, stop.
2. **Gong brief** for the call (prospect email in participants). If Gong has no call, say so in `next_day_source` and label from the Pre-Op stage only.
3. **Label** exactly one of:
   - `qualified`: a live or dated recording programme that fits, the owner on the call or named and engaged, budget or a timeline this financial year, a next step booked.
   - `weak`: a fitting programme but one blocker the AE cannot remove on the first call: budget next FY, not the owner, incumbent locked, one-person team.
   - `unqualified`: no fitting programme, an off-fit problem, a self-serve profile, curiosity, or the prospect did not know what the meeting was.
4. **Day-30 and final** columns fill later: Pre-Op stage at day 30, then promoted / closed lost / won.
5. **Was the score right.** Write one of:
   - `right`: Green and `qualified` or promoted; Red and `unqualified` or closed lost within 14 days; Amber and `weak`.
   - `miss-high`: Green but `unqualified`. The rubric was too generous. Name the component that over-scored.
   - `miss-low`: Red but `qualified` or promoted. The expensive miss: it is the one that costs the rubric its credibility with the vendor and with Nir. Name the component.
   - `early`: no label yet, or the label and the score disagree in a way day 30 will settle (Green and `weak`).
6. Update the row in place. Never append a second row for the same brief.

## `digest` - Friday morning run, drafted for Nir

One table, the week's briefs: company, title and size, score and verdict, the flag or missing question, what the AE found (for meetings already held), and the one change. Below it, two numbers: briefs this week that carried all three answers, and the booked-to-`qualified` rate for meetings held this week. Then one paragraph, at most three sentences, naming the single pattern to fix next week.

Prepared as a table in the daily report under section 6 for Nir only. **Nothing is written for the vendor unless Nir asks for it** (per Nir, 2026-09-19); when he does, it goes through `nik-voice` (internal-ask register), `de-ai`, `critique`, and he sends it.

## `calibrate` - first morning run of the month, or on demand after every 20 outcomed rows

Nir-only memo, `ste` register. Contents, in this order:

1. Rows outcomed this batch, and cumulative.
2. Precision of each verdict: of the Greens, how many `qualified`; of the Reds, how many `unqualified`. Base rate to beat: 10 of 67 held meetings promoted between February and August 2026 (15%), 5 won.
3. `miss-high` and `miss-low` counts, and the component named most often in each.
4. **Reweight only when one component is named in three or more misses in the same direction inside one batch.** Change that component's weights, log before and after in `data/calibration-log.md`, and re-score nothing retroactively (old rows keep the rubric version that scored them; the ledger carries `rubric_version`).
5. Vendor behaviour change: brief compliance rate this batch versus last, and whether the `missing_question` pattern moved.
6. Renewal numbers: meetings held, payable, `qualified`, promoted, won, and cost per `qualified` meeting at $750 per held meeting.

**Push back on single-case reweights, including from Nir.** One Red that converts is a data point, not a rule. Say so and wait for the batch.

## Output schema for `score`

The headline is the flag. The score is supporting detail kept for calibration.

```
Ziff brief: [Company] - [Title], [size], [country] · meeting [date] · AE [name]
FLAG: [none | LIKELY UNQUALIFIED | SELF-SERVE]
  because: [each reason that fired, one clause each, quoting the brief]
  the brief did not say: [which of the three agreed answers is missing, if any]
score NN / 100 (v1.2) · fit NN · incumbent NN · owner+team NN · budget NN · persona NN
```

**The flag rules and where they come from.** A brief is flagged `likely unqualified` when any of these is true, because in calibration batch 1 each one sat on the briefs of meetings the AE found unqualified and almost never on the briefs of qualified ones:

1. **The title is not a buyer.** Not a head, director or manager of marketing, content, brand, communications, video, production or creative services, and not the person who personally runs the programme. Hospitality development manager, brand experience account manager, head of UX and design, project marketing manager at a label: five of the eight unqualified meetings, one qualified (a regional field marketer who brought the owner).
2. **No decision owner is named and no team size is given.** Three of eight unqualified, one weak, one qualified (the same field marketer).
3. **The problem is off-fit and nothing fitting sits under it.** Connectivity, attendance, animations, AI generating video from images or text, with no podcast, webinar, interview or recurring video programme in the brief.

**Soft flags, v1.2** (the meeting is likely to come back weak, and the brief names why): `owner not on the call` when the title is manager-level, no decision authority is stated and no owner is named as joining; `budget next year` when the brief says the evaluation, budget or rollout is next year, next fiscal year or after a named later date. Soft flags print beside the hard flag and never replace it.

`self-serve` is a separate flag: one person recording and editing alone on a phone or consumer tools, or a nonprofit / school with no tools budget stated. In batch 1 these turned into weak meetings, not unqualified ones, so it is reported on its own: the meeting is not a waste, but it is a $750 route to a customer who can sign up on the site.

**What the flag does not catch, yet.** Three of the eight unqualified meetings in batch 1 (a satisfied current setup, no stated pain, pre-revenue) looked ordinary on paper. Nothing in those briefs predicted the outcome, which is exactly the gap the three agreed questions from 18 September are meant to close. And "planning with no date" is not a rule yet: it is Nir's July finding and the CFH row is its first test. The `calibrate` verb adds a rule only when it separates outcomes in a batch.

## Constraints

- Never message the vendor, the AE or the prospect. Every outward line is a draft for Nir.
- Never write to HubSpot.
- Never let the outcome leak into the score. The ledger keeps them in separate columns for this reason.
- A brief that is missing is a finding about the vendor's process, not a reason to skip the row.
- Vendor names beyond Ziff: the rubric is the same, the ledger file is per vendor (`data/<vendor>-scores.csv`), the sender and cc list come from `references/team-context/growth-channels.md`.

## Worked examples

Eight scored briefs, with the reasoning, are the seed rows in `data/ziff-scores.csv` and are walked through in `rubric.md` under "Calibration examples". Read those before scoring the first brief of a run.

## Maintaining this skill

State the current rule, not its history. Rubric weights change only through `calibrate` and only with a `data/calibration-log.md` entry. Feedback on how the vendor emails should sound goes to the `nik-voice` internal-ask register, not here.
