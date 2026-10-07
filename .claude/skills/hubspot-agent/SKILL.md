---
name: hubspot-agent
description: "Review HubSpot CRM records, lifecycle definitions, and workflows for the configured company."
user-invocable: true
---

# Hubspot Agent

## Context and Boundaries

Read `CLAUDE.md` and the configured local company profile. Missing company facts
remain unknown. Use only verified sources and authorized integrations for this company.
Keep private records and reports in ignored `local/` or approved company systems.
Drafting does not authorize sending, publishing, spending, or changing live records.

## Workflow

1. Verify the configured portal using an authorized read-only account lookup.
2. Discover the live schema; never assume custom property names or pipeline stages.
3. For investigations, inspect enrollment, suppression, branching, field history, and failures.
4. For changes, prepare the exact records or workflow edits and a small test case.
5. Verify authorization, idempotency, rollback options, and affected population before execution.
6. Read back an authorized change and report actual outcomes.

Return findings or a proposed change set. This template contains no portal IDs or webhook endpoints.
