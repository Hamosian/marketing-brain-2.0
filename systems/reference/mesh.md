<!-- last-reviewed: 2026-07-25 -->
# Mesh

> Corporate spend platform (cards, subscriptions, reimbursements, vendor payments) run by Finance. Marketing is a spender and a reader, not an owner. Reached through the `Mesh` MCP connector, read-only.

## Overview

Mesh is where company card spend, recurring subscriptions, and reimbursements
live. For Marketing it answers the questions a budget owner actually asks: what
are we spending, on which categories, who owns each line, and how does it move
month over month.

We are a **consumer**. Finance owns the platform, the category taxonomy, the
approval rules, card issuance, and the accounting integration. Marketing reads
its own slice of the data and reconciles against its own records. We do not
change categories, limits, approvals, or cards from here - those requests go to
Finance through their normal process.

## How Claude Works With This

| Action | How |
|--------|-----|
| Report Growth Marketing spend by month, vendor, and card | `/mesh-expenditure-report`, **run from Nir's account** - he holds the department's cards, so the connector covers the department |
| Report spend by Mesh category name, or by person | `/mesh-expenditure-report` with a **Finance export** - the connector exposes neither a category name nor a cardholder field |
| Find spend with a missing invoice or receipt | `/mesh-expenditure-report` - the `receiptStatus` field carries it. `REQUIRED_NO_ATTACHMENT` is the chase list; the skill drafts nudges for Nir and never sends them |
| Pull transactions | `getMyRecentTransactions` (every card the caller holds), `getCardTransactions` (one card) |
| Resolve people across the org | `getOrganizationContacts` - the one org-wide tool, and it returns contacts, not spend |
| Approve, cancel, re-categorize, change a limit | **We don't.** Route to Finance |
| Reconcile invoices against spend | Out of scope for the skill today. The Growth Marketing invoice record is the `Invoices and Payments - Growth Marketing` board (`18390740532`, see `references/monday_boards.md`) |

## Access model (verified 2026-07-25)

| Property | Value |
|----------|-------|
| Connector name | `Mesh`, tool prefix `mcp__Mesh__` |
| Directory / installed server UUID | `fbc4d1a3-0f69-4d02-bad7-a0438b2e73c8` |
| Auth | OAuth - needs an authorized user session |
| Session requirement | Must be **enabled for the session**; the OAuth step needs an interactive session and cannot run headless or on a schedule |
| Company / organization | `Riverside.FM Inc` `5965339899748109882` / `Riverside.FM` `4696213429300708828` |
| Role observed | `companyRole: EMPLOYEE`, `canManageOrganization: false`, `mcpEnabled: true` |
| Tools | 6, all reads: `whoAmI`, `getMyCompanies`, `getMyVirtualCards`, `getMyRecentTransactions`, `getCardTransactions`, `getOrganizationContacts` |
| Mutations | None available, and none permitted |

### Scope follows the cardholder

The transaction tools return **every card the caller holds**, not a personal
subset. Coverage is therefore a property of whose account runs the report:

- **Nir Taranto holds Growth Marketing's cards department-wide**, so a run from his
  account covers the department. This is the intended way to run it.
- Anyone else's run covers only their own cards, and must say so.

The `companyRole: EMPLOYEE` / `canManageOrganization: false` pair governs
organization *administration*, not which of your cards are readable. Do not read it
as a reporting ceiling (an earlier version of this doc did).

**Two limits are absolute regardless of account:** the payload carries a
`spendCategoryStatus` **flag instead of the category name**, and there is **no
date-range parameter**. There is also no cardholder field, so live ownership is
**card level**; person-level attribution needs a Finance export. Field-level
evidence and the full tool table live in the skill's `knowledge/mesh-access.md`.

## What the Team Owns

- Our own read-side interpretation: the Growth Marketing scope filter, the
  canonical row schema, and the report outputs.
- The spending decisions behind the transactions.

## What the Team Does NOT Own

- The platform, the category taxonomy, approval and issuance rules, the
  accounting sync, and anything Finance reconciles against.

## Gotchas

- **Coverage is the card list, so check it.** `getMyRecentTransactions` returns
  every card the caller holds, which is department-wide for Nir and a single
  subscription or two for an IC. Call `getMyVirtualCards` and look before claiming
  any scope.
- **Card names decode merchant descriptors.** `PAIEMENT SOFTLOGIC` is the Pageradar
  subscription, knowable only from the card it sits on. Prefer the card name on
  `SUBSCRIPTION` cards, keep the raw descriptor alongside.
- **A card's currency can differ from its transactions'.** A EUR-denominated card
  produces USD transaction amounts that drift with the rate. That drift is not a
  price change.
- **`spendCategoryStatus` is a flag, not a category.** It tells you a category
  exists, not which one. The honest statement is coverage ("N of M have a
  category set"), never an inferred category name.
- **No date-range parameter.** Paginate to exhaustion (`pageSize` max 100) and
  filter locally; check collected rows against `totalCount` before reporting.
- **Category is Finance's field, not ours.** If a category looks wrong, that is a
  Finance conversation - do not remap it silently in a report.
- **Not enabled by default, so nothing here can be fully automated.** A scheduled or
  headless run cannot complete the OAuth step. The month-end receipt chase therefore
  works as a *reminder* to a human on the 22nd, who runs the skill; a routine cannot
  pull Mesh data on its own. Do not wire a routine that assumes it can.
- **`receiptStatus` is the missing-invoice signal.** `REQUIRED_NO_ATTACHMENT` means
  Finance requires a receipt and none is attached. `OPTIONAL_NO_ATTACHMENT` is missing
  but not required, and is not chased.
- **Former employees' spend persists** in historical months. It is still
  Marketing spend; the skill keeps it and marks the owner `(former)`.
- **Mixed currency.** Mesh returns **no converted amount**, so there is nothing to
  fall back on: report per-currency subtotals, keep every ranking and delta inside
  one currency, and state that no conversion was applied. Never source or derive an
  FX rate (including from a EUR card's own USD amounts).
- **Pending vs settled.** Headline totals are settled; pending is a separate,
  labeled figure. A total that quietly mixes them will not tie to Finance.

## Related

- `.claude/skills/mesh-expenditure-report/` - the skill, plus its access and
  output specs in `knowledge/`.
- `references/monday_boards.md` - the Invoices and Payments board, Growth
  Marketing's own invoice record.
- `references/team.md` - the roster that defines the Growth Marketing scope
  filter.
