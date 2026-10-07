<!-- last-reviewed: 2026-09-07 -->
# Evidence standards

How to handle numbers, sources, and disagreement between systems. Load this for any task that
puts a figure in front of a person - a report, a brief, a Slack digest, a recommendation.

**Use this when:** two sources disagree, a number can't be grounded, or you're about to
present a figure to someone who will act on it.

Adapted from the source-quality discipline in Anthropic's
[claude-cookbooks research-subagent prompt](https://github.com/anthropics/claude-cookbooks/blob/main/patterns/agents/prompts/research_subagent.md),
which requires an agent to flag weak
sourcing and surface conflicts to its lead rather than presenting everything it found as
established fact.

## Why this exists

`.claude/agents/OUTPUT_CONTRACT.md` already says claims must name their evidence and that
ungrounded ones go under `## Not verified`. That covers the *shape* of an honest answer. It
does not tell you what to do when **two systems both answer confidently and disagree** -
which, across Omni, HubSpot, Mixpanel, Snowflake, GSC, Ahrefs, and the ad platforms, is the
normal case rather than the exception.

The expensive failure in this repo is not a missing number. It is a confidently wrong number
in a report to a director, because a wrong number gets acted on and nobody re-derives it.

## Every figure carries a source and an as-of date

Not "signups were up 12%" but "signups up 12% (Omni, PLG funnel, 2026-07-01 to 07-24)". A
number without a source cannot be checked, and a number without a date silently becomes a
claim about today.

This applies hardest to numbers arriving second-hand: a figure quoted in a Slack thread, a
monthly report, or a `references/team-context/` digest is a **point-in-time snapshot**, not
live data. Re-pull it or label it with its original date. Presenting a stale number as
current is the same error as inventing one.

## Precedence when sources disagree

Grounded in what the repo already asserts - `CLAUDE.md` puts Rivermind first for data
questions because it is the analytics team's validated layer, and
`references/product/README.md` makes pricing verify-before-publish.

| Rank | Source | Use for |
|------|--------|---------|
| 1 | Rivermind (`/rivermind:ask`) | Any question it covers - validated by the analytics team |
| 2 | The system of record for that object | HubSpot for contacts/deals/Pre-Ops; monday for work state; Mixpanel for product behaviour; Omni/Snowflake for revenue and funnel |
| 3 | Platform-reported figures | Ad platforms for spend, impressions, and clicks - their own delivery |
| 4 | Third-party estimates | Ahrefs volumes, competitor traffic estimates - directional only, never quoted as fact |

Two rules that matter more than the ranking:

- **The ranking applies to definitions, not just figures.** "What counts as an MQL" is a
  Rivermind question exactly as much as "how many MQLs did we get". A wrong figure is usually
  visible; a wrong definition propagates silently into every number downstream of it, and into
  specs, pipelines, and commission logic built on top. Settle the definition before you count
  anything, and name where it came from.
- **Ad-platform conversions and revenue lose to the warehouse.** Each platform applies its
  own attribution window and view-through logic and counts conversions it can claim. Use
  platforms for what they deliver, the warehouse for what it earned.
- **Pricing, plan names, and beta availability are verify-before-publish** regardless of
  source, per `references/product/README.md`.

> **Open for the team:** rows 2-4 encode a defensible default, not a ratified policy. If
> Growth or the analytics team has a different order, fix it here and this becomes the
> single source of truth. Until then, say which row you applied so a reader can disagree.

## Work state: the board is not the system of record for "done"

Row 2 above says monday is the system of record for work state. That is true for **what work
exists, who owns it, and what it is for**. It is not true for **whether the work shipped**.

Delivery gets confirmed where the work happens - a Slack thread reply, a deploy message, a
production URL - and nobody walks back to move the board column afterwards. A status column
is only as fresh as the last person who remembered to update it, and on a contractor-executed
board that person is frequently nobody.

**So for any claim about whether something is done, live, fixed, or still open, the ordering
inverts:**

| Rank | Source | Why |
|------|--------|-----|
| 1 | The artefact itself | The live URL, the merged PR, the running workflow |
| 2 | The Slack thread where delivery was confirmed | Someone said "is live" and cc'd the requester |
| 3 | The monday item's **updates feed** | Written by a human at the time, dated |
| 4 | The monday **status column** | Trailing indicator, no freshness guarantee |

Verified 2026-08-23 on the Website Development board: five of six items sampled carried a
status that contradicted Slack. `Pricing Page Update_2026_08` (`12782422367`) read
`Ready for QA` six days after Davor deployed it to production and cc'd the board owner;
`fix video resizer page tab crash` (`12837916116`) read `QA` three days after the reporter
confirmed the fix in-thread. Board detail in `references/monday_boards.md`.

### Read the thread, not the channel surface

`slack_read_channel` and `slack_search_*` return **top-level messages only**. In this
workspace the ask is the top-level message and the answer is a reply, so a surface-only read
systematically returns questions without their resolutions. Every "unanswered", "still open",
or "nobody replied" claim is unsafe until the thread has been expanded.

- A result carrying `Thread: N replies` or a non-zero `Reply count` has content you have not
  read. Call `slack_read_thread` with its `channel_id` and `message_ts` before characterising it.
- The same applies on monday: the `Update Summary` text column is a **generated digest with
  its own staleness date**, not the item's updates. Use `get_updates` for what actually
  happened. On `12782422367` the digest was ten days behind the item.

The cheap version of this rule: **never report something as unanswered without having opened
the place an answer would live.**

## Never silently pick a winner

Choosing the number that fits the narrative and dropping the other is the failure mode this
page exists to prevent. When sources disagree:

1. **Report both**, with sources and dates.
2. **Say which you used and why** - precedence, freshness, or definitional fit.
3. **Name the likely cause of the delta** when you can: different attribution window,
   timezone, dedupe rule, a filter one source applies and the other doesn't.
4. **If the delta changes the recommendation, stop and say so.** Do not proceed on the
   convenient figure. A conflict that flips the decision is a finding, not a footnote.
5. **If you can't reconcile it, escalate it** - `## Open questions` for a specialist,
   explicitly for anything director-facing. Unreconciled is a legitimate answer; a
   false-precision average of two disagreeing systems is not.

## Signals a source is weaker than it looks

Check before quoting:

- **Forecast presented as actual.** "Could", "may", "on track to", future tense, a
  projection in a planning doc. State it as a projection, with whose.
- **Second-hand over primary.** A number in a Slack message, a deck, or a summary doc when
  the dashboard is one query away. Go to the dashboard.
- **Vendor or marketing framing.** A platform's own case study, a tool's blog post about its
  own effectiveness. Directional at best.
- **Nameless authority.** "The data shows", "we know that", "it's been proven" with no
  system, query, or owner named.
- **A definition that shifted.** The same metric name meaning different things across
  systems - MQL, activation, active user. **The analytics team owns the canonical
  definitions, so go through `/rivermind:ask` first.** `/preop-data-intelligence` is the
  HubSpot *field-level* view: correct for reading Pre-Op records directly, but it cannot
  express the era cutoffs and qualification gates the canonical models carry, so it will
  disagree with what the business reports. Treat a disagreement between the two as expected,
  not as evidence one is broken (verified 2026-07-29 on MQL/SQL - see
  `systems/owned/partnerstack.md`).
- **A definition you inferred yourself.** Reading columns, DDL, or distinct values to work out
  what a metric means produces something that looks canonical and is not. Schema tells you
  what is stored, never what the business counts. Ask instead.
- **A sample too small to carry the claim.** Percentages over a handful of records. Give the
  denominator or drop the percentage.
- **A status field nobody was required to update.** A monday status column, a "last synced"
  badge, a stage picker. It records the last time a human remembered, not the current state.
  For anything shipped-or-not, see *Work state* above.
- **A channel read that never opened a thread.** "Nobody replied" derived from a surface-only
  Slack read is an artefact of the retrieval, not a finding.

## A negative search is not evidence of absence

"X is missing" is a claim, and a grep that returned nothing is weak evidence for it. Before
reporting a gap, a break, or a thing that was never built, rule out the ways your own search
could have missed it:

- **Case.** HTML attributes and many config keys are not lowercase in the source. A
  case-sensitive grep for `hreflang` finds nothing on a page whose markup says `hrefLang`,
  and the honest-looking conclusion "this page has no alternates" is then simply false. On
  2026-09-23 that shipped as a confidently reported localization bug that did not exist.
- **Encoding and escaping.** `&amp;` for `&`, percent-encoding in URLs, and unicode
  look-alikes all defeat a literal match.
- **Scope.** The corpus may not contain what you searched. A sitemap crawl cannot find a page
  the sitemap omits; a repo grep cannot find a value set in a vendor console.
- **Whitespace and line breaks.** A pattern spanning a newline fails in line-oriented tools.

The cost is asymmetric. A false "it exists" is usually caught by the next step that tries to
use it; a false "it is missing" turns into a bug report, a ticket, or a design decision built
on nothing. So when the finding is an absence, **confirm it a second way** - a
case-insensitive pass, a different tool, or a positive control on a page you know does have
the thing - and say which check you ran.

## A restricted source does not become repo content just because you cite it

Filing a figure into the repo republishes it to everyone who can read the repo, and this one
serves the whole 32-person department. A report shared with four named people, summarized
into a skill's `knowledge/` file, is now readable by all of them - and it *loads on its own*
whenever someone asks a question in that domain. Nobody has to go looking for it.

Before filing anything sourced from a restricted artifact, ask who the source was shared
with. If that audience is narrower than the repo's, the aggregates come in and the
identifying detail stays out:

- **Names of individuals attached to a behaviour count.** "Zach 42, Joel 16" is a
  leaderboard whatever the surrounding caveats say. Log the shape instead - "top three hold
  69 of 93" - and point at the artifact for anyone who needs the breakdown.
- **Customer or record-level identifiers** used as examples. "One flip was reverted" carries
  the same information as naming the account.
- The pointer itself always stays, so the specifics are one click away for whoever is
  actually scoped to see them.

The concentration, the direction and the magnitude are the analytical content, and all three
survive the removal. What does not survive is the reading that a data-reliability finding is
a conduct finding - which is the exact misreading a named count invites, and the reason this
matters even when every caveat is present and correct.

**Ordinary work references are unaffected.** Who owns a ticket, who is in a thread, who sits
in which role - that is what `references/team.md` is for. The rule is about findings that
characterise how a named person behaved.

Filed 2026-09-07, after per-rep attribution-flip counts from a report scoped to named
readers reached three files in this repo. `/chief-of-staff` carries the operational form of
this rule as a key principle, since its daily state files are where the names entered.

## When you can't ground it

In order of preference:

1. **Pull the data.** If a system can answer it, ask the system.
2. **Say what's missing and request it** - `## Open questions`, naming the exact field or
   snapshot you need.
3. **Make the assumption explicit** - `## Not verified`, stating the assumed value and what
   it would take to confirm.

Never fill the gap with a plausible-looking number. A specialist subagent holds no live
access by design (`.claude/agents/README.md`), so for that layer this is absolute: numbers
arrive in the brief or they go under `## Not verified`.

## Related

- `.claude/agents/OUTPUT_CONTRACT.md` - where grounded claims, requests, and caveats go
- `references/agent-prompting.md` - grounding as a prompt constraint (block 3)
- `docs/skill-evals.md` - grounding conformance as a future eval suite
- `CLAUDE.md` - the Rivermind-first directive
- `references/integration-debugging.md` - the same discipline for diagnosing a failing third-party call
