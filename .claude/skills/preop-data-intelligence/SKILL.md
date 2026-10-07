---
name: preop-data-intelligence
description: >
  Riverside's Pre-Op (Deal) data dictionary and analytical layer for HubSpot: the source of truth
  for Pre-Op fields, stages, business rules, attribution logic, and KPI definitions (MQL, SQL,
  conversion rates, BD/AE credit). Trigger on Pre-Ops, intro meetings, meeting bookings/completion,
  BD attribution, AE performance, outbound/inbound sourcing, MQLs, SQLs, conversion rates, deal
  promotion, pipeline stages, "free op", "pre op", "pre-op", "meeting booked", "BD booked",
  "promoted to deal", "how many meetings did X do", "what's our conversion rate", "how many SQLs
  this month" - any meetings, top-of-funnel, or lead-to-opportunity conversion question in HubSpot.
---

# Pre-Op Data Intelligence - Riverside HubSpot Reference

This skill gives you everything you need to correctly interpret, query, and reason about
Riverside's Pre-Op entity in HubSpot. A Pre-Op tracks the first engagement with a prospect
via intro meetings. It is the top-of-funnel object that feeds into the opportunity (Deal) pipeline.

When answering any question about Pre-Ops, intro meetings, BD/AE performance, MQLs, SQLs,
or meeting metrics - consult this skill and follow its definitions exactly. Do not guess or
infer definitions that aren't documented here.

---

## What Is a Pre-Op?

A Pre-Op is a HubSpot Deal record that represents a single engagement cycle with a prospect,
starting from a booked intro meeting. It is the foundational tracking unit for Riverside's
top-of-funnel sales motion.

Key characteristics:
- Every Pre-Op is tied to a booked intro meeting (though rare exceptions exist for manually
  created records - see Business Rules below).
- One Pre-Op = one engagement cycle. If a prospect was previously Closed Lost and re-engages,
  a new Pre-Op is created with an incremented cycle count.
- When a Pre-Op converts, it promotes to exactly one Deal (1:1 relationship, always).
- Once promoted, the Pre-Op record is frozen - no further edits are allowed.

---

## Pipelines

Pre-Ops live in four separate pipelines, segmented by market (verified 2026-08-24; the
earlier three-pipeline layout - Agency / EU / Enterprise - is retired):

1. **Pre-Opp - US Agency** (`29354026`)
2. **Pre-Opp - US Enterprise** (`29152011`)
3. **Pre-Opp - EU Agency** (`89765536`)
4. **Pre-Opp - EU Enterprise** (`916013614`)

EU Enterprise became a first-class pipeline in August 2026; historical EU enterprise records
were migrated out of EU Agency (migration confirmed clean warehouse-side, 2026-08-12).
Pipelines differ in both stages and fields - they are NOT identical copies of each other.
When building reports or queries, always confirm which pipeline(s) the user is asking about.
If the user doesn't specify, ask - or if the context is clearly "all Pre-Ops", query across
all four. A dashboard or saved report still filtered on the old pipeline set silently drops
EU volume - the first thing to check when a HubSpot report disagrees with the warehouse or
with an all-pipeline count.

---

## Stages

The following stages apply to the Pre-Op lifecycle. Note that because pipelines differ, not
every pipeline may have the exact same stage names, but these are the core stages:

| Stage | Definition | Terminal? |
|---|---|---|
| **Meeting Booked** | Pre-Op is created when an intro meeting is scheduled. This is the entry point. | No |
| **Follow-Up** | AE is actively engaging the prospect after the intro meeting. | No |
| **Promoted to Deal** | The Pre-Op converted into an opportunity. A linked Deal is created via Associated Deal ID. | Yes (frozen) |
| **Closed Lost** | The prospect did not convert. This is a terminal stage. | Yes |
| **Action Required** | No-show, unclear next step, or cases needing attention. This is a **temporary holding stage** - Pre-Ops can move back to Follow-Up or other active stages from here. | No |

---

## Core Fields

### Ownership & Assignment

| Field | Definition |
|---|---|
| **Pipeline (Pre-Op)** | Which pipeline this Pre-Op belongs to: US Agency, US Enterprise, EU Agency, or EU Enterprise. |
| **Deal Owner (AE)** | The Account Executive responsible for this Pre-Op. This is the primary ownership field. |
| **BD Owner** | The Business Development rep who booked the meeting. Only populated if a BD actually booked it. |
| **AE Assigned** | Mirrors Deal Owner. |

Ownership rules:
- If the Deal Owner (AE) changes mid-lifecycle, the **current owner** at time of reporting
  gets credit for all metrics (meetings, SQLs, etc.). There is no "original owner" tracking.

### Record Identification

| Field | Definition |
|---|---|
| **Deal Name** | Auto-generated name with a counter reflecting the engagement cycle number. |
| **Record ID** | Unique identifier for the Pre-Op record. |
| **Pre-Op Number Count** | Number of engagement cycles with this prospect. If this is 2, it means there was a previous Pre-Op that was Closed Lost, and this is the second attempt. A new cycle is triggered after a Closed Lost. |

### Dates

| Field | Definition |
|---|---|
| **Create Date** | Auto-populated: when the Pre-Op record was created in HubSpot. |
| **Close Date** | Manually entered by the AE. |

### Deal Characteristics

| Field | Definition |
|---|---|
| **Currency** | The currency for this deal. |
| **Company Market** | SMB / Mid-Market / Enterprise. This is calculated from company size, not manually set. |
| **Deal Type** | Always "New Business" for Pre-Ops. |
| **Deal Probability** | HubSpot-calculated probability based on stage. |
| **Forecast Category** | HubSpot default forecasting category. |
| **Industry** | The customer's industry. |
| **Riverside Industry** | Riverside's internal industry classification (may differ from Industry). |
| **Riverside Use Case** | AE-selected use case for why the prospect needs Riverside. |
| **Current Solution** | AE-selected field for what tool/solution the prospect currently uses. |

### Contact & Quality Indicators

| Field | Definition |
|---|---|
| **# Associated Contacts** | Number of contacts linked to this Pre-Op. |
| **# Decision Maker Contacts** | Number of contacts tagged as decision-makers. |
| **Decision Maker Involved** | Boolean, set by workflow (not manual). Indicates whether a decision-maker is part of the engagement. |
| **Public Domain** | Indicates a non-business email domain (gmail, yahoo, etc.). This is a **data quality signal** - public domain = lower quality lead. |

### Source & Attribution

| Field | Definition |
|---|---|
| **Last Touch Source** | The attribution source: **Inbound**, **Outbound**, or **Customer Success**. Set at Pre-Op creation and treated as locked by every downstream report. It is the single most important attribution field. **In practice it does get edited, at scale:** as of 2026-09-06, 93 Pre-Ops carry a recorded manual flip from Inbound to Outbound and 85 more sit in the state such an edit produces. Never describe this field as immutable, and never read an Inbound/Outbound split as settled without checking. See `knowledge/source-cannibalization.md`. |

### AI & Scoring

| Field | Definition |
|---|---|
| **AI Fields** | Multiple calculated AI fields exist on the Pre-Op. |
| **Raw Score (AI)** | The key AI quality score. Threshold: **≥18 = good quality**, **<18 = low quality**. This score is used for **reporting and analysis only** - it does NOT drive operational routing, prioritization, or workflow automation. |

### Qualification (AE Input)

| Field | Definition |
|---|---|
| **Authority** | AE's assessment of whether they're speaking to someone with buying authority. |
| **Budget** | AE's assessment of budget availability. |
| **Scoring** | AE's qualitative scoring of the opportunity. |

### Pricing

| Field | Definition |
|---|---|
| **Pricing Package (SMB)** | The pricing package shown to the prospect (applicable to SMB). |

### Company Info

| Field | Definition |
|---|---|
| **Company Info** | Company-level data pulled from the associated company record. |

---

## Intro Meeting Tracking Fields

These fields track the lifecycle of the intro meeting associated with the Pre-Op. They are
critical for meeting metrics and SQL definitions.

| Field | Definition |
|---|---|
| **Intro Meeting Create Date** | When the intro meeting was scheduled/created. This is the basis for "meeting booked" counts. |
| **Intro Meeting Start Date** | When the meeting is scheduled to occur. |
| **Intro Meeting Complete Date** | When the meeting lifecycle completed. This field existing (being non-null) is the basis for "meeting took place" / SQL definitions. |
| **Intro Meeting Completion Date (Locked)** | The actual timestamp of when the meeting happened. Locked after completion. |
| **Days Since Intro Meeting** | Calculated: days elapsed since the meeting completed. |
| **Time: Create → Start** | Calculated: time from when the meeting was booked to when it was scheduled to start. |
| **Intro Meeting Booked** | Boolean indicator that a meeting was booked. |
| **Intro Meeting Status** | The meeting's current status. Values: **Scheduled**, **Completed**, **Rescheduled**, **No-show**, **Canceled**. |

---

## System Fields

| Field | Definition |
|---|---|
| **Last Activity Date** | Last activity logged on this Pre-Op. |
| **Last Contacted Date** | Last engagement/contact with the prospect. |
| **Last Modified Date** | Last time any field on this record was updated. |

---

## Deal Linking

| Field | Definition |
|---|---|
| **Associated Deal ID** | Links the Pre-Op to the promoted Deal (opportunity). This is how you track the full funnel from Pre-Op → Deal. Only populated when the Pre-Op reaches "Promoted to Deal" stage. |

---

## Business Rules

These rules define how Riverside's Pre-Op system works. Follow them exactly when answering
questions or building queries.

### Meeting Booked
A meeting is considered "booked" based on the **Intro Meeting Create Date** field being populated.
This is the definitive signal - not the stage name, not a boolean, but this date field.

### Meeting Took Place
A meeting is considered to have "taken place" (completed) when:
- **Intro Meeting Complete Date** exists (is not null), AND
- **Intro Meeting Status = Completed**

Both conditions must be true. A meeting with a Complete Date but a status of "No-show" or
"Canceled" did NOT take place.

### BD Booked the Meeting
A BD (Business Development rep) is credited with booking a meeting when:
- **Last Touch Source = Outbound**, AND
- **BD Owner** is populated (not null/empty)

Both conditions are required. If Last Touch Source is Outbound but BD Owner is empty, the
meeting is "Non-BD Outbound" - currently these are **unattributed** (this is a known gap
that needs to be addressed).

### Pre-Op Creation
A Pre-Op is always tied to a booked meeting. However, rare exceptions exist where Pre-Ops
are created manually without a meeting booking. When counting meetings, be aware that not
every Pre-Op record necessarily equals a booked meeting.

**The creation engine** is the "Pre-Opp Creation [2026 build]" contact workflow (portal
9154210, flow ID `1819472043`). A contact can be **enrolled by hand** (the workflow keeps a
"Manually triggered" start option, which routes through the "Triggered manually" branch), or
it enrolls **automatically** on any one of the four triggers below. On enrollment it waits
5 minutes, then branches: if the contact has no open deal and is not a business customer it
creates the Pre-Op, otherwise it skips creation. The four automated triggers:

1. A **Meeting booked** activity is logged on the contact. (This is HubSpot's "Meeting booked has been completed" enrollment phrasing, i.e. a meeting-booked engagement was created on the contact. It is HubSpot's generic "activity happened" wording and is **not** the Riverside "meeting took place" definition above.)
2. `utm_medium` changes to `affiliate`.
3. `force_generate_pre_opp` (Force Generate Pre Opp) is set to `True`.
4. A form submission whose URL path contains `dashboard` or `demo` (and does not contain `blog`, `webinars`, or `newsletter`).

**Forcing a Pre-Op for a specific contact (manual override).** This is the purpose-built
escape hatch (automated trigger 3), used when an AE needs a Pre-Op without a real booked
meeting. Get the user's approval first: it is a HubSpot write that enrolls the contact and can
create a Pre-Op. Then set both fields **in one HubSpot write**: `source_of_forced_pre_opp_ae_input`
("Source of forced pre opp (AE Input)", valid values `Inbound` or `Outbound`) and
`force_generate_pre_opp` (Force Generate Pre Opp) = `True`. HubSpot rejects a write that sets
the flag without the source (validation error, seen 2026-10-05), and setting the flag enrolls
the contact immediately while the Pre-Op is only created after the 5-minute delay, so the
source must already be on the record when the Pre-Op's Last Touch Source is stamped.

The Pre-Op appears about 5 minutes later, provided the contact has no open deal. A contact
that already has an open deal or is a business customer takes the other branch and no
Pre-Op is created. Verified 2026-07-13.

### Force-generate limitation and the manual fallback (added 2026-08-25)

The `force_generate_pre_opp` trigger above is the documented escape hatch, but it **does not
fire for a whole class of contact**: an existing contact who already passed through the
workflow (older records, already advanced to SQL) is **not re-enrolled** when the flag is set
again, because HubSpot enrollment only fires when the value *changes* to `True`. Toggling the
flag off and back on does not reliably force re-enrollment either. Symptom: you set the flag,
wait 5+ minutes, and no Pre-Op appears (`number_of_associated_pre_opps` stays `0`). Reproduced
across three contacts on 2026-08-25 (Vortex Cloud, My Wealth Solutions, MEP Technologies).

**When force-generate produces nothing within ~5 minutes, create the Pre-Op manually.** This is
also the correct fix for the recurring **calendar-sync gap** - an intro meeting is booked on
the contact but no Pre-Op auto-generates. (This gap is currently recurring for BD-outbound
intro meetings; see `systems/owned/hubspot.md`.)

**Manual Pre-Op creation recipe (also the calendar-sync-gap backfill):**

1. **Confirm it is genuinely missing.** The contact must have **zero** associated Pre-Op deals
   (`num_associated_deals` = 0 / no deal in a Pre-Op pipeline). If one already exists, stop -
   do not create a duplicate.
   **Then check the contact has a company.** If it has none, a company with its email domain is
   only a candidate: confirm it is the right one (one record for the domain, name matches the
   contact's `company` field). If several companies match, ask the user which one. Get the user's
   approval for the association (it is a HubSpot write), then associate it as **Primary** and
   wait about a minute. The workflow can then
   create the Pre-Op itself: it did 8 seconds after the link for Cru on 2026-10-02, and a manual
   create in the same pass left a duplicate. Re-run this step's check before going on.
2. **Find the real intro meeting.** Search `MEETING` objects associated with the contact and
   read `hs_meeting_start_time`, `hs_createdate`, and `hs_meeting_outcome`. If the AE wants a
   Pre-Op with no real meeting, you can still create it but omit the meeting association.
3. **Pick the pipeline by company market** (pipelines differ in stages, so the Meeting Booked
   entry-stage ID differs per pipeline). Verified 2026-08-25:

   | Pipeline | Pipeline ID | Meeting Booked stage ID |
   |---|---|---|
   | Pre-Opp - Agency(SMB) | `29354026` | `1033613941` |
   | Pre-Opp - Enterprise | `29152011` | `1031377048` |
   | Pre-Opp - Europe (EU) | `89765536` | `1033614704` |

   If unsure which market, mirror the pipeline a sibling auto-created Pre-Op used for a similar
   company rather than guessing.
4. **Create the Deal** (`manage_crm_objects`, objectType `deals`) with:
   - `dealname`: `[Pre-Opp #1] {Company} - DD/MM/YYYY` (date = intro meeting start date;
     increment the number for a re-engagement cycle after a prior Closed Lost).
   - `pipeline` + `dealstage` from the table above.
   - `hubspot_owner_id`: the AE/BD owner (for a BD-booked meeting, the BD who owns the contact).
   - `last_touch_source`: `Outbound` for BD-worked contacts (lead status starting `BD:`),
     `Inbound` otherwise. This is the locked attribution field - set it correctly at creation.
   - **Required intro-meeting fields** - HubSpot **rejects the create without
     `intro_meeting_status`**: `intro_meeting_status` (`Scheduled` for a future meeting,
     `Completed` if it already happened), `intro_meeting_booked` = `Booked`,
     `intro_meeting_start_date` (meeting start), `intro_meeting_create_date` (when it was booked).
5. **Associate** the Deal to the `CONTACT`, the `COMPANY`, and the `MEETING` in the same call
   (all three).
6. **Verify** the deal exists and the contact's `number_of_associated_pre_opps` is now ≥ 1. A
   change is not done until it runs.

**Duplicate safety:** if you also set `force_generate_pre_opp` while trying the workflow first,
leave it `false` after a manual create so a late-firing workflow cannot add a second Pre-Op.

### Promotion to Deal
When a Pre-Op is promoted:
- Exactly **one Deal** is created (1:1 relationship, always).
- The Deal is linked back via **Associated Deal ID**.
- The Pre-Op record is **frozen** - no further edits are allowed after promotion.

### Data Quality Rule
**Public Domain = lower quality**. If the Public Domain field is true, the lead came from a
non-business email (gmail, yahoo, etc.) and should be flagged as lower quality in any
quality-focused analysis.

### Engagement Cycles
The **Pre-Op Number Count** tracks how many times Riverside has engaged this prospect:
- Count of 1 = first engagement
- Count of 2+ = re-engagement after a previous **Closed Lost**
- A new cycle (new Pre-Op) is triggered specifically after a Closed Lost outcome

---

## Attribution Logic - Outbound

Understanding outbound attribution is critical for BD performance reporting.

| Concept | Definition |
|---|---|
| **Outbound Identification** | Last Touch Source = Outbound |
| **BD Attribution** | Requires BD Owner to be populated |
| **Valid BD Meeting** | Last Touch Source = Outbound AND BD Owner is populated |
| **Non-BD Outbound** | Last Touch Source = Outbound but BD Owner is empty. These are currently **unattributed** - a known gap. |

### Inbound-to-Outbound reclassification ("source cannibalization")

**178 Pre-Ops / 169 QBD leads** carry Outbound Last Touch Source over an inbound MQL origin:
93 with a recorded flip event, 85 undated. Median flip lands **2 days after the QBD flag**,
almost all by hand, concentrated in five people. **$395,374 ARR of closed-won business** sits
inside the set.

Consequence for anything in this skill: an Outbound count is an upper bound and an Inbound
count a lower bound, on **MQL Definition**, **SQL Definition**, **SQLs by BD**, and every
BD-performance read. Say so when you report one. Full figures, method, and the caveats that
must travel with them: **`knowledge/source-cannibalization.md`**. Intent is not established
and record-level corrections need individual review, so this is a reliability caveat, never
an accusation.

---

## Analytical Layer - How to Answer Key Questions

This section defines exactly how to calculate each metric. When the user asks any of these
questions, use the logic defined here - do not improvise alternative approaches.

### 1. Meetings Booked

**Question:** "How many meetings were booked?"

**Logic:** Count all Deal records where Pipeline = Pre-Op (across all four pipelines: US Agency, US Enterprise, EU Agency, EU Enterprise; see Pipelines).

**Important nuance:** While the vast majority of Pre-Ops represent booked meetings, rare
manually-created exceptions exist. For precise counts, you can additionally filter on
Intro Meeting Create Date being populated, but for standard reporting, counting Pre-Op
records is the accepted approach.

---

### 2. Meetings Completed (Meetings That Took Place)

**Question:** "How many meetings actually happened?" / "How many meetings took place?"

**Logic:** Count Deal records where:
- **Intro Meeting Complete Date** exists (is not null), AND
- **Intro Meeting Status = Completed**

---

### 3. Meetings per AE

**Question:** "How many meetings did [AE name] do?"

**Logic:** Count Deal records filtered by:
- **Deal Owner** = the specific AE
- **Pipeline** = Pre-Op (any of the four pipelines)

For "meetings completed" per AE, add the Intro Meeting Complete Date + Status = Completed filters.

---

### 4. Meetings Booked by a BD

**Question:** "How many meetings did [BD name] schedule/book?"

**Logic:** Count Deal records where:
- **Pipeline** = Pre-Op (any of the four pipelines)
- **Last Touch Source** = Outbound
- **BD Owner** = the specific BD

---

### 5. Completed Meetings by a BD

**Question:** "How many meetings from [BD name] actually happened?"

**Logic:** Same as #4, plus:
- **Intro Meeting Complete Date** exists
- **Intro Meeting Status** = Completed

---

### 6. Conversion Rate (Meeting Conversion)

**Question:** "What's our meeting conversion rate?"

**Formula:**
```
Conversion Rate = Completed Meetings ÷ Booked Meetings
```

Where:
- Completed Meetings = count from logic #2 above
- Booked Meetings = count from logic #1 above

This can be sliced by AE, BD, pipeline, time period, source, etc.

---

### 7. MQL Definition

**Metric:** MQL (Marketing Qualified Lead)

**Definition:** Any Pre-Op where **Last Touch Source = Inbound**.

That's it. An MQL is simply an inbound-sourced Pre-Op. No additional qualification
criteria are required for this classification.

**Reconciliation with the warehouse (added 2026-07-29).** The analytics team's canonical
model describes an MQL as a **demo or contact form submission**. That is not a competing
definition: since **2025-04-01** MQL rows are sourced from HubSpot pre-opportunity deals
flagged as MQLs, so "form submission" and "inbound Pre-Op" are the *same record created at
the same moment*. Rows before that cutoff came from legacy HubSpot form submissions instead.
If a stakeholder says "MQL" meaning a form fill and you say "MQL" meaning an inbound Pre-Op,
you are both right for the current era - do not spend a review cycle resolving it.

Do **not** substitute the HubSpot *contact* lifecycle stage `marketingqualifiedlead` for
either reading. That stage also absorbs self-serve product signups (see
`systems/owned/self-serve-lead-scoring.md` → self-serve signups leaking into MQL).

---

### 8. SQL Definition

**Metric:** SQL (Sales Qualified Lead)

**Definition:** Any Pre-Op where **Intro Meeting Complete Date exists** (the meeting
actually took place).

This applies **regardless of source** - inbound, outbound, or Customer Success.
The qualifying event is that an intro meeting was completed, not how the lead arrived.

**The warehouse bar is deliberately wider (added 2026-07-29).** In the analytics team's
canonical SQL model, membership itself already encodes "the meeting took place": a
post-2025-03-26 pre-opp is only included if the meeting status is `Completed` **or** the deal
reached a qualified stage (Discovery Completed, Demo Completed, and similar). A meeting that
happened but never got status-stamped therefore still counts. **Never re-apply a
meeting-status filter on top of the canonical SQL population** - it silently drops SQLs the
business does report, which matters most when the count drives money (partner commissions,
quota, comp).

Related trap: the canonical SQL model's creation timestamp is the **meeting date**, not the
deal creation date, for post-2025-03-26 rows. Use the raw deal-creation field when you
genuinely need the latter.

---

> **Canonical source for any warehouse-reported MQL/SQL figure.** The definitions above are
> the HubSpot field-level view, correct for reading Pre-Op records directly. For anything the
> business *reports* on, or any spec/pipeline consuming these metrics, go through
> `/rivermind:ask` first - the analytics team owns the canonical models and their feature-store
> context carries the era cutoffs, qualification gates, and field caveats that HubSpot-level
> definitions cannot express. One example worth knowing: on the canonical MQL model,
> `last_touch_source` is a **hardcoded constant** applied to every row, so it is useless as an
> inbound filter there; real attribution lives on the SQL model.

### 9. SQLs by BD

**Question:** "How many SQLs did [BD name] bring?"

**Logic:** Count Deal records where:
- Meeting was completed (Intro Meeting Complete Date exists + Status = Completed)
- **Last Touch Source** = Outbound
- **BD Owner** = the specific BD

---

### 10. SQLs by AE

**Question:** "How many SQLs did each AE generate?"

**Logic:** Count completed meetings (Intro Meeting Complete Date exists + Status = Completed),
grouped by **Deal Owner**.

Remember: the current Deal Owner gets credit, even if ownership changed mid-lifecycle.

---

## What This Model Enables

When used correctly, this Pre-Op structure provides:

- **Full funnel visibility**: Meeting Booked → SQL → Deal (opportunity)
- **Clear attribution**: Inbound vs. Outbound vs. Customer Success, with BD-level granularity
- **Rep performance tracking**: Per-AE and per-BD metrics for meetings and SQLs
- **Consistent KPI definitions**: MQL, SQL, and Conversion Rate are precisely defined
- **Scalable reporting layer**: All metrics derive from the same fields and rules

---

## Timing & Maturity Rules

Added 2026-08-24, from the August 2026 "inbound SQL drop" investigation: a raw
quarter-to-date comparison read as a −19% SQL collapse that matured back to flat. Apply
these rules before comparing any two periods or quoting a rate mid-period.

### Fiscal calendar

Riverside reports on a fiscal year starting Feb 1: Q1 Feb-Apr, Q2 May-Jul, Q3 Aug-Oct,
Q4 Nov-Jan. "Same days of Q2" for an August window means the matching May days.

### An in-flight SQL count is structurally depressed

An SQL only counts once its intro meeting completes, so an open period always runs below
its final value while booked meetings sit on the calendar. Statuses settle slowly
(canonical entity docs: ~76% terminal one week after the meeting, ~86% at a month, ~96.6%
after 30+ days). Never compare an open window's SQL count against a closed window raw -
maturity-match both windows, or project the landing:

> projected SQLs ≈ current SQLs + (pending booked meetings with live future/near slots ×
> trailing booked→completed rate)

The matured booked→completed rate ran 79-84% on Feb-Jun 2026 inbound cohorts (Snowflake
`ent.business_lead`, verified 2026-08-23). Deliver the projection, not only the caveat -
"371 so far, ~468 at maturity, flat vs Q2" answers the question; "the number is immature"
does not.

### No-show rates read inflated mid-period

No-shows get logged near-instantly; completions stamp days later. A mid-month no-show
percentage therefore over-reads, and any month-over-month comparison must use one
consistent formula (same numerator, same denominator treatment) on equally-matured
windows. Two layers exist and disagree ~14% of the time: the deal-side **Intro Meeting
Status** (rep-maintained, goes stale - the dominant divergence is the deal still reading
Scheduled after the calendar event went no-show or cancelled) and the meeting engagement's
own outcome. The engagement layer is the accurate record of what happened to the event;
the deal layer is what most Pre-Op reports read.

### Closed Lost Pre-Ops keep stale meeting statuses forever

Nobody dispositions meetings on dead leads. Measured 2026-08-23: 43% of Pre-Ops carrying
Scheduled/Rescheduled meeting status with no completed meeting were already Closed Lost
(69% of the past-slot inbound subset). Consequences: (a) exclude Closed Lost records from
any "upcoming meetings" or "SQLs still to come" pool before applying a show rate; (b) a
booked-but-unheld counter that ignores deal stage overcounts.

### Country-level rates need their denominators

UK/Germany-style monthly no-show splits run on 13-75 meetings and 1-5 events. Per
`references/evidence-standards.md`: state the denominator or drop the percentage.

---

## Common Pitfalls to Avoid

When working with Pre-Op data, watch out for these mistakes:

1. **Don't confuse "Meeting Booked" with "Meeting Completed."** A booked meeting that was
   a no-show or was canceled is NOT a completed meeting and NOT an SQL.

2. **Don't assume BD Owner = outbound.** Both conditions (Last Touch Source = Outbound AND
   BD Owner populated) must be true for valid BD attribution.

3. **Don't count Non-BD Outbound as BD-attributed.** These are currently unattributed.

4. **Don't forget the pipeline filter.** Pre-Ops live in four different pipelines. Always
   confirm which pipeline(s) the user means, or default to all four.

5. **Don't assume pipelines are identical.** The US/EU Agency and Enterprise pipelines
   differ in both stages and fields.

6. **Don't edit promoted Pre-Ops.** Once a Pre-Op reaches "Promoted to Deal", the record is
   frozen.

7. **Don't treat Action Required as terminal.** It's a temporary holding stage - Pre-Ops
   can and do return to active stages from there.

8. **Don't use Raw Score (AI) for routing or automation.** It's reporting-only.

9. **Don't assume every Pre-Op = a booked meeting.** While almost always true, rare manual
   exceptions exist.

10. **Don't attribute credit to the original AE after a transfer.** The current Deal Owner
    at time of reporting always gets credit.

11. **Don't use Contact Last Touch Source for attribution.** The Riverside product sends events back to HubSpot that can overwrite Last Touch Source on the Contact record. The Pre-Op's Last Touch Source field is set at creation and locked - use that for all attribution analysis.

12. **Don't compare an in-flight period's SQL count to a closed period's, raw.** SQLs mature
    on meeting completion; maturity-match the windows or project the landing first (see
    Timing & Maturity Rules).

13. **Don't count "upcoming meetings" without excluding Closed Lost Pre-Ops.** Dead leads
    keep Scheduled/Rescheduled meeting statuses indefinitely and inflate any
    pending-meeting or recovery pool.

---

## How to Use This Skill

When the user asks a question about Pre-Ops, intro meetings, or related metrics:

1. Identify which metric or concept they're asking about.
2. Look up the exact definition and logic in this skill.
3. Apply the logic precisely - do not improvise or simplify.
4. If querying HubSpot, use the field names and filter logic documented here.
5. If the question is ambiguous (e.g., which pipeline? which time period?), ask for
   clarification before answering.
6. Always distinguish between "booked" and "completed" meetings in your response.
7. When reporting BD metrics, always verify both the Outbound source AND BD Owner conditions.

### What a finished answer looks like

Done when the answer names the metric's definition from this file, the pipelines and window
it covers, and whether the window is closed or still maturing. Every count or rate is quoted
from a query result with its source and as-of date (`references/evidence-standards.md`);
never invent a number, and never fill a gap with a definition that is not written here. If
HubSpot and the warehouse disagree, report both figures and the likely cause (the
pipeline-filter and maturity sections above) rather than picking one.

For example, "how many SQLs did BD drive this quarter?" comes back as: the definition used
(SQLs by BD, section 9: Intro Meeting Complete Date exists + Status = Completed,
Last Touch Source = Outbound, BD Owner populated), the scope (all four pipelines, fiscal Q3 Aug-Oct to date),
the figure with its source and date, and one line saying the quarter is in flight, with the
projected landing from "An in-flight SQL count is structurally depressed".

### What this skill does not own

This skill does not run the numbers that reach a stakeholder on its own. It is the definition
and field layer:

- **Aggregate figures** (counts, rates, trends for a report or deck) go to `/rivermind:ask`
  first, per CLAUDE.md; use the definitions here to check that its answer means the same thing.
- **Record-level lookups and lists** (which contacts no-showed, who owns a deal) are
  `/hubspot-agent`, which loads this file for its definitions.
- **The daily inbound MQL digest for Nir** is `/nir-mql-live-report`; the daily demo report
  and reply drafting is `/inbound-demo-reply`.
- **Lifecycle journeys and nurture design** (MQL to SQL movement as a flow, not a count) are
  `/lifecycle-agent`.
