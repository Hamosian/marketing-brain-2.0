# Invoice inbox to monday - tracking & config

State file for the `invoice-inbox-to-monday` skill. The skill reads and rewrites this file on every run. Add to the Vendor-to-Type map freely; do not hand-edit the Processed ledger during a run.

## Config

| Key | Value |
|-----|-------|
| Gmail account | `hanan.amos@riverside.fm` |
| Gmail label (display name) | `Invoices` |
| Gmail label ID (cached) | `Label_5043835231319327223` (resolved 2026-07-06; note: `label:<id>` queries return nothing in this connector - filter fetched threads by the `labelIds` field instead) |
| Board | `18390740532` (Invoices and Payments - Growth Marketing) |
| Summary recipient (Slack ID) | `U0A3HCFE90S` (Hanan Amos) |
| Window start | `2026/09/13` (last run minus 14-day grace) |
| Last run | `2026-09-27` |
| Month rule | Invoice date on the document; fall back to email received date + flag |

## Month group IDs (cached from board, verified 2026-07-06)

Create-and-cache new months as needed (title format `July 2026`).

| Group | ID |
|-------|----|
| Emailed items (NEVER touch) | `group_mm1fdkmn` |
| October 2026 | `group_mm44behc` |
| September 2026 | `group_mm44f7hj` |
| August 2026 | `group_mm32zwk7` |
| July 2026 | `group_mm3018fc` |
| June 2026 | `group_mm301gh8` |
| May 2026 | `group_mm2dhppr` |
| April 2026 | `group_mm0mheg5` |
| March 2026 | `group_mm0mrpwe` |
| February 2026 | `group_mm05jajx` |
| January 2026 | `group_title` |
| December 2025 | `topics` |

> `group_title` and `topics` look like placeholders but are the real group IDs returned by `get_board_info` - they are monday's default IDs for a board's original groups. Do not "fix" them.

## Column keys (cached from board, verified 2026-07-06)

| Column | Key | Agent writes? |
|--------|-----|---------------|
| Name | `name` | yes |
| Company name | `text_mm4ecyyd` | yes |
| Invoice number | `text_mm4ec06z` | yes |
| Invoice Sum ($, bare number) | `numeric_mky9safm` | yes |
| Contact Email | `email_mm01ykcb` | yes (format `{"email","text"}`, both required) |
| Tax id | `text_mm4eafd8` | yes (from PDF) |
| Website | `link_mm4ep17t` | yes (format `{"url","text"}`, from PDF) |
| Overview | `long_text_mm4ednzr` | yes |
| Invoice (file) | `file_mky9xwjy` | yes (auto-upload; use for unpaid invoices / proformas) |
| Receipt (file) | `file_mm569fkh` | yes (auto-upload; use instead of Invoice column when the document is a paid receipt - see doc-type rule below) |
| Type | `color_mm0e2221` | only from routing map |
| Payed by | `multiple_person_mkz6t3jw` | only from routing map (format `{"personsAndTeams":[{"id","kind":"person"}]}`) |
| Payment Method | `dropdown_mky9maht` | only from routing map (format `{"labels":[...]}`) |
| Email (secondary) | `email_mm4e7cy5` | no (use Contact Email) |
| Invoice Uploaded | `status` | never |
| Date Paid | `date4` | never |
| Payment Done | `boolean_mky9pwjm` | never |
| W8/W9 / Agreement / Campaign Name | `file_mm01zvvw` / `file_mm2td471` / `color_mm0m1sj` | never |

### Invoice vs Receipt - two documents, ONE task item (doc-type rule)

Green Invoice / morning.co sends two kinds of document for the same purchase, and they belong on the **same** board item - one per invoice, never one for the invoice and a second for its receipt:

- **Unpaid invoice / proforma** (subject `Invoice NNNNN` or `Proforma Invoice NNNNN`; a request for payment, no `Payments Details` section) -> this is what **creates** the task item. Attach the PDF to the **Invoice** column (`file_mky9xwjy`), fill amount/vendor/routing as usual. Default flow.
- **Paid receipt** (subject `Invoice / Receipt NNNNN` or `Receipt NNNNN`; the PDF has a `Payments Details` section showing the payment already made, e.g. "Wire transfer ... USD 2,800.00", and a line `Invoice / Receipt for Proforma Invoice MMMMM`) -> the invoice item already exists. **Do not create a new item.** Find the existing item and attach the receipt PDF to its **Receipt** column (`file_mm569fkh`).

**Matching a receipt to its invoice item.** The receipt PDF names the invoice it settles: `Invoice / Receipt for Proforma Invoice MMMMM`. That `MMMMM` is the Invoice number on the existing item (not the receipt's own number NNNNN). Search the board (ITEMS) for `MMMMM`, confirm the same vendor, and attach to that item's Receipt column. If the receipt names no invoice number, match by vendor + amount + month. Only if **no** matching invoice item exists on the board do you create one (invoice-less receipt): create it in the receipt-date month group with the PDF in the Receipt column and the Invoice column empty, and flag it in the summary so finance knows the invoice never arrived.

Leave the payment-status columns (`status`, `date4`, `boolean_mky9pwjm`) untouched - the paying humans set those. Attaching the receipt does not change the invoice item's amount, routing, or group.

### Type label IDs (column `color_mm0e2221`)

Creators Freelancer / Platform Fees `3`, Gifting `4`, Events `6`, B2B Vendors `7`, Freelance `8`, Affiliate Vendors `9`, Affiliates `11`, Review Platforms `12`, SEO `13`, Organic `14`, partnerships `15`, Creators `16`, Affiliate (Freelance and Platforms) `18`. (Verified live 2026-10-04: `10` Affiliate Networks and `17` Creators (Affiliates) RW no longer exist on the board; affiliate platforms and freelancers are filed as `18`.)

## Vendor routing map

Seeded from board history and owner input (2026-07-06). The skill fills **Type**, **Payed by**, and **Payment Method** only from this map; blank cells stay blank on the item. Append confident new mappings (e.g. when the owner says "vendor X belongs to Y, paid by Z"); when unsure, leave the cell blank.

| Vendor matches | Type label (ID) | Payed by (monday user ID) | Payment Method |
|----------------|-----------------|---------------------------|----------------|
| Capterra | Review Platforms (`12`) | | |
| G2 | Review Platforms (`12`) | | |
| TrustPilot | Review Platforms (`12`) | | |
| SoftwareSuggest | Review Platforms (`12`) | | |
| Saasworthy | Review Platforms (`12`) | | |
| MVF | Review Platforms (`12`) | | |
| impact.com | Affiliate (Freelance and Platforms) (`18`) | | |
| Saasmart | Affiliates (`11`) | | |
| Boscia Group | B2B Vendors (`7`) | | |
| MemoryBlue | B2B Vendors (`7`) | | |
| LUPO-DIGITAL | | Savion Ron Shemesh (`77907878`) | |
| MVP GROW | | Hanan Amos (`97582758`) | Bank Transfer |

## Processed ledger

Any Gmail message ID here has been handled and is never re-filed, EXCEPT `filed-no-pdf` (see below). Status: `filed` (item created, PDF attached), `receipt-attached` (a paid receipt attached to an existing invoice item's Receipt column - the recorded item ID is that pre-existing invoice item, no new item was created), `filed-no-pdf` (item created, PDF upload pending - next run retries the upload to the recorded item ID, never re-creates the item), `needs-review` (item created with gaps), `skipped-duplicate`, `skipped-unidentifiable`.

| Gmail message ID | Vendor | Invoice # | monday item ID | Status | Date |
|------------------|--------|-----------|----------------|--------|------|
| 19f36099fca273eb | LUPO-DIGITAL LTD | 50098 | 12452520069 | filed | 2026-07-06 |
| 19f36067288ef908 | LUPO-DIGITAL LTD | 50097 | 12452573515 | filed | 2026-07-06 |
| 19f3529481c6b8b0 | MVP GROW LTD | 41757 | 12452534312 | filed | 2026-07-06 |
| 19f229c6e7d7b1e7 | MVP GROW LTD | 61578 (receipt for inv 41732) | 12310782997 | receipt-attached | 2026-07-12 |
| 19fc677d7fbfe72a | M V P GROW LTD | 41770 | 12818050112 | filed | 2026-08-23 (item 2026-08-17, PDF attached 2026-08-23) |
| 19fd4ce344e66794 | M V P GROW LTD | 41774 | 12818069875 | filed | 2026-08-23 (item 2026-08-17, PDF attached 2026-08-23) |
| 1a02df7007cb1dde | M V P GROW LTD | 61610 (receipt for inv 41757) | 12452534312 | receipt-attached | 2026-09-06 |
| 1a06899430f5f9f5 | M V P GROW LTD | 41789 | 12984493611 | filed | 2026-09-06 |
| 1a07a84dafe47f6c | M V P GROW LTD | 41803 | 13034357643 | filed | 2026-09-13 |
| 1a07a878b90c7000 | M V P GROW LTD | 61613 (receipt for inv 41770) | 12818050112 | receipt-attached | 2026-09-27 |
| 1a0a90d28235ceaf | Windsor Group AG | 0LBDUZ4W-0002 | 13066738407 | skipped-duplicate (filed manually 2026-09-17) | 2026-09-27 |

## Summary DM template

Slack mrkdwn, no em dashes, footer mandatory. `{CURRENCY}` is the invoice's actual currency (`USD` when unstated).

```text
:receipt: *Invoice agent - weekly run* ({DATE})
Filed {N} invoice(s) to the Invoices and Payments board :moneybag:

{per invoice: • *{Vendor}* - {SUM} {CURRENCY} - {Month group} - <{item link}|open>}

{if any: :warning: *Needs manual review*
{per item: • *{Vendor}* - {what is missing} - <{item link}|open>}}

{if any: Skipped: {reasons}}

_Posted by the Marketing OS agent_
```
