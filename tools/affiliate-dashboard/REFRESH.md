# Affiliate Channel Funnel dashboard - refresh runbook

Self-contained runbook to rebuild the **Affiliate Channel Funnel** dashboard from live HubSpot
data and republish it to its stable artifact URL. Written so a fresh Claude Code session (local or
cloud routine) can run it end to end with only this folder and a HubSpot connection.

- **Stable artifact URL (always republish here so the link never changes):**
  `https://claude.ai/code/artifact/6dfc2b68-5f3f-47ef-9ab2-5c399bbeda3f`
  (short form `https://claude.ai/artifact/EaiuGrSTCPW6KxvAXkPQVC` - same artifact). Its title is
  **"Affiliate Channel Funnel - Riverside · Live"**; the ` · Live` suffix comes from the template's
  `<title>` and is how a reader tells this one from any copy. The header chip shows `Live · Snapshot
  <date> · built <time>`, so two publishes of the same snapshot are distinguishable.
- **Never publish without `url=`.** A publish that omits it creates a *second* artifact with the same
  title. That happened on the 2026-08-02 refresh: an org-visible copy
  (`https://claude.ai/artifact/6goC6n3zEkTRrvBZ4d97mA`, owned by another account) circulated as "the
  report" while every later refresh and fix went to the stable URL above. It sat frozen at the Aug-2
  snapshot for seven weeks until 2026-09-20, when it was retitled **"[ARCHIVED 2026-08-02] …"** and
  given a banner pointing here. Do not refresh it; if a new duplicate ever appears in the artifact
  list, do the same to it rather than keeping two live copies in sync.
- **HubSpot portal:** `9154210` (Riverside)
- **Files in this folder:**
  - `dashboard_template.html` - the full dashboard shell. One placeholder, `__DASHBOARD_DATA_JSON__`, where the data JSON is substituted in.
    **Edit this file, never the published page.** Every refresh rebuilds `dashboard.html` from this
    template wholesale, so anything changed only on the live artifact is erased by the next run. This
    happened to tile 4's per-stage MRR line: it was built completely on the live page (column width,
    CSS, copy, JS with the Renewals exclusion, per-deal MRR in the click-through panel) and never
    committed, so the 2026-09-20 refresh wiped it and it had to be reconstructed from a diff of the
    old live page against this file. Same rule and same reason as `build_data.py`'s `STAGE_LABELS`
    below.
  - `build_data.py` - turns the raw HubSpot pulls into `dashboard_data.json` (pipeline/stage label maps, funnel bucket rules, MRR rule, URLs). Run it, don't hand-edit the output.

## What the dashboard shows

A top-bar **search** box (independent of the source chips) matches any contact in the snapshot by
email address, company name, or contact name and lists the hits with a direct HubSpot record link.

Six cross-filterable tiles (filter by source):
1. New meetings by contact creation date - Week/Month/Quarter toggle. Week and Month stay within
   the rolling 6-month window; Quarter switches to full history (fiscal quarters, see below).
   In **Month and Quarter view each bar is stacked by affiliate partner** (segment colors match the
   filter chips, with a partner legend under the chart); Week view stays a single-series bar.
2. Meetings completed by date - same Week/Month/Quarter toggle, independent of tile 1's. **Week view**
   shows two stacked segments: a solid "confirmed" segment (HubSpot's own `meeting_booked___completed`
   date) and a lighter "inferred" segment for contacts missing that property whose deal has since
   reached a stage that can't be reached without an intro meeting (see Step 3.5 - this property
   goes stale on ~1 in 5 contacts once their deal moves past intro). In **Month and Quarter view each
   bar is instead stacked by affiliate partner** (same partner colors/legend as tile 1); the
   confirmed-vs-inferred split is not shown at the bar level there, but the footer still reports the
   inferred total for the window/all-time. A small number of contacts are confirmed-by-deal-stage but
   have no safe date to plot at all; the tile's footer counts these separately rather than dropping
   them silently. The footer also reports the count of **distinct companies** among the shown
   contacts, alongside the raw contact count - a deal is per-account, so this is often the lower of
   the two numbers (see the `vendor_roi.companies` note below for why).
3. Follow-Up-stage pre-opps, stacked by pre-opp pipeline (full history)
4. Every record bucketed by current stage, in the fixed `FUNNEL_ORDER`. **All time / Month / Quarter
   toggle plus a period picker** (added 2026-09-24): Month and Quarter keep only records whose
   `meeting_date` falls in the picked month or fiscal quarter, both over full history. A deal's
   `meeting_date` = the earliest `meeting_completed_effective` (tile 2's date) among its linked
   cohort contacts, from Step 3.5's links. Records with no dated contact are left out of a
   Month/Quarter view and counted in the tile footer. The stage bars, Closed-Lost split and
   per-stage MRR all follow the picked period. Pre-opps in the
   "Promoted to Deal" stage are deliberately excluded - that stage is a stale marker left on the
   originating Pre-Opp record once a real Deal record is created for the same opportunity, and the
   Deal gets its own bucket further down this same list (S1-S7, Closed won/Lost, Active Client).
   Counting both would double-count the opportunity (confirmed by name-matching, e.g. a pre-opp
   "[Pre-Opp #1] Agile Mind" promoted, then a separate "Agile Mind - Agency Studio Plus" deal
   closed-won, then a separate "Agile Mind - Renewal" active-client deal - one customer, three rows).
   The **Closed Lost** bar is stacked by the furthest stage each lost deal reached (see Step 3.6).
   **Every other bucket `STAGE_LABELS` can produce must be in `FUNNEL_ORDER`.** Tile 4 only draws a
   row for buckets named in it - a real bucket left out isn't shown as zero, it's dropped with no
   error. Confirmed 2026-08-30: "Intro Completed" and "Demo Completed" were accidentally missing,
   so 8 real deals across the snapshot never appeared in any tile-4 view or source filter - Nir
   caught it by noticing boscia group's Vendor-ROI SQL count (9) didn't match its visible tile-4
   total (4). If you add a new named bucket anywhere in `STAGE_LABELS`, add it to `FUNNEL_ORDER`
   too (unless deliberately excluding it like Promoted to Deal above) - and add it to
   `FUNNEL_LABELS` (and ideally `ORDINAL_STAGES`) in `dashboard_template.html`, or it renders as
   literal "undefined" text instead of a bar.
5. Total current MRR - closed-won deals only (open renewals excluded to avoid double-counting)
6. Open Follow-Up deals, one wedge per deal
7. **Vendor ROI** (full-width section below): per-vendor cost / SQLs / companies / cost-per-SQL / S1s /
   customers / ARR / ROI. Cost = cumulative paid invoices (Step 3.7); SQLs = completed meetings
   (tile-2 definition, counted per contact); companies = distinct accounts among those SQLs (Nir,
   2026-08-30: a deal is per-account, not per-contact - e.g. two boscia-sourced Bain contacts each
   completing their own meeting still share one deal record, so companies is often lower than
   SQLs). S1s = records that reached S1 or beyond (furthest stage, "Promoted to Deal" pre-opps
   excluded); customers = closed-won; ARR = closed-won MRR x 12; ROI = ARR / cost (a multiple).
   Not filtered by the source chips.

**Fiscal quarters** (tiles 1-2's Quarter view): Q1 Feb-Apr, Q2 May-Jul, Q3 Aug-Oct, Q4 Nov-Jan
(Q4 spans the calendar-year boundary, labeled by the November year) - same definition as
`tools/daily-reports/build/build_artifact.py:fiscal_q`. Only quarters with at least one record
render (no empty placeholder bars).

Named partners (`ziffdavis, memoryblue, pursuit, boscia group`) always appear as filter chips
even when a snapshot has none of their records. **`landd` and `boscia group` are the same partner** and
are merged into a single `boscia group` chip - `build_data.py` normalizes the source tag (via
`SOURCE_ALIASES`) and the template mirrors it in `normSource()`. Step 1 still filters the raw HubSpot
`landd` value in its pull; only the displayed/attributed tag is merged.

## Prerequisites

- A HubSpot connection for portal `9154210` with read access to contacts and deals
  (`search_crm_objects`, `get_crm_objects`).
- Tools: `Bash`, `Read`, `Write`, `Edit`, and the `Artifact` tool for publishing.
- Work in a scratch directory; write all intermediate files there and pass it to `build_data.py`.

> Note: the cross-object `query_crm_data` SQL path is NOT used here - that tool needs a permission
> the current HubSpot connection lacks. Source attribution is done with per-source association
> searches instead (Step 3), which only need the standard `search_crm_objects` scope.

## Step 1 - Pull the affiliate contact cohort

`search_crm_objects` on `contacts`, `limit: 200`, with these four filter groups (each in its own
group so they combine with **OR**):

```json
[
 {"filters":[{"propertyName":"utm_source","operator":"IN","values":["ziffdavis","memoryblue","landd","pursuit","boscia group"]}]},
 {"filters":[{"propertyName":"meeting_source_cp","operator":"IN","values":["ziffdavis","memoryblue","landd","pursuit","boscia group"]}]},
 {"filters":[{"propertyName":"meeting_medium_cp","operator":"EQ","value":"affiliate"}]},
 {"filters":[{"propertyName":"utm_medium","operator":"EQ","value":"affiliate"}]}
]
```

Properties: `utm_source, meeting_source_cp, meeting_medium_cp, utm_medium, createdate, meeting_booked,
meeting_booked___completed, num_associated_deals, hs_full_name_or_email, company, email`. Check `total`;
if > 200, paginate with `offset` until you have every contact.

Write `contacts.json` as a list of objects in this exact shape (this is what `build_data.py` reads):

```json
{"id","name","utm_source|null","meeting_source_cp|null","meeting_medium_cp|null","utm_medium|null",
 "createdate":"YYYY-MM-DD|null","meeting_completed":"YYYY-MM-DD|null","company":"<name>|null",
 "email":"<email>|null","url":"https://app.hubspot.com/contacts/9154210/record/0-1/{id}"}
```

`name` = `hs_full_name_or_email` (fallback to displayName). `meeting_completed` = first 10 chars of
`meeting_booked___completed`. `company` = the `company` contact property (shown in the click-through
panel next to the contact name - passed straight through by `build_data.py`). `email` = the `email`
contact property, also passed straight through - it is shown under the contact name in the click-through
panel **and** is what the dashboard's top-bar search matches on (email or company). If `email` is
omitted from an older pull, `build_data.py` backfills it as `null` and the search/panel simply show no
address for those contacts. Also save
`contact_ids.json` (list of all contact ids), and
`missing_completion_ids.json` (the subset of contact ids where `meeting_completed` is null - feeds
Step 3.5).

## Step 2 - Pull associated deals / pre-opps

Pre-opps and deals are both the `deals` object, distinguished by `record_type`
(`Pre-Opp (SQL)` vs `Deal`). Chunk the contact ids into groups of **≤ 20** and, for each chunk,
`search_crm_objects` on `deals` with `limit: 200` and:

```json
"filterGroups":[{"associatedWith":[{"objectType":"contacts","operator":"IN","objectIdValues":[...chunk...]}]}]
```

> **Chunk size is ≤ 20, not ≤ 100.** HubSpot's `associatedWith IN` filter silently under-matches
> once the id list gets close to ~100 - it reports `total` as fully paginated (no more pages) while
> actually dropping real matches, so the mismatch doesn't surface as an error. Confirmed on the
> 2026-08-02 refresh: two 100-id chunks missed 34 of 144 real deals; re-running the same contacts in
> ≤20-id chunks found all of them, and a further 10-vs-10 split of one 20-chunk returned an identical
> result. Always run the Step 3 validation below - it's the only thing that catches this.

Properties: `dealname, pipeline, dealstage, hs_mrr, amount, createdate, closedate, record_type,
stage_category, region, deal_currency_code, hs_currency_code`. Merge all chunks and **de-dupe by id**.
Save `deals_raw.json` as `{deal_id: <properties dict>}` and `deal_ids.json` (list of all deal ids).

Tip: a few ≤20-id chunks can be sent as separate `filterGroups` (OR) in one call. Large results are
saved to a file by the tool; parse that file rather than reading it all into context.

## Step 3 - Attribute each deal to its source(s)

A deal's source(s) = the source tags of the cohort contacts it is associated with, where a contact's
tag = `utm_source or meeting_source_cp`. Because the cross-object SQL path is unavailable, derive this
with per-source association searches:

1. Group the cohort contacts (from Step 1) by their source tag.
2. For each source group, chunk its contact ids to **≤ 20** (same reason as Step 2) and
   `search_crm_objects` on `deals` with `properties:["hs_object_id"]` and `associatedWith` each chunk.
   Every returned deal id gets that source added to its set.
3. Union across groups → `deal_sources.json` as `{deal_id: [source, ...]}`.

**Validate:** the union of all deal ids seen across the source groups must equal exactly the set in
`deal_ids.json`. If it doesn't, a group search paged or a chunk was dropped - fix before continuing.

## Step 3.5 - Backfill meeting-completed for contacts HubSpot's own field misses

HubSpot's `meeting_booked___completed` contact property reliably stays populated only while a
contact's deal is still early (Pre-Opp/intro). Once the deal progresses past intro, the property is
often left blank even though the meeting demonstrably happened - confirmed on the 2026-08-02
refresh: ~1 in 5 cohort contacts on a post-intro-stage deal had no completion date at all, including
contacts whose deal was already Closed Won or Active Client. Tile 2 undercounted real completions as
a result. This step recovers what it can from deal-stage evidence, without fabricating dates for
contacts it can't safely date.

1. Read `contact_ids.json` from Step 1 - **every** cohort contact, not only the ones missing
   `meeting_completed`. The deal links serve two jobs: backfilling missing meeting dates (below) and
   dating each deal's first meeting for tile 4's Month / Quarter filter, which needs the links of
   contacts that already have a date too (added 2026-09-24). A contact with no date and no
   post-intro deal simply contributes nothing.
2. For each contact id **individually** (one `search_crm_objects` call per id - batching loses the
   per-contact attribution this step needs), `search_crm_objects` on `deals` with
   `associatedWith: [{"objectType":"contacts","operator":"EQUAL","objectIdValues":[<id>]}]`,
   properties `["dealstage","pipeline","stage_category","createdate","record_type"]`, `limit: 20`.
   Save the result as `contact_deal_links.json`: `{contact_id: [{"deal_id","dealstage","pipeline",
   "stage_category","createdate"}, ...]}`, with an entry (possibly `[]`) for every input id.
3. Separately, `get_crm_objects` (direct ID fetch, not a search - no chunk-size caveat applies) on
   `contacts` for the `missing_completion_ids.json` list only, properties `["meeting_booked"]`. Save any non-null results as
   `meeting_booked_lookup.json`: `{contact_id: "YYYY-MM-DD"}`.

`build_data.py` (Step 4) does the actual inference - reasoning over deal buckets, not raw stage ids -
and applies one safety rule worth knowing before touching it: **a linked deal's `createdate` is
only trusted as this contact's own meeting date if the deal doesn't predate the contact by more than
7 days.** A deal that already existed well before the contact record was created means the contact
is a later stakeholder added to an already-in-motion deal (an account teammate looped in after the
fact), not the person whose meeting created it - confirmed on real examples with gaps of 25 to 739
days. Contacts caught by that guard are marked "confirmed, undated" instead of given a fabricated
date. Both files are optional inputs to `build_data.py` - omit them (e.g. for a quick local rebuild)
and every contact simply falls back to its original `meeting_completed` value with no inference.

## Step 3.6 - Closed-Lost stage history (feeds the tile-4 stacked bar)

Tile 4's **Closed Lost** bar is split by the *furthest stage each lost deal ever reached* (e.g. a deal
that got to S1 before it was lost shows under S1; one lost straight out of Meeting Booked shows there).
HubSpot exposes this via the auto-generated per-stage `hs_v2_date_entered_<stageId>` properties: a deal
has a non-null value for every stage it ever entered. `build_data.py` (Step 4) turns those into
`peak_stage` using `PEAK_ORDER`.

1. From `deals_raw.json`, take every deal with `stage_category == "Lost"`.
2. `get_crm_objects` on `deals` (direct ID fetch, batch ≤ 100 ids) requesting one
   `hs_v2_date_entered_<stageId>` per stage id in `build_data.py`'s `STAGE_LABELS`. Generate that
   property list straight from the source of truth (no committed duplicate to drift):

   ```bash
   python3 - <<'PY'
   import re, json
   ids = re.findall(r'"(\d+)":', re.search(r'STAGE_LABELS = \{(.*?)\}', open("build_data.py").read(), re.S).group(1))
   json.dump([f"hs_v2_date_entered_{i}" for i in sorted(set(ids))], open("stage_entered_props.json","w"))
   PY
   ```
3. Write `closed_lost_stage_history.json` as `{deal_id: {stageId: "<entered date ISO>", ...}}`, keeping only
   non-null entries and keying by the bare `stageId` (strip the `hs_v2_date_entered_` prefix). Skip
   `hs_v2_date_entered_current_stage`.

Optional input - omit it and Closed-Lost deals simply render as one solid bar with no stage breakdown.

## Step 3.7 - Vendor spend (feeds the Vendor ROI section)

The **Vendor ROI** section needs cumulative spend per vendor. Source: the **Invoices and Payments -
Growth Marketing** board (`18390740532`, Dor's board, in the `Marketing` monday workspace `6001561` - it
has a built-in "Dor's Dashboard" view). Pull all items (paginate; skip the `Emailed items` intake group
`group_mm1fdkmn`) reading `text_mm4ecyyd` (Company name), `numeric_mky9safm` (Invoice Sum, $),
`boolean_mky9pwjm` (Payment Done), `dropdown_mky9maht` (Payment Method). Map each item to a source tag by
case-insensitive substring on Company name / item name / Payment Method:

| tag | matches |
|-----|---------|
| `ziffdavis` | ziff, swzd, spiceworks |
| `memoryblue` | memoryblue, memory blue |
| `pursuit` | pursuit |
| `boscia group` | boscia, l&d, l and d, landd, l & d |
| `ryze` | ryze |
| `smartreachai` | smartreach, smart reach |

Write `vendor_costs.json` = `{tag: {"paid": <sum Invoice Sum where Payment Done>, "all": <sum regardless>,
"invoices": <count>}}`. `build_data.py` uses `paid` as "cost". Optional input - omit it and the ROI table's
cost / cost-per-SQL / ROI columns render as "-".

**Manual overrides:** the board's `Payment Done` checkbox is under-maintained, so a pulled `paid` can
understate real spend. Put confirmed corrections in `vendor_costs_overrides.json` = `{tag: {"paid": X}}`;
`build_data.py` merges it on top of `vendor_costs.json` (override wins). Current override: `pursuit` paid
`30000` (two invoices actually paid; only one checked on the board - Nir, 2026-08-10). This file is the one
place such corrections live, so they survive refreshes until the board is fixed.

> The monday connector available in a fresh session may not see the Growth Channels workspace, but board
> `18390740532` lives in the `Marketing` workspace and is reachable by id.

## Step 4 - Assemble dashboard_data.json

Run `python3 build_data.py <workdir>`. It reads `contacts.json`, `deals_raw.json`, `deal_sources.json`,
and optionally `contact_deal_links.json` / `meeting_booked_lookup.json` (Step 3.5) from `<workdir>`
and writes `dashboard_data.json`, then prints a sanity report. Key rules it applies (don't change
without reason):

- **Funnel order** (`FUNNEL_ORDER`) is a fixed business order, not alphabetical / by volume.
- **Source merge** (`SOURCE_ALIASES`): `landd` → `boscia group`, applied to every derived source tag
  (contacts, deal attribution, chip lists). See the named-partners note above.
- **`peak_stage`** (Closed-Lost deals only) = furthest stage reached, from `closed_lost_stage_history.json`
  ranked by `PEAK_ORDER`. `null` when no prior stage is recorded → renders as "No prior stage".
- **`vendor_roi`** = per-vendor rollup (cost from `vendor_costs.json`, everything else from this snapshot).
  See the tile-7 definitions above. Rows with no cost and no pipeline are dropped; sorted by ARR desc.
  `companies` (and tile 2's footer company count) dedupe by the contact's `company` property; a
  contact with no company value counts as its own distinct company rather than being merged with
  every other company-less contact into one bucket.
- **MRR** = sum of `hs_mrr` for deals whose bucket is `Closed won` only. Renewal deals (pipeline
  Renewals → bucket `Active Client`) are excluded so already-live revenue isn't double-counted.
- **Account Expansion and Upsell Pipeline deals are EXCLUDED from the dashboard entirely** -
  never shown in any tile, never counted in Vendor ROI's SQLs/S1s/customers/ARR. Both pipelines
  exist only for revenue on an ALREADY-ACTIVE customer account, so a deal in either one is never
  evidence the affiliate channel sourced anything - even when it's linked to a cohort contact,
  even under the `Active Client` bucket Renewals legitimately use. The distinction from Renewals
  (Nir, 2026-08-30): a Renewal traces back to a deal that *did* win within this same affiliate
  dataset, so counting it as `Active Client` reflects real channel-sourced retention. An Account
  Expansion/Upsell deal has no such lineage - the account was already a customer through some
  unrelated route before this contact's affiliate touch, so the deal is incidental, not sourced.
  If the affiliate meeting genuinely brought new business, that shows up as its own Pre-Opp/New-
  Sales deal and is counted normally; only the existing-customer expansion deal itself is excluded.
  `build_data.py`'s `EXPANSION_PIPELINES` set implements this - it filters these deals out of
  `deals_out` before they can reach any tile or ROI calculation, and instead collects them into
  `flagged_existing_customer_deals`, printed by the sanity report as
  `!! N EXISTING-CUSTOMER PIPELINE DEAL(S) EXCLUDED`. **Whoever runs a refresh must read that list
  and relay it to Nir for manual verification** (it will usually be empty) - never silently drop
  it, and never add a flagged deal to the dashboard on your own judgment. Case history: a Bain &
  Company Account Expansion deal kept resurfacing under the S1 bucket because an earlier fix
  mapped its stage id to "S1" purely to silence the warning below, and a later fix only moved it
  to "Active Client" (still shown/counted) before Nir clarified it should never appear at all -
  see `/retro` output from 2026-08-30 before changing this again.
- **Unknown dealstage id:** the script buckets it by Won/Lost/open (or `Active Client` for
  Renewals). If the report prints `!! UNMAPPED STAGES`, reason each into the right bucket - **the
  correct bucket, not just whichever one clears the warning** - add it to `STAGE_LABELS`, and
  **commit the change to this checked-in `build_data.py`** (not just a scratch working copy). A
  fix made only in a session's temp directory is invisible to the next refresh, which starts from
  a clean checkout and will rediscover - and re-"fix" - the exact same stage.
- **`meeting_completed_effective` / `meeting_completed_inferred` / `meeting_confirmed_undated`**
  (per contact) are Step 3.5's output - see above. `meeting_completed` itself is left untouched as
  the raw HubSpot value.
- `today` / `window_start` are computed at build time (window = today − 182 days) and written into the
  JSON, so the rolling 6-month window stays correct on every refresh.

Sanity-check the report against the previous snapshot (contact/deal counts and total MRR shouldn't
move wildly day to day). The report also prints how many contacts were backfilled (dated) vs.
left undated - those counts shouldn't swing wildly either.

## Step 5 - Build and publish

```bash
python3 - <<'PY'
tpl=open("dashboard_template.html").read()
data=open("dashboard_data.json").read()
assert "__DASHBOARD_DATA_JSON__" in tpl and "</script>" not in data
open("dashboard.html","w").write(tpl.replace("__DASHBOARD_DATA_JSON__", data))
PY
```

Publish `dashboard.html` with the **Artifact tool**, passing
`url: https://claude.ai/code/artifact/6dfc2b68-5f3f-47ef-9ab2-5c399bbeda3f` so the link stays stable,
`favicon: 📊`. The `<title>` comes from the file and must end in ` · Live`. Open it and confirm the
numbers roughly match the prior snapshot before finishing, and that the header chip's `built` time is
this run's. If the publish result reports a *new* URL rather than this one, `url=` was dropped - do not
hand that link out; republish to the stable URL and retitle the stray as `[ARCHIVED …]` (see the
"Never publish without `url=`" note at the top).

If Step 4's sanity report printed `!! N EXISTING-CUSTOMER PIPELINE DEAL(S) EXCLUDED`, list every one
of them (deal name, pipeline, sources, URL) in your final message to whoever asked for the refresh -
this is a manual-check flag, not an error to silently swallow, and the deal must stay out of the
published dashboard regardless.
