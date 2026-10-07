<!-- last-reviewed: 2026-09-13 -->
# Skill evals

How the Marketing OS tests its own behaviour, why the layer exists, and how to extend it.

Adapted from the tool-evaluation pattern in Anthropic's
[claude-cookbooks](https://github.com/anthropics/claude-cookbooks)
(`tool_evaluation/`), where an agent runs a suite of task→expected-answer pairs and - the
part worth stealing - reports structured **feedback on the tool definitions it was given**
alongside its answers. The score tells you something broke; the feedback tells you which
definition to fix. Applied here, "tool definitions" are the frontmatter descriptions this
repo routes on.

## The gap this closes

Before this layer the repo had two guardrails and a blind spot:

| Guardrail | Checks | Misses |
|-----------|--------|--------|
| `.github/workflows/team-context-lint.yml`, `scripts/lint_agents.py` | Structure: frontmatter present, tools scoped, models pinned, registries in sync | Whether any of it *works* |
| `/health-check` | Staleness: old `last-reviewed`, missing fields, template drift | Whether a fresh doc is a correct one |

Both are static. Neither could catch the failure mode that actually costs us: **61 skills
routed on descriptions alone.** Add skill 62 whose description says "review the page before
launch" and `/marketing-website-page-qa` quietly starts losing requests. Nothing fails. No
one notices until someone gets the wrong agent and does not mention it.

Routing is the load-bearing surface of a progressive-disclosure repo. It had no test.

## Three tiers

Deliberately split by cost, because an eval nobody runs is worse than no eval. Tiers 1 and 2
test *which skill fires*; tier 3 tests *what it then produces*.

### Tier 1 - deterministic (`scripts/eval_routing.py`)

Stdlib only, no model calls, runs on every PR touching skills or the suite.

Builds a TF-IDF vector per skill over its `name` + `description`, using the same tokenizer
and stopword list as the semantic index (`scripts/sync_embeddings.py`) so "what a keyword
search would match" means one thing across the repo. Then, per case, it ranks every skill
against the request.

**Fails the build** on structural problems only - a case expecting a skill that no longer
exists, a duplicate request, a malformed line. A rename that orphans a case fails here
instead of rotting.

**Warns** on ambiguity: a rival scoring at or above the expected skill. Lexical overlap is a
proxy for what a router keys on, not a prediction of what Claude will do, and a proxy has no
business failing a build on its own. `--strict` promotes warnings to failures for local
tightening work; CI does not use it.

What it is genuinely good at: telling you **where the vocabulary collides**. That is the
input Tier 2 needs, obtained for free.

### Tier 2 - model-in-the-loop (`/skill-eval`)

Reads Tier 1's `--json` output, then scores cases by *reasoning* over descriptions -
resolving the artifacts Tier 1 cannot (no stemming, noisy short requests) and, per the
cookbook pattern, **returning a patch, not just a score**: exact before/after description
text for every miss, with the cause named.

Its central constraint is that scoring uses **only** `name` + `description`. That is what
the router sees. An eval that reads skill bodies to decide routing measures the evaluator's
reading comprehension instead of the system's routing, and will happily report a green suite
over a broken router. Bodies come out only afterwards, to diagnose a miss.

### Tier 3 - output lift (`scripts/eval_output_lift.py`)

Tiers 1 and 2 both stop at the routing surface. Neither one asks whether the skill that fired
produced anything better than the model would have produced alone, which is the question that
decides whether a skill is worth its always-loaded description.

This tier answers it by running every case twice, once with the skill body loaded and once
bare, scoring both arms against the same criteria, and reporting the gap. Zero lift means the
skill is not earning its context cost.

Same cost split as tier 1. The default mode is stdlib-only structural validation of the suite
and runs on every PR; model calls happen only under `--run`, which is a deliberate local step.
Within a run the split repeats: deterministic checks (regex gates and prose-length ceilings)
are scored offline, and only the prose assertions reach a grader. That is this document's own
"deterministic checks first" rule applied one level down.

Two constraints are enforced rather than recommended:

- **The grader is not the model under test.** `--run` requires both `--subject-model` and
  `--grader-model` and refuses when they match. See the closing section of this document.
- **Neither arm runs from the repo root.** Run from here, both arms would load `CLAUDE.md`
  and its always-on directives, including the content pipeline the skills under test belong
  to, and the baseline would arrive carrying most of what the skill was supposed to add.
  Each arm gets an empty sandbox with the skill copied in.

Ported from the eval harness in [DreambigOu/ELI5](https://github.com/DreambigOu/ELI5) (MIT).
Mechanics, the scope rules, and how to add a case: `evals/README.md`.

**What the first run cost us to learn.** A naive forbidden-word check over the whole response
scored `de-ai` at -50 lift, worse than no skill at all, because the skill had produced a clean
rewrite *and* a triage table naming the fourteen AI tells it removed. Every cell tripped a
pattern. A skill whose job is to name a thing cannot be gated by a scan for that thing. Cases
now declare a `scope`, and the two rewrite cases score only a fenced `deliverable` block.
Generalising: **a deterministic check must target the artifact, not the reasoning that
produced it.** Any future suite over skill output will meet the same wall.

## Why the feedback channel matters more than the score

A pass/fail suite over 61 skills tells you *that* routing degraded. It does not tell you
which of two overlapping descriptions to edit - and the intuitive choice is usually wrong.
When skill B starts stealing skill A's requests, the instinct is to strengthen A. But A was
fine; B over-claimed. Padding A leaves both descriptions bloated, the collision intact, and
the next reviewer with no idea why either sentence is worded that way.

So `/skill-eval` classifies every miss by cause before proposing anything:

| Cause | Fix goes in |
|-------|-------------|
| Missing trigger - the description never mentions how people ask | the owning skill |
| Stolen trigger - another skill claims a phrase it does not own | the **other** skill |
| Overlapping scope - two skills genuinely cover the same job | a scope boundary, or a merge |
| Wrong expectation - the eval case is wrong, routing is right | `evals/routing.jsonl` |

That fourth row is not a face-saving option, it is the most common finding on a new suite.
Three of the first eight failures here were the suite being wrong, including one where
`measurement-agent` was expected to own "what counts as an MQL" - a definition that
`CLAUDE.md` assigns to `/preop-data-intelligence`. The eval caught a wrong belief about our
own routing table, which is exactly the value on offer.

## Cost discipline

Descriptions load on every session. A suite that "fixes" each failure by appending trigger
phrases converts a routing problem into a permanent context tax, and the tax compounds
silently across every conversation the repo touches.

Hence the budget in `/skill-eval`: a proposed description stays within ~20% of the current
length and ≤1024 characters. A description that must keep growing to route correctly is a
**scope** problem - the answer is a sharper boundary between two skills, or one skill
instead of two, not more words.

## What this layer does not claim

- **A green suite proves the cases pass, not that routing is correct.** The suite knows only
  what someone thought to write down. Treat `--coverage` gaps as unknowns, not as passes.
- **Tier 1 is a proxy.** It cannot stem, and it scores short requests noisily. Read it as
  "these descriptions share vocabulary", never as "this request will misroute".
- **Tiers 1 and 2 do not test skill bodies at all**, by design: an eval that reads bodies to
  decide routing measures the evaluator's reading comprehension instead of the router.
- **Tier 3 tests bodies, but only for text-in, text-out skills.** Whether
  `/nir-weekly-report` produces a correct document is still not measured, because a skill
  that reads monday or HubSpot cannot be run headless against live systems and give a
  repeatable answer. Until a fixture layer exists, correctness for those skills still comes
  from running them on real data, which is `references/agent-prompting.md` block 2 ("test
  each layer before adding the next") and the `/retro` loop.
- **Tier 3 lift is directional, not a benchmark.** Five cases, three skills, one run each,
  and the grading half is a model. Read the gap across the suite; do not read a single
  per-assertion verdict as a measurement.

## Extending the layer

The routing suite is the first eval because routing is the highest-traffic, lowest-visibility
surface. Two natural next suites, in value order:

1. **Output-contract conformance.** `/skill-eval`'s `contract` mode already scores a
   specialist reply against the five mandatory headings in
   `.claude/agents/OUTPUT_CONTRACT.md`. Turning that into a stored suite of
   reply→expected-verdict fixtures would make the specialist layer's return shape testable
   without a live run.
2. **Grounding conformance.** Given a reply and the snapshot it was handed, check that every
   number in the reply traces to the snapshot, and that anything else sits under
   `## Not verified`. This is the highest-value eval we do not yet have, because a fabricated
   metric in a report to a director is the most expensive failure in this repo - see
   `references/evidence-standards.md`.

3. **Output-invariant conformance, per skill.** The two suites above test shapes that every
   skill shares. This one tests what a *specific* skill must always do: `/chief-of-staff`
   surfaces overdue items when overdue items exist; `/nir-weekly-report` keeps its sections;
   a report that cites a figure carries its as-of date. Each invariant is one stored case
   against a frozen input, so a skill edit that quietly drops a section fails visibly instead
   of shipping.

   **Partly built: `evals/output_lift.jsonl` and tier 3 above.** Per-skill invariants are
   exactly what its `checks` express, and `critique` already has one (a `VERDICT:` line
   naming all six dimensions). What is still missing is the **frozen input**. Every case in
   the suite today is text-in, text-out, because a skill that reads monday or HubSpot cannot
   be run headless against live systems and get a repeatable answer. Covering
   `/chief-of-staff` or `/nir-weekly-report` needs a fixture layer that hands a skill a
   stored snapshot instead of a live connector. That is the next piece of work, and it is a
   prerequisite for suite 2 (grounding conformance) as well, since checking that every number
   traces to its snapshot requires having a snapshot to trace to.

All three follow the same rule as the routing suite: deterministic checks first, model calls
only for what deterministic checks cannot answer.

## The judge should not be the model under test

`/skill-eval` is model-in-the-loop, and today the grading agent runs on the same model as the
agent being graded. Same-model grading shares the blind spot it is supposed to catch: a
convention the model finds natural reads as correct to the grader for the same reason it read
as correct to the author. Where a suite needs a model call rather than a deterministic check,
**run the grader on a different model than the one under test.** This costs nothing structural
- it is a model parameter on the grading agent - and it is the cheapest available correction
for eval bias. Filed from the Lauren Tan agent workshop, 2026-08-29.

**Enforced in tier 3 since 2026-09-13.** `scripts/eval_output_lift.py --run` requires
`--subject-model` and `--grader-model` and exits rather than running when they match. A rule
that lives only in a document is a rule the next person skips; `/skill-eval` should take the
same parameter.
