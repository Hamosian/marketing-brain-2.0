---
name: page-cro
description: Diagnose a Riverside website page that is not converting and decide what to improve - homepage, pricing, feature, use-case and comparison pages. Use when conversion is poor and the cause is unknown, when a page's structure or copy is underperforming, when identifying conversion barriers, when writing conversion-optimized page copy, or when designing an A/B test. Triggered by "this page is not converting", "converting badly", "conversion rate is low", "audit this page for conversion barriers", "improve conversion above the fold", or "design an A/B test for this page".
---

# Page CRO Skill

Frameworks for auditing and improving the conversion performance of Riverside's website pages.

---

## Riverside's Dual GTM Context

Riverside operates two parallel conversion tracks on the same website:

- **PLG (Product-Led Growth):** Self-serve free signup. Target audience: solo creators, podcasters, YouTubers, independent journalists, video interviewers. Success signal: free signup that progresses to a paid subscription.
- **SLG (Sales-Led Growth):** Enterprise demo booking. Target audience: content teams, agencies, corporate communications departments, enterprises (200+ employees), non-profits. Success signal: qualified demo booked via ChiliPiper.

Every page must serve one or both tracks clearly. The default CTA hierarchy for pages that serve a mixed audience is:

1. Primary CTA: "Start recording free" (PLG)
2. Secondary CTA: "Book a demo" (SLG)

Never flip this hierarchy on creator-facing pages. On pages targeting enterprise buyers specifically (e.g., Enterprise use case pages), the hierarchy reverses.

---

## What "Conversion" Means by Page Type

| Page Type | Primary Conversion Goal | Secondary Goal |
|---|---|---|
| Homepage | Free signup | Demo booking (B2B visitors) |
| Feature page | Free signup | Upgrade prompt (existing users) |
| Use case page | Free signup (creator) / Demo booking (B2B) | Lead magnet or pricing quiz |
| Pricing page | Plan selection / Free signup | Demo booking |
| Vs. / Comparison page | Free signup (from competitor evaluation) | Blog/content engagement |
| Blog post | Email capture / content engagement | Free signup |
| Demo landing page | Demo booking | Free signup |

Every CRO decision on a page should connect back to its primary conversion goal. Optimizing for time on page or pageviews alone is not a goal.

---

## Riverside Audience Segments

Not all creators and not all businesses are the same. Tailor copy and structure to the primary segment for each page:

| Segment | Job to Be Done | Key Friction | Proof That Works |
|---|---|---|---|
| Solo podcaster | Record guests remotely without quality issues | Worried about guest setup complexity | "No app download for guests" + audio quality claims |
| YouTube / video creator | Get clean 4K local recordings for edited content | Platform quality unpredictability | Before/after production quality examples |
| B2B content team | Scale video content without a production budget | Stakeholder buy-in, procurement | Customer logos, team management features |
| Agency | Run client recording sessions efficiently | Multi-account management, reliability | Uptime / reliability proof, agency-specific case studies |
| Enterprise (200+ employees) | Secure, compliant, scalable recording infrastructure | Security, SSO, procurement approval | Security certifications, contract/MSA availability |
| Non-profit | Affordable, high-quality recording for mission content | Budget constraints | Non-profit pricing or discount mention |

When writing or auditing copy for a specific page, identify the primary segment first. A page trying to speak to everyone will convert no one.

This table is a compressed Customer Profile: one job, one friction, one proof per segment. When a page needs the full ranked set of jobs, pains, and gains for its segment (or a canvas per B2B stakeholder), or when the question is whether the page's value proposition fits the segment at all rather than how the page is built, run `/value-proposition-canvas` first and build the page from its Value Map. Its evidence sources already rank Riverside pains by won-vs-lost demo-form data; in that aggregate, "record remote interviews" is the pain most over-represented in lost deals. That is a reason to validate the target segment's ranked profile before leading with it, not a rule to drop it from every Business page: it can still be the primary job for an agency or enterprise segment.

---

## Page Audit Framework

Run this audit on any page before starting CRO work:

### 1. Clarity Audit
- Can a new visitor understand what Riverside does within 5 seconds of landing on this page?
- Does the headline state an outcome (not a feature)?
- Is the primary CTA visible without scrolling (above the fold)?

### 2. Friction Audit
- How many clicks does it take to get from this page to a free signup?
- Are there competing CTAs that pull attention in multiple directions?
- Does the page ask for information before establishing value?
- For demo booking pages: is the ChiliPiper embed loading fast and presenting slots immediately, or is the form creating unnecessary qualification steps before showing availability? (Refer to the Book-a-Demo QBD analysis for context on high-friction qualification fields.)

### 3. Trust Audit
- Is there social proof above the fold or near the primary CTA?
- Are proof elements relevant to this page's audience (creator vs. B2B team vs. enterprise)?
- Are claims specific and verifiable ("4K local recording" vs. "the best quality")?
- For B2B pages: are customer logos from recognizable companies or brands the target segment respects?

### 4. Relevance Audit
- Does the page copy match what the visitor was looking for? (Check the top search queries driving traffic to this page via GSC.)
- Does the page speak to a specific segment or try to speak to everyone?
- Does the hero section content match the primary audience for this page?
- Does each benefit on the page relieve a pain or create a gain the segment actually ranks high, or is it a feature looking for a job? (Fit check per `/value-proposition-canvas`; unaddressed pains are fine, benefits that address nothing are not.)

### 5. Downstream Conversion Audit (SLG pages only)
- Track the Quit Before Demo (QBD) rate for visitors coming from this page. A high QBD rate means the page is setting wrong expectations about what happens in the demo. (The numerator lives in HubSpot: contacts flagged `is_qbd_lead` - demo-form MQLs who never booked - routed to inbound SDR follow-up; per-field reliability of that suite is documented in `systems/owned/hubspot.md`, "QBD & No-Show Program Fields". The canonical rate definition, denominator, and page-level attribution are the analytics team's to state - get them via `/rivermind:ask`, don't derive them from these fields.)
- The Europe pipeline historically has a significantly lower QBD rate (~7.5%) than Agency/SMB and Enterprise pipelines (~18%+). If a page is generating European traffic with poor overall QBD, investigate whether segment-specific copy is misaligned.

---

## Page Structure Best Practices

### Homepage

1. Hero: outcome-focused headline + subheadline + primary CTA ("Start recording free") + social proof number (50,000+ creators or equivalent current stat)
2. Product demo or preview - show the product working, not a static screenshot
3. Use case proof points covering the three core use cases: podcast, video interviews, B2B content
4. Feature highlights tied to user outcomes (not a spec list)
5. Social proof section: customer logos (inverted/light section for visual contrast per brand guidelines) or testimonials
6. Pricing summary with CTA
7. FAQ (with schema markup)
8. Final dual-CTA section: "Start free" + "Book a demo"

### Feature Pages

1. Hero: what this feature does for the user in one line
2. Demo / screenshot of the feature in action
3. Three benefit bullets with specifics (not vague superlatives)
4. "How it works" section (2-4 steps)
5. Social proof tied to this feature specifically
6. Related features (internal linking for SEO and depth)
7. CTA: "Try [feature name] free"

### Comparison / Vs. Pages

1. Headline: "Riverside vs. [Competitor]" - exact match to the search query, no clever rewrites
2. Summary table: key features side by side
3. Where Riverside wins (with proof)
4. Where [Competitor] wins - be honest; this builds trust and performs better in AI-generated search summaries, which favor balanced, factual content
5. "Best for" recommendation (segment-specific)
6. Dual CTA: "Try Riverside free" + "Book a demo" for B2B

Riverside currently runs paid campaigns against StreamYard specifically. Vs. pages targeting creator-focused competitors like StreamYard should lead with recording quality and local recording reliability as differentiators. Vs. pages targeting Zoom or Teams should lead with creator-grade output quality and purpose-built recording workflows.

### Pricing Page

The pricing quiz (Typeform) is already instrumented as an MQL signal. If the pricing page links to or embeds a pricing quiz, treat that path as a conversion event - not just a page engagement. Visitors who complete the pricing quiz are tagged as MQLs in HubSpot. Any CRO changes to the pricing page that add or remove the quiz path must be tracked as a change to the MQL generation flow, not just a UX change.

---

## Copy Principles for Riverside Pages

- Headline formula: "[Do this] without [obstacle]" or "[Who it's for]: [Outcome]"
- Body copy: short paragraphs (2-3 sentences), active voice, no filler phrases
- Benefit framing: every feature mentioned should have an outcome attached ("Local recording means connection issues never affect your audio quality")
- Social proof: use specific numbers and names where possible ("50,000+ creators" beats "thousands of users")
- CTAs: action verb + specific outcome ("Start recording free" not just "Get started")
- Tone: creator-first. The Riverside brand speaks to people who care about production quality. Avoid corporate-speak on creator-facing pages.
- No em dashes anywhere in page copy. Use commas, colons, or rewrite the sentence.

Avoid these filler words: "world-class," "best-in-class," "cutting-edge," "innovative," "seamless," "powerful," "robust." These add no information and reduce credibility.

---

## Conversion Rate Benchmarks for SaaS

Use these as reference points, not absolute targets:

| Page Type | Benchmark |
|---|---|
| Homepage (free trial) | 3-8% visitor-to-signup |
| Comparison pages | 10-20% (high intent traffic) |
| Pricing page | 5-15% CTA click rate |
| Demo landing page | 15-35% form submission rate |

If a Riverside page is significantly below these benchmarks, prioritize it for audit and A/B testing.

---

## A/B Test Prioritization

Use the ICE framework:

- **Impact:** How much will this improve conversion if it wins?
- **Confidence:** How confident are we this is a real problem (behavioral data, GSC, HubSpot attribution)?
- **Ease:** How quickly can this be built in Webflow and instrumented?

All tests must be documented in Monday.com with: hypothesis, variable being tested, primary metric, sample size required, and result. Tests that touch the demo booking flow must also track QBD rate as a secondary metric.

Write the hypothesis as a Test Card so the threshold exists before the test runs: "We believe that [hypothesis]. To verify, we will [variant]. We will measure [metric with denominator]. We are right if [threshold]." Close every test with a Learning Card (believed, observed, learned, therefore) and one verdict: confirm, deepen, expand, pivot, execute. Templates and the five data traps (false positive, false negative, local maximum, exhausted maximum, wrong data) are in `.claude/skills/value-proposition-canvas/knowledge/hypothesis-testing.md`. A page-wide hypothesis is judged on the whole population against its pre-set threshold and the data-trap checks. A whole-population result only becomes a problem when it is read as proof of fit for one segment, or generalised beyond the audience actually tested. A result that optimised a local maximum is not a win either.

### Known High-Priority Test: Book a Demo Form (200+ Employee Segment)

For enterprise visitors (200+ employees), the current qualification form before ChiliPiper loads is a documented friction point. The tested hypothesis is: using real-time Clay enrichment to pre-populate or skip company-size qualification fields, and surfacing ChiliPiper calendar availability immediately, reduces QBD rate for this segment. If this test has not been run yet, it should rank at the top of the SLG CRO backlog.

---

## Tracking Requirements for CRO Tests

Any CRO change that affects conversion must be tracked properly before launch:

- UTM parameters on all paid and owned traffic sources must be preserved through the conversion event
- New CTAs or form variants must fire HubSpot tracking events so that converted contacts are correctly attributed
- Pricing quiz path changes must not break the `pricing_quiz_completed_date` or `pricing_quiz_mql_tag` HubSpot properties
- Demo booking flow changes must not break ChiliPiper's HubSpot sync

If a test requires changes to HubSpot workflow logic or new custom properties, coordinate with Marketing Ops before launching.

---

## Heatmap and Session Recording Review

Before writing new copy or redesigning sections, review:

- Heatmaps: where are users clicking? What are they ignoring?
- Scroll maps: where do most visitors stop reading?
- Session recordings: where do visitors pause, scroll back, or abandon?

Behavioral data tells you where friction exists. It does not tell you why. Use it to form hypotheses, not to skip copy thinking.
