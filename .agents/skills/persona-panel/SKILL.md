---
name: persona-panel
description: Runs a draft launch, announcement, web or ad copy, pricing or packaging email, or campaign concept past a panel of Riverside customer personas (podcasters, marketers, producers and agencies, founders, IT buyers, at-risk users) built from real customer voice (VoC research, the demo-form pain map, win-loss reasons, Gong, material the user supplies). Interviews each persona and returns how they read it, what lands, who misreads it, the objection, their next move, and who will push back hardest. A pre-launch structured brainstorm, not evidence. Triggered by "persona panel", "run this past customers", "how would customers react", "audience reaction check", "test this message on personas", "who would push back on this", "pre-launch reaction check", or "/persona-panel". NOT an expert-lens direction debate (marketing-council), NOT a competitor sameness check (are-we-really-different), NOT a verdict on finished writing (critique), NOT a jobs-pains-gains profile (value-proposition-canvas).
user-invocable: true
---

# Persona Panel

Seat a small panel of Riverside customer personas, show them the thing that is
about to ship, and interview each one. The value is hearing *which* segment
reads it wrong, and why, before a real customer does. A panel that loves
everything is a mirror.

The idea comes from multi-agent social simulators such as MiroFish: build
personas from source material, then interview them one by one. We keep the
useful part and drop the infrastructure. Personas come from our own
voice-of-customer evidence rather than from names in a brief, nothing is
self-hosted, and no data leaves for a third-party memory store.

**This is simulation, not research.** Every reaction is inferred from the
evidence behind a persona. It tells you where to look, not what customers
think. Label it as such.

## Where this sits

| The request is... | Goes to |
|-------------------|---------|
| **How would our customers react** to this message, launch, price change or concept | this skill |
| Which **direction** to take, argued from expert lenses (Godin, Sharp, Dunford) | `/marketing-council` |
| Do we **sound like competitors** | `/are-we-really-different` |
| Is this **finished draft good** enough to ship | `/critique` |
| **Who is the customer**: ranked jobs, pains, gains | `/value-proposition-canvas` |
| Why did a **number** move | `/marketing-brain` |

The panel reacts. It never rewrites the copy and never picks the direction.

## Inputs and context to load

- `CLAUDE.md`, then `knowledge/roster.md` (the standing personas, their
  evidence, and the seating guide).
- `references/evidence-standards.md` before any figure appears in the output.
- Only the source files the seated personas cite. Open them only to check a
  claim; the roster already carries the distilled evidence.
- Live refresh sources are optional per run (Step 3).

## Step 1: Frame the test

Ask through `AskUserQuestion` only for what is missing:

1. **The stimulus.** The actual draft, link, or concept. If only an idea is
   given, run at concept level and say so in the output.
2. **What it is.** `Launch / announcement` / `Web or ad copy` /
   `Pricing / packaging change` / `Campaign concept`.
3. **Intended audience.** A named segment, or "general".
4. **What they want to learn** (optional). For example, "will producers read
   this as a price increase".

## Step 2: Seat the panel

Default: **6 seats**. Use the seating guide in `knowledge/roster.md`:

1. Seats that fit the stimulus type and the intended audience. When a segment
   is named, seat two personas from inside it where the roster has two, plus
   one from outside it. If the roster has only one (enterprise or IT is P9
   alone), seat that one and report the gap under **Blind spots**.
2. **One designated skeptic**, whose evidence runs against the stimulus.
3. **One churn-risk or lost-deal voice.** The VoC sources lean towards loyal
   users (the power-user interviews say so themselves), so this seat is a
   counterweight, not optional.
4. Honor explicit requests ("add the enterprise buyer"). The user can ask for
   4 seats (a quick check) or 10 (a broad sweep).

## Step 3: Refresh the evidence (optional, per run)

The roster is the base. Enrich the seated personas when the stimulus needs
current signal. Label every enrichment with its source and as-of date:

- **User-supplied material** (survey export, interview notes, a doc): read it
  first. It outranks the roster for the segment it covers.
- **Win-loss:** for any pricing or packaging test, pull current closed-lost
  reasons for the seated segments. Use a recent `/win-loss-pricing-analyzer`
  report if one exists; otherwise ask `/hubspot-agent` for the reasons. Any
  count or rate goes through `/rivermind:ask` first, per `CLAUDE.md`.
- **Gong:** through `/gong-calls-explorer`. Omni's Gong topic carries meeting
  metadata, not transcripts (`.claude/skills/inbound-demo-reply/pain-map.md`, "Data
  provenance"). Use it to see which segments are actively talking to us,
  never as a source of quotes.

If a live source fails, route around it or continue on the roster alone.
Note it in **Evidence used**, and give the user a short action list for the
fix, per the failure rule in `CLAUDE.md`.

## Step 4: Interview each persona

For each seat, read the stimulus cold, as that persona, and answer:

1. **First read:** what they think this is and who it is for, in one line.
   Misreads are the most valuable finding, so keep them.
2. **What lands:** the words or claims that hit a job or pain in their
   evidence.
3. **What confuses or grates:** jargon, a claim they doubt, a missing answer
   they came for (price, plan, "do I need a licence for this").
4. **The objection:** the one question or pushback they would raise.
5. **Next move:** `Clicks / buys` / `Asks sales` / `Ignores` / `Shares it` /
   `Complains or churns`.
6. **Reaction:** `Warm` / `Mixed` / `Cold`.
7. **In their words:** one simulated line in the persona's register. Label it
   as simulated. Never attribute it to a real customer.

Every point in 2 to 4 must trace to a line in the persona's evidence, or to a
Step 3 enrichment. Cite it in brackets (for example `[pain-map: Producer P2]`).
If the evidence says nothing about the topic, the persona says "no strong
view". Do not invent a reaction.

## Step 5: Read across the panel

1. **Where the panel splits:** 2 to 3 genuine divides. For each: who is on
   each side, and the underlying tension (price vs value, AI help vs control,
   self-serve vs sales).
2. **Loudest pushback:** the persona most likely to object in public or
   churn, and the exact phrase that triggers it.
3. **Lands across the board:** anything warm for four or more seats.
4. **Misread risk:** any claim or word that two or more personas read
   differently from the intent.
5. **Blind spots:** segments the panel did not cover, and where the evidence
   was thin or old.
6. **What to check next:** real validation to run before anyone relies on
   this (Convert test, customer interviews, a reply-rate check), plus
   handoffs.

If the whole panel is warm, swap in a sharper skeptic and run once more. If it
is still warm, report that as the finding and repeat the positive-skew warning.

## Constraints

- **Label the output** with the simulation line in the schema, once, at the top.
- **Read-only.** No writes to any system. Roster changes ship by PR.
- **No percentages of customers.** "4 of 6 personas" is fine. "67% of
  customers" is not. The panel is not a sample.
- **No fabricated customer quotes.** Real verbatims may be cited as grounding,
  with their source file, and they stay internal (`references/messaging/README.md`
  usage rules). Simulated lines are always labeled simulated.
- **Figures carry source and as-of date** (`references/evidence-standards.md`).
  A missing figure is "not in evidence", never a plausible number.
- **Product claims are flagged, not verified.** If a persona doubts a
  capability or plan claim, list it under **What to check next** and hand off to
  `/demo-reply-fact-check` or `/riverside-product-knowledge`.
- **Not a verdict and not copy.** Do not rewrite the stimulus. Suggested
  changes are pointers ("the Pro-to-Business line reads as a price hike to
  P3"), and the rewrite goes to the content pipeline.
- **Who reads it.** The chat report is for the requester. Before any of it
  reaches another person (a Slack thread, a deck, a brief), it runs `/ste` →
  `/de-ai` → `/critique` per `CLAUDE.md`, and it must not be presented as
  customer research.

## Output schema

```
> Simulated persona panel. Reactions are inferred from Riverside's customer-voice
> evidence (sources below), not from real customers. Use it to decide what to
> test, not as proof.

## What the panel saw
[Stimulus type, one-line summary, intended audience, what we wanted to learn]

## Seated: [P1], [P2], ... (skeptic: [name]; churn-risk: [name])
[One line on why this bench]

## Reactions at a glance
| Persona | First read | Reaction | Next move |
|---------|-----------|----------|-----------|

---

### [Persona name]: [segment, 3 to 6 words]
- **First read:** ...
- **Lands:** ... [evidence tag]
- **Confuses or grates:** ... [evidence tag]
- **Objection:** ...
- **Next move:** ... | **Reaction:** ...
- **In their words (simulated):** "..."

(repeat per seat)

---

## Across the panel
- **Where it splits:** ...
- **Loudest pushback:** ...
- **Lands across the board:** ... (or "Nothing warm for four or more seats")
- **Misread risk:** ... (or "None found")
- **Blind spots:** ...

## What to check next
- [Real validation or handoff, one per line, naming the skill]

## Evidence used
- [Source file or live pull, as-of date; any failed source and what was used instead]
```

Never drop a section. Use the fallback line when it is empty.

## Handoffs

| When the panel says... | Hand to |
|------------------------|---------|
| The copy needs rewriting | `/nik-voice` → `/de-ai` → `/critique` |
| A product or plan claim is doubted | `/demo-reply-fact-check`, `/riverside-product-knowledge` |
| The segment itself is unclear | `/value-proposition-canvas` |
| It sounds like everyone else | `/are-we-really-different` |
| A page or conversion issue | `/page-cro` |
| A split worth testing for real | Convert Experiences via `/marketing-brain` |
| The direction itself is in doubt | `/marketing-council` |

## Keeping the roster honest

`knowledge/roster.md` is built from dated sources. When a source refreshes
(the pain map is quarterly; the VoC docs when Product Marketing updates them),
re-check the personas that cite it and bump the roster's as-of line. A new
persona needs at least two evidence lines from a named source, a seating-guide
row, and a PR.

## Done when

The output follows the schema, every seat's lands, confuses and objection
points carry an evidence tag, the skeptic and churn-risk seats are named, at
least one split or an explicit unanimity finding is stated, and every figure
carries a source and as-of date.
