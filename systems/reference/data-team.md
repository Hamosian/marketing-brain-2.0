<!-- last-reviewed: 2026-07-05 -->
# Data Team

> The Data Team (Business Operations org, not Marketing/Growth) runs analytics and data infrastructure requests through three monday boards in their own workspace: intake, execution, and an archive of closed quarters. We are a requester/consumer of this process, not an owner of it.

## Overview

The Data Team sits under Business Operations (Eyal Solnik, Head of Data, reports to Shira Sadoth Zafrir, VP Business Operations - see `references/other_teams.md` for the full org chart and Slack channel). They run their intake, execution and closed-quarter archive on three monday boards in a dedicated **`Data team` monday workspace** (workspace ID `1537478`) - separate from Marketing's own workspace. We do not own or administer these boards; we only submit requests and track their status.

This is a distinct surface from Rivermind (`systems/reference/rivermind.md`), which is the analytics team's self-serve Snowflake Q&A plugin. Rivermind is for answering data questions ourselves; these boards are for requesting the Data Team's own work (new pipelines, dashboards, one-off analyses, data bugs, etc.).

## How Claude Works With This

| Action | How |
|--------|-----|
| Submit a new request to the Data Team | `/data-team-request` - do not create items on **Data requests** (`18399446834`) directly |
| Track a submitted request | `/data-team-request`. It looks the request up by **item ID**, which stays the same on all three boards (see Workflow below) |
| Escalate or ask about priority | Slack `#data-marketing` (`C08283QUCNM`) |
| Do NOT | Create, edit, or move items on these boards without the request actually coming from a person - do not fabricate requests on someone's behalf. Never write to the Main operation or past-Qs boards at all |

## Boards

| Board | ID | URL | Use |
|-------|----|----|-----|
| 📝 Data requests | `18399446834` | https://riversidefm.monday.com/boards/18399446834/views/235554933 | Intake. Anyone (Marketing included) submits new data requests here via `/data-team-request`; do not create items directly on the board or its form. Prioritized items leave this board, so it only holds requests not yet prioritized or cancelled. 24 items as of 2026-10-01. |
| ⚙️ Data group - Main operation board | `18399485085` | https://riversidefm.monday.com/boards/18399485085/views/235787894 | Execution for the current and next quarter. 592 items as of 2026-10-01. |
| Data group past Qs | `18426192716` | https://riversidefm.monday.com/boards/18426192716 | Archive of closed quarters (groups `Q4 2025`, `Q1 2026`, `Q2 2026`). 459 items as of 2026-10-01. **Its Status column is meaningless** (see Workflow). |

### Workflow - how a request actually moves (verified 2026-10-01)

A request is one item with one ID for its whole life. It is **moved** between boards, never copied, and the item ID never changes.

1. **Filed** on Data requests. An automation sets Status to `New request` and notifies whoever is in `People`.
2. **Prioritized.** The "Prioritize" button ("Move to operation", automation `533577861`) moves the item to the Main operation board, into the current-quarter open group. The Data Team also moves intake items there by hand, sometimes into the next-quarter group. Either way the ID is kept and nothing stays behind on the intake board. Request Type, Priority, Stakeholder's team, Stakeholder, People, Files and the Spec link carry over; Completion date lands in `Needed completion date` and Please Elaborate in `Description`.
3. **Arrives as `Backlog`.** An ops-board automation (`533698891`) sets Status to `Backlog` on every item moved in, whatever its intake status was. From there the Data Team works the status, and `Done` items auto-move to the `Current Q - Closed tasks` group.
4. **Archived after its quarter closes.** Closed-quarter items are moved in bulk to Data group past Qs, again keeping their IDs. Seen once so far: on 2026-08-12, every item in the `Q4 2025`, `Q1 2026` and `Q2 2026` groups (459) moved in one batch, 11 days after Q3 began. That board was cloned from the ops board the same morning, automations included, so the copied "moved to this board, set Status to `Backlog`" rule fired on all 459: 413 had been `Done`, 45 `Cancelled`, 1 `Working on it`. All 459 still read `Backlog` and none has been edited since. Expect the same after Q3 closes on Oct 31, but that is not yet observed.

**Reading status from this:**

- On the intake and ops boards, Status is live.
- On past Qs, ignore Status. The real last status is only in the activity log: on `18426192716` the archive move's status change carries it in `previous_value`, and the full history stays in the ops board's log (`18399485085`), which keeps events for items that have since left it.
- Items do get deleted on the ops board: 8 of the 87 prioritized between 2026-06-01 and 2026-09-30. A deleted item reads back empty or `state: deleted` by ID, and the ops log holds the `delete_pulse` event and who did it.
- Match by item ID, never by title. The Data Team renames items after prioritization, and a same-named item on another board is a separate request: three such pairs exist, each second item created by hand by a Data Team member days or weeks apart from the move. There is still no `board_relation` column linking anything.

Evidence (activity logs for 2026-06-01 to 2026-09-30, read 2026-10-01): 87 `move_pulse_from_board` events on intake (62 by the button's automation, 25 by hand) match 87 `move_pulse_into_board` events on ops with the same item IDs, and the automation created no items on ops; 459 `move_pulse_into_board` events on past Qs, all between 06:51 and 06:52 UTC on 2026-08-12; 459 of 459 past-Qs items read `Backlog`, including 197 of 197 created since 2026-05-15.

## Column Schema

### Data requests (intake)

| Field | Column ID | Type | Notes |
|-------|-----------|------|-------|
| The Request | `name` | name | |
| Status | `status` | status | New request, In review, Need clarifications, Cancelled |
| Please Elaborate | `long_text_mm0e1x8v` | long_text | Full request detail |
| Request Type | `color_mm0e440v` | status | See taxonomy below |
| Priority | `color_mm0enpkh` | status | Show stopper / High / Medium / Low |
| Stakeholder's team | `color_mm0edqfa` | status | Requester's department |
| Stakeholder | `multiple_person_mm0ew969` | people | Who is asking |
| People | `multiple_person_mm0eafd5` | people | Which Data team member will work it |
| Completion date | `date_mm0ew99d` | date | Requested deadline |
| Created at | `date_mm0ea54f` | date | |
| Spec | `linkbm9mth9s` | link | Optional detailed spec doc |
| Files | `filechb6jupr` | file | |
| Estimated Days | `numeric_mm1jsy98` | numbers | |
| Prioritize (button) | `button_mm0eszvh` | button | "Move to operation": moves the item (same ID) to the ops board, see Workflow |

### Data group - Main operation board (execution)

| Field | Column ID | Type | Notes |
|-------|-----------|------|-------|
| Task name | `name` | name | |
| Status | `status` | status | Backlog, Ready, Working on it, Waiting for others, Waiting for stakeholder's review, Waiting for PR, Monitoring, Stuck, Done, Cancelled |
| Priority | `color_mm0enpkh` | status | Same scale as intake |
| Request Type | `color_mm0e440v` | status | Same taxonomy as intake, plus "Data bugs" |
| Stakeholder's team | `color_mm0edqfa` | status | Same as intake, plus Cross Company |
| Stakeholder | `multiple_person_mm0ew969` | people | |
| Data team member(s) | `multiple_person_mm0eafd5` | people | |
| Is Planned? | `color_mm0f7qw1` | status | Planned / Unplanned |
| Needed completion date | `date_mm0f2vvp` | date | |
| Task size | `color_mm0x5x3` | status | Small (2d), Medium (5d), Large (10d), XL (20d) |
| Team | `color_mm0nmhqm` | status | Internal Data sub-team: Analysts, DE, AE, Agentic |
| Sprint No | `dropdown_mm0nvmvd` | dropdown | |
| Description | `long_text_mm0xcxr6` | long_text | |
| Spec / Link / Git Branch | `link_mm0fgn49` / `link_mm0ff02f` / `link_mm0pmx7b` | link | |

Groups as of 2026-10-01: `Q3 2026 (Aug 1st - Oct 31th) - Current Q open tasks` (`topics`, where the Prioritize button lands items), `Current Q - Closed tasks` (`group_mm0hhdv0`), `Next Q - Q4 2026` (`group_mm0eycg`). Titles roll each quarter; closed quarters move to Data group past Qs.

### Data group past Qs (archive)

Cloned from the Main operation board on 2026-08-12, so the columns above keep the same IDs here (`name`, `status`, `color_mm0enpkh`, `color_mm0e440v`, `color_mm0edqfa`, `multiple_person_mm0ew969`, `multiple_person_mm0eafd5`, `link_mm0fgn49`). `status` reads `Backlog` for every item regardless of outcome; see Workflow.

## Request Type taxonomy (shared by both boards)

`Analysis`, `Data infra`, `Dashboard`, `Documentation`, `A/B test`, `Data spec`, `Pull data`, `Other`, and (main ops board only) `Data bugs`.

## What Marketing actually submits (as of 2026-07-05 review)

Reviewed all 19 intake items and all 530 main-ops items.

- **Marketing is the single largest non-Data-internal requester.** By `Stakeholder's team` on the Main operation board: Data (internal, 93) > Product - Core (111) > **Marketing (82)** > 75 unset > RevOps (55) > CSM (31) > Finance (28) > Product - Growth (21) > Cross Company (12) > BD (9) > Sales (6) > Support (3) > Engineering (3). On the intake board, 12 of 19 open items (63%) are tagged Marketing.
- **Breakdown of Marketing's 82 main-ops items by Request Type:** Analysis 33 (40%), Data infra 22 (27%), Pull data 6, Dashboard 5, Other 5, Data bugs 4, A/B test 3, Data spec 2, unset 2.
- **Status:** 65 of 82 Marketing items are Done; 6 Working on it, 3 Ready, 3 Backlog, 2 Waiting for others, 1 Cancelled, 1 Monitoring, 1 Waiting for stakeholder's review.
- **Recurring themes:**
  - MQL/SQL funnel and attribution health (`mkt<>gtm funnel - *` series, `MQL Drop Investigation`, `Inbound SQL Drop Investigation`, `SQL/MQL Attribution`, `Quality MQL`, `Marketing ROI`)
  - PLG/self-serve diagnostics (`Self Serve RCA`, `Self Serve Root Cause Analysis`, `Self-serve expansion revenue`, `Abandoned cart opportunity`, `Free-Plan Cannibalisation Risk`)
  - Paid acquisition attribution infra (AppsFlyer modeling/integration, Impact.com Attribution Audit, PartnerStack integration, Bing/OpenAI Snowflake pipelines, server-side conversion events to Google/Meta/LinkedIn/OpenAI Ads via Hightouch)
  - Omni dashboards (A/B Tests dashboard, ICP dashboard, Product Marketing Dashboard, Pricing quiz funnel dashboard)
  - Marketing-funnel data bugs (`Fixing first mrr in marketing funnel`, `Investigating and Fixing Trials in Marketing Funnel`, missing data on Product-Marketing Dashboard)
  - A/B test support (Pricing Page A/B, Font Type A/B, No-free LP A/B test)
- **Notable open item to be aware of:** `Issue with Hubspot data sync for Customer plan contact properties` (intake, High priority, opened 2026-07-05) - free-plan/payment-interval counts in HubSpot (synced via Hightouch) don't match Snowflake (`fs.users`), and this property drives churn-indication marketing segmentation (e.g. email audiences). Worth tracking to resolution since it affects live segmentation.

## Rules That Affect Us as a Requester

- We don't own this process or its schema - if it changes, re-run this review rather than trusting this snapshot as permanent.
- Route requests through `/data-team-request` (which files on the **Data requests** board), not directly to a Data Team member - it's the documented entry point.
- Track a request by its item ID, which survives every move. Never report the Status shown on Data group past Qs; read the item's activity log instead (see Workflow).
- Escalate blocked or unclear requests in `#data-marketing`, not by DMing individual Data Team members.
