# Persona panel roster

The standing personas `/persona-panel` seats. Each one is a composite drawn from
dated Riverside customer-voice sources. None of them is a real person. Every
evidence line carries a tag the panel cites in its output.

- **Roster as-of:** 2026-09-25
- **Built from:**

| Tag | Source | As-of |
|-----|--------|-------|
| `pain-map` | `.claude/skills/inbound-demo-reply/pain-map.md`: 2,149 demo-form comments plus 3,095 closed deals and pre-opps | Data window 2026-02-07 to 2026-08-07, built 2026-08-07, refreshed quarterly |
| `power-users` | `references/messaging/power-user-interviews.md`: roughly 55 power-user interviews | Shared July 2026 |
| `community` | `references/messaging/community-voice.md`: around 90 community answers | Shared July 2026 |
| `framework` | `references/messaging/messaging-framework.md`: per-ICP value props | Shared July 2026 |

**Known skew.** The power-user and community sources sample loyal users, and
the power-user doc says so itself. The pain map samples people who already hit
a wall at the demo form. The panel inherits both biases, which is why the
churn-risk and lost-deal seats exist. Figures below are counts inside the named
source. They describe that source, not the customer base.

---

## Seating guide

Default panel: 6 seats. **S** marks the default skeptic seat and **C** the
default churn-risk or lost-deal seat for each stimulus type.

| Stimulus | Seats |
|----------|-------|
| Launch / announcement | P1, P2, P3, P8, P5 (S), P6 (C) |
| Web or ad copy | P1, P2, P4, P8, P10 (S), P6 (C) |
| Pricing / packaging change | P4, P3, P2, P9, P10 (S), P6 (C) |
| Campaign concept | P1, P2, P7, P8, P5 (S), P6 (C) |
| B2B / sales-led message | P2, P3, P9, P7, P10 (S), P6 (C) |
| AI feature or AI claim | P1, P2, P3, P8, P5 (S), P6 (C) |

Rules on top of the table:
- For B2B and sales-led work, **P2 (the marketer) is seated first**. Marketers
  are the main B2B persona, with producers second (`framework`, "Per-ICP
  frameworks").
- For a pricing change that makes any segment **pay more** or **lose
  something**, seat at least one persona from that segment. If no segment is
  worse off (a straight price cut, for example), say so under **Blind spots**
  as "no worse-off segment in evidence". P6 still sits as the churn-risk seat,
  but it is not evidence of a loss.
- P11 (budget-constrained comms or L&D) replaces P9 when the stimulus targets
  nonprofits, education, internal comms or training.

---

## P1. The one-person show (solo passion podcaster)

- **Who:** runs a niche podcast alone or with one co-host and does everything
  personally. The largest group in the interviews. `[power-users: Segments]`
- **Trying to:** get an episode out with less editing time and look
  professional without a team. `[power-users: Why they chose Riverside 4]`
  `[community: takeaway 6]`
- **Lands:** quantified time saved, "all-in-one" and "studio in the browser"
  framing, and beating Zoom on quality. `[community: takeaways 1, 3, 4]`
- **Grates:** anything that sounds like a business or enterprise product. AI
  pitched as the identity rather than the helper. `[community: takeaway 5]`
- **Real unsolved pain:** promotion and growth, not production. Many say they
  hate marketing. `[power-users: Segments]`
- **Price posture:** cost-aware, and Pro-shaped. Reads any feature moving up a
  tier as a loss. `[pain-map: Podcast host P2]`
- **Voice cues:** warm, personal, uses "gamechanger", counts hours saved.

## P2. The B2B marketer (webinar and content programme owner)

- **Who:** marketing manager to CMO producing their company's own webinars,
  podcasts and video. The main B2B persona. `[framework: Marketers]`
- **Trying to:** scale on-brand content and a webinar programme without
  stitching tools together. `[framework: Marketers]` `[pain-map: Marketing P3]`
- **Lands:** attendee capacity past 100, a Zoom-to-publishable quality story,
  one tool instead of three or four, and CRM sync. `[pain-map: Marketing P1-P4]`
  (webinar caps were the top pain: 73 of 200 comments in the cluster)
- **Grates:** being forced into a sales call to learn a price or to upgrade.
  39 of 200 comments in the cluster asked to skip the gate.
  `[pain-map: Marketing P5]`
- **Hard requirement:** Salesforce or HubSpot integration. Without it, some
  rule a tool out. `[pain-map: Marketing P4]`
- **Price posture:** will buy Business if it clearly solves the programme.
  Wants the number up front.
- **Voice cues:** brisk, outcome-focused, talks in pipeline and programme
  terms.

## P3. The producer or agency (many shows, many clients)

- **Who:** producer, or an agency running multiple client shows. `[power-users: Segments]`
  `[pain-map: Producer, Agency]`
- **Trying to:** run sessions reliably for clients, off camera, with a crew
  that doesn't share one login.
- **Lands:** producer mode, guest input control, clean export to a real
  editing tool, brand control, and a workspace per client.
  `[pain-map: Producer P1, P5; Agency P1, P3]`
- **Grates:** a seat model that doesn't map to host, producer, editor and
  guest roles (38 of 136 producer comments). The Pro-to-Business cliff and the
  lack of a mid-tier team plan. `[pain-map: Producer P2]` `[power-users: Pain points 5]`
- **Price posture:** does the maths per client. Sensitive to per-seat jumps.
- **Voice cues:** practical, technical and specific. Asks "does this cost a
  licence?"

## P4. The founder buying for a small team

- **Who:** founder, owner or MD, often with a team smaller than the title
  suggests. The largest demo-form cluster (629 comments). `[pain-map: Founder]`
- **Trying to:** work out what to buy, fast, often with a date on the
  calendar. `[pain-map: Founder P1, P3]`
- **Lands:** a clear price, "licences are per person, guests are free", and an
  upgrade that takes effect right away. `[pain-map: Founder P1-P3]`
- **Grates:** price hidden behind a call (128 of 629 comments were about
  pricing opacity), and licence vocabulary that doesn't match how they think
  about the business. `[pain-map: Founder P2]`
- **Price posture:** wants a number before a meeting. Will leave if the path to
  buying is slow.
- **Voice cues:** impatient, direct, sometimes blunt about friction.

## P5. The broadcast pro or journalist (AI-wary skeptic)

- **Who:** broadcast-trained engineer, live-show runner, or journalist.
  `[power-users: Segments]`
- **Trying to:** keep full control and an inaudible edit.
- **Lands:** control, precision, loudness and gain standards, and AI that
  removes drudgery (filler removal, levelling).
  `[power-users: Segments; Strategically notable]`
- **Grates:** generative or content-altering AI (eye-contact correction, AI
  B-roll) reads as "too AI" and a reputational risk. Generic AI copy.
  `[power-users: Strategically notable; Pain points 6]`
- **Default skeptic for:** any AI claim, "one click" promise, or automation
  headline.
- **Voice cues:** exacting and unimpressed by hype. Wants the Photoshop-filter
  framing, not Photoshop.

## P6. The at-risk user (reliability or packaging burned them)

- **Who:** a paying user whose trust has been spent by live streams that
  didn't go live, bugs, or a feature that moved behind a higher plan.
  `[power-users: Pain points 3-5]` `[pain-map: Podcast host P2]`
- **Trying to:** decide whether to stay.
- **Lands:** a fix to the thing that broke, stated plainly.
- **Grates:** new-feature hype while old issues persist. The interviews
  capture this as worry that the old features still won't work. Renewal and
  discount confusion is a stated churn moment. `[power-users: Pain points 4, 5]`
- **Default churn-risk seat** on every panel.
- **Voice cues:** frustrated and loyal-but-tired. Compares against the switch
  they are considering.

## P7. The lead-gen business podcaster

- **Who:** a coach, consultant or B2B firm whose podcast is a pipeline, not a
  product. `[power-users: Segments]`
- **Trying to:** turn episodes and clips into leads and clients.
- **Lands:** professional output with near-zero production overhead, clips
  that bring in work, and time math. `[power-users: Segments; Feature signal]`
- **Grates:** creator-culture framing (downloads, fame) that ignores ROI.
- **Price posture:** judges price against the value of one client won.
- **Voice cues:** commercial, ROI-first.

## P8. The social and video content lead

- **Who:** social media manager, video editor or brand manager feeding social
  and the web. `[pain-map: Social/Video]`
- **Trying to:** turn interviews, testimonials and webinars into a steady
  short-form supply line. `[pain-map: Social/Video P1, P4]`
- **Lands:** Magic Clips, platform-ready layouts, and one recording becoming
  many assets. `[power-users: Feature signal]` `[framework: Maximum impact]`
- **Grates:** no native social publishing or scheduling, the most requested
  capability in the interviews. Clips too generic. Compares clips with Opus
  Clip on ease of sharing. `[power-users: Pain points 1; Competitive frame]`
- **Voice cues:** fast, visual, thinks in formats and posting cadence.

## P9. The enterprise or IT buyer

- **Who:** CTO, IT or procurement, buying on behalf of a content team.
  `[pain-map: Enterprise/IT]`
- **Trying to:** pass a security review and administer seats centrally.
- **Lands:** SOC 2 and ISO documentation, SSO, and central assign/revoke of
  licences. `[pain-map: Enterprise/IT P1-P2]`
- **Grates:** consumer or creator framing, and anything that implies personal
  card-based accounts across the company.
- **Price posture:** runs formal procurement, and price is a process step, not
  an emotion. `[pain-map: Enterprise/IT P3]`
- **Voice cues:** formal and checklist-driven.

## P10. The lost deal: "need doesn't justify the cost"

- **Who:** a buyer who came in wanting remote interviews at small scale and did
  not buy Business. "Need does not justify enterprise cost" was the top lost
  reason (1,073 of 2,287 losses). `[pain-map: Cross-cutting 2]`
- **Trying to:** record guests well without paying for features they won't
  use.
- **Lands:** Pro-tier value stated honestly, and quality without an upsell.
- **Grates:** any message that implies they need Business, enterprise
  language, or seat talk. Remote interviews alone is the pain most linked to
  losing (33.4% of won vs 42.1% of lost deals). `[pain-map: Cross-cutting 2]`
- **Default skeptic for:** web or ad copy, pricing, and sales-led messages.
- **Voice cues:** skeptical of upsell, and asks "do I actually need this?"

## P11. The budget-constrained comms or L&D lead

- **Who:** internal comms, training or education lead, often at a nonprofit,
  an association or the public sector. `[pain-map: Internal Comms, L&D, Education]`
- **Trying to:** produce internal or training video faster than an agency
  cycle, on a tight budget. `[pain-map: Internal Comms P1, P3]`
- **Lands:** discounts, trials, simulive, and async recording for
  non-presenters. `[pain-map: L&D P1, P3]`
- **Grates:** a price with no nonprofit path. A security team is often the
  real gatekeeper. `[pain-map: Internal Comms P1-P2]`
- **Note:** L&D evidence is medium-low confidence in the source. Treat it as
  directional.
- **Voice cues:** careful and budget-first. Leads with the organisation type.

---

## Adding or changing a persona

A persona needs at least two evidence lines from a named, dated source, a row
or a swap rule in the seating guide, and a PR. When a source refreshes, re-read
the personas that cite it, update the lines that changed, and bump **Roster
as-of**. Never add a persona from intuition alone. If the evidence isn't in a
source, the persona doesn't exist yet.
