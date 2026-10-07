# Invoice inbox to monday - Nir profile (tracking & config)

Profile state file for the `invoice-inbox-to-monday` skill, **Nir Taranto's** run. Same skill logic as the default (`tracking.md`, Hanan's run), same destination board - only the source mailbox, ledger, recipient, and two policy knobs differ. The skill reads and rewrites this file on every run of the Nir profile. Add to the Vendor routing map freely; do not hand-edit the Processed ledger during a run.

## Config

| Key | Value |
|-----|-------|
| Profile | `nir` |
| Gmail account | Nir Taranto's mailbox - the authenticated Gmail connector account for this run (do not assume Hanan's) |
| Gmail label (display name) | `invoices` |
| Gmail label ID (cached) | `Label_8914995401352105344` (resolved 2026-08-09; note: `label:<id>` queries return nothing in this connector - filter fetched threads by the `labelIds` field, or query by display name `label:invoices`) |
| Board | `18390740532` (Invoices and Payments - Growth Marketing) - **same board as Hanan's profile** |
| Summary recipient (Slack ID) | `U07LETHMPAP` (Nir Taranto) |
| Window start | `2026/06/01` (first-run backfill; later runs: last run minus 14-day grace) |
| Last run | _never_ |
| Month rule | Invoice date on the document; fall back to email received date + flag |
| **summary_mode** | `exceptions-only` (see Policy knobs) |
| **low_conviction** | `ask` (see Policy knobs) |

## Policy knobs (this profile only)

These two knobs are what make the Nir profile behave differently from Hanan's default. The skill logic is otherwise identical.

- **`summary_mode: exceptions-only`** - the weekly DM is a *decision queue*, not a receipt. Send a DM **only** when there is something Nir needs to see: an item held for his call, a needs-review item, a skip, or a failure. If the run filed only clean, confident invoices (or filed nothing), send **no** DM. (Hanan's default is the fuller summary.) To switch to a receipt of every run, set this to `full`.
- **`low_conviction: ask`** - when the skill is **not** highly confident, it does **not** guess and does **not** silently file blanks. Low-conviction triggers: vendor not identifiable, **vendor not on the routing map** (so Type / Payed by / Payment Method are unknown), amount or currency not cleanly readable, or a duplicate that is ambiguous.
  - **Interactive run** (Nir triggers it): stop and ask Nir before writing that item.
  - **Scheduled/headless run** (nobody at the keyboard): file the confident invoices, **hold** each uncertain one (do not create it with guessed/blank routing), record it in the ledger as `held-needs-nir`, and list it in the DM under "need your call." Re-surface held items every run until Nir resolves them; once he answers, file them and (when he gives a routing) append the mapping below. (Hanan's default files unmapped vendors with the routing columns left blank and flags them - it does not hold.)

## Board structure (shared - see `tracking.md`)

Group IDs, column keys, column value formats, the Type label IDs, and the Invoice-vs-Receipt doc-type rule are **identical to Hanan's profile because it is the same board**. Do not duplicate them here - read them from `tracking.md` (verified against the live board 2026-08-09). Key ones the skill needs most:

- Invoice file column `file_mky9xwjy`; Receipt file column `file_mm569fkh`.
- Month groups exist through October 2026; create-and-cache new months as needed (title format `November 2026`).
- Never touch the `Emailed items` group (`group_mm1fdkmn`) or other people's items.

## Vendor routing map (Nir profile)

Nir's invoices may be a different vendor set than Hanan's. Seeded as a convenience from the shared map; unmapped vendors trigger the `low_conviction: ask` path above rather than filing blank. Append confident mappings as Nir confirms them (`vendor X -> Type Y, paid by Z, method W`).

| Vendor matches | Type label (ID) | Payed by (monday user ID) | Payment Method |
|----------------|-----------------|---------------------------|----------------|
| _(none confirmed yet - the profile is new; the first real invoices will populate this)_ | | | |

## Processed ledger (Nir profile)

Separate ledger from Hanan's. Any Gmail message ID here has been handled and is never re-filed, EXCEPT `filed-no-pdf` and `held-needs-nir` (both re-surface). Statuses: `filed`, `receipt-attached`, `filed-no-pdf`, `held-needs-nir` (waiting on Nir's decision - re-listed every run until resolved), `needs-review`, `skipped-duplicate`, `skipped-unidentifiable`.

| Gmail message ID | Vendor | Invoice # | monday item ID | Status | Date |
|------------------|--------|-----------|----------------|--------|------|
| _(empty - no runs yet)_ | | | | | |

## Summary DM template (exceptions-only)

Slack mrkdwn, no em dashes, footer mandatory. Sent only when there is at least one exception (held / needs-review / skip / failure). `{CURRENCY}` is the invoice's actual currency (`USD` when unstated).

```text
:receipt: *Invoice agent - Nir profile* ({DATE})
Filed {N} invoice(s) cleanly. {M} need your call :point_down:

{per held item: • *{Vendor}* - {SUM} {CURRENCY} - {what I need from you, e.g. "not on your routing map - who pays this and how?"} - <{thread link}|email>}

{if any: :warning: *Needs manual review*
{per item: • *{Vendor}* - {what is missing} - <{item link}|open>}}

{if any: Skipped / failed: {reasons}}

_Posted by the Marketing OS agent_
```
