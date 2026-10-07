---
name: demo-reply-fact-check
description: >
  Blocking fact-check gate for prospect-facing product claims. Extracts every capability,
  plan-gating, and limit claim from a drafted email, verifies each against the product
  knowledge base in a fixed source order, and returns VERIFIED / UNVERIFIED / CONTRADICTED
  per claim so unverified claims never reach a lead. Also blocks on use-case fit and on voice:
  a draft that reads like a machine assembled it fails the gate even when every claim is VERIFIED.
  Runs at the end of the inbound-demo-reply drafting flow, and on demand for any outbound copy
  that states what Riverside does.
  Trigger on: "fact-check this draft", "verify these claims", "is that true", "check the
  product claims", or automatically as Step 4.6 of `inbound-demo-reply`.
---

# Demo Reply Fact-Check

A drafted email that names a capability the lead can disprove in one click costs more than an email that says nothing specific. This skill is the gate that stops that.

**Default verdict is UNVERIFIED.** A claim earns VERIFIED by being found in a source, not by sounding right.

**The gate is not free to be wrong in only one direction (per Nir, 2026-09-07).** A false pass costs a lead one disprovable sentence. A false block costs a round trip, a day on the highest-yield touch, and Nir's time overturning it. Both are real costs and the gate is scored on both. Concretely: a BLOCK needs a named source or a quoted sentence behind it (Step 4 severity tiers), an UNVERIFIED needs the search that failed written down (Step 2 evidence line), a rule dispute is never a block (Step 3 scope), and every block Nir overturns becomes a fixture in `false-block-fixtures.md` that the gate must pass from then on (Step 7). Before today the only regression file held claims the gate let through, so every correction ever made to it made it stricter, and over-blocking was invisible by construction.

## When this runs

- **Blocking, every time** at the end of `inbound-demo-reply` Step 4.6, before the report is presented. Every drafted email body goes through it.
- **On demand** for any other prospect-facing copy that states what Riverside does.

It checks **factual claims only**. It does not check tone, voice, length, or structure. Those belong to `nik-voice`, `writing-optimizer`, and the `inbound-demo-reply` self-review checklist.

## Step 0: Assemble the inputs, and run this as a separate pass

**The gate needs context, not just the draft.** Most gating errors are contextual: the claim is true in general and false for this lead on their plan. A gate that only sees the email cannot catch those. Assemble all five before starting:

1. The **draft body**.
2. The **lead's job title, company, and company size**, for the Step 3.5 fit check. Without the title there is no cluster to rank against.
3. The **lead's plan state**, resolved by `inbound-demo-reply` Step 1's Plan state rule (`customer_plan` with `currently_has_mrr` / `customer_status`; raw `plg_plan_family` only when `customer_plan` is empty, because it labels paying Grow, Business, Mobile and Live subscribers `free` and free-plan contacts with a deal `paid_assisted`), plus `product_plan_raw` and whether a self-serve trial is running. "Free" is a material fact, not background.
4. The **lead's own words**: `form_comment` and any inbound reply, verbatim. The claim has to be true as an answer to what they asked.
5. The **ledger** (`verified-claims.md`) and the **red-team fixtures** (`red-team-claims.md`).
6. The **voice sources** for Step 3.6: `nik-voice`, `de-ai`, and `.claude/skills/inbound-demo-reply/drafting-style-digest.md`.

**Run the gate as its own pass, prompted to refute.** The failure mode this skill exists to catch is an author grading their own framing, and the author always finds their framing reasonable. Hand the five inputs to a fresh pass whose job is to break the draft, not to confirm it. Default to disproving. In `inbound-demo-reply` this means a separate `Agent` call over the drafts, not a re-read by the pass that wrote them. If the run cannot spawn one, say so in the report: a self-graded gate is a weaker gate and Nir should know which one ran.

## Step 1: Extract the claims

Read the draft and pull out every sentence or clause that asserts something checkable. Four kinds:

| Kind | Example from a real draft |
|---|---|
| **Capability** | "your instructors record themselves on their own time" |
| **Plan gating** | "What isn't in the self-serve experience is async recording" |
| **Limit or number** | "Grow is 20 hours a month" |
| **Negative claim** | "that's not something we support right now" |

**Negative claims are claims.** "We don't support X" needs a source exactly like "we do support X" does, and it is the more expensive one to get wrong. A failed keyword search is not a source (see Step 2, restatement rule).

**Aggregate and quantifier claims are claims, and they do NOT inherit the verdicts of their parts.** "Most of it is already on your plan", "everything you need is covered", "that's the only thing gated", "you're most of the way there" each assert something about the *whole* set. A stack of individually VERIFIED feature lines never proves one. Verify the aggregate separately by asking: what does this lead actually want to do, and can they do it end to end on the plan they are on? If any step in that job is gated, the aggregate is CONTRADICTED no matter how many parts checked out.
- **The completeness test for a plan-gating answer.** Before shipping, list every gate standing between the lead and the outcome they described, then confirm the draft names the one that bites hardest. Omitting a gate is not a neutral simplification: it is an implied "there are no others", and it reads as a vendor arguing with a customer who has already hit the wall.
- **On a free account, the export watermark is always in scope for any branding, output, or publishing answer.** Video exports carry "Created with Riverside" and audio-only exports get a "Powered by Riverside" intro; removal starts on Pro (IKB `remove-watermark-from-media-in-the-editor`, `what-is-the-created-with-riverside-watermark`). A branding answer to a free user that omits it is CONTRADICTED, because the lead cannot publish unbranded-by-Riverside output at all.
- **When the lead has expressed disappointment, lead with the gate, not the reassurance.** Answer what it costs them and where the line is. Never open by minimising the gap.

**Not claims, skip them:** role-anchored guesses that carry the guess-check ("Content teams usually use Riverside for X. Is that what you have in mind?"), the opener, the CTA, the closer, and anything about the lead rather than the product.

If the draft contains zero claims, return `NO CLAIMS` and stop. That is a normal and good outcome for a 48h follow-up.

## Step 2: Verify each claim

**First, check the ledger.** `verified-claims.md` in this skill's directory holds claims already adjudicated, with source and date. A claim that matches a ledger entry inherits its verdict, no research needed. This is what keeps a daily run cheap: after a few weeks the common edges (async recording, producer role, SSO) are all cached.

Ledger entries expire after **90 days**, and immediately on any known packaging change. An expired entry is re-researched, not trusted.

For claims not in the ledger, work these sources in order and stop at the first that answers cleanly:

1. **`references/product/help-center-reference.md`** - the plan-tier breakdown is the authority for what sits on which tier. Also `riverside-intel` and `references/product-details.md` if present.
2. **`references/messaging/`** - the messaging framework and voice-of-customer research state product facts the help-center distillation omits. Check here before declaring a gap; the distillation provably misses shipped capabilities.
3. **`/rivermind:ask`** - routes to the local IKB (synced Help Center + internal KB). Cite the article slug or URL you used.

   **The IKB is local files, not `docs_search`. Never conflate them (hard rule per Nir, 2026-09-01).** The IKB lives at `${CLAUDE_PLUGIN_ROOT}/.knowledge/context/ikb/_index.md` in the rivermind plugin: a sharded index over ~2,000 article files, read with plain file reads and grep, with no Snowflake in the path. `docs_search` is a Snowflake Cortex Search service, a different thing entirely, and it has been failing since 2026-08-26 on a missing grant. **A `docs_search` error is NOT evidence the IKB is down**, and it never justifies skipping the KB lookup: open the index and grep the articles. A run that reported the IKB unreachable on the strength of a `docs_search` error cached that false blocker into the fact-check ledger for six days. If `/rivermind:ask` will not invoke, read the IKB index directly rather than surfacing the question unanswered; only when the index file itself is absent is the IKB genuinely unreachable.

   **No silent fallback if `/rivermind:ask` will not invoke.** Rivermind is a plugin reached through the Skill tool. If the invocation fails - the rivermind plugin is not installed in this environment, or `Skill` is not in the run's `allowed_tools` (both common in an unattended cloud routine) - do **not** substitute a raw Snowflake or Omni tool such as `docs_search`, `sql_exec_tool`, `searchOmniDocs`, or `askOmni` to adjudicate the claim. Those are analytics tools, not the IKB, and a verdict built from them is unsourced. Treat the claim as UNVERIFIED and record the cause as `rivermind unreachable - could not invoke /rivermind:ask`, which is a routine-environment problem and is distinct from "the IKB returned no answer." That wording sends the fix to the routine's plugin/`allowed_tools` config rather than to the claim.
4. **Escalate.** If the IKB does not cover it, the claim is UNVERIFIED. Write the exact question to post in the support channel and hand it to Nir. Do not reach this step without running `/rivermind:ask` (or recording that it was unreachable, per the note above).

**Restatement rule - search the concept, not their words.** Before recording CONTRADICTED or UNVERIFIED, restate the claim in Riverside's own product vocabulary and search every synonym. A publisher's "headline" is the episode title; "chapters" and "timestamps" are one feature. A failed literal search is never evidence a feature doesn't exist.

**Evidence line - an UNVERIFIED without it is not a verdict (hard rule per Nir, 2026-09-07).** Every UNVERIFIED row carries a `Searched:` clause naming the restated concept, at least three synonyms, the files or IKB shards searched, and a scan of the **section and FAQ titles** in the relevant category of `references/product/help-center-reference.md`. Minimum shape: `Searched: "trial", "try Pro", "free Pro", "upgrade from free", "change plan" in help-center-reference.md CATEGORY 7 (incl. FAQ titles), messaging-framework.md, IKB index`. Without that clause the row is a note, not a verdict: it cannot block a draft and it cannot cut a clause. The failure this fixes: a pass grepped `trial` in a file whose FAQ list contains "try Riverside Pro for free", found nothing, recorded UNVERIFIED, blocked the draft, and escalated to Ann a question the file had already answered. Writing the search down is what makes a keyword miss visible to the reader, and FAQ titles are where the help-center distillation keeps exactly the account-level facts (trial, upgrade, seats, billing) that plan-state questions turn on.

**Standing rulings inherit without research, and re-raising one is a gate regression.** Any ledger row marked `Standing ruling (per Nir ...)` or `do NOT re-flag` settles its claim at every seat count and plan state. Step 2 checks for one before any research. A gate that re-flags a standing ruling has failed a fixture, not found a problem.

**Tier precision.** Finding a feature is not enough. Confirm the *tier*. The recurring failure is a real capability asserted at the wrong tier: branding exists, but it is on Free and Standard in some form, so "the Business plan adds your own branding" is wrong even though branding is real. If a source names the capability but not its tier, that is UNVERIFIED, not VERIFIED.

**Source conflict.** When two sources disagree, prefer the one that names the capability explicitly, record both, and say which you used. Flag the conflict to Nir so the reference gets fixed.

## Step 3: Verify the answer, not just the sentences

Steps 1 and 2 grade clauses. This step grades the reply as a whole, and it carries its own verdict. **A draft where every clause is VERIFIED can still fail here, and that is the point.** Do not skip it because the claim table came back clean.

Answer three questions in order:

1. **What outcome did this lead describe?** Take it from their own words, not from the draft's restatement of them. "I want all of my content branded" is the outcome. "Can I add a logo" is not.
2. **On the plan they are actually on, can they reach that outcome end to end?** Walk the job: create, edit, export, publish. List **every** gate in the path, not just the one the draft happens to mention.
3. **Does the draft name the gate that bites hardest?** If the answer is no, the draft is CONTRADICTED at the answer level even when every sentence is individually true.

Record the result as its own row: `ANSWER-LEVEL | VERIFIED / CONTRADICTED | gates in path: <list> | gate named in draft: <yes/no>`. A CONTRADICTED answer-level row blocks the draft exactly like a failing claim.

**This step grades truth, never template choice (hard rule per Nir, 2026-09-07).** "On their plan, can they reach the outcome" is a product-truth question and belongs here. "Should this lead have got the choice email or the Business reachout" is a drafting-rule question and does not: it is decided by `inbound-demo-reply` Step 4.5, and when the gate disagrees with how that rule was applied, the disagreement is a `FLAG` (Step 4), never a CONTRADICTED answer-level row. Two reasons. The drafter reads the whole record and the gate reads a summary of it, so on routing the drafter is usually better placed. And a rule dispute has an owner, Nir, who settles it by editing the rule; a gate that blocks on it instead forces a redraft against a rule that may itself be wrong, which is what happened when a Marketing Director at a 57-person employer was pushed onto the choice email over a licence-count leg Nir then overruled. When the drafter has already flagged the deviation in the report, the gate adds nothing by blocking it. State the disagreement, name the rule, ship the drafter's reading.

**Three patterns that fail here and pass Step 2:**
- *Minimising the gap.* "Most of it is already on your plan", "you're mostly there", "that's the only thing gated". See the aggregate-claims rule in Step 1.
- *Answering a narrower question than the one asked.* The lead asks about publishing; the draft answers about creating.
- *Omitting the gate that hurts.* Everything stated is true, and the one thing that would change the lead's decision is missing.

## Step 3.5: Check the use case is the right one for this lead (fit check)

Added 2026-08-23 per Nir, after a draft to a production agency anchored on the producer role. Every claim in it was VERIFIED and the email was still wrong: the agency's actual pain is running many clients out of one account, not backstage control. **A gate that only checks whether claims are true will pass a well-sourced answer to the wrong question.** This step is the missing half.

Step 1 tells you to skip role-anchored use-case guesses as "not claims". That still holds for the *truth* check. They are checked here instead, on fit rather than on truth.

**What to check.** Pull the sentence that names the lead's use case or pain: the `X usually use Riverside for Y` guess, the `teams come to us when...` pain line, or whatever the middle sentence asserts about the lead's situation. Then run three tests in order.

1. **Did the lead say it themselves?** If `form_comment` or an inbound reply names a use case or pain, the draft must answer THAT. A stated use case beats every ranking, and a draft that names a different one is `MISMATCHED` even when the substituted pain is more common. Stop here: tests 2 and 3 only apply when the lead said nothing.
2. **Does it match the top-ranked pain for their cluster?** Route the job title through the `inbound-demo-reply` → "Pain by role" table into `.claude/skills/inbound-demo-reply/pain-map.md`, and read that cluster's ranking. The named pain must be the cluster's highest-ranked one, or the draft must say why a lower-ranked one was chosen. **Rank by the cluster's own combined signal, not by the single largest sub-pain**: on the Agency / Production Company cluster, own-studio-per-client (22 of 118) plus licence-model-doesn't-fit-many-clients (26 of 118) together outrank producer access (26 of 118), which is exactly the call the 2026-08-23 draft got wrong.
3. **Is it on the losing side of the win/loss split?** `.claude/skills/inbound-demo-reply/pain-map.md`'s deal data is directional about which pains correlate with closing. "Record remote interviews" appears in **42.1%** of lost deals against **33.4%** of won, because it is a Pro-shaped need and the top loss reason is "need does not justify enterprise cost" (47% of losses). Naming it is `WEAK` on its own. What correlates with winning: webinars and live (+8.8 points), recording quality (+8.7), editing throughput (+6.6), API and SSO (+6.5), repurposing (+5.8). When the draft names a lose-correlated pain and an adjacent scale signal exists in the record (team size, licence count, cadence, audience size, number of shows or clients), the draft should name that instead.

**Verdicts, one row, reported alongside the claim rows:**

| Verdict | Meaning | Action |
|---|---|---|
| `FITS` | Lead stated it, or it is the cluster's top-ranked pain | Ship |
| `WEAK` | Plausible for the cluster but lower-ranked, or lose-correlated with a better signal available | Report as a low-confidence bullet; Nir's call |
| `MISMATCHED` | Contradicts what the lead wrote, or names a pain their cluster does not have | **BLOCK.** Redraft from the right pain, then re-run |

**A `MISMATCHED` fit row is a BLOCK on its own**, exactly like a CONTRADICTED claim, even when every claim row is VERIFIED. That is the whole point of this step.

**When the right pain has no verified Business edge to attach to, that is a finding, not a reason to retreat to a generic line.** The 2026-08-23 case: the agency pain was right but "a separate workspace per client" was not on the verified Business-only list, so the draft fell back to the generic team-roles sentence. The correct move was to verify the capability - it turned out to be real and Business-gated (see the **productions** entry in `verified-claims.md`). Raise it as an open item with the exact claim to verify, rather than quietly softening the draft.

**Skip this step** for a 48h follow-up (no use-case sentence by design), a pure product answer where the middle sentence is a product fact, and a DQ self-serve invite (the template deliberately does not hook on the content focus).

## Step 3.6: Check it reads like a person wrote it (voice check)

A draft can be true, well-fitted, and still unsendable because it reads like a machine assembled it. That failure never shows up in the claim table, so it needs its own rubric and its own verdict.

**Diagnose, never rewrite.** The moment this gate rewrites prose it becomes the author and forfeits the independence that makes it worth running. Name the failure and quote the offending sentence. Step 5 fixes it and re-runs, exactly as it does for a failing claim.

**Load the content skills in full. Reading about them does not count (hard rule per Nir, 2026-08-31).** Before judging a single sentence, actually load `nik-voice`, then `de-ai`, then `.claude/skills/inbound-demo-reply/drafting-style-digest.md` (full paths for all three are listed just below).

**Read the source FILES directly. Do NOT invoke the `Skill` tool for this (hard rule per Nir, 2026-09-03).** When this gate runs as a separate `Agent` pass - which is how it is required to run - the `Skill` tool does not resolve: it returns only a `Launching skill: X` line with no body and then hangs the pass until the 600s stream watchdog kills it. That is not hypothetical; it stalled the gate twice on the 2026-09-03 evening run, both times on the `Skill` call in this step, and no verdict was produced. So load the voice sources by plain file read, at these exact repo-native paths:
- `.claude/skills/nik-voice/SKILL.md`, then its one register `.claude/skills/nik-voice/registers/prospect-email.md`
- `.claude/skills/de-ai/SKILL.md`
- `.claude/skills/inbound-demo-reply/drafting-style-digest.md`

These are the single source; there is no `plugin-skills/` mirror for `nik-voice` or `de-ai` (that folder holds only `writing-optimizer`), so the old fallback path pointed at nothing. If a `Skill` invocation is ever attempted and returns only the launcher line, that is a non-load: do not wait on it, read the file. The rubric below is a checklist of known failure modes, not a substitute for the skills themselves: it catches what has gone wrong before and is blind to whatever goes wrong next. The skills carry the standard; this list only carries the greatest hits.

**Record which ones you loaded, by name, on the `Voice:` row.** A run that judged voice without loading them has not run this step, and must record `Voice: FAIL - content skills not loaded`. This is the one place the pipeline is verified rather than assumed, so an unverifiable claim that it ran is a FAIL, not a pass with a caveat.

**A scripted or regex check does not satisfy this step either.** Grepping for em dashes, the sign-off, the closer and a banned-word list is the `inbound-demo-reply` self-review checklist, and it is blind to every failure below. If a run reports a voice pass when only a script ran, record `Voice: FAIL - script only, no voice pass ran`.

FAIL on any of these, **and on anything the loaded skills flag that this list does not name**. Quote the sentence for each.

- **Buried lede.** The lead asked something and the answer is not in the first sentence. When the honest answer is "no" or "you already have this", that IS the lede and burying it under qualifiers reads evasive.
- **Lede the lead has to decode (added 2026-09-28).** Read the first sentence with the lead's question beside it. If it is technically the answer but the lead would have to work out what it means, it FAILs: "Grow does take a second editor." passed this step on 2026-09-28 against "I am unable to add an extra editor to the Grow plan. I need 2. Is there a reason I can't do this?" The plain version says what they can do in their own terms ("You can have two editors on Grow"). A "why can't I" / "is there a reason" question that the body never gives a reason for also FAILs here, even when the steps are correct.
- **Spec-sheet prose.** Three or more plan tags in the body, or a run of sentences each carrying exactly one fact plus a tier qualifier. This is the most common failure on product answers.
  - **Carve-out: the two-plan choice email ("Solo-shaped lead who is NOT Disqualified") is exempt from the plan-tag count.** Its whole job is to state the Pro-versus-Business difference and let the lead pick, so it names both plans twice by design, and PART 3 explicitly instructs splitting the trailing edges, price step and trial line into separate short sentences. Judge that template on rhythm and on whether the anchor is pasted whole, never on tag density. Without this carve-out the trigger fires on every correctly-built choice email, which trains the reader to skim the Voice row. Do NOT extend the carve-out to product answers or to the standard Business reachout.
- **Seams: sentences that do not join (hard rule per Nir, 2026-09-21).** Score the JOINTS, not only the sentences. For each of the first three sentences after the greeting, name the connective back to the one before it: a pronoun, a repeated noun, a cause, a contrast, a continued subject. No connective is a seam. **Two seams in a body of four sentences or fewer is a FAIL.** Every other check in this list grades sentences one at a time, so a body of individually correct sentences with nothing holding them together passes all of them and still reads like stacked fragments. That is exactly what shipped on 2026-09-21: four bodies passed this step and Nir caught the fragmentation by hand.
- **Flat rhythm. Read it in BOTH directions.** No sentence under ten words, **or** every sentence inside a narrow band, short bands included. A 9 / 6 / 9 opener is as flat as a 22 / 24 / 21 one; the earlier wording was read as the first clause only, so all-short openers sailed through.
- **Stub.** A sentence that carries no claim **and** joins nothing on either side. `inbound-demo-reply` SKILL.md already names "I talk with producers every week." standing alone as too thin; that is a voice failure here, not only a drafting-rule note.
- **Parroting.** The email restates the lead's own question or reuses their noun instead of answering the concern under it.
- **Appraisal.** Any sentence that grades the lead's thinking ("a fair way to approach it", "smart way to think about it", "makes sense").
- **AI vocabulary.** Anything on the `de-ai` list: navigate, leverage, foster, holistic, streamline, seamless, robust, that said, it's worth noting, at the end of the day, don't hesitate to.
- **Performative sincerity.** "I mean it", "genuinely", "I really do" - a person just says the thing.
- **Hedge closer.** A soft trailing offer the lead has already made redundant, e.g. pushing a walkthrough to someone who just said they are booking one.
- **Unexplained template twin. Compare SENTENCES, not whole bodies.** The trigger is the share of the body that is identical to another draft in the same run, not byte-equality: two of four sentences shared is still a twin. Canonical template is a valid reason; it is not an automatic pass, and it must be stated. Comparing whole bodies let a "now differentiated" redraft pass on 2026-09-21 while two of its four sentences were untouched.

## Step 4: Return verdicts

One row per claim:

```
| Claim (quoted from the draft) | Verdict | Source | Note |
|---|---|---|---|
| "async recording ... isn't in the self-serve experience" | VERIFIED | help-center-reference.md, plan-tier breakdown, Business/Enterprise line | Listed as Business/Enterprise only |
| "the Business plan adds your own branding on the studio" | CONTRADICTED | help-center-reference.md, plan-tier breakdown | Free has basic branding on live streaming; Standard adds image/text overlays |
```

- **VERIFIED** - found, at the stated tier, in a named source. Safe to ship.
- **UNVERIFIED** - not found, or found without tier confirmation. **Cut or replace before shipping.**
- **CONTRADICTED** - a source says otherwise. **Cut before shipping**, and flag the rule that produced it.

Then add the Step 3.5 fit row: `Fit: FITS | WEAK | MISMATCHED - <the use-case sentence> - <which test decided it>`.

Then add the Step 3.6 voice row: `Voice: PASS | FAIL - <failure name>: "<quoted sentence>"`, one clause per failure. It is a separate rubric from the claim table and never merges into it: a draft can be all-VERIFIED and still FAIL here.

Then state the gate result in one line: `PASS` (all VERIFIED or NO CLAIMS, **and** the Step 3 answer-level row VERIFIED, **and** the Step 3.5 fit row FITS or WEAK, **and** the Step 3.6 voice row PASS) or `BLOCK: n claim(s) need fixing`. A failing answer-level row alone is a BLOCK, a `MISMATCHED` fit row alone is a BLOCK, and a `Voice: FAIL` row alone is a BLOCK.

**Three severities, and only the first stops the drafts (per Nir, 2026-09-07).** Every finding is tagged with one of these before the result line is written. A finding that does not fit the first two tiers is a FLAG by default.

| Severity | What earns it | What happens |
|---|---|---|
| **BLOCK** | A CONTRADICTED claim with the contradicting source named. A `MISMATCHED` fit row (the draft names a pain the lead's own words rule out). An answer-level CONTRADICTED where a plan gate stands between the lead and the outcome they described. A `Voice: FAIL` on a failure **named in the Step 3.6 list**, with the sentence quoted. | The draft does not ship until fixed and re-checked. |
| **CUT** | An UNVERIFIED capability, tier, limit or negative claim that carries its Step 2 evidence line. | The clause comes out; the rest of the draft ships if it still stands on its own (the `inbound-demo-reply` Step 4.2 rule). Not a block on the draft. |
| **FLAG** | A template or routing disagreement. A `WEAK` fit row. A voice observation not on the named list. Two of our own files disagreeing. A deviation the drafter already flagged. An UNVERIFIED with no evidence line. Anything the gate is not confident about. | Ships as drafted. One bullet in the report's gate section so Nir can overrule. No redraft, no round trip. |

**A BLOCK carries its own proof or it is a FLAG.** "No source says X" is a FLAG until the evidence line is written; "the source says Y" with the file named is a BLOCK. "This reads flat" is a FLAG; "flat rhythm: every sentence is 18 to 22 words, quoted" is a BLOCK. The burden sits on the block, because a block is the expensive verdict and the one that has been wrong most often.

## Step 5: On a BLOCK, fix and re-run

Cut the failing claim or replace it with a VERIFIED one from the same neighbourhood, then re-run Step 2 on the replacement. Never pad around a hole, and never ship a hedge in place of a fact ("there's a good amount on the Business plan" is a fail, not a safe fallback).

**On a `Voice: FAIL`, the drafting pass rewrites the flagged sentences through `nik-voice` then `de-ai`, then re-runs this gate.** The gate does not supply the rewrite. Re-run Step 2 on any sentence whose rewrite introduced or altered a claim: a voice fix is a new draft, not a formatting tweak.

**If the failing claim came from a rule in a skill file, fix the rule too.** A claim that a skill instructed you to make will come back tomorrow. Edit the canonical rule, then redraft from the edited rule.

**A re-check verifies the fix. It does not open a new front (per Nir, 2026-09-07).** The second pass re-runs Step 2 on the sentences that changed and confirms the original block is cleared. A finding on an **unchanged** sentence that the first pass did not raise is a FLAG at most, never a BLOCK, unless it is a CONTRADICTED claim with a named source. Without this, two passes that each find one new thing produce an infinite regress, and the draft Nir approves gets later every round. The 2026-09-07 evening re-check blocked a draft on a sentence the first pass had passed; under this rule that is a FLAG, the draft ships, and the observation reaches Nir as one line.

## Step 6: Write back to the ledger

Append every newly adjudicated claim to `verified-claims.md`:

```
- **Claim:** async recording is Business-plan only
  **Verdict:** VERIFIED · **Source:** references/product/help-center-reference.md, plan-tier breakdown (Business/Enterprise) · **Checked:** 2026-08-10
```

Record CONTRADICTED entries too. They are the more valuable half of the file: they stop the same wrong claim being re-derived every week.

**Write through, not after (per Nir, 2026-09-07).** A VERIFIED or CONTRADICTED verdict is appended the moment it is adjudicated, inside the same pass, not held until the redraft clears. The re-check pass and tomorrow's run both read this file first; a row that exists only in the first pass's output is a row they re-research. Holding rows back is how the same claim got adjudicated twice in one evening.

**Every entry must say where the line IS, not only where it isn't.** A CONTRADICTED entry that stops at "this is not a Business-only feature" leaves the next run to re-derive the real gating from scratch, which is how a wrong claim comes back wearing different words. Pair every CONTRADICTED entry with the VERIFIED entry that states the actual tier. If you genuinely cannot resolve the tier, write the entry as **UNRESOLVED** and say what would settle it.

**An UNRESOLVED entry blocks reuse.** It is not a soft VERIFIED and it is not background colour. Any draft touching that capability goes back through Step 2 research, or the claim is cut. Never treat "we looked at this once and wrote something down" as having settled it.

## Step 7: Regression-test the gate itself

`red-team-claims.md` in this skill's directory holds claims that shipped or nearly shipped and were wrong, each with the verdict the gate should now return. Run the gate over them:

- whenever `verified-claims.md` changes,
- whenever the plan tiers or packaging change,
- whenever this file's rules change.

Any fixture that does not return its expected verdict is a live regression: fix the rule before shipping anything else. Add a new fixture every time a wrong claim reaches a draft, whoever catches it. The fixtures are cheap to run and they are the only part of this skill that tests the gate rather than the copy.

**The test set is two-sided (per Nir, 2026-09-07).** `false-block-fixtures.md` in this skill's directory holds the other half: blocks the gate raised that Nir overturned, each with the verdict the gate should have returned (`PASS`, `CUT` or `FLAG`) and the rule that should have prevented the block. Run both files together, every time. A gate tested only on what it let through can only ever get stricter, and it did: four blocks on 2026-09-07, two of them wrong, one an escalation to Ann of a fact already in the KB. **Add a fixture to `false-block-fixtures.md` every time Nir overturns a block**, whoever wrote the block. The overturn is the reusable part.

**Precision is reported, not assumed.** The `inbound-demo-reply` morning learning loop counts, over the trailing 14 days, blocks raised and blocks overturned, and prints one line when the overturn rate is above one in four. That is the signal to loosen a rule, and it is the only such signal: nothing else in the system pushes the gate in that direction.

## What this skill does not do

- It does not verify pricing. Every price in the product reference is third-party-sourced and conflicting, so **all pricing is verify-before-publish against the live pricing page** and never gets a VERIFIED verdict here. Pricing asks route to the regional sales lead per `inbound-demo-reply` Step 4.2.
- It does not check claims about the lead, their company, or their industry.
- It does not replace the Step 4.2 confidence gate when a lead has asked a direct product question. That gate runs first, during drafting. This one is the net underneath it.
- It does not replace the `nik-voice` -> `drafting-style-digest` -> `de-ai` pipeline during drafting. That pipeline writes the prose. Step 3.6 is the net underneath it, and it diagnoses only: it never hands back a rewritten sentence.
