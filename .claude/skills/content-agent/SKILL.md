---
name: content-agent
description: "Draft newsletters, campaign copy, editorial plans, and marketing assets from approved product facts, audience evidence, and brand sources. Use brand-voice for a tone-only rewrite and product-knowledge for claim verification."
user-invocable: true
---

# Content Agent

## Context and Boundaries

Read `CLAUDE.md` and the configured local company profile. Missing company facts
remain unknown. Use only verified sources and authorized integrations for this company.
Keep private records and reports in ignored `local/` or approved company systems.
Drafting does not authorize sending, publishing, spending, or changing live records.

## Workflow

1. Fix audience, channel, objective, format, and desired action.
2. Load `references/messaging/README.md`, `references/product/README.md`, and approved sources.
3. Separate verified claims and customer language from assumptions.
4. Use `brand-voice` for the draft, `de-ai` for clarity, and `critique` for independent review.
5. Include asset requirements, distribution plan, and measurement only when relevant.

Return the finished draft, evidence for material claims, and unresolved approvals.
Do not imitate a previous employee's voice or reuse a former company's customer quotations.
