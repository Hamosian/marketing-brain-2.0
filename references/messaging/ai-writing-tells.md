# AI writing tells

A checklist of the patterns that make writing read as machine-generated, and how to fix each one. This is the reference behind the `nik-voice → de-ai` pass every Riverside output runs through. Load it whenever you are drafting or editing external-facing copy, or running a final human-quality pass.

Source: adapted from Ruben Hassid's anti-AI taxonomy (July 2026), the community and power-user voice research in this directory, Nik's voice rules in `CLAUDE.md`, and Peter Yang's [no-ai-slop](https://github.com/petergyang/no-ai-slop) skill (added Aug 2026).

## Source of truth

This file is the **canonical, comprehensive list** for Riverside. Maintain the list here; don't fork it into other skills. The `de-ai` skill is the **portable baseline** - it carries a lighter, self-contained version so it still works outside this repo, and it defers to this file wherever the two differ on Riverside work. When you learn a new tell, add it here.

## The point (and what this is not)

The goal is writing a real person would actually type, not writing that sneaks past an AI detector. Those are different jobs. Detectors like Pangram are close to a coin flip on any single short text (one em-dash-to-colon swap can flip a verdict from "100% AI" to "100% human"), so optimizing to beat them is a waste of time and rewards slop that happens to test clean. Optimize for the reader instead. If the writing is specific, has a point of view, and sounds like the person whose name is on it, the detector question takes care of itself.

**Workslop** is the failure mode to avoid: AI output that looks like work but just transfers the work to the reader, who now has to decode it, guess the intent, and redo it. Every tell below is a small act of workslop.

## How to use

1. Draft with `nik-voice` (or the relevant voice/style skill) applied.
2. Run this reference as the final pass: read the draft and actively hunt for each pattern below. When you find one, rewrite it the way a person would type it. Don't just soften it.
3. For a quick gut check, scan the three highest-signal tells first: **em dashes, Tier-1 words, and "it's not X, it's Y."** If a draft has none of those, it is usually most of the way there.
4. For a detect-only request ("is this AI slop?", "flag what reads as AI" without a rewrite), don't rewrite the draft. Name each pattern below that appears, quote the line, and give the fix in a few words. Named patterns are evidence the person can check themselves - don't add a score or a verdict on whether AI wrote it (see the point above about detectors).

## Structure and rhythm tells

- **Low burstiness.** Uniform 15-to-20-word sentences and rectangular paragraphs. Force a spread: at least one sentence of six words or fewer *and* one of 25+, uneven paragraph lengths, and no more than one single-line paragraph.
- **Fractal summaries.** Previews and recaps at every level ("In this section we'll…" / "…as we've seen"). Delete them all.
- **Signposted conclusion.** "In conclusion / Overall," followed by a restatement and an uplift ("Despite the challenges, the future is bright"). Delete it and end on the last concrete point.
- **Pep-talk ending.** "As we move forward, embracing X will be key." Delete on sight.
- **Prompt echo.** "This post will explore…" / "Great question." Delete.
- **Listicle in a trenchcoat.** "The first reason is… The second reason is…" Merge into a flowing argument.
- **Uniform staccato.** "X is A. X is B. X is C." Combine into one sentence with a list, or vary the framing.
- **Dramatic fragmentation.** "That's it. That's the whole thing." or a chain of one-note fragments joined by "And": "X. And Y. And Z." Use complete sentences.
- **Rhetorical setups.** "What if I told you...", "Think about it:", "Plot twist:", a question the very next sentence answers. Drop the setup and make the point directly.

## Punctuation and formatting tells

- **Em dashes.** The most famous tell. AI averages 20+ per piece; people use two or three. Nik's rule is zero. Use a period, comma, or colon.
- **Bold-first bullets.** "**Security:** …" Almost no one does this unprompted. Use it only when a real scannable list genuinely needs labels.
- **Emoji bullets.** Decorative ✅ 🧠 🔹 arrows. Strip them. (Slack messages sent by the OS agent are the deliberate exception, per `CLAUDE.md`.)
- **Title Case Headings and colon-split titles.** "The Power of X: Why Y Works." Use sentence case and cut the colon formula.
- **Colon reveals.** A noun phrase, a colon, then a lowercase dramatic reveal: "The best part: it learns." "The detail that makes it work: a separate agent grades it." Rewrite as a plain sentence and reserve colons for lists, labels, and quotes.
- **Bullets and headers as decoration.** A bulleted list where two sentences of prose would read better, or a header over a two-sentence section. Format should follow the content, not decorate it.
- **Oxford comma every single time.** Dropping it occasionally in a casual register reads more human.
- **Markdown residue.** Stray `**`, `##`, or `[text](url)` in a context that doesn't render markdown.

## Content and voice tells

- **No concrete imagery.** If the first three sentences evoke nothing you can see, inject a thing, place, number, or name.
- **Proper-noun avoidance.** "a client," "a tool," "a city" → name it. (When AI invents names they cluster on Emily and Sarah.)
- **Uniform positivity.** Everything upbeat and certain. Let something be annoying, unresolved, or a real trade-off.
- **Both-sidesing.** Every claim auto-balanced by its counterpoint. Pick a side and commit.
- **Suspiciously tidy anecdotes.** Stories that serve the argument with perfect efficiency. Real stories have tangents.
- **Register scrubbing.** No contractions, no slang. Restore the ones the voice would actually use. (Nir: contractions by default; "would" can stay uncontracted, see `nik-voice`.)
- **Faux-insight setups.** "What nobody tells you," "The part everyone misses," "This is the part most people skip." These flatter the writer as the lone expert. Cut the setup and let the claim stand on its own: "The part everyone misses: distribution is the moat" becomes "Distribution is the moat."
- **Superficial analysis.** Trailing `-ing` clauses that gesture at meaning without adding any: "highlighting the team's commitment," "underscoring its significance," "reflecting a broader shift." State the actual mechanism or consequence instead.
- **Interpretive metadiscourse.** Lines that step outside the subject to tell the reader what to notice or how much weight to give it: "That last part matters more than it sounds," "As you can see," "This distinction matters," a redundant "In other words." If the point is already clear, delete the aside.
- **Weasel attribution.** "Experts agree," "studies show," "widely regarded as," "industry reports suggest." Name the source or cut the claim - the writing-level version of the never-silently-pick rule in `references/evidence-standards.md`.
- **Synonym cycling.** Rotating terms for the same thing across sentences for variety: "The agent reviews the draft. The assistant scores the piece. The tool suggests fixes." Repeat the clear word instead.
- **Portability test.** If a sentence could move unchanged to another person, company, or product, it's probably filler. Cut it or replace it with a fact, example, mechanism, or judgment specific to this subject.

## The word lists

### Tier 1 - never use

**Verbs:** delve, leverage, underscore, harness, foster, navigate (figurative), utilize, facilitate, streamline, bolster, illuminate, showcase, embark, elevate, empower, unleash, unlock (figurative), uncover, optimize, garner, resonate, revolutionize, shed light on, synthesize, elucidate, transcend, reimagine, intertwine, entwine, grapple with, espouse, exemplify, underpin.

**Nouns:** tapestry, landscape (figurative), realm, ecosystem (figurative), paradigm, synergy, testament, beacon, journey (figurative), interplay, intricacies, symphony (figurative), kaleidoscope, tempest, whimsy, quest (figurative), roadmap (figurative), endeavor, myriad, plethora, advancements, trajectory (figurative).

**Adjectives / adverbs:** pivotal, crucial, seamless(ly), robust, vibrant, intricate, meticulous(ly), nuanced, cutting-edge, transformative, game-changing, groundbreaking, unparalleled, invaluable, multifaceted, commendable, indelible, poignant, profound(ly), relentless(ly), tireless(ly), unwavering, unyielding, timeless, ever-evolving, fast-paced.

**Stock phrases:** in today's fast-paced world/landscape, it's important to note, it is worth noting, plays a pivotal/crucial role in, stands as a testament to, marks a pivotal moment, solidifies its position, underscores its significance, rich tapestry/history/heritage, navigate the complexities of, in conclusion, in summary, overall (as an opener), ultimately (as a conclusion opener), at its core, that being said, a key takeaway, paving the way for, valuable insights (into), deeper understanding of, when it comes to, in terms of, in order to, the reality is, the truth is, not only… but also, here's the kicker/the thing/the best part, I hope this email finds you well, look no further, dive/deep-dive into, let's explore/unpack/break down, furthermore, moreover, additionally (sentence-initial), this changes everything, this is huge.

**"It's not X, it's Y" (negative parallelism).** The single most overused AI construction. "This isn't a tool, it's a partner." Rewrite as a direct claim.

### Conversational crutches (Slack, email, DMs)

The tells that give away short, casual writing. AI leans on these as filler; cut or swap each one.

- "non-negotiable" → just say what you actually need people to do
- "I want to be clear" / "let me be clear" → be clear, don't announce it
- "at the end of the day" → cut or rephrase
- "I hear you" → only if someone actually said something you're responding to
- "let's be real" → rarely needed, just be real
- "moving forward" → cut it
- "don't hesitate to" → "just [do the thing]"
- "circle back" → "come back to this" / "revisit"
- "aligns with" → "fits," "matches," "works with"
- "holistic" → almost always cuttable
- "in essence" → cut it, say the thing
- "aforementioned," "henceforth" → never

### Tier 2 - fine on their own, a tell in a cluster

comprehensive, significant(ly), essential, critical, key (adjective), dynamic, innovative, powerful, notable/notably, vital, vast, rich (figurative), deep/deeper (figurative), explore, enhance, ensure, highlight, reveal, engage, embrace (figurative), insights, perspective, framework, approach, strategy, challenges, opportunities, potential, impact(ful), quietly/quiet (figurative "quiet confidence"), genuinely, truly, remarkably, arguably, thought-provoking, well-being, resilience, perseverance, dedication, commitment to, high-quality, step-by-step, sustainable/sustainability.

One of these alone is fine. Three or four in a paragraph is the smell.

## Pro tip

For clear, unglamorous instructional copy (setup guides, internal SOPs), prompting for **ADS-STE100 Simplified Technical English** produces plain, IKEA-instruction clarity with none of the flourish. It is wrong for creative or brand work, right for step-by-step guidance.
