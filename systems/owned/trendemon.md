<!-- last-reviewed: 2026-09-02 (created after a Slack-filed homepage banner was routed to Website Development instead of Marketing Ops - the repo had no Trendemon knowledge at all, so every routing rule keyed on the word "banner" and got it wrong) -->
# Trendemon (On-Site Messaging)

> The platform that serves **messages layered over riverside.com** - site-wide top bars, homepage banners, popups, slide-ins, and in-app messages (the team calls them "in-apps"). Operated by Marketing Operations. Nothing here is built in Webflow, and no website developer is involved.

## Overview

Trendemon is the delivery layer for on-site messaging. A message is configured in Trendemon and rendered over the live site; the page underneath is untouched. That single fact settles almost every question about who owns a request.

**The most useful thing in this doc:** "homepage banner" is not website work. It reads like website work in every request that ever arrives, and it is a Marketing Ops task. See the discriminator below before routing anything with "banner" in it.

## Ownership

**Platform:** Marketing Operations. Jonathan Galili owns it day to day - 12 of the 13 Trendemon tickets on the MOPs board are his.

**Execution is self-serve, and this is the part outsiders get wrong.** Marketing stakeholders normally **build their own messages** in Trendemon. Marketing Ops assists - reviews the message, checks targeting, resolves whatever comes up - rather than acting as the build queue. So a Trendemon ticket is usually a *review-and-support* ticket, not a *build-this-for-me* ticket, and the brief should reflect that. Ask the requester whether they are building it or asking MOPs to, instead of assuming either.

> **The self-serve standard is not settled yet.** `Trendemon - Improve Self Service Message Creation Process - Ensure Standards` ([`12954626014`](https://riversidefm.monday.com/boards/6257866754/pulses/12954626014), P3, opened 2026-09-02, still in `New Requests`) is the open ticket to define it. Until it closes, describe current practice - do not present a house standard that does not exist.

## Routing: Trendemon or Webflow?

The word "banner" appears legitimately on **both** boards. The discriminator is the delivery mechanism, never the wording, and never the placement.

| The ask | Board | Why |
|---|---|---|
| Site-wide top bar, homepage banner, popup, slide-in, in-app message, countdown bar | **Marketing Operations Tasks** `6257866754` | Trendemon renders it over the page. No Webflow work exists. |
| Footer banner on a template, in-text CRO banner, hard-coded promo HTML, cookie banner | **Website Development** `18397093471` | An element inside the page. A developer edits Webflow. |

Real tickets on each side, so this is not hypothetical: MOPs holds `Trendemon - Youtube Webinar Banner` and `Trendemon + GTM - Countdown HP banner for Riverside 2.0`; Website Dev holds `Replace wrong links in footer banner on the /video-editing-glossary pages`, `Remove Black Friday banner code from raw HTML`, and `Cookie Banner Customisation`.

**When the ask names a placement but no mechanism** - "a banner on the homepage", "something above the nav" - it is a Trendemon message. That is simply how stakeholders describe Trendemon work; they do not know the tool's name, and expecting them to say it is how these get misrouted.

**The misroute has happened more than once.** `PLACEHOLDER - Countdown HP banner for Riverside 2.0` and two `Countdown HP banner_2026_06` items sit closed in Website Dev's Backlog / Archive while the real work ran on MOPs as `Trendemon + GTM - Countdown HP banner`. On 2026-09-02 it happened again with the AI Twin homepage banner. Both times the Website Dev copy was dead weight in a sprint.

## Ticket conventions on the MOPs board

Verified live 2026-09-02 against all 13 Trendemon items on `6257866754`.

| Field | Convention | Evidence |
|---|---|---|
| Name | `Trendemon - <Thing>` prefix; `Issue - Trendemon <thing>` for defects | 9 of 13 |
| Type `status_11` | **`Messaging`** (`7`) for any message or banner | 5 of 5 message tickets. Note `Messaging` is the board's label for **all** outbound messaging (145 items - email, newsletters, in-app), not a Trendemon-specific one; `Email blast` (`11`) is dead by policy. See `references/monday_boards.md` |
| Bucket `color_mkzspv3r` | `Bucket 3: Campaign Execution` (index `2`) | 4 of 5; one older one used `Bucket 6: Website` |
| Owner `person` | Jonathan Galili | 12 of 13 |
| POC `dup__of_assignee` | The requesting stakeholder | Ann Tsunakawa, Alon Livneh, Jarred Berman |

Non-message Trendemon work types differently and correctly: analytics and log extraction as `Reporting/Dashboard`, integration work as `Data integration`, process work as `Biz Process`.

## What a message request must carry

A Trendemon ticket that omits these is not startable, because the person building it pastes these strings into the tool verbatim:

- **The exact copy**, unedited, including the CTA text and any arrow or emoji.
- **The exact destination URL.**
- **Go-live date and take-down date** (or an explicit "manual take-down").
- **Targeting** - who sees it. Audience lists come from HubSpot (`Trendemon - Hubspot Audience LIst for Targeting`).
- **Whether the stakeholder is building it or asking MOPs to.**

Put the requester's own words in an item **update**, verbatim - not paraphrased inside the description. `/pm-story` Step 7 requires this.

> **Check the destination is live before the message is.** A message pointing at an unpublished page ships a 404 to the homepage's whole audience. On 2026-09-02 the AI Twin banner was requested against `riverside.com/ai-twin` while that page was still a 404 - caught by a colleague in the launch thread, not by any process. Make "destination returns 200" an explicit Done-When line on every launch-coupled message.

## Known Issues / Failure Modes

- **Display issues are a recurring category.** `Issue - Trendemon Banner Display Issues` ([`12954619929`](https://riversidefm.monday.com/boards/6257866754/pulses/12954619929)) was a P1 on 2026-09-02. Treat a "banner looks wrong" report as a Trendemon platform issue first, not a Webflow bug.
- **Some banners need GTM alongside Trendemon.** The Riverside 2.0 countdown banner was `Trendemon + GTM`. Dynamic behaviour (countdowns, injected values) may need a GTM component, which is also Marketing Ops - it does not make the ticket website work.
- **Link tracking params are not automatic.** `Trendemon Inapps - Tracking Params for Links` ([`12658567651`](https://riversidefm.monday.com/boards/6257866754/pulses/12658567651)) exists because destination links needed tracking parameters added deliberately. Do not assume clicks are attributed by default; confirm per message.

## Knowledge Gaps

Capture these before automating anything against Trendemon - they are genuinely not known to this repo, and inventing them is worse than leaving them blank:

- **Account, workspace, and dashboard URL.** Not recorded anywhere.
- **How the script is installed** on riverside.com, and where it sits in the `<head>` ordering constraint documented in `systems/owned/marketing-website.md`.
- **Whether an API or MCP exists** for creating or auditing messages. Every ticket to date implies manual dashboard work.
- **No dedicated Slack channel.** Requests arrive in launch and campaign channels; there is no `#trendemon`. Discussion currently lands in `#website-dev` (`C0AM2HQMY49`) by default, which reinforces the misroute.
- **Analytics flow.** Three tickets exist (`Trendemon - Analytics Data Flow - Spec`, `Trendemon Analytics - Dashboard Spec for Data Team`, `Log extraction from Trendemon`) but the resulting flow is undocumented here.

## Related Systems

- `systems/owned/marketing-website.md` - the Webflow site the messages render over, and the `<head>` script-ordering rule
- `systems/owned/convert-experiences.md` - the other third-party script layered over riverside.com; same "operated by MOPs, not a Webflow change" shape
- `systems/owned/hubspot.md` - source of the audience lists used for targeting
- `references/monday_boards.md` - the `Messaging` Type label and Bucket IDs referenced above
