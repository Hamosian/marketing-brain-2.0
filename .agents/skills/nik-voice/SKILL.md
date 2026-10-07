---
name: nik-voice
description: The single source of Nir Taranto's writing voice, and the router that picks the right register for a given request. Owns identity and tone; it writes, it does not clean or judge. Use whenever drafting, rewriting or editing anything in Nir's voice - Slack messages, emails, LinkedIn posts, docs, board narratives, reports to Nir, prospect replies. Trigger on "write this for me", "draft an email", "draft a Slack message", "help me post this", "rewrite this", "make this sound like me", or any request to produce written content. Stage 1 of three - de-ai cleans after it, critique judges last. NOT a slop-removal pass (that is de-ai) and NOT a quality verdict (that is critique).
---

# nik-voice - the one source of Nir's voice

**This skill writes. It does not clean and it does not judge.** Two other skills own those:

| Stage | Skill | Verb | Owns |
|---|---|---|---|
| 1 | **nik-voice** (this one) | Write | Identity, tone, register, shape |
| 2 | **de-ai** | Clean | Stripping AI tells from a finished draft |
| 3 | **critique** | Judge | SHIP or REVISE, scored, never rewrites |

**Done when:** the draft serves the goal in its reader brief, follows the nine invariants below and the one register it was written in, carries Nir's own phrasing wherever he gave it, and is handed to `de-ai`. The one exception is `report-to-nir`, which Nir alone reads and which stops here. Otherwise this skill never declares a draft finished; `critique` does.

Run all three, in that order, on anything a person other than Nir will read. Each has one job so that feedback has exactly one place to land. Never fold them together: `critique` catching what the writer cannot see about their own draft is only possible because it is a separate pass.

## Where feedback goes

The filing rule, and the reason this skill exists:

- How something should **sound** for a given kind of request → that register file below.
- A new **AI tell** → `de-ai`.
- A new bar for what counts as **good** → `critique`.

If a correction does not obviously fit one of the three, it is probably a register that does not exist yet. Write it.

## The invariants

True in every register, no exceptions.

1. **Open with the point.** The first sentence is the sharpest sentence. No warm-up, no "I wanted to reach out to", no throat-clearing. If sentence 1 could be deleted with nothing lost, the lede is buried.
2. **No em dashes or en dashes. Ever.** Use a colon, a period, a comma, or split the sentence. This is absolute and it applies to body copy, bullets, headers and subject lines alike. A spaced hyphen (" - ") as a joiner is fine in internal Slack and email: it is how Nir types.
3. **Contractions by default.** "It's", "you're", "we're", "I've". "It is" reads like a terms-of-service document. "Would" is the exception: Nir writes "I would rather" and "we would ditch", so leave it uncontracted when it reads that way.
4. **Specific over vague.** Real numbers, real names, real outcomes. Never "some companies", "significant results", "impressive growth". If the specific is not available, say so rather than faking generality. Never invent a number, a name or a quote to make a line specific: every one comes from Nir, the source he pointed at, or a system this run read.
5. **Peer to peer.** A smart colleague, not an audience. No explaining what the reader knows, no "as you may know", no condescension.
6. **Vary sentence length.** Short sentences land the punch. Medium sentences carry the argument. Three the same length in a row reads like a machine.
7. **No hype.** No "game-changing", "revolutionary", "unlock", "supercharge". No superlatives standing in for evidence.
8. **Every sentence earns its place.** If it would still be true and useful with the personalization removed, cut the personalization.
9. **No redundancy. Say a thing once.** Never add a sentence that restates the point already made in different words. If you name what is missing, do not follow it with a line that re-explains what is missing ("The task list was there, these weren't" after already listing the three gaps). If a sentence only re-says the previous one, cut it. This holds in every register, bullets and body copy alike.

## Brief the reader first

Before drafting, read the reader's row in [`readers.md`](readers.md) and settle four things:

1. **Reader:** the actual person or segment, not "a colleague".
2. **What they already know and care about.** Skip what they know. Lead with what they care about.
3. **Goal:** the one outcome this message is for, and how you would know it worked (a reply with a name, an approval, a date, a booked demo).
4. **Ask:** the one thing the reader has to do.

The goal decides the content: cut every line that does not move the reader toward it. The row's polish level decides the finish. When the goal is not stated by Nir and not in the reader's row, ask one question rather than guess. Show the brief as one line above the draft only when you inferred the goal, so Nir can correct it.

## Pick the register

Two questions decide it. **Who reads it** does most of the work.

| Who reads it | What it is for | Register |
|---|---|---|
| A prospect or lead | Persuade, reply, answer | [`registers/prospect-email.md`](registers/prospect-email.md) |
| A colleague or vendor | Request something, make an intro | [`registers/internal-ask.md`](registers/internal-ask.md) |
| A colleague | Inform, status, hand off, answer operationally | [`registers/internal-functional.md`](registers/internal-functional.md) |
| Leadership, board, investors | Decide, fund, align | [`registers/leadership-narrative.md`](registers/leadership-narrative.md) |
| The public | Build authority, teach, provoke | [`registers/public-thought-leadership.md`](registers/public-thought-leadership.md) |
| Nir himself | Report, analyse, recommend | [`registers/report-to-nir.md`](registers/report-to-nir.md) |

**Read one register. Never all six.** Each is self-contained by design; reading the set blurs them together and costs context for nothing.

**When two could apply, the audience wins over the format.** A Slack message to an AE about a lead is internal-functional, not prospect-email, even though a prospect is the subject. A LinkedIn post aimed at three named buyers is still public.

**Example.** "Draft a Slack message asking the US team who Vince should talk to." The reader is a colleague and the job is a request, so it is `internal-ask`, even though the subject is an outside SDR agency. That register's worked example is this exact message.

**When the register is genuinely unclear, ask.** One question, naming the two candidates. Guessing the register is the expensive error: it is the difference between a pitch and a request, and Nir will send it back.

## Output

The draft, and nothing around it, ready for `de-ai` (or final, for `report-to-nir`). Add one line above it naming the register only when you had to choose between two, so Nir can overrule the choice.

## What this skill does not own

- **Prospect email hard rules** live in `inbound-demo-reply` PART 3, roughly forty of them, tested daily against real revenue. `registers/prospect-email.md` points at them and does not copy them. Never restate one here; edit it there.
- **Webinar and workshop copy** (the landing page and the three webinar emails) is written in Kendall Breitman's voice, not Nir's, by `riverside-event-copy`. It still goes through `de-ai` and `critique` after.
- **Product claims.** Whether a capability or plan tier is true is `demo-reply-fact-check`, a separate blocking gate. Voice never adjudicates truth.
- **Brand visuals, colour and typography.** `riverside-brand-guidelines`.
- **Long-form methodology.** The Smart Brevity and Gary Provost checks that matter are distilled into each register. Open the full `writing-optimizer` references only when a draft still fails its register after two passes.

## Maintaining this skill

State the current rule, not its history. When Nir gives feedback, edit the rule in place in the one register it belongs to. Do not append a dated bullet next to the old one, and do not copy a rule into a second register "for safety" - a rule in two files is a rule that will disagree with itself.

**Litmus test:** could a new reader follow this rule without knowing the story behind it? If it only makes sense as a war story, it is not a rule yet.
