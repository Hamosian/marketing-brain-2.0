<!-- last-reviewed: 2026-07-25 -->
# Evals

Behavioural tests for the Marketing OS. CI lints *structure* and `/health-check` audits
*staleness*; this directory is where we check the system does the right **thing**.

| File | Holds |
|------|-------|
| `routing.jsonl` | Routing suite: which skill should own a given request |
| `output_lift.jsonl` | Output-lift suite: whether the skill that fired beat no skill at all |

Two tiers read the routing suite:

```bash
python3 scripts/eval_routing.py              # deterministic, offline, runs in CI
python3 scripts/eval_routing.py --coverage   # also list skills with no case
/skill-eval                                  # model-in-the-loop, proposes description patches
```

The output-lift suite is offline by default and only calls models under `--run`:

```bash
python3 scripts/eval_output_lift.py          # structural checks, offline, runs in CI
python3 scripts/eval_output_lift.py --list   # the suite and what scores each case
python3 scripts/eval_output_lift.py --run \
    --subject-model claude-opus-5 --grader-model claude-sonnet-5
python3 scripts/test_eval_output_lift.py     # the harness's own tests
```

Design and rationale: `docs/skill-evals.md`.

## Adding a case

One JSON object per line in `routing.jsonl`. `//` comments and blank lines are ignored.

```json
{"request": "how it would actually be asked", "expect": "skill-name", "why": "the near-miss this guards"}
```

- **`request`** - phrase it the way a teammate would type it in Slack, not the way the
  skill's description is worded. A case that echoes the description tests nothing; the whole
  point is the gap between how people ask and how we wrote it down. In particular, don't
  write the routing rule into the request ("Rivermind couldn't answer this, so…") - that
  makes the case pass by construction and tests the phrasing rather than the routing.
- **`expect`** - the frontmatter `name:`, not the directory. The deterministic tier fails the
  build if it does not resolve, so a rename cannot orphan a case quietly.
- **`why`** - what wrong answer this case rules out. This is the field that makes a failure
  diagnosable in six months. `"guards against X"` beats `"tests routing"`.
- **`external: true`** - optional. Set it when the right target lives *outside* this repo,
  the way `/rivermind:ask` does. There is no local description to rank such a case against,
  so the deterministic tier carries it through unscored (verdict `external`) and only the
  model tier judges it. Without this escape hatch the repo's single most-trafficked routing
  directive - *every data question goes to Rivermind first* - would be the one rule the suite
  could not express.

```json
{"request": "what was our CAC by channel in Q2", "expect": "rivermind:ask", "external": true, "why": "..."}
```

Write cases where skills are **near-identical**. `/nir-weekly-report` vs
`/nir-monthly-report`, `/good-morning` vs `/chief-of-staff` vs `/mops-standup`,
`/pm-story` vs `/data-team-request`, the nine `*-copytemplates` skills: those are where
routing actually breaks. A case for a one-of-a-kind skill with unmistakable vocabulary
passes on day one and stays passing forever without ever having tested anything.

Add a case in the same PR as any new skill, and whenever you reword a description.

## Reading the output

| Verdict | Meaning |
|---------|---------|
| `clear` | The expected skill wins on vocabulary alone |
| `ambiguous` | It wins or places top-3, but a rival scores at or above it |
| `weak-trigger` | It ranks outside the top 3 - its description may not describe the job |
| `external` | Target is outside this repo, so it was not scored here - the model tier judges it |

**Warnings are expected, and a clean run is not the goal.** The deterministic tier scores
TF-IDF overlap between the request and each skill's `name` + `description`. That is a proxy
for what a router keys on, not a prediction of what Claude will do, which is why ambiguity
warns instead of failing. By default - which is how CI runs it - only structural problems
fail the build:

- a case expecting a skill that no longer exists
- a case that is not a JSON object, or whose `request`/`expect` is not a non-empty string
- a duplicate request
- `"external": true` on a skill that *does* exist locally, since that would silently drop it
  from scoring

`--strict` additionally fails on `ambiguous` and `weak-trigger`. Use it while deliberately
tightening descriptions; don't wire it into CI, or the proxy starts gating merges.

Two proxy artifacts to recognise before you go fixing a description:

- **No stemming.** "relate" does not match "relationships". A semantically obvious case can
  score 0 for purely lexical reasons.
- **Short requests score noisily.** Few tokens means a couple of shared terms dominate.
- **The corpus is shared, so adding a skill re-scores every case.** IDF is computed across
  all descriptions. A new skill that uses a common term lowers that term's weight for
  everyone, and a case you never touched can start warning because the incumbent's match
  depended on it. So compare the **whole warning set** against `main` rather than looking
  only for your own skill - `... | grep '::warning' | sort > new.txt`, same on a clean tree,
  then `diff`. An identical set is the real "no regressions" check.
- **The skill's `name` is scored too, not just the description.** A distinctive word in a
  hyphenated name (`are-we-really-different` contributes `really`) collides with any case
  whose phrasing happens to share it, and no amount of description editing removes it.
  Dropping the redundant literal trigger from the description halves that term's frequency,
  which is usually enough.

Both resolve at the `/skill-eval` tier, which reasons over meaning instead of counting
terms. Use the deterministic tier to find *where vocabulary collides* and the model tier to
decide whether it matters.

## The standing warnings

Nine cases warn on a clean tree as of 2026-07-25. Each is a real overlap the suite exists to
watch, not a defect to paper over:

| Case | Collides with | Why it stays |
|------|---------------|--------------|
| cognitive biases in pricing copy | `page-cro` | `/page-cro` and `/marketing-psychology` are *designed* to pair on page work |
| ad-hoc SQL over the attribution tables | `pm-story` | "write me" reads as story-writing to a term counter; the model tier separates them |
| what counts as an MQL | `nir-mql-live-report` | The daily digest owns the MQL vocabulary; the Pre-Op dictionary owns the definition |
| funnel performance, what moved | `nir-weekly-report` | Reporting a period vs diagnosing a movement |
| cross-domain spend/signup investigation | `paid-acquisition-agent` | The router must beat every specialist it would delegate to - the hardest routing call in the repo |
| demo bookers who never showed | `inbound-demo-reply` | CRM query vs outreach drafting over the same objects |
| newsletter copy for a launch | `page-cro` | Both own "copy"; surfaces differ. `content-agent`'s description now says page copy belongs to `/page-cro`, which is the boundary this case watches |
| map the marketing os file relationships | `marketing-brain` | Stem artifact plus a genuine name collision |
| onboard a new marketer to this repo | `access-welcome` | Human onboarding vs the automated access DM - a real boundary |

If this table and the run disagree, the run is right: reconcile the table, or fix what
changed. A *new* warning is the signal - it means the PR moved a boundary.


---

# The output-lift suite

Routing tests *which* skill fires. This suite tests whether the skill that fired produced a
better answer than the same model with no skill at all. Every case runs twice, once with the
skill body loaded and once bare, and both arms are scored against the same criteria. **The
number that matters is the gap, not the absolute pass rate.** A skill with zero lift is not
earning the context it costs.

Ported from the eval harness in [DreambigOu/ELI5](https://github.com/DreambigOu/ELI5) (MIT),
which is the clearest small implementation of the with-skill-vs-baseline pattern.

## Adding a case

One JSON object per line in `output_lift.jsonl`. `//` comments and blank lines are ignored.

```json
{"case": "ste-status-update-strips-slop", "skill": "ste", "prompt": "how a teammate would ask",
 "checks": {"forbidden": ["(?i)\\bleverag"], "max_sentence_words": 25, "scope": "deliverable"},
 "assertions": ["a criterion a grader can check against the text"],
 "why": "the wrong answer this case rules out"}
```

- **`case`** - lowercase, hyphens, digits. It becomes a directory under `evals/runs/`.
- **`skill`** - the frontmatter `name:`, not the directory. A rename that orphans a case
  fails the build rather than rotting.
- **`prompt`** - what a teammate would actually type. If the case uses
  `"scope": "deliverable"`, the prompt must also ask for the fenced block.
- **`checks`** - deterministic gates, scored offline with no model call. `required` and
  `forbidden` are regexes; `max_words` and `max_sentence_words` are prose ceilings with
  fenced code excluded. Optional.
- **`assertions`** - prose criteria a grader model scores PASS or FAIL with one line of
  evidence. Optional, but a case needs at least one of checks or assertions or it fails the
  build for scoring nothing.
- **`why`** - required. A failing case with no `why` is undiagnosable six months later.

### Pick the scope deliberately

`checks.scope` decides what a deterministic check measures, and getting it wrong is the
easiest way to build a suite that punishes a skill for working.

| Scope | Measures | Use when |
|-------|----------|----------|
| `response` (default) | everything the model returned | the whole reply is the deliverable |
| `unquoted` | the reply minus fenced code, backticks and quoted spans | the skill cites text it is judging |
| `deliverable` | only a ` ```deliverable ` fenced block | the skill's analysis legitimately names what the check forbids |

This is not theoretical. The first real run of this suite scored `de-ai` at **-50 lift**,
worse than no skill at all. The skill had done its job perfectly: it produced a clean rewrite
and then a triage table naming all fourteen AI tells it had removed. Every cell in that table
tripped a forbidden-word pattern. A de-slopping skill must not **use** the phrase; naming it
is the work. Rescoping those two cases to the deliverable block moved the same run from
+5.3 to +15.8.

## Only seed cases for text-in, text-out skills

A skill that writes to monday, posts to Slack, or stops at a human gate cannot be scored from
a headless one-shot. A case that pretends otherwise measures the harness, not the skill.
Today that limits the suite to the writing skills (`ste`, `de-ai`, `critique`); extending it
to the reporting skills needs a fixture layer that hands a skill a frozen snapshot instead of
live systems, which does not exist yet.

## How a run is isolated

Neither arm runs from the repo root. Run from here, both would load this repo's `CLAUDE.md`
and its always-on directives, including the content pipeline the skills under test belong to.
The baseline arm would arrive carrying most of what the skill was supposed to add, and the
measured lift would collapse toward zero for reasons that have nothing to do with the skill.

So each arm gets an empty temporary directory, and the skill under test is **copied in**
rather than read across the boundary. The very first run of this harness scored a whole case
on the model politely explaining that it could not open the file.

The grader gets a bare sandbox too: it must judge the text in front of it, with no skill body
and no repo conventions to pattern-match the expected answer against.

## Reading a run

`--run` writes to `evals/runs/lift-N/<case>/<arm>/`, which is gitignored. Model output is
live data; the repo keeps pointers, not copies. The committed artifact is the suite, not its
runs.

| File | Holds |
|------|-------|
| `response.md` | what that arm returned |
| `meta.json` | wall time, model, word count |
| `grading.json` | every check and assertion with its verdict and evidence |
| `grading_raw.txt` | the grader's unparsed reply, for when a verdict looks wrong |
| `summary.json` (run root) | pass counts, rates, the lift in points, and whether the run completed |

A failed model call (missing CLI, timeout, nonzero exit, empty output) writes no
`response.md` for that arm, and the harness exits non-zero. **The lift is withheld rather
than printed** whenever any arm failed, and `summary.json` records `"complete": false` with
the reasons. Two arms that answered different numbers of criteria cannot be subtracted, and
an empty response is not a neutral result: it passes every `forbidden` check, so a crashed
CLI would otherwise score an arm as *cleaner* than a working one.

## The grader is never the model under test

`--run` requires `--subject-model` and `--grader-model` and refuses when they match. Same-model
grading shares the blind spot it exists to catch: a convention the model finds natural reads
as correct to the grader for the same reason it read as correct to the author. This was filed
in `docs/skill-evals.md` from the Lauren Tan agent workshop on 2026-08-29 and went
unimplemented until this suite; here it is enforced rather than recommended.

Grading is still the noisy half. On the first clean run the grader returned two verdicts whose
own evidence contradicted them, and on an earlier run it emitted a duplicate verdict for one
assertion and none for another. The parser now indexes by the assertion number the grader
claims, keeps the first verdict per number, and **fails any assertion the grader never ruled
on** - an ungraded criterion is not a pass, it is one nobody demonstrated. Read a single
case's verdict as a signal, not a measurement; read the gap across the suite as the result.

## What this suite does not claim

- **It is not a benchmark.** Five cases across three skills, one run each. Treat a per-case
  lift as directional and a per-assertion verdict as noisy.
- **It does not test routing.** The with-skill arm names the skill file directly. Mixing the
  two would make a routing miss look like a quality regression.
- **A green structural check means the suite is well-formed, not that any skill is good.**
  Lift is only measured under `--run`, which is a deliberate manual step.
