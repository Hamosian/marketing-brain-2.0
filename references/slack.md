# Slack Reference

Workspace: `riversidefm.slack.com`

## Posting to Slack - formatting

- **Slack drops Markdown tables silently.** A `| col | col |` block posts as **nothing** - the pipes and every row between the headings disappear, so a section built as a table lands as an empty heading with no error and no warning. Verified 2026-09-03, when the `/chief-of-staff` v2 brief posted with its Act and Your day sections blank because both were tables. **Never post a table to Slack from any skill.** Use line format instead: a numbered or bulleted list, one item per line, bold-led (`*label*`) where a table would have used a first column. Tables are fine inside repo docs (this file included) because those are read, not posted.
- Links use `<url|label>`, not Markdown `[label](url)`. A bare URL as the last line before trailing text gets absorbed into the link and 404s - use `<url|label>` or a blank line (see the memory note on trailing-text 404s).

## Team Channels

| Channel | ID | Purpose |
|---------|----|---------|
| `#growth-marketing-leaders` | `C0A4Y0BD3BR` | Leadership comms, daily brief source for Nir's direct reports (private, created by Nir Taranto, 2025-12-24). Membership is limited to Nir Taranto's direct reports - anyone else (including their Slack apps/bots) gets `channel_not_found` and won't see it in search. That error means no access, not that the channel is archived or renamed. |
| `#mops-priority-room` | `C0A9JUG9MPZ` | Marketing ops priority requests (private, created by Hanan, 2026-01-21) |
| `#mops-team-internal` | `C0AAQ15SVD3` | Marketing Ops team-internal delivery chatter and daily standups. Destination for scheduled `/mops-standup` and `/ticket-hygiene` posts. |
| `#marketing-internal` | `C043B7GAMPC` | Internal marketing: completions, launches, cross-function updates. Broad - high volume, low request density. |
| `#contact-martech` | `C09HYP45X7T` | **The martech request front door** - where the rest of Marketing asks Marketing Ops for things directly (broken CTAs, tracking questions, ticket chases). Highest density of real, actionable asks of any marketing channel. Primary intake source for `/ticket-hygiene`. |
| `#support-marketing` | `C05TRR8BWBX` | Marketing → Support requests, posted by a `Request for Support` **bot** on a fixed template with a `Requested by:` line naming the human. Note the direction: these are asks *to* Support, not to Marketing Ops, so they are context rather than MOPs intake. |
| `#marketing-revops` | `C07V6N3N5U1` | RevOps ↔ Marketing: HubSpot pipeline changes, form/lifecycle classification updates, data questions. Announcements here routinely create MOPs work without anyone filing a request - e.g. the 2026-08-05 PQL form-ID replacement that produced MOPs `12724801171` and mvpGrow `12723477363`. |
| `#website-dev` | `C0AM2HQMY49` | Internal website comms between developers, Marketing Ops, and senior management (private, created by Yuval Tsabar, 2026-03-15). This is where day-to-day work with the Webflow agency Flow Ninja happens: priority changes, publish coordination, quick fixes. Flow Ninja's developers post here as external members (observed 2026-09-23). |
| `#webflow-riverside` | `C08DJ6BN3NX` | Website task delivery between developers and all marketing stakeholders - where progress and QA of most website tasks happen. **Externally shared (Slack Connect)** because the Webflow devs are contractors: Slack integrations get `mcp_externally_shared_channel_restricted` and cannot post - agents must create a draft (`slack_send_message_draft`) for the human to send. Applies to QA approvals and every other agent post here; see the drafting caveats under `#it-support` in `references/other_teams.md`. |
| `#website-accessibility` | `C0AE8HFK7R7` | **No longer used** (Jonathan Galili, 2026-09-23): accessibility work is ticketed on the Website Development board. Do not send people or posts here. Historical: marketing website accessibility / ADA work (private, created by Yuval Tsabar, 2026-02-09). **Not readable by the Slack integration** - `slack_read_channel` returns `channel_not_found` (verified 2026-08-11). Same situation as `#growth-marketing-leaders` above: that error means no access, not that the channel is archived or renamed. Skip the source and say you skipped it; do not report it as an outage. |
| `#marketing-website-monitoring` | `C05FK3G82H4` | Website alerts and monitoring (public, created 2023-07-06) |
| `#martech-alerts` | `C0752QB0Q93` | Automated martech alerts, including the Onboarding Orchestrator (public, created by Jonathan Galili, 2024-05-26). Bot noise for triage purposes: `/hanan-chief-of-staff` excludes it from its mention search for that reason. |
| `#marketing-growth-seo-team` | `C0B5B672B7B` | Growth SEO team channel (private, created by Nir Taranto, 2026-05-21). Read in `/hanan-chief-of-staff`'s channel sweep. Distinct from `#seo-reports`, the SEO report destination. |
| `#webflow-management` | `C07ALG9LQQ5` | Webflow management (private, created by Abel Grünfeld, 2024-07-02). Read in `/hanan-chief-of-staff`'s channel sweep. |
| `#marketing-growth-report-updates` | `C0ASQBR8YNR` | Automated reporting updates |
| `#seo-reports` | `C0C082P5VT4` | SEO team's report destination (private, created by Amir Bar-Tikva, 2026-09-08). Members are the SEO function only - Amir, Erika, Ortal. Destination for scheduled `/weekly-seo-report` posts. |
| `#marketing` | `C0280QR6KH6` | Broad marketing channel |
| `#marketing-growth-ppc-team` | `C08SC6DHZ6E` | Paid acquisition / PPC team |
| `#marketing-il` | `C033AP4Q6SF` | Israel-based marketing |
| `#marketing-il-internal` | `C05LHR5R97D` | Israel-based marketing (internal) |
<!-- Channel IDs start with C. To find: right-click channel > View channel details > scroll to bottom -->

> **`#marketing-weekly` is referenced but not found.** `systems/reference/marketing-operating-model.md` names it as the Weekly Acquisition Digest's destination and `/chief-of-staff` watches it on Tuesdays, but a channel search on 2026-09-24 (public and private) returned nothing by that name. It may be private without access for the integration, or renamed. Confirm the real channel with the analytics team (Yaniv Barel) before relying on it.

## Cross-Team Channels

| Channel | ID | Purpose |
|---------|----|---------|
| `#data-marketing` | `C08283QUCNM` | Marketing <> Data Team requests/escalation (see `references/other_teams.md` for the Data Team's monday boards) |
| `#it-support` | `C07CMP7EFM1` | IT helpdesk - laptops, accounts, SaaS access, and Claude workspace/connector administration. A top-level post auto-creates a ticket via the IT Service Bot. **Externally shared (Slack Connect):** Slack integrations get `mcp_externally_shared_channel_restricted` and cannot post - agents must create a draft for the human to send. Connector-request process in `references/other_teams.md` |
| `#devops-help` | `C086J2JL6FM` | R&D/DevOps request intake. Requests are filed through a **Slack workflow form** in the channel, which creates a Linear issue on the DevOps team - never create that issue directly. Form fields, the plain-text requirement and the truncation gotcha are in `references/other_teams.md` |
| `#platform-enablement-requests` | `C0B1FN9HS9J` | Platform Enablement request intake. A post here creates a Linear issue on the Platform Enablement team - never create that issue directly. This is the route for anything about the Backoffice Marketing Coupons API, its gateway or our key (`systems/reference/backoffice-coupons-api.md`). |
| `#platform-enablement-fyi` | `C0B455UBVH6` | Platform Enablement announcements (public, created by Alex Eisen, 2026-05-12). |
| `#platform-enablement-code-review` | `C0B55JTM49W` | Platform Enablement code review (public, created by Roei Berkovich, 2026-05-17). Not a marketing route. |
| `#marketing-dev` | `C0AA8HABQKG` | Marketing ↔ R&D/DevOps working channel for website infrastructure: robots.txt and sitemap changes, DNS, CDN paths, the Lovable campaign route, site monitoring (public, created by Jonathan Galili, 2026-01-22). Regulars observed: David Vaknin, Alex Eisen, Eyal Eizenberg, Yoav Avidan. The documented intake for new DevOps work is the `#devops-help` form (`references/other_teams.md`). |
| `#crisis-escalation` | `C01CK54HWJU` | Company escalation channel for cases where users cannot access or use the core Riverside product: Support shift managers and team leads with Dev during a crisis, alongside the incident's own war room (channel topic). Relevant when a website change could be breaking sign-up or login. |
| `#data` | `C03DA53MGBH` | General company data channel (created 2022-05-02). Marketing's own request and escalation route remains `#data-marketing`. |
| `#eng` | `C03RXGQ29FG` | Engineering channel (**private**, members only; Jonathan Galili, 2026-09-23). It does not show in channel search. Expect `channel_not_found` from a non-member integration, as with the other private channels above: that means no access, not that the channel is gone. Joined by the Web Developer during onboarding. |

## Company Channels

Joined by default in onboarding (list from the Marketing Website onboarding doc, 2026-09-23).

| Channel | ID | Purpose |
|---------|----|---------|
| `#general` | `C01B2F1FW10` | Company-wide announcements |
| `#team-il` | `C01VA80ANSJ` | Israel team |
| `#product-updates` | `C02U47PRB62` | Product release updates |
| `#product` | `C01V860MANM` | Product discussion |
| `#customerlove` | `C01FYQBTFV5` | Customer praise |

## User Groups

| Group | Handle | Use |
|-------|--------|-----|
| None documented yet | n/a | n/a |

## Team Members

See `references/team.md` for the full roster (names, Slack IDs, emails).
