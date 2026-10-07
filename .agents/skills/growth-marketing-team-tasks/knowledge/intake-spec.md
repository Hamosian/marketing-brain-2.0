# Intake spec - FEED mode

How `/growth-marketing-team-tasks` turns free-form input (a doc, pasted text, or
Slack messages) into normalized tasks and merges them into a team's ledger. The
standard task format and the ledger file layout are defined in
`references/team-task-registry.md` - this file covers extraction, merge, and the
confirmation gate.

## 1. Identify the team

Match the request to exactly one `feed` team (My tasks, SEO, Paid, Creator,
Growth Channels, SDR). If the user names a `board` team (MOPs), stop and say its
tasks live on Monday and are read live in SHOW mode, not fed. If no team is
clear, ask with one `AskUserQuestion`.

## 2. Ingest the input

Accept, in order of preference for what the user gives you:
- **Pasted text** - use it directly.
- **Google Doc / Sheet link** - read it (Drive tools). Only the one they named.
- **Slack messages / permalinks / a channel-and-range** - read them (Slack
  tools). Only what they named. Do not go hunting for a team's tasks across the
  workspace on your own.

Record where each task came from for the `Source` field: a doc URL, a Slack
permalink, or `pasted <today>` for pasted text.

## Ambiguity: find the context, or ask

Nir writes tasks tersely. Before logging one, resolve it against context - the
`references/team-context/` digests, existing ledger rows, `references/team.md`,
recent tasks, and memory - and expand it into something a reader could act on.
Name the people, tools, and vendors it refers to (e.g. resolve "PT" → PartnerStack,
"SERPD" → SERP Domination). **If confidence is low after that, do not guess -
ask Nir what he means** (one tight `AskUserQuestion` with your best-guess options),
then log it. Getting a shorthand wrong is worse than a quick clarifying question.

## 1-1 dating from the calendar

When Nir says "list things for my 1-1 with [person]" (or "for my next 1-1 with
X"), add the items to that person's ledger and set each task's **ETA to the date
of that 1-1**. Get the date from **Google Calendar** (if the connector is
authorized as Nir): find his next event that is the 1-1 with that person and use
its date. If the calendar connector is not available, do not guess the date -
ask Nir for it (or use a recurring 1-1 slot he has given). Owner still defaults to
the team lead unless Nir names someone; tag the source as "1-1 <date>".

**How to spot a 1-1 in the calendar (Nir's convention):** an event titled with
Nir's name and another person plus "weekly" is their recurring 1-1 - e.g.
"Nir / Abel - Weekly" is the Nir↔Abel 1-1, "Nir / Dor - Weekly" is the Nir↔Dor
1-1. Match `Nir / <person>` (either order) + "weekly" to find the right event,
then use its next occurrence's date.

## 📌 pin-drop tasks (auto-open on the daily run)

Nir **types** 📌 in a Slack message to flag it as one of his own to-dos. The
`/chief-of-staff` daily run scans his posted 📌 messages from the last ~24h and, per
his standing instruction (2026-07-25), **opens each one automatically** in his
ledger - this is the one place a feed writes without the confirm-first gate, and it
is narrow by design:

> **Typed, not reacted.** The scan is a text search, so a 📌 *reaction* on someone
> else's message is not picked up (`hasmy::pushpin:` returns nothing on this
> workspace, and it is unproven whether that means no such reactions exist or the
> modifier is unsupported - do not claim either way). For things Nir flags with
> Slack's own **Later** bookmark rather than a typed pin, see the
> `/chief-of-staff` "Slack Later / saved-items scan": those are readable via
> `is:saved` and are **surfaced for triage, never auto-opened**, because that list
> mixes real asks with reference links.

- **Team / owner:** always **My tasks** (`data/my-tasks.md`), owner `Nir`.
- **Priority:** always **P0**.
- **Due:** **this week** - the current work week's Thursday (the Sun-Thu week's
  end); on Fri/Sat use the upcoming Thursday. Same "This week" the dashboard uses.
- **Status:** `Open`. **Source:** the pin's Slack permalink. **Added/Updated:** today.
- **Title:** a clear imperative pulled from the pinned message (expand terse
  shorthand against context per the ambiguity rule above).
- **Dedupe across runs** by the source permalink and by task meaning, so the same
  pin is never opened twice; a pin already in the ledger is skipped.

The auto-write exception applies **only** to this path (📌 → My tasks, these exact
defaults). A 📌 aimed at another team, or any other free-form input, follows the
normal extract → diff → confirm flow. The daily run reports every auto-opened task
in the brief so Nir can adjust or close it with a normal feed. If a 📌 task needs
different fields (a later due date, a downgrade from P0, a different owner), Nir
changes it in a subsequent feed - the auto-open just guarantees it lands as an
open P0 for the week the moment he pins it.

## Pinging an owner (📨)

When Nir asks to ping/nudge an owner about a task (via the dashboard's "Ping owner"
queue or in chat), **rewrite his terse note into a clear, self-contained Slack DM
with more context than he gave** - state what needs doing, why it matters, the
specific ask, any relevant background from `references/team-context/`, and the ETA
if set. Keep the team Slack tone (warm, a light emoji) and end with the
`_Posted by the Marketing OS agent_` footer. **Show Nir the drafted message and
send only after he confirms** (sending on his behalf is a mutation). Send via
`/slack-agent` or the Slack DM tool to the owner's Slack ID from `references/team.md`.
**Group multiple pings to the same owner into a single DM** (one message covering
all their queued tasks), not one message per task.

## 3. Extract action items

Pull discrete, actionable items. For each, fill the standard fields:

- **Task** - a short imperative line ("Ship the Q3 cluster brief"), not a
  paragraph. Split a compound sentence into separate tasks.
- **Owner** - the person named; if the input names no owner, default to the team
  lead from the registry. Never guess a specific different person.
- **Status** - infer conservatively, and only from the six values the dashboard
  actually offers (`Open`, `In work`, `Need review`, `1-1 notes`, `Watch list`,
  `Done`). `scripts/validate_tasks.py` rejects anything else, so do not invent a
  label: explicit "done/shipped/closed" → `Done`; "working on / in progress /
  underway" → **`In work`**; "done but keep an eye on it / watching / monitoring
  the result" → **`Watch list`**; "needs my review / waiting on my read" →
  `Need review`; agenda material for a specific 1-1 → `1-1 notes`; everything else
  actionable → `Open`. **"Blocked" is not a status** - mark a blocker with priority
  `CNF` and leave the status as whatever the work actually is.
  (Corrected 2026-08-04: this rule previously said `In progress` and `Blocked`,
  neither of which exists in the vocabulary.)
- **Priority** - only if the input states it (`P0`-`P4`, or a blocker → `CNF`).
  Otherwise `-`. Do not assign priority from tone.
- **Due (ETA)** - the task's ETA / target completion date, normalized to
  `YYYY-MM-DD` (resolve "Friday", "next week", "EOM" against today's date). This
  is the field the dashboard shows as "ETA", so capture one for every
  manually-added task; use `-` only if the input gives no date and none is
  implied.

Do not invent tasks, owners, priorities, or dates the input does not support.
Ambiguous fragments that are not clearly action items are dropped, not guessed
into tasks - if unsure whether something is a task, list it separately and ask.

## 4. Merge into the ledger

Load `data/<slug>.md`. For each extracted task, decide against existing rows:

- **New** - no existing row matches (by task meaning + owner). Add a row;
  `Added` = `Updated` = today.
- **Update** - an existing open row clearly matches but a field changed (status
  advanced, due set/moved, priority set). Update those fields; set `Updated` =
  today; keep the original `Added`.
- **Unchanged** - a match with no field change. Leave the row and its dates as-is.
- **Newly done** - the input says an existing open task is finished. Set
  `Status = Done`, `Updated = today`. **Keep the row** (never delete it).

Match on meaning, not exact string - "finish SEO brief" and "complete the SEO
cluster brief" are the same task. When a match is genuinely uncertain, treat it
as New and flag the possible duplicate in the diff for the user to resolve rather
than silently merging. Never delete `Done` rows; git history is the over-time
record. An open ledger task the new input does not mention is carried forward
unchanged - absence from one feed does not mean it is done.

## 5. Confirm, then write

Show a diff before writing anything:

```text
Feed → SEO (Erika) · source: pasted 2026-07-18

New (2)
  + Ship the Q3 cluster brief - Erika - In progress - P1 - due 2026-07-25
  + Fix llms.txt on 3 locale subfolders - Erika - Open - CNF - due -
Updated (1)
  ~ Migration ETA to product - Open → In progress, due set 2026-07-22
Newly done (1)
  ✓ AI Overviews audit - marked Done
Unchanged: 6 · Carried forward: 6
```

Get an explicit yes, then write `data/<slug>.md`. If the user says no, adjust and
re-show. If nothing changed, say so and write nothing. Writing the ledger is the
only mutation this skill performs; it never writes to Monday.

## Answering a task (Q&A / decision tasks)

Nir often logs a task as a question ("Profound: is this the right bet?") and later
gets the owner's answer. An answer reaches the ledger two ways: (a) Nir pastes it
in chat ("here's Erika's answer to X" / "log her reply on the mentions task"), or
(b) he types it into a task's **💬 Answer / comment** field on the dashboard and it
comes back in "Copy my changes" as an `answer/comment: "…"` line. Either way, find
the matching open row, fill its **`Answer`** column, and - if he says so, or the
answer clearly resolves the question - set `Status = Done` in the same step.
`Updated = today`; keep the row.

- Store the answer as short prose in the `Answer` cell; use `<br>` to separate
  points, and attribute it (e.g. `_(Erika, 2026-07-22)_`) so the source is clear.
- If the ledger has no `Answer` column yet, add it as the trailing column (default
  `-` on the other rows) per `references/team-task-registry.md`.
- The dashboard shows a "💬 Answer" toggle on any row whose `Answer` is non-empty;
  no other change is needed for it to appear on the next SHOW render.

Show the diff (answer text + any status change) and write only on confirmation,
like any other feed.

## Focus order (drag-reorder from the dashboard)

The dashboard's Today / This week band lets Nir drag-rank his work. A reorder
arrives as a **`Focus order (save to data/focus-order.md)`** block in "Copy my
changes" or the sync panel, listing ordered task ids per section. Handling:

- Rewrite the `## Today` and `## This week` id lists in `data/focus-order.md`
  to match the block exactly (ids only - strip the parenthesized title hints).
- This is a ranking, not a task change: no ledger row is touched by the order
  itself. A cross-section drag also arrives as a normal `ETA=` change line on
  the task - apply that to the ledger as usual.
- Confirm before writing, like any other feed. If an id in the block no longer
  exists in any ledger, drop it silently (membership is recomputed at render).

## To-read queue (reading-list.md)

The dashboard's 📚 To-read section is Nir's reading queue, stored in
`data/reading-list.md` - reading material, a separate object type from tasks (see
`knowledge/dashboard-spec.md`, To-read queue). Changes arrive in "Copy my changes"
as blocks naming `data/reading-list.md`:

- **`New reading items`** - append rows to `data/reading-list.md` (`Status = unread`,
  next free `read-N` id, `Source = manual`). Dedupe by URL.
- **`Reading marked read`** - set that row's `Status = read`. Keep the row.
- **`Reading items removed`** - drop that row.
- A new-task line tagged **`(from a reading item - also mark it read)`** means the
  "→ make task" button: add the task to the right ledger *and* set the matching
  reading row to `read`.
- A new-reading line tagged **`(Read later: also remove the matching task row from
  its ledger)`** means the reverse - the task's "📚 → Read later" move: add the
  reading row to `data/reading-list.md` *and* delete the matching task row from its team
  ledger (match by title).

Confirm before writing, like any feed. No-owner article captures now land here
(not as P0 My-tasks rows) - see the chief-of-staff SKILL and `.claude/skills/chief-of-staff/data/article-index.md`.

## Marking a task done (quick-complete)

"Mark [task] done", "close [task]", or "[task] shipped" is a minimal feed: find
the matching open row in the team's ledger, set `Status = Done` and
`Updated = today`, keep the row, show the one-line change, and write on
confirmation. The published dashboard is read-only HTML - a checkbox click there
does **not** persist - so completion always flows through this ledger update, and
the dashboard reflects it on the next SHOW render. A true click-to-check
dashboard that writes back requires a hosted app with a backend (the later
visualization phase), which a static Artifact cannot provide.
