---
name: good-morning
description: Use this skill when the user says "good morning", "morning brief", "daily brief", "daily standup", "catch me up", "what happened overnight", "what's going on today", "start of day", or wants a daily summary of active monday work, team updates, Slack activity, open risks, and recommended actions.
---

# Good Morning Brief

Generate a daily morning brief for the team member. The goal is to give them everything they need to orient themselves in 60 seconds: their active work, urgent unowned items, what needs a decision, and what's happening in Slack.

Fetch ALL data in parallel before rendering anything. Speed matters here - this is the first thing someone does in the morning.

---

## Step 1: Read Source Registry and Fetch Everything in Parallel

Read the **Morning Brief Sources** table from `CLAUDE.md`. For each source where Enabled = "Yes" (not commented out), launch the corresponding fetch in parallel. Skip sources that are commented out or not present.

### Source: Active tasks (monday)
Marketing Ops does not run sprints. Do not call `get_sprints_metadata`. This does NOT mean skip grouping entirely - see below.

Use `mcp__monday-api__get_board_items_page` on the configured tasks board.

Configure the filters and columns based on your team's board schema in `references/monday_boards.md`. At minimum:
- Filter to tasks owned by the current user
- Filter to statuses that are not Done, Closed, or Cancelled
- **Also filter by group if the board has them.** On the Marketing Operations Tasks board, `Backlog` and `On Hold` groups hold long-parked items that are technically not Done but are not part of today's workload - exclude them, or overdue/workload counts will be wildly inflated with stale, already-shelved work. Check `references/monday_boards.md` for the current group IDs.
- Prioritize items due today, due this week, overdue, or marked P0/P1 - computed over the group-filtered active set, not the raw status-filtered set
- Fetch the columns you want shown in the brief: owner, status, priority, type, due date, name, board URL

### Source: Unowned bugs (monday)
Same board, different filter: bug or issue items with no owner and status not Done/Closed. Look up type label names or IDs from `references/monday_boards.md` when available.

### Source: Slack (slack)
```
mcp__plugin_slack_slack__slack_read_channel(channel_id: "<channel_id_from_config>", limit: 50, response_format: "concise")
```

If additional channels are added to `CLAUDE.md`, read them in parallel with the team channel.

**Private channels depend on who runs the brief.** The default team channel (`#growth-marketing-leaders`, `C0A4Y0BD3BR`) is private and limited to Nir Taranto's direct reports. If the read returns `channel_not_found`, the runner's Slack connection isn't a member - the channel is not archived or renamed. Skip the source, substitute a channel the runner can access from `references/slack.md`, and say so in the brief instead of failing.

### Source: Open PRs (github)
Only if enabled in the source registry. For each repo listed in the config:
```bash
gh pr list --repo <org>/<repo> --state open \
  --json number,title,author,createdAt,reviewRequests,isDraft \
  | jq '[.[] | select(.isDraft == false) | select(.author.is_bot == false)] | .[:5]'
```

**Team GitHub logins** (for filtering shared repos): Read the `GitHub logins` field from the Team section in CLAUDE.md (pipe-separated list, e.g. `user1|user2|user3`).

**Bot/noise exclusions**: `dependabot` and any `is_bot == true` accounts. Add team-specific CI bot logins here as needed.

### Source: Merged PRs (github)
Only if enabled in the source registry. Compute the cutoff as 6 AM UTC yesterday:
```bash
CUTOFF=$(date -u -v-1d '+%Y-%m-%dT06:00:00Z' 2>/dev/null || date -u -d 'yesterday 06:00' '+%Y-%m-%dT06:00:00Z')
gh pr list --repo <org>/<repo> --state merged --limit 50 \
  --json number,title,author,mergedAt \
  | jq --arg cutoff "$CUTOFF" '[.[] | select(.author.is_bot == false) | select(.mergedAt > $cutoff)]'
```

### Source: PagerDuty (pagerduty)
Only if enabled in the source registry. Fetch both in parallel:
```
mcp__plugin_pagerduty_pagerduty__list_incidents(
  teams_ids: ["<team_id_from_config>"],
  since: <now minus 24h as ISO8601>,
  sort_by: ["created_at:desc"],
  limit: 50
)

mcp__plugin_pagerduty_pagerduty__list_oncalls(
  escalation_policy_ids: ["<escalation_id_from_config>"],
  earliest: true
)
```
Fetch ALL incident statuses (triggered, acknowledged, resolved).

---

## Step 2: Render the Brief

**Important:** Only render sections for sources that were enabled and fetched. If a source is not in the Morning Brief Sources table (or is commented out), skip that entire section silently. Do not show empty sections or "not configured" messages.

Use this exact structure. Keep it tight - this is a morning brief, not a report.

### Header
```
# Good Morning Brief - [Weekday, Month DD, YYYY]
```

---

### Active Work - Your Tasks

Start with a one-line workload summary:

```
Active work: [N] open, [X] overdue, [Y] due this week, [Z] P0/P1
```

Then a table of tasks:

| Task | Status | Priority | Due |
|------|--------|----------|-----|
| [name](url) | emoji + label | label | date |

Status emojis: In Progress, Pending Review, Ready to start, Done, Stuck

One short insight below the table (1-2 sentences max). Flag overdue P0/P1 work, too many simultaneous "In Progress" items, or stale "New" investigations. Keep it actionable, not preachy.

---

### Unowned Bugs

If none: "> No unowned bugs or issues need assignment."

If any, a table:
| Bug | Age |
|-----|-----|
| [name](url) | X days |

Note: if the bug has been sitting for >7 days, flag it - it needs an owner or a close decision.

---

### Slack Highlights

**#growth-marketing-leaders** (last 48h)

Pull only the last 48 hours of messages. List 3-5 key items max. Each item is one line:
- Lead with an emoji that fits the vibe
- Name the person
- One-sentence summary
- If it's an open question or needs a response, add **unanswered** or **needs decision** in bold at the end

---

### PRs Open for Review

Single combined table across all repos, sorted by age ascending (newest first):

| # | Repo | Title | Author | Age |
|---|------|-------|--------|-----|
| [#N](url) | repo-name | title | Name | 3d |

- Mark your own PRs with **you** - those need someone else's review.
- Flag PRs older than 7 days.
- Skip bots and non-team contributors (use the GitHub login allowlist above).

If no team PRs open: "> No open team PRs right now."

---

### Merged Yesterday

Narrative format, grouped by system area. Last 24 hours, team only.

For each area with merged PRs, write a header with an emoji, then one bullet per person who merged something. Link PR numbers inline (e.g. [#123](url)). Highlight if it was you with **you**.

<!-- Customize these system groupings for your team. Examples: -->
<!-- **Backend** - API changes, service updates -->
<!-- **Frontend** - UI, client-side changes -->
<!-- **Infrastructure** - CI/CD, config, tooling -->
<!-- **Team** - team context, skills, docs -->

One line at the bottom: "N merges across the team yesterday."

If none: "> No team merges in the last 24 hours."

---

### PagerDuty - Last 24 Hours

Start with who is currently on-call:
```
On-call: **[Name]** (until [date])
```

If on-call data is unavailable, omit the line rather than showing an error.

Then show a table of all incidents from the last 24 hours, sorted newest first:

| # | Status | Title | Service | Assigned To | Age |
|---|--------|-------|---------|-------------|-----|
| [#N](url) | status | short title | service name | Name | 2h |

- PagerDuty incident URL pattern: `https://n-a.pagerduty.com/incidents/<id>`
- If no incidents in the last 24h: "> No incidents in the last 24 hours."

One line summary below the table: "X open, Y acknowledged, Z resolved in the last 24h."

---

### Suggested Actions

After rendering the full brief, present 3-5 concrete action items derived from the data. Use `AskUserQuestion` with `type: "select"` to let them pick what to act on first.

Options should be specific and actionable, pulled directly from the brief. Include a "Nothing, I'm good" option as the last choice. If the user picks something, help them act on it immediately.

**End-of-month nudge:** if today's day-of-month is 22 or later, add one more option: "Run the monthly backlog review (`/mops-backlog-review`)" - a good time to groom parked/on-hold work since it's the last week of the month. Suggestion only - never run it automatically, and skip this option on any other day.

---

## Key Principles

- **Speed over completeness.** Fetch everything in parallel. Don't paginate Slack unless the first page gives almost nothing.
- **No sprint calls, but DO filter by group.** Marketing Ops does not run a monday-native sprint board, but it does use manual groups (weekly buckets, `Backlog`, `On Hold`) to separate active work from parked work. Filter those out before computing overdue/workload numbers - see `references/monday_boards.md`.
- **Team-only GitHub data.** If PRs are enabled, use the GitHub login allowlist strictly. A non-team PR in the table is confusing and wrong.
- **48h for Slack, since yesterday morning (6 AM UTC) for merged PRs, most recent 5 for open PRs.** Only applies to enabled sources.
- **One line per Slack item.** If you can't summarize it in one line, it's not important enough for the morning brief.
- **No padding.** If a section is empty, say so cleanly and move on. Don't write "I was unable to find any..." - just say "No unowned bugs this sprint."
- **Emoji in section headers** makes the brief scannable at a glance. Use them.
