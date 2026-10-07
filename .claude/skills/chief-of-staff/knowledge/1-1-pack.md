# 1-1 packs - what a lead gets before a 1-1 with Nir

Loaded by `/chief-of-staff` on every run (Step 7). A pack is the list of action
items Nir and a lead will work through in their 1-1 today, sent to the lead before
the meeting so both sides arrive prepared. Nir asked for it on 2026-09-14: "if I
have a 1-1 with someone on that day I want to send them the action items that we
have, take from last week and everything open, suggest it to me and I'll remove the
redundancy and you'll learn what's important after a few times."

The pack starts **wide and gets narrow by feedback**. The first packs will be too
long on purpose. Every cut Nir makes is logged, and after two cuts of the same kind
for the same lead it becomes a rule in that lead's section below. The skill is
allowed to be wrong early; it is not allowed to be wrong the same way twice.

## Who gets a pack

| Lead | Function | Slack ID | Ledger |
|------|----------|----------|--------|
| Erika Varangouli | SEO & AI Search | `U06R47T4ASJ` | `.claude/skills/growth-marketing-team-tasks/data/seo.md` |
| Raz Navon | Paid Acquisition | `U0A31DAME0G` | `.claude/skills/growth-marketing-team-tasks/data/paid.md` |
| Savion Ron Shemesh | Creator + Growth Channels | `U09340B5HCM` | `.claude/skills/growth-marketing-team-tasks/data/creator.md` + `.claude/skills/growth-marketing-team-tasks/data/growth-channels.md` |
| Hanan Amos | Marketing Operations | `U0A3HCFE90S` | `.claude/skills/growth-marketing-team-tasks/data/mops.md` |
| Abel Grünfeld | Nir's manager | `U01B8LQS944` | none; see the Abel section |

Peers and cross-team syncs (Sivan, Yaniv, Ariella, Michal, Raz Messing, vendor
syncs) get **no pack**. Nir's call, 2026-09-14. A direct report Nir shares a group
meeting with today (Hanan in a sync, say) gets a list too when he asks, and Hanan
gets one by default (see his section).

## Detecting a 1-1 on the calendar

Run on today's events from Step 1.D. An event is a 1-1 with a lead when **either**:

1. **Attendees**, after dropping rooms (`c_...@resource.calendar.google.com`) and
   Nir himself, are exactly one person and that person is in the table above.
   This is the primary test. It is what separates "Raz / Nir" with `raz.messing`
   (Brand, no pack) from "Nir / Raz Weekly" with `raz.navon` (Paid, pack).
2. **Title** matches `<first name> / Nir` or `Nir / <first name>` in either order
   with any suffix (`- Weekly`, `-KPI`, `Report overview`), and the attendee list
   is missing or unreadable.

A lead with two sessions today (Savion often has a weekly and a KPI session) gets
**one pack**, sent before the earlier session, covering both. A session that is
clearly single-topic by title ("Report overview Raz / Nir") still gets the full
pack; the title topic goes first.

If the calendar is not reachable, say so once and skip packs. Never guess a 1-1
from the day of the week.

## What goes in (wide by default)

Build from these sources, in this order. Cite nothing to the lead; the pack is a
list of asks, not a dossier.

1. **Open items they owe.** Every row on their ledger with status `Open`,
   `In work`, `Need review` or `1-1 notes`, owner them or their team. Include
   rows past a stated date and rows with no date. Exclude `Done` and `Watch list`.
2. **Last 1-1's agreed actions and where they stand.** Granola: the most recent
   meeting with the same title or the same two attendees. Pull its action items
   and mark each closed or open by checking the ledger, Slack and Gmail. Closed
   ones get one line at the top ("Closed since last time: X, Y"); open ones merge
   into the items above.
3. **Unanswered asks from Nir to them.** Slack messages and emails from Nir with
   a question or request, no reply and no ✅ after 48h, thread-checked (same test
   as the nudge protocol). Two-strike escalations from `data/nudge-log.md` land
   here by design: the pack is the "raise it in your 1-1" the protocol promises.
4. **Items Nir owes them.** Their asks to Nir that he has not answered, from the
   involvement search and the Gmail waiting-on-Nir pass, plus `data/brief-state.md`
   rows where the actor is Nir and the lead is the one waiting. Rendered as a
   separate short block, "On me", so the pack is two-sided.
5. **Their report headline, if filed this period.** One line from
   `data/weekly-report-digest.md`: the headline metric against target and the one
   behind-target KPI. Skip when nothing is filed; never chase inside the pack.
6. **Cross-team items that involve them.** Watch-lane rows in `data/brief-state.md`
   where they are a named actor alongside someone else (a vendor thread, a Data
   Team dependency). One line each.

Then apply `knowledge/1-1-agenda-style.md` to the result, in full. The rules that
bite hardest: asks not descriptions, Nir's priority order not the board's, no
board metadata, consolidate hard, positive tone, check who owns each item.
Consolidation is where "wide" becomes readable: five blog rows are one Blog item.
The pack can be long in items covered and still short in lines.

## The opening line (Nir, 2026-09-14)

Every pack opens by saying why it is being sent and that the list is shared: "I'm
sending the list of open items on our side, so we're both on top of things and
nothing slips between us. Add anything you want to cover, it's your list as much as
mine." Then the tone line for that lead. The list is a shared working surface, not
a checklist handed down.

## Rendering in chat (the approval step)

Packs are approved **in this chat**, never by Slack reply (Nir, 2026-09-14). Show
each pack as the **exact message that will be sent**, so his OK on the list is an
OK on the wording. Number every item so he can cut by number.

```text
### 1-1 pack: Erika, 15:30

Hey Erika 👋 for our 1-1 today, here is what I have open on our side:

1. **Weekly report.** Restart the weekly for SEO from this Sunday, or tell me if
   you want it folded into the monthly.
2. **DE targets.** Bring the numbers for Q3 planning; we set these in August.
3. **Joto retro.** Date for the retro and the Abel slot.
...

On me: the /register free-plan copy (I owe you an answer), the tools direction.

Cut or add anything before 15:00 and I will bring it. See you at 15:30.

Closed since last time: SEO invoicing (paid 8 Sept), tools status confirmed.
Say "Erika: drop 2, 4, send" or "Erika: send". Nothing goes out until you do.
```

Rules for the render:

- **One block per lead**, in meeting-time order, after the action table and
  before "Changed since yesterday". A day with no 1-1 has no section.
- **Run the message through nik-voice (internal-ask register) → de-ai → critique**
  before showing it. The lead reads it, so it is outward-facing. The chat framing
  around it (the "Say ..." line, the closed-since line) is for Nir and stays plain.
- **The "On me" block is inside the message.** The lead should see what Nir owes
  them; it is what makes the pack fair instead of a checklist for them alone.
- **Never send on the same turn you render.** Nir edits first. His reply forms:
  - `Erika: send` sends as shown.
  - `Erika: drop 2, 4, send` removes those items, renumbers, sends. No second
    approval, because he saw the exact text of every surviving item.
  - `Erika: add <text>` appends his item verbatim (his bullets are talking points;
    do not expand them), then show the final once more and wait.
  - `Erika: hold` keeps the draft for the day, sends nothing.
  - Any other edit to wording: apply, show the final once more, wait for `send`.
- **Send** as a Slack DM to the lead, thread-less, with the
  `_Posted by the Marketing OS agent_` footer. If Nir says "as me", drop the
  footer (standing rule in `CLAUDE.md`). Never DM before a stated OK.
- **Timing.** Aim to have the pack approved at least an hour before the meeting.
  If the run starts inside that hour, still show it and say so; Nir decides.

## Scheduled run (no chat available)

The 9:00 scheduled run cannot get chat approval. It **drafts** each pack to
`data/1-1-packs/YYYY-MM-DD-<lead-slug>.md` (the exact message text plus a
`sources` footer listing the ledger rows and permalinks it drew on), and posts one
line per pack in the Slack brief: "1-1 pack drafted for Erika (15:30). Open the
chat and say `packs` to review and send." It sends nothing.

In chat, `/chief-of-staff packs` (or any message mentioning today's packs) loads
today's drafts. A draft older than three hours, or whose sources have changed
(a ledger row closed, an ask answered), is rebuilt before showing. Then the
approval step above runs as normal.

## Abel is different

Abel's pack follows `references/executives.md` and the standing memory rule:
**a numbered list of topic titles, no rationale, no sub-bullets**, sent to his
Slack DM, **never logged on any ledger or board**. Content, in order: decisions
Nir needs from him; things Nir is reporting upward this week (a bottleneck line,
a shipped result, a cadence change); open items from the last Abel 1-1 (Granola).
Suggestions for additions go in chat as one-word titles, not inside the list.
Nir approves the topic list in chat the same way (`Abel: drop 3, send`).

## Learning: `data/1-1-pack-log.md`

One row per pack shown. Columns: date, lead, meeting time, items proposed (short
keys), items cut, items added, sent (yes / no / as-me), and a note.

After Nir's reply, before sending, **classify each cut with one question when it
is ambiguous**: "Cut 2 and 4: done, or not 1-1 material?" The answer routes
differently. *Done* → close the ledger row through FEED mode (diff-first) and the
pack learned nothing. *Not 1-1 material* → the cut is a preference signal and is
logged as such. Do not ask when the reason is obvious (the item is Nir's own, or
the lead already answered in Slack this morning); log the inferred reason and mark
it inferred.

Promotion to a rule, per lead:

- **Two cuts of the same kind** (same item type, same reason) → add a line to that
  lead's section below under "Leave out". Cite both dates.
- **One add** by Nir → a "Bring in" candidate for that lead; a second add of the
  same kind confirms it.
- **A cut Nir explains** ("never put report numbers in Erika's pack") → a rule
  immediately, cited.
- A rule that produces a wrong pack twice gets removed with a note, not patched.

The Sunday brief's Sharpen section may read this log for its "what should be a
skill" question, but the daily loop lives here.

## Per-lead rules (learned; empty until earned)

Each section grows from the log. Do not pre-fill from assumptions.

### Erika
- 2026-09-14: first pack held ("don't send to Erika", no reason). One data point. If it happens again, ask whether her own Thursday status makes the pack redundant.
- Bring in: -
- Leave out: the weekly-vs-monthly cadence question (Nir, 2026-09-14).
- Phrasing: UK-based; her working days are Mon-Fri, so a Sunday pack goes out Monday morning if the 1-1 is Monday.

### Raz Navon
- **Style (Nir, 2026-09-14): very clear and simple, personal, one plain question at the end of each item.** **Never pushy or clipped.** "Where is it?" was rejected. The shape for anything in progress is: one line of context (what it is, why it matters), then "do we have X yet, and what's the ETA?". Every item carries enough context that Raz does not have to guess what Nir means (the webinar sign-ups event needed explaining; SaaSworthy needed the invoice and the budget ask spelled out). He is sensitive to AI-sounding text, so short sentences, no framing, no dashboard vocabulary, nothing that reads like a report. Make each item easy to answer in one line.
- **Scan Jarred's board** (Jarred Berman, Raz's report; monday board `18426843451`) before every Raz pack: items past their date or pushed more than once become one consolidated item. Nir, 2026-09-14.
- Bring in: DesignRush and SaaSworthy (paid listings money), LinkedIn thought-leadership ads strategy plan, the newsletter campaign update, the B2B watch-a-demo video brief, what Jarred learned at events he attends, and a quarterly CRO plan ask (Nir, 2026-09-14). Performance questions (YouTube after August's decline) are asked of Raz, never answered from stale numbers.
- Leave out (one cut each, 2026-09-14, not yet rules): PLG upsell email ("not relevant to him"), Intercom status.
- Leave out: design items. "Raz" in an SEO or website thread (tools design 4-to-2, with Sydney) is **Raz Messing**, Brand. Always check which Raz before filing an item here. Nir, 2026-09-14: "why is it here? it's not related to Raz".

### Savion
- Bring in: Ofra Toubiana's onboarding (joined 2026-09-06) and the quarter's KPIs, as a monthly-report item (Nir, 2026-09-14).
- Leave out: the weekly-vs-monthly cadence question (Nir, 2026-09-14: not pack material).
- Phrasing: one pack covers both her functions (Creator and Growth Channels) and both sessions on a two-session day.

### Hanan
- Build a list on any day Nir shares a meeting with him, 1-1 or not (Nir, 2026-09-14). Shown in chat; sent only on his word.
- Bring in: -
- Leave out: -

### Abel
- Bring in: -
- Leave out: -
- Phrasing: titles only, numbered, no sub-bullets (standing rule since 2026-08-02).
