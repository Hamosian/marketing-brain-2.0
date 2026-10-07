# Nir Weekly Report - config and schema

Heavy reference for `/nir-weekly-report`. The `SKILL.md` body stays lean and
points here. IDs live here (and in `references/`), never inlined in `CLAUDE.md`.

## Reporting period

- The report covers the **most recently completed work week**, Sunday to Thursday
  (Israeli work week). If run mid-week, still report the last *completed* week
  unless the user names a different week.
- **Doc label** uses the Sunday-to-Friday range to match the prior reports'
  wording, e.g. `Week of July 12 to 17, 2026`.
- **Board item name** uses the week's **Thursday** in `DD.MM.YY`, e.g. `16.07.26`
  (this is the board's own convention; the two labels are intentionally
  different).

## Source boards and groups (resolve group IDs dynamically, never hardcode)

| Board | ID | What to pull |
|-------|----|-------------|
| MOPs (Marketing Operations Tasks) | `6257866754` | the weekly group covering the report week, plus the `Nir's Requests` and `Open Tests` groups |
| Website Dev ("DEV") | `18397093471` | the current bi-weekly sprint group covering the report week, plus the next sprint group for priorities |
| Growth Marketing Reports (filing target) | `18395106969` | where the report is filed; group `Weekly Summary` = `group_mkzhx8zc` |
| Subitems of Growth Marketing Reports | `18395107181` | Hanan's per-lead subitem lives here |

- **MOPs** groups are weekly, named `DDMM - DDMM` (e.g. `1207 - 1607`). Call
  `get_board_info` and select the group whose range covers the report week.
  Pull each candidate group **separately** so you keep clean group membership -
  a merged multi-group pull mixes in historical `Nir's Requests` / `Open Tests`
  items and you lose the week boundary.
- **DEV** groups are bi-weekly sprints named `DD.MM.YY - DD.MM.YY`. Pick the
  sprint covering the week (delivered / in progress) and the next sprint (feeds
  priorities). Restrict columns to `name`, `person`, `status`, `date4` to stay
  under the response cap.
- **Status semantics** for both boards: reuse the tables in
  `.claude/skills/nir-monthly-report/SKILL.md` (MOPs: Done=`1`; DEV: Done=`1`,
  Published=`8`). Do not re-derive them.

## Slack channels (enrich, do not duplicate the board)

Search each for the report week (`after:` / `before:` the Sun-Fri dates),
`slack_search_public_and_private`, sorted by timestamp.

| Channel | ID | Mine for |
|---------|----|---------|
| `#website-dev` | `C0AM2HQMY49` | go-lives, prod deploys, blockers |
| `#mops-priority-room` | `C0A9JUG9MPZ` | high-priority items, blockers |
| `#mops-team-internal` | `C0AAQ15SVD3` | the daily MOPs standup posts summarize the week well; Hanan's own overdue P1s live here |
| `#marketing-internal` | `C043B7GAMPC` | launches worth a glance; keep Brand/PMM launches **out** of Hanan's function report |

## Riverside brand for the Google Doc

Source of truth: `references/design-system/` and the `riverside-brand-guidelines`
skill. Tokens used in the report:

```
PURPLE     = 7848FF   (primary.c800 - section headers, "Riverside" wordmark, function line)
NEAR_BLACK = 151515   (title + body)
GRAY       = 555555   (subtitle / meta)
FONT       = Instrument Sans   (whole document)
```

### Build method (verified reliable)

Google Drive `create_file` converts uploaded **HTML** to a Google Doc while
preserving inline styles, so build the report as HTML with inline CSS and upload
it - do not upload a plain-markdown doc (that lands unbranded), and do not
hand-transcribe base64 for a `.docx`.

1. Assemble HTML: a purple `Riverside | Weekly Task Report` wordmark line, a
   28pt near-black `Weekly Task Report` title, the Sun-Fri week line (gray), the
   purple `Marketing Operations + Website Development` line, then each section as
   an `h2` in purple `#7848FF` (16pt, with a `border-bottom`), sub-headers
   (`Marketing Ops` / `Website Dev`) as bold near-black `h3`, and `<ul>` bullets
   in Instrument Sans near-black.
2. `create_file` with `contentMimeType: "text/html"`, conversion left on,
   `title: "MOPs Weekly Report YYYY-MM-DD_to_YYYY-MM-DD"`.
3. **Folder:** place it in the same Weekly Drive folder as the previous week's
   report. Find that folder via the prior week's Hanan subitem doc link
   (`get_file_metadata` -> `parentId`); do not hardcode folder IDs (they rotate,
   see `references/growth-reporting.md`).
4. **Verify** the styling survived: `download_file_content` as `text/html` and
   confirm `#7848ff` and `Instrument Sans` are present before filing.

## Filing on the Growth Marketing Reports board

Growth Marketing Reports board `18395106969`, group `Weekly Summary`
(`group_mkzhx8zc`).

1. **Top-level item:** name = the week's Thursday `DD.MM.YY`. Create it in the
   Weekly Summary group if it does not already exist.
2. **Hanan subitem:** create `Hanan` under it (or reuse the existing one). Columns
   on the subitems board `18395107181`:

   | Column id | Type | Value |
   |-----------|------|-------|
   | `person` | people | Hanan Amos (monday user id `97582758`; confirm via `references/team.md`) |
   | `status` | status | `{"label":"Done"}` |
   | `link_mkzq8gn8` | link | `{"url": <doc url>, "text": "Google Docs"}` ("Report Link G-Drive") |
   | `date_mkzk5nfa` | date | `{"date":"YYYY-MM-DD"}` (the week's Thursday) |

3. Leave the top-level item's `status` unset (other leads fill their own
   subitems; matches how recent weeks were left).

## Idempotency (safe re-runs)

- If the week's `DD.MM.YY` item already exists, **reuse it** - do not create a
  duplicate.
- If Hanan's subitem already exists, **update** `link_mkzq8gn8` (and `status`)
  in place rather than adding a second subitem.
- The board also auto-creates the other four leads' subitems in some weeks; only
  ever create/touch the **Hanan** subitem.

## Relationship to /nir-monthly-report

Distinct artifacts. `/nir-monthly-report` produces the automated MOPs **task
report** that moved to a monthly cadence on 2026-07-05. This skill produces the
**weekly narrative** Hanan files on the Growth Marketing Reports board as one of
five reporting leads (see `references/growth-reporting.md`) - a live weekly
cadence. They do not conflict.
