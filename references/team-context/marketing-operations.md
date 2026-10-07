# Marketing Operations - team context

**Lead:** Hanan Amos · **Function:** Marketing Operations (+ Website)
**Source type:** `board` team (MOPs Tasks `6257866754` + Website Dev `18397093471`) - see `references/team-task-registry.md`
**Last updated:** 2026-07-19 · ingested Mar / May / Jun monthlies + Jul weeklies (no Feb, Apr report in the Drive folder)

> Snapshot of insights, blockers, big bets, and performance from the team's own reports. Not live data - for current numbers route to `/rivermind:ask`; for source reports see the links at the bottom.

**Trajectory Feb→July:** Started the period as a high-throughput fix-and-build shop (~107 items closed in March across MOPs and Website Dev), then narrowed to fewer, more strategic threads by mid-year (33 deliverables in May, 50 in June). The center of gravity shifted from foundational HubSpot lifecycle plumbing and incident cleanup (March) to a webinar-program build-out and attribution integrity (May), then to launch support for Riverside 2.0 and a major pricing-page relaunch (June-July). By July the work is dominated by the July 13 pricing relaunch (shipped successfully), localization launches (FR/DE), and a growing pile of overdue Critical items and stale intake that signal capacity strain against an ambitious roadmap.

## March 2026
- **Performance:** ~107 tasks closed (~65 Marketing Ops across Hanan + Jonathan, ~42 Website Dev shipped to production); 15 items carried into April; 3 major incidents handled (homepage postmortem, Book-a-Demo traffic spike, Cloudfront 404 caching).
- **Insights:** Heavy lifecycle-plumbing month - Hanan rebuilt the HubSpot lifecycle framework (separating "product truth" from GTM orchestration) and fixed a cluster of email routing/pacing/language-mismatch bugs (e.g. contact got 1st email in German, 2nd in English). Localization (FR, PT) welcome drips built out. New PLG v2 composite scoring model made queryable in Omni BI.
- **Blockers:** Security fix for an exposed third-party API token stuck on vendor coordination; hreflang removal from language selector stuck pending investigation; Appsflyer Data Locker Snowflake integration approval pending; Google Search Console DE-property data discrepancy waiting for approval.
- **Big bets:** Led the website agency decision (Flow Ninja vs Flowout/EagleRay); website rebuild plan with Yuval/Jonathan; onboarded Windsor; built Enterprise Form Self-Attribution and Webinar Engine reporting; created a growth library for Claude skills.

## May 2026
- **Performance:** 33 deliverables shipped (20 Marketing Ops Tasks board, 13 Website Dev). Volume down sharply from March, reflecting a shift to heavier/strategic items.
- **Insights:** Execution clustered around three threads - the webinar funnel (LPs, CTAs, pricing, post-event segmentation), self-serve onboarding lifecycle (new email flow + QA of three onboarding workflows), and infrastructure/attribution integrity (Appsflyer, Omni, MQL drop). The MQL drop was traced to pre-ops not being opened and addressed.
- **Blockers:** None explicitly flagged as stuck (completed-items-only scope); a P0 iOS-revenue-not-displaying-in-Appsflyer issue was resolved during the month.
- **Big bets:** Webinar program build-out was the single largest theme - two comparison pages live (Webinar vs Zoom, Webinar vs GoToWebinar), Webinar Registrant API pricing changes, and a pricing-page price-discrimination test (P0). Completed the web-app domain migration and standardized www→non-www redirects sitewide.

## June 2026
- **Performance:** 50 tasks delivered (22 Marketing Ops, 28 Website Dev); 16 in progress into July. Riverside 2.0 newsletter launch shipped 4 new pages in one day, ~2K MCP waitlist registrants, 550K views on X.
- **Insights:** Late June defined by Riverside 2.0 launch support. OpenAI advertising API tracking landed end-to-end (scoping, Pixel Phase 1, CAPI). New-user onboarding emails moved to Eppo testing; a "No Freemium" test was set up.
- **Blockers:** Careers page on riverside.com stuck; items waiting for approval (new-user onboarding test data anomalies, Trendemon+GTM countdown HP banner for Riverside 2.0); Crowdin localization FAQ-section bug pending; Omni homepage-test data discrepancies in progress.
- **Big bets:** Pricing page relaunch flagged as "the biggest date on the calendar" (go-live July 13) including per-geo pricing test and removing the Grow-plan A/B test; Riverside University pages (hub, What's New, Community); new fonts Phase 2; Primer pixel implementation (Nir's request).

## July 2026 (weekly)
- **Performance:** Jul 5-10 light on shipped MOPs work (1 item: HubSpot churn indication fix) but progressed 7 Website Dev items (new product launch pages/OG images, Editor page, Nav Bar V2, font QA). Jul 12-16 was the payoff week: new Pricing page live July 13 (prod deploy confirmed), Grow-plan A/B test removed, per-geo pricing test shipped (Segment anonymous-ID issue resolved), platform FM-link migration completed, FR pricing compare table published (cleared an item overdue since 7/2), Hays case study published, Outbound Source Change Alerting V1 shipped.
- **Insights:** The pricing relaunch executed cleanly on schedule and several long-standing overdue items closed in its wake. Attribution/governance work is rising - Outbound Source Change Alerting, SSO sign-ups attribution audit, and email-sender migration to the COM domain.
- **Blockers:** Book a Demo render-forms-by-location stuck; No Freemium PPC test stuck after a 7/10 revert (recovered next week); author/reviewer blog credentials overdue since 7/10. (Jul 12-16) Transcription-page-off-third-party-tool overdue since 6/18; Help Center project with Erika overdue since 6/30; Video compressor page fix stuck; a DE localization publish blocker holding ~12 queued blog CMS items (needs a German page unpublished, due 7/17); two long-overdue Critical items still open (multi-account HubSpot data flow, Cloudfront caching 404s).
- **Big bets:** Pricing go-live July 13 + pricing QA; Financial Services industry page; iFrame transcription tools (move off third-party); FR localization launch (target July 20); new fonts Phase 2; email sender migration to COM; forcing kill-or-keep decisions on paused tests (Critical Home LP A/B, P1 new-font test). Recurring theme both weeks: unblock mvpGrow by adding need-by dates to items awaiting Riverside sign-off (9 items on 7/5-10, down to 5 on 7/12-16).

## Sources
- March monthly - [March Monthly Report MOPs 2026](https://docs.google.com/document/d/10JA-wawStZtrAiram_U6h6ppIhraXAQN-hFfYHrFjFI)
- May monthly - [MarketingOps May2026](https://docs.google.com/document/d/1Gq0ecBkCqpIZ2yi7SNXkeZ26ufrXZ5cm8JjjAdanPJc)
- June monthly - [MOPs Monthly June Report](https://docs.google.com/document/d/1u8i724V67coEwps6jsJaYa9qm6jW3hlFmCSSddFbZxU)
- July weekly (Jul 5-10) - [MOPs Weekly Report](https://docs.google.com/document/d/1CzM0axPhqqO4ZYnsLQJfbWIraluUev9z1jQt_amCMnI)
- July weekly (Jul 12-16) - [MOPs Weekly Report](https://docs.google.com/document/d/17mb8X3UPuS-WDpo2puCfQW3OwBd5O75hNIsuMKUfySw)
