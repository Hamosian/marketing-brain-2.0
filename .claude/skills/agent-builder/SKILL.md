---
name: agent-builder
description: "Create a focused workflow skill with explicit inputs, outputs, evidence, and tests."
user-invocable: true
---

# Agent Builder

## Context and Boundaries

Read `CLAUDE.md` and the configured local company profile. Missing company facts
remain unknown. Use only verified sources and authorized integrations for this company.
Keep private records and reports in ignored `local/` or approved company systems.
Drafting does not authorize sending, publishing, spending, or changing live records.

## Workflow

1. Define the trigger, user outcome, inputs, output, tool scope, and exclusions.
2. Check existing skills before introducing another overlapping entry point.
3. Keep company facts in the local profile, not in the skill body.
4. Use YAML frontmatter with name matching the directory and a precise description.
5. Define evidence rules, missing-input behavior, external actions, and failure handling.
6. Add synthetic routing and output cases for meaningful behavior.
7. Regenerate the Codex mirror and run the shared preflight.

Return the skill files, verification results, and any integration work still required.
