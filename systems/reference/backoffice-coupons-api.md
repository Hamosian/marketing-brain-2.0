<!-- last-reviewed: 2026-10-06 -->
# Backoffice Marketing Coupons API

> Platform's internal API over Riverside's Stripe coupon catalog: list coupons, create them, and list, add, switch off or bring back the promotion codes customers type at checkout. We are a caller with one API key. **Only Jonathan Galili or Hanan Amos can request or approve its use.**

## Overview

Six endpoints under `https://api.riverside.fm/backoffice/api/coupons`, authenticated by one header, `X-Api-Key: $MARKETING_BACKOFFICE_API_KEY`. They read and write the same Stripe catalog the Backoffice Coupons page uses, so every write is live in production the moment it returns 200. There is no draft state and no undo endpoint.

The full reference is Platform's PDF (see Pointers). This doc holds what the PDF does not: the access rule, how we use the API, and what we learned running it.

## Access rule

**Marketing-brain processes may use this API only when the request comes from Jonathan Galili or Hanan Amos, or when one of them has approved it.** This covers every agent, skill, routine and script in this repo, and it covers reads as well as writes. Set 2026-09-30 by Jonathan Galili.

- **Who is asking** is the session's user (`git config user.email`): `yehonatan.galili@` for Jonathan and `hanan.amos@` for Hanan, on `riverside.fm` or `riverside.com` (`references/team.md`).
- **Approval for anyone else** has to come from Jonathan or Hanan themselves, for the specific operation: in the session, or in a message from them that the agent can read. "Hanan said it's fine" relayed by the requester, a ticket, or a Slack post from someone else is not approval.
- **Approval is per operation.** Approving one migration does not approve the next one, or a routine.
- **No scheduled routine calls this API** unless Jonathan or Hanan approved that routine, and the approval is recorded in the routine's skill.
- **Without approval, stop.** Say who can approve and what they would be approving, and do nothing else with the API, not even a read.

`tools/promo-code-migration/` enforces this in code: every command that calls the API needs `--approved-by jonathan|hanan`, and the ledger records it on every call.

## What the Team Owns

- The API key's use from this repo, under the access rule above.
- `tools/promo-code-migration/`: the tested tool for moving codes between coupons.
- Which coupon each partner and creator code points at, and the record of every move (Change log below).

## What the Team Does NOT Own

- **The API, the gateway and the key.** Platform Enablement owns them. Requests go to `#platform-enablement-requests` (`C0B1FN9HS9J`); see "Gaps filed with Platform" below. There is no `#platform-enablement` channel, only `-requests`, `-fyi` (`C0B455UBVH6`) and `-code-review` (`C0B55JTM49W`) (verified 2026-10-06).
- **Editing or deleting a coupon.** There is no endpoint for either. It happens in the Stripe Dashboard, outside this API.
- **The Stripe catalog as a whole.** Coupons and codes are also made in Backoffice and the Stripe Dashboard. Every code on `30days` had `createdBy: null`, which means it was made in the Dashboard.

## Gaps filed with Platform

The API covers **5 of the 9** Stripe coupon and promotion-code endpoints, and each of those only in part. The rest is filed as **[ENB-1142](https://linear.app/riverside/issue/ENB-1142/marketing-coupons-api-add-the-missing-stripe-coupon-and-promotion-code)** on Linear's **Platform Enablement** team (`c60ff78f-ce48-4ed6-ae85-2bc43b25593b`): opened 2026-10-04 by Jonathan Galili, still in Triage, unassigned and with no priority as of 2026-10-06. The itemised P1/P2 list and the acceptance criteria live in the issue and in its [spec doc](https://docs.google.com/document/d/1KrQGNqYXW3NoUaEbmcBkk8RUvdkUVno901CicPn8ycw/edit); don't restate them here.

The gaps that bite most often already appear elsewhere in this doc: no per-code expiry or cap on create (Moving codes, step 1), no `metadata` on coupons or codes, no pagination past 100 codes, and no way to read expired or fully redeemed coupons from `/catalog` (When It Breaks).

**Already shipped, don't re-file:** promotion-code restrictions, in ENB-1106. ENB-1103 set the pattern for a call that accepts either a Riverside account id or a Stripe customer id.

**How to file.** ENB-1142 was created from a post in `#platform-enablement-requests` (`C0B1FN9HS9J`), and the Linear issue carries that Slack message as its source attachment. File there rather than opening a Linear issue by hand, the same rule that applies to DevOps (`references/other_teams.md`).

## The monthly and yearly catalog split

One product catalog serves both the monthly and the yearly plan, so a coupon cannot be scoped to one billing interval. Asaf Fox established that splitting the catalog is the only fix. **Assessing it sits with the Core Platform Team**, not Platform Enablement (Jonathan Galili, 2026-10-06). It has no org priority behind it; the EU-to-US Stripe account migration is the active Platform priority, and possibly the cheapest moment to do the split.

Until it happens, a code applied through a URL lands on the default yearly plan, so a 100%-off code on that path gives away a year. That hazard is live and independent of the split itself.

## How Claude Works With This

| Task | How |
|------|-----|
| See which coupons are live, and their terms | `GET /catalog`. Lists redeemable coupons only: expired, fully redeemed and deleted ones are left out |
| List a coupon's codes | `GET /promotion-codes?couponId=<id>`. Active and inactive, **one page of 100 at most**: read `truncated` |
| Add a code to a coupon | `POST /promotion-codes/create` with `requestId`, `couponId`, `code` |
| Switch a code off or back on | `POST /promotion-codes/deactivate` or `/activate` with `{"promotionCodeId": "promo_..."}` (the Stripe id, not the text). Idempotent |
| Move codes from one coupon to another | `tools/promo-code-migration/` (procedure below). Never by hand in a loop |
| Create a coupon | `POST /create`. It is live the moment it returns, with no undo, so confirm every field first |

Transport: use `curl`, or set a real `User-Agent`. Python's default `urllib` client gets a Cloudflare 403 (error 1010) before the request reaches Backoffice (`references/integration-debugging.md`, "Separate transport failures from application failures").

Key storage: `~/.config/marketing-os/backoffice.key` (mode 600) or the `MARKETING_BACKOFFICE_API_KEY` environment variable. The setup command is in the tool's README. Never paste the key, or a share link to it, into a prompt: session transcripts keep the full text of every prompt.

## Moving codes between coupons

There is no move call, and a code's text must be unique among active codes (case-insensitive). So a move means: switch off the old code, which releases its text, then create the same text on the new coupon. The tool does this one code at a time:

1. **Compare the two coupons in the catalog first.** Every code takes its discount, duration, total cap, expiry and product scope from the coupon it points at. The create call cannot set a code's own expiry or cap.
2. **Plan from the live list, not an export.** Skip codes that are already inactive: creating one makes it live again. Skip text that is already active on the target: someone may have moved it by hand.
3. **Dry-run, then one canary, then the batch, then reconcile**, with the approver looking at each step before the next.
4. **Pair the writes per code.** Each code is offline for one write gap (6 to 7 seconds). Switching everything off first would leave the early codes offline for the whole run.
5. **If a create fails, reactivate the old code at once.** Stripe refuses the reactivation if the new code took the text, so a successful reactivation proves nothing landed.
6. **To roll back one code**, switch off the new code and then reactivate the old one. After a rollback, use a fresh `requestId`: a reused one replays the first result for 24 hours.

## When It Breaks

Each item below was hit or checked on the 2026-09-30 run.

- **403 with a Cloudflare JSON body (`error_code: 1010`, "browser_signature_banned") is the gateway, not the key.** The key was never checked. Switch to `curl` and run the same call as a control. A real key problem is a 401.
- **A pre-flight that fails must stop the run, not show as empty data.** The first pre-flight script rendered three 403s as "0 codes, coupon not in catalog". Treat any non-200 read as a halt.
- **Backoffice UI exports are not create payloads.** They carry `__typename` and `null` restriction fields, and the create call rejects both (null values and unknown keys are 400s). When restrictions are the default (`false / null / null / []`), leave the `restrictions` object out.
- **The list stops at 100 rows.** After the move `growmonthoffsep` held 106 codes and the list came back `truncated: true`. The newest codes were all on the first page, but verify moved codes against the ledger, not the list alone.
- **The audit trail shows `marketing-service@riverside.fm`, not the person.** The public gateway strips `X-User-Id`, so `createdBy`, `deactivatedBy` and `activatedBy` all read the service account. The tool's ledger is the only record of who approved a change.
- **Write budget: 10 a minute, shared by the whole key.** Creates, deactivations and reactivations all count. At one write every 6.7 seconds, 178 writes ran with no 429s. Another caller using the key at the same time shares the budget.
- **A 400 that mentions Stripe rate limiting is temporary.** Wait and retry. Every other 4xx is Stripe refusing the request, and the message names the field.
- **Redemption counts do not move.** A new code starts at `timesRedeemed: 0`, and history stays on the old `promo_` id. Reports filtered on the old coupon id split at the move time.

## Change log

| Date | Change | Approved by |
|------|--------|-------------|
| 2026-09-30 | (Linear PLA-2678) 89 active codes moved from `30days` ($29 off, once) to `growmonthoffsep` ($45 off, once), 14:49 to 15:15 UTC. The 10 codes already inactive stayed on `30days`. Three of them (`THINKMEDIA`, `demandcurve`, `PeterYang`) already existed on `growmonthoffsep`, created separately before this run. Reports keyed on `30days` see new redemptions under `growmonthoffsep` from this date. | Jonathan Galili |

## Related Systems

- `references/integration-debugging.md`: transport-versus-application failures, including Cloudflare 1010.

## Pointers

- API reference (Platform's PDF): <https://drive.google.com/file/d/1e06GiTKXh0wdVQcyQtECBTDzJDN-u-gr/view?usp=sharing>
- Requests, questions and outages: `#platform-enablement-requests` (`C0B1FN9HS9J`)
- Open gaps: [ENB-1142](https://linear.app/riverside/issue/ENB-1142/marketing-coupons-api-add-the-missing-stripe-coupon-and-promotion-code) (Platform Enablement, Triage)
- Tool: `tools/promo-code-migration/`
- Stripe coupons (Dashboard): <https://dashboard.stripe.com/acct_1FQWAGGcqNE24Ue5/coupons/30days>, <https://dashboard.stripe.com/acct_1FQWAGGcqNE24Ue5/coupons/growmonthoffsep>
