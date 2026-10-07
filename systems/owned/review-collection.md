<!-- last-reviewed: 2026-10-01 -->
# Review Collection (G2, Capterra, Trustpilot)

> How Riverside gets happy users to review it on third-party review sites. One Customer.io automation does the asking: every in-product NPS answer of 9 or 10 triggers a review request from Nir, routed by country to G2, Capterra or Trustpilot, sometimes with an incentive. Owned by the SEO & AI Search team; executive owner Nir Taranto.

## Overview

Reviews on G2, Capterra and Trustpilot feed the review badges on our landing pages, our category placement on the review sites, and how AI models describe and recommend Riverside. The collection flow is a promoter ask: someone who has just told us they would recommend Riverside gets a short, personal email in Nir's name with a link to leave a review.

The asking runs unattended. The parts that need people are the incentives (who funds the gift, who sends it) and the choice of which review site gets which promoters.

## Ownership

| Role | Who | Owns |
|---|---|---|
| Executive owner | Nir Taranto (Senior Director, Growth Marketing) | Budget, the sender identity (every email goes out in his name), the final call on incentives and on which site gets promoters |
| Owner | Erika Varangouli (Head of SEO & AI Search) | The review-site portfolio and the collection program |
| Operations | Amir Bar-Tikva (SEO Manager) | Day-to-day running: review-site status and gaps, profile updates |
| Builder | Marketing Ops (Jonathan Galili, Hanan Amos) | Changes inside Customer.io, made on the owners' request |
| Upstream | Product team | The Appcues NPS survey that triggers the flow: who sees it and how often |
| Platform | R&D | Customer.io itself, which also sends Riverside's product system emails. Marketing has build access |

Dor Druker ran review collection until he left on 2026-08-04; ownership then moved to the SEO team.

**Behavior changes are the owners' call, not Marketing Ops'.** Who is asked, what they are offered and which site they are sent to are decided by Nir and the SEO team. MOPs builds what they decide and does not change the flow on its own initiative, including to fix the known issues below. Nir and the SEO team raise changes when they want them (confirmed 2026-10-01).

## How Claude Works With This

| Action | How |
|---|---|
| Investigate | Customer.io MCP (`cio_*` tools), read-only: automation `16` in workspace `120243`. `GET .../campaigns/16` returns every step in a top-level `actions[]` |
| Make changes | Customer.io UI or API, by MOPs, after the owners agree. Confirm before any write |
| Measure sends and clicks | `GET .../actions/{id}/metrics` per step (`version=2`, `tz`, `res`). Language-split emails report on their split step (`279`, `284`), not on each email |
| Measure reviews | Only on each review site's own vendor dashboard. Nothing attributes a published review back to this automation |

Two reading gotchas: branch, split and audience conditions come back as base64 of URL-encoded JSON, so decode them before reading; and the automation-level `action_metrics` block comes back empty, so use the per-step endpoint.

## The Automation

Customer.io automation **`16`**, "Self-Serve: Send a request for a G2 review after a good NPS score (9-10)", in workspace `120243`: <https://fly.customer.io/workspaces/120243/journeys/automations/16/overview>. Running since 2022-12-26. Workspace `124365` holds a few product test workflows and nothing review-related.

### Who enters

- **Trigger:** the event `NPS Score (Appcues)` with `score` greater than 8, so a 9 or a 10. Appcues sends it when a user answers the in-product NPS survey.
- **Leftover filter:** a second event filter, `timestamp` after 2023-07-23, dates from a 2023 change and does not affect new answers.
- **Excluded:** anyone in segment `52` "Block list", a short hand-kept list of individual addresses that other automations (Abandoned checkout, Guest invite) and several newsletters also exclude.
- **Unsubscribed people** are not sent to. There is no frequency cap.
- **Re-entry:** every qualifying answer starts a new journey (restart mode "rematch"), so a user who answers 9 or 10 again later is asked again.
- **No plan or enterprise filter**, despite "Self-Serve" in the name. Automation `17`, the "Enterprise" twin (trigger `Form Field Submitted (Appcues)`), is an empty draft that has never run.

### Steps

```
NPS Score (Appcues), score 9-10, not on Block list (segment 52)
  |
  190  webhook: look up the person in Mixpanel by email, write $country_code to attribute `country`
  191  wait 60 seconds
  192  branch: country = "us"?
        |
        +-- yes --> 342  random split 50/50
        |              +-- A --> 279  split by locale --> G2 + merch email      [OFF since 2026-09-24]
        |              +-- B --> 343  Capterra $20 gift card email (English)
        |
        +-- no ---> 284  split by locale --> G2 + Trustpilot email, no incentive
  |
  exit
```

The language splits (`279`, `284`) route on the profile attribute `locale`: `pt`, `de`, `fr` and `es` get their own version, everyone else gets English. The webhook queries Mixpanel project `2935643`. A failed lookup (5 to 18 a month) leaves `country` unset, so that person takes the non-US path unless an earlier lookup already set their country.

### The three emails

| | US cohort A: G2 + merch | US cohort B: Capterra $20 | Non-US: G2 + Trustpilot |
|---|---|---|---|
| Status | **Off** ("don't send") since 2026-09-24 | Live since 2026-02-19 | Live |
| English subject | Share your thoughts, grab your gift! | A $20 thank you from Riverside 🎁 | A thank you from Riverside + small ask |
| Asks for a review on | G2 | Capterra | G2 and Trustpilot |
| Incentive | Riverside merch, for a screenshot of the review sent back to Nir | $20 gift card, sent by Capterra once it verifies and publishes the review | None |
| Languages | EN, ES, FR, DE, PT | EN | EN, ES, FR, DE, PT |
| Templates | `114` (EN), `400` to `403` | `667` | `37` (EN), `404` to `407` |

All three send from identity `23`, "Nir from Riverside" (`nir.taranto@riverside.fm`), with no reply-to, so replies land in Nir's own inbox. They are signed "Nir Taranto, Riverside" and have link tracking on.

Review links in use:
- G2: <https://www.g2.com/products/riverside-fm-riverside-fm/reviews/start>
- Trustpilot: <https://www.trustpilot.com/review/riverside.fm>
- Capterra: a campaign-specific review URL in template `667`. It carries the campaign's IDs, so copy it from the template rather than building one.

## Incentives

### The G2 merch offer is paused until Nir settles how the gift gets sent

Since 2026-09-24 the merch email is set to "don't send", while the 50/50 split still runs. US promoters drawn into cohort A pass through with no email, so about half of US promoters currently get no review ask. **This is intended:** Nir paused the offer because there is no way yet to send the gift, and he is still working out the fulfillment process.

- Do not reroute cohort A or turn the merch email back on without Nir.
- The offer has no fulfillment owner today. The email asks reviewers to reply with a screenshot, which lands in Nir's inbox with nobody assigned to verify it or ship anything.

### Vendor-funded campaigns: the Capterra $20 program is the model

A review site can fund the incentive itself. The Capterra program is the one running now:

- **Funding:** Capterra (Gartner Digital Markets) put up a $4K budget, paid out as $20 gift cards to the first 200 verified reviewers. Capterra verifies each review and sends the card; Riverside handles no payouts.
- **Riverside's side is routing only:** half of US promoters go to the campaign's review link through the random split.
- **Terms:** the email links the Gartner Digital Markets review-collection terms plus Riverside's terms and privacy policy.
- **Results after launch** (Dor Druker, #marketing-internal, 2026-03-08): Capterra went from 14 to 42 reviews in 2.5 weeks, nearly all 5/5, and G2 rose 10% month on month alongside it, so the split did not take reviews away from G2.
- **Status 2026-10-01:** still running, with budget left. Customer.io cannot see how many cards remain; Capterra can. The email promises a card, so it has to come off when the budget runs out.

**Reusing the pattern for another site:** get the vendor's campaign review link and terms, add a cohort to the split (or a new branch), and reuse the Capterra email's terms block. A vendor-funded incentive costs Riverside nothing in cash; the real cost is the promoters it draws away from other sites, so the decision is which site they come from.

## Performance

Last 12 months, from Customer.io step metrics (October 2025 to September 2026, Israel-time months, pulled 2026-10-01). Click rate is human clicks over delivered.

| Email | Sent | Delivered | Human opens | Human clicks |
|---|---|---|---|---|
| G2 + merch (US cohort A; all US promoters until 2026-02-19) | 19,919 | 19,672 | 5,456 | 1,224 (6.2%) |
| Capterra $20 (US cohort B, from 2026-02-19) | 7,596 | 7,493 | 2,976 | 559 (7.5%) |
| G2 + Trustpilot (non-US) | 16,636 | 16,425 | 5,773 | 630 (3.8%) |

- About 45,000 journeys started over the 12 months. Entries ran 4.0K to 4.7K a month until June 2026, then 2.2K to 2.9K a month from July. The drop starts upstream, in fewer 9-10 answers arriving from Appcues; the Product team owns the survey.
- US promoters were about 63% of sends before the split (October 2025: 2,746 US, 1,596 non-US).
- All 26 unsubscribes in the period came from the Capterra email.
- Clicks show intent, not reviews. Review counts exist only on the review sites.

## Known Behaviors and Open Issues

Recorded for the owners. None is ticketed; Nir and the SEO team will raise changes when they want them.

| Issue | Effect | Where |
|---|---|---|
| Merch email paused behind a live 50/50 split | About half of US promoters get no ask. Intended for now (see Incentives) | Steps `342`, `279` |
| Trustpilot appears only in the non-US email | US promoters, the majority, never see a Trustpilot link | Templates `114`, `400` to `403`, `667` |
| A Mixpanel service-account credential sits in plain text in the webhook's Authorization header | Anyone with Customer.io access can read it. Never copy it into this repo, Slack or a ticket | Step `190`, template `113` |
| The Mixpanel lookup duplicates data already on the trigger | The Appcues event carries `user.countryCode`, so the webhook, the 60-second wait and the failed lookups could all go | Steps `190`, `191` |
| No unsubscribe link in the G2 email bodies | The G2 templates use the empty layout and add no footer. Unsubscribed people are still skipped | Templates `37`, `114`, `400` to `407` |
| Capterra email's desktop footer links are `#` placeholders | On desktop, Unsubscribe, Manage preferences, Support and the social icons go nowhere. Only the mobile footer has real links | Template `667` |
| Re-asked on every 9-10 answer; no enterprise filter | The same user can be asked repeatedly, and enterprise users get the self-serve ask | Automation settings |
| `country` is written with a trailing newline | Harmless today (US promoters still match the branch), but trim it if the step is rebuilt | Step `190` |

## History

| Date | Change |
|---|---|
| 2022-12-26 | Automation goes live: a G2 ask on every NPS 9-10 answer |
| 2024-02-20 | Mixpanel country lookup and the US-only merch offer added |
| 2025-02-25 | Spanish, French, German and Portuguese versions added (Asaf Fox) |
| 2026-02-19 | US promoters split 50/50 to launch the Capterra $20 campaign (Jonathan Galili) |
| 2026-08-04 | Dor Druker, who ran review collection, leaves; ownership moves to the SEO team |
| 2026-09-24 | Merch email set to "don't send" on Nir's call (Jonathan Galili) |

## Not Covered Here

The planned HubSpot to Trustpilot integration, new-review alerts and replies to reviews, and collection on other review sites (TrustRadius, OMR/Trusted, SaaSworthy, SoftwareSuggest) are outside this doc. Ask the owners.
