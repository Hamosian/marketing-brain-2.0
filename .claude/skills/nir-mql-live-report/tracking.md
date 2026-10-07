# Nir MQL live report - tracking & config

State file for the `nir-mql-live-report` skill. The skill reads and rewrites this file on every run that sends a digest. Add cached property names freely; do not hand-edit the Reported log during a run.

## Config

| Key | Value |
|-----|-------|
| Active recipient (Slack ID) | `U07LETHMPAP` (Nir - flipped from shadow rollout 2026-07-03) |
| Raw Score (AI) threshold | `18` |
| Pre-Op pipelines | `29354026` (Agency/SMB), `29152011` (Enterprise), `89765536` (Europe) |
| HubSpot portal ID | `9154210` |
| Report window | **Prior calendar day only** - `Intro Meeting Create Date` >= yesterday 00:00 and < today 00:00 (account timezone). Single-day slice, not a rolling lookback. |
| Deal-stage filter | Include only open Pre-Ops: `Associated Deal ID` empty AND `dealstage` NOT IN the cached Promoted-to-Deal / Closed-Lost stage IDs below. |
| Last-run date | `2026-07-03` |

### Recipients

| Person | Slack ID |
|--------|----------|
| Nir Taranto (target) | `U07LETHMPAP` |
| Hanan Amos (shadow) | `U0A3HCFE90S` |

### Cached HubSpot internal property names (deals object)

Resolve on first run via `search_properties(objectType="deals", query=...)` and fill in. The guessed names (`last_touch_source__c`, `bd_owner`) are wrong - always verify.

Resolved and verified 2026-07-03 against the deals object.

| Concept | Internal name | Notes |
|---------|---------------|-------|
| Last Touch Source | `last_touch_source` | Filter `EQ "Inbound"` |
| Raw Score (AI) | `raw_score__ai_` | Filter `GTE "18"` |
| Public Domain | `public_domain` | Exclude with `NEQ "true"` (values are `"true"`/`"false"`) |
| Intro Meeting Create Date | `intro_meeting_create_date` | Prior calendar day: `GTE` yesterday 00:00 **AND** `LT` today 00:00 (epoch ms). Single-day window. |
| Associated Deal ID | `associated_deal_id` | Resolved 2026-07-15. **Do not filter on it via `search_crm_objects`** - the tool's association-pseudo-property parser matches the `associated_{x}` name pattern and throws `Invalid object_type: deal_id`, even though this is a plain deal property, not an association. Instead fetch it as a property and filter for blank/empty in code. |

### Cached terminal Pre-Op stage IDs (per pipeline)

Resolve on first run from the deals pipelines/stages metadata and cache the label -> ID map. Used to exclude `Promoted to Deal` and `Closed Lost` so only open Pre-Ops (Meeting Booked, Follow-Up, Action Required; Enterprise also Intro Completed / Demo Completed) qualify. `dealstage` filter: `NOT_IN` all six IDs below.

| Pipeline | Promoted to Deal stage ID | Closed Lost stage ID |
|----------|---------------------------|----------------------|
| Agency/SMB (`29354026`) | `67154607` | `67154608` |
| Enterprise (`29152011`) | `66605111` | `66605113` |
| Europe (`89765536`) | `166509142` | `166509143` |

Resolved 2026-07-15 by sampling live deals per pipeline and cross-referencing `dealstage` enumeration labels. Note: the `dealstage` property's enumeration options are global across pipelines and include a 4th "Action Required / Meeting Booked / Intro Completed / Demo Completed / Follow-Up / Promoted to Deal / Closed Lost" stage set (IDs starting `1397905...`) that does not belong to any of our three Pre-Op pipelines - ignore it.

## Reported log

Any Pre-Op (Deal) ID listed here has already been reported and will never be re-sent. Append `<Pre-Op ID> | <date>` per reported lead.

| Pre-Op (Deal) ID | Date |
|------------------|------|
| 61648944464 | 2026-07-03 |
| 61647351066 | 2026-07-03 |

## Message template

Fill and send verbatim structure. Slack mrkdwn. No em dashes. Sort leads by AI score descending. Footer is mandatory. Skip the whole message if there are zero new leads.

```
🎯 New inbound demo MQLs - {WEEKDAY, MON DD}

{N} new high-quality inbound leads booked a demo yesterday ({YESTERDAY}) and are still open Pre-Ops (not yet moved to a deal). By market: Agency {a} · Enterprise {b} · EU {c}.

• *{Company}* - {Contact}, {title} · AI score {X} · {Market} · AE {Owner} · <{hubspot_link}|View>
• ...

_Posted by the Marketing OS agent_
```
