# Designing a cloud routine: cadence, act condition, bail-out

Load this when the thing being built is a **cloud routine** (Step 0, type 5),
before filling template 5. It covers the three design decisions template 5 used
to leave implicit (how often to check, when to act, when to stop) and the rule
Step 1 now asks about instead of offering a bare Daily / Weekly / Monthly menu.

Adapted from the `marketing-loops` skill in Corey Haines's
[marketingskills](https://github.com/coreyhaines31/marketingskills) (MIT). The
nine-part loop anatomy and the cadence rule are kept. Their guardrails file is
not imported: this repo's rules are stricter and already live in `CLAUDE.md`
(confirm before any mutation), `docs/platform-integration.md` §7 (the only
routines authorized to write unattended) and `references/change-control.md`
(the ways a routine fails to run at all).

## The cadence rule

Match how often the routine **checks** to how fast the signal actually changes,
not to how often someone would like an update. Over-frequent routines are the
common failure: they produce output nobody reads, and they train the reader to
skip the one run that matters.

| Signal | Check cadence | Why |
|--------|---------------|-----|
| Rankings, Search Console impressions, backlinks | Weekly | Move slowly; daily checks read noise |
| Ad creative fatigue, CPA drift | Every 2 to 3 days | Platform feedback loops are days, not hours |
| Signup / activation funnel step rates | Weekly | Needs enough signups to be significant |
| Inbound demo requests, PQL crossings | Daily | The response window is short |
| Content or page decay | Monthly | Traffic erosion is gradual |
| Competitor pricing / positioning pages | Weekly | Shifts are infrequent but matter |
| Invoices, backlog hygiene | Weekly / monthly | The underlying queue fills slowly |

Two mechanical limits sit under the table (`references/change-control.md`,
failure mode 4): cron is UTC-only, so record the intended local time next to
the cron expression, and the minimum interval is one hour.

## Check is not act

Most runs of a healthy routine find nothing to do and say so. Design the two
separately:

- **Check cadence**: how often it looks.
- **Acts when**: what must be true for it to do anything beyond logging "no
  action". A threshold, a new record not in the ledger, a delta against
  baseline.

A routine that acts every run is usually acting on noise. A ranking watch that
checks weekly should post only when a priority page drops past a stated number
of positions, and a demo digest that runs daily should say "no new requests"
rather than re-summarize yesterday's.

## The nine parts, mapped to template 5

| Part | Template 5 section | New here |
|------|--------------------|----------|
| Check cadence | `## Cadence` | Justify it against the table above |
| Acts when | `## Acts when` | Yes |
| Purpose | Opening line | |
| Skills used | `## Steps` | Which skills the body invokes |
| Loop body | `## Steps` | |
| Self-check | `## Self-check` | Yes |
| State / idempotency | `## Constraints` (ledger / marker) | |
| Stop / bail-out | `## Stop / bail-out` | Yes |
| Output | `## Done when` plus the schema | |

If the author cannot fill **Acts when**, **Self-check** and **Stop / bail-out**
concretely, the routine is not ready to schedule.

## Self-check before acting

Before the routine acts, it rules out the three false positives that look like
a signal:

1. **Tracking or source breakage**: a drop to zero is a broken event more often
   than a real collapse. Compare to a known-good baseline first.
2. **Seasonality and calendar**: compare to the same period last month or last
   year, not only to last week. Weekends and holidays are not churn.
3. **Small sample**: state the minimum count below which the run logs "too few
   to read" and exits.

Then name the failure kind before picking the fallback
(`references/agent-prompting.md`, block 7): glitch, tool down, empty, or wrong.

## Stop / bail-out

Every routine has one, including heartbeats. "n/a" is not an answer.

- **Source outage**: report "stale data, no run" and exit. Never fabricate
  movement from partial data.
- **Manual disable**: the schedule is the kill switch; the skill doc names the
  trigger so someone can find it.
- **Escalate instead of acting** on: a revenue or spend anomaly, a high-value or
  strategic account, anything that would go public, anything that would delete
  or contact many records at once. Stage a draft and stop.
- **Vanity check**: if the output goes unread for two cycles, the routine posts
  once asking whether to continue, then pauses. A digest nobody reads is worse
  than none.

## When not to build a routine

- **The real work is strategy or creative direction.** Routines maintain and
  optimize; they do not set positioning or invent a campaign.
- **The action publishes or spends.** Auto-drafting is fine; auto-publishing
  and budget shifts stay human-gated. `docs/platform-integration.md` §7 lists
  the only routines allowed to write unattended, and each writes to a narrow,
  ledgered surface.
- **The signal is too sparse.** A weekly conversion-rate check on a few dozen
  visits measures noise.
- **Nobody would act on the output.** Then it is a report, and
  `references/growth-reporting.md` is the place to decide whether it exists.

## Exemplars in this repo

The live routines and their cadences are catalogued in
`docs/platform-integration.md` §7. `nir-mql-live-report` (daily, prior-day
window, ledgered) and `invoice-inbox-to-monday` (weekly, Sunday, ledgered) are
the cleanest examples of check-vs-act done right. Candidate routines that do
not exist yet are in `routine-ideas.md`.
