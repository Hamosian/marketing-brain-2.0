<!-- last-reviewed: 2026-04-30 -->
# Marketing Ops · Q1 FY26 Retro

> **Period:** Feb 1, 2026 to Apr 30, 2026
> **Scope:** Marketing Ops function (both monday boards: Marketing Operations Tasks `6257866754` and Website Development `18397093471`)
> **Sources:** monday.com (339 items with Q1 due dates), Slack (#growth-marketing-leaders, #mops-priority-room, #website-dev)
> **Team:** Hanan Amos (lead), Jonathan Galili (engineering, data, attribution), Yuval Tsabar (marketing website). Plus contracted contributors Davor, Milutin, Raphael Landau, Igor Suprun.

## TL;DR

Marketing Ops shipped **245 of 339 planned items in Q1**, a **72% completion rate** across the function's two monday boards. Output came from a 3-person core team (223 shipped) plus 4 contracted contributors (77). The headline insight: **85% of all Q1 items were unplanned**. The team is operating in a heavily reactive mode, and the size of the gap between planned (43 items) and actual (339 items) is itself the most important finding. Heading into Q2, **94 items carry over**, including **7 P0 / Urgent items**.

---

## By the Numbers

| Metric | MOps Tasks | Website Dev | Combined |
|---|---|---|---|
| Items planned in Q1 | 193 | 146 | **339** |
| Shipped | 128 | 117 | **245 (72%)** |
| Cancelled or stuck | 4 | 3 | 7 |
| Carrying into Q2 | 61 | 26 | **87** |

### Output by group (items shipped)

| Group | Shipped | Scope |
|---|---|---|
| Core team (Hanan, Jonathan, Yuval) | **223** | MOps lead, attribution, AI tooling, HubSpot, data integrations, reporting, marketing website, A/B tests, accessibility, localization |
| Contracted (4) | 77 | Website pages, bug fixes, localization, design, dev support |

### Planned vs Unplanned

This is the headline finding. Combined across both boards:

| Bucket | Count | Share |
|---|---|---|
| **Planned** (on the books before Q1, or tagged Planned on Web Dev board) | 43 | **13%** |
| **Unplanned** (added in-flight during Q1) | 287 | **85%** |
| Unmarked | 9 | 3% |

On the Website Development board (which has a native Planned? column), **88% of shipped items were Unplanned**. On the MOps Tasks board, using created-before-Q1 as a proxy, the split is similar (12% planned, 88% unplanned).

The interpretation: the team entered Q1 with roughly 43 items intentionally scoped for the quarter and finished it having delivered 245 items. This is not a planning problem alone, it is a reactive operating model. Q2 planning will not bend the curve unless something changes about how requests enter the team.

### Volume by month created (combined)

| Month | Items created |
|---|---|
| 2025-11 (carryover from Q4) | 2 |
| 2025-12 (carryover from Q4) | 3 |
| 2026-01 (run-up) | 29 |
| 2026-02 | 130 |
| 2026-03 | 121 |
| 2026-04 | 54 |

Feb and March were comparable peaks (~125 items per month created). April dropped to 54, partly explained by the early-March external event that affected the team's pace through April.

### Shipped by work type (MOps Tasks board only, since Web Dev has no Type column)

| Type | Shipped |
|---|---|
| Reporting / Dashboard | 23 |
| Biz Process | 22 |
| HubSpot | 19 |
| Data integration | 18 |
| Website related (MOps side) | 16 |
| Issue / Bugs | 11 |
| Messaging | 9 |
| Website A/B test | 4 |
| Email blast | 2 |
| Attribution | 1 |

Reporting and HubSpot together accounted for a third of MOps Tasks output. Attribution work is undercounted by tag (much of it shipped under Biz Process and HubSpot labels).

The Website Dev board does not categorize by type. Its 117 shipped items include: page launches and updates, A/B tests, localization (DE, FR, ES), accessibility audit implementation, security fixes, comparison pages, AI page work, transcription page, editor page, and a long tail of bug fixes and design corrections.

---

## Wins

1. **Self-Attribution Channel infra plus weekly Slack report.** New HubSpot property auto-tags every Enterprise form fill. Weekly digest now lands in #growth-marketing-leaders breaking down "How did you hear about us" by channel. Visibly used by the team within a week. (Hanan)
2. **AI tooling rollout for the team.** Mixpanel and Omni added to Claude as MCP connectors. Brand skill built and shared. Deck-builder skill validated by Savion. Step-change in how the team handles ad-hoc analysis and assets. (Hanan)
3. **HubSpot lifecycle and PLG framework.** PLG Lifecycle, Lifecycle framework rebuild, French welcome drip, ChiliPiper 10d calendar fix, Win-back segmentation, Source-of-truth for HS properties. Long-standing tech debt cleared. (Hanan, Jonathan)
4. **Reporting depth.** Mixpanel A/B test reporting revamp, PPC convert-test dashboard template, Subscription cancellations report, Newsletter report, Organic traffic sources, Event Desktop activation, Website visit event. (Jonathan, Hanan)
5. **Localization expansion.** French marketing pages launched (with Raphael, Igor), DE locale fixes throughout the quarter, German pricing page recovered, Israel terms and privacy pages added. (Yuval)
6. **Accessibility audit implementation.** Header, footer, and product pages remediated for AA. Dedicated #website-accessibility channel set up. Ongoing work but a real Q1 throughput. (Yuval, Raphael)
7. **Operational reliability across the website.** PPC 404 alerts, Cloudfront issues triaged, /plans-to-/pricing redirect, /de locale 404 cleanups, security fix on exposed third-party API token, broken navbars across multiple pages corrected. (Yuval, Jonathan)

---

## Misses and Stuck Work

### Top-priority carryovers into Q2

| Source | Status | Owner | Item |
|---|---|---|---|
| MOps | Working on it | Jonathan | Cloudfront caching causing intermittent 404 errors (P0) |
| MOps | Working on it | Jonathan | iOS revenue data not displaying in AppsFlyer Analytics UI (P0) |
| MOps | Working on it | Jonathan | Multi-account feature and HubSpot data flow (P0) |
| MOps | Test is Open | Jonathan | Home LP A/B test (P0) |
| MOps | New | Hanan | Budget report process with Erika (P0) |
| Web Dev | New | Yuval | Static Assets, Love & Labor (Urgent) |
| Web Dev | New | Yuval | Love and Labor: Birth certificate LP (Urgent) |

### P1 carryovers worth flagging

- **Attribution debt.** Fix UTM attribution (past UTMs always showing). Mobile app events for FB apps. Daily event log for anomaly explanation.
- **HubSpot investigation pileup.** Multiple "Investigate HubSpot contact..." tickets opened in April never moved past New.
- **SEO debt.** "SEO debts: provide plan and ETA for no-index and robots.txt fixes" and "Find independent solution for robo.txt management". Both still New.
- **Demand gen follow-ups.** Email campaign to MQLs who didn't book a demo. New no-show cadence for demo bookings. Both opened in late March, both stalled.
- **Website backlog.** Replace internal links to parametrized URLs (P1 Working on it), Page URL cache (P1, no movement), Anomaly detection and on-call protocol for Website (P1, dropped in April).

---

## Themes and Patterns

### What drove the quarter

1. **Performance pressure was the dominant context.** Feb closed at 78% of target. Signups down 14%, trials down 8%. Nir publicly called for new sources and CVR experiments on March 2. This shaped priority more than any planning doc.
2. **AI adoption became a strategic Hanan-led project.** The team explicitly debated Claude vs GPT (IT/Security ask, March 2). Hanan led the answer. Multiple recognition moments in #growth-marketing-leaders.
3. **External event in early March slowed everyone down.** March 9 to 10 messages line up with the March creation peak and explain April's drop. Q1 was not a smooth quarter.
4. **Website ops was a heavy and recurring tax.** #mops-priority-room was dominated by 404s, broken DE redirects, careers page, transcription page, AI page, marketers page, accessibility audit. Now correctly visible as Yuval's primary throughput, not "overflow".

### Process patterns worth naming

1. **The team is operating in 85% reactive mode.** Of 339 Q1 items, only 43 were planned. This is not a complaint about discipline. It is a structural feature of the function and the most important finding in this retro.
2. **MOps Tasks board: Stage column is decorative.** 173 of 193 items sit in Stage = Requirements. Items move from Requirements directly to Done.
3. **MOps Tasks board: Primary Goal field has no variance.** 189 of 193 items tagged "Increase Engagement". The field adds zero signal.
4. **Priority inflation on the MOps board.** 72 P1s plus 17 P0s out of 193: ~46% of work P1-or-higher.
5. **April investigation backlog (MOps).** Many "Investigate X" tickets opened in April and stayed New.
6. **Web Dev board uses Planned? properly.** Yuval is correctly tagging items and the data is reliable. This should be the model for the MOps Tasks board too.

---

## Lessons for Q2

1. **Treat the planned/unplanned ratio as a real metric.** Track it weekly. Aim for shifting it from 13/87 to at least 30/70 over Q2. That requires either more planned work entering, or fewer unplanned requests being accepted, or both.
2. **Decide what the MOps Tasks board is for.** Run the Stage workflow properly or retire those columns. Adopt the Web Dev board's Planned? field as a model.
3. **Re-baseline priority on the MOps board.** No more than 5 active P0s at once. No more than 25% of open work tagged P1.
4. **Triage New items weekly.** 30 minutes on Mondays for #mops-priority-room and the Tasks board. Catches the April investigation pileup pattern.
5. **Separate investigation from delivery tickets.** Investigations have unbounded scope and stall delivery. Time-box them or move to a separate, lower-priority track.
6. **Acknowledge and budget for website ops.** It is not overflow. It is a sub-stream of MOps with its own owner (Yuval), its own board, its own Slack channel. Plan for it explicitly in Q2 capacity.
7. **Capture the AI tooling work in this repo.** Brand skill, MCP rollouts, deck-builder skill are load-bearing and not yet documented in this repo.

---

## Q2 Implications

### Carry over (must finish)

- All 5 MOps P0s (Cloudfront, iOS AppsFlyer, Multi-account HubSpot, Home LP test, Budget report).
- Both Web Dev Urgent items (Love & Labor static assets and birth certificate LP).
- Open A/B tests on MOps board (Descript vs CoCo, Home LP). Decide ship or kill in Week 1.

### Kill or defer (suggested)

- "Clarify decision on Teamblind LP in Claude" (P1, March 17, no movement).
- April HubSpot investigation pileup. Triage Week 1: commit or close.
- Old Web Dev Stuck items: "Remove image/link on webinar page", "Clean up the code for /community pages" (both P3 Stuck since early Feb).

### Scale (worked, do more)

- Self-Attribution weekly report. Add parallel reports for SLG funnel UTM completeness and paid attribution.
- AI tooling rollout. Next layer: HubSpot MCP playbook, "campaign report in 60s" skill, brand-asset workflows.
- Yuval's planning discipline (Planned? field). Bring this practice to the MOps Tasks board.
- Localization. FR is live, DE recovered, more locales likely in Q2.

### New bets to set up early

- Anomaly explanation workflow on top of reports (open task on MOps).
- Clear owner for SEO debt (currently Hanan by default). Either staff it or formally deprioritize.
- A weekly intake review to fight the 85% unplanned rate. Not a planning meeting, a triage moment.

---

## Open Questions for the Q2 Plan

1. Are we accepting the 85% reactive rate, or actively trying to bend it? If yes, with what mechanism?
2. Who triages new requests entering both boards? Is it Hanan, or do Jonathan and Yuval each filter their own?
3. What is the right capacity reservation for unplanned work in Q2 (e.g. 50% of bandwidth) vs planned initiatives?
4. Is there a moment in Q2 to retire or replace the MOps board's Stage and Primary Goal fields?
5. Should we add a Type / Area-of-impact column on the Web Dev board so future retros can categorize its output?
