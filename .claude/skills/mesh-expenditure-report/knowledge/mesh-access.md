# Mesh access, schema, and normalization

Everything `/mesh-expenditure-report` needs to get trustworthy rows out of Mesh.
Load before the first Mesh call.

**Verified live on 2026-07-25** against the `Mesh` connector with one employee account.
Tool names, parameters, and response fields below are observed, not assumed.

## 1. The connector

| Property | Value |
|----------|-------|
| Connector name | `Mesh` |
| Tool prefix | `mcp__Mesh__` |
| Directory / installed server UUID | `fbc4d1a3-0f69-4d02-bad7-a0438b2e73c8` |
| Auth | OAuth. Must be **enabled for the session**; the OAuth step needs an interactive session and cannot be completed headless |
| Riverside company | `Riverside.FM Inc` - `companyId` `5965339899748109882` |
| Riverside organization | `Riverside.FM` - `organizationId` `4696213429300708828` |
| Observed role | `companyRole: EMPLOYEE`, `canManageOrganization: false`, `mcpEnabled: true` |

## 2. What scope actually means here

**The transaction tools are scoped to the cards the caller holds, not to a
personal subset of them.** This is the single most important thing to get right,
and it was initially misread as an org-wide ceiling. It is not one:

- `getMyRecentTransactions` returns transactions across **every card the runner
  holds**. Verified on an employee account holding more than one card: the pull covered all of them.
- **Nir Taranto holds Growth Marketing's cards department-wide**, so a run from
  his account returns department-wide spend from the same three calls. This is the
  intended way to run the skill.
- A run from an individual contributor's account covers only their cards.

So coverage is a property of **whose account runs it**, and it is checkable:
call `getMyVirtualCards` and look at the list before reporting anything. The
account role (`companyRole: EMPLOYEE`, `canManageOrganization: false`) governs
organization *administration*, not which of the runner's cards are readable, so
do not read it as a reporting ceiling.

**Two limits are absolute, whoever runs it:**

1. **No category names.** Transactions carry `spendCategoryStatus` - an enum flag
   (observed: `HAS_SPEND_CATEGORY`) saying whether a category is set. The category
   *value* is not in the payload. Report flag coverage, never an inferred name.
2. **No date-range filter.** Only `pageIndex` / `pageSize` (max 100). Pull to
   exhaustion and filter locally. On a department-wide account that is many pages:
   always reconcile collected rows against `totalCount`.

Also absent from the transaction payload: department/team field, cost center,
approver, and any converted-currency amount. A **cardholder** field is absent too,
which is why LIVE ownership is card level and person-level rollups need either
card metadata that supports it or the Finance export (section 6).

## 3. Verified tools

| Tool | Params | Returns / notes |
|------|--------|-----------------|
| `whoAmI` | none | `email`, `fullName`, `contactId`, per-company date patterns, and the company/organization list. Start here for identity |
| `getMyCompanies` | none | `companyId`, `companyName`, `companyRole`, `organizationId`, `mcpEnabled`, `canManageOrganization` |
| `getMyRecentTransactions` | `companyId` (req), `pageIndex`, `pageSize` (max 100) | Transactions across **every card the caller holds**, plus `totalCount`, `pageIndex`, `pageSize`. **No date filter** |
| `getCardTransactions` | `companyId` + `cardId` (both req), `pageIndex`, `pageSize` | Same row shape, one card. Use to isolate a card's history or reconcile a gap |
| `getMyVirtualCards` | `companyId` (req), `cardIds`, `statuses`, `pageSize` | The caller's cards, **and the scope check**: the list tells you whether this run is department-wide or one person's. Carries `spendingLimit`, `spendingLimitPeriod`, `amountSpent`, `amountRemaining`, `type`, `currency`, `createdDate` - budget vs actual comes from here. Defaults to `ACTIVE` only; pass `cardIds` to resolve a closed card referenced by an older transaction. Statuses: `ACTIVE`, `INACTIVE`, `CANCELED`, `EXPIRED`, `SUSPENDED` |
| `getOrganizationContacts` | `companyId` + `organizationId` (both req), `search` | **Org-wide people** (not spend). Use it to resolve owner names/emails in EXPORT |

All six are reads. No write tool is permitted by this skill.

## 4. Verified transaction fields

Observed payload from `getMyRecentTransactions`:

| Field | Example | Notes |
|-------|---------|-------|
| `id` | `<19-digit id>` | Stable transaction ID - use for dedupe |
| `selfIssuedChargeId` | `<19-digit id>` | Present on self-issued charges |
| `date` | `<epoch ms>` | Epoch **milliseconds, as a string** |
| `dateFormatted` | `2026-07-22T13:14:43.000Z` | ISO 8601. Prefer this; derive `month` from it |
| `amount` | `70.00` | Number. Sign convention for refunds unconfirmed - see section 5 |
| `currency` | `USD` | ISO code |
| `merchantName` | `<raw payment descriptor>` | The vendor. Raw, unnormalized - see section 5 |
| `type` | `charge` | Only `charge` observed so far |
| `status` | `COMPLETED` | Only `COMPLETED` observed so far |
| `cardId` | `<19-digit id>` | Resolve via `getMyVirtualCards` |
| `cardLastFourDigits` | `<4 digits>` | Useful label |
| `note` | `Monthly software subscription...` | Free text, often the best available description |
| `receiptStatus` | `MATCHED_AUTOMATIC` | Also seen: `REQUIRED_NO_ATTACHMENT`, `OPTIONAL_NO_ATTACHMENT` |
| `memoStatus` | `HAS_MEMO` | Also seen: `OPTIONAL_NO_MEMO` |
| `spendCategoryStatus` | `HAS_SPEND_CATEGORY` | **A flag, not the category name** |

Envelope: `transactions[]`, `totalCount` (string), `pageIndex`, `pageSize`.
The verification pull returned a `totalCount` in the low twenties.

**Unconfirmed** (the sample was small and all-`COMPLETED`): the enum values for
refunds/credits/reimbursements in `type` and `status`, and whether a refund
arrives as a negative `amount` or a distinct `type`. Confirm on a run that
contains one and update this file.

## 5. Canonical row schema and normalization

Normalize both sources to this. One row per transaction.

| Field | From LIVE (connector) | From EXPORT |
|-------|----------------------|-------------|
| `txn_id` | `id` (always present, always stable) | export's transaction ID. **If the export has none, assign a per-row occurrence key** (source row number, or `date+vendor+amount+owner#n` with `n` counting identical rows) - never a bare content hash |
| `date` | `dateFormatted` | export date column |
| `month` | `YYYY-MM` derived from `date` | same |
| `vendor` | `merchantName` | merchant/vendor column |
| `amount` | `amount` | amount column |
| `currency` | `currency` | currency column |
| `type` | `type` | type column, else `Other` |
| `status` | `status` | status column, else `pending` (conservative) |
| `card` | `cardLastFourDigits` + name via `getMyVirtualCards` | card column if present |
| `description` | `note` | memo/note column |
| `category` | **unavailable** - set `Unknown (not exposed)`, and record `spendCategoryStatus` separately as coverage | category column, else `Uncategorized` |
| `owner` | the **card** (card level, not person level) | cardholder column, else `Unattributed` |

Rules:

- **Completed is the headline.** Totals and MoM use completed/settled rows.
  Pending is a separate labeled figure. Declined/failed excluded with a count.
- **Refunds net down** as negatives against their vendor, category, and month. A
  month may legitimately go negative.
- **Currency:** report in the transaction currency. Mesh returns **no converted
  amount**, so a mixed-currency window gets per-currency subtotals and an
  explicit "no conversion applied" note. Never source an FX rate.
- **Category coverage, not category names, in LIVE.** Report "N of M
  transactions have a category set in Mesh" from `spendCategoryStatus`. That is
  the only honest category statement the connector supports.
- **Vendor names are raw, and the card name often decodes them.** `merchantName`
  is a payment descriptor that often does not name the product; the
  subscription is identifiable only because the card it sits on is named after
  the tool. On `type: SUBSCRIPTION` cards, prefer the card name as the vendor
  label and keep the raw descriptor beside it. Do **not** apply the card name when
  the merchant clearly is not that subscription (a charge from a different
  merchant on a tool-named card keeps its own merchant name).
- **A card's currency can differ from its transactions'.** A card can be
  `currency: EUR` with a EUR limit while its transactions report USD amounts that
  drift by a few percent month to month with no change to the subscription. That drift is the EUR to USD rate, not a price change: say so
  rather than flagging it as a spend increase, and never derive a rate from it.
- **Recurring subscriptions** land in the month charged. Never annualize or
  amortize; flag large one-offs in movers instead.
- **Dedupe only on a stable source ID.** One authorization plus its settlement is
  one transaction - keep the settled one, matched on `id`. **Never deduplicate on a
  content key** like `date+vendor+amount+owner`: two legitimate same-day charges to
  the same vendor for the same amount collide on it, and collapsing them
  understates spend. Rows without a source ID are **kept**, distinguished by their
  occurrence key. If you suspect true duplicates in an export and cannot prove it
  from IDs, report the suspicion in data notes rather than dropping a row.

## 6. EXPORT: the Finance export

Everything downstream of the pull is source-agnostic, so an export slots into the
same pipeline. It is no longer needed for department coverage (a run from Nir's
account gives that); it is needed for the two things the connector never returns:
**category names** and a **cardholder** column for person-level attribution.

**Ask for these columns:** date, amount, currency, merchant/vendor, **category**,
**cardholder/owner**, type, status, and department/team if Mesh carries one.
Without category and cardholder, the export adds nothing over LIVE -
say so rather than filling gaps.

Note in the output that the source was an export and give its export date: an
export is a point-in-time snapshot and can miss late-settling transactions.

## 8. Receipt compliance: the missing-invoice signal

`receiptStatus` is how you find spend with no invoice or receipt attached. Verified
values from the 2026-07-25 pull (one account):

| Value | Means | Chase? |
|-------|-------|--------|
| `MATCHED_AUTOMATIC` | Mesh matched a receipt itself | No |
| `HAS_ATTACHMENT` | receipt uploaded | No |
| `OPTIONAL_NO_ATTACHMENT` | missing, but Mesh does not require one | No |
| `REQUIRED_NO_ATTACHMENT` | **required and missing** | **Yes** |

**The chase list is `REQUIRED_NO_ATTACHMENT` only** (decided 2026-07-25). Mesh's own
requirement flag decides what is chaseable. Chasing an `OPTIONAL_NO_ATTACHMENT` row
undermines the credibility of the whole process: it asks someone for a receipt Finance
does not want, and it trains people to ignore the next nudge, including the one that
matters. Report the `OPTIONAL_NO_ATTACHMENT` count as context if useful, but never
chase it.

Scope the chase to **completed** transactions in the window. A pending charge has
not settled, so a missing receipt on it is not yet a lapse.

`memoStatus` has the same shape for memos (`HAS_MEMO`, `OPTIONAL_NO_MEMO`). Not part
of the chase; mention it only if asked.

### Who to chase, and the gap that blocks it

**The card record carries no cardholder field.** `getMyVirtualCards` returns `name`,
`lastFourDigits`, `status`, `type`, `currency`, `spendingLimit`,
`spendingLimitPeriod`, `amountSpent`, `amountRemaining`, `createdDate` - and no
person. So a transaction resolves to a **card**, and card-to-person has to come from
somewhere else:

1. **The card name**, when it names a person rather than a tool. On the account
   verified so far the names are tools (SaaS product names), which identifies
   the subscription, not who owes the receipt.
2. **A mapping recorded here**, once someone with the department-wide card list has
   confirmed it. There is no such mapping yet.
3. **`getOrganizationContacts`** resolves names and emails org-wide, but does not
   link a person to a card.

**Never guess a recipient.** If a card does not resolve to a person, the chase list
names the **card** and says attribution is unresolved. A nudge sent to the wrong
person about their spending is worse than no nudge, and it is the kind of error that
gets the whole report distrusted. Resolving this mapping is the first job of the
first run from an account that holds the department's cards.

## 7. Growth Marketing scope filter (EXPORT only)

LIVE needs no roster filter: the card list *is* the scope. In EXPORT, where a
cardholder column exists, "Growth Marketing" means Nir Taranto's org. Build the person list **fresh each run** from
the `## Growth Marketing (Nir Taranto)` section of `references/team.md` - that
file is the single source of truth and the roster changes. Do not copy it here.

1. **Department field, if the export has one** - keep rows mapping to Growth
   Marketing or one of its functions (SEO & AI Search, Paid Acquisition, Creator
   Marketing, Marketing Operations, Growth Channels, Inbound SDR).
2. **Owner match** - match cardholder by **email first**, then name. Names
   collide and transliterate inconsistently (see the naming notes in
   `references/team.md` - Jonathan Galili's address uses `yehonatan.galili`).
   `getOrganizationContacts` resolves a partial identity to an email.
3. **Former employees' historical spend** is still Growth Marketing spend. If a
   department field places it in the org, keep it and suffix the owner `(former)`.
   If only the roster is available and the person is not on it, exclude and count
   it - do not guess.
4. **Unmatched rows** are excluded and counted in data notes. A large unmatched
   count means the filter needs work, and that is worth saying out loud.

**Always report rows pulled, rows in scope, and rows filtered out.** Silent
filtering is how a spend report quietly loses a vendor.
