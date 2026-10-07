---
name: nir-monthly-report
description: Build the monthly task report for Hanan's manager Nir as a clean Riverside-branded .docx. Pulls a full month of task data from the MOPs and Website Dev Monday boards plus context from four Slack channels, then renders four sections (Month at a Glance, What We Delivered, What Is In Progress, Next Month Priorities). Trigger with "monthly report for Nir", "Nir's monthly report", "monthly task report", "MOPs monthly report", or "/nir-monthly-report".
---

# Nir Monthly Task Report

Generate the monthly task report for Nir Taranto (Hanan's manager, Senior Director, Growth Marketing). It is a quick read: Nir should finish it in a few minutes. Pull a full month of work from two Monday boards, enrich with four Slack channels, and render a clean Riverside-branded `.docx`.

> **Cadence history:** the automated task-report moved to a monthly cadence on 2026-07-05, when Nir asked ("please work on the monthly by next Tue and no need for weekly"). This skill produces only the monthly; the separate weekly narrative Hanan files on the Growth Marketing Reports board is now `/nir-weekly-report`. Default reporting period is the most recently completed calendar month.

The report has **four content sections in this order**: Month at a Glance, What We Delivered, What Is In Progress, Next Month Priorities (preceded by a title block).

Run the data pulls (Monday + Slack) in parallel where possible. Confirm nothing with the user unless a board or channel is unreachable.

---

## Boards and channels (verified against `references/monday_boards.md`)

| Source | ID | Role in report |
|--------|----|----|
| Website Dev board ("DEV") | `18397093471` | All bi-weekly sprint groups overlapping the report month |
| MOPs board | `6257866754` | All weekly groups overlapping the report month **and** the "Nir's Requests" group |

| Slack channel | ID | What to mine |
|---------------|----|--------------|
| `#marketing-internal` | `C043B7GAMPC` | broad marketing context, completions, launches |
| `#mops-team-internal` | `C0AAQ15SVD3` | MOps delivery + in-progress signal (daily standups are a good month summary) |
| `#mops-priority-room` | `C0A9JUG9MPZ` | high-priority items, blockers |
| `#website-dev` | `C0AM2HQMY49` | dev priorities, go-live dates, deploy notes, blockers |

> **Known drift to handle:** Yuval has left Riverside; the Website Dev board owner role is Jonathan Ydov's from 2026-09-27 (covered interim by Jonathan Galili before that). The Webflow agency Flow Ninja executes: Milutin and Dusan develop, and Andrija ("Djura") leads. Flowout's Davor also executed until the week of 2026-09-20, so earlier months' threads name him. Look for whoever is currently posting dev-priority lists, go-live dates, deployment confirmations, and blockers.

---

## Step 1: Pull the month's task data from Monday

Tools live on the Monday MCP server (`get_board_info`, `get_board_items_page`).

**Resolve group IDs dynamically - never assume group names.** Both boards group work by date range, but with different cadences and formats:

- **MOPs board (`6257866754`)**: weekly groups (Sun-Thu work weeks) named like `0706 - 1106` (DDMM - DDMM) or `2806/06 - 0207/26`. A calendar month spans roughly 4-5 of these groups, including boundary weeks that overlap month edges.
- **DEV board (`18397093471`)**: bi-weekly sprint groups named like `22.06.26 - 03.07.26` (DD.MM.YY). A month spans 2-3 of these.

For each board:

1. Call `get_board_info` and read the group list. Select **every group whose date range overlaps the report month**, including boundary weeks/sprints that spill into adjacent months.
2. Also select the **"Nir's Requests"** group on the MOPs board.
3. Call `get_board_items_page` with `includeColumns: true` and a `group` filter. The `group` filter accepts multiple group ids in one call (`operator: any_of`, `compareValue: [ids...]`), so one call per board is enough.
4. Restrict `columnIds` to `name`, `person`, `status` to stay under the 25KB response cap (the MOPs board has 900+ items).

### Columns to capture

| Field | MOPs (`6257866754`) | DEV (`18397093471`) |
|-------|---------------------|---------------------|
| Name | `name` | `name` |
| Assignee | `person` (owner) | `person` (assignee) |
| Status | `status` | `status` |

Capture per item: **task name, status, assignee.**

### Status semantics

Use the board schemas in `references/monday_boards.md` (filter by label `id`, not index).

- **MOPs `status`:** Done = `1`. Active = Working on it (`0`), Waiting for approval (`7`), Pending (`2`), Test is Open (`8`). Treat Waiting-for-approval / Pending as the "Waiting/Stuck" parenthetical cases. New (`6`) items from the month feed Next Month Priorities.
- **DEV `status`:** Done = `1`, Published = `8` (also a completion). Active = Working on it (`0`), QA (`7`), Ready for QA (`11`), Ready for live (`10`), Audit post-live (`13`). Stuck = `2`, HOLD = `3` (note as blocked). New = `6`, Next item (`4`) feed Next Month.
- **Dedupe recurring tasks**: monthly recurring items (e.g. "Impact - Subscription Cancellations") can appear once per week/sprint group. List them once, noted as recurring if relevant.

---

## Step 2: Pull Slack context

Search each channel for the **report month** with `slack_search_public_and_private` (Slack MCP server). Use `in:<#CHANNEL_ID> after:YYYY-MM-DD before:YYYY-MM-DD` with `sort: timestamp`; one query per channel is usually enough (run in parallel, paginate if the month was busy). Use the context to **enrich**, not duplicate, the Monday data - especially launches, go-lives, and blockers not captured on the boards.

- `#website-dev` (`C0AM2HQMY49`): go-live / launch dates, deployment-confirmed-live notes, and blockers.
- `#mops-priority-room` (`C0A9JUG9MPZ`) and `#mops-team-internal` (`C0AAQ15SVD3`): completions, blockers, what the team turned to next. The daily standup posts in `#mops-team-internal` summarize open counts and risks well.
- `#marketing-internal` (`C043B7GAMPC`): launches and results worth a delivered bullet or a glance highlight (e.g. launch metrics).

Keep only signal that maps to one of the report sections.

---

## Step 3: Build the report as a simple .docx

Use the **docx skill** (`anthropic-skills:docx` - Node.js + the `docx` npm package). Keep formatting clean and minimal. This is a manager's quick read, not a design piece.

### Brand styling (apply lightly)

```
PURPLE     = "7C5CFF"
NEAR_BLACK = "0F0F14"
MID_GRAY   = "2A2A35"
LIGHT_GRAY = "E6E6EB"
```

- **Font:** Arial throughout.
- **Title:** 28pt bold NEAR_BLACK.
- **Section headers:** 16pt bold PURPLE with a thin PURPLE bottom border.
- **Body / list items:** 11pt NEAR_BLACK.
- **Page:** US Letter (12240 x 15840 DXA), 1-inch margins.
- **Header:** `Riverside | Monthly Task Report` with a right-aligned date.
- **Footer:** page number, centered.
- **Lists:** `LevelFormat.BULLET` via a numbering config. **Never** paste unicode bullet characters.
- **No complex tables.** Simple bullet lists only.

### Report structure (four sections + title block, in this order)

**1. Title block**
- "Monthly Task Report"
- The report month and the work-week range it covers (e.g. "June 2026 (work weeks of May 31 to July 2)")
- "Marketing Operations + Website Development"

**2. Month at a Glance**
3-5 bullets max: delivered counts per board, the month's dominant theme (launches, big projects), one or two headline results from Slack (launch metrics, major ships), and the biggest date on next month's calendar.

**3. What We Delivered**
Two sub-headers: **Marketing Ops** and **Website Dev**. List every Done task as a simple bullet - **task name and assignee only**. No hours, no status labels, no extra columns. Group multi-phase efforts into one bullet where it reads better (e.g. "OpenAI advertising API: scoping, Pixel Phase 1, and CAPI").
- Marketing Ops bullets: MOPs month groups (Done = `1`) + Nir's Requests (Done = `1` within the month).
- Website Dev bullets: DEV month groups (Done = `1`, plus Published = `8`).
- Also fold in meaningful completions surfaced in Slack that aren't on the boards.

**4. What Is In Progress**
Two sub-headers: **Marketing Ops** and **Website Dev**. List every active task as a bullet - **task name and assignee**.
- Include: Working on it, QA, Ready for QA, Ready for live, Audit post-live, open tests.
- For Stuck / Waiting items, add a brief parenthetical, e.g. `(Stuck)` or `(Waiting for approval)`.

**5. Next Month Priorities**
A short **unified** list (no sub-grouping), 6-8 bullets max. Write each as an action with owner and, where known, a target date:
`Ship the pricing page relaunch, go-live target July 13 (Milutin, Dusan)`.
Draw from: next month's sprint/week groups (New `6` / Next item `4`), current dev-priority posts in `#website-dev`, upcoming go-live dates from Slack, and open items in Nir's Requests. Flag ownerless items with `(owner needed)`.

### Tone

- Plain language, no jargon.
- **No em-dashes** - use commas or colons instead.
- No emojis.
- Short and scannable.

### File output

- Filename: `MOPs_Monthly_Report_[YYYY-MM].docx` (e.g. `MOPs_Monthly_Report_2026-06.docx`).
- Save to the **session scratchpad directory** (the path provided in the harness environment for this session), not `/mnt/user-data/outputs/` (that path is from a different runtime and does not exist here).
- Validate with the docx skill's validator: `python scripts/office/validate.py <filepath>` (script ships with the docx skill bundle).
- Present the file to the user: use `present_files` if available, otherwise give the absolute path as a clickable link.

---

## Notes and conventions

- This is a **read + generate** workflow - no Monday or Slack writes. No confirmation needed unless a source is unreachable.
- If a resolved group is empty or a channel returns nothing, render that sub-section as a single line ("No items this month.") rather than omitting it silently, so Nir sees the section was checked.
- For assignee display names, the `person` column returns user ids; resolve to names via the item column values or `references/team.md` if needed.
- If something non-obvious comes up while running this (a renamed group, a new status label, a channel that moved), suggest `/retro` to capture it back into this skill or `references/monday_boards.md`.
