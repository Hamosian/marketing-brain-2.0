---
name: lifecycle-agent
description: "Design consent-aware onboarding email journeys, nurture sequences, retention and win-back messages with segmentation, triggers, suppression, delays, and exit rules."
user-invocable: true
---

# Lifecycle Agent

## Context and Boundaries

Read `CLAUDE.md` and the configured local company profile. Missing company facts
remain unknown. Use only verified sources and authorized integrations for this company.
Keep private records and reports in ignored `local/` or approved company systems.
Drafting does not authorize sending, publishing, spending, or changing live records.

## Workflow

1. Define audience, lifecycle state, trigger, objective, and success measure.
2. Verify CRM schema, consent requirements, suppression rules, and event freshness.
3. Map journey branches, delays, re-entry rules, frequency caps, and exit criteria.
4. Draft messages from approved claims using `content-agent`.
5. Test edge cases with synthetic contacts before proposing activation.
6. Validate account, recipient population, authorization, and rollback before enabling a journey.

Return the journey, copy, test cases, measurement, and unresolved dependencies.
