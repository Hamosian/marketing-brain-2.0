---
name: marketing-council
description: Debates a marketing decision from opposing, documented expert lenses before anyone drafts anything. Seats 3 to 5 named thinkers (Godin, Ogilvy, Schwartz, Hopkins, Halbert, Brunson, Hormozi, Dunford, Sutherland, Sharp, Handley, Vaynerchuk) as a simulated council, always including a dissenter, applies each one's published frameworks to the case, maps where they genuinely disagree, then gives a chair's recommendation with Riverside skill handoffs. Use for a direction decision with stakes - positioning, pricing or packaging, brand vs performance spend, a launch, channel choice - not for diagnosing a number or judging a draft. Triggered by "marketing council", "convene the council", "debate this decision", "opposing views on", "what would Godin say", "what would Sharp say about", "channel Hormozi on this", "pressure-test this direction", "board of advisors", or "/marketing-council".
user-invocable: true
---

# Marketing Council

Convene a simulated board of marketers whose documented frameworks collide,
apply each to one Riverside decision, and surface the trade-offs before a
direction is chosen. The value is the disagreement, not any single take. A
council that agrees is a mirror.

Adapted from the `marketing-council` skill in Corey Haines's
[marketingskills](https://github.com/coreyhaines31/marketingskills) (MIT):
the bench, the dissenter rule and the disagreement map are theirs. The
Riverside seating guide, the data rules, the handoffs and the boundary with
`/marketing-brain` and `/critique` are ours.

**This is persona simulation, not the real people.** Every take is built from
what the advisor actually published (`knowledge/advisors/`). Label it as such.

## Where this sits

| The request is... | Goes to |
|-------------------|---------|
| A **direction decision with stakes** (how to position, what to charge, brand vs performance, launch or not, which channel) | this skill |
| A **diagnosis of a number** from many angles ("why did trials drop") | `/marketing-brain` depth-first, which pulls live data and reconciles specialists |
| A **verdict on a finished draft** | `/critique` |
| A **sameness check against competitor copy** | `/are-we-really-different` |

The council sets direction. It never writes the page, the deck or the email.

## Inputs and context to load

- `CLAUDE.md`, then `references/evidence-standards.md` if the question carries a figure.
- Only the seated advisors' dossiers from `knowledge/advisors/`. Never all twelve for a three-seat session.
- Any figure in the question comes from Nir or from `/rivermind:ask`. The council does not invent metrics, benchmarks or competitor numbers; an advisor who needs a number they do not have says so.

## Step 1: Frame the question

Ask through `AskUserQuestion` only for what is missing:

1. **The decision.** One sentence, with the options on the table.
2. **The stakes.** What changes if it goes well or badly; what was already tried.
3. **Mode.** `Council session (3 to 5 seats, default)` / `Quick take (one named advisor)` / `Full council (all 12; long, only when the stakes justify it)`.

Then write the one-line Q2 tie (awareness, activation, pipeline). If there is none, say so; the council still runs, but the synthesis notes it.

## Step 2: Seat the bench

For a council session, seat 3 to 5:

1. Two or three whose lens fits the question type.
2. **At least one designated dissenter** whose documented position runs against where the question already leans. Name them as the dissenter in the output.
3. Honor explicit requests ("I want Sharp and Dunford on this").

| Riverside question type | Strong fits | Natural dissenters |
|-------------------------|-------------|--------------------|
| Positioning vs Descript, StreamYard, Zoom | Dunford, Godin, Schwartz | Sharp (distinctiveness over differentiation) |
| PLG pricing, packaging, free-to-paid gates | Hormozi, Brunson, Hopkins | Sutherland (price is not the value lever), Godin |
| Brand awareness spend vs performance | Sharp, Ogilvy, Sutherland | Hopkins, Halbert (show the response) |
| Content and thought leadership | Handley, Godin, Vaynerchuk | Sharp (reach beats depth), Hopkins |
| Paid media mix and channel choice | Hopkins, Sharp, Vaynerchuk | Godin (interruption is a tax) |
| SLG pipeline motion, enterprise narrative | Dunford, Hormozi, Halbert | Handley (trust erodes under pressure), Sharp |
| Launch or campaign strategy | Brunson, Godin, Halbert | Sharp (launches fade, availability compounds) |
| Creator and partner channels | Vaynerchuk, Godin, Halbert | Sharp, Ogilvy (measure it) |

## Step 3: Run the session

1. **Load the seated dossiers.** Each holds frameworks with sources, documented positions, signature questions, blind spots and voice notes.
2. **Optional research pass.** When the question is specific or time-sensitive, or Nir wants sources, run `WebSearch` per seated advisor for their published take on this class of question, primary sources first (their books, newsletters, talks). If research contradicts a dossier, follow the research and note it.
3. **Each advisor's take**, 2 to 4 paragraphs: open by applying their signature questions to this case, apply their named frameworks to the specifics, land a recommendation with the conviction their record supports. In their register per the voice notes. No fabricated quotes.
4. **The disagreement map.** 2 to 4 genuine conflicts. For each: who says what and from which framework, the underlying trade-off it exposes (reach vs resonance, price vs value, brand vs response), and what evidence would settle it for Riverside.
5. **Chair's synthesis.** The recommendation fitted to Riverside's stage, motion (PLG, SLG or both) and Q2 priorities; which advisor's warning stays on as a tripwire and what signal trips it; the next steps, each handed to the skill that executes it.

## Constraints

- **Label the session** once at the top with the simulation line in the schema.
- **No fabricated quotes.** Direct quotation only when the dossier or the research pass names the source. Otherwise paraphrase and name the work.
- **No invented endorsements.** An advisor applies a framework to the case. Never state or imply the real person holds a view about Riverside, a Riverside competitor or a named controversy.
- **Living advisors get extra care.** Godin, Brunson, Hormozi, Dunford, Sutherland, Sharp, Handley and Vaynerchuk are active; prefer the research pass for anything time-sensitive.
- **Strongest version of each view.** No strawmen for the synthesis to knock down. If a dossier does not reach the question (Hopkins on TikTok), say so and reason by explicit analogy.
- **If the seated bench agrees**, re-seat with a sharper dissenter before writing. If it still agrees, say so in the disagreement map; unanimity on a real decision is itself a finding worth stating.
- **Figures carry source and as-of date**, per `references/evidence-standards.md`. Missing figure: write "not in evidence" rather than a plausible number.
- **Council output is normally read by Nir alone.** If it goes into anything another person reads (a deck for Abel, a Slack thread), it runs `/nik-voice` then `/de-ai` then `/critique` first.

## Output schema

```
> Simulated council. Each take is built from the advisor's published frameworks
> and positions, not their actual review.

## The question before the council
[1 to 2 sentences: the decision, the options, the stakes. Q2 tie: <priority or "none">]

## Seated: [A], [B], [C] ([mode]; dissenter: [name])
[One line on why this bench]

---

### [Advisor A]: [lens, 3 to 5 words]
[2 to 4 paragraphs]
**Bottom line:** [one sentence]

### [Advisor B]: ...

---

## Where the council disagrees
1. **[Conflict]**: [A] holds X ([framework]); [B] holds Y ([framework]).
   The trade-off: [tension]. What settles it for Riverside: [evidence or test].
2. ...
(If none after re-seating: "The bench agrees on [X]. Unanimity noted as a finding.")

## Chair's synthesis
[Recommendation fitted to Riverside's stage, motion and Q2 priorities]
- **Do:** [2 to 4 concrete next steps]
- **Tripwire:** [which advisor's warning to watch, and the signal that trips it]
- **Execute with:** [skill handoffs from the list below]
```

## Handoffs

| When the direction is... | Hand to |
|--------------------------|---------|
| Positioning or customer-side value work | `/value-proposition-canvas`, then `/are-we-really-different` to check it lands as distinct |
| Anything written for a person | `/nik-voice` then `/de-ai` then `/critique` |
| A page or conversion change | `/page-cro` |
| A paid media move | `/paid-acquisition-agent` |
| A behavioral mechanism to build in | `/marketing-psychology` |
| A cross-system plan or investigation | `/marketing-brain` |
| A test the disagreement map called for | Convert Experiences via `/marketing-brain` |

## Adding an advisor

Add `knowledge/advisors/<slug>.md` with the same headings as the existing
dossiers (Lens, Core frameworks, Documented positions, Signature questions,
Best for / blind spots, Voice notes, Key works, Status), every position
sourced, and add a row to the bench table in `knowledge/advisors/README.md`.
For an internal person (an exec, a former boss), the user supplies the
positions; never invent them. Ships by PR like any skill edit.

## Anti-patterns

- **The agreeing council.** Re-seat.
- **Name-flavored generic advice.** If the take survives with the name swapped, it is not a take.
- **Quote soup.** Apply the method, do not stitch famous lines.
- **Council for execution.** Direction here, drafting elsewhere.
- **Twelve seats on a headline.** Match bench size to stakes.
- **Diagnosis in disguise.** "Why did X drop" is `/marketing-brain`'s job; the council answers "what should we do about X".

## Done when

The output follows the schema, names the dissenter, contains at least one
genuine conflict (or states that unanimity is the finding), every figure
carries a source, and each "Do" step names the skill that executes it.
