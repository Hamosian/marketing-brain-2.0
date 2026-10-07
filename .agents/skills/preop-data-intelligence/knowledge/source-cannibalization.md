# Pre-Op source cannibalization - QBD leads reclassified Inbound to Outbound

<!-- Loaded on demand by /preop-data-intelligence (see "Attribution Logic - Outbound") and
by /chief-of-staff, which tracks the live version of this as a pattern. Aggregates only:
the record-level detail (contact names, companies, deal ids) stays in the source artifact,
per the repo's pointers-not-copies rule. -->

**Source:** [Pre-Op source cannibalization](https://claude.ai/code/artifact/21138898-4268-40a6-98d4-787c86054770)
· HubSpot portal 9154210 · **data as of 2026-09-06** · owner Hanan Amos, shared with named
people only. Filed into the repo 2026-09-07 at Nir's instruction.

> **This artifact URL was reused.** Until at least 2026-08-10 the same URL held the QBD
> contact audit of 2,588 flagged contacts. It now holds this report instead. Cite the URL
> for *this* content only, and do not assume the earlier audit is still retrievable there.

## What it measures

QBD leads whose Pre-Op now carries **Last Touch Source = Outbound** despite an inbound MQL
origin. **178 Pre-Ops (SQLs), 169 QBD leads.** Two segments, distinguished only by whether
an audit trail exists:

| Segment | Count | What it is |
|---|---|---|
| **Recorded flips** | 93 Pre-Ops, 92 leads | A change event exists: the governance flow's flip-tracking fields hold a previous value of `Inbound`, and/or the flow's event log sheet "Last Touch Source: Inbound to Outbound" (events 2026-05-01 to 2026-08-12). Where both sources cover a deal, the HubSpot fields win. |
| **Undated reclassifications** | 85 Pre-Ops, 79 leads | Outbound today, an Inbound MQL Contact ID attached, a QBD contact, and **no flip event in either source**. Dated by Pre-Op creation because the change date exists only in each record's property history. Nearly all created by the Pre-Opp Creation automation. |

## Why it matters

`preop-data-intelligence` states that Last Touch Source "is set once at Pre-Op creation and
locked… under normal operations it does not change." **That is not what the data shows.**
93 deals carry a recorded manual edit of that field, and 85 more sit in a state that edit
would produce. The field the model calls locked is the field being rewritten, so:

- **Inbound is undercounted and outbound overcounted** on any report keyed to Last Touch
  Source, which is most of them (MQL and SQL definitions, BD attribution, channel ROI).
- **Nir owns inbound attribution.** These 178 records are the mechanism behind the number
  he would be defending.
- **$395,374 ARR** of closed-won business sits inside the affected set (see below), so this
  is not a rounding question.

## Sales outcomes across the 178

- **31** Pre-Ops still open
- **35** promoted to a sales deal
- **17** closed won: **$32,948/mo, $395,374 ARR**
- **5** open sales pipeline: **$16,452/mo**

Money is HubSpot Monthly Recurring Revenue per deal, in deal currency; the sales KPIs count
deals in the four New Sales pipelines associated with these leads.

## Tier split (all 178)

Tier is derived from the Pre-Op's pipeline: **Agency** = US Agency, **Ent** = US Enterprise,
**EU** = EU Agency + EU Enterprise.

- **Agency 81** · **Ent 53** · **EU 44**

Pipeline detail, recorded flips: US Agency 42, US Enterprise 23, EU Agency 21, EU Enterprise
6, US Agency New Sales 1. Undated: US Agency 38, US Enterprise 30, EU Agency 12, EU
Enterprise 5.

## Recorded flips - who and when

Nearly all are **manual user edits made right after the contact was QBD-flagged (median 2
days).** Latency after the QBD flag: **0-2 days 50**, 3-7 days 14, 8-30 days 17, 30+ days 1,
no flag latency recorded 11.

**Highly concentrated.** Eleven actors in total: ten individual users and one automation
(1 event). The top three account for **69 of the 93**, and the single largest for **42 (45%)**.
The remaining eight account for 4 or fewer each.

Per-person counts stay in the source artifact. The concentration is the analytical point and
it survives without the names; a named count next to a flip total reads as a leaderboard, and
this is a data-reliability finding where **intent is not established**. Anyone who needs the
individual breakdown to act on it should open the artifact, where the audience is scoped.

By fiscal quarter: **Q2 FY26 68, Q3 FY26 25.** By month: May 9, Jun 29, Jul 30, Aug 15,
Sep 10. (Riverside fiscal year starts February: Q1 Feb-Apr, Q2 May-Jul, Q3 Aug-Oct, Q4
Nov-Jan.)

## Undated reclassifications - how they read

Their Outbound classification: **Cold Lead 45**, Existing self service user 25, New Sign up 9,
blank 5, Inbound After Prospecting 1.

The first two account for 70 of 85, and both are claims a rep makes about a lead that
arrived inbound. "Existing self service user" in particular describes a PLG user, which is an
inbound origin by definition.

## Deal status at time of reading

Recorded flips: Closed Lost - Pre-Opp 51, Promoted to Deal 18, Follow-Up Stage 16, Meeting
Booked 3, Intro Completed 2, Demo Completed 1, Action Required 1, Closed won 1.

Undated: Closed Lost - Pre-Opp 60 (split across two spellings of the stage, "Closed Lost" 42
and "Close Lost" 18 - a separate stage-naming defect worth fixing), Promoted to Deal 16,
Meeting Booked 3, Follow-Up Stage 3, Intro Completed 1, Action Required 1, Unqualified 1.

## Company size

Full coverage on all 178 records (the deal's Company Size field). Recorded flips skew smaller
(11-50 is the largest bucket at 27); undated skew larger (201-1000 at 23, 10000+ at 15).
So the two segments are not the same population and should not be pooled without saying so.

## Caveats the source states, and you must carry

- **Intent is not established.** Some reclassifications may be legitimate. This is a data
  reliability finding, not a conduct finding, and it must not be presented as one.
- **The undated segment has no bulk-readable flip dates.** Property history on sampled
  records shows Inbound-to-Outbound changes, but **each record must be checked individually
  before any attribution is corrected.**
- One recorded flip was **reverted to Inbound** and is marked as such.
- Two logged deals **no longer exist in HubSpot** and are omitted.
- Event-log coverage ends **2026-08-12**, so September flips are visible only through the
  HubSpot fields. Recency is uneven by construction.
- Period filtering goes by flip date; sales deals follow their lead's flip date.
- A human reviews before this informs a decision.

## Related

- `preop-data-intelligence` SKILL.md, "Source & Attribution" and "Attribution Logic - Outbound"
- `systems/owned/hubspot.md`, "QBD & No-Show Program Fields"
- `.claude/skills/chief-of-staff/data/patterns.md`, pattern "Pre-Opp Last Touch Source flipped Inbound → Outbound by SDRs"
- Nir's own ledger row "QBD and attribution (resolve ASAP - take it)" in `.claude/skills/growth-marketing-team-tasks/data/my-tasks.md`
