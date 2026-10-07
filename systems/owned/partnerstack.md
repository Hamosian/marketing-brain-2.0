<!-- last-reviewed: 2026-07-29 -->
# PartnerStack

> The affiliate and partner program platform, and the Snowflake → Hightouch → PartnerStack
> activation path that tells it which milestones to pay partners for.

## Overview

PartnerStack runs Riverside's affiliate/referral partner program: partner onboarding, the
marketplace listing, commission calculation and partner payouts. It went live mid-June 2026
as the Growth Channels team's replacement bet for underperforming review-site vendors (see
`references/team-context/growth-channels.md`).

Riverside does not let PartnerStack infer conversions. **Snowflake is the source of truth and
Hightouch activates data out to PartnerStack,** so what a partner gets paid for is decided by
our own warehouse, not by their tracking.

The partner-program strategy and vendor relationship sit with Growth Channels - see `references/team.md` for current ownership rather than duplicating it here.
The data path is built and owned by Data Engineering. Marketing Ops writes the specs.

## How Claude Works With This

| Action | How |
|--------|-----|
| Add or change a paid milestone | Write a spec, then `/data-team-request`. See "Writing the spec doc" in that skill - Marketing states the milestone and the API contract, DE picks the source |
| Get an MQL/SQL/funnel definition | `/rivermind:ask` first. The analytics team owns the canonical models; do not derive definitions from HubSpot fields for anything that drives payout |
| Investigate a partner not being credited | Check whether the click resolved to the lead at all (see Attribution below) before suspecting PartnerStack |
| Change commission rates or triggers | PartnerStack app, by PartnerStack's team. Not a data change |
| Attribution gap vs platform-reported revenue | Same class of problem as the Impact.com gap in `references/team-context/growth-channels.md` - reconcile before trusting either number |

## The activation path

```
Website ─► Segment ─► Snowflake ─► Hightouch ─► PartnerStack
                     (source of truth)  (activation)
```

Four PLG indications were live as of the original integration spec: **link clicks / page
views, customer sign-ups, free trials, and paid subscriptions.** Two B2B lead milestones
(**MQL created**, **SQL created**) were specced in July 2026 to extend it.

Each indication is a Snowflake model that Hightouch syncs. Models live in the
`data_transformation` dbt project under `models/bi/partnerstack/`, follow a
`partnerstack__<event>` naming convention, and expose PartnerStack's own field names
(`customer_key`, `ps_partner_key`, `click_id`) rather than internal ones - so a new indication
should match that shape. DE owns which upstream tables feed them.

## Platform constraints that shape every spec

These are the non-obvious ones. They are properties of PartnerStack and Hightouch, so they
constrain any future milestone regardless of implementation.

| Constraint | Consequence |
|---|---|
| **Hightouch has no native Actions support.** Its PartnerStack destination covers customers, transactions and events only. | Any custom milestone goes over Hightouch's **HTTP Request** connector, POSTing to the Actions API directly. Established pattern: the free-trials sync. |
| **`value` on an action is an occurrence count, not an amount.** PartnerStack defines it as how many times the action happened, minimum 1. | It cannot carry lead value or tier. Sending `2` registers two actions and *multiplies* a flat commission rather than raising it. Always send `1`. |
| **The Actions payload has no `meta` object** (the Customers endpoint does). | Segment/tier metadata cannot ride on the action. To pay different rates per segment, register a **separate action type per segment** and give each its own reward trigger. Carry the tier on the customer record for visibility. |
| **An action must target a record that already exists** in PartnerStack. | A lead needs a customer record before its action is sent, or the action fails and the partner is never credited. Order the syncs with a **Hightouch sequence** (lead upsert → action), each triggered on the upstream sync succeeding. |
| **`external_key` is the only dedup handle** on an action, and it is optional/nullable with no documented uniqueness enforcement. | Make it deterministic and unique per lead per milestone, and enforce once-only upstream too. Trigger action syncs on **rows added only** - never rows changed or removed, or a routine refresh will re-fire or retract paid actions. |
| **Commission triggers are configured in the PartnerStack app,** by their team. | Sending an action type with no trigger configured is safe and deliberate: data accrues so payment can be switched on later with no engineering work. |
| **Actions can be backdated** via `created_at` (epoch milliseconds). | Send the event date, not the sync date. A milestone can be confirmed days after it occurred, and commission must date to the event. |

## Attribution

The partner is identified by the PartnerStack click (`ps_xid` / `ps_partner_key` on the
landing-page URL), which has to be carried through to whatever milestone we are paying for.

**Do not build attribution that routes through a Riverside user ID.** The implemented PLG path
resolves an anonymous visitor to a `user_id`, which is fine for sign-ups and trials but drops
a meaningful share of B2B leads, who frequently never create a Riverside account at all. Any
B2B milestone needs a path that works without one.

## Known Issues / Failure Modes

| Issue | Symptoms | Resolution |
|-------|----------|------------|
| Omni undercounts PartnerStack activity | Platform shows real traffic and signups; Omni shows a fraction (450+ visits / 8 signups / 2 trials in launch week vs 4 signups tracked all month) | Tagging/attribution gap, same family as the Impact.com gap. Reconcile against the platform before reporting either figure |
| Action fails silently, partner never credited | No commission appears, no obvious error | Almost always the target record did not exist when the action fired. Check sync ordering first |
| `dim_user_attribution` does not exist | Named in the original integration spec as the identity-resolution table | It was never built. The shipped models resolve clicks inline instead. Do not go looking for it |
| PartnerStack onboarding sheet says Salesforce | Their solutions-team plan lists Salesforce as the CRM and maps lead/partner forms to Salesforce objects | Template default in their standard onboarding kit. Riverside runs on HubSpot; no Salesforce work is ever in scope |

## Related

- **Specs:** original integration spec (syncs 1 to 4) and the July 2026 B2B lead indications spec, both linked from the Growth Channels drive
- **Docs:** [PartnerStack Actions API](https://docs.partnerstack.com/reference/post_v2-actions-1) · [Hightouch PartnerStack destination](https://hightouch.com/docs/destinations/partnerstack) · [Hightouch HTTP Request](https://hightouch.com/docs/destinations/http-request) · [Hightouch sync sequences](https://hightouch.com/docs/syncs/schedule-sync-with-sequences)
- **Contacts:** Growth Channels owns the vendor relationship; PartnerStack side has a solutions/technical contact for integration questions and a CSM for program questions
- **Upstream:** Segment (click capture), Snowflake (source of truth), Hightouch (activation)
- **Downstream:** partner commissions and payouts; Growth Channels affiliate reporting
- **Specialist skills:** `data-team-request` (spec + intake), `rivermind:ask` (metric definitions), `marketing-ops-automation-agent`
