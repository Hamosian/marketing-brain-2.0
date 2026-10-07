<!-- last-reviewed: 2026-09-25 -->
# Pyramid Principle: deep reference

**Put the single governing thought first, then group the support beneath it by three rules. Build it bottom-up if you have to; always present it top-down.** This file holds the parts of Minto's method that `SKILL.md` only points at: the origin, the introduction patterns, the construction steps, the common mistakes and the sources. Load it for a long document, an executive summary, an upward memo, or a restructure the rules in `SKILL.md` do not settle.

## Where the method comes from

Barbara Minto joined McKinsey in 1963 as its first female MBA hire (Harvard Business School, one of eight women in a class of about 600). She saw that consultants' analysis was sound but their reports were hard to follow, because findings, conclusions and recommendations were mixed together. She decided the fault was in the thinking, not the language: people started writing before they had worked out what they thought. She published *The Pyramid Principle: Logic in Writing and Thinking* in the 1980s and expanded it later as *The Minto Pyramid Principle: Logic in Writing, Thinking and Problem Solving*. Minto is also widely credited with coining MECE.

The reason top-down works is working memory. A reader spends effort recognising words and more effort working out how ideas relate, and comprehension gets what is left. Minto cites Miller's "Magical Number Seven, Plus or Minus Two" (1956): the mind cannot hold many separate items, so it groups them. If the reader gets the summary first, every later idea has a slot to land in. If the conclusion comes last, the reader holds everything and guesses where it is going.

## The three rules and the four orders

The rules are the same as in `SKILL.md`. They are repeated here with Minto's own names.

1. Ideas at any level must always be summaries of the ideas grouped below them.
2. Ideas in each grouping must always be the same kind of idea. The test is one plural noun: reasons, steps, problems, recommendations.
3. Ideas in each grouping must always be logically ordered. Minto says there are only four possible orders, and the right one follows from how the group was produced:

| Order | Also called | Use when the group came from | Example |
|---|---|---|---|
| Deductive | Argument order | Reasoning from premises to a conclusion | Major premise, minor premise, therefore |
| Chronological | Time order | A process or a cause-and-effect chain | Step 1, step 2, step 3 |
| Structural | Spatial order | Dividing an existing whole into its parts | Region by region, funnel stage by stage |
| Comparative | Degree or ranking order | Classing like things together | Most important first |

## Vertical and horizontal logic

**Vertical.** Each statement raises one question in the reader's head (Why? How? How do you know? What should we do?). The line directly below answers it, and only it. The top point answers the reader's main question and raises a new one. The key line answers that. Each key-line point raises a further question, answered one level down. Do not raise a question you are not ready to answer.

**Horizontal.** A grouping is deductive or inductive.

- **Deductive:** each point follows from the one before and ends in a "therefore". It is heavy to read, because the reader must hold every premise before reaching the point, and one broken link breaks the conclusion. Keep it to four steps at most. It works well at paragraph level.
- **Inductive:** several independent ideas of the same kind, summarised by what they have in common. If one support fails, the point still stands. Minto prefers inductive groups at the key line and above, and says it is always better to present the action before the argument there.

**Limits.** At most four steps in a deductive chain. Two to five items in an inductive group. Never a lone child point: one point is not a group. A group above five usually hides a missed higher-level grouping.

## MECE

Mutually Exclusive, Collectively Exhaustive. Siblings do not overlap, and together they cover all of what the parent claims. MECE is how you check rules 2 and 3 in practice. Overlap means categories are mixed. A gap means the parent claims more than its support proves. When a gap is real and cannot be filled (the data does not exist yet), narrow the parent's claim to what the support does prove, and say what is missing.

## The introduction: SCQA

A document, memo or long brief opens with a short story the reader already accepts, which ends on the question the governing thought answers.

- **Situation:** a stable, uncontroversial fact the reader already knows and agrees with.
- **Complication:** the change or problem that creates tension in that situation.
- **Question:** the question the complication raises. Often left implied.
- **Answer:** the governing thought. The top of the pyramid.

The introduction reminds; it does not inform. Nothing new goes in it except the complication, and it carries no data and no argument. Its length depends on what the reader needs, not on how long the document is. For a reader who already has the context (most chat and Slack), skip it.

### Four common patterns

| Purpose | Situation | Complication | Question | Answer |
|---|---|---|---|---|
| Directive (giving direction) | We want to do X | We need you to do Y | How? | The steps |
| Seeking funds (approval to spend) | We have a problem | We have a solution that costs N | Should you approve? | Yes: the benefit outweighs the cost |
| Explaining how to | We must do X | We are not set up to do it, or the current way does not work | How do we get set up? | The steps |
| Choosing between alternatives | We want to do X | There are several ways to do it | Which is best? | The choice, with the main reason for it and the main reason against each other option. If it depends on goals: "Choose A if you care most about X" |

### Four orderings of the introduction

| Variant | Order | Use it when |
|---|---|---|
| Standard | S, C, A | The reader needs a moment of context before the answer lands |
| Direct | A, S, C | The reader is busy and trusts you. **The default for upward writing in this repo** |
| Concerned | C, S, A | The reader is already worried about the complication |
| Aggressive | Q, S, C, A | You want to sharpen the question the reader should be asking |

The four orderings come from secondary summaries of the book; treat them as a working guide, not as Minto's exact wording.

## Building the pyramid

**Top-down, when you broadly know your point.**

1. State the subject.
2. Decide the reader's question.
3. Write the answer.
4. Write the Situation.
5. Write the Complication.
6. Check that S and C really lead to that question and that answer.
7. Ask what new question the answer raises. The answers to it are the key line.
8. Repeat one level down.

**Bottom-up, when the point is still unclear** (notes, transcripts, data dumps, a long thread).

1. List every point you want to make.
2. Work out how they relate: cause and effect, or same kind.
3. Group them, and write the conclusion each group implies.
4. Repeat up the levels until one thought remains. That is the governing thought.

"Think bottom-up, present top-down" is the short form.

## Common mistakes and their fixes

| Mistake | What it looks like | Fix |
|---|---|---|
| Burying the lead | Background, method and analysis first, conclusion last: the order the work was done in | Move the answer to line 1. Background shrinks to an SCQ or disappears |
| Intellectually blank summary | "The company has three problems", "There are five changes", or headings like Findings, Issues, Conclusions | State the result the actions achieve together, or the inference the findings support |
| Unrelated list | A set of points with no stated link | Every grouping implies a point. Write it, or split the list |
| Mixed kinds | Problems, causes and recommendations in one list | Apply the one-plural-noun test and split into separate groups |
| Too many items | Seven, nine, twelve bullets in one group | Find the two or three higher-level groups hiding inside |
| Deduction at the top | The reader follows a long argument before learning the action | Make the key line inductive. Put the chain lower down |
| Lone child | A heading with one bullet under it | Merge it into the parent, or find its sibling |
| Repeated close | A final "In summary" that restates line 1 | Cut it. End on the ask, or end |

## Short outputs and BLUF

An email, a Slack reply, an executive summary or an answer to a question is a small pyramid. The answer goes in the first line. Then 2-5 supporting points of the same kind, in a logical order. S and C are skipped or compressed when the reader has the context. This matches the military BLUF (Bottom Line Up Front) format, where the first line states the purpose and the action needed, and the background follows as bullets (HBR, Sehgal 2016). BLUF covers only the "answer first" step. Minto adds the grouping and ordering rules for everything underneath it.

**Known limit.** Top-down suits informing and persuading better than exploring. When a reader is likely to reject the conclusion, or the task is to think something through together, still lead with where you have landed, but frame it as the current view and make the key line the evidence and open questions, so the support is judged on its own.

## Validation checklist (full form)

1. There is one governing thought, and the reader finds it in the first sentence or on the first slide.
2. It answers the question the S and C raise. The Situation is uncontroversial and the Complication really creates the Question.
3. Every point's question is answered by the line directly below, and only there.
4. Every group passes the one-plural-noun test.
5. Every group is MECE against its parent's claim.
6. Every group is in one named order, and that order matches how the analysis was done.
7. At most four deductive steps. Two to five inductive items. No lone child.
8. Each summary is a real inference or effect, not a label.
9. Siblings share one grammatical form.
10. The key line is inductive, with the action before the argument.

## Sources

- Barbara Minto, official site: <https://www.barbaraminto.com/> and <https://www.barbaraminto.com/concept>
- Wikipedia, Barbara Minto: <https://en.wikipedia.org/wiki/Barbara_Minto>
- McKinsey Alumni, "Barbara Minto: MECE: I invented it, so I get to say how to pronounce it": <https://www.mckinsey.com/alumni/news-and-events/global-news/alumni-news/barbara-minto-mece-i-invented-it-so-i-get-to-say-how-to-pronounce-it>
- StrategyU, The Pyramid Principle, parts 1 and 2: <https://strategyu.co/pyramid-principle-partone/>, <https://strategyu.co/pyramid-principle-2/>
- Will Larson, notes on The Pyramid Principle: <https://lethain.com/pyramid-principle/>
- Sebastien Phlix, book summary: <https://www.sebastienphlix.com/book-summaries/minto-pyramid-principle>
- Manager 138, Pyramid Principle introductions: <https://manager138.com/resources/minto_pyramid_principle/ch4_introductions.html>
- ModelThinkers, Minto Pyramid and SCQA: <https://modelthinkers.com/mental-model/minto-pyramid-scqa>
- Kabir Sehgal, "How to Write Email with Military Precision", HBR, 2016: <https://hbr.org/2016/11/how-to-write-email-with-military-precision>
