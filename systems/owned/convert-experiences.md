<!-- last-reviewed: 2026-08-30 (created from the /home staging audience investigation - the missing exists/doesNotExist comparison operators) -->
# Convert Experiences (A/B Testing)

> The A/B and split-URL testing platform running site-wide on riverside.com. Loaded from a freeform `<head>` script block in Webflow (see `systems/owned/marketing-website.md`). This doc covers how to debug it from the page, how its audience rules are actually evaluated, and the failure modes that fail *silently*.

## Overview

Convert's tracking script ships the entire project config - every running experiment, its audience rules, site areas, variations, and the dictionaries that name them - into the page as `window.convert.data`. **You can diagnose almost any targeting problem from the browser without dashboard access.** That is the single most useful fact in this doc.

- **Account:** `10042201` · **Project:** `10042699`
- **Script:** `https://cdn-4.convertexperiments.com/js/10042201-10042699.js` (~342 KB, config baked in)
- **Tracking script version:** 1.5.2 as of 2026-08-30 (`release.type: "latest"`; previous 1.5.1)
- **Dashboard:** `https://app.convert.com/accounts/10042201/projects/10042699/`
- **Registered domains:** `riverside.com`, `stg.riverside.com`, `riverside.fm`, `riversidefm-design.webflow.io`, `riversidefm-design-com-domain-staging.webflow.io`

## Ownership

**Platform administration:** Marketing Operations (Jonathan Galili, 2026-09-23). Experiments are configured in the Convert dashboard, not in this repo.

**Usage is department-wide, not Growth-only.** Convert is the marketing department's A/B testing tool for riverside.com, and tests are run by teams across Abel's org - homepage tests are the clearest example, since the homepage is a shared surface rather than any one sub-org's. Treat a Convert question as a department-level request: the failure modes below are silent and identical no matter which team configured the test, so don't route it as a Growth-only concern.

## Debugging from the page

Run these in the console on any page where the test should be running.

| What you want | Where to look |
|---|---|
| Was this visitor bucketed? | `_conv_v` cookie. `exp:{}` = **not bucketed**. `exp:{1004146527.{v.1004346282-g.{...}}}` = in experiment `1004146527`, variation `1004346282` |
| Did the experiment execute on *this* pageview? | `convert.currentData.experiments` - empty means it did not run here |
| Is this a new bucketing or a repeat view? | `convert.currentData.experiments[<id>].first_time` (`false` = re-execution of an existing bucketing) |
| The experiment's config | `convert.data.experiments['<id>']` |
| What the audience rule actually says | `.t_ad_r` on that experiment (decode with the tables below) |
| What the Site Area actually matches | `convert.data.locations['<locId>']` |
| Visitor first-seen / session count | `_conv_v` fields: `fs` first seen, `sc` session count, `pv` pageviews |
| Did Convert forward an event to Segment? | A request to `api.segment.io/v1/**t**` (track). `/v1/p` is the site's own pageview and fires regardless |

`convert.getCookie(name)` returns **`null`** for an absent cookie - not `""`. This matters for comparison operators (below).

## Decoding an audience rule (`t_ad_r`)

The nesting is not self-evident. Verified against the minified rule processor:

```
t_ad_r[i].r        -> array of AND-groups   (OR between them)
  AND-group        -> array of OR-arrays    (AND between them)
    OR-array       -> array of conditions   (OR between them)
```

So `r: [[ [A], [B], [C] ]]` is `A AND B AND C`, while `r: [[ [A, B] ]]` is `A OR B`.

Each condition dispatches to `this["process" + entities[entid].nice_name]`, with the operator looked up as `comparisons[compid].module_name`.

| `entid` | Entity | | `compid` | Operator |
|---|---|---|---|---|
| 50 | `pageUrl1` | | 4 | `matches` |
| 51 | `useragent` | | 8 | `startsWith` |
| 52 | `testedVisitor` | | 10 | `equal` |
| 53 | `cookie` (name in `dn`) | | 13 | `exists` ⚠️ |
| 54 | `jscondition` (expression in `data`) | | 14 | `doesNotExist` ⚠️ |

## Ready-to-paste JavaScript conditions (Segment cookies)

Because `exists` / `doesNotExist` are unusable (issue 1 below), **every Segment-cookie test must be a JavaScript condition** - entity `54` (`jscondition`), operator `equal` (`10`).

Two mechanics to get right:

- Convert wraps your text as `convert.gEval = ( <your text> );`, so it must be a single **expression**, not statements. Wrap anything multi-line in an IIFE.
- The condition's own **NOT toggle also inverts the result** (`processJscondition` applies `b.not`). Invert in the JavaScript *or* with the toggle - never both.

### `ajs_user_id` - is this browser a known, identified Riverside user?

Written by Segment on `analytics.identify()`. Persistent (~1 year) and scoped to `.riverside.com`, which the marketing site can read (verified) - so it survives across sessions and is already in `document.cookie` when Convert evaluates. **This is the correct signal for "already a Riverside user."**

**Not** an identified user - anonymous visitor (this is the "exclude existing Riverside users" case):

```js
!/(^|;\s*)ajs_user_id=[^;\s]/.test(document.cookie)
```

**Is** an identified user:

```js
/(^|;\s*)ajs_user_id=[^;\s]/.test(document.cookie)
```

### `ajs_anonymous_id` - has Segment ever run in this browser?

Written by Segment on load for **every** visitor, identified or not. It carries no information about who someone is - only whether Segment has executed here before. It is a **UUID v4**, so it encodes no timestamp (see "Cookie age" below).

Segment has **never** run here (see the warning below before using this as "new visitor"):

```js
!/(^|;\s*)ajs_anonymous_id=[^;\s]/.test(document.cookie)
```

Segment **has** run here before:

```js
/(^|;\s*)ajs_anonymous_id=[^;\s]/.test(document.cookie)
```

### What these actually mean - read before using `ajs_anonymous_id`

**`ajs_anonymous_id` absent does NOT mean "new visitor."** Because Convert evaluates before Segment loads (issue 6), the cookie is absent only on a visitor's **first pageview on the domain**. A genuinely new visitor who lands on `/blog` and then navigates to the test page already has it, and will be excluded. Gating a test on it therefore recruits only visitors whose **entry page is the test page** - a real population, but skewed to direct/brand traffic, and it must be reported as such rather than as "new visitors". Verified 2026-08-30.

**Both cookies only hold at the moment of bucketing** (issue 5). A visitor who is anonymous when bucketed and logs in later stays in the test permanently.

**Ad-blocked / consent-blocked visitors never get either cookie**, so they read as "anonymous" and "never seen" on every visit.

### Why `[^;\s]` rather than just `=`

Requiring at least one value character makes an **empty** cookie (`ajs_user_id=;`) read as *not identified*, which is the correct interpretation. Verified against the edge cases - both forms correctly reject decoy names such as `my_ajs_user_id` and `ajs_user_id_bak`, and both tolerate a missing space after the semicolon; they diverge **only** on the empty-value case. The simpler `/(^|;\s*)ajs_user_id=/` is what was validated live in Convert (it behaved identically there, because the cookie was fully absent); the `[^;\s]` form is the safer default.

## Known Issues / Failure Modes

### 1. `exists` and `doesNotExist` are declared but NOT implemented (silent, total)

The config dictionary declares operators 13 (`exists`) and 14 (`doesNotExist`), but **neither is defined in the tracking script**. Every other operator exists on `E.a.J`; these two do not. `processCookie` calls `this.A[module_name](...)` on `undefined`, which throws.

**Any Cookie condition using "exists" / "does not exist" evaluates to false and the whole audience never qualifies.** No error, no Live Logs entry, nothing - indistinguishable from "no visitors matched."

Confirmed 2026-08-30 by a controlled test: same entity, same present cookie, only the operator varied - `exists` did not bucket, `equal` did. Reported to Convert support.

**Workaround:** express it as a JavaScript condition (entity 54), which is implemented and has its own internal error handling. Copy-paste conditions for both Segment cookies, in both directions, are in "Ready-to-paste JavaScript conditions" above.

Do **not** substitute "Cookie equals empty value" - `getCookie` returns `null`, `equal` is loose `==`, and `null == ""` is false. "Cookie contains ''" short-circuits to always-true.

### 2. A throwing condition silently evaluates to FALSE

The AND evaluator wraps each condition in `try { ... } catch(f) { return n }`. Any exception anywhere in a condition quietly fails the entire audience. This is the mechanism behind issue 1 and makes every targeting bug look like "nobody matched." **When an audience mysteriously matches nobody, suspect a throwing condition before suspecting the logic.**

### 3. `testedVisitor` throws on stale experiment IDs

`processTestedVisitor` dereferences `data.experiments[e].tp` for every experiment ID in the visitor's `_conv_v`. A visitor holding an ID for a since-deleted experiment throws → issue 2 → audience false. Returning visitors quietly stop qualifying for any audience containing a "tested visitor" condition.

### 4. Site Area `matches` is exact string equality

Operator 4 is `b === c` after lowercasing (trailing slashes stripped, query strings **not**). `https://riverside.com/home?utm_source=x` does **not** match a Site Area of `https://riverside.com/home`. Use `startsWith` (8) or `regeMatches` (5) for anything that must catch UTM or `gclid` traffic.

### 5. The audience is an ENTRY gate only - it is never re-evaluated

Once a visitor is in `_conv_v`, Convert re-executes the experience and re-fires the Segment event on every subsequent qualifying pageview **without re-checking the audience**. This is correct sticky-bucketing behaviour (a visitor must keep seeing the same variation), but it means:

- Seeing the Convert→Segment event fire in a new tab for an already-bucketed visitor is **expected**, not a leak. Check `first_time: false` to confirm.
- Any audience expressing a *mutable* property ("not logged in", "new visitor") only holds **at the moment of bucketing**. A visitor who logs in mid-test stays in the test permanently.

### 6. Convert evaluates BEFORE Segment/GA/HubSpot load

Measured on a cold load of `stg.riverside.com/home` (2026-08-30): Convert executes at **~405 ms**, Segment's `analytics.min.js` at **~490 ms**. Convert is a synchronous `<head>` script; the analytics vendors are async.

Consequence: **any audience condition reading a vendor-written cookie sees "absent" on a visitor's first-ever pageview.** For persistent cookies this is usually harmless (returning visitors carry them from the previous session), but it means a condition like "`ajs_anonymous_id` does not exist" is true *only on the first pageview on the domain* - so a test gated on it recruits only visitors whose **entry page** is the test page. Verified: a first-session visitor who had already viewed another page was not bucketed.

If a condition must wait for an async value, Convert supports `convert_recheck_experiment()` inside a JS condition (it rewrites to `convert.executeExperimentLooped('<id>')`). Avoid it on split-URL tests - deferring the decision produces a visible flash of the original before redirect.

### 7. `gdprw: true` is a reporting flag, not a consent gate

`prj.extset.gdprw` appears exactly once in the whole bundle - in the config JSON. It is never referenced by runtime logic. Do not diagnose a non-firing experiment as a consent problem on the strength of this flag. (The site's actual consent tool is CookieHub; `dnt: "1"` *is* honoured, checked against `navigator.doNotTrack`.)

### 8. Split-URL `$N` capture tokens can leak into the variation URL

A `variation_pattern` such as `https://stg.riverside.com/lp/home?$3` emits the literal token when the capture group is empty-but-present. Currently masked because the exact-match Site Area (issue 4) only ever admits the bare URL, so `$3` resolves empty and the trailing `?` normalises away. **Broadening the Site Area to catch UTM traffic will un-mask this.** Fix both together or neither.

## Testing an audience rule without touching the dashboard

`convert.checkExperiments()` is guarded and will **not** re-evaluate after page load, so mutating `convert.data` post-load proves nothing. To actually test a rule change, patch the config inside the script text and boot a fresh instance:

```js
const t = await fetch('https://cdn-4.convertexperiments.com/js/10042201-10042699.js').then(r => r.text());
const start = t.indexOf('"t_ad_r":'), end = t.indexOf(',"locs":["<locId>"]', start);
const patched = t.slice(0, start) + '"t_ad_r":' + JSON.stringify(newRule) + t.slice(end);
// clear _conv_v first, then:
delete window.convert; window.convert_temp = {};
(0, eval)(patched);
// read the _conv_v cookie for the verdict - it survives the redirect a variation may trigger
```

Always run a **control** alongside the change (a rule you expect to pass and one you expect to fail). A rule that fails for the reason you assumed and a rule that fails for an unrelated reason look identical from `exp:{}`.

**This writes real visitors into the experiment's data.** Only do it on a staging/test experience, and reset the experiment's data afterwards.

## Cookie "age" - what is and is not available

JavaScript cannot read a cookie's age. `document.cookie` exposes only `name=value`; creation time, `Expires`/`Max-Age`, domain and path are invisible to script.

- **`ajs_anonymous_id` is a UUID v4** - purely random, no embedded timestamp. Segment's localStorage entries hold only the raw ID. **Segment cannot answer "how old is this visitor."**
- Cookies that *do* encode a first-seen timestamp, all present on riverside.com:

| Cookie | Format | Gives you |
|---|---|---|
| `_ga` | `GA1.1.<random>.<unixSeconds>` | first-seen timestamp |
| `__hstc` | `hash.utk.<firstVisit>.<prevVisit>.<currVisit>.<sessionNumber>` | first visit **and session number** (`=== 1` means first session) |
| `_fbp` | `fb.1.<unixMillis>.<random>` | creation timestamp |

All are subject to issue 6 (absent on the very first pageview - treat absent as "new") and to ad-blocking, which differs per vendor and skews the cohort.

The race-free option is a first-party cookie written synchronously in `<head>` **before** the Convert script - but note `marketing-website.md`'s hard head-ordering rule: the referrer/UTM-preservation script must run first.

## Related Systems

- `systems/owned/marketing-website.md` - where the Convert script is installed (freeform head code) and the `<head>` ordering constraint
- Segment/analytics wiring is shared with the Next.js app; see the Convert→Segment forwarding note in issue 5

## Pointers

- Experiment summary: `https://app.convert.com/accounts/10042201/projects/10042699/experiences/<experienceId>/summary`
- Live Logs are server-side and only show visitors Convert actually bucketed - a silently-failing audience (issues 1-3) produces an **empty** log, not an error
