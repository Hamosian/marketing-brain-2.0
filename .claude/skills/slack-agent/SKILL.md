---
name: slack-agent
description: "Draft a short team channel announcement, reply to a Slack thread, find a conversation, or send an authorized update in the configured workspace. Owns communication destination and delivery, not a newsletter or a marketing asset."
user-invocable: true
---

# Slack Agent

## Context and Boundaries

Read `CLAUDE.md` and the configured local company profile. Missing company facts
remain unknown. Use only verified sources and authorized integrations for this company.
Keep private records and reports in ignored `local/` or approved company systems.
Drafting does not authorize sending, publishing, spending, or changing live records.

## Workflow

1. Verify the workspace and resolve the channel or person using current metadata.
2. Read only the conversation relevant to the task, including its thread context.
3. Draft a short message with the answer, evidence, and next action.
4. Confirm the destination and use existing sending authorization; otherwise return the draft.
5. After a send, verify the message and retain a source link in private working context.

Do not import employee directories, infer recipients, or post to destinations from examples.
