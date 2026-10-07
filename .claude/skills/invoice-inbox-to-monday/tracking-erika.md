# Invoice inbox to monday - Erika profile (tracking & config)

Profile state file for the `invoice-inbox-to-monday` skill, **Erika Varangouli's** run. Same skill logic as the default (`tracking.md`, Hanan's run), same destination board - only the source mailbox, ledger, recipient, and policy knobs differ. The skill reads and rewrites this file on every run of the Erika profile. Add to the Vendor routing map freely; do not hand-edit the Processed ledger during a run.

**This profile runs in Erika's own environment against her own connected Gmail.** It only reads the intended mailbox when the authenticated Gmail connector for the run is `erika.varangouli@riverside.com`. If a different account is connected, stop and surface it - do not file another mailbox's invoices under this profile. See the Setup section for the one-time steps only Erika (or someone acting in her environment) can complete.

## Config

| Key | Value |
|-----|-------|
| Profile | `erika` |
| Gmail account | `erika.varangouli@riverside.com` - the authenticated Gmail connector account for this run (do not assume Hanan's `@riverside.fm`) |
| Gmail label (display name) | `Invoices` |
| Gmail label ID (cached) | _unresolved - resolve on first run via `list_labels` (match display name `Invoices`) and write the ID back here; note: `label:<id>` queries return nothing in this connector - filter fetched threads by the `labelIds` field, or query by display name `label:Invoices`_ |
| Board | `18390740532` (Invoices and Payments - Growth Marketing) - **same board as Hanan's and Nir's profiles** |
| Summary recipient (Slack ID) | `U06R47T4ASJ` (Erika Varangouli) |
| Window start | `2026/06/01` (first-run backfill; later runs: last run minus 14-day grace). The Gmail `Invoices` label, not this window, is the real filter - only emails Erika has labeled are considered. |
| Last run | _never_ |
| Month rule | Invoice date on the document; fall back to email received date + flag |
| **summary_mode** | `full` (see Policy knobs) |
| **low_conviction** | `file-blank-and-flag` (see Policy knobs) |
| **default_payed_by** | Erika Varangouli (monday user `58104737`) (see Policy knobs) |

## Policy knobs (this profile only)

- **`summary_mode: full`** - DM Erika a summary of **every** run's results (per the template below). Stay silent only on a fully-empty run (zero filed, zero problems). This matches Hanan's default profile.
- **`low_conviction: file-blank-and-flag`** - when a vendor is not on the routing map, still file the item, leave **Type** and **Payment Method** blank, and flag it in the summary. Do not hold. (Guardrail 2 - never invent data - still applies: amounts/dates come only from the PDF or email, never a guess.)
- **`default_payed_by: Erika Varangouli (58104737)`** - fill the **Payed by** column with Erika on **every** item this profile files, so all of her invoices land under her name - even for vendors not yet on the routing map. If a vendor is ever given an explicit `Payed by` in the routing map below, that explicit value overrides this default for that vendor. This knob defaults the Payed by person only; **Type** and **Payment Method** are never defaulted.

Net effect for an unmapped vendor under this profile: item created, **Payed by = Erika**, Type and Payment Method blank, flagged in the summary so Erika can map it (append the mapping once known).

## Board structure (shared - see `tracking.md`)

Group IDs, column keys, column value formats, the Type label IDs, and the Invoice-vs-Receipt doc-type rule are **identical to Hanan's profile because it is the same board**. Do not duplicate them here - read them from `tracking.md`. Key ones the skill needs most:

- Invoice file column `file_mky9xwjy`; Receipt file column `file_mm569fkh`.
- Payed by column `multiple_person_mkz6t3jw` (format `{"personsAndTeams":[{"id":58104737,"kind":"person"}]}` for the Erika default).
- Month groups exist through October 2026; create-and-cache new months as needed (title format `November 2026`).
- Never touch the `Emailed items` group (`group_mm1fdkmn`) or other people's items.

## Vendor routing map (Erika profile)

Erika owns SEO & AI Search; her invoices are likely SEO tools/vendors, a different set than Hanan's paid/creator vendors. Starts empty and self-populates. Because `default_payed_by` is set, **Payed by is Erika on every item regardless of this map** - so this map only needs to supply **Type** and **Payment Method** per vendor. Append confident mappings as Erika confirms them (`vendor X -> Type Y, method W`); an explicit `Payed by` here would override the Erika default for that vendor only.

| Vendor matches | Type label (ID) | Payed by (monday user ID) | Payment Method |
|----------------|-----------------|---------------------------|----------------|
| _(none confirmed yet - the profile is new; the first real invoices will populate this)_ | | | |

## Processed ledger (Erika profile)

Separate ledger from Hanan's and Nir's. Any Gmail message ID here has been handled and is never re-filed, EXCEPT `filed-no-pdf` (re-surfaces for upload retry). Statuses: `filed`, `receipt-attached`, `filed-no-pdf`, `needs-review`, `skipped-duplicate`, `skipped-unidentifiable`.

| Gmail message ID | Vendor | Invoice # | monday item ID | Status | Date |
|------------------|--------|-----------|----------------|--------|------|
| _(empty - no runs yet)_ | | | | | |

## Summary DM template (full)

Slack mrkdwn, no em dashes, footer mandatory. `{CURRENCY}` is the invoice's actual currency (`USD` when unstated).

```text
:receipt: *Invoice agent - Erika profile* ({DATE})
Filed {N} invoice(s) to the Invoices and Payments board :moneybag:

{per invoice: • *{Vendor}* - {SUM} {CURRENCY} - {Month group} - <{item link}|open>}

{if any: :warning: *Needs a vendor mapping* (filed under your name, Type/Payment Method blank)
{per item: • *{Vendor}* - <{item link}|open>}}

{if any: :warning: *Needs manual review*
{per item: • *{Vendor}* - {what is missing} - <{item link}|open>}}

{if any: Skipped: {reasons}}

_Posted by the Marketing OS agent_
```

## Setup (one-time, in Erika's environment)

These steps cannot be done from another person's session - they need Erika's own Claude Code environment and her Gmail. Do them once, then the weekly routine is autonomous.

1. **Clone / pull the repo** on Erika's machine (she has `riversidefm/marketing-brain` access) so `.claude/skills/invoice-inbox-to-monday/` (including this file) is present.
2. **Connect her Gmail** in claude.ai connector settings, authenticated as `erika.varangouli@riverside.com`. This is the mailbox the run reads - the skill does not switch accounts.
3. **Create the Gmail label `Invoices`** and apply it to invoice emails (going forward, and to any past invoices she wants backfilled - the label, not the date window, is what the skill files). A Gmail filter that auto-labels known invoice senders keeps it hands-off.
4. **First run interactive**, in Erika's environment: `/invoice-inbox-to-monday` naming the `erika` profile (read `tracking-erika.md`). This resolves and caches the label ID above, backfills labeled invoices, and confirms the board writes look right before going headless.
5. **Register the weekly scheduled task** in Erika's environment (recommended: Monday ~08:00 Europe/London - she is UK-based and Sunday is her day off, unlike the Israel-team Sunday runs). Task prompt:

   > You are the Marketing OS agent running the weekly invoice filing routine for the **Erika profile** (scheduled headless run). Work in the marketing-brain repo on this machine and first `git pull` on main. Then execute the `/invoice-inbox-to-monday` skill exactly as written in `.claude/skills/invoice-inbox-to-monday/SKILL.md`, using the **`tracking-erika.md`** profile: read it for config (Gmail account `erika.varangouli@riverside.com`, `Invoices` label, board `18390740532`, recipient Slack `U06R47T4ASJ`, window start, the `summary_mode: full` / `low_conviction: file-blank-and-flag` / `default_payed_by: Erika (58104737)` knobs) and its Processed ledger. Confirm the connected Gmail is Erika's before fetching; if it is not, stop and report it. Fetch labeled invoice emails in the window, read each invoice PDF for the real amount/currency/date (never guess), dedupe against the ledger and board, create one item per new invoice in the invoice-date month group with the agent-writable columns filled - Payed by from the vendor's routing-map entry when it specifies one, otherwise Erika per `default_payed_by` (so unmapped vendors still land under Erika); Type and Payment Method only from the routing map - then attach the invoice PDF to the Invoice column (`file_mky9xwjy`). Handle paid receipts per the skill's Invoice-vs-Receipt rule: attach a receipt to its matching existing invoice item's Receipt column (`file_mm569fkh`) instead of creating a duplicate invoice item, and for an unmatched receipt do exactly what that rule says (do not invent alternate handling here). Never touch the Emailed items group, and do not otherwise edit existing items (attaching a paid receipt to its own invoice item is the one allowed edit). DM Erika the full-summary per the template in `tracking-erika.md` (Slack mrkdwn, no em dashes, footer `_Posted by the Marketing OS agent_`). Append filed invoices to the ledger, update last-run date, commit and push (`invoice-inbox-to-monday: filed N invoices - erika profile`). Output a short run report.
