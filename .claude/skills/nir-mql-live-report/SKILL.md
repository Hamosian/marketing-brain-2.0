---
name: nir-mql-live-report
description: Daily live report that DMs Nir the new high-quality inbound MQLs who booked a demo (intro meeting) the day before and are still open Pre-Ops. Queries HubSpot Pre-Ops across the three Pre-Op pipelines, filters to inbound + demo-booked-yesterday + high-quality + not-yet-promoted (still in the Pre-opportunity phase), dedupes against a reported ledger, and posts a named lead list to Slack. Runs daily as a cloud routine, or on demand. Trigger phrases - "Nir MQL report", "inbound demo MQLs", "live MQL report", "run the nir mql report", "daily MQL digest for Nir".
---

# Nir MQL live report

The Marketing OS agent's daily digest of **new high-quality inbound leads who requested a demo the day before and are still open Pre-Ops**, DMed to Nir Taranto (Senior Director of Growth Marketing). It answers "which good inbound demo leads came in yesterday and haven't moved to a deal yet" in one Slack message, so Nir sees fresh, still-actionable pipeline without opening HubSpot.

**This is a sanctioned automation skill.** Per `CLAUDE.md`, on **scheduled runs** it is authorized to send the digest DM **without per-message confirmation**, but only under the guardrails below. It never invents lead data and never reports a Pre-Op twice.

## What qualifies (the report definition)

A Pre-Op qualifies when **all six** hold. A Pre-Op is a HubSpot **Deal** record in one of the three Pre-Op pipelines. Load `.claude/skills/preop-data-intelligence/SKILL.md` for the authoritative field semantics - do not improvise definitions.

1. **Inbound MQL** - `Last Touch Source = Inbound` on the **Pre-Op** record. Never use the Contact-level `hs_latest_source`; the product overwrites it (see `systems/owned/hubspot.md` known issues). Last Touch Source is set once at Pre-Op creation and locked.
2. **Demo request** - `Intro Meeting Create Date` is populated (a booked intro meeting). This is the agreed proxy for "requested a demo"; there is no first-class demo-request field.
3. **High quality** - `Raw Score (AI) >= 18` **AND** `Public Domain = false` (business email, not gmail/yahoo).
4. **Booked the day before** - `Intro Meeting Create Date` falls within the **prior calendar day** (from `00:00:00` yesterday up to, but not including, `00:00:00` today, account timezone). This is the "new MQLs from the day before" window: a single-day slice, **not** a rolling lookback. A lead that booked two days ago is out of scope even if never reported.
5. **Not yet moved to a deal (still in the Pre-opportunity phase)** - the Pre-Op has **not** been promoted to a Deal and is not in a terminal stage. Concretely: `Associated Deal ID` is **empty** (promotion is what populates it - see `preop-data-intelligence`) **AND** the Pre-Op's stage is neither `Promoted to Deal` nor `Closed Lost`. Only open Pre-Op stages qualify (Meeting Booked, Follow-Up, Action Required; Enterprise also Intro Completed / Demo Completed).
6. **Not already reported** - the Pre-Op ID is not in the Reported log in `tracking.md` (dedupe safety net; see guardrail 1). With the single-day window this mainly guards against a re-run on the same day.

Pre-Op pipelines (all three, always):

| Pipeline | ID | Market |
|----------|----|--------|
| Pre-Opp - Agency(SMB) | `29354026` | Agency / SMB |
| Pre-Opp - Enterprise | `29152011` | Enterprise |
| Pre-Opp - Europe | `89765536` | EU |

## Guardrails (non-negotiable)

1. **Report each Pre-Op once.** Anything in the Reported log is never re-sent. Dedupe by Pre-Op (Deal) ID.
2. **Never invent lead data.** Every field in the digest (company, contact, score, owner, link) comes from the HubSpot query. If a field is missing, show it as blank, do not guess.
3. **Recipient is config, not improvised.** Send only to the Slack ID in the `tracking.md` Active recipient config. Default rollout DMs Hanan (shadow); flip to Nir only when validated.
4. **Confirmation rule.** Scheduled/headless runs auto-send. Interactive runs draft the digest and confirm the recipient with the user before sending.
5. **Zero new leads means no message.** Do not send an empty ping. Log "no new MQLs" and stop (no commit).
6. **Slack unavailable means no state change.** If `slack_send_message` is unavailable or fails (a headless cloud run may lack an authed Slack connection), do **not** append anything to the Reported log. Leave the records unreported so the next run retries, and surface the failure in the output.

## Steps

### 1. Load state and config
Read `.claude/skills/nir-mql-live-report/tracking.md`. Parse: Active recipient Slack ID, `Raw Score (AI)` threshold, cached HubSpot internal property names, cached per-pipeline terminal stage IDs (Promoted to Deal / Closed Lost), the report window, last-run date, the Reported log (set of already-reported Pre-Op IDs), and the message template.

**First-run / uncached property names:** if the cached internal property names are empty or a query returns `propertiesNotFound`, resolve them live on the `deals` object and write them back to `tracking.md`:
```
mcp__HubSpot__search_properties(objectType="deals", query="last touch")
mcp__HubSpot__search_properties(objectType="deals", query="raw score")
mcp__HubSpot__search_properties(objectType="deals", query="public domain")
mcp__HubSpot__search_properties(objectType="deals", query="intro meeting create")
mcp__HubSpot__search_properties(objectType="deals", query="associated deal")
```
The guessed names `last_touch_source__c` / `bd_owner` are wrong (per `systems/owned/hubspot.md`) - always verify.

**First-run / uncached terminal stage IDs:** the `Promoted to Deal` and `Closed Lost` stages have different internal IDs in each of the three Pre-Op pipelines. If they are not cached in `tracking.md`, resolve the stage label -> ID map for each pipeline live (via the deals pipelines/stages metadata) and cache the `Promoted to Deal` and `Closed Lost` stage IDs per pipeline. These drive the "still in the Pre-opportunity phase" filter in step 2.

### 2. Query HubSpot for qualifying Pre-Ops
Route through `hubspot-agent` conventions. Use `mcp__HubSpot__search_crm_objects(object_type="deals", ...)` with filters, once per Pre-Op pipeline or with a pipeline `IN` filter covering all three:
- `pipeline` IN (`29354026`, `29152011`, `89765536`)
- Last Touch Source (cached name) `= Inbound`
- Intro Meeting Create Date (cached name) `is known` (has property)
- Raw Score AI (cached name) `>= 18`
- Public Domain (cached name) `= false`
- **Intro Meeting Create Date within the prior calendar day**: `>=` start of yesterday (`00:00:00` local, epoch ms) **AND** `<` start of today (`00:00:00` local, epoch ms). This is the day-before slice - it **replaces** the old rolling lookback, so a run only ever returns leads booked yesterday.
- **Associated Deal ID (cached name) `is unknown`** (not populated) - the Pre-Op has not been promoted to a Deal.
- **`dealstage` NOT IN** the cached `Promoted to Deal` and `Closed Lost` stage IDs for all three pipelines - keeps only open Pre-Op stages. (Associated Deal ID being empty already drops Promoted; this also drops Closed Lost and is a belt-and-suspenders guard on promotion.)

Request properties: dealname, pipeline, dealstage, Raw Score (AI), Intro Meeting Create Date, Associated Deal ID, Deal Owner, associated company + primary contact (name, job title). Resolve owner names via `mcp__HubSpot__search_owners` if only IDs come back.

### 3. Dedupe against the ledger
`new = qualifying Pre-Ops - Pre-Op IDs in the Reported log`. If `new` is empty: log "no new MQLs", stop. No DM, no commit.

### 4. Enrich each new lead
For each: company name, primary contact (name + title), Raw Score (AI), market (from pipeline), Deal Owner (AE), and HubSpot record link `https://app.hubspot.com/contacts/9154210/record/0-3/<dealId>`.

### 5. Render the digest
Fill the message template in `tracking.md`. Slack mrkdwn, no em-dashes, mandatory `_Posted by the Marketing OS agent_` footer. Sort leads by Raw Score (AI) descending. Include the by-market count line.

### 6. Send
Send via `mcp__Slack__slack_send_message` with `channel_id` = the Active recipient Slack ID (a user ID = a DM). Interactive run: confirm first. Scheduled run: send directly. If Slack fails, follow guardrail 6 (no state change) and surface the error.

### 7. Persist state
Append each reported Pre-Op ID + today's date to the Reported log, update the last-run date, then commit so state survives to the next run:
```bash
git add .claude/skills/nir-mql-live-report/tracking.md
git commit -m "nir-mql-live-report: reported <N> new MQLs"
git push
```
Only commit when something changed (a DM was sent). In a cloud routine, commit on the routine's branch / open a PR per the routine's convention.

### 8. Report
Summarize: how many new MQLs, recipient, any Slack/query failures. Interactive runs print it; scheduled runs treat it as the routine's output.

## Notes
- **Single-day window, not a lookback.** As of the criteria change, the report is scoped to leads whose `Intro Meeting Create Date` is the **prior calendar day** only. This replaced the earlier 7-day rolling lookback. The Reported ledger stays as a same-day re-run guard, not as the primary time filter. If a daily run is missed, that day's leads are **not** picked up by the next run - they fall outside the day-before window. Backfill manually if a run is skipped.
- **Only open Pre-Ops.** The report deliberately excludes Pre-Ops already promoted to a Deal (`Associated Deal ID` populated) and Closed Lost Pre-Ops, so Nir only sees leads still in the Pre-opportunity phase that are actionable. A lead that booked yesterday but was already promoted or lost by run time will not appear.
- **Inbound is a slightly polluted signal.** The raw inbound Pre-Op count includes ~16.7% PLG existing users, mis-tagged outbound, referrals, and CS (see `sql-mql-attribution/INBOUND-SQL-WITHOUT-MQL-ANALYSIS.md`). The `Raw Score (AI) >= 18` gate plus the demo-booked filter already narrows this considerably; do not add extra dedup logic beyond the ledger.
- **Demo is a proxy.** "Requested a demo" = booked intro meeting (`Intro Meeting Create Date` populated). There is no first-class demo-request field. If a true demo-form signal is needed later, revisit `Form Type` on the Omni `MQLs to SQLs to Deals` model once its values are confirmed live.
- **Attribution field caveats** live in `systems/owned/hubspot.md` and `.claude/skills/preop-data-intelligence/SKILL.md`. Always read the Pre-Op's locked Last Touch Source, never the Contact's.
- This skill is read-only against HubSpot. The only write is the Slack DM and the `tracking.md` commit.
