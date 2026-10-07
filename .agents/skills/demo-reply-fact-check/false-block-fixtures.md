# False-Block Fixtures: the other half of the gate's regression set

Blocks the gate raised that Nir overturned. Each one is a test of the **gate**, not of the copy, and each records what the gate did wrong so the failure mode is the reusable part.

`red-team-claims.md` tests for claims the gate let through. This file tests for drafts it should have let through. Run both together (Step 7), every time `verified-claims.md`, the plan tiers, or `SKILL.md` change. A fixture that returns BLOCK when its expected verdict is PASS, CUT or FLAG is a live regression: fix the rule before shipping anything else.

**Add a fixture every time Nir overturns a block**, whoever wrote the block.

Format:

```
### <short name>
- **Draft as blocked:** <the sentence or decision the gate blocked, verbatim>
- **Lead context:** <plan state, title, headcount, own words, the facts the verdict turned on>
- **Gate's verdict:** <what it returned> · **Expected verdict:** PASS | CUT | FLAG
- **Why the block was wrong:** <one line>
- **Rule that must prevent it:** <SKILL.md step and rule name>
- **Cost:** <what the wrong block cost: a round trip, an escalation, a day on a touch>
```

---

### free-account-pro-trial
- **Draft as blocked:** "The trial is free for 14 days at riverside.com/start." on a choice email to an active free-plan user (6 recordings, 1 studio).
- **Lead context:** `plg_plan_family` = free, no Pro trial ever started, education-affiliated, 1 licence, form_comment "niks".
- **Gate's verdict:** UNVERIFIED, answer-level CONTRADICTED, BLOCK, plus an escalation question drafted for Ann · **Expected verdict:** CUT of `/start` only (the omit-/start rule fires on `plg_plan_family` set), with the trial and upgrade facts VERIFIED
- **Why the block was wrong:** The gate grepped `trial` in `references/product/help-center-reference.md`, found nothing, and recorded "no source states a free account can reach the Pro trial." The same file's CATEGORY 7 FAQ list contains "try Riverside Pro for free", "change plan anytime" and "Upgrade or change your subscription plan". The fact was in the file the pass had already read, under a title the keyword missed. Escalating it to Ann sent a PMM a question the help center answers.
- **Rule that must prevent it:** Step 2, Evidence line (FAQ-title scan is mandatory before UNVERIFIED); Step 2, Restatement rule.
- **Cost:** One full redraft round trip, one wasted escalation, and the draft Nir approved was later than it needed to be. Ledger row added 2026-09-07 so Step 2 now resolves it from cache.

### buyer-title-choice-email-block
- **Draft as blocked:** The standard Business reachout to a Marketing Director at a 57-employee e-learning SaaS, with every claim VERIFIED and Voice PASS.
- **Lead context:** 1 licence, no plan, Not Booked, `content_audience_dropdown` = "My company or internal teams", company record France 57 emp E_LEARNING.
- **Gate's verdict:** answer-level CONTRADICTED ("solo-shaped test fires, silent deviation, wrong template"), BLOCK · **Expected verdict:** FLAG (rule dispute; drafter's reading ships; Nir decides the rule)
- **Why the block was wrong:** Which template a lead gets is `inbound-demo-reply` Step 4.5's call, not a product-truth question, and the gate stretched the answer-level row (built for "can they reach the outcome on their plan") into "did the drafter pick the template I would have picked." The drafter's original read was right: Nir overruled the licence-count leg for a buyer title at a real employer the same evening, and that is now a written guard in Step 4.5. Blocking forced a redraft onto the choice email, which then had to be reverted.
- **Rule that must prevent it:** Step 3, "This step grades truth, never template choice"; Step 4, severity tiers (rule dispute = FLAG).
- **Cost:** Two redrafts of the same email in one evening, one Gmail draft rebuilt, and the wrong template briefly sitting in the drafts folder.

### recheck-opens-new-front
- **Draft as blocked:** "There's a [full walkthrough] and a [short version] if you'd rather watch." on the re-check pass of a choice email, after the first pass had passed that sentence.
- **Lead context:** Same active free user as `free-account-pro-trial`; `/start` had been cut in the fix between passes.
- **Gate's verdict:** Voice FAIL (orphaned offer), BLOCK on the re-check · **Expected verdict:** FLAG. The observation was fair; the severity was not.
- **Why the block was wrong:** A re-check exists to confirm the original block cleared. This finding was on a sentence the first pass had passed, raised only after the fix changed its neighbour. Every pass that finds one new thing on an unchanged sentence pushes the approved draft one round later, with no limit.
- **Rule that must prevent it:** Step 5, "A re-check verifies the fix. It does not open a new front."
- **Cost:** A third edit to the same draft and the drafts file rewritten twice.

### async-recording-re-flagged
- **Draft as blocked:** "Async recording ... is on the Business plan" on drafts to small-seat leads, 2026-08-11 and again 2026-08-17.
- **Lead context:** Various; the re-flags turned on the IKB's "some Business plans, contact your CSM" wording.
- **Gate's verdict:** REVIEW / low-confidence caveat "may over-promise to a small-seat lead", twice · **Expected verdict:** PASS
- **Why the block was wrong:** Per-contract provisioning wording is not a plan gate. Nir settled it on 2026-08-17 as a standing ruling in the ledger. The gate raised it twice because nothing told it a settled claim inherits at every seat count.
- **Rule that must prevent it:** Step 2, "Standing rulings inherit without research, and re-raising one is a gate regression."
- **Cost:** Two low-confidence bullets Nir had to read and dismiss, and a standing ruling he had to hand-write into the ledger.

### webinar-cap-withheld
- **Draft as blocked:** A Business webinar-capacity answer, 2026-08-25. The gate treated the IKB's internal 100/200 spread as too wide to quote, gave the lead no number, and asked the lead for their audience size instead.
- **Lead context:** A webinar-capacity question from a Business candidate.
- **Gate's verdict:** UNVERIFIED on the number, answer softened · **Expected verdict:** PASS on "100 on self-serve, up to 10,000 on Business"
- **Why the block was wrong:** Internal provisioning caps describe per-contract state, the same distinction already settled for async recording. Nir rejected the softened answer as poor and wrote the standing ruling.
- **Rule that must prevent it:** Step 2, Standing rulings; Step 5, "never ship a hedge in place of a fact" (the hedge here was asking the lead a question instead of answering theirs).
- **Cost:** A worse email to a real lead, and Nir's time to overturn it.
