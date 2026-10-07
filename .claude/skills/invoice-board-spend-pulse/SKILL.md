---
name: invoice-board-spend-pulse
description: Three-times-a-week (Sun/Tue/Thu) or on-demand spend pulse DM'd to Nir, read from the "Invoices and Payments - Growth Marketing" monday board (18390740532). This month's invoice totals for two teams only - Creator Marketing and Growth Channels - with the previous month beside them and one unitemized remainder line for everything else. Read-only (never creates, edits, or moves an item). Trigger phrases - "invoice board pulse", "spend pulse", "spend by team", "totals by team", "what have Creator Marketing and Growth Channels spent", "invoice board update for Nir". Distinct from /mesh-expenditure-report (reads Mesh card spend, not this board).
---

# Invoice board spend pulse

The Marketing OS agent's thrice-weekly **spend total for Nir Taranto**, computed from the monday board **Invoices and Payments - Growth Marketing** (`18390740532`) - the board Savion Ron Shemesh keeps grouped by month (created by Dor Druker, who departed 2026-08-04).

It answers one question: **how much have Creator Marketing and Growth Channels spent this month.** Those two teams only. Totals only, no line items, no exception lists.

**This is a read-only reporting skill.** It never creates, edits, moves, or deletes a board item, and never touches a file or status column. The only side effect is one Slack DM. That constraint is what makes it safe to run unattended on a board six people write to by hand.

## Scope

The audience is a Senior Director. Target **6 to 8 lines**. Two team totals, current month, previous month beside them, one remainder line. Nothing else.

**Related but different:** `/mesh-expenditure-report` reports **card and subscription spend from Mesh**, Finance's spend platform. This skill reports **invoices filed on the monday board**. The two do not reconcile to the same number and must never be presented as if they do - a Mesh card charge and a board invoice are different records of different things.

## Config

Board IDs, column keys, group IDs, the payer-to-team map, the recipient, and the message template live in `knowledge/config.md`. Read it first.

## What it computes

### Two teams only
**Reported teams: Creator Marketing and Growth Channels.** Nothing else. Marketing Operations, SEO & AI Search, Paid Acquisition, and Inbound SDR are deliberately out of scope - do not add them back, and do not report them as `$0`.

The month group matching the **run date's calendar month in Asia/Jerusalem** (a run on 2026-08-02 reports the `August 2026` group). Resolve the month in that timezone explicitly, never in UTC or the host's local zone - an on-demand run late on the last evening of a month would otherwise report the next month and show both teams as empty. Sum `numeric_mky9safm` (Invoice Sum, bare number, `$`, treat as USD) for each of the two teams, plus the same two figures from the **previous month group** beside them, so each number is interpretable rather than a bare figure repeated three times a week.

**Team comes from `multiple_person_mkz6t3jw` (Payed by), mapped through the payer-to-team table in config.** The board has no team column, so the person who paid is the attribution key. Dalit Cordoval, Gili Remen and Ofra Toubiana all report to Savion, so their spend rolls into Creator Marketing.

**`Payed by` is a monday People column, so it can hold more than one person** and its `text` value then arrives comma-separated (`Dor Druker, Savion Ron Shemesh`). Never assume one name. Split on commas, trim, and resolve every name:

| Resolved names | Attribution |
|----------------|-------------|
| **Any name is Dor Druker** (checked first - his legacy Growth Channels items; Savion/Nir were added to them after his 2026-08-04 departure, see config) | Growth Channels |
| All map to the same reported team | That team |
| All map to the remainder | Remainder |
| They map to **different** teams, or mix reported with remainder | `Unattributed` |
| Any name is unmapped | `Unattributed` |

Never split one invoice's amount across teams and never pick the first name - a shared invoice has no defensible single owner, and guessing would silently move money between two teams' figures. Two exceptions exist, both owner rulings (Hanan, 2026-08-26) recorded in `knowledge/config.md`, not guesses: the Dor-presence row above (Dor's name on a cell marks one of his legacy Growth Channels items), and the vendor-exceptions table there (MVF and Saasworthy attribute to Growth Channels by item name, applied before the payer map). When an item typed Affiliates, Affiliate Networks, Review Platforms, Affiliate Vendors, or partnerships resolves outside Growth Channels, mention it in the run report as a candidate for a ruling - never move it yourself.

**Report by month group, not by Date Paid.** The group is how Savion actually organizes the board, so it is the reporting unit.

### The three rules that keep the totals honest

1. **Label the total for exactly what it covers.** The reported figure is `Creator Marketing + Growth Channels`, not the month's board total - other teams file on this board too. Never label a two-team sum as the month total or as Growth's spend.
2. **Carry one remainder line.** Report **known out-of-scope payers** as a single `Other teams on this board: $X (N invoices)` figure, unitemized. It exists so the two-team sum cannot be misread as the whole board, and it is the only trace of those teams. **Omit it only when the bucket has no items** - never because its amounts sum to zero, which is a different thing entirely.
3. **Anything unattributable goes to an `Unattributed` line, never silently into either reported team.** That covers a blank `Payed by`, a payer absent from the config map, and a multi-person cell whose names resolve to different teams (see the table above). Its amount appears on its own line with the item count - an attribution gap must never quietly shrink Creator Marketing or Growth Channels. Never guess the team from the vendor, the Type, or the payment method.

### The three states a team line can be in

A team line has three distinct outcomes and they must never be collapsed into each other:

| State | Condition | Renders as |
|-------|-----------|-----------|
| Figure | Has items, at least one with a **populated** amount | `$X` |
| No records | Has **no items at all** that month | `no invoices this month` |
| Amount unavailable | Has items, but **every** amount is blank | `N invoices, amount not entered` |

The third state is the one that is easy to get wrong. `$0` would invent a number the board does not contain, breaking guardrail 2; `no invoices this month` would be plainly false when invoices exist. So name it for what it is. Such a team contributes **nothing to the combined figure** but **does contribute its invoice count**, and the combined line carries the same caveat so the sum is never read as complete.

**`0` is a populated amount, not a blank.** A genuine zero is a fact the board asserts; an empty cell is the absence of a fact. Treat them as different in every calculation: a `0` counts toward the sum (adding nothing) **and** toward the invoice count, and never appears in the blank-amount tally. Only a truly empty `numeric_mky9safm` is blank.

That distinction creates one case worth spelling out: if a team's populated amounts genuinely sum to zero, render it as `$0 across N invoices` rather than a bare `$0`. The bare form is reserved-against precisely because it reads as absence, and here the figure is real. Absence still renders `no invoices this month` - these teams spend through Mesh cards and ad platforms this board never sees, so a bare `$0` standing in for "no records" would read as "spent nothing" and be false.

Blank amounts are always excluded from the sums and reported as a trailing count (`N invoices have no amount entered`), because they make the figures an understatement by an unknown amount.

**The same three states apply to the `Other teams on this board` and `Unattributed` lines**, not just to the two reported teams. Each bucket independently renders: nothing at all when it has no items; `N invoices, amount not entered` when it has items but every amount is blank; and a figure otherwise. A bucket whose populated amounts genuinely sum to zero renders `$0 across N invoices`. The trap this closes: an all-blank bucket sums to zero, and a naive `omit if zero` would delete the only evidence that those invoices exist.

## Guardrails (non-negotiable)

1. **Read-only.** No `create_item`, no `change_item_column_values`, no group creation, no file or status writes on board `18390740532`. If a run surfaces something that needs fixing, mention it and let a human do it.
2. **Never invent a number.** Every figure traces to a column read in this run. Blank stays blank - never estimated, never inferred from a similar vendor, never carried forward.
3. **Never blend Mesh and board figures.** See "Scope".
4. **One recipient.** The DM goes only to the Slack ID in `knowledge/config.md` (Nir Taranto, `U07LETHMPAP`). Never a channel.
5. **Connector unavailable means stop.** If monday or Slack is unavailable, stop and report which one. Never send a partial or zero-filled report - a wrong total is worse than no message.
6. **Team totals are routing facts, not performance judgements.** Report the figure. Do not rank teams, editorialize on whether a number is high or low, or imply anyone overspent. This lands in the inbox of the person those teams report to.

## Steps

### 1. Load config
Read `knowledge/config.md` for the group table, column list, payer-to-team map, recipient, and template.

### 2. Resolve the month groups by title, live
**Do not trust the config table as the only source of group IDs.** It is a cache that stops at a fixed month, so a month past the end of it would otherwise look identical to a month that does not exist - and reporting a real month as absent would send Nir a false "no invoices" for both teams. Resolve titles against the live board every run:

```graphql
boards(ids: [18390740532]) { groups { id title } }
```

Match the target month's title in `<Month YYYY>` format (e.g. `November 2026`), derived from the run date in Asia/Jerusalem, case-insensitively, and treat the config table purely as a fallback and a sanity check.

**The current and previous months fail differently and must be handled separately.** The current month is the report; the previous month is only a reference figure. Resolve each independently and never pass an unresolved ID into the items query:

| Situation | Action |
|-----------|--------|
| Current month's title on the board | Normal, report it |
| **Current** month's title absent from the board | The month genuinely has no group yet. Report `no group created yet`, send that as the pulse, **never create the group** |
| **Previous** month's title absent from the board | Not a failure. Query only the current group and render the reference as `last month not on the board` |
| Title on the board but missing from the config table | The cache is stale. Report normally **and** flag in the run report that config needs the new ID appended |

### 3. Read the items
Query only the group IDs that actually resolved - one ID if the previous month is absent, two otherwise:

```graphql
boards(ids: [18390740532]) {
  groups(ids: [<resolved ids only>]) {
    id title
    items_page(limit: 500) {
      cursor
      items { id name column_values(ids: ["numeric_mky9safm","multiple_person_mkz6t3jw"]) { id text } }
    }
  }
}
```

**Page until the cursor is null.** A month group is around 54 items today, but a single page silently truncating a busy month would understate the totals with no visible symptom - the worst failure this skill has, because the number still looks plausible. If `cursor` comes back non-null, follow it with `next_items_page(cursor: "...", limit: 500)` and keep going until it is null. Assert the item count you summed matches the count you retrieved, and say so in the run report.

### 4. Compute
Creator Marketing and Growth Channels sums for both months, their combined figure, the remainder line, any `Unattributed` line, and the blank-amount count. **Do the arithmetic in a script, not mentally** - 50+ items per month makes a hand sum a silent-error risk.

Check that the two team sums, the remainder, and any unattributed amount add up to the group's **populated-amount total** - the sum of every present `numeric_mky9safm` value, blanks excluded from both sides so they cannot make a correct run look broken. **Reconcile amounts against amounts and counts against counts**, never one against the other: money against the populated-amount total, items against the retrieved item count.

**If they do not reconcile, take the diagnostic path.** This overrides the always-sends rule in step 5, and the two must not be read as being in tension: the pulse still goes out, but it carries **no figures**. Send instead a short DM naming what failed (`the payer map does not reconcile against the board total for August, so figures are withheld this run`), the size of the discrepancy, and that the next pulse will retry. Then surface the same thing in the run report.

Withholding beats both alternatives. Sending unreconciled totals would put a wrong number in a director's hands, which guardrail 2 exists to prevent; sending nothing would be indistinguishable from a quiet board, so Nir would read broken as calm.

### 5. Send the DM
One Slack DM to the config recipient, following the template in `knowledge/config.md`. **Standard markdown, not Slack mrkdwn** - this connector converts `**bold**` and `[text](url)`; a native mrkdwn `<url|text>` link posts as that literal string (verified 2026-07-30). Team style: sentence case, **no em dashes, no exclamation marks**, no decorative emoji beyond the single section marker in the template. Mandatory final line: `_Posted by the Marketing OS agent_`.

Close with a **next-report line** (`Next report: Sunday 2 August`) so Nir knows when the following one lands and can tell a missed run from a quiet board. Compute it from the actual run date **in Asia/Jerusalem** (the same zone as the reporting month, for the same reason) using the cadence table in config - the next Sunday, Tuesday, or Thursday strictly after today in that zone. Never hardcode it, and never print a date that has already passed.

**This pulse always sends**, including on a quiet run - a total that has not moved is itself the signal. There are exactly two departures from that, and they differ in kind:

- **Reconciliation failure** (step 4): the DM still goes out, as a diagnostic with no figures.
- **Connector unavailable** (guardrail 5): no DM at all, because none is possible. If Slack is down the message cannot be delivered; if monday is down there are no figures to deliver. Stop, change nothing, and surface which connector failed to the caller and the run report.

So the guarantee is precise: **whenever the run can reach both connectors, Nir hears something** - a figure or a diagnostic, never silence. A connector outage is the one case where silence is correct, and it is visible in the run report rather than swallowed.

### 6. Report
Print a short run summary: per-team totals, month total, and the Slack message link.

## Notes
- **Cadence.** Sunday, Tuesday, Thursday at 08:00 Asia/Jerusalem (`0 8 * * 0,2,4`). Sun-Thu is the Israeli work week, so this lands three times inside it. No state is carried between runs - each run reads the board fresh - so a missed run costs nothing.
- **No snapshot.** Totals-only reporting needs no delta baseline, so there is no state file and nothing to commit. Earlier versions of this skill diffed against a snapshot; that was removed when the scope narrowed to totals.
- **The board is shared.** Savion, Erika, Raz, Nir, and Hanan all file on it, plus `/invoice-inbox-to-monday` and monday's email intake. (Dor Druker filed historically; departed 2026-08-04.) This skill is a reader, not an owner.
- **Amounts are USD.** The Invoice Sum column carries a `$` unit and no currency field. A figure that looks wrong by an order of magnitude is usually a non-USD amount entered raw. It is not this skill's job to convert it, and it is **not a blank-amount case** - the value is present, so it stays in the sums and out of the blank-amount count. Mention it in the run report so a human can check it, and never silently rescale it.
- **Coverage caveat.** This board is not the whole of Growth's spend. Ad platform spend, Mesh card charges, and anything Finance pays without a board item are invisible here. The pulse is a report on the board, and it should never be described to Nir as total Growth spend.
