---
name: invoice-inbox-to-monday
description: Weekly automation that reads invoice emails from a Gmail label ("Invoices"), downloads and reads the invoice PDF for the real amount and date, and files each invoice as a fully-populated item (including the attached PDF) in the correct month group on the "Invoices and Payments - Growth Marketing" monday board (18390740532). Dedupes via a processed ledger, never touches the Emailed items group, and DMs the owner a Slack summary of what it filed. Runs per profile (default tracking.md = Hanan; tracking-nir.md = Nir; tracking-erika.md = Erika), each against its own connected Gmail, weekly as a cloud routine, or on demand. Trigger phrases - "file my invoices", "run the invoice agent", "invoices to monday", "process invoice emails", "invoice inbox".
---

# Invoice inbox to monday

The Marketing OS agent's weekly sweep of **invoice emails into the monday invoices board**. It reads everything under the Gmail label `Invoices` in `hanan.amos@riverside.fm`'s mailbox, downloads and reads each invoice PDF for the real facts, and creates one fully-populated item per invoice - with the PDF attached - in the month group matching the **invoice date on the document**, on the board **Invoices and Payments - Growth Marketing** (`18390740532`).

**This is a sanctioned automation skill.** Per `CLAUDE.md`, on **scheduled runs** it is authorized to create monday items, attach files, set owner/payment from the routing map, and send the summary DM **without per-item confirmation**, but only under the guardrails below. It never invents invoice data and never files the same invoice twice.

## Run profiles

The same skill logic runs for more than one person, each with its own **profile file** holding the source mailbox, processed ledger, summary recipient, and any per-profile policy knobs. All profiles file to the same board.

- **Default profile:** `tracking.md` (Hanan Amos). Used when the runner names no profile.
- **Named profiles:** the runner names the profile file, e.g. `tracking-nir.md` (Nir Taranto) or `tracking-erika.md` (Erika Varangouli). Read that file for config instead of `tracking.md`.

**Each profile runs against its own Gmail.** The source mailbox is whatever Gmail account is authenticated in the environment the run executes in - the skill does not switch mailboxes. So a profile only reads the intended person's invoices when it runs in that person's environment with their Gmail connected (e.g. the Erika profile runs in Erika's own Claude Code against `erika.varangouli@riverside.com`). The profile's `Gmail account` field records which mailbox that must be; if the connected account does not match, stop and surface it rather than filing another mailbox's invoices under this profile.

A profile may set three **policy knobs** (default profile behaves as if all are off/unset):

- **`summary_mode`** - `full` (default: DM every run's results; stay silent only on a fully-empty run) or `exceptions-only` (DM **only** when the run produced something the recipient must act on - a held item, needs-review, skip, or failure; otherwise send no DM even if invoices were filed).
- **`low_conviction`** - `file-blank-and-flag` (default: when a vendor is unmapped, file the item with routing columns left blank and flag it) or `ask` (do **not** guess or file blanks; **hold** the uncertain item and ask the recipient - inline on interactive runs, via the DM's "need your call" queue on scheduled runs - then file once answered). See guardrail 8.
- **`default_payed_by`** - unset (default): the **Payed by** column is set only from the Vendor routing map, per vendor, and stays blank when the vendor is unmapped. Set to a monday user (id + name): the skill fills **Payed by** with that person on **every** item this profile files, so all of a profile's invoices land under one owner. A vendor's explicit `Payed by` in the routing map still overrides the default when present. This knob defaults **only** the Payed by person - **Type** and **Payment Method** are never defaulted and still come only from the routing map.

## What qualifies

An email qualifies when **both** hold:

1. It carries the Gmail label named in the **active profile file** (display name `Invoices`; label ID cached there - resolve via `list_labels` and re-cache if missing or stale). Each profile caches its own label ID because the label lives in that profile's own mailbox.
2. Its Gmail **message ID is not in the active profile's Processed ledger** (each profile keeps a separate ledger).

The search window is `after:` the window start in the **active profile file** (first run: that profile's backfill start; later runs: last-run date minus 14 days as a grace overlap - the ledger, not the window, is the dedupe). Read all three - label cache, ledger, window - from the profile the run named (`tracking.md` only when the run named no profile), never from `tracking.md` when a named profile is active.

One email can contain more than one invoice (e.g. two billing periods); create one item per invoice, like the existing "Saasmart - For May" / "Saasmart - For June" pattern.

## Reading the invoice PDF (the source of truth)

The Gmail connector **cannot read attachment bytes**, but invoice-delivery services put a **document download link in the email HTML**, and that link is the real source of the amount, currency, and invoice date. Always try to read the PDF before falling back to email text.

1. From `get_thread` (FULL_CONTENT), find the document **download** link in the HTML. For **Green Invoice / morning.co** (the common sender `notify@morning.co`), that is the `https://www.greeninvoice.co.il/api/v1/documents/download?d=...` URL behind the "Download File" button. **Do not** use the `https://pages.greeninvoice.co.il/en/documents/view?...` link - it is a JS-rendered page and returns no readable content.
2. Download the PDF to the scratchpad with `curl -sL -A "Mozilla/5.0" -o <invoiceNo>.pdf "<downloadUrl>"`, then `file` it to confirm it is a real PDF (not an HTML error page).
3. **Read the PDF** (the Read tool renders PDFs) and extract: total payable, currency, invoice date, line items, vendor legal name, Tax ID, website, and the vendor's real email. Keep the downloaded file - it is uploaded to the Invoice column in step 5.
4. Only when there is **no readable download link** (e.g. a bare PDF attachment, which the connector cannot read) do you fall back to email text for the identifiable fields (vendor, invoice number) and mark the amount/date `needs-review`. No PDF is attached in that case - it stays a human upload until attachment-byte access exists.

## Extraction rules

Prefer the PDF (above); fall back to the email subject/body/sender.

| Fact | Source | If missing |
|------|--------|-----------|
| Vendor (item name) | PDF / sender / subject | Required - if truly unidentifiable, skip and flag in the summary |
| Company legal name | PDF / body | Leave blank |
| Invoice number | Subject or PDF (`INV-...`, `#...`, doc number) | Leave blank |
| Amount | **PDF total payable** (else body) | Blank + mark **needs manual review** only if no readable PDF |
| Currency | PDF/body | Assume USD; if non-USD, note it in Overview (Invoice Sum is a bare number) |
| Invoice date | **Document date on the PDF** (else email date) | Fall back to email received date + note the basis in Overview |
| Contact email | Vendor email on the PDF, else sender address | Leave blank if only a no-reply relay (e.g. `notify@morning.co`) |
| Tax ID | PDF | Leave blank |
| Website | PDF | Leave blank |

## Filing rules

- **Month group = invoice date's month.** Group IDs are cached in `tracking.md`. If the month group does not exist yet, create it (title format `July 2026`, positioned among the other month groups) and cache the new ID.
- **Item name:** vendor short name, optionally with context, matching board convention (`Capterra`, `Saasmart - For June`, `LUPO-DIGITAL - CRM scope`).
- **Columns to fill (agent-writable):** Company name (`text_mm4ecyyd`), Invoice number (`text_mm4ec06z`), Invoice Sum (`numeric_mky9safm`), Contact Email (`email_mm01ykcb`), Tax id (`text_mm4eafd8`), Website (`link_mm4ep17t`), Overview (`long_text_mm4ednzr`), Type (`color_mm0e2221`) and Payed by (`multiple_person_mkz6t3jw`) and Payment Method (`dropdown_mky9maht`) - the last three **from the active profile's Vendor routing map**, with one exception: **Payed by** is also set from the profile's `default_payed_by` knob when it is set (routing-map `Payed by` overrides it), so under a `default_payed_by` profile Payed by is never blank while Type/Payment Method stay map-only. See "Type / owner / payment" below. Full column reference in `references/monday_boards.md`.
- **Column value formats (monday API gotchas):** email = `{"email":"x@y.com","text":"x@y.com"}` (both keys required, `text` non-null); dropdown = `{"labels":["Bank Transfer"]}` (array, not `label`); link = `{"url":"https://...","text":"label"}`; people = `{"personsAndTeams":[{"id":<numericUserId>,"kind":"person"}]}`; number = bare string.
- **Overview always contains:** one-line description + key line items, invoice date + basis (`document` or `email received`), currency if non-USD, `proforma` flag when applicable, the Gmail thread link (`https://mail.google.com/mail/u/0/#all/<threadId>`), any needs-review flag, and `Filed by the Marketing OS agent`.
- **Attach the PDF** to a file column - see step 5. An **unpaid invoice / proforma** creates the item and its PDF goes to the **Invoice** column (`file_mky9xwjy`, the default). A **paid receipt** (subject `Invoice / Receipt` or `Receipt`, PDF has a `Payments Details` section) does **not** create an item - one invoice = one item - it attaches to the matching existing invoice item's **Receipt** column (`file_mm569fkh`). Full rule + matching logic in the "Invoice vs Receipt" section of `tracking.md`. This is no longer a manual step.
- **Columns never touched:** Invoice Uploaded status (`status`), Date Paid (`date4`), Payment Done (`boolean_mky9pwjm`), W8/W9, Agreement, Campaign Name. Those are the paying humans' to set.

### Type / owner / payment - routing map only
Set **Type**, **Payed by**, and **Payment Method** only from the Vendor routing map in the active profile file. When a vendor is not mapped, leave those columns **blank** - never infer an owner, payment method, or type. When you learn a confident new mapping (e.g. the user tells you "vendor X belongs to person Y, paid by Z"), append it to the routing map.

**Exception - `default_payed_by`:** when the active profile sets the `default_payed_by` knob, fill **Payed by** with that person on **every** item, even for unmapped vendors (a vendor's explicit routing-map `Payed by` still overrides the default). This is the only column a profile default touches - **Type** and **Payment Method** are never defaulted and still come only from the map, so an unmapped vendor under a `default_payed_by` profile files with Payed by set and Type/Payment Method blank (and is flagged per `low_conviction`).

## Guardrails (non-negotiable)

1. **File each invoice once.** Dedupe by Gmail message ID (ledger) AND by company + invoice number: before creating, search the board (`search`, ITEMS) for the invoice number and confirm the matching item belongs to the same company; skip only when both match (different vendors can reuse the same invoice number), and note the skip in the summary.
2. **Never invent data.** Amounts come from the PDF (via the download link) or the email body - never a guess, no inference, no currency conversion. If neither is readable, leave blank and flag needs-review.
3. **Create-only, with one exception.** Never move existing items, never edit their amount/routing/group, and never touch the `Emailed items` group (`group_mm1fdkmn`) - other people's intake flow lives there. The **single** allowed edit to an existing item is attaching a **paid receipt** PDF to its `Receipt` column (`file_mm569fkh`): a receipt settles an invoice that is already its own item, so it must land on that same item, not a new one (see "Invoice vs Receipt" in `tracking.md`).
4. **Monday failure means no ledger entry.** If `create_item` fails, do not record the message as processed; the next run retries. A failed **file upload** does not roll back the item (the item is the deliverable), but it must stay retryable: record the message with status `filed-no-pdf` and its item ID, and note "PDF upload pending" in the summary. The next run re-uploads to that existing item (it never re-creates it) and flips the status to `filed` on success. Slack failure does NOT roll anything back - surface the error instead.
5. **Confirmation rule.** Scheduled/headless runs are **fully autonomous**: read PDF, create, attach file, set routing columns, DM - all without confirmation. Interactive runs list the proposed items and confirm with the user before writing.
6. **When to DM.** Default (`summary_mode: full`): zero new invoices means no DM (log "no new invoices" and stop, no commit); otherwise DM the results. `summary_mode: exceptions-only`: DM **only** when the run produced a held item, a needs-review item, a skip, or a failure - if it filed only clean invoices, or nothing, send no DM (still commit the ledger).
7. **Recipient is config.** The summary DM goes only to the Slack ID in the **active profile file** (default `tracking.md` = Hanan `U0A3HCFE90S`; `tracking-nir.md` = Nir `U07LETHMPAP`).
8. **Low-conviction handling is per profile.** Default (`low_conviction: file-blank-and-flag`): an unmapped vendor files with routing columns blank and is flagged. `low_conviction: ask`: never guess and never file blank routing - **hold** the uncertain item (vendor unidentifiable, vendor not on the routing map, amount/currency not cleanly readable, or an ambiguous duplicate). On interactive runs, ask before writing it; on scheduled runs, file the confident invoices, record each held item as `held-needs-nir`, list it in the DM's "need your call" queue, and re-surface it every run until resolved. Guardrail 2 (never invent data) is absolute in both modes.

## Steps

### 1. Load state and config
Read the **active profile file** (the one the runner named, e.g. `tracking-nir.md`; default `.claude/skills/invoice-inbox-to-monday/tracking.md`): mailbox, label name + cached label ID, window start, board/group/column IDs, recipient Slack ID, Vendor routing map, Processed ledger, last-run date, and any `summary_mode` / `low_conviction` policy knobs. A named profile may point back to `tracking.md` for the shared board structure (group/column IDs) - read both in that case.

### 2. Fetch labeled emails
Resolve the label ID if uncached (`list_labels`, match display name `Invoices`, write back). Then `search_threads`.

> **Preferred query:** `label:Invoices after:<window>` - the **display name** (not the ID) works in this connector and returns exactly the labeled threads (verified 2026-07-12: `label:Invoices after:2026/06/22` returned the 4 labeled threads and nothing else). Use this first; it avoids paging ~200 unrelated threads.
> **Connector quirk / fallback:** `label:<labelId>` (the ID, e.g. `label:Label_5043...`) returns **nothing** in this connector. If the display-name query ever misbehaves, fall back to a broad search (`after:<window> has:attachment filename:pdf`, or `after:<window>`) and filter the returned threads to those whose message `labelIds` array contains the Invoices label ID.

For each returned thread not fully in the ledger, `get_thread` (FULL_CONTENT) for bodies, links, and attachment metadata.

If the Gmail connector is unavailable or unauthorized, stop with no state change and surface: "Gmail connector disconnected - reconnect it in claude.ai connector settings."

### 3. Read PDFs, extract, dedupe, classify doc type
For each qualifying message: download and read the PDF (see "Reading the invoice PDF"), apply the extraction rules, and drop anything already in the ledger or matching an existing board invoice number (guardrail 1). **Classify each document** as an invoice/proforma or a paid receipt (see "Invoice vs Receipt" in `tracking.md`): a receipt (subject `Invoice / Receipt`/`Receipt`, PDF has a `Payments Details` section) is routed to the receipt path in step 4, not treated as a new invoice. Build the proposed list, tagging each entry invoice vs receipt.

**Attachment-pending retries.** A ledger entry with status `filed-no-pdf` is *not* done: the item exists (item ID recorded) but its PDF never uploaded. For each such entry, re-download the PDF and retry the upload (step 5) to that recorded item ID - do **not** create a new item. Flip the status to `filed` on success; leave it `filed-no-pdf` if it fails again. All other ledger statuses (`filed`, `needs-review`, `skipped-*`) are terminal and skipped.

### 4. File to monday
**Invoice / proforma:** resolve the month group (create + cache if missing), `create_item` in that group with the column values (respect the value formats above), applying Type and Payment Method from the routing map and Payed by from the routing map or, when the active profile sets `default_payed_by`, that default (routing-map Payed by overrides it). Capture the returned item ID.

**Paid receipt:** do **not** create an item. Find the existing invoice item it settles - the receipt PDF names it (`Invoice / Receipt for Proforma Invoice MMMMM`); search the board (ITEMS) for `MMMMM`, confirm the same vendor, and use that item's ID (else match by vendor + amount + month). If no matching invoice item exists, fall back to creating one in the receipt-date month group and flag it in the summary. Record the receipt in the ledger against the existing item ID with status `receipt-attached`.

Interactive runs confirm the full list (creations and receipt-attachments) first.

### 5. Attach the PDF to the right item + column
Target depends on document type (see "Invoice vs Receipt" in `tracking.md`): an invoice/proforma uploads to the **newly created item's** Invoice column (`file_mky9xwjy`); a paid receipt uploads to the **existing invoice item's** Receipt column (`file_mm569fkh`). Upload the downloaded PDF to that item + column:
1. `get_asset_upload_url` with `fileName`, `contentType: application/pdf`, `fileSize` (bytes).
2. PUT the file, **check the HTTP status first**, then capture the **bare** ETag (strip the `ETag:` header name and quotes - `finalize_asset_upload` wants just the hex):
   ```bash
   HTTP=$(curl -sS -o /dev/null -w '%{http_code}' -D headers.txt -X PUT "<upload_url>" \
     -H "Content-Type: application/pdf" --data-binary @<file>)
   [ "$HTTP" = 200 ] || { echo "PUT failed ($HTTP) - re-fetch a fresh upload_url and retry"; }
   ETAG=$(grep -i '^etag:' headers.txt | sed -E 's/.*"([^"]*)".*/\1/')
   echo "$ETAG"   # e.g. 68214650c354ab625f49c3cbac80eced  (no quotes, no "ETag:" prefix)
   ```
   (Single-quote the URL - it contains `&` and `%`; a stray space corrupts the signature.)
3. Only if `$HTTP` is `200` **and** `$ETAG` is non-empty, call `finalize_asset_upload` with `uploadId`, `etag: $ETAG`, `boardId`, `itemId`, and the `columnId` chosen above (`file_mky9xwjy` for an invoice, `file_mm569fkh` for a receipt). Otherwise do not finalize - record the invoice `filed-no-pdf` (guardrail 4) so the next run retries.

### 6. Send the summary
DM the recipient via Slack: count filed, per-invoice line (vendor, sum + currency, month group, item link `https://riversidefm.monday.com/boards/18390740532/pulses/<itemId>`), a separate "needs manual review" section, and any skips/failures (including PDF-upload failures). Slack mrkdwn, no em dashes, mandatory `_Posted by the Marketing OS agent_` footer. Zero filed and zero problems: no message (guardrail 6).

### 7. Persist state
Append each filed invoice (message ID, vendor, invoice number, item ID, date) to the Processed ledger, update last-run date and window start, append any new vendor classifications/routing to the map, then commit:
```bash
git add .claude/skills/invoice-inbox-to-monday/tracking.md
git commit -m "invoice-inbox-to-monday: filed <N> invoices"
git push
```
Only commit when something changed. This routine commits its ledger straight to `main` and pushes - the tracking file is run state, not code, so it skips the PR gate by design.

### 8. Report
Summarize: invoices filed per month, needs-review count, skips, failures. Interactive runs print it; scheduled runs treat it as the routine's output.

## Notes
- **Weekly cadence.** The routine runs Sunday mornings (Asia/Jerusalem). A missed week self-heals: the 14-day grace window plus the ledger picks up the backlog.
- **The board is shared.** Dor, Savion, Raz, and others file invoices on this board manually and via the Emailed items intake. This skill only adds the **email-sourced invoices of whichever profiles run it** (Hanan, Nir, Erika), each from that person's own mailbox; it is not the board's owner.
- **PDF read + upload is automatic** for invoices delivered with a document download link (Green Invoice / morning.co and similar). A true PDF attachment with no link still can't be read via the connector - those file as needs-review with no attachment until attachment-byte access exists.
- **Non-USD invoices** get the raw number in Invoice Sum and the currency called out in Overview and the DM. Finance decides how to normalize.
