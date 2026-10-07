---
name: value-proposition-canvas
description: >
  Design, check, and test a value proposition with the Value Proposition Canvas
  (Osterwalder and Pigneur). Builds an evidence-tagged Customer Profile (jobs,
  pains, gains) for a segment or B2B stakeholder, a Value Map (products and
  services, pain relievers, gain creators), checks Fit, scores it against the
  ten characteristics, and turns the riskiest assumptions into Test Cards and
  Learning Cards. Seeds every profile from Riverside's own voice-of-customer
  evidence. Trigger on "value proposition", "value prop", "customer
  profile", "jobs to be done", "JTBD", "jobs, pains and gains", "pain
  relievers", "gain creators", "do we have fit", "problem-solution fit", "what
  needs to be true", "test card", "learning card", "hypothesis to test",
  "customer interview guide", "customer discovery", "who is this really for",
  or "/value-proposition-canvas". NOT a page audit (page-cro), NOT the bias
  catalogue (marketing-psychology), NOT closed-lost coding
  (win-loss-pricing-analyzer); never writes the final copy (content-agent).
---

# Value Proposition Canvas

You design value propositions the way *Value Proposition Design* (Osterwalder,
Pigneur, Bernarda, Smith; Strategyzer, 2014) prescribes: understand the customer
first, make the offer explicit second, check Fit, then test the assumptions
before anyone builds or ships. The canvas has two sides. The **Customer Profile**
is what you observe and cannot control (jobs, pains, gains). The **Value Map** is
what you design and can control (products and services, pain relievers, gain
creators). **Fit** is when the map addresses the jobs, pains, and gains that
matter most to the customer, and it exists in three stages: on paper
(problem-solution), in the market (product-market), and in the bank (business
model).

Two rules carry the whole skill:

1. **The customer exists independently of the offer.** Profile the segment as an
   anthropologist would, with the product forgotten. A profile written with the
   offer in mind is the most common failure and the reason this skill exists.
2. **Evidence trumps opinion.** Every sticky note carries a tag: `Assumed`,
   `Observed` (interview, form comment, call), or `Verified` (a measured
   experiment). Rank by evidence, never by who said it loudest. Figures and
   verbatims follow `references/evidence-standards.md`: source plus as-of date,
   and no invented quotes.

## Pick the mode

| Ask sounds like | Mode | Read first |
|---|---|---|
| "who is this for", "what do producers actually need", "build a customer profile" | **PROFILE** | `knowledge/customer-profile.md` |
| "how does X create value", "what's our value prop for agencies", "map the offer" | **MAP** | `knowledge/value-map-and-fit.md` |
| "do we have fit", "is this a good value prop", "score it", "compare to StreamYard" | **FIT** | `knowledge/value-map-and-fit.md` |
| "what needs to be true", "test card", "how would we test this", "learning card", "what did we learn" | **TEST** | `knowledge/hypothesis-testing.md` |
| "interview guide", "questions for the call", "customer discovery plan" | **DISCOVER** | `knowledge/customer-discovery.md` |

A full run is PROFILE then MAP then FIT then TEST. Most asks want one mode.
Say which one you are in.

## Step 0: Scope the segment

Before anything, pin four things or the canvas is mush:

- **One segment per canvas.** Never blend Solopreneurs with Enterprise. In B2B
  make a separate canvas per stakeholder: end user (the producer or host),
  economic buyer (marketing lead, founder), decision maker, recommender,
  influencer, and saboteur (IT, procurement, the incumbent tool's owner).
- **Context.** When, where, with whom, under what constraint. The same podcaster
  has different jobs recording a solo episode at midnight and a client webinar
  with 400 registrants on Friday.
- **Motion.** PLG (self-serve, "Start recording free") or SLG (demo, Business
  plan). The pains that win differ by motion (see Step 1).
- **Invent or improve.** Improving an existing proposition tolerates a thin
  profile; inventing one does not.

## Step 1: Seed from Riverside evidence before asking anyone

The repo already holds most of the raw Customer Profile. Read in this order and
tag each note with where it came from:

1. `.claude/skills/inbound-demo-reply/pain-map.md` - pains by requester title
   with n, verbatims, and the won-vs-lost pain table (2,149 form comments, 3,095
   closed deals, Feb to Aug 2026). This is the only quantified pain ranking in
   the repo. Its sharpest finding: "record remote interviews" is the pain most
   associated with **losing** (42.1% of lost vs 33.4% of won), while live and
   webinar, recording quality at volume, editing throughput, integration and
   SSO, and repurposing correlate with winning. Rank accordingly.
2. `references/messaging/power-user-interviews.md` - decision drivers,
   quantified gains ("7 hours to 2 per episode"), social and emotional jobs
   ("makes me look like I have a team"), per-segment friction.
3. `references/messaging/community-voice.md` - the customer's own mental model
   and the real competitor (fragmented workflows, not a named tool).
4. `.claude/skills/page-cro/SKILL.md` - the audience segment table already
   carries a Job to Be Done and a Key Friction column per segment.
5. `references/messaging/messaging-framework.md` - the per-ICP "key value prop
   and three core benefits" is Riverside's existing **Value Map**. Use it as the
   starting Value Map in MAP mode, never as the Customer Profile.
6. `/win-loss-pricing-analyzer` output when it exists - coded loss reasons are
   pain and unmet-gain evidence.
7. Quantities (segment size, adoption, conversion) go through `/rivermind:ask`
   first, per `CLAUDE.md`.

If a job, pain, or gain appears in none of these, it is `Assumed`. Say so.

## Step 2: Run the mode

**PROFILE.** List jobs (functional, social, emotional, plus the supporting
buyer, co-creator, transferrer jobs), pains (undesired outcomes, obstacles,
risks), and gains (required, expected, desired, unexpected). Make each concrete
with the customer's own measure ("more than 40 minutes of post per episode",
not "takes too long"). Ask why until the underlying job surfaces. Rank: jobs by
importance, pains by severity, gains by relevance. A good profile is crowded;
a profile with six notes means you do not understand the customer yet.

**MAP.** List only the products and services that form the proposition for
this segment. Write pain relievers and gain creators as explanations of how
value is created ("no guest download", "separate tracks so a bad guest mic does
not sink the episode"), never as more product names. Do not try to address
every pain. Great propositions pick a few and relieve them extremely well.

**FIT.** Walk each pain reliever and gain creator and tick the job, pain, or
gain it addresses. Anything unticked is probably not creating value. Then score
the proposition against the ten characteristics in the knowledge file (0 to 10
each, with a one-line reason). Optionally draw the Strategy Canvas against the
two or three competitors buyers actually name (Zoom, StreamYard, Descript,
Goldcast per the pain map).

**TEST.** Extract the hypotheses ("what needs to be true about the customer,
the proposition, the business model"), rank by how critical each is to
survival, and write a Test Card per top hypothesis. Test the circle (do they
have this job, pain, gain) before the square (do they want our reliever), and
the square before the rectangle (channels, revenue, cost). Close each
experiment with a Learning Card and one of five verdicts: confirm, deepen,
expand, pivot, execute.

**DISCOVER.** Derive the interview outline from the ranked profile, apply the
eight ground rules (facts not opinions, ask why, never pitch, open doors at the
end), and plan the mix: interviews first, then observation or an experiment
that makes people act, because what customers say and do differ.

## Step 3: Hand off

This skill produces the canvas, the score, and the cards. It does not ship:

- Copy built on the Value Map goes to `/content-agent` (branded artifacts) or
  `/page-cro` (website pages), then through `/nik-voice`, `/de-ai`, `/critique`.
- Website split tests run through `/page-cro` on Convert Experiences; ad
  tracking tests through `/paid-acquisition-agent`; landing-page MVPs through
  `/website-agent`. The Test Card's metric definition comes from
  `/rivermind:ask`, never from the schema.
- Tracked work goes through `/pm-story`. A Learning Card that changes how the
  team thinks is a `/retro` candidate.
- Deeper JTBD copywriting theory (Four Forces, job statements, six failure
  diagnoses) lives in
  `.claude/skills/inbound-demo-reply/plugin-skills/writing-optimizer/references/jobs-to-be-done.md`.
  Read it for long-form copy; the host skill switches it off for four-sentence
  emails on purpose.

## Output contract

Fixed sections, always present. Write "None found" rather than dropping one.

```markdown
### Value Proposition Canvas: {segment or stakeholder} / {mode}
- Segment and context:
- Motion: PLG | SLG
- Evidence read: (files, as-of dates, n)

#### Customer Profile (ranked, tagged)
| Jobs | Pains | Gains |
| job [Assumed/Observed/Verified: source] | ... | ... |

#### Value Map
- Products and services:
- Pain relievers -> pain addressed:
- Gain creators -> gain addressed:

#### Fit
- Addressed extreme pains / essential gains:
- Unaddressed on purpose:
- Relievers or creators that fit nothing:
- Ten-characteristics score: n/100 with the two weakest named

#### Riskiest hypotheses and Test Cards
- We believe that ... / To verify we will ... / And measure ... / We are right if ...

#### Learning Cards (TEST mode, once results exist)
- Believed / Observed / Learned / Therefore ... / Verdict: confirm | deepen | expand | pivot | execute

#### Not verified
- Every `Assumed` note that a decision depends on, and what would verify it
```

### Example: one FIT line, grounded

For example, a FIT run on the SLG (demo) motion, with the pain map read first, returns
lines like these. Figures are quoted from the won-vs-lost table in
`.claude/skills/inbound-demo-reply/pain-map.md` (window 2026-02-07 to 2026-08-07), which
covers all closed deals and pre-opps and is not split by title, so the canvas says so rather than
presenting it as one segment's ranking:

```markdown
#### Fit
- Addressed extreme pains / essential gains: recording quality at volume
  [Observed: pain map, won 49.4% vs lost 40.7%, n=3,095 closed deals and pre-opps]; live and webinar
  [Observed: pain map, won 40.8% vs lost 32.1%]
- Unaddressed on purpose: "record remote interviews" as the lead pain
  [Observed: pain map, the most loss-associated theme, lost 42.1% vs won 33.4%]
- Relievers or creators that fit nothing: None found
```

A line that cannot carry a tag like those is `Assumed`, and it moves to Not verified.

## Done when

The run is done when every section of the output contract is present (or says "None
found"), every Customer Profile note carries an evidence tag with its source, and every
`Assumed` note a decision rests on is listed under Not verified with what would verify
it. A canvas whose top-ranked pains are all `Assumed` is not finished: say the evidence is
thin and route the gap to DISCOVER or TEST rather than presenting it as a profile.

## What this skill does not own

This skill does not audit or write the page, and it does not grade us against competitors:

- A page's conversion problems are `/page-cro`; the bias catalogue is `/marketing-psychology`.
- Coding closed-lost reasons is `/win-loss-pricing-analyzer`; this skill reads its output
  as evidence.
- Whether our claims sound like Descript's or StreamYard's is `/are-we-really-different`.
- A simulated customer reaction to a finished message is `/persona-panel`; a debate between
  expert lenses on a direction is `/marketing-council`.
- Interviewing a colleague about our own systems is `/curious-intern`; DISCOVER mode here
  plans interviews with customers.
- Final copy is `/content-agent` or `/page-cro`, then the content pipeline (Step 3).

## Guardrails

- Never invent a verbatim, a segment size, or a conversion figure; quote every
  figure from the file it came from. Thin evidence is a finding; say it is thin.
- Never list products in the pain reliever or gain creator boxes.
- Never write a profile "with the product in mind". If every pain happens to
  match a feature, start the profile over.
- Never treat one interview as validation. Interviews are `Observed`; only an
  experiment where people act (click, sign up, book, pay) is `Verified`.
- Pricing, plan names, and plan gating are verify-before-publish; check
  `references/product/` before any pain reliever claims a plan edge.
- Do not create monday items or send Slack directly; route through `/pm-story`
  and `/slack-agent`.
