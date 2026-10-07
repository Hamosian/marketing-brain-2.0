# Claim matching and the distinctiveness score

## Why the score is a formula

A subjective "this feels generic" grade cannot be compared across runs, so it
cannot show whether positioning improved. The formula below is arithmetic on the
bucket counts. Two runs on the same claim set and the same competitor roster
give the same number, and a change in the number means the copy changed.

## Prominence weight

Not every claim carries the same load. Weight each claim before scoring:

| Weight | Claim position |
|--------|----------------|
| 2 | Lead claim - the hero headline, the H1, the elevator pitch, the primary value proposition, the first thing on the page or in the deck |
| 1 | Supporting claim - a benefit bullet, a section subhead, a secondary proof point |

A generic hero costs far more than a generic bullet, and the weight is what makes
the score say so.

## Bucket burden

Each bucket contributes a fraction of its weight to the sameness burden:

| Bucket | Burden factor | Reasoning |
|--------|---------------|-----------|
| Shared | 1.0 | A competitor makes the same promise. It does nothing for a buyer choosing between us |
| Drifted | 0.7 | Nobody says it identically, but it reads as category boilerplate. Slightly better than shared, because the wording is at least ours to fix |
| Unclaimed but unproven | 0.3 | Nobody else makes it, but nothing backs it. It carries potential, not distinctiveness |
| Ownable | 0.0 | Nobody else can make it and something backs it. This is the whole point |

## The formula

```
burden  = SUM(weight * burden_factor) / SUM(weight)      across every claim
score   = round(10 - 9 * burden)                          clamped to 1..10
```

**Higher is better. 10 means fully distinct; 1 means indistinguishable.** Always
state the direction in the output line so nobody reads it backwards.

| Score | Read it as |
|-------|-----------|
| 9-10 | Distinct. A buyer could tell us apart from the copy alone |
| 7-8 | Mostly ours, with a soft edge or two |
| 5-6 | Half the message is category boilerplate. The lead claims are where to look |
| 3-4 | We sound like the category. A buyer gets no help choosing |
| 1-2 | Interchangeable with any competitor page |

Report the score to a whole number. Do not report a change smaller than 1 point
as movement; the claim-extraction step is not that precise.

## Matching rules

**Match on the promise, not the wording.** "Hours of editing, done in seconds"
and "cut your edit time by 90%" are the same claim. "Studio-quality results" and
"broadcast-quality output" are the same claim.

**The portability test decides Drifted.** Paste our sentence, unchanged, onto the
competitor's homepage. If it reads as true and native there and no reader would
notice the swap, it is drift - even if that competitor does not currently use
those words. Portability, not string overlap, is the test.

**A structural claim is not shared just because the words appear.** If a
competitor says "local recording" in a help article but cannot deliver it in the
product, that is not a competing claim. Only marketing claims on marketing pages
count. Note the distinction in the output when it comes up.

**When a claim splits, split it.** "End-to-end platform with studio-quality
results" is two claims and they usually land in different buckets. Splitting is
what surfaces the case where a strong claim is riding on a generic one.

**Cap the claim set.** 8-15 claims for a full positioning run, 5-10 for a single
page. Beyond that, matching gets mushy and the score stops meaning anything.
If the source has more, keep the highest-prominence ones and say how many were
set aside.

## Common findings, and what they usually mean

| Pattern | Usually means |
|---------|---------------|
| Every lead claim is Shared, supporting claims are Ownable | The differentiator exists but is buried. The fix is ordering, not new copy |
| High Drifted count, low Shared | Nobody has taken our position yet, but our language stopped signalling it. The fix is wording |
| Ownable claims all fail the evidence test | Positioning is running ahead of proof. Route to `/value-proposition-canvas` before writing more copy |
| Score improves but Ownable count is flat | Something got cut rather than sharpened. Check that a real claim did not go missing |

## Reproducibility

Record in the output, every run: the competitor roster, the fetch date, the claim
count, and the score. Without those four, a later run cannot tell whether the
copy improved or the method changed.
