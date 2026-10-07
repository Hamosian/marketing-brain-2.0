<!-- last-reviewed: 2026-10-06 (onboarding: list `24889` now suppresses G2 Leads form contacts from the self-serve onboarding series, see Known Issues. Previous 2026-10-05: Pre-Op gap: `Pipeline not known` also fires when a company is linked but its market was blank at evaluation, fix is a manual create; Known Issues: `numberofemployees` far above Clay, 6,487 companies, plus the Praxis LinkedIn-website case. Previous 2026-10-02: Pre-Op gap, fourth case: a Contact with no company gets no Pre-Op and no [PREOPP NOT CREATED] note; associating the company made the workflow create the Pre-Op in seconds, so link the company before any manual create. Previous 2026-09-28 evening: onboarding fix: the self-serve onboarding series was emailing prospects with an open deal; list `24696` now suppresses it, see Known Issues, plus "Who received which marketing email" under the Snowflake section. Also the same evening: plan-family fix live: workflow A2 `1892315393` is now the only writer of `plg_plan_family` and A's seven plan-family actions are gone; stale-field row and "PLG lifecycle workflow chain" updated with the before/after counts. Earlier the same day: added "PLG lifecycle workflow chain": how workflows A, C, the State Router, the State Change Handler and H feed each other, the motion-state to lifecycle-stage map, and the constraint any plan-family fix must meet; stale-field row now counts Business and Mobile/Live payers read as `free`. Earlier the same day, `plg_plan_family` stale-field row: `paid_assisted` also lands on free-plan contacts with a deal, 1,443 of 5,384; Grow-as-free count refreshed to 8,682. Earlier, 2026-09-24: added why a completed intro meeting has no Pre-Op: the workflow's own [PREOPP NOT CREATED] note and its three reasons, plus how to size real gaps. Earlier the same day: marked Dor Druker as departed in the HubSpot teams table) -->
<!-- prior: 2026-09-23 (added "Building audience lists": which contact fields are stale or mislabelled for segmentation, list-builder UI traps, the EU Enterprise pipelines, and query quirks 5-8, from the R4B Target Audience list build and two QA rounds. Earlier the same day: a second cause of vendor meetings with empty `*_cp` fields: the Chili Piper meeting type's guest form lacked the three fields, so a correctly placed Ziff EU link lost its tags while the UTM fields landed; recorded in `systems/owned/chilipiper.md`. Previous 2026-09-20: the BIDIRECTIONAL_SYNC-alone signature also fits a real vendor meeting handed off by email: the handoff thread and the Gong guest list sit on the Contact, read them before calling it "not the vendor's"; a no-show is readable the same way. Previous 2026-09-11: added Chili Piper double-logging, future NO_SHOW mis-click and departed-owner routing; the BIDIRECTIONAL_SYNC tell now applies to a sync meeting standing alone on its contact; Chili Piper platform mechanics live in systems/owned/chilipiper.md) -->
# HubSpot

> CRM, lifecycle marketing, and marketing-side attribution.

## Overview

HubSpot is Riverside's CRM and marketing attribution layer. It tracks the full lead lifecycle: from first touch through intro meeting (Pre-Op), pipeline opportunity (Deal), and closed revenue.

**Scale:** ~2.4M contacts, ~22.5K Pre-Op records, ~36K total deals.

**How leads enter HubSpot:**
- Webflow form fills (website, landing pages)
- Direct ad platform sync: LinkedIn Lead Gen Forms + other ad platform integrations push leads directly as contacts
- Product events from the Riverside platform (sign-ups, activations) sync back into HubSpot contact records - this is the primary source for B2C/PLG contacts (lifecycle stage: `subscriber`)

**Who owns it:** Jonathan Galili (HubSpot infrastructure, integrations, attribution pipelines). Hanan Amos owns strategy and tooling decisions.

**HubSpot portal:** `app.hubspot.com` (account ID: 9154210)

## How Claude Works With This

| Action | How |
|--------|-----|
| Read deals/contacts/companies | HubSpot MCP (`get_crm_objects`, `search_crm_objects`) |
| Manage records | `manage_crm_objects` (always confirm before writes) |
| Campaign data and attribution | `read_campaign_data`, `get_campaign_attribution_reports` |
| Pre-Op / meeting analysis | `preop-data-intelligence` skill |
| Find owners (AEs, BDs, CSMs) | `search_owners` |
| Review/audit/sign off on a workflow | `hubspot-workflow-qa` skill - QA checklist, naming conventions, and Monday.com ticket process |

## Read-Only API Access

Claude reads HubSpot data through the HubSpot MCP server (`get_crm_objects`, `search_crm_objects`, `query_crm_data`, etc.) - no manual API setup needed for that path.

For a standalone script or tool that needs direct read-only REST API access (outside the MCP), use a scoped Private App rather than a full-access API key:

1. In HubSpot: **Settings → Integrations → Private Apps → Create a private app**.
2. Name it descriptively (e.g. `<team> - Read Only`).
3. On the **Scopes** tab, grant only the `.read` scopes you need (e.g. `crm.objects.contacts.read`, `crm.objects.deals.read`, `crm.objects.companies.read`, `crm.schemas.deals.read`, `marketing-email.read`). Do **not** grant any `.write` or `.delete` scopes - HubSpot enforces this at the API level, so write/update/delete calls made with a read-only token get rejected with a 403.
4. Create the app and copy the access token (`pat-...`). Store it as a secret (env var / secrets manager) - never commit it to this repo.

Portal: `app.hubspot.com` (account ID: 9154210).

## Pipeline Map

Riverside uses 13 pipelines total. Always filter by pipeline when querying deals.

### Pre-Op Pipelines (top-of-funnel intro meetings)

| Pipeline (current label) | ID | Market | Closed Lost stage |
|----------|----|--------|--------|
| Pre-Opp - US Agency (was Agency(SMB)) | `29354026` | Agency / SMB | `67154608` |
| Pre-Opp - US Enterprise (was Enterprise) | `29152011` | Enterprise | `66605113` |
| Pre-Opp - EU Agency (was Europe) | `89765536` | EU | `166509143` |
| Pre-Opp - EU Enterprise | `916013614` | EU Enterprise (since Aug 2026) | `1397905045` |

"Promoted to Deal" is a closed stage (`hs_is_closed = true`), so `Is Deal Closed? = false` selects only in-flight Pre-Ops.

**Pre-Op stage differences by pipeline:**
- Agency(SMB) + Europe: Meeting Booked → Follow-Up → Action Required → Promoted to Deal / Closed Lost
- Enterprise: adds two extra stages after Meeting Booked: **Intro Completed** and **Demo Completed** before Follow-Up

**Meeting Booked entry-stage IDs** (needed for manual Pre-Op creation; verified 2026-08-25):
Agency(SMB) `29354026` → `1033613941`, Enterprise `29152011` → `1031377048`, Europe `89765536` → `1033614704`.

**Recurring calendar-sync gap (open, as of 2026-08-25):** BD-outbound intro meetings are being
booked on the contact without the Pre-Op auto-generating, so AEs surface companies with a booked
meeting but no Pre-Op. Seen on Vortex Cloud (2026-08-24) and My Wealth Solutions + MEP Technologies
(2026-08-25); Spacebring the same day generated fine. Interim fix is manual creation with
meeting-data backfill - full recipe in `.claude/skills/preop-data-intelligence/SKILL.md` under
"Force-generate limitation and the manual fallback". `force_generate_pre_opp` is **not** a reliable
workaround for these: it does not re-enroll existing/older contacts. Root-cause fix on the
"Pre-Opp Creation [2026 build]" workflow (flow `1819472043`) is still needed.
**It is not only existing contacts (2026-09-24).** Five affiliate contacts had a completed intro and no
pre-opp anywhere: three pre-2026 contacts (fits the re-enroll gap) and two created days before their
meeting (Rhonda Lanouette `248846420917`, W Silver `246947649348`), so a second failure exists. Reported
to Hanan; `inbound-demo-reply` Step 3.6 now checks every booking for a pre-opp each morning.

**Why a completed intro meeting has no Pre-Op: read the workflow's own note first (added
2026-09-24).** The workflow does enroll these contacts, new and old alike. When it skips creation it
logs a note on the Contact that starts `[PREOPP NOT CREATED]` and names the reason, the territory,
the company market and the meeting or form that triggered it. Search the Contact's notes for that
token before guessing. There are three reasons, and each is a different fix:

| Note reason | What happened | Example (2026-09-24, from Nir's affiliate-cohort report) |
|---|---|---|
| `Meeting Type not in trigger conditions` | The meeting arrived by calendar sync (`BIDIRECTIONAL_SYNC`: the AE sent their own invite, Chili Piper never ran), so when the workflow read it there was no sales-intro meeting type on it, or the AE had typed it `cs_intro` / `cs_renewal`. A sync meeting created *before* the Contact exists never fires the trigger at all, even with the right type. | W Silver / Broughton (`246947649348`): the real intro (created 4-Sep, contact created 7-Sep) never triggered; the 10-Sep and 15-Sep meetings were rejected. John Walsh / Beat Media (`253302951`): rejected three times, so this was not the old-contact gap. |
| `Pipeline not known` | No company on the Contact (personal Gmail/Yahoo address), so territory and market are blank and the workflow cannot pick a pipeline. Also fires when a company **is** linked but its Company Market was still blank when the workflow ran (see "Company linked, market blank" below). | Rhonda Lanouette (`248846420917`), Jamie Egenti (`500425251`); market blank: Cindy Diffenderfer (`252631009540`) |
| `Existing Open Deal or Business Customer` | By design: the Contact sits under a company with an open deal or a customer lifecycle. It also fires when a subsidiary's contact is associated with a parent that is a customer. | Tim Pritchard (`243930151229`): the `omc.com` domain ties him to Omnicom (customer, 1 open deal) as well as Manning Gottlieb OMD |

The workflow writes these notes on every meeting it evaluates, follow-ups included (about 19,800
between 2026-06-01 and 2026-09-24), so a count of notes is not a count of gaps. To size real gaps,
start from completed sales-intro meetings whose contact has `number_of_associated_pre_opps = 0`, and
then drop any company that already has a Pre-Op from the same cycle. `number_of_associated_pre_opps`
counts the contact's own Pre-Ops only. Most "missing" ones are sitting on the company under a
different contact: 243 of the 288 typed sales-intro meetings in that window were covered that way.
Also include meetings with an empty `hs_activity_type`. A SQL `NOT LIKE` filter on the type
silently drops them, and those are the calendar-sync meetings this gap is about.

**No company on the Contact and no note at all: link the company first (added 2026-10-02).** A
fourth case writes no `[PREOPP NOT CREATED]` note, so the note search above comes back empty. Andy
Hauer (`27234051`, created 2021) booked an inbound enterprise intro through Chili Piper on
2026-10-01 (`meeting_type_cp__c` = `sales_intro_inbound_enterprise__`, meeting `117818457247`).
His work address (`cru.org`) matched an existing Cru company (`6611545955`, 179 contacts), but the
Contact had no company associated. No Pre-Op was created and the Contact had no notes at all. On
2026-10-02 the Contact was associated with Cru as its primary company, and the workflow created
the Pre-Op 8 seconds later (`65535312526`, US Enterprise, Meeting Booked, owner = the meeting
host, Inbound, meeting attached). So this was not the old-contact re-enroll gap, even though the
Contact was old. Why the Contact had no company, and which trigger condition fired on the
association, were not read.
- **Check:** a booked sales intro, `number_of_associated_pre_opps = 0`, no note, and no company on
  the Contact while a company with the email's domain exists.
- **Fix:** a domain match is only a candidate. Confirm it is the right company first (one record
  for the domain, company name matches the Contact's `company` field). If more than one company
  matches, or a parent and subsidiary both do (the Omnicom case above), ask the requester which one
  before changing anything. Then associate it as **Primary** and wait about a minute before creating
  anything by hand. Creating the Pre-Op manually in the same pass produced a duplicate on 2026-10-02.

**Company linked, market blank when the workflow ran (added 2026-10-05).** `Pipeline not known`
does not always mean "no company". Cindy Diffenderfer (`252631009540`) was a new contact
(2026-10-02 22:06:49Z); HubSpot auto-created her company OHAI (`58950912564`) from the email
domain one second later and she booked an inbound agency intro through Chili Piper at 22:08Z.
The workflow evaluated the meeting at 22:21Z and logged `Pipeline not known` with
`Company Market:` blank. By 2026-10-05 OHAI read `Agency`, but nothing re-runs the workflow
once the market fills in, so the booking stayed without a Pre-Op. When the market was written
was not read (no property history through the MCP), so whether this is a race with whatever
sets Company Market or that logic running late is open.
- **Check:** the note says `Pipeline not known` but the Contact has a company, and the company's
  `company_market` is filled now.
- **Fix:** create the Pre-Op by hand (`preop-data-intelligence` manual recipe). Force-generate is
  not a shortcut: HubSpot rejects `force_generate_pre_opp` = true unless
  `source_of_forced_pre_opp_ae_input` is set with it, so write both in one update. Done for Cindy on 2026-10-05
  (`65672025511`, US Agency, Meeting Booked).
- **Note text:** the note prints the Company Market *label*. `Agency (Mid Market)` is the value
  `Mid Market`, not two markets. Mitch Carson (`198949383550`) got `Pipeline not known` with that
  market on a Business Plan form trigger (2026-10-04 07:41Z), and a meeting booked 16 hours later
  created his Pre-Op in US Agency normally (`65668004764`). Why the form path could not pick a
  pipeline for Mid Market was not traced. His first booking (2026-10-03 07:36Z, company created 2
  minutes before) left no note at all, also not traced.

### Sales Pipelines (post-Pre-Op opportunities)

| Pipeline | ID | Type |
|----------|----|------|
| US Agency New Sales | `9297003` | New business, Agency/SMB. Closed won `26497059`, closed lost `26497060` |
| US Enterprise New Sales | `9308023` | New business, Enterprise. Closed won `26589200`, closed lost `26589201` |
| EU Agency New Sales | `89892425` | New business, EU. Closed won `166590834`, closed lost `166590835` |
| EU Enterprise New Sales | `916006193` | New business, EU Enterprise (since Aug 2026). Closed won `1397903678`, closed lost `1397903679` |
| Renewals | `3711152` | Existing business renewals. Closed won `12706105`, closed lost `12706106` (the CS churn record) |
| Upsell Pipeline | `33402955` | Upsell to existing customers |
| Account Expansion | `891525221` | Expansion revenue |
| Partnership & Channel Sales | `2662763` | Partner-sourced deals |
| Influencer Marketing | `71445776` | Creator/influencer deals |

**New Sales stages (each of the four New Sales pipelines has its own stage IDs):**
S1 Needs Discovered → S2 Buy-in from wider team → S3 Trial → S4 Decision Maker Buy-in → S5 Commercials → S6 Legal & IT & Security → S7 Draft Contract → S8 Pending Payment → Closed Won / Closed Lost

**Renewals stages:** Active Client → Ready for Renewal → Notice Sent → Meeting Scheduled

## Key Objects

- **Contacts** - 2.4M records. Lifecycle stage `subscriber` = PLG/product signups. New contacts often enter with `hs_lead_status = "BD: New/Not Contacted"` triggering BD outreach workflows.
- **Pre-Ops (Deals in Pre-Op pipelines)** - intro meeting tracking. See `preop-data-intelligence` skill for full field definitions and KPI logic.
- **Deals (Sales pipelines)** - post-Pre-Op opportunities, one Deal per promoted Pre-Op (1:1).
- **Companies** - account-level rollup associated with contacts and deals.
- **Campaigns** - marketing campaign attribution.

## Team Structure in HubSpot

| Team | Role | Key members |
|------|------|-------------|
| AE | Account Executives (close deals) | Nicole Passarelli, Debbie Mohnblatt, Carley Cowman, Merrin Trombka, Netta Abres, Michael Bassal |
| BD | Business Development (book meetings) | 30+ reps including Jordan Landes, Jack Bergman, Meital Tschernia, Danielle Baxter |
| BD Managers | Manage BD team | Richard Dieu, Zach Ben-Levy, Joel Pearlman, Anna Muni |
| Agency | Agency-focused AEs | 27 members including Jared Young, Ori Tal, Liran Ben-Gal |
| Enterprise | Enterprise-focused AEs | Hagai Benziman, Anton Fridman, Stacey Elman, Carley Cowman, Tom Lepage, Merrin Trombka, Erin Neal |
| Customer Success | CSMs | 30 members, owns Renewals pipeline |
| Marketing | Growth team | Hanan, Savion, Gili, Erika, Dor (departed 2026-08-04), Jonathan, Nir, Dalit + others |
| RevOps | Operations | Dan Markel, Daniel Weisfelner, Daniel Nitsan |

## Riverside Use Cases (deal field)

Executive interviews, Internal communication, Keynote speakers, Learning & Development, Live show, Onboarding videos, Panel discussions, Podcasts, Private podcasting, Radio, Talking head presentations, Testimonials, Town halls, Training materials, Video marketing materials, Virtual events, Voice overs, Webinars

## Self-Serve Scoring & the 24h Frozen Score

The self-serve (PLG) lead scoring system lives on the Contact object. Owner: Hanan. Validated 2026-07-12 (statistical battery, triple-verified); definitive read due ~2026-08-31 on the July cohort.

**Live score fields:** `self_serve_composite_score` (identity + behavior blend, observed range 0 to ~44), `self_serve_identity_score` (ICP), `ss_behavior_score` (first-day product activity), `self_serve_lead_tier` (High/Mid/Low Quality). Behavior inputs sync from Snowflake via Hightouch.

**Tier thresholds** (workflow `1785077505`, on `self_serve_composite_score`): before 2026-07-12 High was >= 75 then >= 51, both above the score's actual maximum, so High Quality was always empty and Mid nearly so. Since 2026-07-12: **High >= 23, Mid 12 to 22.99, Low < 12** (expected shares ~5% / ~35% / ~60%). Any tier calibration must split cohorts at 2026-07-12; `lead_tier_at_24h` snapshots before that date reflect the unreachable-threshold regime.

**24h frozen snapshot (measurement infrastructure, live since 2026-06-29 13:09 UTC):** workflow "Score snapshot at 24h" stamps write-once copies at contact age 24h: `composite_score_at_24h`, `icp_score_at_24h`, `behavior_score_at_24h`, `lead_tier_at_24h`, `score_24h_captured_at`, `score_24h_pre_paid_flag`. QA as of 2026-07-12: fill rate 100%, capture at almost exactly 24h, zero leakage (every snapshot pre-dates payment), zero at-or-below-zero scores. Config doc: `SelfServe_24h_Frozen_Score_Config.docx` (Hanan).

Conventions that will bite you:
- `score_24h_pre_paid_flag` is written **only when true** (Option A branch). Filtering `= 'false'` matches nobody; exclude `= 'true'` instead. Pair that exclusion with `score_24h_captured_at IS NOT NULL` (or `composite_score_at_24h IS NOT NULL`) so the pre-paid cohort filter cannot silently admit unsnapshotted contacts, which also have a non-true flag.
- `lead_tier_at_24h` is **null** (not "Unassigned") when the live tier was empty at 24h. ~45% of pre-2026-07-12 snapshots are null. See `query_crm_data` quirk 2 below for how GROUP BY misreports these nulls as an "Unassigned" bucket.
- `signup_composite_score` (freeze-at-creation predecessor) is null on every contact portal-wide; the at-creation copy always grabbed null. Retire or ignore.

**`quality_signup` is generated by the scoring system, never use it as a validation target or ads signal.** Values: `no` / `mid quality` / `strong`. Every labeled contact sits above fixed score thresholds (all mid-quality in the validation cohort were composite >= 30) and labels get reassigned as live scores move, so score-vs-label AUC (~0.999) is circular. The `strong` assignment stopped for contacts created after April 2026 and `mid quality` volume fell ~10x; whoever consumes that label has been starved since May.

**Validation results (preliminary, 47 converters, cohort Jun 29 to Jul 10):** frozen composite AUC 0.620 vs paid self-serve conversion (live-score baseline 0.64, so leakage ~0.02); behavior component 0.723 (carries all the signal); ICP component 0.472 (chance). ~73% of self-serve payers pay within their first 24h, so any 24h score only ranks the remaining ~27%. Full report artifact linked from the 2026-07-12 session; re-run the same banded-count method for the definitive read.

## QBD & No-Show Program Fields

QBD = "Quit Before Demo": an MQL who submitted a demo form but never booked the meeting. The `page-cro` skill tracks the QBD *rate* per page; the Contact fields below flag the *people* and route them into inbound SDR follow-up (workflow `1696104547`, "[Lead Routing] QBD - MQL without meeting - Inbound SDR Followup"). Audited 2026-08-10 against all 2,588 flagged contacts. **That audit's artifact URL has since been reused:** `https://claude.ai/code/artifact/21138898-4268-40a6-98d4-787c86054770` now serves a different report, "Pre-Op source cannibalization" (data as of 2026-09-06) - verified 2026-09-07. Ask Hanan for the current location of the 2,588-contact audit rather than citing that URL for it. Both are private hosted artifacts (owner Hanan, named viewers only) containing contact names, so check the sharing note there before forwarding.

**QBD leads reclassified Inbound to Outbound ("source cannibalization").** The report now at that URL finds **178 Pre-Ops / 169 QBD leads** carrying Outbound Last Touch Source over an inbound MQL origin - 93 with a recorded flip event, 85 undated - with **$395,374 ARR** of closed-won business inside the set and a median flip **2 days after the QBD flag**. It reads directly on inbound attribution, which Nir owns. Figures, method and caveats: `.claude/skills/preop-data-intelligence/knowledge/source-cannibalization.md`.

**Where the program runs** (per the inbound-activation transition doc, 2026-08, Google Doc `1Fvqg5NV3haVFWUXPL_jeyR8rMiEhBhZ3ATg3zhsiy54`). QBD is one of the inbound re-engagement motions, alongside No-Shows (booked but did not attend). HubSpot is the system of record:
- **QBD dashboard:** `app.hubspot.com/reports-dashboard/9154210/view/18005266`
- **Automated QBD re-engagement email:** campaign `381242208`, plus existing QBD outreach templates. Contact owners get an email notification when they own a QBD.
- **Signal capture:** the Book a Demo page workflow (`1732408125`) is where the abandonment is flagged.
- **Enterprise QBDs** are monitored and flagged in Slack `#enterprise-inbound`.
- **Project tracking** for the motion is Monday board `7685991621`; RevOps is building a more systemized tracker, with an interim manual spreadsheet used to attribute which outreach motions drive meetings. The workstream's primary KPI is demos booked, segmented by source (signal-based, QBD / No-shows, LinkedIn, webinar).

**Contact fields, per-field verdicts (as of 2026-08-10):**

| Field | Verdict | Detail |
|-------|---------|--------|
| `is_qbd_lead`, `first_qbd_timestamp`, `last_qbd_timestamp` | Reliable | 100% populated. `last_` matches `first_` within 1 min on 98% of records and within 1 hour on the remaining ~2% (no re-trigger observed anywhere), so analyses key on `first_qbd_timestamp` alone |
| `booked_after_qbd`, `completed_after_qbd` | Reliable | Internally consistent; the only safe basis for QBD conversion rates |
| `qbd_outcome` | Broken for rates | Blank on 81.8%. The `Not Booked` option has **never been written once**, so it records wins only - no denominator, no conversion rate. Also credits only the BD-task touch; the automated email and manual follow-up land in the misleading "Alone" values |
| `qbd_owner` | Dead | Populated on 1 of 2,588. Use `hubspot_owner_id` as a weak proxy (contact owner, not QBD worker) |
| `amount_of_qbd_indicators` | Dead | Constant 1 on every record despite being described as a counter |
| `qbd_bd_task_timestamp` | Partial | Only exists from the BD-task launch **2026-05-25**; useful as the launch marker |
| `lead_original_source` | Dead (on this cohort) | Blank on all 2,588 QBD leads, so inbound/outbound cannot be confirmed from it |

**No booking date exists at usable coverage.** `bd_qbd_booked__timestamp` (50), `engagements_last_meeting_booked` (70), `meeting_booked` (87 of 630 booked). "Booked within N days" is not computable for anyone until the workflow that flips `booked_after_qbd` also stamps a datetime.

**No-Show sibling suite is dormant and carries a landmine.** `is_no_show_lead`, `first/last_no_show_timestamp`, `booked/completed_after_no_show`, `no_show_outcome`, `no_show_owner`, `amount_of_no_show_indicators`: zero records on all of them (never launched). The `no_show_outcome` options were cloned from QBD and the **internal values were never renamed** - the option labeled "Booked from No-Show Work" stores the literal string `Booked from QBD Work`. Harmless at zero records; the day the program turns on, unscoped raw-value consumers - anything comparing enum values without scoping them to the `no_show_outcome` field (cross-field rollups, exports, the Snowflake sync) - can count No-Show outcomes as QBD outcomes. Rename the internal values before launch - zero records means no data migration, but not zero references: first audit anything that points at the old QBD-derived values scoped to this field (workflow branches, saved filters, lists, exports, the Snowflake sync mapping), update those in the same change, then rename the options keeping their labels.

**Enum values are inconsistent across the siblings:** `is_qbd_lead` stores `true`/`false`, `is_no_show_lead` stores `Yes`. Always `get_properties` before filtering - a `= 'true'` filter on the No-Show flag silently returns zero.

**Deal-side source-flip tracking** (feeds governance workflow `1851241373`, "[Governance] Checking Last Touch Source Change"): `last_touch_source` (enum Inbound/Outbound/Customer Success), `previous_last_touch_source_value`, `last_last_touch_source_modified_date`, `last_touch_source_change_type/name/ref`, plus `inbound_mql_contact_id` as a direct deal-to-contact join key. These fields are **only populated from 2026-07-02**, so any flip count is a floor for that window. First audit (2026-08-10): 63 flips portal-wide, all Inbound to Outbound, all manual user edits; 27 QBD contacts affected, every flip after the QBD flag (median 4 days), 20 of 27 inside the 80 "from QBD work" credits.

**Pulling at scale via the MCP:** oversized `search_crm_objects` results are auto-saved to a local file instead of returning inline. That is the practical route for bulk pulls - page with `limit: 200` + `offset`, let each page land on disk, then aggregate the saved files with a script. A 2,588-record pull is 13 pages. Treat the saved result files as sensitive HubSpot data (they carry names, emails, and deal details): keep them in the session scratchpad or another private workspace, never commit or share them, and delete the intermediates once aggregated. Deal record URLs use object type `0-3` (`app.hubspot.com/contacts/9154210/record/0-3/{dealId}`); contacts use `0-1`.

## Pre-Opp Attribution Redesign (in flight)

The response to the source-flip problem above. Direction agreed across Growth and RevOps (as of 2026-08-14): attribution facts get stamped by workflows at fixed events and locked, and BD compensation stops depending on anything a rep can edit: it reads the locked source stamps plus evidence fields, so working an inbound Pre-Opp has a paid lane that does not require corrupting the source. The flips hit the whole inbound funnel, not one program: all 63 audited flips took an inbound Pre-Opp to Outbound, and the 27 QBD ones are just the best-instrumented slice. **Nothing below is live yet** - `last_touch_source` is still rep-editable, and the flip-tracking fields plus the 2026-08-10 audit above remain the current state.

**Two working documents:**

- **Growth's compiled solution** (hosted artifact `https://claude.ai/code/artifact/cbf2479b-8771-4fef-8147-61d87804a8cf`, private - ask Hanan for access), built from the Hanan + Nir + RevOps attribution discussion (Google Doc `1IXTwCXdrZXDQFEXkWGMqIUmox0VW54bAAN0eR7Aj2C4`, tabs 1 and 2). Three-layer field model (system-stamped locked facts / rep-editable additive context / calculated validation with a 60-day window), evidence-based comp lanes with the assisted rate left open for Nir + RevOps, and a Phase 0 that needs no build: lock rep edit rights on `last_touch_source`, add a same-day RevOps alert to workflow `1851241373`, and announce the lock together with the assisted lane.
- **RevOps' "Riverside Attribution Model"** (Matan + Kartikeya, Aug 2026, collaborative Excalidraw board - the link carries edit access, get it from Hanan or Matan). The fuller build: LOCK 1/2/3 stamping (Pre-Opp created / first meeting booked / first meeting completed; written once, never overwritten by status changes, rep read-only, RevOps-edit only), three separate source sets (`Last Touch` / `First Booked Meeting` / `First Completed Meeting`, each with Source + Detail #1 + CTA), per-meeting fields parsed from the Chili Piper description (`meeting_source_cp` / `meeting_medium_cp` / `meeting_campaign_cp`, not yet real Omni columns), Multi Attribution Source (auto-set by comparing the locked sets inside the window, RevOps-overridable), Pull/Push intent derived from Detail #1, Pre Opp Number for re-engagement, 11 worked customer flows, and an open-decisions list headed to Michal.

**BD comp in the RevOps model:** primary = `last_touch_source` = Outbound AND BD Owner populated. This is consistent with the lock principle above, not a contradiction of it: in the target state `last_touch_source` is LOCK-1-stamped at creation and rep-read-only, so primary comp reads a locked fact rather than today's editable enum, and comp is only safe to switch on after that lock lands. Secondary = `last_touch_source` NOT Outbound AND a BD value in Multi Attribution Source AND BD Owner populated, all mandatory (the NOT-Outbound wording exists so a CX-sourced no-show recovered by BD still pays; see their Flow 11). Primary vs secondary is derived from `last_touch_source`, not a new field. Both pay the same in their model. The multi-touch window is 45 days, proposed, pending Michal's sign-off.

**Known deltas between the two documents (raised with Matan as clarification questions, 2026-08-14):** equal secondary pay is asserted as decided but was an open rate decision on the Growth side; 45-day window vs the 60 days in the marketing proposal; no journey-level first-touch field and no first/last/calculated validation triad (their own open item concedes `last_touch_source` is an originating-touch concept whose name misleads); no meeting-to-company-to-contact "meaningful initiator" resolution; no enforcement rollout (when the rep-edit lock lands, whether the `1851241373` alert stays on as tripwire, and what happens to the 63 recorded flips and comp already paid on them); and no definition of what BD activity qualifies to auto-write a BD value into Multi Attribution Source - with equal pay and a 45-day window, a single logged call could turn any inbound SQL into full secondary comp.

## Chili Piper (`*_cp`) Meeting Fields & Vendor Attribution

The `_cp` Contact fields are written by Chili Piper when a meeting is booked through a Chili Piper
scheduling link. Two families:

- **Source** - `meeting_source_cp`, `meeting_medium_cp`, `meeting_campaign_cp`. Pulled from the
  scheduling link's parameters and echoed into the meeting description. These carry the
  vendor/affiliate attribution.
- **Lifecycle** - `meeting_type_cp__c`, `meeting_creation_date_cp__c`, `booking_status_cp__c`,
  `confirmed_cp__c`, `canceled_cp__c`, `no_show_cp__c`, `rule_name_cp__c`.

Appointment-setting vendors (ZiffDavis/SWZD, MemoryBlue, Pursuit, Boscia) book on their own tagged
link. A correctly tagged vendor meeting looks like this (sampled across 101 ZiffDavis contacts,
2026-08-17 - the signature is identical on every one):

| Field | Value |
|-------|-------|
| `meeting_source_cp` | vendor tag, e.g. `ziffdavis` |
| `meeting_medium_cp` | `affiliate` |
| `meeting_campaign_cp` | `bookmeeting` |
| `utm_source` / `utm_medium` | mirror of source / medium |
| `meeting_type_cp__c` | `sales_intro_inbound_agency_10d_` |
| `contact_source` | `Outbound` |

**`meeting_type_cp__c` is the diagnostic, but it does not imply empty source fields.** The plain
`sales_intro_inbound_agency__` (no `_10d_`) means the booking resolved a link wired to the *website*
meeting type rather than the vendor's. **Corrected 2026-09-09:** this doc previously said that also
meant "no source parameters were captured and all three source fields are empty". It does not. The
meeting type and the source parameters are set by two independent mechanisms - the type comes from
the scheduling **link record**, the `meeting_*_cp` values from **query parameters** - so a vendor
booking through a website link lands on the plain type with `meeting_source_cp`,
`meeting_campaign_cp` and `meeting_medium_cp` all correctly populated. Treat these as three separate
signatures:

| `meeting_type_cp__c` | `meeting_*_cp` source fields | What it means |
|---|---|---|
| `_10d_` | populated | Correct. Vendor booked on a properly wired vendor link. |
| plain | **populated** | Vendor booked through a `__website_` link. Attribution survives; the prospect got a 5-day calendar instead of 2 weeks. |
| plain | empty | Vendor booked off-link entirely. This is the invoicing blind spot below. |
| `sales_intro_inbound_enterprise__` | empty, but `utm_source` = vendor tag and `utm_medium` empty | Vendor booked on the US 1000+ website link through the malformed double-`?` URL that lacks `meetingTypeId`. Chili Piper ran, parsed the tags, and did not capture them. Two cases as of 2026-09-17 (contacts `244765888081`, `248602780935`); mechanism and the working URL in `systems/owned/chilipiper.md` Known Issues. Backfill the three `*_cp` fields once the vendor claim is established. |

Only the third and fourth rows are attribution failures. The second is a booking-experience and window defect,
and the full mechanism is in `systems/owned/chilipiper.md`.

**Failure mode: a vendor meeting you are invoiced for that the attribution layer cannot see.** When
a vendor books outside their tagged link, the meeting is real, held, and billed, but it carries no
`meeting_source_cp` - so it never enters the affiliate contact pull and is missing from the vendor's
SQL count, cost-per-SQL, and ROI in the Affiliate Channel Funnel dashboard. Verified 2026-08-17 on
contact `116315091032` (Milind Patel, Kingsley Napley LLP): intro call held 20-Jul-2026, claimed by
ZiffDavis on their tracker (row 81, "Meeting Held", August invoice month, matching email and time),
every CP and UTM source field empty. Backfilled the three CP fields by hand. This is silent and
recurring - it will repeat on every meeting the vendor books off-link, so treat a fix on one record
as a patch, not a resolution.

**Failure mode: a vendor with no link of its own books on another vendor's tagged link.** Worse
than off-link booking, because the meeting is *tagged* - to the wrong vendor - so nothing looks
missing. Verified 2026-08-19 on the entire Boscia Group / L&D Collective engagement: Boscia never
got its own tagged link, so its SDRs (Sam Blackwood, Alex Stewart, @bosciagroup.com) booked all 7
delivered client meetings (BAE, Marriott, Brookdale, Bain, AdventHealth, AOL, Humana) through
**memoryBlue's** link. Every one carried `meeting_source_cp = memoryblue`, crediting memoryBlue's
SQL count with Boscia's work, and several were booked with the SDR's own email, hiding the client
entirely (the real client is recoverable from the meeting's contact associations and the booking
payload echoed in `hs_meeting_body`). This blocked the L&D renewal decision until fixed (Monday item
`12755969908`). Fix applied 2026-08-19 across 11 contacts: client contacts re-tagged/backfilled to
`meeting_source_cp = boscia group` (when the wrong vendor's link had also stamped `utm_source`, the
UTM was re-pointed too, so the dashboard's OR-pull doesn't double-attribute - the "leave UTMs empty"
rule below applies to *empty* fields, not wrongly captured ones), and the vendor-staff contact
records (`232391599451`, `234244423937`) had CP+UTM tags cleared so vendor employees stop counting
as anyone's SQLs. Prevention is the same both ways: every appointment-setting vendor gets its own
tagged link and books with the client's email - made a condition of the Boscia renewal.

**A second path to the same wrong answer:** that record's Pre-Op was force-generated
(`force_generate_pre_opp = true`) with `source_of_forced_pre_opp_ae_input = Inbound`, which is what
stamped the Pre-Op `last_touch_source = Inbound`. A vendor-sourced meeting can therefore read as
inbound at both the Contact and the Pre-Op level without anything looking broken.

**Fix the CP fields, not the source fields.** `contact_source` and the Pre-Op's `last_touch_source`
define the MQL (MQL = inbound Pre-Op, see `preop-data-intelligence`), so flipping them to Outbound to
"correct" vendor attribution moves the record out of the inbound MQL count - a reporting change, not
a data fix. Pre-Op Last Touch Source is also set-at-creation and treated as locked. The affiliate
pull ORs `utm_source` / `meeting_source_cp` / `meeting_medium_cp` / `utm_medium`, so
`meeting_source_cp` alone is enough to restore attribution. Leave the UTM fields empty unless asked -
they are meant to be captured from URL parameters, not hand-written.

**Contact age is not evidence against a vendor's claim.** A contact who first reached us long before
the vendor engagement still gets vendor-tagged on a later meeting - e.g. contacts created 2025-05-04
carry `meeting_source_cp = ziffdavis` on 2026-08-11 meetings. Verify the claim against the vendor's
own tracker (for ZiffDavis, the SWZD performance sheet in `references/team-context/growth-channels.md`,
which lists booked date, meeting date, status, and invoice month per meeting), not against the
contact's create date.

**Nor is the SQL date - and a pre-program SQL date means the meeting is a re-engagement, not a new
SQL.** The `*_cp` source fields are stamped by Chili Piper at *booking* time and the newest booking
overwrites the last, but `hs_v2_date_entered_salesqualifiedlead` is a one-time lifecycle stamp that
cannot re-fire on a contact already sitting at SQL. Book a vendor meeting on an existing SQL and the
record ends up carrying the vendor tag beside an SQL date from years earlier. That is the field
behaving correctly, not a mistag or a backfill. Measured 2026-09-07 across 122 `ziffdavis` contacts:
21 were created before 2026, but only 3 were already SQL before Ziff booked them - Charlie
Stansfield / Twinings (`604284901`, SQL 2024-01-30, Ziff booking 2026-06-30), Robin Gardner /
Chatham House (`419435201`, SQL 2025-01-24, Ziff booking 2026-06-19) and Milind Patel / Kingsley
Napley (`116315091032`, SQL 2025-04-23, the 2026-08-17 hand-backfill above). Reporting consequence:
count vendor-sourced meetings off `meeting_creation_date_cp__c`, never off the SQL or create date,
and treat these three as re-engagements of existing pipeline rather than net-new SQLs when checking
a vendor invoice or cost-per-SQL.

**`hs_meeting_source` on the Meeting tells you whether Chili Piper ran at all - check it before you
backfill.** The two failure modes above are both *vendor mis-tagging*, and both leave
`meeting_type_cp__c` populated, because a Chili Piper booking happened. A meeting whose
`hs_meeting_source = BIDIRECTIONAL_SYNC` and which stands **alone** on its Contact never went through
Chili Piper at all: it arrived from the AE's own calendar via the two-way sync, so **every** `_cp`
field is empty, `meeting_type_cp__c` included. That empty diagnostic is the tell - the plain
`sales_intro_inbound_agency__` means "booked off-link", but *nothing at all* means "not booked
through a link". Two qualifiers before you act on it. The `_cp` fields are **Contact** fields, not
Meeting fields, so read them off the associated Contact, never off the Meeting record. And check the
Contact's other meetings first: a `BIDIRECTIONAL_SYNC` meeting sitting *beside* an `INTEGRATION` /
Chili Piper meeting at the same start time is the calendar-sync copy of a booking that did run (see
"Every Chili Piper booking can land as two meeting records" below), and the Contact's `_cp` fields
are populated. Empty `_cp` fields alone do not establish how a meeting was booked. Such a meeting is often
created **before** its Contact, which is an artifact of sync ordering (HubSpot lands the calendar
event, then creates/matches the Contact when it resolves the guest email), not a cause of missing
tags. Do not read the timing as the explanation.

**Missing tags are not by themselves evidence that a meeting is a vendor's - and backfilling on the
assumption is the mirror of the mis-tagging bug.** The affiliate pull ORs the CP and UTM fields, so
hand-writing `meeting_source_cp` pushes the record straight into the vendor's SQL count,
cost-per-SQL, and ROI. Writing a vendor tag onto a meeting that vendor never set inflates their
numbers exactly as silently as an off-link booking deflates them, and it manufactures the invoice
justification along with it. **The vendor's own claim is the precondition for the backfill, not the
consequence of it**, so require both: the LHO email (ZiffDavis sends one per booked meeting, from
`charles.green@swzd.com`) and a matching row on the vendor's tracker. Neither present, no backfill -
hold the row at `REVIEW` and go ask the vendor and the AE who set the meeting. Verified 2026-09-08 on
contact `246947649348` (W Silver, Broughton Group, UK, intro call 2026-09-10, AE Alan Kirschberg):
reported as an untagged Ziff affiliate meeting, but `hs_meeting_source = BIDIRECTIONAL_SYNC`, no
`_cp` field set at all, no LHO email for Broughton in the mailbox, and no Broughton row on the SWZD
tracker (current to 9-Sep, one planned meeting, Nodor International). Ziff had also told us on
2026-09-02 that no EU slot was bookable past 7-Sep, so their links could not have produced a 10-Sep
UK meeting created on 4-Sep. No tags were written.

**The same signature also fits a real vendor meeting, handed off by email - and the proof sits on the
Contact record, so read it before calling the meeting "not the vendor's".** Verified 2026-09-20 on
contact `248887694939` (Belinda Bullen, Exhibition Place, Canada, meeting `117017550513`, AE Spencer
Herbst): `hs_meeting_source = BIDIRECTIONAL_SYNC`, no sibling Chili Piper meeting, every `_cp` field
empty, no Chili Piper booking under either company email in any status. It was Ziff's meeting anyway.
Charles Green (`charles.green@swzd.com`) had reached the prospect, rescheduled her, and on 2026-09-16
looped the AE in by email; the AE then sent his own calendar invite (Charles on the guest list), which
is exactly what produces this signature. Three places show it, all on the Contact: the logged **email
engagements** (a thread with `charles.green@swzd.com` in it, the AE's own invite as organizer), the
**Gong participants** on the call (`charles.green@swzd.com` beside the AE and the prospect), and a
`[PREOPP NOT CREATED] ... Meeting Type not in trigger conditions` note, because a calendar-synced
meeting does not fire the Pre-Op workflow. Two consequences for the claim rule above. The "matching
tracker row" half lags: on 2026-09-20 the SWZD tracker's held-meetings table had no rows for the
15-Sep (Obsidian), 16-Sep (Starr) or 18-Sep meetings, so a missing row inside the last two weeks is
not evidence either way. The LHO plus the handoff thread on the record, confirmed by the program
owner (Nir, 2026-09-20: "it's Ziff's, they connected him to her"), is the claim; the three `*_cp`
fields were backfilled on that. And **held is a separate question from Ziff's**: this one was a
no-show. The Gong record is 1 minute of the AE alone ("They're not in here"), and the AE's logged
emails at 10:42 and 10:59 EDT say the prospect was invited but not on the bridge and offer a
reschedule. No-shows are not billable, so a vendor meeting with this shape goes on the invoice check
as "booked, not held", not into the held count.

**The EU Chili Piper availability gap is the upstream cause worth fixing.** ZiffDavis raised EU
booking capacity twice (2026-08-26, on Jared's and Shayan's links as a workaround; 2026-09-02, no EU
slot past 7-Sep against an expected 15-day window) while the Americas links were fine. A vendor that
cannot reach our booking links books around them - by email, straight onto an AE's calendar - and
every one of those meetings arrives with no attribution and no way to tell it from an ordinary
inbound call. Per-record backfill does not touch this; EU calendar availability does.

**Every Chili Piper booking can land as two meeting records.** This is the other face of the `BIDIRECTIONAL_SYNC` tell above: a sync-sourced meeting standing *alone* on a contact means Chili Piper never ran, but a sync-sourced meeting *beside* an `INTEGRATION` / Chili Piper record at the same start time is a duplicate of a booking that did. Chili Piper writes its own meeting
engagement (`hs_object_source_label = INTEGRATION`, `hs_object_source_detail_1 = Chili Piper`,
`hs_activity_type` set to the link's meeting type, outcome `SCHEDULED`). When the rep's Google
Calendar is synced with meeting logging on, HubSpot also logs the calendar invite Chili Piper
created: `hs_meeting_source = BIDIRECTIONAL_SYNC`, `hs_object_source_label = INTERNAL_PROCESSING`,
no activity type, no outcome, `hs_created_by_user_id` = the rep, created a minute or two before or
after the Chili Piper record. Same title, start time, Meet link and reschedule URL. Verified
2026-09-11 on Steven Franklin / Jonathan Lee Recruitment (`247384285057`: `116577094684` Chili Piper
+ `116599747717` sync copy), Alexandre Bernicot (`247453265333`) and Fred Reibin (`244520468848`),
across two reps, so treat it as the default shape of a Chili Piper booking rather than an anomaly.
The contact-level affiliate pull is unaffected (one contact, one tag), but any count of meeting
*objects* (meetings per rep, no-show rate, a "meetings held" cross-check against a vendor invoice)
double-counts unless it filters `hs_object_source_detail_1 = Chili Piper` or dedupes on contact +
start time. Per record, delete the sync copy in the HubSpot UI (the MCP cannot delete engagements).
At the source, it is the calendar-sync meeting-logging setting on the reps who book through Chili
Piper.

**A `NO_SHOW` on a meeting whose start time is in the future is a mis-click, not a sync artefact.**
When an AE moves a call by issuing a new invite, the outcome for the missed slot belongs on the old
record. On 2026-09-11 the reissued Broughton Group call (`116661910655`, 15 Sep) carried `NO_SHOW`
while the original 10 Sep record (`116453043330`) had no outcome; `hs_updated_by_user_id` on the
new record was the AE's own user, twelve minutes after he created it. Reset the future record to
`SCHEDULED` and leave the missed slot's outcome to the AE. `hs_updated_by_user_id` answers "sync or
person" in one read.

**Vendor-booked contacts can keep routing to a departed owner.** Ziff bookings through Chili Piper
set `hubspot_owner_id` on the new contact to Dor Druker (`85255513`, left 2026-08-04): 12 of the
Ziff contacts created between 2026-08-11 and 2026-09-09 are his, while the meeting itself is owned
by the AE Chili Piper assigned. `search_owners` still reports him `isActive: true`, so nothing
flags it. Where the assignment lives (the Chili Piper affiliate link's owner rule, or a HubSpot
workflow) was not yet traced. Repointing needs a decision on the successor (the AE on the meeting,
or Savion as Growth Channels cover). Steven Franklin (`247384285057`) was moved to Jared Wight on
2026-09-11 at Nir's flag; the other 11 are untouched.

## HubSpot to Snowflake to Omni: what survives the trip

Only a small fraction of HubSpot's contact properties are queryable in Omni, and the attrition is
silent at every hop. Measured 2026-08-13.

| Stage | Object | Contact fields |
|---|---|---|
| HubSpot (source of truth) | portal `9154210` | 1,236 active (+5 archived) |
| Hevo raw landing | `HEVO.HEVO.HUBSPOT_CONTACTS` | 1,203 |
| dbt staging | `ANALYTICS.STG.STG_HUBSPOT__CONTACTS` | 126 |
| dbt transform | `ANALYTICS.TRF.HUBSPOT__CONTACTS` | 106 |
| Omni topic | `Hubspot Contacts` (view `omni_dbt_trf__hubspot__contacts`) | 106 |

`ANALYTICS.TRF.HUBSPOT__CONTACTS_WITH_USER` carries 128 (the TRF set plus product-user joins).

**Landing in Hevo is not the same as being queryable.** A property has to be added to the dbt model
to reach Omni. Roughly 1,100 properties stop at the raw layer, where only direct Snowflake SQL can
see them.

**The ~33 properties missing from the Hevo table are not selected by fill rate.** Tested both
directions: `made_a_recording` and `last_editing_recording_snapshot` are populated for zero contacts
and *are* present, while `total_recordings_count`, `used_producer_mode`, `used_screenshare`,
`used_mobile`, `total_magic_clips_count`, `podcast_subscribers`, and `guest_joined_studio` are
absent. The selection rule is unknown, and schema drift in the Hevo pipeline is the likeliest
explanation. Confirm with the pipeline owner before assuming a given property will appear, rather
than inferring a rule from a sample.

### Who received which marketing email

The HubSpot MCP has no per-contact email history. Read it from Snowflake:

- `ANALYTICS.STG.STG_HUBSPOT__EMAIL_EVENTS`: one row per event (`SENT`, `DELIVERED`, `OPEN`, ...), with `RECIPIENT`, `CREATED_AT`, `EMAIL_CAMPAIGN_ID` and `SUBJECT` (subject is filled on `SENT` rows). It was current to the day on 2026-09-28, although `information_schema.LAST_ALTERED` for the view shows 2025.
- `ANALYTICS.STG.STG_SEGMENT__HUBSPOT_EMAIL_CAMPAIGNS`: `ID` (text) to the email's internal `NAME` (for example `Onboarding DF-5A Trial push`). Join on `EMAIL_CAMPAIGN_ID::string = ID`.

A workflow's send action stores the email's `content_id`, not this campaign id, so to find the workflow that sends an email see `.claude/skills/hubspot-workflow-qa/knowledge/reading-workflows-via-api.md`. For "did this contact have an open deal at send time", join `STG_HUBSPOT__DEAL_CONTACT` to `STG_HUBSPOT__DEALS` (`CREATED_AT`, `IS_CLOSED`, `ENTERED_CLOSED_AT`, `DEALS_PIPELINE_ID`); pipeline names are in `STG_HUBSPOT__DEAL_PIPELINES`. Customer.io workspace `120243` sends only transactional product email (file uploaded, producer invite), so lifecycle marketing email is HubSpot, not Customer.io.

### Consequence for the self-serve scoring model

Every scoring property reaches Hevo raw (`self_serve_identity_score`, `ss_behavior_score`,
`self_serve_composite_score`, `self_serve_lead_tier`, `quality_signup`, plus
`composite_score_at_24h`, `lead_tier_at_24h`, `selfserve_score_explanation`,
`suspicious_seat_abuse_score`). `signup_composite_score` does not.

**None of them reach STG or TRF, so none are queryable in Omni.** Three consequences worth knowing
before someone promises a dashboard:

- The self-serve scoring model cannot be reported on in Omni at all.
- `quality_signup`, the flag sent to Meta CAPI / Google Enhanced Conversions / TikTok Events API,
  cannot be joined to conversion outcomes in the warehouse. Its effectiveness cannot be measured
  where every other channel metric lives.
- The product-behaviour properties that feed the score are absent too, so the model's inputs cannot
  be audited from Omni either.

To analyse the model today, query `HEVO.HEVO.HUBSPOT_CONTACTS` directly with `sql_exec_tool`. To put
any of it on a dashboard, the fields have to be promoted into the dbt staging and transform models
first. Model detail: `systems/owned/self-serve-lead-scoring.md`. Omni-side behaviour:
`systems/owned/omni-bi.md`.

## Building audience lists (verified 2026-09-23)

Learned building the "R4B Target Audience" list for Abel (list `24578`: lost SQLs and deals, PLG users who fit Business, churned Business customers) and QA-ing it twice against live data. The saved list description holds the full definition; helper exclusion lists are `24577` (contacts at Enterprise Customer companies) and `24587` (Allstate; open Pre-Op or New Sales deals created in the last 180 days; contacts at Churned Customer companies with an open deal, i.e. a live win-back; open Renewals, Upsell or Account Expansion deals). Excluding churned companies with an open deal removed 8,737 contacts, about 27% of the churned group (51 companies).

**Fields that look right and are not:**

| Field | What is wrong | Use instead |
|---|---|---|
| Contact `intro_meeting_status_from_deal` | Stale since about Sep 2025. Workflow `1696053865` copies the deal's status to the contact once (re-enrollment off), so the contact keeps its first value, usually `Scheduled`. On Pre-Ops completed in the last 30 days, only 1.8% of contacts read `Completed`. It is also contact-level, so it can match a different deal than the one you filter on. | The deal's own `intro_meeting_status`, inside the same deal-association block as the stage filter. Do not also require `intro_meeting_completed_date`; it is patchy on older records. |
| Contact `onboarding_questions_acquisition_sources` | A persona field (see `self-reported-attribution.md`), and frozen for new signups since Nov 2024: about 140 new values a month against about 19K a month in Aug 2024. The sister field `onboarding__what_best_describes_you_` froze at the same time. | For signups since Nov 2024, `onboarding_questions_intent` (use case). It is free text in two formats, bare (`webinar`) and JSON (`["webinar"]`), so filter with `contains any of`, not `is equal to any of`. |
| Contact `plg_plan_family` | **Fixed 2026-09-28** (workflow A2, see "PLG lifecycle workflow chain"): free-plan contacts on `paid_assisted` went from 1,443 to 1, and paying Grow, Business, Mobile and Live contacts on `free` from about 15,750 to 39 while the backfill finished. Still wrong: 904 Reactivated contacts read `cancelled`, because the Churned rule fires on any churn date. Before the fix it was wrong in both directions. It labels paying subscribers `free`: of about 8,050 Active/Reactivated Grow contacts (8,682 by 2026-09-28), none are `paid_self_serve`, and 95% have `currently_has_mrr = true` at a median $39/month; on 2026-09-28 it also read `free` on 1,820 Active Business contacts and 4,882 Active Mobile or Live contacts with MRR. And `paid_assisted`, meant as a sales-managed Business motion, also lands on free-plan contacts once they have a deal or Pre-Op: on 2026-09-28, 1,443 of the 5,384 `paid_assisted` contacts sat on `customer_plan = free plan`, and every one of the 1,443 had at least one deal (none had zero). **Writer and cause (read in the workflow canvas 2026-09-28):** the only writer is the HubSpot workflow "[MKT] PLG Lifecycle A - Normalize Inputs" (flow `1801078318`, re-enrollment on, trigger Customer Plan or Customer Status known; not Snowflake or Hightouch, and `plg_state_source` reads `workflow`). First matching branch wins: Churned, then **Sales Managed Open** (Lead Type = B2B AND associated deals > 0, no plan or status check) -> `paid_assisted`, then Paid Self Serve, whose plan list omits Grow, Business, Mobile and Live, so a Grow payer falls through to Signed Up -> `free`. No branch writes `expanded_paid` or `unknown` (0 contacts hold `expanded_paid`). Workflow C "Derive PLG Motion State" (`1801223477`) reads the field, and the motion state it feeds sets Lifecycle Stage: see "PLG lifecycle workflow chain" below before changing any of this. | Usable since 2026-09-28 for current payers and free accounts. For anything that decides a send, still resolve from `customer_plan` plus `currently_has_mrr` / `customer_status` (the inputs A2 reads), as the Plan state rule in `inbound-demo-reply` Step 1 does, and treat `cancelled` on a Reactivated contact as unreliable. |
| Contact `email_type` (custom, "Corporate / Work email") | Labels a share of freemail and ISP addresses Corporate (googlemail.com, mac.com, comcast.net, yopmail.com, hotmail.*). | Pair it with an email `doesn't contain any of` filter on `@`-prefixed freemail domains (the `@` stops `me.com` matching `acme.com`). |
| Company `type` | Correct and live: `Enterprise Customer` (about 2,300 companies) matches a live Business account on about 99% of records, and `Churned Customer` agrees with `churn_date` on 98%. It flips on or after the churn date, and it lags win-backs (Allstate, won back 2026-09-08, was still `Churned Customer` on 2026-09-23). | Keep using it. Do not substitute company `customer_type` (stale `Active` on long-churned accounts) or `contract_end_date` (not cleared on mid-term cancellation); both over-exclude. |

**List-builder UI traps:**

- An association block set to "where **all of** the associated companies match" plus `is none of` makes the preview fail ("There was a problem fetching the preview"). To exclude by a company property, build a helper active list and exclude its members.
- The "Exclude contacts" section accepts only segments, individual contacts and email domains. Any property-based exclusion needs a helper list.
- Save requires **Department** and **List Validity**, custom required fields on the Create segment form.
- Saving a filter edit can replace the list description with an AI-generated one. Re-check the description after every filter save.
- The estimated size in the editor is unreliable: it read 125K for a list that processed to 95.8K. Trust only the processed size.
- Several conditions inside one deal-association block apply to the same deal. That is how to express "a Closed Lost Pre-Op whose own intro was Completed".
- "Is equal to any of" trims whitespace on text values; the API's `IN` does not, so an API reconciliation of a list can land a few contacts short.

**Reach:** in list `24578` only about 41% of members are marketing contacts who have not unsubscribed. Churned-company contacts are 92% non-marketing. Size a list for email or ads on marketing contacts, not on list size.

## PLG lifecycle workflow chain (read 2026-09-28)

Six live contact workflows turn plan data into `plg_plan_family`, PLG Motion State and Lifecycle Stage. They feed each other, so a change to one moves the others. All were read in the workflow canvas on 2026-09-28; all have re-enrollment on.

**A "[MKT] PLG Lifecycle A - Normalize Inputs" (`1801078318`).** Trigger: Customer Plan known OR Customer Status known. First matching branch wins, and every path writes, in this order, PLG Motion State, PLG Is Paid Customer, PLG Trial Status, then Lifecycle Management Source = workflow. Until 2026-09-28 each path also wrote `plg_plan_family` (the last column below shows what it wrote); those seven actions were removed when A2 took the field over.

| Branch | Condition | Motion state | Is Paid Customer | Plan family (until 2026-09-28) |
|---|---|---|---|---|
| Churned | Customer Status = Churned, OR Churn Date known | Churned | false | cancelled |
| Sales Managed Open | Lead Type = B2B AND associated deals > 0 | Sales Managed Open | false | paid_assisted |
| Paid Self Serve | Customer Plan in the self-serve list (no Grow, Business, Mobile or Live) AND Status Active/Reactivated | Paid Self Serve | true | paid_self_serve |
| Free Active | Customer Plan = Free Plan AND Status = Active | Free Active | false | free |
| Signed Up | License Activated = Yes | Signed Up | false | free |
| Business Trial / Trial Ended Unconverted | Business Trial Started = Yes, end date after / before today | Business Trial / Trial Ended Unconverted | false | trial |

**A2 "[MKT] PLG Lifecycle A2 - Plan Family" (`1892315393`), live since 2026-09-28, is the only writer of `plg_plan_family`.** Trigger: Customer Plan, Customer Status or Currently Has MRR known, re-enrollment on. First match wins: Customer Status = Churned or Churn Date known -> cancelled; Customer Plan = Business AND Status Active/Reactivated -> paid_assisted; A's self-serve list plus Grow AND Status Active/Reactivated, or Mobile/Live AND Currently Has MRR = true AND Status Active/Reactivated -> paid_self_serve; Free Plan AND Status Active, or License Activated = Yes -> free; Business Trial Started = Yes with the end date after or before today -> trial; otherwise no write. On turn-on it backfilled the 24,252 contacts then holding `paid_assisted`, or `free` on Grow, Business, Mobile or Live with Active/Reactivated status. It writes plan family only, so it moves no motion state and no lifecycle stage: Sales Managed Open, SQL and Customer counts were flat across the change (4,374 / 29,120 / 224,943 before, 4,374 / 29,123 / 224,948 after).

**C "[MKT] PLG Lifecycle C - Derive PLG Motion State" (`1801223477`).** Trigger: Product Plan Raw, PLG Is Paid Customer or PLG Trial Status known. It re-derives motion state, first match wins. Since 2026-09-28 (revision "1 action added, 1 action edited") its first branch is PLG Motion State = Sales Managed Open -> end with no write, so only A decides that state, and its old plan-family branch now matches `expanded_paid`, which no contact holds (it read `plg_plan_family = paid_assisted` -> Sales Managed Open before). Then: Is Paid Customer = True AND plan family `paid_self_serve` AND Self-Serve Combined Score >= 70 -> Customer Expansion; Is Paid Customer = Yes -> Paid Self Serve; Trial Status `active` -> Business Trial; `ended_unconverted` -> Trial Ended Unconverted; Self-Serve Behavior Score > 0 -> Free Active; Lifecycle Stage = Other -> Churned; otherwise Signed Up. C shows re-enrollment on, but which properties re-enroll it was not read. **Unconfirmed:** if A's Is Paid Customer write re-enrolls C, C can run before the contact's plan family is final. That would explain Rohit Goswami (`251038005161`, `paid_assisted` with motion state Signed Up) and the 1,012 `paid_assisted` contacts outside Sales Managed Open on 2026-09-28, but no property history or workflow log was read to prove the order. Backups of A and C taken before the change: "[BACKUP 2026-09-28, keep OFF] PLG Lifecycle A - Normalize Inputs" (`1892314405`) and "... C - Derive PLG Motion State" (`1892316600`), both off.

**State Router "[MKT] PLG Lifecycle - State Router" (`1800995446`)** sets Lifecycle Stage from motion state on every change: Signed Up and Free Active -> Subscriber; Business Trial and Trial Ended Unconverted -> Lead; Paid Self Serve and Customer Expansion -> Customer; Churned -> Churned; **Sales Managed Open -> Sales Qualified Lead**; Unknown -> no change. The State Change Handler (`1800994901`) stamps previous motion state and the change time, D stamps timestamps, and H "Mismatch Flagger" (`1801148341`) clears and rewrites Lifecycle Mismatch Reason (`paid_not_customer`, `trial_not_promoted`, `owned_not_sql`, `opportunity_without_deal`, `customer_with_free_plan`, `churned_not_churned`). H writes that property only: no tasks, emails or notifications. All three fire on motion-state changes, not on plan-family changes.

**Lists that read `plg_plan_family`:** R4B Target Audience `24578` (groups 3, 4 and 7 take `Cancelled` or `Paid self-serve` with a business persona) and Signal 5 `21739` (plan family `Trial`, PLG Previous Plan Family `trial`, or a trial motion state). Both showed "Used in (0)" on 2026-09-28, so a change in membership sends nothing from HubSpot.

**What any change to plan family or motion state has to respect (the 2026-09-28 fix followed steps 1 to 3).** Any change to motion state goes straight into Lifecycle Stage through the State Router, and Sales Managed Open becomes SQL, so a fix that narrows A's Sales Managed Open branch moves B2B contacts with a Pre-Op out of SQL. The version that moves no motion state and no lifecycle stage:
1. Compute `plg_plan_family` from plan data alone, in its own place (now A2): Churned -> cancelled; `business` Active/Reactivated -> paid_assisted; the self-serve list plus Grow (Active/Reactivated) or Mobile/Live with MRR -> paid_self_serve; the free and trial rules as today. Remove actions 23 to 29 from A in the same sitting, so only one workflow writes the field.
2. Stop C reading `paid_assisted` before plan-family values change. **Done 2026-09-28** (see C above). Without it, Business customers, who become `paid_assisted`, would be moved into Sales Managed Open and SQL. C's branch 5 (Customer Expansion) still reads plan family, and the fix did not change its timing. C does not trigger on `plg_plan_family`, so a paying self-serve contact with a Self-Serve Combined Score of 70 or more can reach C before A2 writes `paid_self_serve`, take the Is Paid Customer = Yes branch instead and stay Paid Self Serve, because A2's later write does not rerun C. The same order existed when A wrote both fields. The durable fix is to add PLG Plan Family to C's triggers and re-enrollment; not done as of 2026-09-28.
3. Backfill only the contacts whose value changes (current `paid_assisted`, plus `free` on Grow, Business, Mobile or Live with Active/Reactivated), not every contact the trigger matches. Then switch the trigger to the permanent one and answer No to enrolling existing contacts.
4. Leave PLG Is Paid Customer alone: it is `false` for Grow and Mobile payers, which keeps them at Subscriber. Correcting it moves about 13,500 Grow, Mobile and Live payers to Customer, a separate decision.

## Known Issues / Failure Modes

| Issue | Symptoms | Resolution |
|-------|----------|------------|
| Product events overwrite Contact Last Touch Source | Contacts that arrived via ads/forms show an incorrect/product-side source after product activity (sign-up, activation) fires back into HubSpot. | Use Pre-Op Last Touch Source (not Contact `hs_latest_source`) for attribution reporting. Flag to Jonathan if systemic. |
| `bd_owner` and `last_touch_source__c` are not the correct HubSpot field names | MCP `get_properties` returns "propertiesNotFound" for these. | The deal-side attribution field is `last_touch_source` (verified 2026-08-10; see "QBD & No-Show Program Fields" for its flip-tracking companions). For BD owner, run `search_properties(objectType="deals", query="bd owner")` before querying. |
| Product-synced timing fields are backfill snapshots, not event dates | `plg_signed_up_at`, `plg_paid_self_serve_at` (Hightouch from Snowflake) and `hs_v2_date_entered_customer` are pinned to the sync/migration date, e.g. a single `2026-04-22` timestamp shared across thousands of contacts. Any "days between" computed from them is fabricated (a real case produced a fake ~65-day form-to-paid that was just `2026-04-22` minus the form date). `riverside_account_signup_timestamp`, `trial_started_at`, and `paid_started_at` have partial, era-limited coverage. | Do not use the HubSpot mirror for signup/trial/paid timing. Pull true dates from Snowflake `ANALYTICS.FS.USERS` (`SIGN_UP_AT`, `FIRST_MRR_DATE`), joined by email. `profitwell_activated_on` is the only HubSpot field that matches true first-paid to the day, but it covers ~25% of customers. See `omni-bi.md` for the joinable tables. |
| Cloned workflows inherit settings that are invisible on the canvas | A clone quietly does the wrong thing with nothing erroring. Three things carry over: the parent's **suppression lists** (usually the parent's own success list - self-suppression there, silent cross-suppression in the clone), the parent's **description**, and the parent's **success/failure lists**. The 2026-09-07 clone above carried a 14,645-contact suppression list growing ~1,200/week that would have blocked a large and rising share of enrollments. | Treat `suppressionListIds` as expected-empty on any clone and justify each entry that stays; resolve every `listId` to its name; read the description against the actual trigger. Checklist: `.claude/skills/hubspot-workflow-qa/SKILL.md` -> "Cloned workflows". |
| Inconsistent asset naming across lists, workflows, and marketing emails | A April 2026 audit of 2,136+ lists, ~100 workflows, and ~90 marketing emails found systemic naming issues: missing category prefixes, person names embedded in asset names, inconsistent "don't touch" warnings, uncleaned clones, and mixed date formats - makes assets hard to find and workflows risky to hand off between team members | Follow the naming standard and use the QA checklist in `hubspot-workflow-qa` skill before building or modifying a workflow; full audit findings in `.claude/skills/hubspot-workflow-qa/knowledge/naming-conventions.md` |
| Vendor-booked meetings arrive with no Chili Piper source data | An appointment-setting vendor (ZiffDavis, MemoryBlue, Pursuit, Boscia) invoices for a meeting that is missing from their SQL count / cost-per-SQL / ROI in the Affiliate Channel Funnel dashboard. `meeting_source_cp`, `meeting_medium_cp`, `meeting_campaign_cp` and the UTM fields are all empty; `meeting_type_cp__c` is the plain `sales_intro_inbound_agency__` instead of the vendor's `_10d_` link. First confirmed 2026-08-17 (contact `116315091032`). | Verify the claim on the vendor's own tracker, then backfill the three `*_cp` source fields on the Contact - **not** `contact_source` or the Pre-Op `last_touch_source`, which define the MQL. Full signature, diagnostic, and rationale: "Chili Piper (`*_cp`) Meeting Fields & Vendor Attribution" above. Per-record fix only; the cause is the vendor booking off their tagged link, which needs raising with the SWZD program owner. **Second cause (2026-09-23):** the UTM fields are set, only the `*_cp` fields are empty, and `meeting_type_cp__c` is `sales_intro_bd_outbound_enterprise_new`. That is a correct Ziff EU booking whose meeting type's guest form dropped the tags, not an off-link booking. Fix and diagnosis: `systems/owned/chilipiper.md` Known Issues. |
| Vendor-booked meetings tagged to the *wrong* vendor | A vendor with no tagged link of its own books through another vendor's link, so the meetings are fully tagged and nothing looks missing - the credit just lands on the wrong vendor. Boscia/L&D Collective booked all 7 delivered meetings through memoryBlue's link (verified + fixed 2026-08-19, 11 contacts); several used the SDR's own @bosciagroup.com email, hiding the client. | Recover the client from the meeting's contact associations and the booking payload in `hs_meeting_body`, re-tag `meeting_source_cp` (and a wrongly captured `utm_source`) on the client contacts, clear tags on vendor-staff contact records. Full case: "Chili Piper (`*_cp`) Meeting Fields & Vendor Attribution" above. Prevention: every vendor gets its own tagged link, books with the client's email. |
| An untagged meeting reported as a vendor's, that is not | All three `*_cp` source fields are empty on the Contact *and so is* `meeting_type_cp__c`, with `hs_meeting_source = BIDIRECTIONAL_SYNC` and **no sibling** `INTEGRATION` / Chili Piper meeting at the same start time - the meeting came off the AE's calendar via the two-way sync, so Chili Piper never ran and there is nothing to have carried a tag. (A sync meeting *beside* a Chili Piper one is the double-logging row below, not this.) Often created before its own Contact, which is sync ordering, not the cause. Looks identical to a vendor booking off-link, but the vendor may simply not have set it. First confirmed 2026-09-08 (contact `246947649348`, Broughton Group). | Do **not** backfill on the report alone - a hand-written `meeting_source_cp` enters the affiliate pull and inflates that vendor's SQL count, cost-per-SQL, and ROI, and manufactures the invoice justification with it. Require the vendor's own claim first: the LHO email plus a matching row on their tracker. Neither present, hold at `REVIEW` and ask the vendor and the AE who set the meeting. **Before asking, read what is already on the Contact:** its logged email engagements and the Gong participant list. A vendor handoff by email (`charles.green@swzd.com` looping the AE in, the AE sending his own invite with Charles as a guest) produces this exact signature and *is* the vendor's meeting (Exhibition Place, contact `248887694939`, 2026-09-16; tags backfilled 2026-09-20 on the program owner's confirmation). A missing tracker row inside the last two weeks is not evidence either way; the tracker lags. Full case: "Chili Piper (`*_cp`) Meeting Fields & Vendor Attribution" above. |
| Company-level campaign segmentation drags in 26,931 seeded test contacts | A contact audience built from a company property instead of the campaign's own contact list returns ~35k where the real audience is ~6.5k, and ~26k of the emails are `@riverside.fm`. Company `RiversideFM, Inc.` (id `5918661955`, domain `riverside.fm`) has 26,955 associated contacts, of which 26,931 are seeded test records (`1526elza15@riverside.fm`, `8008clemmie_gleichner@riverside.fm`), and it is tagged `General` in `seat_campaign_list_membership`. So is `dquirogat.com` (6 contacts). Hit 2026-09-09 while building the Q3-2026 seat campaign "last chance" segment. | Build contact audiences from the campaign's contact list, never from a company property rollup. For the Q3-2026 seat campaign: list `24152` (`[contacts] Seat campaign - all contacts`) and its claim-filtered child `24205` (`[contacts] Seat campaign - Company didn't claim`). Fix the cause as well: set `seat_campaign_list_membership` on `RiversideFM, Inc.` to `excluded account` so the internal record cannot enter a future audience. |
| Self-serve onboarding series emails prospects who have an open deal | A prospect in an open Pre-Opp or sales deal gets the free-signup onboarding emails, including "Try Riverside Pro free for 14 days" (DF-5A / DF-5B), and sales hears about it on the call. About 375 open-deal contacts got a trial push between 2026-08-01 and 2026-09-28 (Snowflake send log, as of 2026-09-28). Cause: the [Onboarding Orchestrator](https://app.hubspot.com/workflows/9154210/platform/flow/1815158647/edit) and the two series it feeds, [Self Serve Freemium](https://app.hubspot.com/workflows/9154210/platform/flow/1815081324/edit) (DF-*) and [Self Serve Trials](https://app.hubspot.com/workflows/9154210/platform/flow/1817182827/edit) (DT-*), kept sales prospects out only through `Lead Type is B2B` (list `20878`: `lead_type` = B2B, `isenterprise`, or a paying Business company). A self-serve signup keeps `lead_type` = Self Service after a deal opens, so that check never matched them. | Fixed 2026-09-28 (Hanan, per Nir): list `24696` `[OPS] Open deal - onboarding suppression` suppresses all three workflows. It holds contacts with an open deal in a new-sales pipeline (US/EU Agency, US/EU Enterprise New Sales, default Sales Pipeline), or in a Pre-Opp pipeline created in the last 60 days, so stale Pre-Opps do not block onboarding forever. Renewals, Upsell and Expansion are left out: they are existing customers. When the deal closes, the contact leaves the list and gets marketing email again, but is not re-enrolled in onboarding. Second gap, fixed 2026-10-06 (Hanan, per Nir): a G2 demo request who also creates a Riverside account gets the same series, because the signup, not the G2 form, enrolls them (first case: a contact who submitted the [G2 Leads form](https://app.hubspot.com/submissions/9154210/form/e7bc736c-697a-4ad2-8b2e-21cb8803c4a2/submissions) and signed up five minutes later, then got DF-3). Nir qualifies G2 leads himself before any booking link or trial invite. List `24889` `[OPS] G2 Leads form - onboarding suppression` (submitted that form in the last 60 days) now suppresses the same three workflows. **Any new lifecycle or trial-offer workflow aimed at self-serve users needs `24696` and `24889` as suppression lists.** A `lead_type` check alone does not keep sales prospects out. |
| Self-serve product signups leaking into MQL + BD outreach | PLG signups (source `Riverside.fm Backend App`, zero form submissions) are promoted to `marketingqualifiedlead` + `hs_lead_status = "BD: New/Not Contacted"` minutes after signup, contradicting the PLG-only self-serve model. Systemic (verified 2026-07-14). | Exclude product signups from the MQL/BD-promotion workflow. Full root-cause, scale, cohort query, and guard spec: `systems/owned/self-serve-lead-scoring.md` → "Known failure: self-serve signups leaking into MQL / BD outreach". Owner: Jonathan. |
| Chili Piper booking logged twice (Chili Piper record + calendar-sync copy) | Two meetings on the contact with the same start time and Meet link: one `INTEGRATION` / Chili Piper with an activity type and outcome, one `BIDIRECTIONAL_SYNC` / `INTERNAL_PROCESSING` with neither. Seen across reps (verified 2026-09-11, 3 contacts). Inflates any meeting-object count; contact-level attribution unaffected. | Delete the sync copy in the UI (the MCP cannot delete engagements); for counts, filter on `hs_object_source_detail_1 = Chili Piper` or dedupe on contact + start time. Source fix is the calendar-sync meeting-logging setting for Chili Piper reps. Detail: "Chili Piper (`*_cp`) Meeting Fields & Vendor Attribution" above. |
| New Ziff contacts owned by Dor Druker after his departure | Contact owner `85255513` on Chili Piper-created Ziff contacts from 2026-08-11 onward (12 by 2026-09-09) while the meeting owner is the AE. `search_owners` still reports him active. | Trace the assignment (Chili Piper link owner rule vs HubSpot workflow) and repoint to the agreed successor; reassign per record meanwhile. Steven Franklin (`247384285057`) moved to Jared Wight 2026-09-11. |
| One affiliate rep's meetings fan out across every Pre-Op he touches | A meeting shows on Pre-Ops belonging to unrelated companies, and anything reading a deal's evidence through its associations (Clay close-lost narratives, most visibly) blends companies - Clay wrote Nettwerk's story onto the Metro Wallcoverings record. Cause, from the one booking read in full (Le Ski, 2026-09-16): the Ziff Davis rep `charles.green@swzd.com` is in that booking's attendees from the moment it is booked, so HubSpot's calendar sync matches the existing contact onto the meeting and then associates the meeting with every deal the contact is on. Counts measured separately, 2026-09-16: he carries 58 Pre-Ops and 17 meetings, that one meeting reached 6 unrelated Pre-Ops, and 3 new bad associations appeared in a day. **The one-booking observation and the 17-meeting count are separate evidence.** Whether the other 16 carried him from booking rather than a later edit was not checked, so do not assume this diagnosis for every affiliate booking without reading the booking. Note Chili Piper syncs only the *primary* guest, so this association is HubSpot's, not Chili Piper's. | He is not configured on the `_10d_` meeting type or on `eu_agency_51-200__website_` (both read 2026-09-16; other links and the EU router were not checked), so on that reading cleanup alone recurs - stop him being added to the invite (partner-side) or stop HubSpot treating a calendar attendee as a deal contact, then unpick the deal associations. Detection sweep for other vendors: a contact with a high `num_associated_deals` spanning unrelated companies. Full case and the Chili Piper-side evidence: `systems/owned/chilipiper.md` -> Known Issues. Open as of 2026-09-16. |
| Company `numberofemployees` is 0 while Clay has the real count | `numberofemployees` = 0 (often with `annualrevenue` = 0) on records that are enriched (`hs_is_enriched` = true) and carry a real `clay_number_of_employees`, `company_size` and `hs_employee_range`. Every headcount rule then reads the company as unknown size. 19,490 companies matched on 2026-10-01 (Netwrix, Shopify, Swiss Re, Wayfair among them), 17,189 of them last modified before 2026-09-30, so this is long-standing, not a single bad sync. Nothing copies the Clay count into `numberofemployees`. What writes the 0 is unconfirmed: the paired revenue 0 and the ZoomInfo rolling enrichment job on these records point at ZoomInfo, but the MCP does not expose property history. | Read the field history in the UI to confirm the writer. Proposed fix (not built as of 2026-10-01): a company workflow that sets `numberofemployees` from `clay_number_of_employees` when the first is 0 or empty and the second is above 0. Until then, `/inbound-demo-reply` falls back to `clay_number_of_employees` itself. Netwrix (`16089133071`) was set to 757 by hand on 2026-10-01. |
| Company `numberofemployees` far above Clay's count | The opposite of the 0 problem: a small business carries a mid-size or enterprise headcount, so it routes to the wrong market and Pre-Op pipeline. 6,487 companies had `numberofemployees` >= 100 while `clay_number_of_employees` was 1-10 (HubSpot search, 2026-10-05; a threshold count, not a field-to-field comparison). Many were created the same day with round values (Delta Plumbers 100 vs Clay 1, Florida Automobile Dealers Association 150 vs 3), and Mitch Carson's company (`58945074098`) had 175 vs 2 and read Mid Market. What writes these values was not read. A separate shape: Praxis Passvogel (`57912517757`, a one-person therapy practice) had both counts wrong and in agreement (3,657 and Clay 3,675) because its `website` held a LinkedIn company URL rather than its domain, which put its Pre-Op in EU Enterprise. | Praxis fixed by hand 2026-10-05 (1 employee, `company_size` 0-1, market Agency, website set to the domain, Pre-Op moved to EU Agency, same Action Required stage); Clay's own field still says 3,675 and may write back. For the pattern: find the writer before proposing a rule. Detection: `numberofemployees` >= 100 and `clay_number_of_employees` between 1 and 10, or a `website` containing `linkedin.com/company`. |

## query_crm_data Quirks

### `query_crm_data` can be permission-blocked while `search_crm_objects` still works

Measured 2026-09-15. `query_crm_data` returned "This connector requires additional permissions. The user needs to reconnect it with the appropriate access." on a plain SELECT against CONTACT, while `search_crm_objects` against the same objects, with the same session, returned full results including association filters.

**Do not treat a `query_crm_data` permission error as HubSpot being unavailable.** Fall back to `search_crm_objects` with `filterGroups` and, for cross-object work, `associatedWith`. It handles most reporting shapes: `associatedWith` with an `IN` list of up to 100 contact ids pulls every associated deal in one call, which is how the Ziff-sourced Pre-Op set was assembled. What you lose versus `query_crm_data` is GROUP BY and aggregates, so counts have to be done client-side over the returned rows.

Verified behaviors of the HubSpot MCP `query_crm_data` tool (SQL-style queries against CRM objects), discovered 2026-07-12 while running the 24h frozen score statistical validation against portal 9154210. Each was confirmed by cross-checking against independent counts.

### 1. `= 'false'` on a write-once-when-true flag matches nobody

`score_24h_pre_paid_flag` is a sparse write-once field: it is set to `'true'` only for contacts that were pre-paid at 24h and left **NULL** otherwise - the literal value `'false'` is never stored. So `WHERE score_24h_pre_paid_flag = 'false'` returns 0 rows.

This is a data-shape gotcha, **not** a tool bug (an earlier note misdiagnosed it as a "boolean equality + datetime IS NOT NULL" engine fault). Verified 2026-07-12: `... AND score_24h_pre_paid_flag = 'true' AND plg_paid_self_serve_at IS NOT NULL` returns 138, so boolean equality composes fine with a datetime `IS NOT NULL` check; and `score_24h_pre_paid_flag = 'false'` with no other filter returns 0.

**Canonical cohort query:** require a captured snapshot and exclude the true flag, rather than including a `= 'false'` that matches nobody:

```sql
WHERE composite_score_at_24h IS NOT NULL
  AND (score_24h_pre_paid_flag IS NULL OR score_24h_pre_paid_flag != 'true')
```

Watch for the same shape on any other write-once-when-true flag.

### 2. GROUP BY coerces NULLs into named buckets and can over-count

GROUP BY results fold NULL values into named buckets and the row totals can exceed the true cohort size.

Verified case: GROUP BY `lead_tier_at_24h` returned an "Unassigned" bucket of 35,919 even though `lead_tier_at_24h = 'Unassigned'` matches 0 contacts (those contacts are NULL), and the group-by row total (79,510) exceeded the true filtered cohort total (74,516) by ~5k. Plain single-filter COUNT queries reconcile exactly (40,887 Low + 181 Mid + 33,448 NULL = 74,516).

**Recommendation:** never trust GROUP BY totals for cohort work; use plain single-filter COUNTs and reconcile them against the cohort total.

### 3. Date BETWEEN boundaries evaluate at portal-timezone midnight

`BETWEEN` date boundaries evaluate at portal-timezone midnight (a US timezone, empirically midnight ET), and in the tested case the end boundary behaved as exclusive of the named day's end.

**Recommendation:** validate cohort windows empirically - compare a known record set against the SQL count before running banded analyses.

### 4. An associated-object property in SELECT silently drops a list-membership filter

`WHERE hs_crm_search.ilsListIds = '<listId>'` works on its own and composes fine with GROUP BY. It breaks the moment the SELECT names an associated-object property: the list filter is dropped with no error and the query answers for the whole portal.

Verified 2026-09-09 against list `24205` (6,181 members):

- `SELECT email FROM CONTACT WHERE hs_crm_search.ilsListIds = '24205'` returns 6,181 - correct.
- `SELECT riverside_role, COUNT(*) FROM CONTACT WHERE hs_crm_search.ilsListIds = '24205' GROUP BY riverside_role` totals 6,181 - correct.
- `SELECT email, COMPANY.name FROM CONTACT WHERE hs_crm_search.ilsListIds = '24205'` returns 7,083,167 - every contact in the portal.

The 7M answer looks like a normal result set, so the failure is invisible unless you know the list size. It is also the exact shape that makes a company-side check look clean.

**Recommendation:** never mix a list filter with an associated-object property. Query the list contact-side only, then look up the company properties in a second query. Reconcile every list-filtered result against `hs_list_size` on the `OBJECT_LIST` record before using it.

An associated-object condition in **WHERE** is safe with the list filter (verified 2026-09-23: `WHERE hs_crm_search.ilsListIds = '24578' AND COMPANY.type = 'Enterprise Customer'` returned 0 on a list that excludes them, and the `Churned Customer` version matched the in-list count). Only the SELECT form drops the filter.

### 5. Several DEAL.* conditions in one WHERE apply to the same deal

`WHERE DEAL.dealstage IN (...) AND DEAL.intro_meeting_status = 'Completed'` counts contacts with one deal that meets both conditions, not contacts with one deal of each. Verified 2026-09-23: `DEAL.dealstage = '67154607' AND DEAL.pipeline = '9297003'` returned 0 for a contact on a promoted US Agency Pre-Op and a separate US Agency New Sales deal.

### 6. WHERE nesting is capped at 20 levels

A long `OR` chain (for example 30 `email LIKE` terms) fails with "WHERE clause is too deeply nested (exceeded 20 levels)". Split it into two queries and add the counts, or use `search_crm_objects` with `CONTAINS_TOKEN`.

### 7. `search_crm_objects` names the list filter `ilsListIds`

In `search_crm_objects` filterGroups the list-membership property is `ilsListIds` (for example `{"propertyName": "ilsListIds", "operator": "EQ", "value": "24578"}`). `hs_crm_search.ilsListIds`, the `query_crm_data` name, is rejected as an invalid property. For substring email checks against a list, `email CONTAINS_TOKEN "*googlemail.com"` works where a list-filtered `email LIKE` was rejected.

### 8. Text `IN` does not trim trailing spaces

`onboarding__what_best_describes_you_` holds values such as `'Business Owner '` with a trailing space. The list builder's "is equal to any of" matches them; `IN (...)` in `query_crm_data` and `search_crm_objects` does not. Use `LIKE` or expect a small undercount when reconciling a list.

## Click-ID Capture on Third-Party-Hosted Forms

HubSpot parses ad click identifiers (`fbclid`, `gclid`, and the equivalents) out of the **`pageUrl` recorded on the form submission** and writes them to the contact properties `hs_facebook_click_id`, `hs_google_click_id`, `hs_linkedin_click_id`, `hs_bing_click_id`, `hs_tiktok_click_id`.

This works even when the form is **not** on a Riverside domain and has no HubSpot tracking code on the page. Verified 2026-09-07 for a Typeform-hosted quiz: a submission recorded `pageUrl = https://form.typeform.com/to/buNbcQcb?fbclid=test123` and the resulting contact carried `hs_facebook_click_id: "test123"`. So appending `fbclid` to an externally hosted form's link is sufficient for capture - the ad platform does the appending, and the integration posting into HubSpot only needs to pass the source URL through.

Two consequences worth knowing before relying on it:

- **HubSpot stores the bare click id.** Meta's Conversions API expects `fbc` in the full cookie format `fb.1.<click_timestamp_ms>.<fbclid>`. The stored value has to be reformatted before it reaches Meta - see `paid-acquisition.md` -> "Meta Conversions API via Segment".
- **The property can hold junk.** Test traffic writes literal placeholder values (`"fbclid"`, `"test123"` both seen in the portal). Anything forwarding these downstream should treat a non-`fbclid`-shaped value as absent rather than passing it on.

To check whether a given form's submissions actually carry a click id, read the submissions directly rather than sampling contacts - `/api/form-integrations/v1/submissions/forms/{formGuid}` returns `pageUrl` per submission (method: `.claude/skills/hubspot-workflow-qa/knowledge/reading-workflows-via-api.md`).

## Related Systems

- **Upstream:** Paid acquisition (ad lead gen), Marketing website (form fills), Riverside product (sign-up events), Chili Piper (`*_cp` meeting stamps - `systems/owned/chilipiper.md`)
- **Downstream:** Omni BI (revenue + funnel reporting), Sales workflows

## Pointers

- **HubSpot portal:** `app.hubspot.com` (account 9154210)
- **Pre-Op data dictionary:** `preop-data-intelligence` skill
- **Self-reported attribution merge (design/build spec):** `systems/owned/self-reported-attribution.md` - one derived Contact field (`sr_attribution_channel`) merging onboarding + Gong (+ enterprise-form) "How did you hear about us?" answers into one canonical channel. Note the two corrections it documents: `onboarding_questions_acquisition_sources` is a persona field (not a channel), and `onboarding__how_did_you_hear_about_us_` stores picks as a JSON-array string (`["Word of mouth"]`).
- **Slack:** `#mops-priority-room` (`C0A9JUG9MPZ`)
- **Owner:** Jonathan Galili (infra), Hanan Amos (strategy)
- **Specialist skills:** `hubspot-agent`, `lifecycle-agent`, `marketing-ops-automation-agent`, `measurement-agent`, `hubspot-workflow-qa`
