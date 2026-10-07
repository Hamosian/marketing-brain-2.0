# Growth Reporting (Nir's report library)

> The weekly and monthly reports Nir Taranto receives across his Growth functions: where they are indexed, how the cadence runs, and the shared grammar they use. Consumed by `/chief-of-staff` (daily orchestration) and `/nir-monthly-report` (which generates the MOPs monthly). This is a pointer and a schema, not a copy: live reports live on the Monday board and in Google Drive and go stale here, so read them from source, do not transcribe numbers into this file.

## The hub: Growth Marketing Reports board (`18395106969`)

This Monday board is the single source of truth for the reporting cadence. Created and owned by **Dor Druker** (Growth Channels Lead, departed 2026-08-04); **Savion Ron Shemesh** now covers Growth Channels reporting on top of Creator Marketing. Board is in the Growth Channels workspace (`13382295`). The process, stated in the board description, is:

1. Write the report in a Google Doc.
2. Upload it to the correct weekly (or monthly) folder in the shared Drive.
3. Add the Google Doc link to the report's row on this board.

Each period (a week or a month) is **one top-level item** with **five subitems, one per reporting lead**. The subitems are where the actual per-function reports and their submission status live.

### Board structure

- **Groups:** `Weekly Summary` (`group_mkzhx8zc`), `Monthly Summary Report` (`group_mkzhhsvs`), `GPT` (`group_mkzhw4jh`, holds the ChatGPT report-builder assistants the team uses, external chatgpt.com links).
- **Top-level item = one period.** Named by date: weeklies as `DD.MM.YY` (e.g. `25.06.26`), monthlies as `<Month> YYYY Summary` (e.g. `June 2026 Summary`).
- **Top-level columns:** `status` (Working on it `0` / Done `1` / Stuck `2`), `date4` (the report's target date), `doc_mkzhgg7s` ("Report Link G-Drive", sometimes a consolidated Monday Doc), `link_mkzh9z39` (Link).

### Subitems board (`18395107181`) - one report per lead

Every period item has five subitems, one per Nir direct report who files:

| Subitem | Lead | Function |
|---------|------|----------|
| Dor | Savion Ron Shemesh (covering since Dor Druker's departure, 2026-08-04) | Growth Channels (PLG vendors, affiliates, B2B pipeline) |
| Raz | Raz Navon | Paid Acquisition (brand + non-brand PPC, budget, CRO, creative) |
| Savion | Savion Ron Shemesh | Creator Marketing |
| Erika | Erika Varangouli | SEO & AI Search |
| Hanan | Hanan Amos | Marketing Operations + Website |

**Transition note (2026-08-04):** the subitem is still literally named "Dor" on the Monday board until someone renames it - don't assume the label has changed just because the reference has. Savion now files both the Growth Channels and Creator Marketing subitems for each period.

Subitem columns: `person` (Owner), `status` (Working on it `0` / Done `1` / Stuck `2`), `link_mkzq8gn8` ("Report Link G-Drive"), `doc_mkzhpxnp` ("monday Doc"), `date_mkzk5nfa` (Date). The report doc for a function is the link on that lead's subitem; read it there rather than guessing the Drive path.

**Coverage:** five functions file (Growth Channels, Paid, Creator, SEO, MOPs+Website). **Inbound SDR is owned by Nir directly** (Ayelet Jacobson is an IC on it) and is not part of this reporting cadence, so SDR has no standalone report. Do not imply an SDR report exists.

### How to read the latest reports (do not hardcode item IDs)

1. `get_board_items_page` on `18395106969` with `includeSubItems: true`, ordered by `date4` descending (or take the most recent item in the `Weekly Summary` / `Monthly Summary Report` group).
2. The current in-progress period is the newest item whose `status` is not Done. Its subitems show, per lead, whether the report is filed (`Done`) or still outstanding (`null` / `Working on it` / `Stuck`).
3. For a filed report, follow the subitem's `link_mkzq8gn8` (G-Drive) or `doc_mkzhpxnp` (Monday Doc) to read it.

This board is also the **report-submission tracker**: which leads have filed this week and which Nir is still waiting on falls straight out of the subitem statuses.

## Where reports actually arrive: Slack (read this first)

Since Dor's departure the board and the Drive folder tree are not kept current. **Leads share their monthly report in Slack, usually a DM to Nir with a Google Doc or Claude artifact link** (August 2026: Raz 3 Sep, Erika 5 Sep, Hanan 6 Sep, Savion 10 Sep, all by DM). Weeklies by lead: **Erika** posts Claude artifacts in her DM with Nir and the SEO group DM; **Savion** shares a Google Doc titled by week ("DD/MM-DD/MM Creators"), which reaches Nir as a Drive share email; **Raz** shares the Weekly Paid Acquisition Report as a Doc, also a Drive share email; **Jarred** sends the CRO + Creative weekly by DM or Drive share. So the check is Slack DMs plus Nir's Gmail for `drive-shares-dm-noreply` and Docs comment notifications. To check who has filed, search Slack DMs and group DMs from each lead for a Doc or artifact link in the first ten days of the month; use the board and Drive only as a fallback.

## Where the report docs physically live (Google Drive)

The docs the board links to sit here. Navigate with the Drive connector only when the board link is missing.

```text
Growth marketing Reports/            1K18G3elXvPK5FycgIhBNE46l95nGvC3D
  Year 2026/                         1xQIBx2jTl3BVHW7GgR2Q9kjW-GCRPn9T
    Weekly/  1K_hciYjUVcnkr42hDGnCrMrMt_FKgwko   -> <Month YYYY>/ week <DD-DD/MM>/ docs
    Monthly/ 1594yhoxl2PO19bspOXWW2dkxMQQtRqFm   -> <Month>/ docs
```

Top-level shared folder: `1MByB7bkM6bsN59Ujx5cW5pkQY_yXmvly`. **Do not hardcode month/week folder IDs** - they rotate, duplicate, and a fresh period folder can be empty. Prefer the board's subitem links; fall back to a Drive title search (`title contains 'weekly'` / `'monthly'`, newest first) only if the board link is absent.

## Shared report grammar

Every report, weekly or monthly, follows the same skeleton. When the chief-of-staff surfaces a function, match this vocabulary so the daily brief and the periodic report read as one system.

1. **Highlights** - bold-lead bullets, each naming a metric, its move (MoM or vs target), and a one-word verdict (surging, declining, on track).
2. **Targets vs actuals** - the load-bearing table. Columns in some order of `Metric | Last Month | MTD | Projected | Target | % vs Target | % vs LM`. Everything is read against target and last month.
3. **Function deep dives** - budget vs actual by channel, cohort by channel, signups by user intent, CRO funnel (Visit->SU, SU->Trial), vendor performance, B2B pipeline (meetings booked/completed, SQLs, deals, closed won).
4. **Initiative / test status** - CRO tests as Running / Planned / Recently completed; creative pipeline as In progress / Next up / Blocked.
5. **Recruiting status** - open roles and candidate stages (Nir is often an interviewer).
6. **Insight callouts** - a short "Insight:" block under each table.
7. **Key observations and next steps** - the forward-looking list; these are the open threads to carry into the next period.
8. **Source line** - every table cites its source (Omni topic, Monday board id, HubSpot portal 9154210). Preserve these when quoting.

## KPI vocabulary Nir expects

- **Funnel:** Visit -> Signup (V->SU) -> Trial (SU->T) -> Subscription -> Paid. Always state the CVR window; never default silently (see the operating model doc).
- **Brand vs non-brand (Generic)** split is reported separately for almost every metric. Keep them apart.
- **Core metrics:** Signups, Trials, Subscriptions, New MRR (and First-month MRR / FmRR for Growth Channels vendors), CVRs, Spend, CPA / Cost-per-sub, Attainment vs target.
- **Attainment framing:** a function behind target (e.g. Growth Channels PLG at ~24% of MRR target) is a risk to surface; a function at an all-time high (e.g. non-brand MRR) is a highlight.
- **Targets** live in Nir's `targets_2026` Google Sheet (`1zgDqqQ1vaaYSUzX93cz_3oqc3PZpRfLhndwT723AicI`), SLG quarterly tab: MQL → SQL → Opportunities → Pipe Created → Win rate → Won deals → Win MRR, by `Agency-SMB`, `Agency-MM`, `Europe-SMB`, `Europe-MM`, `Europe-Ent`, `Enterprise`, per fiscal quarter. The GTM QBR table rolls these up as **Agency (SMB) = Agency-SMB + Agency-MM**, **Enterprise = Enterprise (US)**, **Europe = Europe-SMB + Europe-MM + Europe-Ent**; that mapping reproduces the Q1 FY26 QBR target column to the dollar (verified 2026-09-07). Actuals for the same table come from the Omni `Sales rollover` topic (`systems/owned/omni-bi.md` → QBR basis). Budgets come from the "2026 Budget Skill" the reports cite. Do not invent targets.

## Cadence

- **Weekly: retired (Nir, 2026-09-17).** The weeklies are folded into the monthly. The weekly cadence and its Drive folder tree lapsed after Dor's departure (2026-08-04) and were not rebuilt, so do not chase or expect a weekly unless Nir restarts it (`/chief-of-staff`, Friday report-submission check). Historically a new item appeared in the `Weekly Summary` group each week and the five leads filled their subitems.
- **Monthly:** a `<Month> Summary` item is created in the first days of the following month (June 2026 Summary was targeted Jul 6). The MOPs monthly is automated (`/nir-monthly-report`, moved to monthly on 2026-07-05 at Nir's request).

## How Claude should use this

- **Consume, do not duplicate.** The chief-of-staff daily brief references the latest report per function (headline metric vs target, plus open next-steps) and links to it via the board. It does not recompute funnel numbers - route any real data question to `/rivermind:ask`.
- **Track submission.** From the current period's subitems, tell Nir which leads have filed and which are outstanding - a ready-made chase list near the weekly/monthly deadline. The `/chief-of-staff` **Friday run automates this check and the chase**: weekly on most Fridays, monthly on the first Friday of the month, auto-DMing any missing lead (Israel leads to file first thing Sunday, Erika on Friday since she is UK-based). See the "Friday report-submission check" step in `.claude/skills/chief-of-staff/SKILL.md`.
- **Carry forward next-steps.** The "Key observations and next steps" list from the last report is a running set of threads; surface the ones that need Nir (a budget decision, a recruiting interview, a CRO test awaiting a call, an attribution gap to resolve).
- **Anchor org pulse to targets.** Read each function against its target where a recent report gives one; behind-target functions are risks.
- **Flag cadence.** Near a period deadline, note reports are due, show the submission tracker, and offer to help assemble (MOPs monthly -> `/nir-monthly-report`).
