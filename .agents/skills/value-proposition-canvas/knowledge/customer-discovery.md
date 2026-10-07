# Customer discovery: understanding customers before designing for them

Six techniques for gaining customer insight, the interview method, and how to
turn a pile of interviews into synthesised profiles. Condensed from *Value
Proposition Design* chapter 2.3, with the Riverside sources named.

## Six techniques (use a mix)

| Technique | What you do | Difficulty | Strength | Weakness | Riverside route |
|---|---|---|---|---|---|
| Data detective | Desk research on data you already have and public data | Low | Cheap foundation | Static, from another context | `.claude/skills/inbound-demo-reply/pain-map.md`, `references/messaging/power-user-interviews.md`, `references/messaging/community-voice.md`, HubSpot form comments via `/hubspot-agent`, Gong metadata via `/gong-calls-explorer`, GSC via `/organic-dashboard`, product usage via `/rivermind:ask` |
| Journalist | Talk to customers | Medium | Quick first insights | People say one thing and do another | Power-user interviews, Pre-Op and discovery calls (Gong UI for content; Omni holds metadata only), community threads |
| Anthropologist | Observe customers in their real setting | High | Unbiased, real behaviour | Hard to learn about new ideas | Session recordings and heatmaps (`/page-cro`), Mixpanel flows via `/rivermind:ask`, watching a producer run a live recording |
| Impersonator | Be the customer for a day | Medium | First-hand jobs, pains, gains | Not representative | Record, edit, and publish an episode end to end from a disclosed internal or test account on the plan the target segment actually buys (podcast hosting and publishing start at Pro; plan gating is in `references/product/help-center-reference.md`, so a Free account can only take you through recording and editing). Never book a demo posing as a prospect: the public form creates HubSpot contacts and Pre-Op records and triggers sales follow-up. Walk the demo path in a test environment instead, label those notes as synthetic, and keep them out of `Observed` evidence and funnel metrics |
| Co-creator | Build with customers | Very high | Deep insight | Does not generalise | Community programme, beta cohorts, creator partners |
| Scientist | Run an experiment customers participate in | High | Fact-based behaviour, works for new ideas | Policy constraints | `knowledge/hypothesis-testing.md` |

## The data detective: start with what exists

Before an interview, list from existing data:

- Top search terms and trends around the job (Keyword Planner, Trends, GSC
  via `/organic-dashboard`).
- Third-party reports worth reading as a starting point.
- The ten most frequent positive and negative things said about the brand on
  social and in the community (`references/messaging/community-voice.md`).
- The top three questions, complaints, and requests from support and from
  the demo form (`.claude/skills/inbound-demo-reply/pain-map.md` cross-cutting findings: plan and licence
  questions dominate every cluster).
- Top three ways customers reach the site, most and least visited pages.
- Three patterns in usage data relevant to the idea (`/rivermind:ask`).

## The journalist: interview method

1. **Create a customer profile** with your current beliefs, ranked, tagged
   `Assumed`.
2. **Create an interview outline.** Decide what you want to learn. Derive
   questions from the profile: the most important jobs, most extreme pains,
   most essential gains. Do not derive them from the product.
3. **Review the outline** after each interview or two; retire questions that
   have stopped teaching you anything.
4. **Conduct the interview** following the ground rules below. Two people:
   one leads, one takes notes. Record if allowed, knowing that a visible
   recorder changes answers.
5. **Capture** jobs, pains, gains on an empty profile per interviewee. Capture
   business-model learnings too (how they buy, who signs, what they pay
   today).
6. **Search for patterns** across interviews: similar jobs, pains, gains;
   what stands out; recurring contexts.
7. **Synthesise** one profile per segment that emerges, with representative
   labels for the frequent items.

### Eight ground rules

1. **Beginner's mind.** Listen fresh; do not interpret as you go. Chase the
   unexpected job, pain, or gain.
2. **Listen more than you talk.** The goal is to learn, not to inform,
   impress, or convince.
3. **Facts, not opinions.** Not "would you...?" but "when did you last...?"
4. **Ask why** to reach real motivations. "Why is that important?" "Why is
   that such a pain?"
5. **Learning, not selling,** even when a sale is in play. Not "would you buy
   this?" but "what are your criteria when you choose a tool for this?"
6. **Do not mention the solution early.** Not "our product does..." but
   "what are you struggling with most?"
7. **Follow up.** Get permission to come back with more questions or a
   prototype.
8. **Open doors at the end.** "Who else should I talk to?"

(These draw on Rob Fitzpatrick's *The Mom Test*, 2013.)

Interviews are a starting point, not a decision basis. Complement them with
observation and experiments that produce behavioural evidence.

## The anthropologist: dive into the customer's world

B2C: shadow a creator for a day, observe where they buy and decide. B2B:
work alongside a production team through one publishing cycle, or watch a
marketing team run a webinar. Time-stamp what you see (activity) separately
from what you think (interpretation). Capture what is not said: hesitation,
workarounds, feelings. Stay non-judgemental.

A day-in-the-life sheet has three columns: time, what I see, what I think.
Close by writing the jobs, pains, and gains you observed.

## Identifying patterns and synthesising profiles

1. **Display** every individual profile side by side.
2. **Group and segment** profiles with similar jobs, pains, gains into one
   or more segments.
3. **Synthesise** each segment into a master profile using representative
   labels for the frequent items ("lack of time" for "no time", "limited
   time because of the day job", "takes too long to learn").
4. **Design** prototypes for the master profiles with more confidence than
   before, and with the notes now tagged `Observed` and sized ("mentioned by
   14 of 22").

Watch outliers. Most are noise; some are bellwethers of where the segment is
heading, and some are positive deviants who solved the job better than
everyone else. Keep them visible even when they do not enter the master
profile.

## Earlyvangelists

Prioritise interviewees and pilots who have the problem, know it, are
actively looking, have cobbled together an interim solution, and have or can
get budget. They shape the proposition fastest and become the foothold
market.

## Riverside notes

- `references/messaging/power-user-interviews.md` documents the interview
  order used with 70 or so power users (background, workflow, feedback,
  likes, struggles, goals, requests, quotes). It is a decent template; add
  the "why" ladder and the "when did you last" phrasing.
- Verbatims from form comments and interviews are `Observed`. Deal
  `pain_points` text is AE-written or AI-summarised and is ranking evidence,
  not a verbatim; `.claude/skills/inbound-demo-reply/pain-map.md` explains this and its other limits.
- Never quote one customer back to a prospect, and never fabricate a quote
  when the evidence is thin. Say the evidence is thin.
- If the ask is to interview a **colleague** to extract tribal knowledge
  about Riverside's own systems, that is `/curious-intern`, not this file.
