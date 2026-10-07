# Register: internal functional

Informing a colleague. A status update, a task summary, a data answer, an ops message, a handoff, a how-to. Clarity beats warmth, and there is nothing to persuade.

**This register delegates. Apply the `ste` skill** and write it in Simplified Technical English: main point first, short sentences, one idea each, active voice, no hype adjectives, no filler.

**Then keep going: `de-ai`, then `critique`, same as any other register (per Nir, 2026-09-07).** `ste` replaces the *writing* stage here, not the pipeline. A colleague is another person, and a functional message reads like a machine wrote it just as easily as a landing page does, so it earns the cleaning pass and the verdict. The only thing that skips stages 2 and 3 is output Nir alone reads, which is `report-to-nir.md`. The earlier version of this line claimed a status update "is not prose" and could not carry AI tells; it can.

## What this register adds on top of `ste`

- **The invariants in `SKILL.md` still hold.** No em dashes, contractions, open with the point, specific over vague.
- **Slack brevity: the channel gets the answer, the DM gets the depth.** A channel or thread reply leads with the answer, about five short lines, then stops. No headers, no tables, no evidence appendix, no narrating your own process. If the full answer needs more room, post the short version in-thread with one pointer line and DM the long version to the person who asked. Full convention in `CLAUDE.md`.
- **The link is the detail.** For a ticket, PR or doc, post one line and the link. Never its field values.
- **In a thread, always reply in-thread** (`thread_ts`).
- **Do not shrink a scheduled report.** The brevity rule governs conversational replies. It does not apply to `/chief-of-staff`, `/nir-mql-live-report`, `/mops-standup` or `/invoice-inbox-to-monday` artifacts.

## Handing work to a colleague

- Name the owner and the deadline. "Can you check this?" not "this needs to be checked."
- Say what happens if they do nothing.
- One ask per message. Two asks means two messages, or one message and a numbered list of exactly two items.

## When this is the wrong register

- You are **requesting** something rather than informing → `internal-ask.md`. The tell is a question mark in the last line.
- You are writing to **leadership to get a decision** → `leadership-narrative.md`.
- The reader is **Nir** → `report-to-nir.md`.
