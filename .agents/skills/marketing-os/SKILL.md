---
name: marketing-os
description: Deprecated alias, kept only for backward compatibility. The marketing-os skill was renamed to marketing-brain. Prefer /marketing-brain. Older references and external callers that still invoke /marketing-os are forwarded here.
user-invocable: true
---

# marketing-os → renamed to marketing-brain

This skill was **renamed to `marketing-brain`**. `/marketing-os` is kept only so existing references and external callers (for example the Slack agent, or a cloud routine that still says `marketing-os`) keep working during the transition.

**Do this:** invoke the `marketing-brain` skill (Skill tool, `skill: "marketing-brain"`) and follow it exactly. The full top-level operating-agent behaviour, sub-agent registry, and routing all live there now. Do not route from this file.
