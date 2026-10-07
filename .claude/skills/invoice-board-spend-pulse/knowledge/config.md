# Invoice board spend pulse - config

Config for the `invoice-board-spend-pulse` skill. Read this before every run. Verified against the live board 2026-07-30 (301 items).

## Core config

| Key | Value |
|-----|-------|
| Board | `18390740532` (Invoices and Payments - Growth Marketing) |
| Board owner of record | Dor Druker (created it, departed 2026-08-04); month groups now maintained by Savion |
| DM recipient | `U07LETHMPAP` (Nir Taranto) |
| Cadence | Sunday, Tuesday, Thursday 08:00 Asia/Jerusalem (`0 8 * * 0,2,4`) |
| Reporting unit | Month **group**, not `date4` (Date Paid). Current month is derived in **Asia/Jerusalem** |
| Reported teams | **Creator Marketing and Growth Channels only.** **Known out-of-scope payers** (the remainder table below) collapse into one unitemized `Other teams on this board` line. Anything **unattributable** - blank, unmapped, or a mixed multi-person cell - goes to a **separate `Unattributed` line**, never into the remainder. They are different data-quality states and must never be merged |
| Team attribution | `multiple_person_mkz6t3jw` (Payed by), mapped through the table below |
| Currency | USD (Invoice Sum column carries a `$` unit, no currency field) |

## Columns to read

Only these two are needed for totals by team. Requesting more is waste.

| Field | Column key | Used for |
|-------|------------|----------|
| Invoice Sum | `numeric_mky9safm` | Every total. Bare number, USD |
| Payed by | `multiple_person_mkz6t3jw` | Team attribution via the map below |

Pull `id` and `name` alongside them so an unattributed or blank-amount item can be named.

**Never write to any column on this board.** This skill is read-only (guardrail 1).

## Payer to team map

The board has no team column, so the person who paid is the attribution key. Sourced from `references/team.md` (roster verified 2026-06-15). The `Payed by` cell renders sometimes as a display name and sometimes as an email, so match on either.

### Reported teams

| Payed by (name or email) | Team |
|--------------------------|------|
| Savion Ron Shemesh / savion.ron@riverside.fm | Creator Marketing |
| Dalit Cordoval / Dalit.Cordoval@riverside.fm | Creator Marketing |
| Gili Remen / gili.remen@riverside.fm | Creator Marketing |
| Ofra Toubiana / ofra.toubiana@riverside.fm | Creator Marketing |
| Dor Druker / dor.druker@riverside.fm | Growth Channels |

**Dalit, Gili and Ofra are Creator Marketing Managers reporting to Savion**, so their spend rolls into Creator Marketing rather than standing alone. That is the single most load-bearing line in this map: Dalit and Gili are the two largest creator payers after Savion himself, and dropping them would understate Creator Marketing by roughly a third.

**Ofra Toubiana (Senior Creator Marketing Manager) joined 2026-09-06** and is mapped ahead of her first invoice, on the same basis as Dalit and Gili - her reporting line in `references/team.md`, not a vendor or Type inference. She has no board history, so a run that reports no Ofra spend is the expected state, not a lookup failure.

**Dor Druker departed 2026-08-04; Savion Ron Shemesh now covers Growth Channels on top of Creator Marketing.** Keep the Dor Druker row above as-is - it correctly attributes historical invoices already on the board where he is the payer. Do not delete it.

**Dor-presence precedence rule (ruled by Hanan, 2026-08-26):** a `Payed by` cell that **includes Dor Druker attributes to Growth Channels**, even when other names are present. After his departure, Savion and Nir were added to his recurring Growth Channels items (August 2026 examples: `Ron` and `Impact.com`, both `Dor Druker, Nir Taranto, savion.ron@riverside.fm`), so the mixed-cell rule would otherwise send real Growth Channels spend to `Unattributed` - in August that was about $18.5k. This rule is evaluated **before** the mixed-cell and unmapped-name rows in the SKILL.md attribution table. It is an owner ruling about his legacy items, not a guess from vendor or Type.

**Owner-ruled vendor exceptions (Hanan, 2026-08-26):** two vendors attribute to **Growth Channels** by item name, applied after the Dor-presence rule and before the payer map. Both were Dor's vendors (July 2026 payer: Dor Druker) whose `Payed by` moved fully off him after his departure, so the payer map alone would misfile them.

| Item name (prefix match) | Team | Why |
|--------------------------|------|-----|
| MVF | Growth Channels | Dor's affiliates vendor; payer moved to Nir + Raz in August 2026 |
| Saasworthy | Growth Channels | Dor's review-platforms vendor; payer moved to Raz in August 2026 |

These are rulings by the board's owner chain, not inferences - the "never guess the team from the vendor" rule still holds for every vendor not in this table. The daily-report script `tools/daily-reports/build/spend_actuals.py` embeds the same payer map, Dor-presence rule, and exceptions for the channel report's spend lines - **change the two together**.

**B2B vendors - daily report only (Nir, 2026-09-19).** Nir asked which non-PPC costs the daily channel report should carry and ruled: **Savion's, Raz's, Erika's and Dor's - not Hanan's**, plus his own B2B vendor invoices on a line of their own. `tools/daily-reports/build/spend_actuals.py` therefore emits a fourth figure, `b2b_vendors_spend`, for items whose `Payed by` resolves to **Nir alone**, and the channel report renders it as a `B2B vendors` spend line inside the ROI denominator. September 2026: $14,250 (Ziff Davis inv 1328002), which the report had been discarding.

Three boundaries on that rule, so it does not leak:

- **It is evaluated after the Dor-presence rule and the vendor exceptions**, so a legacy cell naming both Dor and Nir still reads Growth Channels. The July 2026 `SWZD Ziff Davis` item (payer Dor Druker) stays Growth Channels; the ruling did not reopen it. The same vendor therefore sits on two different lines across months, by payer - that is the ruling as given, not a bug to tidy.
- **Nir maps only when he is the sole payer.** He pays across teams, which is why this table deliberately left him unmapped; a cell naming Nir *and* someone other than Dor still goes to `Unattributed` rather than quietly landing in B2B vendors.
- **This does not change the thrice-weekly pulse DM.** That message stays two teams plus one remainder line, and Hanan's Marketing Ops invoices stay out of every reported line in both surfaces.

Gaps that stay flagged rather than guessed:

- Any other Growth Channels vendor whose payer cell no longer contains Dor resolves by the plain map: an unmapped payer (Nir - he pays across teams and is deliberately unmapped) sends it to `Unattributed`, a mapped one sends it to that payer's team, which may be wrong. Current example: `DesignRush` (Review Platforms, payer Raz Navon, appeared August 2026 with no amount yet) - once an amount lands it would file under the remainder via Raz. When an item typed Affiliates, Affiliate Networks, Review Platforms, Affiliate Vendors, or partnerships resolves outside Growth Channels, mention it in the run report as a candidate for a ruling here - never move it yourself.
- If Savion starts paying for Growth Channels vendors on his own, his `savion.ron@riverside.fm` entry is indistinguishable in this table from his Creator Marketing spend and would silently misattribute to Creator Marketing. This map cannot resolve that split from the `Payed by` column alone - if Growth Channels spend looks understated, flag it as a known limitation rather than guessing at a split. **This is now the norm** (September 2026: Impact, PartnerStack and Ron Davidman, ~$31k, all paid by Savion). The pulse DM still carries the limitation; the daily reports resolve it with the Type split below.

**Type split - daily reports only (Hanan for Nir, 2026-10-04).** `tools/daily-reports/build/spend_actuals.py` applies the rules above to decide which invoices count, then puts each counted invoice on a line by its `Type` (`color_mm0e2221`): `Affiliates` → Affiliates; `Affiliate (Freelance and Platforms)`, `Freelance`, `Affiliate Vendors`, `Creators Freelancer / Platform Fees` (and the retired `Affiliate Networks`) → Affiliate freelancers & platforms; `B2B Vendors` → B2B vendors; any other Type keeps its payer line. The Type split never moves an out-of-scope item (Marketing Ops, an unmapped payer) into a reported line. It reads Type as the board owners filed it, so it is not the forbidden "guess the team from the vendor". This does not change the pulse DM.

### Remainder - not reported by team

Everyone else who files on this board collapses into the single `Other teams on this board` line. Listed here so a run can tell "known but out of scope" apart from "unmapped", which is a different problem.

| Payed by (name or email) | Actual team | Treatment |
|--------------------------|-------------|-----------|
| Hanan Amos / hanan.amos@riverside.fm | Marketing Operations | remainder |
| Jonathan Galili / yehonatan.galili@riverside.fm | Marketing Operations | remainder |
| Erika Varangouli / erika.varangouli@riverside.fm | SEO & AI Search | remainder |
| Amir Bar-Tikva / amir.bartikva@riverside.fm | SEO & AI Search | remainder |
| Ortal Hadad / ortal@riverside.fm | SEO & AI Search | remainder |
| Raz Navon / raz.navon@riverside.fm | Paid Acquisition | remainder |
| Jarred Ilan Berman / jarred.berman@riverside.fm | Paid Acquisition | remainder |
| Ayelet Jacobson / ayelet.jacobson@riverside.fm | Inbound SDR | remainder |

A payer in **neither** table, or a blank `Payed by` cell, goes to an **`Unattributed`** line with its item count - never into a reported team and never into the remainder, because an unmapped payer could belong to either and guessing would corrupt the figure. Never infer a team from the vendor, the Type, or the payment method.

The two team sums, the remainder, and any unattributed amount must add up to the group's **populated-amount total**: the sum of every `numeric_mky9safm` value that is present, blanks excluded. Blanks are excluded from both sides of the check, so they can never make a correct run look inconsistent. **Amounts and counts reconcile separately** - compare money against the populated-amount total and items against the retrieved item count, never one against the other. A numeric `0` is populated and belongs in the amount side. If the check fails, this map has a gap: take the diagnostic path rather than sending figures that do not reconcile.

When someone joins or moves team, update this table and `references/team.md` together.

## Month group IDs

> **This table is a cache, not the source of truth.** It stops at October 2026. Resolve the month group by **title against the live board** every run (`boards { groups { id title } }`) and use this table only as a fallback and a sanity check. A month past the end of this table must never be reported as `no group created yet` on the strength of its absence here - that would send a false "no invoices" for both teams. Absence is only real when the **board** has no group with that title. When you find a title on the board that is missing below, note it in the run report so the row gets appended.

| Group | ID |
|-------|----|
| Emailed items (not reported, never written) | `group_mm1fdkmn` |
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

> `group_title` and `topics` are the real monday IDs for the board's two original groups, not placeholders. Do not "fix" them.

If the **live board** has no group titled for the current month, report `no group created yet`. **Do not create it** - group creation on this board belongs to Savion (Dor Druker, who used to share this, departed 2026-08-04). A month simply missing from the cache above is not the same thing and must not be reported that way.

## Message template

**Use standard markdown, not Slack mrkdwn.** This connector (`slack_send_message`) converts standard markdown: `**bold**`, `_italic_`, and `[text](url)` links. Slack's native mrkdwn (`*bold*`, `<url|text>`) does **not** render here - a `<url|text>` link posts as that literal string. Confirmed by sending on 2026-07-30.

Sentence case, no em dashes, no exclamation marks. The one section emoji below is the only decorative character allowed. Footer mandatory.

```text
💰 **Creator Marketing and Growth Channels spend - {MONTH}**

• **Creator Marketing**: ${AMOUNT}   (last month ${PREV})
• **Growth Channels**: ${AMOUNT}   (last month ${PREV})
{a team with no items that month renders `no invoices this month` instead of an amount}
{a team whose every amount is blank renders `{N} invoices, amount not entered` - never $0}
{a team whose populated amounts genuinely sum to zero renders `$0 across {N} invoices`, never a bare $0}

**Both teams, {MONTH}: ${TWO_TEAM_TOTAL}**  ({N} invoices)
{if the bucket has items: Other teams on this board: ${REMAINDER} ({M} invoices) - omit only when it has NO items, never merely because the amounts sum to zero}
{if that bucket has items but every amount is blank: Other teams on this board: {M} invoices, amount not entered}
{if any: **Unattributed**: ${AMOUNT} ({P} invoices with a blank, unmapped, or mixed-team Payed by)}
{if that bucket has items but every amount is blank: **Unattributed**: {P} invoices, amount not entered}

{if any: {K} invoices have no amount entered, so these figures are an understatement.}
Board: [Invoices and Payments](https://riversidefm.monday.com/boards/18390740532)
Next report: {NEXT_DAY} {NEXT_DATE}

_Posted by the Marketing OS agent_
```

### Computing the next-report line

The cadence is Sunday, Tuesday, Thursday. From the current run, the next report is:

| This run | Next report |
|----------|-------------|
| Sunday | Tuesday (+2 days) |
| Tuesday | Thursday (+2 days) |
| Thursday | Sunday (+3 days) |

Render it as day name plus date, e.g. `Next report: Sunday 2 August`. Derive it from the actual run date **in Asia/Jerusalem** rather than hardcoding - a manual on-demand run on some other weekday must still point at the next real cadence day, which is the next Sunday, Tuesday, or Thursday strictly after today. Do not print a next-report line that has already passed.

### Three things the template must never do

1. **Never label the two-team sum as the month total, the board total, or Growth's spend.** It is `Both teams, {MONTH}`. Other teams file on this board, and the remainder line exists precisely so the sum cannot be misread.
2. **Never print `$0` for a reported team with no items that month** - use `no invoices this month`. Both teams spend through Mesh cards and ad platforms this board never sees, so `$0` would read as "spent nothing" and be false.
3. **Never rank, praise, or criticize a team's figure**, and never itemize the remainder. Report the numbers. Nir draws the conclusions.

## Reference figures (verified 2026-07-30, for sanity-checking a run)

If a run's numbers diverge wildly from this shape, suspect a mapping or query bug before believing it.

| Line | July 2026 | June 2026 |
|------|-----------|-----------|
| Creator Marketing | $131,137.77 | $134,879.25 |
| Growth Channels | $82,725.36 | $141,418.00 |
| **Both teams** | **$213,863.13** | **$276,297.25** |
| Other teams on this board | $2,800.00 | $2,879.00 |
| Unattributed | none | none |
| Populated-amount total (reconciliation denominator) | $216,663.13 | $279,176.25 |
| Items retrieved / with an amount | 54 / 53 | 54 / 54 |

The remainder in both months is Marketing Operations. SEO & AI Search, Paid Acquisition, and Inbound SDR filed nothing on this board in either month, which is why the remainder is small - it is not evidence that those teams spend little, only that their spend does not arrive as board invoices.

July also carries 1 invoice with no amount entered, excluded from every figure above: the item **named** `Cristi Cristian Cotovan` (item `12418515805`). That is the item name, not the payer - its `Payed by` is `savion.ron@riverside.fm`, which is why it attributes to Creator Marketing rather than `Unattributed`. Attribution always follows `Payed by`, never the item name.
