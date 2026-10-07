---
name: mesh-expenditure-report
description: Report Growth Marketing expenditures from Mesh (Finance's corporate spend platform) by month, vendor, card, and owner, and draft a missing-receipt chase list for Nir. Reads the Mesh connector live (scope follows the runner's own cards) and is read-only; outputs a running Google Doc, a Riverside-branded dashboard, and a multi-tab Google Sheet. Triggered by "Mesh expenditures", "Mesh spend", "expenditure report", "spend by category", "what are we spending per month", "spend by owner", "who hasn't uploaded invoices", "missing receipts", "chase invoices", "extract our expenditures", or "/mesh-expenditure-report". Distinct from /invoice-board-spend-pulse (reads a monday board, not Mesh).
user-invocable: true
---

# Mesh expenditure report

Answer "what are we spending, on what, who owes a receipt, and how does it move
month over month" from Mesh. Four outputs: a **running Google Doc** that accumulates
the numbers month by month (the record Nir reads), a Riverside-branded **interactive
dashboard**, a multi-tab **Google Sheet**, and a **receipt chase list drafted for Nir
to send**.

**Nir sees the numbers before anything else happens.** No nudge reaches a person from
this skill, ever - it hands Nir drafts and he decides. Every figure carries its source
and as-of date (`references/evidence-standards.md`).

**Read-only against Mesh:** this skill never creates, edits, approves, or cancels
anything in Mesh. Outside Mesh it publishes the dashboard artifact and creates the
Google Sheet, both gated on confirmation (step 8). Nothing is published or filed
without a yes.

**The running doc is updated by a human paste, not by this skill.** The Drive toolset
here can create a document but cannot update or delete one, so the skill creates the doc
on the first run and thereafter produces the new month as a paste-ready section, with an
instruction saying where it goes. That keeps the doc's URL stable and keeps the record in
one file. Full contract, including what to do when the month is already in the doc, in
`knowledge/output-spec.md` §C.

**Scope follows the cardholder.** The connector returns every card the runner
holds, not some personal subset of them. So coverage is a property of **whose
account runs the skill**:

- **Nir Taranto holds Growth Marketing's cards department-wide**, so a run from
  his account covers the department. This is the intended way to run it.
- A run from anyone else's account covers only their own cards, and must say so.

Always state whose account was read and what that covers. Never present one
person's cards as a department total, and never assume department coverage
without checking the card list.

| Mode | Source | Adds |
|------|--------|------|
| **LIVE** (default) | Mesh connector | Spend by month, vendor, card, and type, for every card the runner holds. Card-level ownership. |
| **EXPORT** | Finance-provided Mesh export | Mesh's **category names** and an explicit **cardholder** column, which the connector does not expose |

**Two limits are absolute, whoever runs it (verified 2026-07-25):** transactions
carry a `spendCategoryStatus` **flag**, not the category name, and there is **no
date-range parameter** (paginate and filter locally). Person-level owner
attribution depends on what the card records carry, which is why EXPORT still
matters. Field-level evidence in `knowledge/mesh-access.md`.

## Inputs and context to load

- Start from `CLAUDE.md`. Load `systems/reference/mesh.md` for the ownership
  boundary and access model.
- `knowledge/mesh-access.md` - **load every run before the first Mesh call.**
  Verified tool list and parameters, the response fields that actually exist, the
  canonical row schema, normalization rules, and the export column requirements.
- `knowledge/output-spec.md` - **load before step 7**, not at delivery: step 7 builds
  the chase list from its §D format. Carries the running doc's structure and update
  contract, dashboard sections, Sheet tabs, and the chase-list format, including which
  sections are suppressed without an export.
- `references/evidence-standards.md` - the source-plus-as-of-date rule every figure in
  the doc has to carry.
- `references/team.md` - the roster: the EXPORT scope filter, and resolving a card to
  a person for the chase list.
- `references/growth-reporting.md` - where the running doc is filed in Drive.

## Steps

1. **Establish scope first.** Call `whoAmI` and `getMyCompanies`, then
   `getMyVirtualCards` and **look at the card list before reporting anything**.
   The number and naming of cards is what tells you whether this run covers the
   department or one person. Say which in the output. If the user asked for
   department-wide spend and the card list is clearly one person's, say so rather
   than quietly reporting a narrower number.
2. **Resolve the window.** Default: the last 6 complete calendar months plus the
   current month to date. Honor a window the user names. State it in the output
   and label the current month **partial**.
3. **Pull the data.**
   - *LIVE:* `getMyRecentTransactions` paginated to exhaustion (`pageSize` max
     100 - compare rows collected against `totalCount` before reporting). It
     covers every card the runner holds. There is **no date-range parameter**:
     pull everything available, then filter to the window locally. On a
     department-wide account this is many pages, so do not stop at the first.
     Use `getCardTransactions` per card when you need a card's history in
     isolation or to reconcile a gap, and `getMyVirtualCards` with `cardIds` to
     resolve closed cards referenced by older transactions.
   - *EXPORT:* read the export and map its columns onto the canonical schema.
     Use `getOrganizationContacts` to resolve owner names and emails when the
     export carries partial identities.
4. **Attribute owners.** LIVE gives ownership at **card** level, not person
   level: attribute each transaction to its card, and roll cards up to a person
   or function only where the card records support it (name, or a mapping in
   `knowledge/mesh-access.md`). Where they do not, report by card and say person
   level needs the export. Apply the Growth Marketing scope filter only in EXPORT
   mode, where a cardholder column exists.
5. **Normalize** onto the canonical row schema, applying the currency, refund,
   pending, and category rules in `knowledge/mesh-access.md` exactly.
6. **Aggregate.** Always: **month**, **vendor x month**, **card**, **type**. With
   an export, also: **category x month** and **owner x month**. MoM deltas on complete
   months only.
7. **Build the receipt chase list.** Filter completed rows in the window to
   `receiptStatus == REQUIRED_NO_ATTACHMENT` (that value only - see
   `knowledge/mesh-access.md` §8). Group by card, then resolve to a person **only**
   where the card records support it; an unresolved card is listed under its card
   name with "cardholder unresolved", never assigned to a guess. Draft one block per
   recipient per `knowledge/output-spec.md` §D. Write "No required receipts
   outstanding" when clean. This skill never sends these.
8. **Deliver the outputs** per `knowledge/output-spec.md`, **after confirming
   them**. Build the dashboard (load `artifact-design`,
   `riverside-brand-guidelines`, `riverside-ux-patterns`, and `dataviz` first) and
   the workbook, state what will be published and where the Sheet will be filed,
   and get a yes before the publish and the upload. Render and look at the dashboard
   before publishing: theme, horizontal overflow, and console errors are only visible in
   the render, and read any doc back after writing it. **Find the running doc before
   creating one** (search Drive by title): create it only if it does not exist, and
   otherwise hand over the new month as a paste-ready section per
   `knowledge/output-spec.md` §C, replacing that month's section if the doc already has
   one. Then return the chat summary with the links and the chase list.

## Constraints

- **Read-only against Mesh.** Mesh is Finance's system of record. Only the read
  tools in `knowledge/mesh-access.md` are permitted. Approvals, limits, card
  changes, and re-categorization go to Finance.
- **The skill never chases anyone.** It drafts the receipt nudges and hands them to
  Nir. No Slack, no email, no calendar invite to the people named, with or without
  approval. A compliance nudge carries weight only when it comes from the person who
  owns the budget, and a nudge sent to the wrong person costs more than the receipt
  is worth.
- **Chase `REQUIRED_NO_ATTACHMENT` only.** Mesh's own requirement flag decides.
  Nudging about receipts Finance does not require trains people to ignore the nudge.
- **Confirm the external writes.** Publishing the artifact and creating the
  Google Sheet both leave this session, and spend data is sensitive: show what will be
  published, where the Sheet will be filed, and what will go into the doc, then wait for
  a yes. Never
  publish over an existing dashboard, and never file into a **shared** Drive folder,
  without saying so first. This skill is interactive and has no unattended
  exception - if it is ever scheduled, that gate has to be revisited explicitly.
- **Never claim a cut the source cannot support.** LIVE has no category names, and
  its ownership is card level, not person level - suppress or relabel those
  sections and say why. Never infer a category from the merchant name, and never
  present an inferred value as Mesh's.
- **Every figure carries a source and an as-of date.** "Mesh connector, account
  [email], N cards, pulled [date]", not a bare total
  (`references/evidence-standards.md`). A number without a date becomes a silent claim
  about today, and this doc is read months later.
- **Never overstate coverage.** Department-wide coverage is a claim about the card
  list, so check it. A run whose cards are one person's is one person's spend,
  said plainly, whoever asked for what.
- **Ground every number in a pulled row.** No estimates, no extrapolation, no
  filling a gap with a plausible figure. A missing month shows "no data".
- **Verify the pull is complete.** `getMyRecentTransactions` returns
  `totalCount`; if collected rows are fewer, keep paginating or report the
  shortfall. A truncated pull understates spend.
- **Never invent an FX rate.** Report in the transaction currency. Mesh supplies no
  converted amount, so a mixed-currency window gets per-currency subtotals and an
  explicit "no conversion applied" note. Because nothing is converted, **every
  total, ranking, and MoM delta is computed within a single currency** - a EUR
  vendor cannot be ranked against a USD one, or subtracted from it.
- **Refunds and credits stay in as negatives** against the vendor, category, and
  month they belong to. A month can legitimately go negative.
- **Pending separated, not merged.** Headline totals use completed/settled rows;
  pending is its own labeled figure. Declined and failed rows are excluded with a
  count.
- **Uncategorized is a bucket** with a count, never distributed or hidden.
- **Whose cards, stated.** Every output names the account read and how many cards
  it covers. That one line is what makes the totals interpretable.

## Output schema

Publish the artifact and the Sheet, then return this chat summary:

**Mesh expenditures - [Growth Marketing | name] - [window]**
1. **Scope and source** - the account read, how many cards it covers, and whether
   this is LIVE or LIVE plus an export (with the export's date). Always first.
2. **Total** - completed total for the window, pending shown separately, currency
   basis named.
3. **By month** - the per-month series, current month flagged partial.
4. **By vendor** - top vendors with totals and the months they appear in.
5. **By card** - cards ranked by spend, each against its limit where the record
   carries one.
6. **By owner** - person or function rollup where the card records support it.
   Otherwise: "Card level only - person level attribution needs the Finance
   export's cardholder column."
7. **By category** - export only. Without one: "Not available - the connector
   returns a category flag, not category names." Report the flag coverage instead.
8. **Movers** - largest MoM increases and decreases across complete months; "No
   material movement" when nothing moved.
9. **Data notes** - window, rows pulled vs `totalCount`, cards covered, rows
   filtered out, currency basis, and any gap. Never drop this section.
10. **Receipt chase** - how many people, how many transactions, total outstanding,
    and how many cards are unresolved. "No required receipts outstanding" when clean.
    The drafted per-person blocks follow, for Nir to send.
11. **Links** - the running doc, the dashboard, and the Google Sheet.

## Cadence

Run on demand, and once a month for the month-end close. **The run itself is manual:**
the Mesh connector needs interactive OAuth and cannot authenticate in a scheduled or
headless session (`systems/reference/mesh.md`), so a routine cannot pull the data
itself. What is scheduled is a **reminder on the 22nd of each month** - roughly a week
before month end - to run this skill so the chase list reaches people while they can
still act on it. Exact days-to-month-end vary by month; the reminder is deliberately
approximate rather than a per-month calculation.

The reminder is delivered as a **push notification**, not a Slack DM: routines created
from a session carry no MCP connectors, so a fired session has no Slack tool and cannot
message anyone (verified 2026-07-25, `trig_01J6JAZ3bixTjo34C1LiCjeY`). Its prompt
therefore does no tool work at all - it emits the reminder text and the completion push
delivers it. If a Slack DM is wanted instead, the routine has to be created from the
claude.ai routines UI, where connectors can be attached.

## Done when

The new month is in the running doc, or handed over as a paste-ready section with its
placement stated; the dashboard is published; the Sheet has its transaction tab and
applicable pivot tabs; the chase list is drafted (or reported empty); and the summary
above is returned with the links, the scope stated, and an honest data-notes section. If the run could not reach the scope the user asked for,
the run is done when that gap is reported plainly - not by passing a narrower
number off as the department's.
