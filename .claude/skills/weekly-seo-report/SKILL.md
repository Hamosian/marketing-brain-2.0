---
name: weekly-seo-report
description: The weekly SEO report, 7 days of organic search traffic and conversion for the whole site across all locales. Compares the last 7 complete days of organic search against the prior 7 from Snowflake, split by brand / non-brand / LLM, with the landing pages that gained and lost the most sign-ups, plus a Google Search Console tab on its own lagging window carrying top 25 queries and pages by clicks, the non-brand query and page click movers both ways, and top 10 countries. Publishes to one stable Riverside-branded artifact URL updated in place, then DMs Amir the headlines and posts to the SEO reports channel. This is search performance, so for the weekly monday task report use /nir-weekly-report, for one locale /seo-de-report, and for rank tracking, AI-overview share or content cohorts the monthly /organic-dashboard. Runs Thursdays as a cloud routine, or on demand. Trigger with "weekly seo report", "organic weekly report", "7 day organic report", "how did organic search do last week", or "/weekly-seo-report".
---

# Weekly SEO Report

The 7-day organic funnel for the SEO team: what converted, which pages moved,
and what in the data would mislead someone reading it. One artifact, two tabs,
one stable URL.

**Read + generate only.** It never writes to Snowflake or Search Console. The
only side effects are republishing the artifact and sending the Slack summary.

> **Scope, and what is deliberately out.** This is the *conversion* report:
> Snowflake funnel plus Search Console. **No Ahrefs, no rank tracking, no
> content-cohort or keyword-taxonomy analysis** - those are monthly questions
> owned by [`/organic-dashboard`](../organic-dashboard/SKILL.md), and at a
> weekly grain rank movement is mostly crawl-schedule noise that crowds out the
> funnel. Route those asks there. System doc for both:
> [`systems/owned/seo-organic-dashboard.md`](../../../systems/owned/seo-organic-dashboard.md).

## The one thing that must not change

Publish to the **stable URL in [`knowledge/stable-url.md`](knowledge/stable-url.md)**,
passing it as the Artifact tool's `url`, keeping the title and favicon. It is
shared with the organization; a new URL strands that. Read the live version
before publishing, or the service refuses the write.

## Operating model

| Dimension | Decision |
|---|---|
| **Window** | The **7 complete days ending yesterday**, against the 7 before. Pulled Thursday that is Thu-Wed vs Thu-Wed. Resolved only by `scripts/resolve_week.py`. |
| **Why 7 days** | Weekend organic traffic is about half a weekday, so any window that is not a multiple of 7 measures the calendar. Holidays are checked separately; the script flags them. |
| **Search Console** | Runs on its **own** window, because Windsor lags ~3 days. Announced in a banner on the tab and on every table. The two tabs overlap and are never read as one period. |
| **Delivery** | The artifact, plus a short Slack DM to Amir Bar-Tikva (`U0B3NM80M1N`). Post to `#seo-reports` (`C0C082P5VT4`, the SEO team: Amir, Erika, Ortal) only when asked; the default is the DM. |
| **Analysis** | Try `/rivermind:ask` first per the department data rule. Per-URL weekly organic funnel is a documented coverage gap, so expect it to punt - fall back to `/data-agent` (Snowflake `analytics.bi.marketing_rollover`) and say so in the run summary. |
| **Storage** | Artifact-only. Source systems remain the record; a lost artifact is rebuilt by one run. |

## Non-negotiable safeguards

Full reasoning and the evidence behind each:
[`knowledge/build-and-render.md`](knowledge/build-and-render.md).

1. **Homepage merge.** `NULL`, `''` and `homepage` all become `/`. 55% of
   organic subscription rows carry a NULL path; a `clean_url_path IS NOT NULL`
   filter looks like hygiene and deletes the biggest page on the site.
2. **`first_mrr` only on `new_subscription` rows.** Unfiltered it reads 4.5x too
   high, without erroring.
3. **Thin-base floor.** Under 5 prior subscriptions or $100 prior MRR shows a
   grey absolute chip, never a percentage.
4. **Never a numeric filter on a Windsor pull.** It silently changes the totals
   of the rows it returns. Pull unfiltered, rank locally.
5. **Non-brand = property total minus brand**, using `/\b(riv|rev[ei]r)/i`.
   Never sum non-brand from query rows.
6. **The table restates.** Query both windows in the same run, and expect last
   week's published figures to have moved.

## Steps

### Step 0 - Resolve the windows and check freshness

```bash
python3 .claude/skills/weekly-seo-report/scripts/resolve_week.py --json
```

Check Snowflake reaches the window's last day.

For Search Console, **always pull the daily series as `date` + `device`, never
`date` alone.** The single-dimension `date` rollup is defective: it has returned
no row at all for three consecutive days while merging five days into one. The
second dimension makes it correct, and device rows reconcile exactly to the
property total, so summing them is exact rather than an approximation. Full
proof and the reconciliation check: [`knowledge/data-dictionary.md`](knowledge/data-dictionary.md).

Then take the GSC window's last day from that series and re-run the script with
`--gsc-through <that date>`. A ~3-day lag is normal and is not a fault.

- **Snowflake short by a day or two:** shift both windows back so they end on
  the last settled day, keeping them 7 days each. On 2026-09-17 the table
  reached only Sep 15, so the windows ran Sep 9 to 15 against Sep 2 to 8,
  Wednesday to Tuesday. Confirm the last day is complete, not partial, by
  checking it against the same weekday in prior weeks. Say in the masthead and
  the notes that the windows shifted and that this breaks exact comparability
  with the previous edition.
- **Snowflake short by more than two days, or the last day looks partial:** do
  not publish. DM Amir the source and its latest date, and stop.
- **GSC genuinely short** (the device pull is also missing days): publish the
  funnel anyway, it is most of the report. Replace the Search Console tab with
  what is wrong, the daily evidence, and the last known good window, and say so
  in the masthead and the DM. Never carry a stale window forward as current, and
  never call a source broken before trying the second dimension.

### Step 1 - Pull

Run the Snowflake CTE and the GSC calls in
[`knowledge/data-dictionary.md`](knowledge/data-dictionary.md). Both windows in
one query so they cannot drift.

### Step 2 - Validate

Homepage present and top; channel table foots to the tiles; every table footer
equals an independently computed sum; thin-base cells render grey chips. Compute
the coverage figures rather than estimating them.

### Step 3 - Write the notes

The data-notes section is the part people quote. Order by how much each would
change a decision, and cover at minimum: anything that restated, any holiday in
either window, the auth-page contamination, and the cohort caveat. Where a cause
is not established, write that. Never invent one.

Carry threads between editions: if last week raised a question, answer it this
week or say it is still open.

### Step 4 - Render

Write the payload to a JSON file, shape in
[`knowledge/data-payload.md`](knowledge/data-payload.md), then:

```bash
REPORT_DATA=<your-payload>.json REPORT_OUT=organic-conversion.html \
  python3 .claude/skills/weekly-seo-report/render_report.py
```

`REPORT_OUT` is required and must point **outside the repo** - the renderer
refuses to run without it, so a run can never drop report HTML into the tracked
skill directory.

`render_report.py` holds no figures of its own - every number, every lede, the
data-notes findings and the footer paragraphs all come from the payload, and
window labels derive from `_meta`. **That is the invariant to protect:** the
funnel tab once carried its findings as hardcoded prose and quietly republished
a stale week's figures for months. If you find yourself editing the renderer to
say something about this week, it belongs in the payload. A structurally
complete synthetic payload ships as `report-data.example.json` and smoke-tests
the renderer. The GSC tab's seven sections are fixed; do not add or reorder them
without changing the spec in
[`knowledge/build-and-render.md`](knowledge/build-and-render.md) first.

### Step 5 - Publish

Read the live artifact first (the service refuses a publish from a session that
has not), `node --check` the inline script, confirm the funnel tab is the one
visible at rest and both panels toggle, check the renderer's cross-foot lines
all passed, then publish with `url` set. Never publish without `url` - that
mints a new link and strands the bookmark.

### Step 6 - Send

DM Amir. Five short lines, energetic, no Markdown tables (Slack does not render
them), the artifact link as the detail, footer
`_Posted by the Marketing OS agent_`. Lead with the funnel direction, then the
one thing that most needs attention, then anything broken in the data.

## Constraints (it runs unattended)

- **Read-only**, and idempotent: the artifact updates in place, so a re-run
  overwrites rather than duplicating. Before sending, check the destination for
  an existing message covering the same window and skip if present.
- **Every ambiguous branch has a default, not a question**: Snowflake stale →
  skip and DM; GSC short after the device workaround → publish the funnel and
  document the break; nothing
  material moved → say so; cause unknown → "cause not established".
- **Never invent a cause**, and never present a number whose provenance is not
  in the data dictionary.
- Load-bearing connectors are Snowflake, Windsor.ai and Slack. `monday-api`,
  `hubspot` and `gdrive` are irrelevant here; their auth state never blocks a run.

## Cadence

Thursdays. Deployed as a recurring trigger firing `/weekly-seo-report`.

| | |
|---|---|
| **Intended local time** | **Thursday 09:00 Asia/Jerusalem** |
| Cron during IDT, UTC+3 (late Mar to late Oct) | `0 6 * * 4` |
| Cron during IST, UTC+2 (late Oct to late Mar) | `0 7 * * 4` |

`cron_expression` is **UTC with no timezone**, so the local hour drifts an hour
at each DST boundary. The local time above is the intent - fix the cron at the
boundary rather than re-deriving it. Erika is UK-based, so record the intended
local time beside any change.

**Thursday is not arbitrary.** Snowflake carries data through D-1, so a Thursday
run gets a complete Thursday-to-Wednesday week against the Thursday-to-Wednesday
before it, both holding exactly 2 weekend days. Any weekday works; a run that is
not a multiple of 7 days from the previous one does not.

### Deploying the routine

`references/change-control.md` lists seven ways a routine ends up "written but
not running." Four bite this one:

1. **A routine clones `main`.** This skill must be on `main` before a routine
   can find it. Register after the merge, or register disabled and enable after.
2. **Connector grants cannot be added after the fact.** This needs Snowflake and
   Windsor.ai. `create_trigger` from a repo session cannot pass through
   connectors held via a project-configured MCP server rather than a personal
   claude.ai connector, and `update_trigger` cannot repair it. If the create
   response warns that the trigger stores no connectors, **do not deploy it** -
   it will look created and fail on every firing. Have Amir create it at
   https://claude.ai/code/routines, where his own grants attach.
3. **No effort lever.** `session_context` accepts an `effort` key, returns 200,
   and discards it. The prompt is the only lever. Never trust a 200 - read the
   stored config back.
4. **Bound the follow-up in the prompt.** The prompt must say: publish, report,
   and schedule no self check-in. There is nothing to wait for - the artifact
   either published or it failed.

## Done when

The artifact at the stable URL shows the current window on both tabs (or a
documented reason the Search Console tab could not advance), every figure
cross-foots, and the DM is sent - or the freshness gate failed on Snowflake and
Amir has been told why.
