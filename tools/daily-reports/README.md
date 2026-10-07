# Daily Reports

Nir's two Claude-driven daily reports, rebuilt each morning from Snowflake:

- **PLG channel-detail** → claude.ai artifact `0b9eef24`
- **ROI & Growth** → Analytics Hub report `de39972a`

**Run it:** follow [`REFRESH_DAILY.md`](REFRESH_DAILY.md) - the unified recipe (one anchor, one data
pull, both reports). This is what the `refresh-daily-reports` scheduled task executes.

**System doc:** [`systems/owned/daily-reports.md`](../../systems/owned/daily-reports.md) - architecture,
data model, schedule, gotchas.

```
tools/daily-reports/
  REFRESH_DAILY.md         # operational recipe (source of truth)
  targets_2026.xlsx        # tracked input: 2026 targets
  manual_inputs.json       # tracked input: seo_spend + slg_arr, and the fallback snapshot for the two invoice-board spend lines, keyed YYYY-MM
  build/
    build_artifact.py      # channel-detail builder (+ shared compute_params)
    build_roi_artifact.py  # ROI builder (imports compute_params)
    spend_actuals.py       # Growth Channels + Creative partnerships spend from the monday Invoices board (run each morning, recipe Step 5)
  state/                   # git-ignored delay-gate markers
```

Runtime outputs (`build/*.html`, `build/*_values.json`, `build/board_items.json`, dated ROI HTML) are
git-ignored. Requires Python 3 + `openpyxl`.
