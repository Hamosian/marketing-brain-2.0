# Promo code migration

Moves a Stripe coupon's active promotion codes onto another coupon, keeping the same customer-facing text. It uses the Backoffice Marketing Coupons API. Built for the 2026-09-30 move of 89 codes from `30days` to `growmonthoffsep`: 178 writes, all 200 on the first attempt, with each code offline for 6 to 7 seconds.

**Access rule:** use this tool, or the API behind it, only when Jonathan Galili or Hanan Amos asked for it or approved it. Every API command needs `--approved-by jonathan` or `--approved-by hanan`, and the ledger records it on every call. The rule and the API's behavior are documented in `systems/reference/backoffice-coupons-api.md`.

## Why it exists

The API has no move call. A code has to be switched off on the old coupon before the same text can be created on the new one, because the text must be unique among active codes. Done by hand that is error-prone: a failed create leaves a partner's code dead, a reused `requestId` replays an old result, and the write budget is 10 a minute. The tool pairs the two writes per code, paces them, rolls back a code whose create fails, and keeps a ledger so a crash resumes cleanly.

## Setup (once)

Get `MARKETING_BACKOFFICE_API_KEY` from Platform Enablement (`#platform-enablement-requests`). Copy it from wherever it was sent (never paste it into a Claude prompt: session transcripts keep the full prompt text), then:

```bash
mkdir -p ~/.config/marketing-os && (umask 077; pbpaste | tr -d '[:space:]' > ~/.config/marketing-os/backoffice.key) && pbcopy < /dev/null && echo saved
```

The tool also reads the `MARKETING_BACKOFFICE_API_KEY` environment variable if it is set.

## Run

```bash
python3 migrate.py plan --from 30days --to growmonthoffsep --canary FORUM --approved-by jonathan
```

Then, in order, each step after the person approving it has looked at the one before:

1. `dry-run`: prints every request body. No calls.
2. `run --only <canary> --execute`: one code. Check both coupons, and test the code at checkout if you can.
3. `run --execute`: everything still pending, quietest codes first. Stops at the first unexpected response.
4. `reconcile`: re-lists both coupons and checks every moved code against the ledger.

`rollback --only CODE --execute` puts a code back: it switches the new one off and the old one on.

The plan, the state and `ledger.jsonl` live in `~/promo-migrations/<from>-to-<to>/`, outside the repo. Keep the ledger: it is the only record that maps each old `promo_` id to its new one.

Before a real run, compare the two coupons' terms in the catalog (`GET /catalog`). Every code takes its discount, duration, cap and expiry from the coupon it points at.

## Test

```bash
python3 test_migrate.py
```

It runs against a mock API with no network or key. The cases: the full run, the canary, a 429, a lost create response, a create that fails, a switch-off that fails, a create and reactivate that both fail, resuming mid-pair, drift between plan and run, rollback then rerun, and the approval gate.
