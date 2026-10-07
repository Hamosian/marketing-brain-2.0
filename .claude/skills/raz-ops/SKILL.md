---
name: raz-ops
description: Use this skill when Raz Navon wants to see or change the state of his own cloud routines (scheduled triggers), monday.com tasks, or standing personal preferences - and have the requested change actually carried out, not just noted. Also holds his running "remember this for later" ledger, e.g. notes to fold into his own weekly Paid-Acquisition writeup, recalled back to him whenever he asks. Takes a freeform instruction ("move my Tuesday invoice pulse to Friday", "remember I don't want Slack pings after 6pm", "add a task to review X", "remember to add X to my writeup", "what have I asked you to remember this week"), classifies which system it maps to, and executes it after confirmation. Personal to Raz only, not department-wide. Triggered by "raz ops", "manage my routines", "check my routines", "update my routine", "remember that...", "what do I need to add to the report", "stop doing X", or "/raz-ops".
---

# Raz Ops

Raz Navon's personal orchestration layer over his own cloud routines and monday tasks. He tells it what to remember or change; it maps that instruction to a real system and makes the change - never just a note that nothing acts on.

## Inputs and context to load
- Always start from CLAUDE.md.
- `references/team.md` to confirm Raz's identity if a task lookup needs it.
- `references/monday_boards.md` for board/column IDs when touching monday.
- This skill is scoped to raz.navon@riverside.fm. Do not manage another person's routines or tasks under this skill - route those to `/chief-of-staff`, `/mops-standup`, or the owning person's own workflow instead.
- **Routine visibility boundary - two distinct causes for an empty `list_triggers`.** Both are common; do not assume a routine doesn't exist just because the tool returns nothing - ask where it lives first.
  1. **Local routine.** Raz's local Claude Code desktop app has its own "Routines" list (labeled "Local routines only run while your computer is awake and online"). These are stored on his machine, not in Claude's cloud trigger system, and are **invisible to every MCP tool in every session** - `list_triggers` explicitly excludes them. There is no remote way to read or edit one; Raz must open it in the local app himself.
  2. **Cloud routine on a different account.** `list_triggers` only returns routines owned by *this calling account* (the shared repo session). A cloud routine Raz registered under his own personal claude.ai login is a real `trig_...` object, just not one this session's account can see or edit - the same boundary documented for `/inbound-demo-reply`'s routine, which lives in Nir's own account.
  - Either way, this skill cannot mutate the routine directly. Say so plainly, and offer: (a) Raz edits it himself (locally, or at claude.ai/code/routines), or (b) he pastes its current prompt here and this skill drafts the updated wording for him to paste back in.

## Steps
1. **Show current state.**
   - Cloud routines: call `list_triggers` (claude-code-remote MCP). These are already scoped to the calling account, so no extra filter is needed.
   - Monday tasks: use `monday-agent` to pull open items on the Marketing Operations Tasks board (`6257866754`, unless the user names another board) where Raz Navon (monday user ID `97365904`) is the **Owner** (`person`) or the POC - and the POC is **two** columns on this board, both titled `POC`: `dup__of_assignee` (the one to **write**) and `peopleeozmsvcu`. **Read both.** Confirmed live 2026-08-18: Raz had zero items as Owner but 19 under `peopleeozmsvcu`; re-confirmed 2026-09-02 that both columns still carry live data, so querying either one alone under-reports. Do not report "no open items" off the Owner column alone, and never write `peopleeozmsvcu` (see `references/monday_boards.md`). Exclude `Done` status; treat `Cancelled` as closed too even though its `is_done` flag is technically `no` (see `references/monday_boards.md`'s status label table) - it is finished work, not open work.
   - Present both as a short current-state summary before asking what to change.
2. **Take the instruction.** The user gives a freeform ask - a schedule change, a task edit, a new reminder, an ad hoc "just do this now" request, or a standing preference.
3. **Classify it** into exactly one of:
   - **Cloud routine change** - edit an existing routine's schedule/prompt/enabled state, create a new one, or fire one now. Use `update_trigger` / `create_trigger` / `delete_trigger` / `fire_trigger`.
   - **Monday task change** - a brand-new task always goes through `/pm-story` (it writes the Why/What/Done When; never create monday items directly). An update to an existing item's status/owner/date goes through `monday-agent`.
   - **Ad hoc action** - a one-off "do this now" (e.g. "send X to Slack", "pull me a quick number") - hand off to the relevant skill-agent (`slack-agent`, `data-agent`, etc.) or `/marketing-brain` if it's broad.
   - **Report content reminder** - "remember to add X to this week's report" (or similar). Raz's weekly report is a routine his local Claude Code app or personal claude.ai account runs (see the routine visibility boundary above) - this skill cannot write into it directly. Instead, append a row to `data/weekly-report-notes.md`'s Pending table (`Note`, `Added` = today) and confirm it's logged. See "Report content recall" below for how Raz gets these back.
   - **Report content recall** - "what do I need to add to this week's report", "remind me what I've added this week" (or similar - this is a read, not a write). Read `data/weekly-report-notes.md`'s Pending table and list every row back to him. See "Report content recall" below for the full behavior.
   - **Standing preference with no live system to hold it** - e.g. "don't message me on weekends" - save to Claude Memory (an individual preference, per CLAUDE.md's memory rule), not to the repo.
   - If the instruction is genuinely ambiguous between two of these, ask which one before acting - never guess on a mutating action.
4. **Show the exact change and confirm** before making it (see Constraints).
5. **Execute**, then report back plainly what changed (before -> after), or that the preference is now saved.

## Report content recall (on-demand, not a routine)

Raz asks for this himself (e.g. Thursday morning, before he writes his weekly
report) rather than this skill pushing it to him on a schedule - there is no
cloud routine here. This replaced an earlier Slack-digest design once Raz said
he'd rather just ask when he wants it; see `references/change-control.md`
("A session with no passable connector grants creates a routine with none")
for why a Slack-push version built from this session wouldn't have worked
anyway, in case a future request revives that direction.

1. **Load state.** Read `data/weekly-report-notes.md`.
2. **If Pending is empty:** say so plainly ("nothing logged for this week's report yet") - don't fabricate items.
3. **If Pending has rows:** list them back to Raz in chat, plainly - this is a reminder for him to fold into his own report, not the report itself.
4. **Move recalled rows to Sent**, filling `Sent` with today's date, and commit:
   ```bash
   git add .claude/skills/raz-ops/data/weekly-report-notes.md
   git commit -m "raz-ops: report notes recalled"
   git push
   ```
   Never delete a Sent row - it is the week-over-week record, same as the
   team-task-registry ledgers. If Raz is just checking in mid-week ("what's in
   there so far") rather than doing his actual pre-report recall, ask before
   moving rows to Sent - moving them prematurely could drop an item off his
   radar before he's actually written it up.

## Constraints
- **Confirm before every mutation.** Show the before/after state of the routine, task, or item and get an explicit yes before calling `update_trigger`, `create_trigger`, `delete_trigger`, `fire_trigger`, or any monday write. No silent changes.
- **Scope guard.** Only act on routines this account owns and monday items where Raz is the owner. If asked to change something outside that scope, say so and point to the skill that owns it instead of acting.
- **Task creation always goes through `/pm-story`.** Never call monday item-creation tools directly for a new task.
- **Cron is UTC.** When changing a routine's schedule, convert the requested local time to UTC before calling `update_trigger`/`create_trigger` (see `references/change-control.md` on cron/DST drift).
- **Memory is for Raz's personal preferences only** - never save team or system knowledge here; that still goes to the repo per CLAUDE.md's knowledge-routing table.
- If `list_triggers` or the monday pull returns empty, say so plainly ("no routines found" / "no open tasks found") rather than treating it as an error - and if the user pushes back that a routine should exist, check the visibility boundary above before concluding anything.

## Output schema
## Current State
- Routines: ... (or "No routines found")
- Open tasks: ... (or "No open tasks found")

## Proposed Change
- What: ...
- Before -> After: ...
- Awaiting confirmation.

## Result
- What actually changed, or "Saved to memory as a standing preference."

## Done when
The requested change has been made and confirmed back to Raz (or the preference is saved to memory), and the current-state summary reflects it.
