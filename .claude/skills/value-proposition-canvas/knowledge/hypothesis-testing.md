# Hypothesis testing: Test Cards, Learning Cards, the experiment library

How to reduce the risk of a value proposition with cheap experiments before
building or launching, and how to keep measuring once it is live. Condensed
from *Value Proposition Design* chapters 3 and 4, with Riverside routing.

## Why experiments, not plans

A business plan is an execution document for a known environment. A new or
changed proposition lives under uncertainty, where polishing a plan gives
the illusion of control. Test the most important assumptions cheaply first,
then spend more on more reliable experiments as certainty grows. The
approach is customer development (Steve Blank) plus lean start-up (Eric
Ries) applied to the canvases.

## Ten testing principles

1. Evidence trumps opinion, including the boss's and the investor's.
2. Learn faster and reduce risk by embracing cheap, quick failure.
3. Test early, refine later.
4. Experiments are a lens on reality, not reality.
5. Balance learnings with vision.
6. Identify idea killers first: test the assumptions that could blow up the
   idea.
7. Understand customers first: test jobs, pains, and gains before testing
   what you could offer.
8. Make it measurable.
9. Not all facts are equal: what interviewees say is weaker than what they
   do.
10. Test irreversible decisions twice as hard.

## Build, measure, learn applied to the canvases

| Artifact | Build | Measure | Learn |
|---|---|---|---|
| Conceptual prototype (canvases) | Sketch profile, map, business model | Fit on paper, ballpark numbers, the seven business-model questions | Whether to adapt the prototype; which hypotheses need testing |
| Hypotheses | Interviews, observations, experiments | What happened versus what you believed | Whether a building block must change |
| MVP | Minimum feature set built to learn, not to sell | Whether products actually relieve pains and create gains | Which relievers and creators work |

Customer development in four steps: **discovery** (get out and learn jobs,
pains, gains), **validation** (experiments on whether customers value the
relievers and creators), then **creation** and **company building** once
validated. The first two are search; pivots happen there. Only then execute
and scale.

## Test the circle, then the square, then the rectangle

- **Circle (Customer Profile).** Do you have evidence of which jobs, pains,
  and gains matter, and which matter most? Test this first. If you start by
  testing the proposition you cannot tell whether customers reject the
  proposition or simply do not have the pain.
- **Square (Value Map).** Do you have evidence of which products, relievers,
  and creators customers want, and which they want most? Test one reliever
  or creator at a time, as cheaply as possible, before prototyping products.
- **Rectangle (Business Model).** Do you have evidence you can reach them
  through the channels, acquire and retain them, generate revenue, access
  the resources and partners, and earn more than it costs? A wanted
  proposition dies in a model that spends more to acquire a customer than it
  earns.

## Extract and prioritise hypotheses

A **business hypothesis** is something that must be true for the idea to
work, partially or fully, and has not been validated. Write them for the
customer ("producers at agencies lose more than two hours a week to guest
setup"), the proposition ("a no-download guest link is the reliever they
value most"), and the business model ("agencies will buy Business seats
without a call").

Rank by how critical each is to survival. Test the killers first. Merge
duplicates.

## The Test Card

```
Test Card                       Name | Assigned to | Deadline | Duration
We believe that     <hypothesis>                                Critical: low..high
To verify that, we will   <experiment>                          Test cost: low..high
And measure         <metric>                                    Data reliability: low..high
We are right if     <threshold that validates or invalidates>   Time required: short..long
```

Book example: "We believe businesspeople look for methods to design better
value propositions. To verify, we will run a search campaign on the term. We
will measure click-through rate. We are right if CTR is at least 2 percent."

Rules: one hypothesis per card; a metric with a denominator; a threshold set
**before** the test; several cheap cards may test the same hypothesis before
one expensive one. Rank cards: most critical first, but cheap and quick
early when uncertainty is highest.

At Riverside the metric definition comes from `/rivermind:ask` (never
derived from a table). The experiment itself routes to the owner: website
split tests to `/page-cro` on Convert Experiences, ad-tracking tests to
`/paid-acquisition-agent`, landing-page MVPs to `/website-agent`, email
tests to `/lifecycle-agent`. Tracked work goes through `/pm-story`.

## The Learning Card

```
Learning Card                   Insight name | Person | Date of learning
We believed that    <hypothesis>                                Data reliability: low..high
We observed         <data and results, may aggregate several Test Cards>
From that we learned that   <insight>                           Action required: minor..drastic
Therefore, we will  <decision and action>
Verdict             confirm | deepen | expand | pivot | execute
```

### After learning: five verdicts

The verdict is one of five fixed values. The same five words are the
`Verdict` field of the Learning Card, the TEST mode of the skill, and the
experiment readout in `/measurement-agent`; do not paraphrase them.

| Verdict | When | Then |
|---|---|---|
| `confirm` | Small, early data points to a drastic action | Run a more reliable test before acting |
| `deepen` | You know a trend exists but not why | Follow the quantitative signal with qualitative interviews |
| `expand` | Satisfied with insight and reliability | Test the next building block (channels, partners, price) |
| `pivot` | Tests invalidated the attempt | Back to design: new segment, proposition, or model |
| `execute` | Insight and reliability are both strong | Start scaling |

A Learning Card that changes how the team thinks is a `/retro` candidate so
the learning lands in this repo.

## How quickly are you learning

Cycle time through build, measure, learn is the only thing between you and
knowing what customers want. Six quick cycles beat three slow ones.

| Instrument | Speed | Use |
|---|---|---|
| Canvases, napkin sketches | Ultra fast | Shape ideas, generate hypotheses |
| Interviews with customers, partners, stakeholders | Fast | First market insight, kept in-house |
| Experiment library (below) | Fast to slow | Start quick, move to reliable as direction firms |
| Business plan | Slow | Only with clear evidence, near execution |
| Outsourced market study | Very slow | Incremental changes only; cannot adapt |
| Pilot | Very slow | Precede with cheaper learning; pilots test refined propositions |

## Five data traps

| Trap | What happens | Guard |
|---|---|---|
| False positive | Seeing a pain that is not there | Test the circle before the square; run a second, different experiment before a big decision |
| False negative | Missing a pain that is there | Check the test was adequate for the market (Dropbox's search ads failed because nobody searched for a category that did not exist yet) |
| Local maximum | Optimising a small win while a bigger opportunity sits next to it | Focus on learning over optimising; go back to design when the numbers feel too small |
| Exhausted maximum | Mistaking the whole population for a sample | Design tests that prove potential beyond the immediate subjects |
| Wrong data | Abandoning an idea because the wrong people were tested | Try other segments and alternatives before giving up |

## Choosing a mix of experiments

Two axes. **Say versus do**: start with what customers say (interviews,
surveys), move to what they do (clicks, sign-ups, deposits). **Direct versus
indirect**: direct contact teaches why and how to improve; indirect
observation (web) teaches how many and how much, unbiased by your presence.

Use a **call to action** whenever possible. The more the subject must invest
to perform it, the stronger the evidence: click, then survey, then e-mail,
then meeting with a budget holder, then letter of intent, then prepurchase.
Low-investment CTAs early, high-investment CTAs later. Experiments test
three things: interest and relevance, priorities and preferences, and
willingness to pay.

### Experiment library

| Experiment | What it tests | Notes | Riverside route |
|---|---|---|---|
| Ad tracking | Existence of a job, pain, gain, or interest in a proposition, before it exists | Pick terms that represent what you test; pay per click; no clicks may mean no interest, or a category nobody searches yet | `/paid-acquisition-agent` |
| Unique link tracking | Genuine interest after a pitch | Send a trackable link to more detail; unused means low interest or bigger pains elsewhere | Any outreach; `/inbound-demo-reply` follow-ups |
| MVP representations | Make it feel real without building | Data sheet, brochure, storyboard, video (phone first, crew later), product box, landing page | `/content-agent` for the artifact |
| Functional MVPs | Whether relievers and creators work | Learning prototype with a minimal feature set; Wizard of Oz with humans behind the front | Product and `/website-agent` |
| Illustrations, storyboards, scenarios | Which of 8 to 12 alternative propositions customers rank highest | Four or five meetings per segment; one canvas per B2B stakeholder; A/B the scenarios; always ask why | `/content-agent` |
| Landing page MVP | Whether the job, pain, gain, or proposition is important enough to act on | Headline and copy from the Value Map; traffic from the target segment only; one CTA; measure the funnel (audience, visitors, action, willing to talk); reach out to those who acted and learn their jobs, pains, gains | `/website-agent`, tracking via `/measurement-agent` |
| Split testing | Which alternative wins on a CTA | Equal traffic; one variation if you need attribution; multivariate for combinations. Fix in the Test Card before launch: the minimum detectable effect, the sample size or power it implies, a stopping rule (a date or a sample reached, never "when it looks significant"), and guardrail metrics such as QBD rate or form completion. A 95 percent significance read on its own, or one reached by peeking at a low-volume test, does not decide. The book's own title was chosen this way (8.51 vs 6.62 vs 8.21 percent) | `/page-cro` on Convert Experiences |
| Speed boat | The most extreme pains | Customers place anchors on a boat, lower is worse; add sails for gains | Workshops, community sessions |
| Product box | Jobs, pains, gains and the messages customers would buy | They design the box, then pitch it to you as a sceptic | Workshops |
| Buy a feature | Priority among not-yet-built features | Play money, prices from real cost, budget that forces trade-offs and pooling | Community, customer advisory |
| Mock sale | Sincere interest and price elasticity | Buy button and price variants that end in an intent form, a waitlist, or a payment provider's sandbox or test-token checkout. Never collect real card numbers or CVV for an experiment; deleting them afterwards is not a control. Tell subjects at the end and offer a reward | Requires legal and brand sign-off; confirm before running |
| Presale | Willingness to pay | Pledges, letters of intent, signatures, even non-binding; easier in B2B; a strong presale is still only an indicator | SLG pipeline |
| Life-size prototype | Reaction to a full experience | Always attach a CTA; people design the perfect experience they would never pay for | Rare here |

## Measuring progress

Track movement along the readiness ladder (after Steve Blank's investment
readiness levels): idea designed, business model and proposition prototyped,
assessed against competitors, customer assumptions validated
(**problem-solution fit**), interest validated, preference validated,
willingness to pay validated (**product-market fit**), business model
validated (**business model fit**), then monitoring.

A **progress board** holds the canvases with tested, validated, and
invalidated elements marked; a backlog, build, measure, learn, done lane for
Test Cards; Learning Cards with insights and actions; and the ladder
position. Keep it where the team already tracks work (a monday board via
`/pm-story`, or a doc), not in a new tool.

## Evolve: once the proposition is live

**Create alignment.** The canvas is a shared language. Sales scripts, ad
copy, decks, packaging, and partner briefs should all point at the same
jobs, pains, gains and the relievers and creators chosen for them. This is
where `references/messaging/messaging-framework.md` and the Value Map should
agree; when they drift, one of them is wrong.

**Measure and monitor.** For each building block define an indicator and a
target (book examples: conversion from book to online sign-up, target 25
percent; readers who feel the theory and practice balance is right, target
80 percent). Track proposition performance (quantitative), customer
satisfaction (perception), and business-model performance. Investigate when
an indicator crosses its threshold. Metric definitions via `/rivermind:ask`
and `/measurement-agent`.

**Improve relentlessly.** Use the same Test Card and Learning Card loop on
"what if we changed X" scenarios and measure the causal effect on
satisfaction.

**Reinvent while successful.** Take exploration as seriously as execution;
prefer continuous experiments to big bets; do not wait for a crisis; treat
new ideas as energy, not risk; judge them by customer experiments rather
than the opinions of managers or experts. Keep asking: what in the
environment is changing; is the business model expiring; is the proposition
still compelling as the customer's jobs, pains, and gains evolve?
