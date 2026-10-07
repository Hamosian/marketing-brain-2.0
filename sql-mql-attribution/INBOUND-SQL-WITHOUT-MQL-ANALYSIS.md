# Inbound SQLs without MQLs: root-cause analysis and attribution framework

Prepared 2026-06-14. Source data: `Results_2026-06-08-1117.csv` (652 inbound-classified SQLs with no linked marketing MQL). Analysis artifacts in `sql-mql-attribution/`.

## Executive summary

We analyzed all 652 inbound SQLs (completed intro meetings, Last Touch Source = Inbound) that have no linked marketing MQL record. Every MQL field in the export is null for all 652 rows, confirming the join to the marketing-lead record fails for the entire population.

The single most important finding is that "inbound SQL without an MQL" is largely a definitional and data-capture problem, not a tracking-pixel problem. Riverside runs two different "MQL" concepts that are being treated as one:

1. Funnel-stage MQL: a Pre-Op whose Last Touch Source = Inbound. By this definition every one of these 652 SQLs already is an MQL.
2. Marketing-attribution MQL: a separate form-submission record carrying first-visit UTM and channel, linked to the SQL by identity (email, anonymous_id, product user_id). This record is missing for all 652.

When we classify the 37% of records that carry an AE "how did they hear about us" note, only about 5% of the population are genuine marketing inbound that should have a form-MQL and failed to join. The rest never had a form-MQL by nature: existing product users, referrals, mis-tagged outbound, events, re-engaged old deals.

The honest headline:

- Recoverable to an actual campaign or channel: roughly 31 records (4.8%), about $5.1K won MRR per month. Small.
- The real win is de-polluting the inbound number: about 109 records (16.7%) are not marketing inbound at all and currently distort the Inbound MQL count, MQL-to-SQL conversion, and any CAC or ROAS that divides spend by inbound volume.
- The durable fix is forward capture: 63% of records have no AE source note at all. That capture gap, not a channel mystery, is the largest category.

The problem is also accelerating: orphan inbound SQLs grew 118 (2023), 134 (2024), 214 (2025), 186 in the first five-and-a-half months of 2026 (about 370 annualized).

## 1. What the data shows (root-cause analysis)

### 1.1 The population is genuinely MQL-less and growing

- 652 records, all classified inbound, all with completed intro meetings.
- 100% have a null MQL across every MQL column (MQL_ID, first-visit UTM, channel group, form fields). This is a clean left-join miss, not partial data.
- 94.5% (616) carry a contact email, so they are identity-joinable. Only 36 (5.5%) have no email and are structurally unrecoverable by identity.
- Funnel outcome of the 652: 187 promoted to a deal (28.7%), of which 110 closed won, 61 closed lost, 16 still open.
- Won revenue with zero marketing attribution: $130,829 MRR per month across the 110 wins, roughly $1.57M ARR.

Yearly trend (by SQL create date):

| Year | Orphan SQLs | Promoted | Won |
|---|---|---|---|
| 2023 | 118 | 36 | 21 |
| 2024 | 134 | 43 | 28 |
| 2025 | 214 | 68 | 44 |
| 2026 (to mid-June) | 186 | 40 | 17 |

Note: 2023-05 alone holds 50 records (36 closed lost), which has the signature of a one-time historical migration batch. It should be flagged and excluded from trend baselines.

Sized against the funnel (Omni, topic "MQLs to SQLs to Deals", FY2023 to FY2026): there are 14,934 inbound SQLs and 283 outbound SQLs in the period, 15,217 total. The 652 orphans are therefore about 4.4% of all inbound SQLs, roughly 1 in 23. Approximate per-year orphan rate (calendar orphans over fiscal SQLs, so directional): 2023 ~6%, 2024 ~3%, 2025 ~3%, 2026 ~6%. The absolute count grows with the funnel while the rate stays in a 3 to 6% band with a 2026 uptick that lines up with the outbound mis-tag surge. The very low outbound SQL count (283, under 2% of the funnel) is itself a symptom: outbound is being under-tagged and absorbed into Inbound, which is exactly category C below.

### 1.2 Root-cause categories with volume and impact

The only attribution signal that survives in this export is the AE free-text field `AE_DISCOVERY_HOW_DID_THEY_HEAR_ABOUT_US`, populated on 37% (241) of records. We classified those 241 with an LLM pass plus a deterministic keyword pass; the two methods agree on 86.7% of records, which gives confidence in the distribution. The 411 blank records are reported as their own category. The LLM pass is the canonical labeling; per-record labels are in `classified_orphan_sqls.csv`.

| # | Root-cause category | Records | % | Promoted | Won | Won MRR/mo | Has email |
|---|---|---|---|---|---|---|---|
| A | Existing or self-serve product user (PLG) | 72 | 11.0% | 32 | 21 | $22,072 | 68 |
| B | Referral, word of mouth, dark social | 58 | 8.9% | 22 | 14 | $17,040 | 56 |
| C | Outbound mis-sourced as inbound | 36 | 5.5% | 3 | 1 | $1,155 | 36 |
| D | Re-engagement of past or closed-lost deal | 16 | 2.5% | 9 | 7 | $13,442 | 16 |
| E | Event or field marketing | 14 | 2.1% | 2 | 0 | $0 | 14 |
| F | Digital inbound, MQL join failed | 31 | 4.8% | 7 | 4 | $5,104 | 31 |
| G | AI or LLM sourced | 1 | 0.2% | 0 | 0 | $0 | 0 |
| H | Customer Success sourced | 1 | 0.2% | 1 | 0 | $0 | 1 |
| I | Captured but uninformative | 12 | 1.8% | 1 | 1 | $675 | 12 |
| J | No discovery captured (blank field) | 411 | 63.0% | 110 | 62 | $71,342 | 382 |
| | Total | 652 | 100% | 187 | 110 | $130,829 | 616 |

What each category means and why no MQL exists:

- A. PLG existing user. Already on Pro, self-serve, or Individual before sales engaged. No marketing form by nature. Sales engaged a product user directly. Examples: "using Pro", "churned account that switched to PRO", "already a user for podcasts".
- B. Referral and word of mouth. Personal recommendation, investor or colleague intro, partner or producer referral. Untrackable, no form. Examples: "Recommended by Alexis Ohanian", "investor introduction", "Referral from existing customer".
- C. Outbound mis-sourced. Reached via BD or AE cold outreach (cold email, cold call, LinkedIn outreach, named reps reaching out) but the Pre-Op was tagged Inbound. The source label is wrong. Examples: "Cold outreach email from Lauren", "Contract BDR sourced", "Received a cold call".
- D. Re-engagement of past deal. A prior sales relationship revived, a new Pre-Op cycle. Any MQL sits on a prior cycle or predates the MQL system. Examples: "Old deal that is reopening", "Past Deal that was marked as Closed-Lost".
- E. Event and field marketing. Met at NAB or conferences, usually a manually created Pre-Op, no digital form. NAB alone appears 8 times.
- F. Digital inbound, join failed. Genuine self-driven digital discovery (organic search, ads, site research) where an MQL should exist but the identity join failed. This is the only truly campaign-recoverable category. Examples: "Google Search for podcast recording software", "Youtube ad and LinkedIn ads when searching for podcasting tools".
- G. AI or LLM sourced. Discovery via ChatGPT, Grok. Small today, fastest-growing discovery channel industry-wide.
- H. Customer Success sourced. Existing-customer expansion driven by CS ("CSMQL").
- I. Uninformative. Discovery captured but no usable signal: "Unsure", "Unknown", generic intent with no channel.
- J. No discovery captured. The AE left the field blank. The largest category by far at 63%, and the largest single revenue contributor among orphans ($71.3K won MRR). 382 of these 411 still have an email, so they are identity-joinable.

### 1.3 Strategic grouping by what we can do about each

| Group | Categories | Records | % | Won MRR/mo |
|---|---|---|---|---|
| Campaign-recoverable (true inbound, join failed) | F | 31 | 4.8% | $5,104 |
| De-pollution: remove from inbound credit (debit) | C, H | 37 | 5.7% | $1,155 |
| De-pollution: relabel as Product-Led, keep in funnel | A | 72 | 11.0% | $22,072 |
| Marketing-influenced, non-form source | B, E, G | 73 | 11.2% | $17,040 |
| Inherit prior-cycle attribution | D | 16 | 2.5% | $13,442 |
| Capture gap (fix forward) | I, J | 423 | 64.9% | $72,017 |
| Structurally unrecoverable by identity (no email) | subset across A,B,G,J | 36 | 5.5% | n/a |

Two cautions that the analysis enforces:

- Debit versus relabel are different operations. Outbound (36) and CS (1) should be removed from the inbound-marketing credit. PLG (72) should not be deleted, it should stay in the full-funnel SQL count and only be excluded from the marketing-attributable view via a filter. Treating all 109 as one "remove from inbound" set is wrong and would silently drop completed-meeting SQLs.
- The outbound mis-tag is overwhelmingly a 2026 phenomenon: 32 of 36 outbound-mis-sourced records were created in 2026 (2025: 1, 2024: 3, 2023: 0), accelerating month over month. This is a recent process or tagging change, not a historical pattern, so it must not be subtracted uniformly across history.

## 2. Recommended attribution framework

A tiered waterfall assigns an auditable basis to every one of the 652 SQLs without ever inventing a channel to fill a cell. Each record lands in exactly one tier. Inferred values are written only to inference columns, never over the locked Pre-Op Last Touch Source or the genuine form-MQL fields.

| Tier | Name | Matches on | Assigns | Coverage |
|---|---|---|---|---|
| 1 | Hard identity stitch | Email, anonymous_id, or product user_id joined to product, web session, and ad-click data. Sub-order: (1a) hard ad-click id (gclid, fbclid, msclkid, li_fat_id) timestamped before Pre-Op create; (1b) self-serve account with signup before Pre-Op create; (1c) first-touch organic session with no paid params | 1a: Paid plus campaign, HIGH (the only path that may ever write Paid). 1b: Product-Led, HIGH. 1c: Organic, HIGH. Populates INFERRED_MQL_ID | ~99 records (15%). Campaign-recoverable slice inside = 31 digital |
| 2 | Structural CRM reclassification | BD Owner populated (mis-tag), or prior Pre-Op cycle (Pre-Op Number Count > 1), or CS creator or active subscription | BD Owner: reclassify to Outbound (debit, removed from inbound credit). Prior cycle: inherit original source forward. CS: Customer Success | ~53 records (8%) |
| 3 | Deterministic keyword classification | AE discovery text, unambiguous lexical signatures only (referral, event, AI, explicit organic) | Referral, Event, AI Search at MED. Never Paid | ~73 records (11%) |
| 4 | LLM tie-breaker | Same discovery text, second opinion on Tier 3 | Agreement upgrades confidence, disagreement keeps the conservative label and flags for review. Quality layer, no new coverage | 0 net new |
| 5 | Identity re-join of the blank residual | The 382 blank records with an email | If a real form-MQL surfaces, raise a data-quality alarm and populate INFERRED_MQL_ID. Otherwise Sales-Direct or Unknown at the record level, confidence NONE | ~382 records (59%) |
| 6 | Uninformative sink | Discovery present, no usable signal | Sales-Direct or Unknown, retain text for future re-mining | ~12 records (2%) |
| 7 | Unrecoverable flag | No email and no identity key | Flag Unrecoverable, never guessed | ~36 records (5.5%) |

### Core business rules

1. Disambiguate the two MQLs. Redefine reporting MQL as `acquisition_type = Marketing Inbound`, not `Last Touch Source = Inbound`. Update the `preop-data-intelligence` skill accordingly. The current definition is structurally polluted.
2. Inference never touches source-of-truth fields. Write only to INFERRED_MQL_ID and sibling columns (inferred_channel_group, inferred_source, inference_tier, inference_confidence, inference_evidence, attribution_basis). INFERRED_MQL_ID is populated only where the true MQL_ID is null.
3. Paid is quarantined behind deterministic evidence. Paid or a specific campaign can be assigned only via a hard ad-click id whose timestamp precedes Pre-Op creation. No free-text, LLM, or aggregate prior may ever write Paid. An AE typing "saw your ad" with no click id routes to Organic or Unknown, never Paid. This is the core anti-ROAS-inflation control.
4. Debit versus relabel. Outbound and CS are debited out of the inbound credit. PLG is relabeled but kept in the full-funnel SQL count and excluded from the marketing-attributable view only by filter. Never delete a completed-meeting SQL from the SQL fact (36 of the outbound records are already promoted to deals).
5. Two report views, never conflated. Marketing-attributable view (true form-MQL plus HIGH and MED inferred only) feeds CAC, ROAS, and MQL-to-SQL by campaign. Full-funnel view (all 652 with basis visible) feeds pipeline coverage and exec funnel volume. The funnel model left-joins from the SQL grain so no SQL is dropped.
6. Forward capture beats backfill. Split Last Touch Source into a locked acquisition_type plus a required source_detail enum, auto-detect PLG, outbound, and CS at Pre-Op creation, gate stage advancement on a non-blank source_detail, and add re-engagement inheritance for Pre-Op Number Count > 1.
7. Required field alone is not enough. A required picklist gives a non-null value, not a true one (AEs will pick "Other"). Pair it with auto-detection and a published monthly accuracy match-rate against call notes, with a completion-quality target.

## 3. Estimated reporting improvement

State the improvement honestly as before and after, not as recovered ad spend.

Before:
- 0 of 652 (0%) carry any source attribution.
- $130,829 won MRR per month sits entirely unattributed.
- The Inbound MQL count includes at least 109 non-marketing records (PLG, outbound, CS) that overstate marketing's contribution and depress measured MQL-to-SQL quality.

After:
- Every one of the 652 SQLs carries an auditable attribution_basis: campaign, channel, structural, reclassified, or capture-gap. None are silently dropped from the funnel.
- Campaign or channel recoverable via identity: about 31 records (4.8%), about $5.1K won MRR per month (3.9% of the $130.8K total). This is the only slice that returns true campaign credit.
- Correctly removed or relabeled out of marketing inbound: 109 records (16.7%), about $23.2K won MRR. This de-pollutes the inbound number, which is the highest-value outcome.
- Assigned a real non-campaign source (referral, event, AI, re-engagement): about 89 records (13.7%), about $30.5K won MRR.
- Capture-gap residual that only forward capture fixes durably: about 423 records (64.9%), about $72.0K won MRR.

Net effect on the reports: the Inbound MQL number drops (removing the polluting 109), MQL-to-SQL conversion by channel becomes meaningful for the recoverable slice, PLG and referral and outbound get their own honest lanes, and exec funnel volume stops losing completed-meeting SQLs.

Sizing against the funnel: the 652 orphans are about 4.4% of the 14,934 inbound SQLs in FY2023 to FY2026 (15,217 SQLs total). So this is a contained, fixable gap rather than a majority of the funnel. Two things make it worth fixing anyway: the orphans skew to high-value deals ($1.57M ARR won with no attribution), and the same root causes (mis-tagged outbound, PLG counted as inbound, blank source capture) distort the much larger inbound population too, not just these 652. Note that the Omni funnel topic reports every inbound SQL as "MQL present" because it defines MQL as an inbound Pre-Op, so it cannot currently surface the form-MQL gap at all. That reporting blind spot is itself part of the fix.

## 4. Technical requirements

Effort: S small, M medium, L large.

| Area | Requirement | Effort |
|---|---|---|
| Identity layer (dbt) | Build an identity spine keyed on a person surrogate, unioning HubSpot contact email (normalized: lowercase, trim, strip plus-tags, with a review allow-list for role addresses so legitimate B2B shared inboxes are not dropped), web anonymous_id, product user_id, and contact id. Handle multi-contact Pre-Ops by defining a canonical contact and unioning candidate sets across associated contacts. | L |
| Candidate model (dbt) | Build an inferred-MQL candidate model implementing the precedence ladder (ad-click, signup-before-create, first-visit channel, anonymous-id first-visit, temporal-nearest within a bounded window). Pick one winner per Pre-Op by precedence then time delta. | M |
| Backfill and columns (dbt) | Populate INFERRED_MQL_ID only where the true MQL_ID is null. Add companion columns: inferred_attribution_method, inferred_channel_group, inferred_source, attribution_confidence, attribution_basis, inference_evidence, inferred_at. Encode the category-to-basis map as a version-controlled seed. | M |
| Funnel re-point (dbt) | Change the MQL-to-SQL funnel model to left-join from the SQL grain with attributed_channel_group = coalesce(true channel, inferred channel, 'unattributed'). Add a test asserting SQL count in the funnel equals completed-meeting Pre-Op count, so zero SQLs are dropped. Ship the two report views. | M |
| Classification jobs | Productionize the keyword pass and the LLM pass over records with discovery text, with agreement gating and a hard non-paid output constraint. Both passes already exist as artifacts in this analysis. | M |
| HubSpot fields | Add a locked acquisition_type single-select and a required source_detail enum (about 16 values drawn from observed patterns), keep a small optional free-text note, and migrate the 652 by Record-ID-keyed import from the classification map. Redefine reporting MQL. | M |
| HubSpot workflows | Creation-time workflows: PLG auto-detect on product plan or user_id, outbound detection on BD Owner or logged sequence in a trailing window (also catch non-BD outbound), CS detection, re-engagement inheritance on Pre-Op Number Count > 1, and required-property-on-stage gating. | L |
| Validation harness | Held-out test that masks true form-MQL links and measures inferred-versus-true channel match rate to gate confidence thresholds, stratified to resemble the orphan population mix (not the cohort that already has MQLs). Surface any exact form-MQL hit inside this gap as a data-quality alarm. | M |
| Ops and governance | Materialize candidate and backfill models as incremental on Pre-Op create date, re-evaluate confidence-NONE records each run, publish a weekly source-quality exceptions view with a target under 5%, and a monthly list of high-MRR confidence-NONE SQLs. Map and version every downstream dashboard and Omni topic affected by the MQL redefinition, since the historical Inbound MQL trend will shift. Assign owners per `references/team.md`. | S |

## 5. Risks, guardrails, and open questions

From adversarial review of the framework:

- Identity presence is not campaign recovery. 94.5% have an email, but that is joinability, not a form-MQL. Realistic campaign recovery is the ~5% digital slice. Do not promise recovered ad credit beyond that.
- Ban unbounded temporal joins from record writes. A nearest-session match within a long window can attach an unrelated visit to a sales-direct SQL. Keep temporal-nearest at LOW confidence, exclude it from CAC and ROAS, and set a precision floor before it is written even to the full-funnel view.
- Dual-track the time series at cutover. Keep the legacy MQL definition running alongside the new one, restate at least a trailing 12 months on both, and never splice a pre-change number against a post-change number on one axis. The 2026 outbound mis-tag must be fixed forward, not subtracted uniformly across history.
- Required field can relocate the gap. Without auto-detection and a measured adoption and completion-quality KPI, blanks become "Other" selections.
- Re-engagement inheritance needs guards. The prior cycle may itself be an orphan, the inherited campaign may be defunct (needs a recency cap), and crediting the original channel for a revived deal is a debatable choice versus a last-touch-on-re-engagement alternative.
- AI and LLM should not be dead-ended. Carve out an AI Search inferred channel detectable from referrer domains (chatgpt.com, perplexity.ai) and add a forward-capture enum value, since this channel is growing.
- No human-labeled ground truth yet for the free-text tiers. The 86.7% keyword-versus-LLM agreement measures consistency, not correctness. Hand-label a 50 to 100 record sample, publish precision and recall per category, and resource the roughly 13% review queue.

Open inputs needed before publishing numbers to leadership:

1. Total SQL population: resolved. 14,934 inbound SQLs in FY2023 to FY2026 (Omni), so the 652 orphans are about 4.4% of inbound SQLs.
2. Confirmation of the 2023-05 batch as a migration artifact (against HubSpot import history).
3. Currency basis of DEAL_MRR. This export has no currency column, so MRR is summed as-exported; confirm it is USD-normalized before MRR-based prioritization.
4. Whether the 2026 outbound mis-tag reflects a real new BD motion or a detection change, to choose forward-only fix versus restatement.

## Appendix: method and artifacts

- `classified_orphan_sqls.csv`: all 652 records with root-cause category, suggested source, funnel outcome, and MRR.
- `crosstab.json`: category-by-impact aggregates.
- `llm_classification.json`, `keyword_classification.json`: the two classification passes (canonical is the LLM pass).
- Classification method: LLM pass over the 241 non-blank discovery strings into a fixed 9-category taxonomy with a single-auditor consistency reconciliation, cross-checked against an independent deterministic keyword classifier (86.7% agreement). Blank records form their own category. All financial and timing figures computed deterministically from the export.
- Definitions follow the `preop-data-intelligence` skill: MQL = inbound Pre-Op, SQL = Pre-Op with a completed intro meeting, Last Touch Source set at Pre-Op creation and locked.
