# Refresh recipe - Riverside daily reports (unified)

Rebuilds **both** daily reports from one cold run, one anchor, one data pull:

| Report | Builder | Live surface |
|--------|---------|--------------|
| PLG channel-detail | `build/build_artifact.py` | claude.ai artifact `0b9eef24-e1a7-4e3c-b145-f666fa97a7c8` |
| ROI & Growth | `build/build_roi_artifact.py` | Analytics Hub report `de39972a29cf46f3bbb57fac09833214` (Marketing/Reports) |

Everything the channel report needs is a **subset** of the ROI query set except its per-channel
breakdown, so this recipe runs the ROI queries once plus one extra per-channel query, then feeds both
builders. This replaces the two old recipes (`refresh_artifact/REFRESH.md`, `REFRESH_ROI.md`) that ran
as two separate cold sessions 15 minutes apart.

**Paths.** Every path below is written **relative to the repo root**, so the same recipe works on a
local machine and in a cloud routine (which clones the repo to its own directory). Resolve `<REPO>`
once at the start of the run and prefix it:
- Local: `<REPO>` = `/Users/nirtaranto/Documents/Claude/marketing-brain`
- Cloud routine: `<REPO>` = the checkout root (usually the working directory the session starts in)

| What | Path (from repo root) |
|---|---|
| Build dir | `tools/daily-reports/build/` |
| Wrapper | `tools/daily-reports/build/daily_build.sh` |
| Targets workbook | `tools/daily-reports/targets_2026.xlsx` |
| Manual inputs | `tools/daily-reports/manual_inputs.json` |
| State/markers | `tools/daily-reports/state/` |

- `daily_build.sh` starts with `cd "$(dirname "$0")"`, so it can be invoked from any working directory -
  pass it whatever absolute-or-relative path reaches the script and it finds its own siblings.
- `build_roi_artifact.py` imports `compute_params()` from `build_artifact.py`; keep both in `build/`.
- Requires Python 3 with `openpyxl` (reads the targets workbook). **In a cloud routine, verify the import
  before doing anything else** (`python3 -c "import openpyxl"`) and `pip install openpyxl` if it is
  missing - the cloud image is not guaranteed to carry it and the failure would otherwise surface only
  after all eight Snowflake queries have run.

---

## Step 0 - Data-refresh delay gate (do this FIRST, once for both reports)
Check the Slack `#data` channel for any message posted TODAY (local date) whose text contains
`Heads up: today's data refresh is delayed`. Resolve the channel with `slack_search_channels` for
"data", read recent messages with `slack_read_channel`, keep only messages dated today.
- **No such message today:** continue to Step 1. (If any stale `../state/.delay_skip_*` marker exists from
  the retired retry task, delete it - nothing writes these any more.)
- **A delay message today, and a LATER message today says it is resolved:** continue to Step 1 and say so
  in the run summary (`delay flagged HH:MM, resolved HH:MM, ran`). A resolution is a human or bot message
  posted **after** the delay message, same day, in `#data` or its thread, saying the issue is handled -
  "issue resolved", "fixed", "data is up to date", "all data is up to date", "handled". Read the thread on
  the delay message (`slack_read_thread`), not just the channel surface: the resolution is often a reply
  there rather than a top-level post. The Step 2 staleness gate is what actually clears the data - if the
  anchor still lags, Step 2 stops the run on its own, which is the intended division of labour.
  A resolution that only promises a future fix ("looking into it", "will update", "will let you know when
  the data is updated") is **not** a resolution - it names no completed action. Treat it as unresolved.
  Added 2026-09-15 on Nir's ruling, after a run skipped a day whose delay had been resolved 46 minutes
  later and whose anchor was fully loaded. The old rule read the delay message alone and could not be
  talked out of a skip by any amount of good news.
- **A delay message today with no resolution after it:** do NOT run the refresh and do NOT deploy. Alert
  Nir with a Slack DM (find him by `nir.taranto@riverside.fm` via `slack_search_users`, then
  `slack_send_message` to that DM):
  "Heads up: the Riverside daily reports were NOT refreshed today - the data refresh in #data is delayed.
  Re-run `/refresh-daily-reports` once it clears." End with the summary
  `Skipped: today's data refresh is delayed per #data; Nir DM'd` and STOP.
  There is no automatic retry - the 12:40 retry task was removed on 2026-07-28 because it was a no-op
  on virtually every run. A delayed day is refreshed by re-running this recipe manually.
- **`#data` check itself cannot run** (Slack tool/channel unavailable): note it in the summary and
  continue - the Snowflake gate below still protects against bad data.

**What this gate is and is not.** It is a coarse early exit that saves eight queries and a deploy when the
warehouse is known-broken. It is **not** the data-correctness check - Step 2 is. So a resolved delay hands
the decision to Step 2 rather than overriding it, and an unresolved delay stops the run even when the
anchor looks fine, because the feature-store break that triggers these alerts can leave signups healthy
while the MRR models are still wrong (seen 2026-08-31: $39k of phantom churn with normal signup volume).

## Step 1 - Snowflake HARD GATE
Confirm the Snowflake MCP `sql_exec_tool` is loadable (search `omni snowflake sql_exec` / load
`mcp__21692eba-baf7-4d51-a758-980bc61e6b7e__sql_exec_tool`). If Snowflake is NOT available, **ABORT** -
do not fabricate data, do not deploy either surface; report the connector is off and stop.

## Step 2 - Find the latest complete day (anchor) - once
```sql
SELECT date_day,
       COUNT(DISTINCT CASE WHEN metric='sign_up' THEN id END) AS signups,
       COUNT(*)                                               AS all_rows,
       MAX(DATEADD('day',-1,CURRENT_DATE))                    AS expected_anchor
FROM analytics.bi.marketing_rollover
WHERE date_day >= DATEADD('day',-6,CURRENT_DATE)
GROUP BY 1 ORDER BY 1;
```
Anchor = most recent `date_day` with `signups > 0` (today is always incomplete).

**STALENESS HARD GATE - compare, never eyeball.** `expected_anchor` is Snowflake's own
`CURRENT_DATE - 1`; use it, not the runner's local clock or the shape of the result window.

- `anchor == expected_anchor` → continue to Step 3.
- `anchor < expected_anchor` → **do NOT deploy either surface.** Yesterday has not landed. DM Nir
  (`nir.taranto@riverside.fm` via `slack_search_users` → `slack_send_message`): "Heads up: the Riverside
  daily reports were NOT refreshed today - yesterday (`<expected_anchor>`) is not in
  `marketing_rollover` yet. Re-run once it lands." End with the summary
  `Skipped: <expected_anchor> rollover not loaded; Nir DM'd` and STOP. There is no retry task - a
  skipped day is refreshed by re-running this recipe manually.

Shipping the day before yesterday is the failure this gate exists to stop. **The anchor rule alone will
not catch it**: "most recent day with `signups > 0`" happily returns the day before when yesterday is
empty, which reads like a clean run and deploys a day-stale report to both surfaces. The comparison
above is what makes the miss visible - do it explicitly and state both dates in the run summary.

**Yesterday can be mid-load, and it can finish loading during your run (seen 2026-08-29).** A day that
is loading shows up as `signups = 0` with a **non-zero `all_rows`** - rows are arriving but the
`sign_up` metric has not landed. Treat that as "not ready", not as "a real zero-signup day". Two
consequences worth knowing:
- A run that starts before the load finishes sees an empty yesterday even though the data is minutes
  away. That is a legitimate skip; re-run manually rather than deploying the older day.
- If you have already deployed and then notice yesterday has appeared, **re-run the whole recipe from
  Step 2 for the correct anchor and redeploy both surfaces.** Both deploys overwrite in place, so a
  corrected re-run is cheap and leaves no stale copy behind.

## Step 3 - Get windows/targets for the anchor - once (local, cheap)
Run this ONE command with the absolute path - no `cd`, no `&&` chaining - so it stays a single
allow-once command (the wrapper `cd`s into the build dir itself):
```
bash <REPO>/tools/daily-reports/build/daily_build.sh plan <ANCHOR>
```
It prints the channel windows, then the ROI windows. Use the printed windows verbatim in the queries below. The ROI plan's `RANGE_START` = earliest of
`prev_month_window[0]`, `prev_week_window[0]`, `rollover_window[0]` - the lower bound for the PLG queries.
Do not hand-compute windows.

## Step 4 - Run the unified query set (substitute the windows from Step 3)

**Q1 - PLG by channel** (yesterday + MTD + prior-month same window). *Channel report only.*
```sql
SELECT COALESCE(channel_group,'Unknown') AS channel,
 COUNT(DISTINCT CASE WHEN metric='sign_up' AND date_day='<ANCHOR>' THEN id END) AS y_signups,
 COUNT(DISTINCT CASE WHEN metric='trial'   AND date_day='<ANCHOR>' THEN id END) AS y_trials,
 ROUND(SUM(CASE WHEN metric='new_subscription' AND date_day='<ANCHOR>' THEN first_mrr END),0) AS y_first_mrr,
 COUNT(DISTINCT CASE WHEN metric='sign_up' AND date_day BETWEEN '<CURM_START>' AND '<ANCHOR>' THEN id END) AS m_signups,
 COUNT(DISTINCT CASE WHEN metric='trial'   AND date_day BETWEEN '<CURM_START>' AND '<ANCHOR>' THEN id END) AS m_trials,
 ROUND(SUM(CASE WHEN metric='new_subscription' AND date_day BETWEEN '<CURM_START>' AND '<ANCHOR>' THEN first_mrr END),0) AS m_first_mrr,
 COUNT(DISTINCT CASE WHEN metric='sign_up' AND date_day BETWEEN '<PREVM_START>' AND '<PREVM_END>' THEN id END) AS pm_signups,
 COUNT(DISTINCT CASE WHEN metric='trial'   AND date_day BETWEEN '<PREVM_START>' AND '<PREVM_END>' THEN id END) AS pm_trials,
 ROUND(SUM(CASE WHEN metric='new_subscription' AND date_day BETWEEN '<PREVM_START>' AND '<PREVM_END>' THEN first_mrr END),0) AS pm_first_mrr
FROM analytics.bi.marketing_rollover
WHERE date_day BETWEEN '<PREVM_START>' AND '<ANCHOR>'
GROUP BY 1 HAVING m_signups>0 OR pm_signups>0 ORDER BY m_trials DESC;
```
→ `plg_channel_rows` in order: `[channel, y_signups, y_trials, y_first_mrr, m_signups, m_trials, m_first_mrr, pm_signups, pm_trials, pm_first_mrr]`.
This still feeds the header pulse + Key Insights; keep it.

**Q1b - PLG per-channel detail** across all windows the redesigned channel table needs. *Channel report only.*
Window placeholders map to the channel `plan` keys: `CURM0/ANCHOR`=`cur_month_window`, `PREVM0/PREVM1`=`prev_month_window`,
`CURW0/ANCHOR`=`cur_week_window`, `PREVW0/PREVW1`=`prev_week_window`, `CURQ0`=`cur_q_window[0]`,
`PREVQF0/PREVQF1`=`prev_q_full_window`, `R7_0`=`last7_window[0]`, `PR7_0/PR7_1`=`prev7_window`,
`R14_0`=`last14_window[0]`, `PR14_0/PR14_1`=`prev14_window` (the channel plan prints all of them since
2026-09-06). Counts are `COUNT(DISTINCT id)`; First MRR is `SUM(first_mrr)` on new subs.
```sql
SELECT COALESCE(channel_group,'unknown') AS channel,
 COUNT(DISTINCT CASE WHEN metric='sign_up'          AND date_day BETWEEN '<CURM0>'  AND '<ANCHOR>'  THEN id END) AS m_su,
 COUNT(DISTINCT CASE WHEN metric='trial'            AND date_day BETWEEN '<CURM0>'  AND '<ANCHOR>'  THEN id END) AS m_tr,
 COUNT(DISTINCT CASE WHEN metric='new_subscription' AND date_day BETWEEN '<CURM0>'  AND '<ANCHOR>'  THEN id END) AS m_sub,
 ROUND(SUM(CASE WHEN metric='new_subscription'      AND date_day BETWEEN '<CURM0>'  AND '<ANCHOR>'  THEN first_mrr END),0) AS m_fmrr,
 COUNT(DISTINCT CASE WHEN metric='sign_up'          AND date_day BETWEEN '<PREVM0>' AND '<PREVM1>'  THEN id END) AS pm_su,
 COUNT(DISTINCT CASE WHEN metric='trial'            AND date_day BETWEEN '<PREVM0>' AND '<PREVM1>'  THEN id END) AS pm_tr,
 COUNT(DISTINCT CASE WHEN metric='new_subscription' AND date_day BETWEEN '<PREVM0>' AND '<PREVM1>'  THEN id END) AS pm_sub,
 ROUND(SUM(CASE WHEN metric='new_subscription'      AND date_day BETWEEN '<PREVM0>' AND '<PREVM1>'  THEN first_mrr END),0) AS pm_fmrr,
 COUNT(DISTINCT CASE WHEN metric='sign_up'          AND date_day BETWEEN '<CURW0>'  AND '<ANCHOR>'  THEN id END) AS w_su,
 COUNT(DISTINCT CASE WHEN metric='trial'            AND date_day BETWEEN '<CURW0>'  AND '<ANCHOR>'  THEN id END) AS w_tr,
 COUNT(DISTINCT CASE WHEN metric='new_subscription' AND date_day BETWEEN '<CURW0>'  AND '<ANCHOR>'  THEN id END) AS w_sub,
 ROUND(SUM(CASE WHEN metric='new_subscription'      AND date_day BETWEEN '<CURW0>'  AND '<ANCHOR>'  THEN first_mrr END),0) AS w_fmrr,
 COUNT(DISTINCT CASE WHEN metric='sign_up'          AND date_day BETWEEN '<PREVW0>' AND '<PREVW1>'  THEN id END) AS pw_su,
 COUNT(DISTINCT CASE WHEN metric='trial'            AND date_day BETWEEN '<PREVW0>' AND '<PREVW1>'  THEN id END) AS pw_tr,
 COUNT(DISTINCT CASE WHEN metric='new_subscription' AND date_day BETWEEN '<PREVW0>' AND '<PREVW1>'  THEN id END) AS pw_sub,
 ROUND(SUM(CASE WHEN metric='new_subscription'      AND date_day BETWEEN '<PREVW0>' AND '<PREVW1>'  THEN first_mrr END),0) AS pw_fmrr,
 COUNT(DISTINCT CASE WHEN metric='trial'            AND date_day BETWEEN '<CURQ0>'  AND '<ANCHOR>'  THEN id END) AS q_tr,
 ROUND(SUM(CASE WHEN metric='new_subscription'      AND date_day BETWEEN '<CURQ0>'  AND '<ANCHOR>'  THEN first_mrr END),0) AS q_fmrr,
 COUNT(DISTINCT CASE WHEN metric='trial'            AND date_day BETWEEN '<PREVQF0>' AND '<PREVQF1>' THEN id END) AS pq_tr,
 ROUND(SUM(CASE WHEN metric='new_subscription'      AND date_day BETWEEN '<PREVQF0>' AND '<PREVQF1>' THEN first_mrr END),0) AS pq_fmrr,
 COUNT(DISTINCT CASE WHEN metric='sign_up'          AND date_day='<ANCHOR>' THEN id END) AS d_su,
 COUNT(DISTINCT CASE WHEN metric='trial'            AND date_day='<ANCHOR>' THEN id END) AS d_tr,
 COUNT(DISTINCT CASE WHEN metric='new_subscription' AND date_day='<ANCHOR>' THEN id END) AS d_sub,
 ROUND(SUM(CASE WHEN metric='new_subscription'      AND date_day='<ANCHOR>' THEN first_mrr END),0) AS d_fmrr,
 COUNT(DISTINCT CASE WHEN metric='sign_up'          AND date_day='<PREVW1>' THEN id END) AS pd_su,
 COUNT(DISTINCT CASE WHEN metric='trial'            AND date_day='<PREVW1>' THEN id END) AS pd_tr,
 COUNT(DISTINCT CASE WHEN metric='new_subscription' AND date_day='<PREVW1>' THEN id END) AS pd_sub,
 ROUND(SUM(CASE WHEN metric='new_subscription'      AND date_day='<PREVW1>' THEN first_mrr END),0) AS pd_fmrr,
 COUNT(DISTINCT CASE WHEN metric='sign_up'          AND date_day BETWEEN '<R7_0>'   AND '<ANCHOR>' THEN id END) AS r7_su,
 COUNT(DISTINCT CASE WHEN metric='trial'            AND date_day BETWEEN '<R7_0>'   AND '<ANCHOR>' THEN id END) AS r7_tr,
 COUNT(DISTINCT CASE WHEN metric='new_subscription' AND date_day BETWEEN '<R7_0>'   AND '<ANCHOR>' THEN id END) AS r7_sub,
 ROUND(SUM(CASE WHEN metric='new_subscription'      AND date_day BETWEEN '<R7_0>'   AND '<ANCHOR>' THEN first_mrr END),0) AS r7_fmrr,
 COUNT(DISTINCT CASE WHEN metric='sign_up'          AND date_day BETWEEN '<PR7_0>'  AND '<PR7_1>'  THEN id END) AS pr7_su,
 COUNT(DISTINCT CASE WHEN metric='trial'            AND date_day BETWEEN '<PR7_0>'  AND '<PR7_1>'  THEN id END) AS pr7_tr,
 COUNT(DISTINCT CASE WHEN metric='new_subscription' AND date_day BETWEEN '<PR7_0>'  AND '<PR7_1>'  THEN id END) AS pr7_sub,
 ROUND(SUM(CASE WHEN metric='new_subscription'      AND date_day BETWEEN '<PR7_0>'  AND '<PR7_1>'  THEN first_mrr END),0) AS pr7_fmrr,
 COUNT(DISTINCT CASE WHEN metric='sign_up'          AND date_day BETWEEN '<R14_0>'  AND '<ANCHOR>' THEN id END) AS r14_su,
 COUNT(DISTINCT CASE WHEN metric='trial'            AND date_day BETWEEN '<R14_0>'  AND '<ANCHOR>' THEN id END) AS r14_tr,
 COUNT(DISTINCT CASE WHEN metric='new_subscription' AND date_day BETWEEN '<R14_0>'  AND '<ANCHOR>' THEN id END) AS r14_sub,
 ROUND(SUM(CASE WHEN metric='new_subscription'      AND date_day BETWEEN '<R14_0>'  AND '<ANCHOR>' THEN first_mrr END),0) AS r14_fmrr,
 COUNT(DISTINCT CASE WHEN metric='sign_up'          AND date_day BETWEEN '<PR14_0>' AND '<PR14_1>' THEN id END) AS pr14_su,
 COUNT(DISTINCT CASE WHEN metric='trial'            AND date_day BETWEEN '<PR14_0>' AND '<PR14_1>' THEN id END) AS pr14_tr,
 COUNT(DISTINCT CASE WHEN metric='new_subscription' AND date_day BETWEEN '<PR14_0>' AND '<PR14_1>' THEN id END) AS pr14_sub,
 ROUND(SUM(CASE WHEN metric='new_subscription'      AND date_day BETWEEN '<PR14_0>' AND '<PR14_1>' THEN first_mrr END),0) AS pr14_fmrr
FROM analytics.bi.marketing_rollover
WHERE date_day BETWEEN '<PREVQF0>' AND '<ANCHOR>'
GROUP BY 1 HAVING m_su>0 OR pm_su>0 OR pq_tr>0 ORDER BY q_fmrr DESC NULLS LAST;
```
The `d_*`/`pd_*` pair feeds the table's **Daily** view: anchor day vs the same weekday last week - and
`<PREVW1>` (= prev_week_window[1]) is exactly anchor−7, so no extra window is needed. The `r7_*`/`pr7_*`
and `r14_*`/`pr14_*` blocks (added 2026-09-06) feed the **7d** and **14d** views: the last 7 / 14 complete
days ending at the anchor vs the 7 / 14 days immediately before. They ignore the calendar week, which is
the point - WoW on a Saturday anchor compares six elapsed days, 7d always compares a full span. `<PR14_0>`
is anchor−27, well inside the `<PREVQF0>` lower bound of the WHERE clause.
→ `plg_channel_detail`, one row per channel in this exact field order, **45 fields** (nulls → 0):
`[channel, m_su,m_tr,m_sub,m_fmrr, pm_su,pm_tr,pm_sub,pm_fmrr, w_su,w_tr,w_sub,w_fmrr, pw_su,pw_tr,pw_sub,pw_fmrr, q_tr,q_fmrr, pq_tr,pq_fmrr, d_su,d_tr,d_sub,d_fmrr, pd_su,pd_tr,pd_sub,pd_fmrr, r7_su,r7_tr,r7_sub,r7_fmrr, pr7_su,pr7_tr,pr7_sub,pr7_fmrr, r14_su,r14_tr,r14_sub,r14_fmrr, pr14_su,pr14_tr,pr14_sub,pr14_fmrr]`.
A 29-field row (pre-2026-09-06) still builds; the 7d/14d toggles then print "fields missing from this build" in the caption rather than zeros.
In the first month of a quarter, QTD == MTD (so `q_tr==m_tr`, `q_fmrr==m_fmrr`) - that's expected, not a bug.
Channel grouping (Paid / Partnerships / Affiliates) and the Q3 attainment are computed inside the
builder's template - the query stays flat per `channel_group`. **Channel targets are NEVER derived from
history**: they come from the `CHANNEL_Q_TARGETS` constant in `build_artifact.py`, hand-copied from the
quarter plan (Q3 2026: artifact `34ed9a9f-c6c4-4da1-8270-d542fd13ba1e`). When a new quarter starts and no
plan entry exists yet, the table shows "-" for share/attainment - flag it in the run summary and ask Nir
for the plan; do not substitute a computed split. (`pq_tr`/`pq_fmrr` stay in the query for context only.)

**Q2 - PLG high-level counts** across four windows (month + week, cur + prev). *ROI report. Independent
conditional aggregates - the windows overlap, do NOT use a single first-match CASE.*
```sql
SELECT 'signups' AS metric,
  COUNT(DISTINCT CASE WHEN metric='sign_up' AND date_day BETWEEN '<CURM0>'  AND '<ANCHOR>' THEN id END) AS cur_m,
  COUNT(DISTINCT CASE WHEN metric='sign_up' AND date_day BETWEEN '<PREVM0>' AND '<PREVM1>' THEN id END) AS prev_m,
  COUNT(DISTINCT CASE WHEN metric='sign_up' AND date_day BETWEEN '<CURW0>'  AND '<ANCHOR>' THEN id END) AS cur_w,
  COUNT(DISTINCT CASE WHEN metric='sign_up' AND date_day BETWEEN '<PREVW0>' AND '<PREVW1>' THEN id END) AS prev_w
FROM analytics.bi.marketing_rollover WHERE date_day BETWEEN '<RANGE_START>' AND '<ANCHOR>'
UNION ALL SELECT 'trials',
  COUNT(DISTINCT CASE WHEN metric='trial' AND date_day BETWEEN '<CURM0>'  AND '<ANCHOR>' THEN id END),
  COUNT(DISTINCT CASE WHEN metric='trial' AND date_day BETWEEN '<PREVM0>' AND '<PREVM1>' THEN id END),
  COUNT(DISTINCT CASE WHEN metric='trial' AND date_day BETWEEN '<CURW0>'  AND '<ANCHOR>' THEN id END),
  COUNT(DISTINCT CASE WHEN metric='trial' AND date_day BETWEEN '<PREVW0>' AND '<PREVW1>' THEN id END)
FROM analytics.bi.marketing_rollover WHERE date_day BETWEEN '<RANGE_START>' AND '<ANCHOR>'
UNION ALL SELECT 'new_subs',
  COUNT(DISTINCT CASE WHEN metric='new_subscription' AND date_day BETWEEN '<CURM0>'  AND '<ANCHOR>' THEN id END),
  COUNT(DISTINCT CASE WHEN metric='new_subscription' AND date_day BETWEEN '<PREVM0>' AND '<PREVM1>' THEN id END),
  COUNT(DISTINCT CASE WHEN metric='new_subscription' AND date_day BETWEEN '<CURW0>'  AND '<ANCHOR>' THEN id END),
  COUNT(DISTINCT CASE WHEN metric='new_subscription' AND date_day BETWEEN '<PREVW0>' AND '<PREVW1>' THEN id END)
FROM analytics.bi.marketing_rollover WHERE date_day BETWEEN '<RANGE_START>' AND '<ANCHOR>';
```
→ `plg_hl.signups/.trials/.new_subs` = `{cur_m, prev_m, cur_w, prev_w}`.

**Q3 - PLG MRR sums** (first MRR + net MRR) across the same four windows. *ROI report; also supplies the
channel report's Net MRR.* Net = new-sub `first_mrr` + expansion + reduction + churn + reactivation (signed).
```sql
SELECT 'first_mrr' AS metric,
  ROUND(SUM(CASE WHEN metric='new_subscription' AND date_day BETWEEN '<CURM0>'  AND '<ANCHOR>' THEN first_mrr END),0) AS cur_m,
  ROUND(SUM(CASE WHEN metric='new_subscription' AND date_day BETWEEN '<PREVM0>' AND '<PREVM1>' THEN first_mrr END),0) AS prev_m,
  ROUND(SUM(CASE WHEN metric='new_subscription' AND date_day BETWEEN '<CURW0>'  AND '<ANCHOR>' THEN first_mrr END),0) AS cur_w,
  ROUND(SUM(CASE WHEN metric='new_subscription' AND date_day BETWEEN '<PREVW0>' AND '<PREVW1>' THEN first_mrr END),0) AS prev_w
FROM analytics.bi.marketing_rollover WHERE date_day BETWEEN '<RANGE_START>' AND '<ANCHOR>'
UNION ALL SELECT 'net_mrr',
  ROUND(SUM(CASE WHEN date_day BETWEEN '<CURM0>'  AND '<ANCHOR>' THEN COALESCE(CASE WHEN metric='new_subscription' THEN first_mrr END,0)+COALESCE(expansion_delta_mrr,0)+COALESCE(reduction_delta_mrr,0)+COALESCE(churned_mrr,0)+COALESCE(reactivation_mrr,0) END),0),
  ROUND(SUM(CASE WHEN date_day BETWEEN '<PREVM0>' AND '<PREVM1>' THEN COALESCE(CASE WHEN metric='new_subscription' THEN first_mrr END,0)+COALESCE(expansion_delta_mrr,0)+COALESCE(reduction_delta_mrr,0)+COALESCE(churned_mrr,0)+COALESCE(reactivation_mrr,0) END),0),
  ROUND(SUM(CASE WHEN date_day BETWEEN '<CURW0>'  AND '<ANCHOR>' THEN COALESCE(CASE WHEN metric='new_subscription' THEN first_mrr END,0)+COALESCE(expansion_delta_mrr,0)+COALESCE(reduction_delta_mrr,0)+COALESCE(churned_mrr,0)+COALESCE(reactivation_mrr,0) END),0),
  ROUND(SUM(CASE WHEN date_day BETWEEN '<PREVW0>' AND '<PREVW1>' THEN COALESCE(CASE WHEN metric='new_subscription' THEN first_mrr END,0)+COALESCE(expansion_delta_mrr,0)+COALESCE(reduction_delta_mrr,0)+COALESCE(churned_mrr,0)+COALESCE(reactivation_mrr,0) END),0)
FROM analytics.bi.marketing_rollover WHERE date_day BETWEEN '<RANGE_START>' AND '<ANCHOR>';
```
→ ROI: `plg_hl.first_mrr/.net_mrr` = `{cur_m, prev_m, cur_w, prev_w}`.
→ Channel: `plg_totals.cur.net = net_mrr.cur_m`, `plg_totals.prior.net = net_mrr.prev_m` (no separate query).

**Q4 - New-subscriber breakdown** (billing period + plan, MTD vs same window last month). *ROI report.*
```sql
SELECT CASE WHEN recurring_interval='year' THEN 'Yearly' ELSE 'Monthly' END AS billing,
  CASE WHEN product_group ILIKE 'Pro%' THEN 'Pro' WHEN product_group='Mobile Plus' THEN 'Mobile Plus'
       WHEN product_group='Grow' THEN 'Grow' WHEN product_group='Webinar' THEN 'Webinar' ELSE 'Other' END AS plan,
  COUNT(DISTINCT CASE WHEN date_day BETWEEN '<CURM0>'  AND '<ANCHOR>' THEN id END) AS cur_m,
  COUNT(DISTINCT CASE WHEN date_day BETWEEN '<PREVM0>' AND '<PREVM1>' THEN id END) AS prev_m
FROM analytics.bi.marketing_rollover
WHERE metric='new_subscription' AND date_day BETWEEN '<PREVM0>' AND '<ANCHOR>'
GROUP BY 1,2 ORDER BY 1,2;
```
→ `subs_breakdown.billing` = `[[Yearly,cur,prev],[Monthly,cur,prev]]`,
   `subs_breakdown.plan` = `[[Pro,…],[Mobile Plus,…],[Grow,…],[Webinar,…],[Other,…]]`. Each row `[name, cur_m, prev_m]`.

**Q5 - SLG by segment, inbound** (current quarter-to-date vs prior quarter same fiscal day). *Shared -
run once, feed both reports.*

`sql_pipeline` has exactly four values, all stable since 2023:
`Pre-Opp - US Agency`, `Pre-Opp - US Enterprise`, `Pre-Opp - EU Agency`, `Pre-Opp - EU Enterprise`.
The three report segments map as: **EU = both EU pipelines aggregated** (region-level segment),
**Agency = US Agency only**, **Enterprise = US Enterprise only**. Match the pipeline names exactly -
do NOT reintroduce loose `%Agency%` / `%Enterprise%` / `%Europe%` patterns (see the fixed-bug note below).
```sql
SELECT CASE WHEN quarter_name='<CURQ_LABEL>' THEN 'cur' ELSE 'prior' END AS q,
 CASE WHEN sql_pipeline ILIKE 'Pre-Opp - EU%'           THEN 'EU'
      WHEN sql_pipeline ILIKE 'Pre-Opp - US Agency'     THEN 'Agency'
      WHEN sql_pipeline ILIKE 'Pre-Opp - US Enterprise' THEN 'Enterprise' END AS seg,
 COUNT(DISTINCT CASE WHEN metric='sql' THEN id END) AS sqls,
 ROUND(SUM(CASE WHEN metric='deal'     THEN deal_amount END),0) AS pipe,
 ROUND(SUM(CASE WHEN metric='won_deal' THEN deal_amount END),0) AS won
FROM analytics.bi.sales_rollover
WHERE last_touch_source='Inbound' AND (
  (quarter_name='<CURQ_LABEL>'  AND timestamp::date BETWEEN '<CURQ0>'  AND '<ANCHOR>')
  OR (quarter_name='<PREVQ_LABEL>' AND timestamp::date BETWEEN '<PREVQ0>' AND '<PREVQ1>'))
GROUP BY 1,2 ORDER BY 1,2;
```
→ `slg.cur/.prior.{Agency,EU,Enterprise}.{sqls,pipe,won}` (same object for both reports).
A segment with no rows must still be written as `{"sqls":0,"pipe":0,"won":0}` - both builders index all
three segments by name and raise `KeyError` on a missing one.

**Fixed 2026-08-12 - the EU-always-zero bug.** The original CASE read
`WHEN ... ILIKE '%Agency%' THEN 'Agency' WHEN ... ILIKE '%Europe%' THEN 'EU' WHEN ... ILIKE '%Enterprise%'`.
Two defects compounded: (a) no pipeline value contains the string "Europe" - they say "EU" - so the EU
branch never fired and EU reported 0 in **every run since this report launched**; (b) because the
`%Agency%` branch was evaluated first, `Pre-Opp - EU Agency` fell into **Agency** and
`Pre-Opp - EU Enterprise` fell into **Enterprise**. EU was therefore never missing from the totals -
it was silently misfiled into the other two segments, inflating both. Company-level totals (e.g. B2B won
MRR) were always correct; only the segment split was wrong. **Scope note:** this query is inbound-only by
design and the `slg_tgt` targets in `targets_2026.xlsx` are inbound targets. An all-source EU count runs
roughly 45% higher (Aug 1-11: 67 all-source incl. 1 `Unknown`-source row, vs 46 inbound) - if someone
reports a bigger EU number from HubSpot or Omni, that gap is the inbound filter, not this mapping.

**Q6 - Spend by channel** (MTD + trailing-30-day). *Shared - run once. ROI uses both windows; channel
uses the MTD window only.*
```sql
SELECT 'mtd' AS win, channel_name, ROUND(SUM(daily_cost_in_usd),0) AS spend
FROM analytics.bi.daily_campaign_signup_attribution
WHERE report_date BETWEEN '<CURM0>' AND '<ANCHOR>' GROUP BY 1,2 HAVING SUM(daily_cost_in_usd)>0
UNION ALL
SELECT '30d', channel_name, ROUND(SUM(daily_cost_in_usd),0)
FROM analytics.bi.daily_campaign_signup_attribution
WHERE report_date BETWEEN '<ROLL0>' AND '<ANCHOR>' GROUP BY 1,2 HAVING SUM(daily_cost_in_usd)>0;
```
Map `channel_name` → key: `Acquisition Google Ads`→`Google`, `Microsoft`→`Bing`, `Linkedin`→`LI`,
`Facebook`→`FB`, `OpenAI`→`OpenAI`. **If a new channel appears, add it under its own key and call it out
in the run summary** (both reports).
→ ROI: `spend_mtd` + `spend_30d`. Channel: `spend` = `spend_mtd`.

**Q7 - PLG trailing-30-day MRR.** *ROI report.*
```sql
SELECT ROUND(SUM(CASE WHEN metric='new_subscription' THEN first_mrr END),0) AS first_mrr_30d,
  COUNT(DISTINCT CASE WHEN metric='new_subscription' THEN id END) AS new_subs_30d,
  ROUND(SUM(COALESCE(CASE WHEN metric='new_subscription' THEN first_mrr END,0)+COALESCE(expansion_delta_mrr,0)+COALESCE(reduction_delta_mrr,0)+COALESCE(churned_mrr,0)+COALESCE(reactivation_mrr,0)),0) AS net_mrr_30d
FROM analytics.bi.marketing_rollover WHERE date_day BETWEEN '<ROLL0>' AND '<ANCHOR>';
```
→ `plg_30d.{first_mrr,new_subs,net_mrr}`.

**Q8 - PLG onboarding intent by channel and plan** (the use case a person picks in the signup question).
*Channel report only; feeds the Onboarding Intent card under the Monthly Snapshot - both its intent table and
its use case × plan matrix. The channel table's TOTAL row leads the table (first row) since 2026-09-16.* Same window placeholders and the same 40 window fields as Q1b, minus Q1b's four
`q_`/`pq_` fields, plus an `intent` grain and a `plan` grain, **plus two 30-day and two 90-day windows** the
channel table does not have: `r30_` = `last30_window` (`<R30_0>`..`<ANCHOR>`, the last 30 complete days) and
`pr30_` = `prev30_window` (`<PR30_0>`..`<PR30_1>`, the 30 before) - the ROI report's trailing-30 definition;
`r90_` = `last90_window` (`<R90_0>`..`<ANCHOR>`) and `pr90_` = `prev90_window` (`<PR90_0>`..`<PR90_1>`), added
2026-10-06 on Nir's ask for a 90-day view on the card. The channel plan prints all four, plus
`intent_range_start`, the query's lower bound. Added
2026-09-15 (Nir's ask); plan added 2026-09-16 so the matrix does not need a query of its own (a separate
query came back small enough to display inline, which would have meant re-typing 30 KB of rows by hand every
morning); 30d added 2026-09-16.
**Intent is read at the contact (user) level, not the account level** (Nir, 2026-09-30). Each rollover
row is mapped to the person behind it, and that person's own answer is used:
`analytics.fs.users.user_first_intent_onboarding`, the first answer the user gave to the signup question
(from the `account_onboarding_flow_intent_answered` Segment event). Do **not** use
`marketing_rollover.metadata_purposes` (the account's answer) or
`fs.users.latest_account_metadata_onboarding_intent` (also the account's answer, with `'skip'`).

How the mapping works. `marketing_rollover` has no `user_id` column. Its `id` means a different thing per
metric: `user_id` for `sign_up`, `trial_id` for `trial`, `account_customer_group_id` for
`new_subscription`. `analytics.bi.marketing_funnel_analysis` carries all three next to `user_id`, so it
bridges them. Checked 2026-09-30 on Sep 1–28: 139,674 signups, 25,540 trials and 10,863 new subscriptions
each mapped to exactly one user, with no event left unmatched and none mapped to two. Totals do not change,
so the reconciliation below still holds. Re-run that check if a reconciliation ever fails.

Which intent option to use, and why:
- **`user_first_intent_onboarding`: use it.** One text value per person, so each signup lands in one
  bucket and the table adds up.
- **`onboarding_answer_one_intent`: do not use it for bucketing.** It is the list of every answer the
  person picked. About 1,300 September signups (~1.6% of answered) changed their answer and have two, so
  bucketing on it would count those people twice. Use it only to count how many changed their answer.
- **The account-level fields: do not use them.** On Sep 1–28 about 9,200 signups had an account answer
  but no answer of their own (usually a teammate on an account someone else set up), and about 12,000
  had their own answer on an account with none. User level answered 84,443 of 139,676 signups (60.5%);
  account level answered 81,688 (58.5%).

The user-level values are spelled differently from the account-level ones. The query renames four of them
so `build_artifact.py`'s `INTENT_TAXONOMY` recognises every value with no builder change:
`podcast`→`podcasts`, `livestream`→`live streaming`, `webinar`→`webinars`,
`internalcommunications`→`internal communication`. The other six (`videoclips`, `transcription`,
`marketingvideos`, `coursevideos`, `internalvideos`, `marketingcontent`) already match. User level has
no comma-separated or retired multi-select answers, so the **Legacy bucket goes empty on the new query**,
which is expected. If the card flags an unrecognised token, the product added an option: add it to the
rename list here (if it's a respelling) or to `INTENT_TAXONOMY`.
```sql
WITH bridge AS (
  SELECT DISTINCT 'sign_up' AS b_metric, user_id AS b_id, user_id AS b_user_id FROM analytics.bi.marketing_funnel_analysis WHERE user_id IS NOT NULL
  UNION ALL SELECT DISTINCT 'trial', trial_id, user_id FROM analytics.bi.marketing_funnel_analysis WHERE trial_id IS NOT NULL
  UNION ALL SELECT DISTINCT 'new_subscription', account_customer_group_id, user_id FROM analytics.bi.marketing_funnel_analysis WHERE account_customer_group_id IS NOT NULL
)
SELECT COALESCE(r.channel_group,'unknown') AS channel,
 CASE LOWER(TRIM(u.user_first_intent_onboarding))
      WHEN 'podcast' THEN 'podcasts' WHEN 'livestream' THEN 'live streaming'
      WHEN 'webinar' THEN 'webinars' WHEN 'internalcommunications' THEN 'internal communication'
      WHEN '' THEN 'no_answer'
      ELSE COALESCE(LOWER(TRIM(u.user_first_intent_onboarding)),'no_answer') END AS intent,
 CASE WHEN r.product_group ILIKE 'Pro%' THEN 'Pro' WHEN r.product_group='Mobile Plus' THEN 'Mobile Plus'
      WHEN r.product_group='Grow' THEN 'Grow' WHEN r.product_group='Webinar' THEN 'Webinar' ELSE 'Other' END AS plan,
 COUNT(DISTINCT CASE WHEN r.metric='sign_up'          AND r.date_day BETWEEN '<CURM0>'  AND '<ANCHOR>'  THEN r.id END) AS m_su,
 COUNT(DISTINCT CASE WHEN r.metric='trial'            AND r.date_day BETWEEN '<CURM0>'  AND '<ANCHOR>'  THEN r.id END) AS m_tr,
 COUNT(DISTINCT CASE WHEN r.metric='new_subscription' AND r.date_day BETWEEN '<CURM0>'  AND '<ANCHOR>'  THEN r.id END) AS m_sub,
 ROUND(SUM(CASE WHEN r.metric='new_subscription'      AND r.date_day BETWEEN '<CURM0>'  AND '<ANCHOR>'  THEN r.first_mrr END),0) AS m_fmrr,
 -- ...then the identical four-field block for each remaining window, in this order:
 --   pm_  BETWEEN '<PREVM0>' AND '<PREVM1>'      w_   BETWEEN '<CURW0>' AND '<ANCHOR>'
 --   pw_  BETWEEN '<PREVW0>' AND '<PREVW1>'      d_   = '<ANCHOR>'          pd_  = '<PREVW1>'
 --   r7_  BETWEEN '<R7_0>'  AND '<ANCHOR>'       pr7_ BETWEEN '<PR7_0>'  AND '<PR7_1>'
 --   r14_ BETWEEN '<R14_0>' AND '<ANCHOR>'       pr14_ BETWEEN '<PR14_0>' AND '<PR14_1>'
 --   r30_ BETWEEN '<R30_0>' AND '<ANCHOR>'       pr30_ BETWEEN '<PR30_0>' AND '<PR30_1>'
 --   r90_ BETWEEN '<R90_0>' AND '<ANCHOR>'       pr90_ BETWEEN '<PR90_0>' AND '<PR90_1>'
 -- (copy the blocks from Q1b verbatim - same aliases, same windows - drop q_tr/q_fmrr/pq_tr/pq_fmrr, and
 --  add the two 30-day then the two 90-day blocks at the end in the same four-field shape. Generate the
 --  56 window columns with a short script from the plan's windows rather than typing them.)
FROM analytics.bi.marketing_rollover r
LEFT JOIN bridge b ON b.b_metric = r.metric AND b.b_id = r.id
LEFT JOIN analytics.fs.users u ON u.user_id = b.b_user_id
WHERE r.date_day BETWEEN '<INTENT_RANGE_START>' AND '<ANCHOR>'
  AND r.metric IN ('sign_up','trial','new_subscription')
GROUP BY 1,2,3 ORDER BY 1,2,3;
```
- **Prefix every rollover column in the window blocks with `r.`** (`r.metric`, `r.date_day`, `r.id`,
  `r.first_mrr`, `r.product_group`) now that the query joins two more tables. `LEFT JOIN` on both so an
  event with no user, or a user with no `fs.users` row, still counts and falls into `no_answer` instead of
  vanishing from the totals.
- **`plan` is Q4's mapping of `product_group`** and only means anything on subscription rows (trials carry
  a plan ~14% of the time, signups ~1%). The builder sums plan away for the intent table and reads only
  the `sub`/`fmrr` fields per plan for the matrix, so the split on signup/trial rows is harmless.
- The `WHERE` lower bound is `<INTENT_RANGE_START>` from the channel plan = the earlier of `<PREVM0>` and
  `<PR90_0>` (anchor-179), which since the 90d view is always `<PR90_0>`. Use the printed value. Restricting `metric` to the three PLG events keeps rows
  with an intent but no PLG event (expansion, churn) out, so no all-zero rows come back.
- **Result size.** ~22 channels × ~25 raw tokens comes back around 60 KB - too large for the MCP
  result to display inline, so it is saved to a file. Parse that file into `plg_intent_rows` with a
  script (`json.loads`, nulls/blank → 0); never re-type it. It has also timed out once at the MCP
  layer on first run (2026-09-15) and succeeded on immediate retry: retry once before splitting it.
- **Bucketing is the builder's job, not the query's.** The query passes raw lower-cased tokens
  through. `build_artifact.py` collapses them with `INTENT_TAXONOMY` (the ten tokens of the current
  single-answer question: `podcasts`, `videoclips`, `transcription`, `live streaming`, `webinars`,
  `marketingvideos`, `internalvideos`, `coursevideos`, `marketingcontent`, `internal communication`,
  which is 1:1 what `analytics.bi.accounts_use_cases.usage_purpose` normalises) and
  `INTENT_LEGACY_TOKENS` (answers from the retired multi-select form, plus any comma-separated
  value). A token in neither set keeps its own row under its raw name **and** is flagged in the
  card's note - that is how a newly added question option surfaces. When you see that flag in a
  built report, add the token to the right constant and rebuild.
- **Coverage - read this before trusting any month-over-month figure on the card.** The use-case question
  was answered by 34-190 signups a month from June 2025 to July 2026 (a test flow, ~0.03% of ~150k monthly
  signups), 906 in August 2026, and 39,178 in September (51%) - it went live in signup the week of
  **2026-08-31**. `analytics.bi.accounts_use_cases` shows the identical ramp, so this is the product's
  history, not a data gap. Consequences the builder encodes: share defaults to **% of answered** (the intent
  mix; a share of all signups just tracks how many were asked - "Podcasts 0.2% → 17.8% of signups" is a
  rollout curve, not a 75× shift, which is how 2026-09-16's fourth pass on this card went wrong); count
  changes are always absolute with the prior beside them; and where the prior window has under 20% answered
  or fewer than 100 answers, the share line shows the prior share **and its sample size** ("was 69.4% of
  219") with **no computed change**, because a change against ~200 test-flow answers is noise. The caption
  says this in words on MoM / 14d / 30d until October; WoW and 7d have a like-for-like prior. Trial and
  subscription rows carry the account's answer from signup, so their coverage lags signups by the conversion
  delay. Where a change IS computed (WoW, 7d, and any view once October gives MoM a real prior) it is relative -
  "35.1% ▲ +1.0% · was 34.7%", Nir prefers this to percentage points - with one decimal at most, rendered as a
  multiple from +1,000% up and never with a thousands comma ("+7,425%" once read as 7.425 with three decimals).
  None of this is a data problem - do not "fix" it in the query.
→ `plg_intent_rows`, one row per (channel, raw intent token, plan), **59 fields** (nulls → 0):
`[channel, intent, plan, m_su,m_tr,m_sub,m_fmrr, pm_su,pm_tr,pm_sub,pm_fmrr, w_su,w_tr,w_sub,w_fmrr, pw_su,pw_tr,pw_sub,pw_fmrr, d_su,d_tr,d_sub,d_fmrr, pd_su,pd_tr,pd_sub,pd_fmrr, r7_su,r7_tr,r7_sub,r7_fmrr, pr7_su,pr7_tr,pr7_sub,pr7_fmrr, r14_su,r14_tr,r14_sub,r14_fmrr, pr14_su,pr14_tr,pr14_sub,pr14_fmrr, r30_su,r30_tr,r30_sub,r30_fmrr, pr30_su,pr30_tr,pr30_sub,pr30_fmrr, r90_su,r90_tr,r90_sub,r90_fmrr, pr90_su,pr90_tr,pr90_sub,pr90_fmrr]`.
A 43-field (pre-30d) or 51-field (pre-90d) row still builds; the card's 30d / 90d view then says the fields are missing instead of rendering zeros as data.
**90d coverage (checked 2026-10-06):** the user-level answer (`user_first_intent_onboarding`) has covered 56-60% of
signups every month since April 2026, so the 90d prior is like-for-like and the card shows no thin-prior flag on it.
Reconcile before writing: the MTD sums across all rows must equal Q2/Q3's `cur_m` exactly for signups,
trials and new_subs, and within a few dollars for first_mrr (each row is ROUNDed before you sum them;
2026-09-15 came in $2 under). Every PLG row has some intent value, if only `no_answer`, so a bigger gap
means a window or metric filter is wrong.

**Q8 comes back large (~220 KB with the 90d windows, ~790 rows) and the MCP saves it to a file.** Parse it with a script into `report_values.json`
(`json.loads` on the saved text from its first `{`, blanks/nulls → 0), and print the MTD reconciliation; never
re-type a row. If it times out at the MCP layer, retry it once before anything else. (A declared-source query, Q9,
ran 2026-09-16 only; Nir removed that table the same day.)

## Step 5 - Spend lines: invoice-board actuals every run, manual fallback
The channel report's **Growth Channels** and **Creative partnerships** lines are computed from the
**Invoices and Payments - Growth Marketing** board (`18390740532`) on every run (decided 2026-08-26),
so the report carries board actuals as of the run morning. `../manual_inputs.json` is the fallback for
those two lines and still the source for `seo_spend` and `slg_arr`.

1. **Load a monday read tool.** ToolSearch for `monday api read` and load the read-only GraphQL tool
   (`all_api_read`). Do NOT hardcode the MCP server id - it differs per account and machine.
2. **Resolve the ANCHOR month's group by title, live** (`<Month YYYY>` of the anchor date, e.g. anchor
   2026-09-01 → `September 2026` - the anchor's month, not the run date's):
   `boards(ids: [18390740532]) { groups { id title } }`
3. **Pull that one group's items**, paging until `cursor` is null:
   ```graphql
   boards(ids: [18390740532]) { groups(ids: ["<group id>"]) { title items_page(limit: 500) {
     cursor items { id name column_values(ids: ["numeric_mky9safm","multiple_person_mkz6t3jw","color_mm0e2221"]) { id text } } } } }
   ```
4. **Save the response VERBATIM** to `tools/daily-reports/build/board_items.json` (git-ignored). Paste
   the raw JSON unmodified - never re-type items or amounts.
5. **Compute deterministically** - one command, absolute path, never sum by hand:
   ```
   python3 <REPO>/tools/daily-reports/build/spend_actuals.py <REPO>/tools/daily-reports/build/board_items.json
   ```
   Use its `creative_partnerships_spend`, `growth_channels_spend`, `affiliates_spend`,
   `affiliate_freelancers_spend` and `b2b_vendors_spend` for `manual.*` in `report_values.json`, all
   five with `manual_basis` = `"invoice_actual"`. **Also paste the script's whole JSON object, verbatim,
   into `roi_report_values.json` as `invoice_spend`** (Step 6): the ROI report renders it as its
   Invoice-board actuals card.
   **Split by Type (Hanan for Nir, 2026-10-04).** The payer rules decide which invoices count; the
   board's Type column then decides the line. `Affiliates` → Affiliates; `Affiliate (Freelance and
   Platforms)`, `Freelance`, `Affiliate Vendors`, `Creators Freelancer / Platform Fees` → Affiliate
   freelancers & platforms; `B2B Vendors` → B2B vendors; anything else keeps its payer line, and the
   leftover Growth Channels line renders as **Other Growth Channels**. This exists because Savion pays
   for both Creator Marketing and Growth Channels since Dor left, so the payer rule alone filed
   September's affiliate platforms and freelancers (Impact, PartnerStack, Ron Davidman: ~$31k) under
   Creative partnerships and showed Growth Channels at $0. The split never changes the total that
   counts: creative + growth + affiliates + affiliate freelancers + B2B equals what the three old
   lines summed to.
   `b2b_vendors_spend` (added 2026-09-19 on Nir's ruling) is the B2B vendor spend Nir files
   himself - Ziff Davis and the like - and renders as its own `B2B vendors` spend line inside the
   ROI denominator. Before the ruling it fell into the script's `other` bucket and was discarded,
   which cost September $14,250 of real spend and overstated MTD ROI by about 10 points. The
   scope Nir set that day: **Savion's, Raz's, Erika's and Dor's invoices count, Hanan's
   (Marketing Ops) do not** - so `other_teams_total` is now expected to be Marketing Ops only,
   and a non-Hanan item landing there is a signal to check, not noise. The attribution rules (payer
   map, Dor-presence, owner-ruled vendor exceptions) are embedded in the script; the human-canonical
   copy is `.claude/skills/invoice-board-spend-pulse/knowledge/config.md` - change the two together.
   Carry the script's `flagged` items (Growth-Channels-suspect vendors with unruled payers, blank
   `Payed by`) and its blank-amount count into the run summary - they are the reason a figure may
   understate, and a flagged vendor needs a human ruling before it counts anywhere.
6. **Fallback - spend lines never abort the run.** If the monday tool is unavailable, the anchor
   month's group does not exist on the board, or the script exits non-zero: use `../manual_inputs.json`
   (anchor-month key) for the two lines with `manual_basis` per that file's `_note` (currently
   `invoice_actual`), and flag "spend lines from manual fallback, as of <the note's as-of date>" in the
   run summary and the Notion line. If the anchor-month key is also missing or all-null, derive the
   spend lines from the ROI `budgets_monthly` below × the month run-rate (`mrr` from the plan) with
   basis `budget_prorated` (convention since 2026-07-26). Do **not** pass nulls through: `money()` in
   `build_artifact.py` renders `null` as `$0` (it is `Math.round(null)`), so nulls silently ship $0
   spend lines and an ROI inflated by roughly 100 points rather than visibly flagging.

- **`seo_spend` and `slg_arr`** still come from `../manual_inputs.json` (no SEO invoices are filed on
  this board; SLG ARR is not an invoice figure). Missing/null → `seo_spend` from `budgets_monthly` ×
  the month run-rate (`budget_prorated`), SLG ARR from the plan's `slg_arr_monthly` × `mrr`.
- **ROI report ROI unchanged:** its ROI still prices non-PPC spend off fixed monthly budgets in
  `roi_report_values.json` (not `manual_inputs.json`). The invoice-board split shows there as a
  separate **Invoice-board actuals** card (from `invoice_spend`), never inside that ROI. Budgets:
  `budgets_monthly = {"SEO":70000,"Creative partnerships":150000,"Growth Channels":80000}`. Keep unless
  Nir changes them. SLG ARR is derived by the builder (B2B-MRR target ×12 ÷3) - no manual SLG ARR input.

## Step 6 - Write value JSONs and build both
Write both files in `build/` (schemas at the top of each builder):
- `report_values.json` - `anchor_date`, `plg_channel_rows` (Q1), `plg_channel_detail` (Q1b), `plg_intent_rows` (Q8),
  `plg_totals`, `slg`, `spend`, `manual`, `manual_basis`.
  `manual` carries `growth_channels_spend`, `creative_partnerships_spend`, `affiliates_spend`,
  `affiliate_freelancers_spend`, `b2b_vendors_spend` (all five from Step 5's board pull; the two
  affiliate keys since 2026-10-04) and `seo_spend`, plus `slg_arr`. Omitting
  `b2b_vendors_spend` is allowed and drops the line rather than rendering $0 as a fact - but on a normal
  run it should be present, so a missing key belongs in the run summary.
  (No `notion_url` - the Notion log was retired 2026-08-18.)
  If `plg_channel_detail` is omitted, the channel table renders empty - the builder no longer derives it from `plg_channel_rows`.
  If `plg_intent_rows` is omitted, each table in the Onboarding Intent card renders a one-line "no rows in this build" notice naming the missing key; the rest of the report is unaffected.
  - **`manual_basis` (added 2026-08-13) - always include it.** A map from each `manual` key to its
    provenance: `"invoice_actual"` (taken from the Invoices and Payments board - lags accrued spend),
    `"budget_prorated"` (monthly budget × month run-rate), or `"actual"` (a non-lagging real MTD figure).
    It drives the "⚠ Mixed spend basis" banner on the channel report: any `invoice_actual` line makes the
    banner render and name the lagging lines. Omitting the key silently ships the report **without** the
    warning - exactly the months it is needed. Rule of thumb: a value computed live from the board by
    `spend_actuals.py` (Step 5) is `invoice_actual`, and so is a value copied from `manual_inputs.json`
    that came from the invoices board; a value you derived from `budgets_monthly` × run-rate (the
    missing/null fallback in Step 5) is `budget_prorated`.
- `roi_report_values.json` - `anchor_date`, `rollover_window` (= ROLL), `plg_hl`, `subs_breakdown`,
  `slg`, `spend_mtd`, `spend_30d`, `plg_30d`, `budgets_monthly`, `notion_url`, and `invoice_spend`
  (added 2026-10-04: Step 5's `spend_actuals.py` JSON object, verbatim). Omit `invoice_spend` when
  Step 5 fell back to `manual_inputs.json`; the card then says it has no figures rather than showing
  stale ones.
After both JSONs are written, build both with the wrapper - ONE command, absolute path, no `cd`/`&&`:
```
bash <REPO>/tools/daily-reports/build/daily_build.sh build <ANCHOR>
```
It runs both builders (→ `plg_daily_snapshot.html`, `roi_daily_snapshot.html`), copies the ROI file to
`Riverside_ROI_Report_<ANCHOR>.html`, and then runs an **anchor sanity check that can fail the build**.
Do NOT hand-run the builders in a `cd ... && python3 ... && cp ...` compound: that trips the
cd-with-write approval prompt and, because the dated filename changes daily, re-prompts every run even
after "Always allow".

**The anchor sanity check is a gate, not a printout (fixed 2026-08-19).** It asserts that the `<ANCHOR>`
you passed on the command line is the one the builders actually rendered, by requiring both the long
form (`August 18, 2026`, the "Latest complete day" header) and the short form (`Aug 18`, the
"MTD through" label) to be present in *each* of the two HTML files. On a mismatch it prints
`FAIL <file>: missing [...]` and **exits non-zero** - stop there, do not continue to Step 7.

On a failure it also **deletes the staged `Riverside_ROI_Report_<ANCHOR>.html`** and says so. That file
is copied before the check runs, so a failed build has already overwritten it with wrong-anchor HTML;
leaving a deploy-ready filename over rejected content is exactly how a bad build reaches the Hub, since
Step 7 uploads it by name. Nothing recoverable is lost - whatever was there was clobbered by the copy.
The practical consequence: after a failure the dated file is *gone*, so rebuild rather than looking for
it. In the rare case the delete itself fails (permissions, file held open), the check says
`COULD NOT remove the staged ...` and still exits non-zero - delete that file by hand before rebuilding,
because it holds the rejected build under a deploy-ready name. The usual cause is a value JSON whose `anchor_date` disagrees with the `<ANCHOR>` argument: fix
Step 6's JSONs and rebuild.

Until 2026-08-19 this check grepped the HTML for `YYYY-MM-DD` and could never fail - neither builder
emits an ISO date - so it printed either an unrelated hardcoded date or nothing at all. If you are
reading an old run log, treat its "anchor sanity" output as noise. The expected strings are now derived
in Python rather than with `date`, so the check behaves identically on macOS and in the Linux cloud
routine.

## Step 7 - Deploy both surfaces
1. **Channel** - Artifact tool: `file = build/plg_daily_snapshot.html`,
   `url = https://claude.ai/code/artifact/0b9eef24-e1a7-4e3c-b145-f666fa97a7c8`, `favicon = 📊`
   (keeps the same shareable link).
2. **ROI** - invoke the `rivermind:analytics-hub-report-manager` skill (it bundles the API token and
   resolves its own `hub_report_manager.py` path - do NOT hardcode a plugin path, it changes per
   session). Replace in place: `… "Riverside_ROI_Report_<ANCHOR>.html" --replace de39972a29cf46f3bbb57fac09833214 --json`.
   Confirm `{"ok": true, "action": "replace"}`. `--replace` keeps the id, `/hub/<id>` link, and folder.

The retired claude.ai ROI artifact `371dbe5d-733b-4c27-a62c-f6aa288ef9a4` is NOT refreshed (since
2026-07-08). The Hub is the ROI report's only live surface.

## Step 8 - Log
If Notion MCP is connected, append a one-line dated note to page
`38f97be2-38ae-81ff-8792-d21a98f9c386`. End with a one-line summary covering both reports: anchor date,
Trials / First MRR / Net MRR attainment, MTD ROI, PPC WoW, and any missing manual inputs or new spend
channels.
