---
name: access-welcome
description: Automation skill that welcomes new collaborators on the riversidefm/marketing-brain repo. Polls the GitHub collaborator list, finds anyone not yet processed, resolves them to a Slack identity, and DMs them the standard repo activation guide. Runs daily as a cloud routine, or on demand. Trigger phrases - "welcome new repo members", "check for new collaborators", "run the access welcome agent", "who got repo access".
---

# Access Welcome agent

The "communication agent" for repo onboarding. When someone is granted access to `riversidefm/marketing-brain`, this skill DMs them the activation guide so they can turn the Marketing OS brain on without anyone being asked.

**This is a sanctioned automation skill.** Per `CLAUDE.md`, it is authorized to send the welcome DM **without per-message confirmation**, but only under the guardrails below. It never improvises message content and never guesses a recipient.

## Guardrails (non-negotiable)

1. **Only the fixed template.** Send the message in `tracking.md` verbatim, substituting `{FIRST_NAME}` only. Never rewrite it.
2. **Never guess a recipient.** Only DM a handle resolved to a Slack ID with high confidence (see Step 3). If unsure, alert Hanan and mark `alerted`. A wrong DM is worse than a missed one.
3. **Welcome each person once.** Anything in the Processed log is never re-messaged.
4. **Send only to humans newly granted access.** Skip bots/service accounts and anyone already in the log.
5. **Never welcome someone who has left Riverside.** If `references/team.md` (Joiners and departures) or a note in `tracking.md` records the person as departed, log them `skipped` and send nothing (`timseneker-source`, 2026-09-06, is the worked case in `tracking.md`). Repo access can outlive employment.

**Done when:** every handle in `new_handles` has exactly one new Processed-log row (`welcomed`, `alerted` or `skipped`), every `welcomed` row matches a DM that Slack confirmed as sent, the change to `tracking.md` is committed, and the report below is printed. A run where Slack failed is not done for those people: they stay unlogged.

## What this skill does not own

This skill sends one fixed DM when GitHub access lands. It does not write a new hire's onboarding doc or plan their first 90 days (`/onboarding-doc-builder`), and it does not answer "tell me about the team" or "what do you know about me" (`/team-intro`). Granting repo access is a person's job; this skill only reacts once access is accepted.

## Steps

### 1. Load state
Read `.claude/skills/access-welcome/tracking.md`. Parse the Handle map, the Processed log (set of already-handled handles), and the message template.

### 2. List current collaborators
```bash
gh api "repos/riversidefm/marketing-brain/collaborators?per_page=100" --jq '.[].login'
```
`new_handles = current collaborators − handles in Processed log`. If empty, log "no new collaborators" and stop (no commit).

### 3. Resolve each new handle to a Slack identity
For each handle in `new_handles`, resolve in this order, stopping at the first high-confidence hit:
1. **Handle map** in `tracking.md`.
2. **Roster match** - fetch the GitHub user's name/email (`gh api users/<handle> --jq '{name,email}'`) and match against `references/team.md` by email or full name.
3. **Slack search** - search Slack users by the name or email from step 2.

If resolved with high confidence → recipient = that Slack ID + first name. If not → **do not DM**; queue an alert to Hanan (`U0A3HCFE90S`) naming the unresolved handle, and mark it `alerted`.

### 4. Send the welcome DM
For each resolved recipient, send the template via Slack `slack_send_message` to their Slack ID, substituting `{FIRST_NAME}`. Restore the real newlines and code fences when sending (the template stores the body inline). Keep the `_Posted by the Marketing OS agent_` footer.

### 5. Update state and persist
For every handle processed this run, append a row to the Processed log: `welcomed` (DM sent), `alerted` (unresolved, Hanan notified), or `skipped` (bot/service account, or departed per rule 5). Use today's date. Also add any newly resolved handle to the Handle map for next time.

Then commit the change so state survives to the next run:
```bash
git add .claude/skills/access-welcome/tracking.md
git commit -m "access-welcome: log <handles> (<statuses>)"
git push
```
(In a cloud routine, commit on the routine's branch / open a PR per the routine's convention. Only commit when something changed.)

### 6. Report
If run interactively, print the report; if run as the routine, this is the routine's output. Fixed sections, always present, "none" when empty. Every name and Slack ID comes from the source that resolved it (handle map, roster or Slack search); never invent one.

Output format, for example as it would read for the `jonathanydov` row logged 2026-09-28 (name and Slack ID as the handle map holds them; the source line names whichever of the three Step 3 sources resolved the handle):

```
Access welcome - 2026-09-28
Welcomed (1): jonathanydov -> Jonathan Ydov (U0C0T6TUC8Y), source: handle map
Alerted (0): none
Skipped (0): none
State: tracking.md committed
Failures: none
```

When Slack was unavailable, `Welcomed` reads "none", the handles waiting for a retry are listed under `Failures`, and `State` says nothing was logged for them.

## Notes
- **Cannot see pending invitations** (needs repo admin; this token has write only). The skill only sees access once the person has *accepted* and appears in the collaborator list. That is the intended trigger point anyway - they can act on the DM immediately.
- **Cloud-routine Slack caveat:** a headless cloud run may not have an authed Slack connection. If `slack_send_message` is unavailable or fails, do **not** mark anyone `welcomed`; leave them unprocessed so the next run (or a local run) retries, and surface the failure in the report.
- The canonical activation content lives in `docs/ACTIVATE.md`. If those steps change, update the template in `tracking.md` to match.
