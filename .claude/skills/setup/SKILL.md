---
name: setup
description: "Set up a new company profile and verify configuration readiness without activating integrations."
user-invocable: true
---

# Setup

## Context and Boundaries

Read `CLAUDE.md` and the configured local company profile. Missing company facts
remain unknown. Use only verified sources and authorized integrations for this company.
Keep private records and reports in ignored `local/` or approved company systems.
Drafting does not authorize sending, publishing, spending, or changing live records.

## Workflow

1. Run `python3 scripts/company_config.py --init`; never overwrite an existing profile.
2. Ask for company name, website, timezone, audience, positioning, and actual tools.
3. Store these facts in the ignored local profile. Do not replace generic repository text
   with employee names, credentials, account IDs, or customer evidence.
4. Record sources for brand, product, messaging, and metrics. Leave unknowns blank.
5. Run `python3 scripts/company_config.py --require-ready` and report missing fields.
6. Test each requested integration read-only, confirm account identity, then mark it enabled.
7. Keep automation disabled until destinations, cadence, failure handling, and scope are authorized.

Return the setup status, missing inputs, and the first useful draft workflow.
