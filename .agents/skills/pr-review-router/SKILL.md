---
name: pr-review-router
description: Automation skill that routes newly opened pull requests on riversidefm/marketing-brain to the marketing manager who owns the area the PR touches, and DMs them a Slack nudge to review and approve or request changes on GitHub. Routing is by files changed - brand/design -> Raz Messing, PMM/content/social -> Sivan Mazuz, everything else -> Nir Taranto. Runs once daily as a cloud routine, or on demand. Trigger phrases - "route PRs to managers", "PR review router", "notify managers about open PRs", "who should review this PR", "run the PR review router".
---

# PR Review Router

The "communication agent" for pull-request review. When a PR is opened against `riversidefm/marketing-brain`, this skill works out which marketing manager's area it touches and DMs that manager a short Slack nudge with the PR link, so review-and-approve happens without anyone chasing.

**This is a sanctioned automation skill.** Like `access-welcome`, it is authorized to send its DM **without per-message confirmation**, but only under the guardrails below. It never improvises message content and never notifies a manager it cannot resolve to a routed area.

## What it can and cannot do

- **It is a nudge, not an approval.** Slack cannot approve a PR. The DM links to the PR; the manager approves or requests changes **on GitHub**. Do not claim a PR was approved.
- **It polls; it is not instant.** As a daily cloud routine it wakes once a day and processes every PR opened since it last ran. Expect up to a day between PR-open and DM. This is a Claude cloud routine (`RemoteTrigger`), not a GitHub webhook.
- **Managers.** Route only to these three (source of truth `references/team.md`):

  | Manager | Slack ID | Sub-org |
  |---|---|---|
  | Raz Messing | `U08HMKEAYC8` | Brand |
  | Sivan Mazuz | `U08KPU4E7PW` | Marketing (PMM, content, community, social) |
  | Nir Taranto | `U07LETHMPAP` | Growth Marketing (catch-all) |

  Note there are two people named Raz. This is Raz **Messing** (Brand), never Raz Navon (Paid Acquisition).

## Guardrails (non-negotiable)

1. **Fixed template only.** Send the message body from `tracking.md` verbatim, substituting the marked fields only (`{FIRST_NAME}`, `{PR_TITLE}`, `{PR_NUMBER}`, `{PR_URL}`, `{AUTHOR}`, `{AREA}`, `{FILE_COUNT}`). Never rewrite it. Keep the `_Posted by the Marketing OS agent_` footer.
2. **Notify each PR once per manager.** Anything already in the Processed log for that `(PR number, manager)` pair is never re-messaged. Re-opened or updated PRs do not re-fire.
3. **Skip drafts and bots.** Do not route draft PRs, and do not route PRs authored by bots/service accounts (`github-actions[bot]`, `dependabot[bot]`, and anything ending in `[bot]`). The graph/embedding refresh commits are direct CI commits, not PRs, so they are irrelevant here anyway.
4. **Only PRs targeting `main`.** Ignore PRs opened against other bases.
5. **No routed area, no DM.** If a manager cannot be resolved for a PR (should not happen given the catch-all, but if the map ever removes it), do not guess - alert Hanan (`U0A3HCFE90S`) and mark the PR `alerted`.

## Routing: files changed -> owning manager

For each PR, list the changed files and match every file against the map below in order. A PR can match more than one manager (it DMs each matched manager once). Any file that matches **neither** Raz nor Sivan is a Nir file, so a PR touching any general/Growth/systems/CLAUDE.md content routes to Nir.

**Raz Messing - Brand** (`U08HMKEAYC8`):
- `.claude/skills/riverside-brand-guidelines/**`
- `.claude/skills/riverside-ux-patterns/**`
- `.claude/skills/riverside-presentation/**`
- `.claude/skills/video-project-intake/**`
- `references/design-system/**`
- `.claude/agents/marketing/marketing-brand-design-director.md`

**Sivan Mazuz - Marketing / PMM / content / social** (`U08KPU4E7PW`):
- `references/messaging/**`
- `.claude/skills/content-agent/**`
- `.claude/skills/*-copytemplates/**`
- `.claude/agents/marketing/marketing-content-creator.md`
- `.claude/agents/marketing/marketing-social-media-strategist.md`
- `.claude/agents/marketing/marketing-pr-communications-manager.md`
- `.claude/agents/marketing/marketing-instagram-curator.md`
- `.claude/agents/marketing/marketing-tiktok-strategist.md`
- `.claude/agents/marketing/marketing-twitter-engager.md`
- `.claude/agents/marketing/marketing-x-twitter-intelligence-analyst.md`
- `.claude/agents/marketing/marketing-linkedin-content-creator.md`
- `.claude/agents/marketing/marketing-global-podcast-strategist.md`
- `.claude/agents/marketing/marketing-email-strategist.md`

**Nir Taranto - Growth (catch-all)** (`U07LETHMPAP`):
- Every path not claimed above: `CLAUDE.md`, `PHILOSOPHY.md`, `systems/**`, most of `references/**`, `docs/**`, `evals/**`, `scripts/**`, `tools/**`, and every skill/agent not listed under Raz or Sivan.

`{AREA}` in the message is the manager's sub-org label ("Brand", "Marketing", or "Growth Marketing"). When a PR routes to more than one manager, each gets their own DM naming their own area; note in the report that the PR was multi-routed.

**The map is meant to be tuned.** `references/design-system/` is the *product* design system, mapped to Raz as the nearest owner; if the department decides otherwise, edit this table (and open a PR). When in doubt about a path, it falls to Nir by design.

## Steps

### 1. Load state
Read `.claude/skills/pr-review-router/tracking.md`. Parse the Processed log (the set of already-handled `(PR#, manager)` pairs) and the message template.

### 2. List open PRs
```bash
gh pr list --repo riversidefm/marketing-brain --state open --base main \
  --json number,title,author,isDraft,url,createdAt,files --limit 100
```
Drop drafts (`isDraft: true`) and bot authors (login ends in `[bot]`). For the rest, `files` gives the changed paths for routing.

### 3. Route each PR
For each remaining PR, match its changed files against the map above to produce the set of owning managers. Then subtract any `(PR#, manager)` pairs already in the Processed log. What remains is this run's DMs.

If nothing remains, log "no PRs to route" and stop (no commit).

### 4. Send the DM
For each `(PR, manager)` to notify, send the template via Slack `slack_send_message` to the manager's Slack ID, substituting the marked fields. `{FIRST_NAME}` is the manager's first name; `{AREA}` is their sub-org label. Restore real newlines when sending. Keep the footer.

### 5. Update state and persist
For every `(PR#, manager)` handled this run, append a row to the Processed log with today's date and status `notified`, `alerted` (unresolved, Hanan notified), or `skipped` (draft/bot - optional to log). Then commit so state survives to the next run:
```bash
git add .claude/skills/pr-review-router/tracking.md
git commit -m "pr-review-router: notified <PR#s> (<managers>)"
git push
```
(In a cloud routine, commit on the routine's branch / open a PR per the routine's convention. Only commit when something changed.)

### 6. Report
Summarize: which PRs routed to which managers, which were multi-routed, which were skipped (draft/bot), and any alerts. If run interactively, print it; as the routine, this is the routine's output.

## Notes
- **Cloud-routine Slack caveat:** a headless cloud run may not have an authed Slack connection. If `slack_send_message` is unavailable or fails, do **not** mark anyone `notified`; leave the pair unprocessed so the next run (or a local run) retries, and surface the failure in the report. (Same failure mode documented in `access-welcome`.)
- **Idempotency is per pair, not per PR.** A PR that routes to two managers records two rows; if one DM fails, only the failed pair retries.
- **Cadence:** once daily. The cron lives on the registered routine, and the intended local time is recorded next to it per `references/change-control.md` (cron is UTC-only). This skill doc is the behaviour; the routine is what performs it - both must exist for the cadence to be real.
- **Registering the routine:** merge this skill to `main` first, then register the daily routine (or register disabled and enable after merge). A routine clones `main`; an unmerged skill does not exist to it. See the cloud-routine section of `references/change-control.md`.
