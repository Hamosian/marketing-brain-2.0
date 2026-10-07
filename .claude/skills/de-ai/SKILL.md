---
name: de-ai
description: Strips AI tells from a finished draft so it reads like a person typed it. One mechanical cleaning pass, run on every piece of writing a person other than the author will read - Slack messages, emails, LinkedIn posts, docs, decks, prospect replies. Stage 2 of three - brand-voice writes before it, critique judges after. Trigger on "de-slop this", "make it sound human", "more human", "add personality", "this sounds like AI", "sounds robotic", "it feels generic", "fix AI writing", "humanize this", or automatically as the final prose pass on any drafted content. Absorbs and replaces the retired content-humanizer skill. NOT a voice or tone skill (that is brand-voice) and NOT a quality verdict (that is critique).
---

# de-ai - the cleaning pass

AI-generated text has a recognizable smell. People cannot always name it, but they feel it instantly. This skill catches and fixes the patterns that trigger that feeling.

**One job: strip the tells from a draft that is already written.** It does not choose the tone, pick the register, or decide whether the piece is any good. `brand-voice` did the first two before this ran; `critique` does the third after.

Run it as the **final prose pass** on anything outward-facing. It is cheap by design: a checklist over finished text, no research, no judgment calls.

Apply the pass to writing intended for another person. Private working notes may skip the pass unless requested.

## First: triage the density

Count the tells before fixing any of them.

- **Roughly 10 or more tells per 500 words: stop editing and rewrite.** Polishing a draft that is 80% AI patterns produces AI patterns with nicer words. Say so, and send it back to `brand-voice` with the register named.
- **Under that: fix in place**, pattern by pattern, below.

Score each find 🔴 kills credibility / 🟡 softens impact / 🟢 polish only, and fix every 🔴 before touching a 🟢.

## The patterns

### 1. Too clean, too organized 🔴

Real people do not write with one perfect idea per paragraph, each building neatly on the last. Real messages meander. A thought interrupts another thought. Someone circles back.

**AI:** three paragraphs, each a self-contained single theme, reading like an outline that got fleshed out.
**Human:** ideas bleed into each other, punctuation is functional rather than architectural, emphasis comes from word choice and repetition instead of paragraph breaks and bold.

This is the highest-frequency failure and the hardest to see in your own draft. Four tidy paragraphs in a three-line Slack message is the tell, not the tidiness.

### 2. AI vocabulary 🔴

Never just delete. Always replace.

| AI phrase | Use instead |
|---|---|
| delve, delve into | look at, dig into, break down |
| leverage, utilize | use |
| navigate (metaphorical) | deal with, figure out, get through |
| the [X] landscape | how [X] works today, or cut |
| crucial, vital, pivotal | state the thing and let it be self-evidently important |
| robust, comprehensive, holistic | be specific: "handles 10,000 requests/sec" |
| foster, facilitate | help, make easier, allow |
| furthermore, moreover, in addition | nothing, or "and", or "also" |
| ensure | make sure, or cut |
| that said | but, or cut |
| moving forward | cut |
| circle back | come back to this |
| aligns with | fits, matches, works with |
| don't hesitate to | just [do the thing] |
| at the end of the day | cut |
| in essence | cut |
| aforementioned, henceforth | never |

The rule: if the word feels like it came from a thesaurus or a TED talk, swap it for the word you would use texting a coworker.

### 3. Hedging chains 🔴

AI hedges constantly, because it does not know if it is right. Humans hedge sometimes, not every sentence. Cut on sight:

"It's important to note that" · "It's worth mentioning that" · "One might argue that" · "In many cases" · "In most scenarios" · "It goes without saying" · "Needless to say" · "I want to be clear" · "Let's be real" · "Here's the thing"

Just note the thing. Just be clear. Just be real.

### 4. Performative sincerity 🔴

AI signals that it is being sincere. A person says the thing and lets the sincerity live in the action.

**AI:** "Let me know if I can help. I mean it."
**Human:** "let me know if I can help with anything"

Cut "I mean it", "genuinely", "I really do care" every time.

### 5. Overly parallel structure 🟡

"Not X. Not Y. Not Z. Just W." Or "Do A. Do B. Do C." Real people use parallel structure sometimes, then break it before it becomes a drumbeat.

**AI:** "Push meetings. Push deadlines. Push anything that isn't critical."
**Human:** "push meetings and deadlines if you need to, anything that's not critical can wait"

Note: `brand-voice` uses parallel negatives deliberately in the public register. Once per piece is a move; twice is a tell.

### 5b. The rule-of-three verdict 🔴

A conditional that stacks three tidy clauses and lands on a short pronouncement: "If we know what they record today, what they use for it, and the owner is on the call, that's a booking." It reads like a policy being handed down, not a person talking, and it is one of the most recognisable machine shapes because it is so neat: three parallel items, a comma, a four-word verdict. The same shape shows up as "X, Y and Z. That's the meeting we want." or "Do A, B and C, and you're done."

**Fix:** say it the way it was said to you. Two items and a plain "as long as" beat three items and a verdict: "we can skip budget, as long as we know which tools they're using today and that there's a real use case." Never end a paragraph on a verdict line ("that's a booking", "that's the bar", "that's the meeting we want").

### 6. Vague claims dressed as evidence 🔴

AI replaces specific claims with vague ones because specific claims can be wrong.

"Many companies" → which ones · "Studies show" → which study · "Significantly improved" → by how much · "Leading brands" → name one · "A lot of" → how many

If the specific is not available, say so honestly rather than reaching for the vague version. You cannot invent proof, so flag the gap instead of smoothing over it.

### 7. False certainty 🟡

Asserting confidently about things nobody can be certain of. "Companies that do X are more successful." According to what? This is not confidence, it is laziness wearing confidence.

### 8. Unnecessary bolding and formatting 🟡

In Slack and quick email, real people almost never bold. They certainly do not bold a key phrase in every paragraph like a textbook. Bold should be rare and only for something genuinely critical. No headers in a Slack message. No bullets unless listing actual separate items.

### 9. The neat closing 🟡

AI wraps everything with a bow: a final restatement, a motivational closer, an "in conclusion" paragraph that paraphrases the intro. Real messages just end, sometimes mid-thought.

**Test:** cut the last sentence. If the piece is better, it was a bow.

### 10. Perfect grammar in casual contexts 🟢

In Slack, real people skip opening capitals, write run-ons joined by commas, start sentences with "and" or "but", and do not always end with a period. Match the formality to the channel. A board narrative needs proper grammar; a Slack message does not.

### 11. Emotional stage directions 🟡

AI describes emotions instead of expressing them. "I'm starting to feel the toll on all of us" is a narrator describing a character. "this is taking a toll on all of us, I can feel it" is a person talking.

### 12. Rewriting the input instead of preserving its energy 🔴

When the author gives rough notes, preserve their intent and useful phrasing. Clarify grammar without adding opinions, scope, or personal anecdotes.

## The fix process

1. **Read it back as if a coworker sent it.** Would you think "this sounds like ChatGPT"? That part needs fixing.
2. **Triage the density.** Ten-plus tells per 500 words means rewrite, not edit.
3. **Scan the vocabulary table.** Replace every hit.
4. **Check the structure.** Every paragraph a clean single-topic unit? Break it up.
5. **Check the formatting.** Strip back to what a person would type.
6. **Cut the last sentence** and see if it is better.
7. **Read once more.** If it passes "would I believe a human typed this in 45 seconds", it is done.

## Format notes

- **Slack:** minimal formatting. Lowercase fine. Run-ons fine. Can be one block. Use emoji only when the author asks for them.
- **Email:** slightly more structured, still conversational. Short paragraphs. Never "I hope this finds you well."
- **LinkedIn:** structured and intentional, but perfectly alternating short and long sentences is its own tell. Break the rhythm somewhere.
- **Docs and reports:** formal grammar is fine. Watch the vocabulary and the too-neat structure.
- **Decks:** bullets are expected. Cut the AI vocabulary and keep the language conversational.

## Honest reporting

**A tick you cannot justify is worse than a missing one.** If this skill was invoked and returned no body, its rules were not read and the pass did not happen. Say so rather than claiming it ran. Applying the rules from memory is not the pass.

## Related

- `brand-voice` writes the draft and owns the register. It runs first.
- `critique` scores the result and returns SHIP or REVISE. It runs last and never rewrites.
- `ste` handles plain-language drafting before this review when appropriate.
- **Retired: `content-humanizer`.** Its detection list, severity triage, density threshold and replacement tables are folded in above. Its voice-injection mode belongs to `brand-voice` and its rhythm patterns are distilled into the registers. Do not reintroduce it; two humanizers is the duplication this consolidation removed.
