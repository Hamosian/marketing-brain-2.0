---
name: seo-de-report
description: Generates the DE (/de/) organic search performance report - per-URL visits, sign-ups, subscriptions, and first MRR for organic search (Non-Brand + Brand + LLM combined into one channel, since the split is unreliable for localized pages) compared across any two equal-length date ranges. Publishes a Riverside-branded, sortable/searchable HTML artifact (stable URL, updated in place) plus a CSV export. Defaults to the most recently completed calendar month vs the month before when no range is given. Runs on demand for any date range, or monthly as a cloud routine for the standard MoM view. Trigger with "DE organic report", "German organic search report", "run the DE report", "/de/ organic performance", "seo de report", or "/seo-de-report".
---

# SEO DE Report

Generate the `/de/` organic search performance report: every `/de/` URL that
got organic search traffic in the requested window, with visits, sign-ups,
subscriptions, and first-month MRR, compared against the prior equal-length
period. Ships as one self-contained HTML artifact (sortable/searchable table,
KPI tiles, a "where the change concentrates" mover chart) plus a CSV export.

This is a **read + generate** workflow. It never writes to Snowflake, Omni,
or HubSpot. The only side effects are (re)publishing the artifact and sending
the CSV/HTML files.

## The one thing that must not change

**Update the existing artifact in place** so any bookmark/link already shared
keeps working:

```text
https://claude.ai/code/artifact/cf7fdcec-3ce0-4717-a332-e1bd3750cd88
```

Pass this as the Artifact tool's `url` parameter (same `favicon` 📉) for the
**default range** (most recent completed month vs the month before) - that is
the one bookmarkable "current state" link. For a genuinely different one-off
ad hoc range someone explicitly wants as its own separate link (e.g. "compare
Q1 to Q2"), ask whether to update the standard URL or mint a new one; default
to a new one only when asked.

## Operating model

| Dimension | Decision |
|---|---|
| **Delivery** | Published claude.ai Artifact (private) + a CSV export sent as a file. Send the standalone HTML file too if the person wants a direct-download copy (see `knowledge/build-and-render.md` for why the artifact page itself is *not* a valid direct-download file). |
| **Storage** | Artifact-only. The latest snapshot lives in the artifact; source systems remain the record. Derived, not authoritative - a lost artifact is rebuilt by one run. |
| **Refresh** | On-demand for any date range (`/seo-de-report jan vs feb 2026`, `/seo-de-report last quarter`, etc.), or automatically once a month via a cloud routine using the default range. |
| **Analysis** | Always try `/rivermind:ask` first, per the department-wide data-question rule. Per-URL organic-funnel breakdowns for a single locale are a **documented coverage gap** today, so expect it to punt - fall back to `/data-agent` (Snowflake `analytics.bi.marketing_rollover`) and note the fallback in the run summary rather than pretending Rivermind covered it. Re-check Rivermind coverage occasionally; if it picks this up, prefer it. |
| **Comparison** | Any two **equal-length** periods. Default = most recently completed calendar month vs the month before (matches the pilot Jul-vs-Jun run and the calendar-month-vs-calendar-month MoM convention `/organic-dashboard` already uses) - "equal-length" here means full calendar month vs. full calendar month, understood to differ by up to a few days like any calendar-month MoM figure, not a day-count-normalized comparison. A partial current period is labelled partial and never compared as if complete. |
| **Known issue** | The Non-Brand vs. Brand `channel_group` split is unreliable for localized (`/de/`) pages - this report deliberately reports organic search as **one combined channel** (Non-Brand + Brand + LLM) per URL instead of perpetuating a misleading split. Flagged to the Data Team; if you use `/data-team-request` to file that, link it here. |
| **Exclusions** | `/de/home` is confirmed non-indexed and excluded from every run - see the Excluded URLs list in `knowledge/build-and-render.md` before adding or removing an exclusion. |

Full data source, query shape, safeguards, and the render-script contract:
[`knowledge/build-and-render.md`](knowledge/build-and-render.md). Read it
before your first run.

## Steps

### Step 0 - Resolve the date range
- Explicit range given → validate it's two **equal-length** periods (e.g. two
  full calendar months, two full quarters, two identical day-counts). If
  unequal, say so and ask which side to trim rather than silently comparing
  apples to oranges.
- No range given → default to the most recently completed calendar month vs.
  the month before (this is what the cloud routine always uses).
- If the "current" side is still in progress (mid-month), label it partial
  and do not present it as a complete-period comparison.

### Step 1 - Pull the data
Try `/rivermind:ask` first per the department-wide data-question rule. For
this specific shape (per-URL organic funnel, single locale, arbitrary date
range) expect it to punt - that's the known gap, not a bug in your query.
Fall back to `/data-agent` and query Snowflake `analytics.bi.marketing_rollover`
filtered to `clean_url_path = 'de'` or `'de/...'` (**no leading slash** -
`clean_url_path` is stored as `de`, `de/transkription`, etc., not `/de`,
`/de/transkription`; a literal `/de` prefix silently matches zero rows, it
does not error - confirmed 2026-09-07 building the Sep monthly run) and not
an unrestricted `de` prefix match either (that would also catch unrelated
paths like `design` or `dev`), `channel_group IN ('organic search non brand',
'organic search brand', 'organic llm')`, summed **combined** per
`clean_url_path` (prepend the `/` yourself when building the render script's
`url` field), for both periods. Then **drop every URL on the Excluded
URLs list** (`knowledge/build-and-render.md`) before moving on - currently
just `/de/home` (confirmed non-indexed, not eligible for organic traffic).
Exact query shape and the canonicalization rules are also in that file.

### Step 2 - Validate
- Per-URL visits (**after** applying the exclusion list) should sum to the
  topline total for each period, once the excluded URLs' traffic is also
  removed from the topline. If it doesn't foot, investigate before
  publishing - don't silently paper over a mismatch.
- The `/de` homepage should be at or near the top of the table; if it's
  missing or near-zero, the canonicalization step likely broke - see the
  organic-dashboard's homepage-NULL gotcha, which applies here too
  (`systems/owned/seo-organic-dashboard.md`).
- If any excluded URL shows non-zero traffic in this pull, don't just drop it
  silently - note it in the Step 5 summary (see the Excluded URLs section in
  `knowledge/build-and-render.md`).

### Step 3 - Shape and render
Assemble the per-URL records into the JSON schema documented in
`knowledge/build-and-render.md`, then run:

```bash
python3 .claude/skills/seo-de-report/scripts/build_report.py <input.json> <output.html> --csv <output.csv>
```

The script owns all layout/styling/interactivity (brand tokens, font,
sortable table, mover chart) - it never invents numbers. If the visual design
ever needs to change, edit the script, not a copy pasted into a one-off run.

### Step 4 - Publish and deliver
- Publish `<output.html>` via the Artifact tool. Use the stable `url` (above)
  for a default-range run; ask before minting a new URL for anything else.
- Send `<output.csv>` (and the raw HTML file, if asked for a downloadable
  copy) via the file-send tool.

### Step 5 - Report
Summarize the headline KPI deltas (visits/sign-ups/subscriptions/first MRR),
the two or three biggest movers from the chart, and any data-quality flag
from Step 2. Keep it to what changed - the artifact carries the full detail.

## Constraints

- **Never invent figures.** If a source lacks coverage for part of the
  requested range, say so; don't interpolate or estimate.
- **Equal-length periods only, with one named exception.** The default full
  calendar-month-vs-calendar-month MoM view is exempt from day-count parity
  (see the Comparison row above) - that's the intended, department-standard
  convention, not a defect. Everywhere else, comparing unequal ranges (a
  31-day month to a 28-day month picked as an ad hoc range, or a partial
  month to a complete one) without flagging it produces a misleading
  percentage - always label partial periods and unequal ad hoc ranges.
- **Surface data-quality anomalies, don't silently fix them** (a per-URL sum
  that doesn't foot to the topline, a canonicalization break, a channel this
  locale doesn't normally see).
- **Cloud-routine runs are unattended** (no human to confirm): this is fine
  because the workflow is read + generate only - it never writes to a live
  system, so the usual mutating-action confirmation gate doesn't apply. It
  still must not silently swallow an error: if a source query fails, the
  routine's report should say so rather than publishing a partial/stale page.

## Cadence

On demand at any time, for any range. Also runs **monthly as a cloud
routine** - early in the month (after Snowflake's prior-month data has
settled), using the default range - which updates the stable artifact URL
and sends a completion notification with the headline deltas. Re-wire the
schedule only after a tested real run; see `knowledge/build-and-render.md`
for the trigger configuration on file.

## Done when

The artifact is updated at the stable URL (or a new one, if that was the
explicit ask), the CSV has been delivered, and the summary in chat states the
headline deltas, the top movers, and any data-quality flag.
