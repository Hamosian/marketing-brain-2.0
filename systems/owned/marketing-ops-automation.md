<!-- last-reviewed: 2026-08-13 -->
# Marketing Ops Automation

> Lead routing, scoring, and the integrations that keep HubSpot ↔ ad platforms ↔ data warehouse in sync.

## Overview
Marketing Ops Automation covers the workflows and syncs that move prospects from marketing touchpoints into sales, reporting, and lifecycle systems. It includes lead routing, scoring, HubSpot workflows, ad platform conversion syncs, and the HubSpot to warehouse path that feeds Omni reporting.

## How Claude Works With This
| Action | How |
|--------|-----|
| Investigate a routing issue | `marketing-ops-automation-agent` plus `hubspot-agent`; check HubSpot records, relevant workflows, and `#mops-priority-room` |
| Modify a workflow | Always confirm before changes; production impact |
| Audit lead-scoring logic | `marketing-ops-automation-agent` plus HubSpot properties and downstream Omni checks |
| Investigate attribution or sync issues | `hubspot-agent`, `measurement-agent`, and relevant system docs |

## Components
| Component | Purpose | Tool |
|-----------|---------|------|
| Lead routing | Round-robin, territory assignment, and sales handoff | HubSpot workflows and properties |
| Lead scoring | Fit and intent scoring model | HubSpot properties, ICP fields, lifecycle rules |
| Sync: ad platforms to HubSpot | Lead gen forms, conversion uploads, audience sync | HubSpot plus ad platform connectors |
| Sync: HubSpot to warehouse | Reporting tables for Omni | Warehouse and Omni reporting layer |
| Product events to HubSpot | PLG signups, activations, and lifecycle signals | Product event sync into HubSpot contact records |

## Known Issues / Failure Modes
| Issue | Symptoms | Resolution |
|-------|----------|------------|
| Product events overwrite Contact Last Touch Source | Contacts that arrived via ads/forms show product-side source after sign-up or activation | Use Pre-Op Last Touch Source for attribution reporting; flag systemic cases to Jonathan |
| Unknown or stale HubSpot field names | MCP queries return `propertiesNotFound` or empty data | Use `search_properties` before querying or changing workflow logic |
| Workflow changes have unclear blast radius | Routing, scoring, or attribution shifts unexpectedly downstream | Identify upstream trigger, downstream systems, rollback path, and owner before changes |
| Reporting symptom may be sync freshness | Omni or dashboard value looks wrong, but HubSpot record is correct | Check source freshness and warehouse sync before changing HubSpot workflows |
| Self-serve signups auto-promoted to MQL + BD outreach | A lifecycle workflow moves raw product signups (source `Riverside.fm Backend App`, zero form submissions) to `marketingqualifiedlead` + `hs_lead_status = "BD: New/Not Contacted"` minutes after signup, routing PLG-only contacts into BD's queue against the self-serve model's design. Systemic (verified 2026-07-14). | Add an exclusion branch to the MQL/BD-promotion workflow gating out product signups, then backfill the affected cohort to `subscriber`. Full spec, scale, and cohort query: `systems/owned/self-serve-lead-scoring.md` → "Known failure: self-serve signups leaking into MQL / BD outreach". Owner: Jonathan. |

## Related Systems
- **Upstream:** HubSpot, paid platforms, marketing website forms
- **Downstream:** Sales (lead delivery), Omni BI (reporting)

## Pointers
- **Slack:** `#mops-priority-room`
- **Monday board:** Marketing Operations Tasks - `6257866754`
- **Specialist skills:** `marketing-ops-automation-agent`, `hubspot-agent`, `measurement-agent`, `pm-story`
- **Knowledge gaps to fill:** exact workflow names, scoring property map, conversion upload runbook, Hevo pipeline owner (the HubSpot to warehouse *path* is now mapped per-stage in `systems/owned/hubspot.md` → "HubSpot to Snowflake to Omni"; the owner and the rule governing which properties land are still open)
