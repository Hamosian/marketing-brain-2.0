# Data source, safeguards, and the render script contract

## Data source

| Source | System | Access | Scope |
|---|---|---|---|
| Organic funnel | Snowflake `analytics.bi.marketing_rollover` | `/data-agent` (read) | `clean_url_path = 'de'` or `clean_url_path LIKE 'de/%'` (**no leading slash** - see the gotcha below; also not an unrestricted `de` prefix match, which would also catch unrelated paths like `design` or `dev`), `channel_group IN ('organic search non brand','organic search brand','organic llm')`, summed **combined** (not split) per URL, for the requested period and the prior equal-length period |

### Gotcha: `clean_url_path` has no leading slash

Confirmed 2026-09-07, direct against `analytics.bi.marketing_rollover`: the
column stores `de`, `de/transkription`, `de/home` - never `/de`,
`/de/transkription`. A filter written as `clean_url_path = '/de' OR
clean_url_path LIKE '/de/%'` (what an earlier revision of this skill
documented, and what a literal reading of Step 1 would have run) returns
**zero rows, silently** - no error, just an empty result set that looks like
"no DE organic traffic this period" instead of "wrong filter." Always query
without the leading slash, then prepend `/` yourself when building the
render script's `records[].url` field. This is the same shape of gotcha
`/weekly-seo-report`'s Snowflake pulls and the Omni `Marketing Funnel
Analysis` topic both carry - check a sample row before trusting a
zero-result query against this table.

Rivermind (`/rivermind:ask`) is the department's required first stop for any
data question, but a per-URL, single-locale, arbitrary-date-range organic
funnel breakdown is not in its canned coverage today - that's a documented
gap, the same shape of gap `/organic-dashboard` already carries for its
Business Impact / Content pages. Try it first anyway (coverage changes over
time); fall back to `/data-agent` and note the gap in your run summary rather
than silently skipping the required-first-stop step.

## Why organic search is one combined channel here

The Non-Brand vs. Brand `channel_group` classification is unreliable for
localized (`/de/`) pages - it was built against English-language query
patterns and misclassifies German-language brand/non-brand queries. Splitting
it out would present a confident-looking but wrong mix. Report organic search
(Non-Brand + Brand + LLM) as **one combined channel per URL** instead, and
carry the explanatory callout (baked into
`.claude/skills/seo-de-report/scripts/build_report.py`'s default
`channel_note`) so a reader understands why this differs from a topline
dashboard that still splits Non-Brand/Brand for non-localized pages. File the
underlying classification bug with the Data Team via `/data-team-request` if
it hasn't been filed yet; link the ticket here once it exists.

## Excluded URLs

Some `/de/...` paths are confirmed non-indexed and cannot legitimately
receive organic search traffic. Any visits attributed to organic search on
one of these is a tracking/attribution artifact, not real demand - **exclude
them from the pull entirely** (drop the row before shaping the render
script's input; don't merge their numbers into another URL, and don't leave
them in the table at zero-out).

| URL | Reason | Confirmed |
|---|---|---|
| `/de/home` | Non-indexed page, not eligible for organic search traffic. Earlier revisions of this skill mistakenly treated it as a legitimate second homepage variant (see git history) - that was wrong. Its Jul 2026 numbers (117 visits, 23 sign-ups) were a tracking artifact, not real organic demand. | 2026-08-06, confirmed by Amir |

If a future pull shows renewed non-zero organic traffic to an excluded URL,
don't silently drop it without comment - note it in the run's Step 5 summary
(the page may have gotten indexed, or the same artifact recurred) so a human
can decide whether the exclusion still holds.

## Safeguards

1. **Apply the Excluded URLs list before anything else** - filter those rows
   out of the raw pull first, then compute totals/movers/the per-URL sum
   check below. Excluding *after* computing the topline will make safeguard
   #3 below fail for the wrong reason.
2. **Canonicalize NULL/empty `clean_url_path` the same way the organic
   dashboard does** (see its safeguard #1-2) before filtering to `/de` -
   dropping NULLs can hide the real homepage row entirely.
3. **Per-URL sum (after exclusions) must foot to the topline total** for
   each period. If it doesn't, that's a data-quality signal - investigate
   before publishing, per `references/evidence-standards.md`'s
   never-silently-pick rule.
4. **Equal-length periods only.** The render script's schema takes
   `current`/`prior` blocks - it has no concept of period length, so getting
   this right is entirely the data-pull step's job. A partial current month
   compared to a complete prior month must be labelled, not silently
   presented as a like-for-like MoM change.
5. **Freshness.** Snowflake rebuilds daily (dbt), data lands ~D-1. For a
   "most recent completed month" default range, confirm the month is
   actually fully closed (today's date is past the 1st of the following
   month) before pulling - this is why the cloud routine runs a few days into
   the new month rather than on the 1st.
6. **A URL that looks like a variant is a hypothesis, not a fact, until
   confirmed.** `/de/home` above is now confirmed excluded. If a future run
   turns up another `/de/...` path that looks like a duplicate, test page, or
   non-indexed variant, surface it for human confirmation rather than
   silently merging or excluding it yourself - the same rule the organic
   dashboard follows for unconfirmed variants.

## The render script

`scripts/build_report.py` is the single source of truth for the report's
layout, styling, and interactivity (KPI tiles, the mover bar chart, the
sortable/searchable table, both light and dark themes, the embedded
Instrument Sans variable font at `assets/InstrumentSans-subset.woff2`). It
takes already-shaped numbers and never invents or queries anything itself -
all it does is render. If the look needs to change, edit this script once
rather than hand-rolling a report per run.

```bash
python3 .claude/skills/seo-de-report/scripts/build_report.py <input.json> <output.html> --csv <output.csv>
```

### Input JSON schema

```json
{
  "locale": "/de/",
  "period_a_label": "July 2026",
  "period_b_label": "June 2026",
  "period_a_short": "Jul",
  "period_b_short": "Jun",
  "period_range_note": "Jul 1-31, 2026 vs Jun 1-30, 2026",
  "source_note": "Snowflake organic funnel export",
  "generated_note": "Generated Aug 6, 2026",
  "channel_note": "<optional override of the default classification-bug callout HTML; omit to use the default>",
  "records": [
    {
      "url": "/de",
      "current": {"visits": 1621, "signups": 391, "subs": 27, "mrr": 858.99},
      "prior":   {"visits": 1901, "signups": 492, "subs": 60, "mrr": 1952.56}
    }
  ]
}
```

**Trust boundary:** every field above except `channel_note` is treated as
plain text and HTML-escaped by the script before rendering - safe even if a
`records[].url` or a label came from data with HTML/script metacharacters in
it (e.g. a crawler-logged query string). `channel_note` is the one deliberate
exception: it's rendered as raw HTML so the classification-bug callout can
carry markup. Only pass a `channel_note` you or the skill authored yourself
for this run - never forward third-party or user-submitted text into it.

Do not pass a grand total - the script sums `records` itself, which is also
how safeguard #3 (per-URL sum vs. topline) gets checked: if your topline pull
disagrees with the script's summed total, that mismatch is the signal.

The script also emits the CSV with the same delta/percent columns the pilot
run's spreadsheet used, so a person who wants raw numbers in a sheet gets the
identical figures the HTML shows.

### Font asset

`assets/InstrumentSans-subset.woff2` is a Latin-only (ASCII) subset of the
real Instrument Sans variable font (weight range 400-700), per
`riverside-brand-guidelines` ("fallback to system fonts only if the real font
is technically impossible" - it isn't; this proves it). URL paths and report
copy are ASCII-only today; if a future run needs to render non-ASCII text
(e.g. a German-language page *title* rather than its path), re-subset the
font with a wider Unicode range rather than silently falling back - see the
pilot run's font-fetch steps (fetched from the `google/fonts` GitHub repo,
subset with `fonttools`) if you need to regenerate it.

## Cloud routine trigger

The monthly refresh is wired as a Routine, self-bound to the session that
created it (not `create_new_session_on_fire`) - this org has disabled
per-trigger MCP connector grants, so a fresh-session routine would start with
no Omni/Snowflake access at all. Self-binding keeps the routine inside a
session that already has that connector live, at the cost of resuming a
conversation each month rather than starting clean. Runs the default date
range on the 3rd of each month. Check
`mcp__Claude_Code_Remote__list_triggers` for the live `trigger_id`/cadence if
you need to edit or disable it; it is not duplicated here to avoid a second,
driftable copy of the same fact. If this org ever re-enables per-trigger
connector grants, switching to `create_new_session_on_fire` (with the
`Omni Analytics` connector attached and `notifications: {push: true}`) is the
better long-term shape - it isn't tied to one person's session.
