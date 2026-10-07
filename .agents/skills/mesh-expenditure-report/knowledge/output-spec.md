# Output spec: doc, dashboard, Sheet, chase list

Four deliverables per run: a **running Google Doc** (the record Nir reads), the
**dashboard** (for reading now), the **Sheet** (for working the numbers), and, when
anything is outstanding, a **receipt chase list drafted for Nir to send**. All four
come from the same normalized rows - if a figure differs between them, the run is
wrong.

**Every figure carries its source and as-of date** (`references/evidence-standards.md`):
"Mesh connector, pulled 2026-07-25", not a bare total. A number without a date
silently becomes a claim about today.

**Scope and source change what ships.** Coverage depends on whose cards the run
read (see `knowledge/mesh-access.md` §2), so **every deliverable opens with the
account read and the number of cards it covers**. In **LIVE** the category section
is **suppressed with its reason shown** and the owner section is **card level**,
never rendered empty or filled with inferred values. An **EXPORT** adds category
names and person-level ownership.

## A. Interactive dashboard (Artifact)

Load these first: `artifact-design` (design investment calibration),
`riverside-brand-guidelines` (the single source of truth for color and type),
`riverside-ux-patterns` (layout, hierarchy, interaction states, accessibility),
and `dataviz` (chart form and palette rules - read it before writing any chart
code).

**Title:** `Mesh expenditures - Growth Marketing - [Month YYYY window]`
**Favicon:** keep it stable across redeploys.

### Sections, in order

1. **Header** - title, resolved window, and an explicit scope line naming the
   account and its card count: "Growth Marketing, N cards on Nir Taranto's Mesh
   account", or "[Name]'s own Mesh spend, N cards. Not a department total."
   Completed transactions unless labeled pending.
2. **Snapshot row** - stat tiles: total completed, pending (labeled), vendor
   count, month-to-date flag. An export adds category and owner counts; LIVE
   instead shows category coverage ("N of M have a category set in Mesh").
3. **By month** - the per-month series, current month visibly partial. This is the
   primary view.
4. **Category x month** - **export only.** A stacked bar per month (categories
   as series) or a category-by-month matrix with per-cell values; pick whichever
   stays readable at the real category count, and follow `dataviz` on palette and
   legend. Total column plus MoM delta on complete months only. Without an export, render
   a single explanatory line in its place: "Category breakdown needs a Finance
   export - the Mesh connector returns a category flag, not category names."
5. **By card and owner** - cards ranked by spend, each against its limit where the
   record carries one. Roll up to person or function only where the card records
   support it; otherwise label the section card level and note that person level
   needs the export's cardholder column. With an export, owners ranked by total
   with `Unattributed` shown as its own row, never hidden.
6. **Top vendors** - ranked vendors with total and the months they appear in.
   Recurring subscriptions and one-offs are visually distinguishable. Show the
   grouped vendor name with the raw descriptor available on hover or in the table.
7. **Movers** - largest MoM increases and decreases across complete months, each
   naming the vendor (plus category and cardholder with an export) behind the move.

8. **Transactions** - the full drill-down table (date, vendor, amount, currency,
   type, status, card, description; plus category and cardholder with an export),
   filterable by month and vendor, in its own `overflow-x: auto` container so the
   page never scrolls sideways.
9. **Footer / data notes** - mode, source (account read, or export with its date),
   window, rows pulled vs `totalCount`, rows in scope, rows filtered out,
   category coverage or uncategorized count, currency basis, and any source gap.
   Never omit this.

**Mixed-currency windows partition every ranking and delta by currency.** No
conversion is applied anywhere (`knowledge/mesh-access.md` §5), so a EUR total and
a USD total cannot be ranked against each other or subtracted: totals, vendor
rankings, month series, and MoM deltas are all computed **within** a currency and
labelled with it. A single-currency window renders exactly as described above,
with the currency named once in the header.

### Rules

- Self-contained: inline all CSS/JS, no external requests (a strict CSP blocks
  them). Theme-aware for light and dark. Responsive.
- Every displayed figure traces to rows in the transactions table. No computed
  placeholder ever ships.
- Empty section text, never a dropped section: "No pending transactions in this
  window", "No material movement".
- **Updating an existing dashboard:** redeploy the same file path to keep the URL.
  For a dashboard published in an earlier session, find it with the Artifact
  tool's `action: "list"` and pass its `url` - otherwise a new URL is minted and
  Nir's bookmark goes stale.
- Write the HTML to the session scratchpad directory, not into the repo.

## B. Google Sheet

Build a multi-tab workbook with the `xlsx` skill, then upload it to Drive with
conversion so it lands as a native Google Sheet with every tab intact:

```
mcp__Google_Drive__create_file
  title: "Mesh expenditures - Growth Marketing - [window]"
  contentMimeType: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
  base64Content: <the .xlsx>
  parentId: <the growth-reporting shared folder, see below>
```

Leave `disableConversionToGoogleType` unset so it converts. If conversion fails,
send the `.xlsx` to Nir directly with `SendUserFile` and say the Sheet conversion
failed - do not silently downgrade to a single-tab CSV.

**Location:** file it under the growth-reporting shared Drive folder from
`references/growth-reporting.md` (top-level `1MByB7bkM6bsN59Ujx5cW5pkQY_yXmvly`).
Do not hardcode a month subfolder - those rotate. If no suitable folder resolves,
create it in My Drive and say where it went.

### Tabs

| Tab | Contents | Mode |
|-----|----------|------|
| `Transactions` | One row per transaction, the full canonical schema from `knowledge/mesh-access.md`. This is the tab everything else is derived from. | Both |
| `By month` | Months down, totals plus MoM delta on complete months. | Both |
| `By vendor` | Vendors down, months across, totals, sorted by total descending. | Both |
| `By category` | Categories down, months across, totals and MoM delta columns. `Uncategorized` included as a row. | Export only |
| `By owner` | Owners down, months across, totals. `Unattributed` included as a row. | Export only |
| `Notes` | Mode, source (account or export + date), window, rows pulled / in scope / filtered out, category coverage, currency basis, and every caveat from the dashboard footer. | Both |

Omit the export-only tabs entirely when running LIVE rather than shipping empty
ones, and say so in `Notes`.

### Rules

- Amounts as numbers, not text - Nir pivots off this. One currency per column; if
  the window is mixed-currency, add a `currency` column and per-currency subtotal
  rows rather than blending. Pivot tabs get a currency dimension too: no row or
  total ever mixes currencies, matching the dashboard.
- Dates as real dates, `month` as `YYYY-MM` text so it sorts correctly.
- No formulas that reference the dashboard or external files; the workbook must
  stand alone.
- Pivot tabs are computed values, not live formulas over `Transactions` - the
  numbers must match the dashboard exactly at the moment of the run.

---

## C. The running Google Doc

One living document, not a new file per month. It is the artifact Nir actually reads,
so it is the one that must survive.

**Title:** `Growth Marketing spend - Mesh`
**Location:** the growth-reporting shared Drive folder from
`references/growth-reporting.md` (top-level `1MByB7bkM6bsN59Ujx5cW5pkQY_yXmvly`).

**Find it before creating it.** Search Drive by title first. Only create the doc if no
match exists, and say which you did. Two docs with the same name is the failure mode
here: the numbers diverge and nobody knows which is current.

**Newest month first.** The newest month's section sits at the top, directly under the
doc header, so opening the doc shows the latest month without scrolling. Earlier months
are never overwritten or reordered, because the point of the doc is the trend.

### How the update actually happens: Drive here is create-only

**The Drive toolset in this repo exposes create, read, and copy. There is no
update-content and no delete** (verified 2026-07-25, the hard way: three copies of this
doc exist because a formatting fix could not be applied in place). So the skill cannot
prepend a section to an existing doc, and this spec must not pretend otherwise.

The contract is therefore **paste-ready output plus a human paste**:

1. Find the doc by title and read it with `read_file_content`, so you know which months
   it already contains and what the header says.
2. Produce the new month's section as a self-contained block in the structure below,
   ready to paste directly under the doc header.
3. Hand it over with one explicit instruction: paste at the top, above the previous
   month. Say if the header's scope or last-updated line needs changing too.

The doc's URL never changes under this model, which is the property that matters most:
Nir bookmarks it and links in Slack keep working.

**Never create a second doc with the same title to work around the missing update.**
That forks the record, and a forked record is worse than a manual paste.

**If hands-off updating matters more than living in Drive,** a monday doc is the
update-capable alternative: `mcp__monday_com__update_doc` inserts markdown blocks
after a named block, so the prepend can be automated. That is a deliberate platform
change, so propose it rather than silently switching.

### Rerunning a month the doc already has

Runs repeat by design: the reminder fires on the 22nd, and someone may rerun at month
close or after a correction. **Replace that month's section in place; never append a
second one.** If the doc already carries a `## [Month YYYY]` heading for the month you
produced, the handover instruction is "replace the existing section", and the new
section carries a fresh source-and-as-of line so the swap is visible. Every other month
stays untouched.

A month appearing twice is a data-integrity failure rather than a cosmetic one: whoever
reads the trend will double-count it. If you cannot tell whether a section is the same
month, say so and stop rather than pasting a possible duplicate.

### Header (written once, updated in place)

- What the doc is, that it comes from Mesh, and that Mesh is Finance's system of record.
- The scope line: whose account is read and how many cards that covers.
- Last updated date, and the two standing caveats: no category names from the
  connector, and ownership at card level unless an export was used.

### Per-month section, in this order

1. `## [Month YYYY]` heading, with `(month to date)` when partial.
2. **Source line:** "Mesh connector, account [email], N cards, pulled [date]." Every
   figure below inherits it.
3. **Totals** by currency, completed, with pending shown separately if non-zero.
4. **By vendor** - a table: vendor, total, transaction count, raw descriptor.
5. **By card** - a table: card, total, monthly limit, percent used, currency.
6. **Receipt compliance** - count required-and-missing, listed per card or person.
   Write "All receipts filed" when clean, never omit the line.
7. **Month over month** - the delta against the previous complete month, within a
   currency, and the reason where it is known (a new card, a one-off, rate drift).
8. **Notes** - rows pulled vs `totalCount`, anything unresolved.

Apply `riverside-brand-guidelines` for the doc: purple H2s, near-black body, the
purple accent bar under section titles, and the logo in the header.

### Writing and format rules for the doc (learned the hard way, 2026-07-25)

- **Never use the em dash character.** This is a strict Riverside brand writing rule
  (`riverside-brand-guidelines`), and it applies to the doc, the dashboard, the chase
  drafts, and Slack. Use a comma, a colon, a period, parentheses, or rewrite the
  sentence. Do not blind-substitute one punctuation mark for another: rewrite so the
  sentence reads naturally without it.
- **Do not put `<b>` or `<i>` inside a `<td>`** when creating the doc from HTML.
  Google's HTML import turns inline bold inside table cells into **literal asterisk
  characters**, so a header renders as `**Card**`. Use `<th>` for header rows, and
  carry emphasis in a `<td style="color:...">` instead of a tag.
- **Read the doc back after writing it** (`read_file_content`) and check for stray
  asterisks and em dashes before sending anyone a link. The create call reports
  success regardless.
- **There is no update-content or delete tool for Drive docs** in this toolset, only
  create. A formatting mistake therefore costs a duplicate file that a human has to
  trash, which is exactly the fork this spec warns about. Get it right in one pass:
  compose, read back, and only then share the link.

---

## D. The receipt chase list (drafted, never sent)

`REQUIRED_NO_ATTACHMENT` only (`knowledge/mesh-access.md` §8). This skill **drafts**
the nudges and hands them to Nir. It does **not** message the people - not with
approval, not on a schedule. The chase comes from Nir.

Open with the provenance line, which applies to the summary and every block below:

```text
Source: Mesh connector, account [email], N cards, pulled [date].
```

Then one copy-pasteable block per recipient:

```text
[Name or card, if unresolved]
Missing receipts in Mesh, [Month YYYY]:
  - [date]  [vendor]  [amount] [currency]  card [name] ...[last4]
  - [date]  [vendor]  [amount] [currency]  card [name] ...[last4]
Total outstanding: [amount] [currency] across [n] transactions.
```

Then, above the blocks, a one-line summary for Nir: how many people, how many
transactions, total outstanding, and how many cards could not be resolved to a person.
The provenance line sits above that summary, so every date, amount, count, and total in
the chase list inherits a source and an as-of date like every other figure this skill
produces (`references/evidence-standards.md`).

**Rules**

- **Unresolved cards are listed, not guessed.** A card that does not map to a person
  appears under its card name with "cardholder unresolved" beside it. Never infer a
  recipient from a card name that names a tool.
- **Nothing is sent by this skill.** No Slack, no email, no calendar invite to the
  people involved. Drafts only.
- **Say when the list is empty.** "No required receipts outstanding" is a result worth
  reporting, and it is the state the chase is trying to reach.
- **Keep it factual.** No chasing language, no urgency framing, no implied judgement.
  Nir decides the tone when he sends it.
