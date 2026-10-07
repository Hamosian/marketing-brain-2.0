# Nudge protocol - team accountability loop

Loaded by `/chief-of-staff` on every run (Step 5). Defines when a team member gets
nudged about overdue or unanswered work, what the message says, and how the loop
escalates. Designed 2026-09-02 from Nir's ask ("send alerts to team members who are
behind their tasks or didn't respond") plus the anti-nag evidence that more pings
produce *less* completion - the loop is deliberately conservative.

## Mode

```
mode: draft
```

- **`draft`** (current): the run prepares each nudge DM, presents it in the brief's
  Nudges section ready to send, and sends only on Nir's word.
- **`auto`**: the run sends the DMs itself and reports in the brief who was nudged
  about what.

Promotion to `auto` is Nir's explicit call only - propose it after roughly a week of
drafts he approved without corrections, and record the date and his wording here when
he flips it. A false-positive nudge (the person had already answered, or the date was
wrong) drops the mode back to `draft` until the cause is patched.

## Triggers (strict - a nudge fires only on these)

1. **Overdue task**: a ledger row with a **stated** due date (set by Nir or the owner -
   never an agent-inferred date, which the row's notes mark as "inferred" / "ETA set")
   that is 3+ working days past, status open, owner not Nir.
2. **Unanswered ask**: a Slack message or email from Nir with a direct ask to a named
   person, 48h+ old, with no reply and no ✅ reaction - **after** reading the full
   thread (`slack_read_thread`). An answer anywhere in the thread, or a ✅ from the
   person, kills the trigger.
3. **Missing weekly/monthly report**: handled by the Friday chase in the main skill,
   which keeps its own standing send authorization. Log its sends here all the same.

Never nudge: on inferred dates, on `Watch list` or `1-1 notes` rows, on items Nir
parked, on anything already nudged within the cooldown, or anyone outside Riverside
(vendors and partners surface to Nir as "waiting on external" instead).

## Cadence and anti-nag rules

- **One DM per person per day, maximum**, bundling all their triggered items.
- **Cooldown: 2 working days per item.** An item nudged Monday is not mentioned again
  before Thursday even if other items trigger a DM in between.
- **Two strikes then escalate**: after 2 nudges on the same item with no response, stop
  nudging. The item becomes a brief line for Nir: "raise [item] with [person] in your
  1-1." Nag loops train people to ignore the bot; the third touch must be human.
- **Working hours only**, recipient's timezone (Erika is UK; the rest are Israel).
  Sun-Thu for Israel, Mon-Fri for Erika. The 9:00 brief run satisfies this by default.
- **Escape valves in every message**: the recipient can always answer "done", "need
  until [date]", or "blocked because [x]" - each resolves the nudge without doing the
  task. Feed their answer back into the ledger via FEED mode (diff-first).
- **Social, not administrative framing**: name the task and what it unblocks, never a
  count of their open items and never a list of everyone else's misses.

## Message anatomy

Each nudge DM carries: the task (linked to its source), the stated due date, days
overdue or days since the ask, **what it blocks** (one clause - this is what makes the
nudge legitimate), and the escape valves. Warm team tone, light emoji, short. Run
nik-voice → de-ai on the draft. End with `_Posted by the Marketing OS agent_`.

Example shape (draft, not a template to copy verbatim):

> Hey Amir 🙏 the tools-page update was due Sunday and the every-other-day cadence
> went quiet. It's holding up Erika's Thursday status. Done already, need more time,
> or blocked on something? Any of those works, just tell me.
> _Posted by the Marketing OS agent_

## Logging - `data/nudge-log.md`

Every drafted or sent nudge gets a row: date, person, item key (matching
`data/brief-state.md`), trigger, mode (draft/sent/chase), and outcome once known
(replied / resolved / escalated / no response). The log is the cooldown and
two-strike memory - read it before triggering anything. It is also the measure of
the system: on Sundays, if the log shows nudges are mostly ignored or mostly
false positives, say so and propose a rule change instead of nudging harder.
