---
name: hubspot-workflow-qa
description: >
  Structured HubSpot workflow QA review for Marketing Operations. Trigger whenever someone reviews,
  checks, audits, signs off on, or troubleshoots a HubSpot workflow - new builds, modifications,
  pre-launch checks, post-launch verification - even if they don't say "QA". Also for a workflow QA
  checklist, logging workflow issues, validating enrollment triggers, branching logic, email sends,
  lead scoring rules, lifecycle stage changes, or confirming Slack/ad-platform integrations fire.
  Covers all workflow types: nurture sequences, lifecycle automation, lead scoring, internal
  notifications (Slack, task creation), deal pipeline automation, ad audience syncs.
---

# HubSpot Workflow QA Skill

This skill guides you through Riverside's official HubSpot workflow QA process. Apply it whenever a workflow is being built, modified, or reviewed - whether pre-launch or post-launch troubleshooting.

## Context

- **Team**: Marketing Operations (Marketing department)
- **Access level**: Super Admin in HubSpot
- **Scope**: Data flows and messaging flows across all HubSpot workflow types
- **Integrations in scope**: Slack notifications, PPC ad platform syncs (Google Ads, Facebook/Meta, LinkedIn)
- **Issue logging**: Google Document linked from a Monday.com ticket on [Marketing Operations Tasks board](https://riversidefm.monday.com/boards/6257866754)
- **Monday.com board ID**: `6257866754` (workspace: Marketing) - see `references/monday_boards.md` for the full column/label schema
- **Connected tools**: HubSpot MCP, Monday.com MCP, Slack MCP, Google Drive, Claude in Chrome

---

## Reading the Workflow (Claude in Chrome)

A QA review is only as good as what you actually read. The HubSpot editor renders the flow lazily and collapses most of it - `get_page_text` on the edit URL typically returns the trigger block and nothing else. Reading only what the canvas volunteers is how suppression lists and branch wiring get missed.

**Read the flow definition through the authenticated internal API, then cross-check the canvas.** One call returns enrollment criteria, every action, every connection, suppression lists, custom-code source and declared secrets:

```javascript
const tok = document.cookie.split('; ').find(x => x.startsWith('hubspotapi-csrf=')).split('=')[1];
const r = await fetch('/api/automation/v4/flows/<FLOW_ID>?portalId=9154210', {
  headers: { 'accept': 'application/json', 'X-HubSpot-CSRF-hubspotapi': tok }
});
window.__F = await r.json();
```

**Read `knowledge/reading-workflows-via-api.md` before doing this.** It carries the endpoint table, the action-type-id map, the graph-walk (including the `defaultBranch` vs `staticBranches[].connection` shape difference that produces false "orphaned branch" findings), the slice-reading pattern, and the rule against echoing secrets found in custom code.

### The canvas is the control, not the source

**Before reporting any structural finding, confirm it against the canvas.** It renders the flow in plain English, so it is both a second source and the version a human reviewer sees - it is what catches your own parsing errors. In the 2026-09-07 review an API misparse produced a false "the failure branch is orphaned" finding on a correctly wired workflow; the canvas showed the truth immediately.

The canvas is also strictly better for **filter direction**. `IN_LIST` and `NOT_IN_LIST` differ by three characters in JSON and are easy to skim past; the canvas spells them out - *"is member of X"* versus *"is not member of X"* - where an inverted exclusion is unmissable.

### Rules summary

1. **Read the flow definition via the API** - this is the step most likely to be skipped, and skipping it is how P0s survive QA
2. **Note the `revisionId`** - it is how you later prove a fix actually saved
3. **Walk every action** including custom-code `sourceCode`, and run the orphan check
4. **Cross-check the canvas** for filter direction and for anything you are about to report as a defect
5. **Never flag "needs verification"** for something the API returns. Only flag what genuinely needs a human: live tests, business intent, and anything configured outside HubSpot
6. **Never echo a credential** found in custom code into a report, update, or Slack message
7. **Document everything** - include the full trigger and branch conditions in the QA report

---

## QA Process (5 Steps)

### Step 1 - Intake (Auto-Discover → Ask)

The user provides the HubSpot workflow URL (and optionally a Monday.com ticket URL). Claude does the rest.

#### A. Auto-discover (do this before asking the user anything)

1. **Read the flow definition** - Navigate to the workflow URL in Chrome, then pull the full definition through the internal API (see "Reading the Workflow" above and `knowledge/reading-workflows-via-api.md`): name, status (ON/OFF), object type, enrollment trigger, re-enrollment, suppression lists, every action and how they connect. Note the `revisionId`. Cross-check the canvas for filter direction.
1b. **Check whether it is a clone** - search the portal for the workflow's own name minus its distinguishing qualifier (e.g. `Webhook`, `Segment Webhooks`) and look for a sibling with near-identical structure. If one exists, run the cloned-workflow checks in Step 3 before anything else. A clone's inherited settings are the single richest source of P0s in this portal.
2. **Search Monday.com board `6257866754`** for an existing ticket matching this workflow name. Note whether one exists.
3. **Create a Monday.com ticket** if none exists: Name = `QA: [Workflow Name]`, Group = `topics`, Type = `HubSpot`, Stage = `QA`.
4. **Create a QA doc** attached to the ticket: `monday.com:create_doc` with `location: "item"`. Title: `Workflow QA: [Workflow Name]`.

#### B. Ask the user interactively (only what you can't determine)

Present what you found, then ask ONLY for context you genuinely need. Skip any question where you already have the answer. Use tappable options or concise questions - not a wall of text.

| Question | When to ask |
|---|---|
| "Has this been tested with a sample contact?" | Always ask |
| "Re-enrollment is ON - what triggers it, and is this intentional?" | Only if re-enrollment is enabled |
| "This workflow sets [property]. Is it part of a chain with other workflows?" | Only if the workflow writes to properties other workflows might read |
| "This will update [property] for potentially [X] contacts. Rollback plan?" | Only if writing at scale for the first time |
| "What's the business purpose of this workflow?" | Only if not clear from name/description |
| "Who built this workflow?" | Only if not determinable from Monday.com or HubSpot |

**Never ask for things you can determine yourself:** workflow name, enrollment conditions, branch logic, action details, Monday.com ticket existence, workflow ON/OFF status. Read them via Chrome and MCP tools.

Wait for the user's responses before proceeding to Step 2.

### Step 2 - Naming & Hygiene Audit

Before reviewing logic, check that the workflow and all its components follow naming conventions. Inconsistent naming is a leading cause of errors when workflows interact or when team members need to maintain each other's work.

> **Context from Riverside's HubSpot audit (April 2026):** Analysis of 2,136+ lists, ~100 workflows, and ~90 marketing emails revealed systemic naming issues across all asset types. Lists have bracket prefixes on only 20% of assets; workflows are better at ~40% but still inconsistent; marketing emails mix 4+ different naming schemes. Common issues: person names in asset names, "don't touch" in 5+ formats, `(Clone)` and `(cloned)` not cleaned up, internal IDs embedded in email names, inconsistent date formats, and emoji/special characters in workflow names.
>
> **For the full naming guide with before/after examples from real data, read `knowledge/naming-conventions.md`.** The summary below covers the essential rules; the knowledge file has object-specific patterns and the complete audit findings.

#### Naming Convention Standard

**Rule 1: Always use a category prefix in square brackets.**

Every asset name starts with a bracketed category tag. This is non-negotiable - it's how the team finds, filters, and understands assets at a glance.

| Prefix | Meaning | Use for |
|---|---|---|
| `[WF]` | Workflow-dependent asset | Lists, emails, and forms that exist to serve a specific workflow |
| `[MKT]` | Marketing (general) | Cross-motion campaign assets, marketing-owned segments, general send lists |
| `[PLG]` | Self Serve motion (PLG) | Product usage segments, self-serve behavioral lists, freemium/paid-SS audiences |
| `[B2B]` | Business / Enterprise motion | Sales-assisted marketing assets, enterprise audience segments, B2B campaign lists |
| `[BD]` | Business Development (team) | BD team-specific operational assets: signup notifications, rep assignments, outreach lists |
| `[OPS]` | Marketing/Sales Ops | Operational lists, data hygiene, internal reporting |
| `[ICP]` | Ideal Customer Profile | Tier lists, scoring segments, fit-based lists |
| `[ENRICH]` | Enrichment | Data enrichment triggers and segments |
| `[EXCL]` | Exclusion / Suppression | Do-not-email, competitor, invalid contact lists |
| `[TEST]` | Test / Temporary | Must include an expiry date (see Rule 5) |
| `[ARCHIVE]` | Deprecated / Legacy | Lists kept for historical data but no longer active in workflows |

> **`[PLG]` vs `[B2B]` vs `[BD]` - how to choose:**
> - **`[PLG]`** = the asset targets or supports the **Self Serve motion** (freemium, paid self-serve, product-led growth). Example: `[PLG] Paid SS - Login Last 30d + Business Email`
> - **`[B2B]`** = the asset targets or supports the **Business/Enterprise motion** (sales-assisted, enterprise customers). Example: `[B2B] BLAST - NAB 2026 Invite`, `[B2B] Newsletter Business - 2026-03`
> - **`[BD]`** = the asset is for **Business Development team operations** (rep routing, signup notifications, sequence assignment). Example: `[BD] New Signup - Rep Assignment Routing`
> - When in doubt: if the audience is "Business" or "Enterprise" customers, use `[B2B]`. If the asset is about how the BD team operates internally, use `[BD]`.

**Rule 2: Use hyphens as the standard delimiter. Never use AND as a delimiter.**

Separate name segments with ` - ` (space-hyphen-space). For filter logic descriptions, use `+` instead of `AND` to keep names shorter.

| Instead of | Write |
|---|---|
| `Paid Self Serve AND Logged in Last 30 Days AND Business Email` | `[PLG] Paid SS - Login Last 30d + Business Email` |
| `Freemium Self Serve AND Logged in Last 60 Days` | `[PLG] Freemium SS - Login Last 60d` |

**Rule 3: Never put person names in asset names. Use HubSpot's ownership features instead.**

Asset ownership belongs in HubSpot metadata (creator field, folder permissions, description), not in the name. Person names make assets untransferable when team members change roles.

| Instead of | Write |
|---|---|
| `Growth Ruben - Matchmaking hosts - Premium plan, never recorded` | `[MKT] Matchmaking Hosts - Premium + Never Recorded` |
| `Carley - PreOps in "Completed" → "Follow up" stages month+` | `[OPS] PreOpps - Completed to Follow Up - Stale 30d+` |
| `Mitchell - Companies to review (probably remove)` | `[TEST] Companies to Review - Expires 2025-05-01` |

**Rule 4: Standardize protection warnings as a suffix tag.**

When a list should not be edited by others, use a single consistent suffix: `⛔ LOCKED`. Do not use inline warnings, asterisks, or all-caps.

| Instead of | Write |
|---|---|
| `Dont Touch - Contacts with Open Pre-Opp or Deal` | `[OPS] Contacts with Open Pre-Opp or Deal ⛔ LOCKED` |
| `QBD - DONT TOUCH - Contact with open Deal Entity` | `[OPS] QBD - Open Deal Entity Contacts ⛔ LOCKED` |
| `ICP - Tier 1 - **Dont Touch` | `[ICP] Tier 1 ⛔ LOCKED` |
| `Pre Opps with past intro meetings (DO NOT EDIT - used in deal tags)` | `[OPS] PreOpps - Past Intro Meetings ⛔ LOCKED` |

Add the reason in the HubSpot list description field, not in the name (e.g., "Used in deal tags - do not modify filters").

**Rule 5: Date and version formatting.**

Use `YYYY-MM` for dates and `v#` for versions. Every `[TEST]` asset must include an expiry date.

| Element | Format | Example |
|---|---|---|
| Creation/reference date | `YYYY-MM` | `2025-08` |
| Quarter reference | `YYYY-Q#` | `2025-Q1` |
| Version | `v#` | `v2` |
| Time window | `Last #d` (days) | `Last 30d`, `Last 180d` |
| Test expiry | `Expires YYYY-MM-DD` | `Expires 2025-06-01` |

| Instead of | Write |
|---|---|
| `Ops Sales - Inbound SQL - All time - 08/25 V` | `[OPS] Inbound SQL - All Time - 2025-08 v1` |
| `Companies with a closed pre opp created in Q1'25` | `[OPS] Closed PreOpps - 2025-Q1` |

**Rule 6: Clean up cloned and auto-generated names immediately.**

Never leave `(cloned)`, `(Copy of...)`, or auto-generated timestamps in production. Rename or archive within 24 hours of creation.

| Instead of | Write |
|---|---|
| `Steven Bot users in BD companies (cloned)` | `[BD] Bot Users in BD Companies` (or archive the duplicate) |
| `[Workflows] - Tue Mar 31 2026 09:33:39 GMT-0500 - Pre-Opp - ...` | `[WF] PreOpp - Associate Meeting Contacts to Deal` |

**Rule 7: Workflow-dependent assets reference their parent workflow.**

Lists, emails, and notifications created for a specific workflow start with `[WF]` followed by a short workflow identifier, then their role.

| Asset Type | Pattern | Example |
|---|---|---|
| Workflow | `[Category] Purpose - Qualifier - v#` | `[MKT] MQL - Onboarding Nurture - v2` |
| Enrollment list | `[WF] [Short WF Name] - Enrollment` | `[WF] MQL Onboarding - Enrollment` |
| Suppression list | `[WF] [Short WF Name] - Suppression` | `[WF] MQL Onboarding - Suppression` |
| Marketing email | `[WF] [Short WF Name] - ##. [Description]` | `[WF] MQL Onboarding - 01. Welcome` |
| Slack notification | `[WF] [Short WF Name] - Notify [Channel]` | `[WF] Deal Pipeline - Notify #sales-alerts` |

**Rule 8: Workflow names use category prefixes from the standard set.**

Good prefixes already in use: `[MKT]`, `[Lead Routing]`, `[Property]`, `[Sync Data]`, `[CSM]`, `[AE Automation]`, `[Pre-Opps]`, `[Outreach Sync]`, `[Deduplication]`. Extend to the ~60% of workflows that currently have no prefix. No emojis, arrow characters (`➝`), or pipe characters (`|`) in names.

**Rule 9: Marketing email names follow type-specific patterns.**

| Email Type | Pattern | Example |
|---|---|---|
| One-time blast | `[MKT] BLAST - [Topic] - [Audience]` | `[MKT] BLAST - Newsletter Business - 2026-03` |
| Lifecycle/onboarding | `EM-YYYY-MM [Journey] - [Step]. [Description]` | `EM-2024-11 Paid Welcome - 2b. Demo Webinar Invite` |
| Event/webinar | `[MKT] [Event Type] - [Name] - [Stage]` | `[MKT] Webinar - B2B YouTube 2026-04 - Reminder 1` |
| Vendor automated | `[Vendor] [Vendor Name] - [Trigger]` | `[Vendor] ZiffDavis - Meeting Completed` |
| Language variants | Append ` (xx)` as last element | `EM-2024-11 Paid Welcome - 2b. Demo Webinar (fr)` |

Remove internal HubSpot IDs from email names (found in ~10 emails during audit).

#### Hygiene Checks During QA

When reviewing a workflow, verify:
- Workflow name follows the `[Type] - [Audience] - [Purpose] - v#` pattern
- All dependent lists, emails, and forms start with `[WF]` and reference this workflow
- No orphaned assets (lists or emails created for this workflow but not used)
- No `(cloned)`, `(Copy of)`, person names, or auto-generated timestamps in any asset name
- No inline warnings - if a list needs protection, it uses the `⛔ LOCKED` suffix and has a description explaining why
- Test assets have expiry dates
- Folder organization in HubSpot - workflow is in the correct team/campaign folder
- If naming violations are found, log them as P2 issues and include specific rename recommendations in the QA report

### Step 3 - Logic Review

Walk through every branch of the workflow, checking each section below. For complex workflows (15+ actions, nested if/then), draw out the logic tree before reviewing individual nodes.

Work from the flow definition you pulled in Step 1, not from what the canvas volunteers. Do NOT report a collapsed or unrendered part of the canvas as a finding - it means you have not read the definition yet. Include the full trigger and branch conditions in the QA report.

#### Cloned workflows - check these four things first

Cloning is the normal way workflows get built here, and an inherited setting is the highest-yield place to look. Every one of these shipped in a single clone reviewed 2026-09-07:

| Inherited thing | Why it breaks | Check |
|---|---|---|
| **Suppression lists** | The parent's suppression list is usually the parent's *own* success list - sensible self-suppression there, silent cross-suppression here. A clone reviewed 2026-09-07 carried a 14,645-contact list growing ~1,200/week that would have blocked a large and rising share of enrollments, with no error anywhere | `suppressionListIds` should be `[]` unless the reviewer can state why each list belongs |
| **Description** | Describes the parent's logic, so the next reviewer starts from a false model of the workflow | Read it against the actual trigger and actions |
| **Success / failure lists** | May still point at the parent's lists, mixing two populations into one segment | Resolve every `listId` to its name |
| **The action that was swapped** | The clone kept the parent's *branch* but replaced the action it branches on, so the branch may be reading a signal the new action does not produce the same way. See "When a clone swaps the action a branch reads" below | Compare the clone's action types against the parent's |

#### When a clone swaps the action a branch reads

Observed on the 2026-09-07 clone: the parent (`[OPS] High Quality Sign Ups - Segment Webhooks`, flow `1820737316`) sends its webhook with HubSpot's **native webhook action** and branches on that action's `hs_execution_state`. The clone (flow `1878717070`) kept that branch verbatim but replaced the action with a **custom-code** action.

Whether `hs_execution_state` carries the same meaning for both action types was not established during that review, so treat an unchanged branch sitting on a substituted action as unverified rather than as either working or broken.

Two things follow, neither of which depends on settling that question:

- **Prefer branching on a value the action itself declares.** A custom-code action's own output field (e.g. `statusCode`) is unambiguous about what it reports. Route the expected success value explicitly and point the default branch at the failure path, so an action-level failure that produces no output fields still falls to the default and gets caught.
- **Prove the failure path with a deliberate-failure test before sign-off.** Break the call on purpose - an invalid credential is the cheapest way - and confirm the contact reaches the failure list and any alert actually fires. This is the only thing that settles it, whichever signal the branch reads.

Use the full checklist in the next section. Focus especially on:
- Enrollment triggers matching the intended audience (not too broad, not too narrow)
- Re-enrollment settings (should contacts go through again? Under what conditions?)
- If/then branch conditions using the correct properties and operators
- Delay timing (business hours vs. calendar days, timezone handling)
- Goal criteria and unenrollment triggers (contacts should exit when the goal is met)
- Suppression logic (unsubscribed contacts, competitors, internal emails)

### Step 4 - Report & Log

#### A. Write findings to the QA Doc

Create the QA doc as a Monday.com doc attached to the ticket (`monday.com:create_doc`, `location: "item"`, `item_id: [ticket ID]`). Write the full report using this structure:

```
# Workflow QA: [Workflow Name]
Date: [Date]
Reviewer: [Name]
Monday.com ticket: [Link]
HubSpot workflow URL: [Link]
Status: [PASS / PASS WITH NOTES / FAIL]

## Summary
[1-2 sentence overall assessment]

## Issues Found

### [Issue Title]
- **Severity**: P0 / P1 / P2 / P3
- **Category**: [Enrollment | Logic | Email/Content | Data | Integration | Naming | Compliance]
- **Description**: [What's wrong]
- **Expected behavior**: [What should happen]
- **Recommendation**: [How to fix]
- **Screenshot/evidence**: [Link or description]

## Checklist Completion
[Paste completed checklist with pass/fail per item]
```

#### B. Update the Monday.com ticket

Board: `Marketing Operations Tasks` (ID: `6257866754`)

Update the ticket with these column values (see `references/monday_boards.md` for the full schema):

| Column | Column ID | Value to set |
|---|---|---|
| Type | `status_11` | `HubSpot` (label id: 6) |
| Stage | `status_18` | `QA` (label id: 3) - or `Launched` (id: 1) if approved |
| Priority | `priority_1` | Set to highest severity found: P0 (id: 10), P1 (id: 110), P2 (id: 109), P3 (id: 7) |
| HubSpot URL | `short_text01ee10v7` | The workflow URL |
| Bucket | `color_mkzspv3r` | `Bucket 5: Work Process & Work Flows` (label id: 4) |
| HubSpot work | `multi_selectyy1zfsn6` | `Workflow` |
| Tags | `tags__1` | Add `Hubspot` tag (id: 28385917) |

If **no ticket exists**, create one:
- **Item name**: `QA: [Workflow Name]`
- **Group**: Current sprint week group (e.g., `group_mm23g95f` for current week) or `topics` (New Requests)
- Set all column values above
- Link the Google Doc in the Assets column (`files`)

#### C. Add QA summary as an update/comment on the ticket

Post the summary (status, issue count by severity, top findings) as an update on the Monday.com item so it's visible in the ticket activity feed.

### Step 5 - Sign-off

| Situation | Action |
|---|---|
| P0 issues found | **Do not approve.** Notify builder immediately in Slack with link to QA doc. Workflow must not go live. Set Monday.com Stage to `QA`, Status to `Pending`. |
| P1 issues found | **Do not approve until resolved.** Update Monday.com ticket with P1 details. Builder fixes before launch. |
| P2/P3 issues found | Log in Monday.com for next sprint. Workflow may launch at reviewer's discretion. |
| No issues / all resolved | Set Monday.com Stage to `Launched`, Status to `Done`. Post approval in Slack with QA doc link. Workflow is clear to activate. |
| Uncertain about severity | Escalate to Marketing Ops lead or relevant stakeholder. |

### Step 5b - Re-QA after fixes (do not skip)

When the builder reports fixes, **re-read the flow definition and verify each claimed fix individually.** Never mark a finding resolved on the strength of the report. Evidence from the 2026-09-07 review, where five fixes were reported: one had not saved, and one introduced a **new P0** - the exclusion added for a P2 finding was configured as `IN_LIST` instead of `NOT_IN_LIST`, which would have enrolled only existing paid customers and excluded every prospect.

1. **Re-pull the definition** and compare `revisionId` against the round you last reviewed. Unchanged revision means nothing saved.
2. **Verify each claimed fix against the specific field** it touches - an item-by-item pass, not a glance at the canvas. A fix made in the UI but not saved leaves the field untouched while the canvas may still show the edit.
3. **Run the full regression sweep**, not just the changed items: re-walk the action chain, re-run the orphan check, re-resolve every `listId`, re-check the code for credentials. Fixes move actions around, and a rebuilt branch can drop a path.
4. **Re-check anything a fix could have inverted** - filter direction most of all - against the canvas text.
5. **Report your own errors plainly.** If a round-1 finding turns out to be wrong, withdraw it in the round-2 report and say so. A QA doc that quietly drops a finding is worse than one that never raised it.
6. Repeat until no P0 or P1 remains. Only then does Step 5 sign-off apply.

Track findings in a single register carried across rounds, each row holding a severity and a live status (Fixed / Open / Accepted / Withdrawn), so the ticket shows one history rather than three disconnected reports.

---

## QA Checklist

### 1. Enrollment Triggers & Filters

| Check Item | Priority |
|---|---|
| Enrollment trigger matches the stated audience - not too broad (risk of wrong contacts entering) or too narrow (intended contacts excluded) | P0 |
| All filter properties exist in HubSpot and are actively populated (no reliance on empty/deprecated fields) | P0 |
| AND/OR logic in enrollment filters is correct - test mentally with 3 example contacts (one who should enroll, one who shouldn't, one edge case) | P0 |
| Re-enrollment setting is intentional: if ON, confirm contacts should legitimately re-enter; if OFF, confirm one-pass is correct | P1 |
| Contact list or segment used for enrollment is active (not static) unless static is intentional | P1 |
| Enrollment trigger does not overlap with another live workflow's trigger (risk of double-enrollment or conflicts) | P1 |
| Estimated enrollment volume has been sanity-checked (use active list count as a proxy) - flag if unexpectedly large or zero | P2 |
| Every entry in `suppressionListIds` is deliberate - resolve each `listId` to its name and state why it belongs. On a cloned workflow the default expectation is `[]` | P0 |
| Every list-membership filter has the intended **direction** - confirm on the canvas that an exclusion reads "is **not** member of", not "is member of" | P0 |
| Turn-on plan is explicit about historical contacts - do not bulk-enroll existing contacts where the downstream system rejects stale events (Meta CAPI drops conversions older than 7 days) | P1 |

### 2. Workflow Actions & Logic Flow

| Check Item | Priority |
|---|---|
| Every if/then branch has been walked through - no dead ends or branches with no actions | P0 |
| If/then conditions use the correct property, operator, and value (watch for "is equal to" vs "contains" vs "is known") | P0 |
| Delays are set correctly: business days vs. calendar days, correct timezone, appropriate duration | P1 |
| Goal criteria is set and correct - contacts who achieve the goal are removed from the workflow | P1 |
| Unenrollment / suppression triggers are in place (e.g., contact unsubscribes, becomes a customer, is marked as competitor) | P0 |
| No infinite loops - if re-enrollment is on, confirm the workflow cannot re-trigger itself endlessly | P0 |
| Actions are in the correct sequence (e.g., property update happens before the email that references that property) | P0 |
| A branch reading an action's `hs_execution_state` sits on the same action type it was written for - if the action was substituted (e.g. native webhook to custom code), prefer a value the action itself declares, and prove the failure path with a deliberate-failure test | P1 |
| Every action is reachable from `startActionId` - run the orphan check, and confirm the branch's default path is wired to the failure handling | P0 |
| Workflow does not have unnecessary or duplicate actions (copy/paste artifacts) | P2 |

### 3. Email & Content (for workflows containing email sends)

| Check Item | Priority |
|---|---|
| Email is in "Published" or "Automated" status - not still in draft | P0 |
| Subject line and preview text are final - no placeholders, no Lorem Ipsum | P0 |
| Personalization tokens have fallback/default values (e.g., `{{ first_name \| default="there" }}`) | P0 |
| Smart content rules (if any) are correctly configured and tested with sample contacts | P1 |
| All links in the email work and point to the correct destination | P0 |
| UTM parameters are present on links that require tracking (confirm with Growth team) | P1 |
| Unsubscribe link is present and functional | P0 |
| Email sender name and address are correct for this workflow type | P1 |
| Email renders correctly on desktop and mobile (use HubSpot preview/test send) | P1 |
| Send frequency / throttling: contact won't receive too many emails too quickly across all active workflows | P1 |

### 4. Data Integrity (property updates, lifecycle stages, lead scoring)

| Check Item | Priority |
|---|---|
| Properties being set/updated exist and accept the value being written (correct field type, within allowed options) | P0 |
| Lifecycle stage changes follow the correct progression (stages only move forward unless explicitly intended to regress) | P0 |
| Lead score changes are appropriate in magnitude and direction - won't cause score inflation or unintended MQL/SQL triggers | P1 |
| Property updates won't overwrite data set by other workflows or manual entry (check for conflicts) | P1 |
| Contact owner assignment logic is correct (round-robin working, correct team, no assignment to inactive users) | P1 |
| Workflow is not setting the same property that its own enrollment trigger checks (risk of re-enrollment loop or self-defeating logic) | P0 |
| If copying/syncing data between objects (contact → deal, deal → company), mapping is correct | P1 |

### 5. Integrations & Notifications

| Check Item | Priority |
|---|---|
| **Slack notifications**: correct channel, message content includes all needed context (contact name, deal info, link back to HubSpot record) | P1 |
| **Slack notifications**: no sensitive PII in channel messages (respect data handling policies) | P1 |
| **Ad audience sync** (Google Ads, Meta, LinkedIn): correct audience/list mapped, sync direction is correct, audience size is reasonable | P1 |
| **Ad audience sync**: suppression audiences are in place (don't advertise to existing customers, unsubscribed contacts, etc.) | P1 |
| **Task creation**: task is assigned to the correct owner, has a due date, and includes enough context to act on | P2 |
| **Internal email notifications**: correct recipient, useful subject line, links back to HubSpot record | P2 |
| All integration actions are tested (not just assumed to work) - use a test contact to verify | P1 |

### 6. Compliance & Suppression

| Check Item | Priority |
|---|---|
| Marketing emails respect subscription status - contacts who have opted out will NOT receive the email | P0 |
| GDPR consent: if applicable, workflow checks for lawful basis / consent before processing or emailing EU contacts | P0 |
| Suppression list is applied: competitors, internal domains, known bad data, do-not-contact records are excluded | P1 |
| CAN-SPAM: physical address present in email footer, unsubscribe mechanism works | P0 |
| If workflow processes minors' data or data from regulated industries, additional compliance checks have been confirmed with Legal | P1 |
| Data retention: workflow does not store or copy personal data into properties/fields where it shouldn't persist | P2 |

### 7. Testing & Validation

| Check Item | Priority |
|---|---|
| Workflow has been tested with at least one test contact (enrolled, completed all branches, verified outputs) | P0 |
| Test contact(s) have been removed / cleaned up after testing | P2 |
| If workflow is time-sensitive (delays, scheduled sends), test plan accounts for verifying timing behavior | P1 |
| Edge cases have been considered: what happens if a contact has no email? No owner? Missing required property? | P1 |
| If replacing or modifying an existing live workflow: rollback plan is documented | P1 |

---

## Quick Reference: Common Mistakes

These are the errors the Marketing Ops team encounters most frequently. Pay extra attention during QA:

1. **Wrong enrollment filters** - AND vs. OR confusion, using "contains" when "is equal to" is needed, referencing a deprecated property.
2. **Missing personalization fallbacks** - Tokens render as blank when the property is empty, making emails look broken.
3. **Delay misconfiguration** - Business days vs. calendar days, wrong timezone, or delays that push sends into weekends/holidays.
4. **Property update conflicts** - Two workflows writing to the same property, or a workflow overwriting a value that was manually set by Sales.
5. **Re-enrollment loops** - Workflow updates a property that matches its own enrollment trigger, causing contacts to loop.
6. **Missing suppression** - Unsubscribed or competitor contacts entering a nurture sequence.
7. **Stale email content** - Workflow references an email that's still in draft, or has outdated pricing/feature claims.
8. **Integration failures** - Slack message goes to wrong channel, ad audience sync includes suppressed contacts.
9. **Clone artifacts** - an inherited suppression list, the parent's description, or the parent's success/failure lists carried over unreviewed. Nothing errors; the workflow just quietly does the wrong thing.
10. **A branch left pointing at a substituted action** - the workflow was cloned, the action was swapped, and the branch that reads its result was never revisited. Prove the failure path fires with a deliberate-failure test rather than assuming the signal still means what it did.
11. **An exclusion configured as an inclusion** - `IN_LIST` where `NOT_IN_LIST` was meant. Read it back on the canvas: "is member of" vs "is not member of".
12. **A credential hardcoded in a custom-code action** - often alongside a declared secret that goes unused. Replacing it with `process.env` is not enough; the key is preserved in every prior revision and needs rotating.

---

## Tips

- **Test with real-ish data**: Use a test contact that mirrors your actual audience (has values in the properties the workflow checks). A blank test contact won't catch filter issues.
- **Read the workflow backwards**: Start from the last action and work up. This catches dead-end branches and missing exit criteria more reliably than top-down review.
- **Check the "Other workflows" panel**: HubSpot shows which other workflows a contact is in. Look for conflicts and overlaps.
- **Use HubSpot's workflow performance tab post-launch**: Set a reminder to check enrollment counts and error rates 24-48 hours after activation.
- **Document assumptions**: If the workflow depends on a property being populated by another system (Salesforce, form, import), note that dependency in the QA doc.

---

## Escalation Contacts

| Topic | Contact |
|---|---|
| Workflow logic / Marketing Ops | Marketing Ops Lead |
| Email content / Brand | Content Lead |
| Compliance / Legal | Legal team |
| Ad platform integrations | Growth / Paid Media team |
| Slack integration issues | RevOps / IT |

Questions? Post in the relevant Slack channel or reach out to Marketing Ops leadership.
