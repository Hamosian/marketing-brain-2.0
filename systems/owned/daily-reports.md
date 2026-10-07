# Daily Reports (Nir's PLG/ROI daily artifacts)

> Two Claude-driven daily reports Nir owns, rebuilt every morning from Snowflake: a **PLG channel-detail**
> report and an **ROI & Growth** report. Distinct from the analytics team's n8n "Daily Self-Serve Funnel
> Report" (see [Marketing Operating Model](../reference/marketing-operating-model.md)) - these two are
> ours, code lives in this repo, and we maintain them.

## What it is

| Report | Audience view | Builder | Live surface | Refreshed |
|--------|---------------|---------|--------------|-----------|
| PLG channel-detail | Per-channel signups / trials / subscriptions / first-MRR with a MoM⇄WoW⇄Daily toggle, channel groups (Paid / Partnerships / Affiliates) expandable to sub-channels, planned-share-% next to each name, and Q3 attainment (trials & first MRR) at the **channel-group level only**. Targets come exclusively from the quarter plan (`CHANNEL_Q_TARGETS` in the builder, copied from the Q3 2026 plan artifact `34ed9a9f…`); channels absent from the plan and sub-channels show "-" - **never derive channel targets from history** | `tools/daily-reports/build/build_artifact.py` | claude.ai artifact `0b9eef24-e1a7-4e3c-b145-f666fa97a7c8` | Daily |
| ROI & Growth | PLG month/week/30d, sub breakdown, SLG by segment, spend, ROI | `tools/daily-reports/build/build_roi_artifact.py` | Analytics Hub report `de39972a29cf46f3bbb57fac09833214` (`…/hub/de39972a…`, Marketing/Reports) | Daily |

Both anchor on the **latest complete day** (yesterday) - never same-day, which is always incomplete.

## Source of truth

- **Recipe:** [`tools/daily-reports/REFRESH_DAILY.md`](../../tools/daily-reports/REFRESH_DAILY.md) - the
  unified step-by-step the routine follows. Gates once, finds the anchor once, runs one query set, builds
  and deploys both reports.
- **Builders:** `tools/daily-reports/build/*.py`. `tools/daily-reports/build/build_roi_artifact.py` imports `compute_params()` from
  `tools/daily-reports/build/build_artifact.py` for all date math (windows, run-rates, targets), so they must stay co-located.
  Requires Python 3 + `openpyxl`.
- **Inputs (tracked):** `tools/daily-reports/targets_2026.xlsx` (2026 monthly/quarterly targets),
  `tools/daily-reports/manual_inputs.json` (Nir's ~weekly spend inputs, keyed `YYYY-MM`).
- **Targets model** (`PLG targets` sheet, all literals - no formulas - so cells are safe to edit
  directly; `SLG targets` is quarterly by `Q1-2026`..`Q4-2026` columns):
  - **PLG New MRR** = row 11, column by anchor month. Updated 2026-08-04: **Q3 (Aug/Sep/Oct) is a flat
    $300,000 per month**, replacing the old ramp (474,417 / 519,007 / 566,369). July and earlier are
    untouched. Row 10 ("First MRR", un-seasonalized) is *not* what the builder reads.
  - **PLG Signups** = row 4, read directly (all-device, no factor). Added 2026-08-05: the channel report
    previously showed Signups with **no** target ("-"); it now carries one. The ROI report shows PLG as
    Current + MoM + WoW with no target column, so this change is channel-report-only.
  - **PLG Trials** = row 6 × 1.10 (mobile-app factor; row 6 is web-plan trials, the report shows total).
  - **Q3 funnel rebased to $300K (2026-08-05).** When New MRR was cut to $300K, only row 11 changed -
    signups (row 4) and trials (row 6) still held the old ramp calibrated to ~$540K first MRR (targets ran
    ~2× actuals). Aug/Sep/Oct rows 4-10 + 12 were rebuilt **bottoms-up from $300K holding CVR/ARPU flat at
    trailing-90d rollover actuals** (ARPU $27.52, Trial→Sub 59.7%, Signup→Trial 10.85%; ≈Q2, so not a
    one-month blip). Result, flat across the quarter: **Signups 168,295/mo · Trials 18,260/mo (shown) ·
    Subs ~10,900/mo**. Traffic (row 2) and first-visit CVR (row 3) were left as-is, so row 4 is now a
    bottoms-up MRR-driven target rather than traffic × CVR.
  - **Net MRR has NO target** (confirmed by Nir 2026-08-04). `net_tgt` is `None` and the report renders
    "-" for target/projection/attainment. It was previously *derived* as First-MRR-target × 0.5528
    (February's net-to-new ratio, 208,094 / 376,476) applied to every month - a figure nobody planned.
    Do not reinstate a derived Net MRR target; if Finance issues real monthly ones, read them from the sheet.
  - **SLG** unchanged: B2B Win MRR = `SLG targets` row 65 (Q3-2026 = $313,794, quarterly). Note this
    ~$300K quarterly SLG number is easy to confuse with the new $300K *monthly* PLG New MRR target.
- **Runtime (git-ignored):** report_values.json, roi_report_values.json (both under
  `tools/daily-reports/build/`), the built
  `*.html`, dated `Riverside_ROI_Report_<date>.html`, and `state/.delay_skip_*` markers.

## Data model

Snowflake via the Omni Snowflake MCP (`sql_exec_tool`), plus one monday read:

| Source | Used for |
|-------|----------|
| `analytics.bi.marketing_rollover` | PLG signups, trials, new subs, first MRR, and net-MRR deltas (expansion/reduction/churn/reactivation, stored signed) |
| `analytics.bi.sales_rollover` | SLG SQLs / pipeline / won by segment (Agency, EU, Enterprise), inbound only |
| `analytics.bi.daily_campaign_signup_attribution` | Paid spend by channel (MTD + trailing-30d) |
| monday "Invoices and Payments - Growth Marketing" board (`18390740532`) | Channel report's invoice-board spend lines (**Creative partnerships**, **Affiliates**, **Affiliate freelancers & platforms**, **B2B vendors**, **Other Growth Channels**) and the ROI report's **Invoice-board actuals** card, computed **every run** from the anchor month's group via `tools/daily-reports/build/spend_actuals.py` (added 2026-08-26; split by the board's Type column since 2026-10-04; attribution rules are canonical in `.claude/skills/invoice-board-spend-pulse/knowledge/config.md`) |

## Schedule & reliability

- **Runs on the LOCAL scheduler** (`refresh-daily-reports` in `~/.claude/scheduled-tasks/`, daily 10:50
  local time). **The cloud-routine migration was attempted and rolled back on 2026-08-13, same day:**
  the routine (`trig_01MHqmEdGVhTb7xjJAZcUdU6`, https://claude.ai/code/routines) is kept but **disabled**.
  Its proof run passed everything except the ROI hub deploy - the `rivermind` plugin never materializes
  in the cloud container (the container's installed_plugins.json stays `{"plugins":{}}` even though the account shows
  the plugin enabled), so `rivermind:analytics-hub-report-manager` and its bundled API token do not exist
  there, and the `enabled_plugins` field on the trigger is **silently ignored** by the update API (as is
  `sources.git_repository.branch`). Nir chose to switch back to local rather than run cloud with a
  failing hub deploy. Re-attempting the migration means solving plugin delivery first - either a working
  plugins toggle on the routine, or vendoring the hub-upload script with its token as a routine secret
  (never committed).
- **Never enable both schedulers at once** - they write the same artifact, the same hub report, and the
  same Notion log, so a double-run races on all three. **The two schedulers are separate lists**:
  `list_scheduled_tasks` shows only local tasks and will never show the routine (see
  `references/change-control.md`).
- **Cloud-routine requirements** (verified 2026-08-13; kept for the day the migration is retried):
  - Connectors attached: Snowflake, Slack, Notion.
  - `allowed_tools` **must list `Artifact` explicitly** - it is *not* in `preset:default`, and without it
    the channel-report deploy fails while the rest of the run appears to succeed. `Skill` must also be
    present (needed for the ROI hub deploy); it *is* in the default preset, but hand-writing the list
    without it silently removes it.
  - The `branch` field on `sources.git_repository` is **ignored** - the routine always clones `main`.
    Any recipe change must merge to `main` before it takes effect.
  - `openpyxl` is not guaranteed in the cloud image; the prompt preflights the import and installs it.
- ⚠️ **Resolved 2026-08-13 by live run - the ROI hub deploy does NOT work in cloud.** The proof run
  (session `cse_01AjCWYD2KawnztkCMt3BuZz`) confirmed `rivermind:analytics-hub-report-manager` never
  resolves in the routine container: the plugin is account-delivered per session, the container's
  installed_plugins.json is empty, and no skill, script, or bundled token exists there. The run failed
  the hub deploy loudly (as the prompt requires) and deployed everything else correctly, including a
  clean unattended reproduction of the corrected EU split. This failure is why the migration was rolled
  back - see the Schedule section above for the two candidate fixes before any retry.
- **Delay gate:** if `#data` posts "today's data refresh is delayed", the run is skipped and Nir gets a
  Slack DM saying the reports were not refreshed. There is **no automatic retry** - the 12:40
  `refresh-daily-reports-retry` task was retired 2026-07-28 (it fired daily but was a no-op on virtually
  every run, since delays are rare). A delayed day is recovered by running the refresh manually once
  `#data` clears.
- **Hard gates:** if the Snowflake MCP is unavailable, the run **aborts** - it never fabricates data or
  deploys a stale surface. A report is never shipped older than the latest complete day.
- **monday is a soft dependency (added 2026-08-26):** the channel report's Growth Channels and Creative
  partnerships lines are pulled live from the Invoices board each run (recipe Step 5). If the monday
  connector is missing from the runner's session, or the board query or `tools/daily-reports/build/spend_actuals.py`
  fails, the run does **not** abort - it falls back to `tools/daily-reports/manual_inputs.json` for those
  two lines and flags the staleness in the run summary. The runner's account needs the monday connector
  for the live pull.

## Gotchas

- **The report will read lower than live Omni dashboards intraday - that is correct, not a bug.** Both
  read the same Snowflake tables; the report cuts off at the last complete day (the anchor) while a
  dashboard shows the quarter up to this minute, which includes (a) SQLs created today, still
  accumulating, and (b) SQLs stamped with **future** dates - since March 2025 an SQL's `sql_created_date`
  is its intro-*meeting* date, so a meeting booked for next week already sits in the data. Verified
  2026-08-13: dashboard `0068a9a5` read Agency 144 / EU 53 / Ent 13 vs the report's 143 / 47 / 12, and
  the gap decomposed exactly into 6 same-day + 2 future-dated SQLs. Healthy invariant: dashboard ≥
  report during the day; a dashboard reading *below* the report is the actual anomaly.

- **A day-stale report is the quiet failure mode - the anchor rule will not catch it (2026-08-29).**
  The anchor is "most recent `date_day` with `signups > 0`", so when yesterday has not loaded yet the
  rule silently returns the day before and the run looks clean all the way through: the build's anchor
  sanity check passes (it only verifies the HTML matches the anchor you *passed*), both deploys succeed,
  and the summary reads normal. Nothing downstream of Step 2 can detect it. The only guard is the
  explicit `anchor == CURRENT_DATE - 1` comparison now in the recipe's Step 2 - take `expected_anchor`
  from Snowflake, not the runner's clock. **A loading day looks like `signups = 0` with non-zero
  `all_rows`**, and it can finish loading mid-run: on 2026-08-29, Aug 28 was empty at anchor time and
  had 4,856 signups twenty minutes later. If you spot it after deploying, re-run from Step 2 and
  redeploy - both surfaces overwrite in place, so there is no stale copy to clean up.

- **`tools/daily-reports/manual_inputs.json` is the fallback, not the source, for the two invoice lines
  (since 2026-08-26).** `growth_channels_spend` and `creative_partnerships_spend` are computed live from
  the Invoices board on every run; this file covers them only when the board pull fails, so keep those
  two roughly current with an as-of date in the month's `_note`. `seo_spend` and `slg_arr` still come
  from here every run. Keyed by month (`YYYY-MM`); a missing anchor month falls back to budget-prorated
  figures per the recipe, never a silent carry-forward.
- **The two reports handle spend inputs differently:** the channel report prices its invoice-board lines
  into its ROI (fallback `tools/daily-reports/manual_inputs.json`); the ROI report's ROI uses fixed
  `budgets_monthly` in its values JSON and derives SLG ARR from targets, and shows the same invoice-board
  split only as a separate card outside that ROI. Don't conflate them.
- **Type decides the line, payer decides the scope (2026-10-04).** Savion pays for both Creator Marketing
  and Growth Channels since Dor left, so the payer alone cannot separate them; the board's Type column
  does. If affiliate spend lands in Creative partnerships again, check the item's Type on the board first:
  a blank or `Creators` Type is a filing gap for the board owner, not a script bug.
- **New spend channel** in `daily_campaign_signup_attribution` → add it under its own key and call it out
  in the run summary; the channel-name→key map lives in the recipe (Q6).
- **Retired surface:** the old claude.ai ROI artifact `371dbe5d-…` has not been refreshed since
  2026-07-08. The Analytics Hub is the ROI report's only live surface.
- **Legacy scripts left behind:** the original `~/Downloads/daily_report_scripts/` also held one-off
  generators - gen_html_report.py, gen_pdf_final.py, run_full_report.py, q1_plg_report.py and
  mcp_to_csv.py - that are **not** part of the daily flow and were intentionally not migrated. Names are
  deliberately unquoted: they do not exist in this repo, and backticking them makes
  `scripts/lint_references.py` read them as repo files and fail the build.

## History

Originally lived entirely in `~/Downloads/daily_report_scripts/` (untracked, hardcoded absolute paths)
and ran as two separate cold routines 15 minutes apart, each re-finding the anchor and re-reading `#data`.
Migrated into the repo and unified into a single daily run (one anchor, one gate, one query set → both
reports) in July 2026.

## Related

- [Marketing Operating Model](../reference/marketing-operating-model.md) - the analytics team's daily
  funnel report we consume (do not confuse), the OO data model, and Snowflake rollover tables.
- [Rivermind](../reference/rivermind.md) - the Analytics Hub host and the `analytics-hub-report-manager`
  skill used to push the ROI report.
- [Omni BI](omni-bi.md) - our maintained BI dashboards.

## Verifying a builder change (added 2026-09-15)

The channel report is a claude.ai artifact behind login, and the in-app Browser pane is not signed in
to claude.ai (and never should be handed credentials). A session that started as a scheduled task is
also flagged unattended, so `preview_start` refuses to launch a dev server. What works in both cases:
wrap the built file in a doctype/head skeleton (mirrors what the artifact wrapper adds, so quirks mode
cannot skew the CSS) and open it with a `file://` URL in the in-app pane - the JS runs, `find` /
`read_page` / `form_input` / `get_page_text` all work, and console errors are readable. Screenshots
come back black while the pane is hidden; read the page as text instead. The wrapper lives at
`tools/daily-reports/build/preview_wrapper.html` (git-ignored with the other build HTML) and is
rebuilt by hand - it is not part of `daily_build.sh`. When a person is present,
`.claude/launch.json` also has a `daily-report-preview` static server for the build folder.
