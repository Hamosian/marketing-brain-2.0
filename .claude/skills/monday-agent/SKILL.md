---
name: monday-agent
description: "Read and update task board items, statuses, owners, and due dates in the configured monday.com workspace. Use pm-story to write a new task's purpose and acceptance criteria, not for bulk status updates."
user-invocable: true
---

# Monday Agent

## Context and Boundaries

Read `CLAUDE.md` and the configured local company profile. Missing company facts
remain unknown. Use only verified sources and authorized integrations for this company.
Keep private records and reports in ignored `local/` or approved company systems.
Drafting does not authorize sending, publishing, spending, or changing live records.

## Workflow

1. Verify workspace and board identity against the local profile.
2. Discover column IDs, types, statuses, and owner mappings from current metadata.
3. Search for existing work before creating anything; identify possible duplicates.
4. For a new task, use `pm-story` to define why, what, and done-when.
5. Apply only authorized changes and read back the affected items.

Return item references, state, owner, next action, and any unresolved schema questions.
Do not assume every company uses monday.com; route elsewhere when its integration is absent.
