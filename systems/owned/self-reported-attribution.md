<!-- last-reviewed: 2026-07-14 -->
# Self-Reported Attribution - Merged "How Did You Hear About Us?" Field

> Design spec for one derived HubSpot Contact field that merges Riverside's two independent self-reported "How did you hear about us?" sources - the onboarding quick-click and the considered answer given on a sales call - into a single canonical channel. The existing enterprise-form channel is folded in as an optional third feeder so the whole org converges on one taxonomy. **This is a design/build spec, not a live system yet.** No fields have been created; nothing writes to production. Portal `9154210`. Grounded on live property inspection 2026-07-14.

## Purpose

Riverside asks "How did you hear about us?" in two places that never get combined:

1. **Onboarding (self-serve)** - the answer users click right after sign-up. Lives on the Contact as `onboarding__how_did_you_hear_about_us_`. **519,742 contacts populated** - by far the highest-volume attribution signal we own.
2. **Post-meeting (sales)** - the answer a prospect gives on the intro/sales call, captured only in **Gong** transcripts and call notes. **Not a structured HubSpot property today.**

Because these live independently, neither gives a full read on self-reported attribution. Self-serve users usually skip the sales motion; sales-led contacts may never complete onboarding - so the two datasets are **largely complementary, not duplicative**. The overlap (a self-serve user who later takes a sales call) is small but high-value, and it's the only place the two can disagree.

Self-reported attribution matters at Riverside specifically because **click-based source is broken for PLG**: product events sync back into HubSpot and overwrite the Contact `Last Touch Source` (see `hubspot.md` → Known Issues). Self-report is independent of that corrupted signal and captures word-of-mouth / podcast / "guest on Riverside" / organic-YouTube discovery that leaves no click. It **complements, never replaces** UTM/click attribution.

## Two corrections to the original brief (read first)

**1. `onboarding_questions_acquisition_sources` is a persona field, not a channel field - do not merge it.** The brief flagged it as a "related field to check," and both its label ("Onboarding Questions Acquisition Sources") and its HubSpot description ("Where the user heard about Riverside as answered after sign up") imply it's a channel. It is not. Its 971,524 populated values are a **persona/segment** dimension: *Part time creator, Business owner, Small to mid-size company, Full time creator, Freelancer, Agency, Personal project, Large company, Non-profit, Other*. Feeding it into a channel merge would corrupt the taxonomy (e.g. "Agency" as a persona colliding with the free-text referral "through our podcast agency," which is a *mechanism*). It is **blocklisted by name** from the merge and routed to a separate persona track. A rename + description fix is filed (§J) so no future workflow re-wires it.

> **Status 2026-09-23: the field is frozen for new signups, and the rename never shipped.** Onboarding switched from the persona question to a use-case question in Nov 2024. Since then only about 145 new contacts a month get a value (551 created 2026-06-01 to 2026-09-23), against about 19K a month in Aug 2024. The sister field `onboarding__what_best_describes_you_` froze at the same time. `onboarding_persona_segment` does not exist in the portal, and the HubSpot description still says "Where the user heard about Riverside". The live onboarding signal is `onboarding_questions_intent` (use case). It is free text in bare and JSON-array formats, so match it with "contains". Any segment keyed on the persona fields covers signups up to Oct 2024 only. The R4B Target Audience list (`24578`) is a live consumer of both persona fields: check it before any rename. Detail: `systems/owned/hubspot.md` -> "Building audience lists".

**2. The onboarding channel field stores picks as a JSON-array *string*.** `onboarding__how_did_you_hear_about_us_` stores a selection as the literal string `["Word of mouth"]` - the brackets and quotes are part of the stored value - while free-text "Other" answers are stored as **bare strings** (no brackets). A naive HubSpot workflow equality check against `Word of mouth` matches **zero rows**. Parsing must strict-parse the JSON array **and** handle bare text. This is the single biggest reason the merge must run in code, not in an if/then workflow.

**Watch item (not a blocker):** "Word of mouth" is **36%** of the onboarding sample - implausibly high for a single quick click, i.e. a default/first-option bias artifact. The waterfall treats the onboarding WOM *picklist default* as low-trust; a product fix for the widget is in §J.

## Architecture

```
SOURCE A: onboarding__how_did_you_hear_about_us_   (Contact, 519K, JSON-array string + free-text tail)
SOURCE B: Gong transcript / call notes            (unstructured -> must be structured first, §I)
SOURCE C: enterprise_form_attribution_channel     (existing categorized field, folded in as 3rd feeder)

   A ─ Ops Hub custom-coded action ─► sr_attribution_onboarding_channel (+conf, +raw)
                                          │
   B ─ Gong Smart Tracker ─► Snowflake LLM classify ─► shared normalizer ─► Hightouch
          │                                                                     │
          ├─► Pre-Op sr_attribution_gong_* (per-call, rep-facing, pointer only) │
          └─► Contact sr_attribution_salescall_* (winning call rollup) ◄─────────┘
                                          │
   C ─ (already normalized) ──────────────┤
                                          ▼
                       Ops Hub merge action - confidence-gated waterfall (§E)
                                          │
                                          ▼
              sr_attribution_channel  (THE merged canonical value)
              + rollup, source, confidence, raw, secondary(+json),
                conflict, default_suspect, normalizer_version, signature
                                          │
                                          ▼
              Pre-Op mirror (read-only) for /preop-data-intelligence reporting
```

Every value is **derived**; both original source fields stay fully intact (§H.5). The merge is a pure function of its inputs and re-derivable at any time.

## Merged field definition

| | |
|---|---|
| **API name** | `sr_attribution_channel` |
| **Label** | Self-Reported Attribution Channel |
| **Object** | Contact (mirrored read-only to Pre-Op) |
| **Type** | enumeration (22 canonical values, §C.1) |
| **Meaning** | The single best canonical read of how this person says they found Riverside, merged across onboarding + sales-call + enterprise-form self-report, chosen by a confidence-gated priority waterfall. |
| **Namespace** | All new properties use the `sr_attribution_*` prefix; labels carry "Self-Reported Attribution …". |

Confidence is stored everywhere as a **`number` 0.00-1.00** with fixed bands: **High ≥ 0.80 · Medium 0.50-0.79 · Low < 0.50**.

## Field inventory

### Sources - left intact, read-only (never written by this system)

| Field / source | Object | Type | Role |
|---|---|---|---|
| `onboarding__how_did_you_hear_about_us_` | Contact | string | Source A raw (519,742 populated). |
| Gong transcripts + call notes | Gong / Snowflake | - | Source B raw (§I). |
| `enterprise_form_attribution_channel` | Contact | enumeration | Existing categorized precedent; reused **as-is** as a 3rd feeder. |
| `how_did_they_hear_about_us__enterprise_form_` | Contact | string | Raw behind the enterprise field. |
| `how_did_they_hear_about_us`, `how_did_they_hear_about_us_` | Contact | enumeration | Legacy fragmented enums. Not fed in; flagged for deprecation (§J). |
| `onboarding_questions_acquisition_sources` | Contact | string | **Persona, not channel. Blocklisted** (correction 1). |

### Per-source normalized feeders - CREATE (Contact)

| API name | Type | Written by | Purpose |
|---|---|---|---|
| `sr_attribution_onboarding_channel` | enumeration | Ops Hub action | Normalized onboarding channel |
| `sr_attribution_onboarding_channel_raw` | multi-line text | Ops Hub action | JSON-stripped pick or bare free text - the contact's own answer, kept for in-portal re-normalization |
| `sr_attribution_onboarding_confidence` | number (0-1) | Ops Hub action | Per-source confidence |
| `sr_attribution_onboarding_default_suspect` | bool | Ops Hub action | True **only** when the raw pick is the picklist default `["Word of mouth"]` (see fix in §D/§E) |
| `sr_attribution_salescall_channel` | enumeration | Hightouch | Winning Gong call's canonical channel (contact-level rollup) |
| `sr_attribution_salescall_confidence` | number (0-1) | Hightouch | LLM extraction confidence of the winning call |
| `sr_attribution_salescall_call_date` | datetime | Hightouch | Winning call date (recency tie-break) |
| `sr_attribution_salescall_call_url` | single-line text | Hightouch | Pointer/drill-back to the winning call (audit; **no verbatim quote in HubSpot**, §F/PII) |
| `sr_attribution_salescall_synced_at` | datetime | Hightouch - **written LAST** | Barrier field: keys re-enrollment + idempotency so the merge never reads a half-written Gong payload (**blocker fix**, §H) |
| `enterprise_form_attribution_confidence` *(optional)* | number (0-1) | its workflow | Defaults to **0.80** (already human-categorized) if the workflow can't emit one |

### Merged canonical + audit fields - CREATE (Contact)

| API name | Type | Purpose |
|---|---|---|
| `sr_attribution_channel` | enumeration (22) | **The merged self-reported channel.** |
| `sr_attribution_channel_rollup` | enumeration | Stored reporting rollup (§C.2); each of Guest/Blog/Event/Email/Not-Sure gets its **own** rollup value, not folded into Other. |
| `sr_attribution_source` | enum: `onboarding` / `sales_call` / `enterprise_form` / `reconciled` / `none` | Winning source / provenance |
| `sr_attribution_confidence` | number (0-1) | Confidence of the winning value |
| `sr_attribution_raw` | multi-line text (**sensitive, TTL**) | Raw winning text for onboarding/enterprise winners; for a sales-call winner this holds the call **pointer**, not the verbatim quote (§F/PII). Enables re-normalization. |
| `sr_attribution_secondary_channel` | enumeration | Highest-confidence **losing** value (fast filter for the overlap segment) |
| `sr_attribution_secondary_source` | enum (source enum) | Source of that secondary |
| `sr_attribution_secondary_json` | multi-line text | **Every** losing `(source, channel, confidence)` tuple, JSON-serialized - so a 3-way disagreement drops nothing (§F). |
| `sr_attribution_conflict` | bool | True when ≥2 *specific* sources disagree at the **rollup** level (§F) |
| `sr_attribution_computed_at` | datetime | Last actual write |
| `sr_attribution_normalizer_version` | number (int) | Synonym-map version used - key to re-normalization (§H.4) |
| `sr_attribution_input_signature` | single-line text | Idempotency hash (§H.2) |

### Gong per-call fields - CREATE (Pre-Op / Deal), rep-facing mirror

The warehouse is source of truth; these give reps drill-back and a place to correct. **Pointer, not transcript** - no verbatim prospect speech is copied into HubSpot by default (§F/PII).

| API name | Type | Purpose |
|---|---|---|
| `sr_attribution_gong_channel` | enumeration | Classified channel for this call |
| `sr_attribution_gong_confidence` | number (0-1) | Extraction confidence |
| `sr_attribution_gong_captured_at` | datetime | Call date |
| `sr_attribution_gong_call_id` | single-line text | Gong reference |
| `sr_attribution_gong_call_url` | single-line text | Deep link to the call moment (drill-back to hear the quote in Gong) |
| `sr_attribution_gong_method` | enum: `ai_classified` / `rep_entered` / `not_detected` | Primary vs fallback provenance |

### Other CREATE

| API name | Object | Type | Purpose |
|---|---|---|---|
| `sr_attribution_channel` (mirror) | Pre-Op | enumeration | Read-only copy of the merged value for deal-level reporting via `/preop-data-intelligence` |
| `sr_attribution_source` (mirror) | Pre-Op | enumeration | Mirror of the source indicator |
| `onboarding_persona_segment` | Contact | enumeration | Normalized home for the mis-named persona field's values - a separate track that never touches the channel merge |

## C. Canonical picklist + reporting rollup

**Granularity decision: store the granular value, roll up to enterprise for reporting.** The source captures LinkedIn/Facebook/Instagram/X/TikTok/Reddit and Blog/Event/Email as clean first-class picks with real counts; collapsing them at store time throws away structured signal the field exists to preserve. "Converge, don't fork" is honored by a **mandatory rollup** to the existing `enterprise_form_attribution_channel` groups, so weekly reporting reconciles.

### C.1 The 22 canonical values (internal value → label → rollup)

| # | Internal value | Label | Rollup group |
|---|---|---|---|
| 1 | `word_of_mouth_referral` | Word of Mouth / Referral | Word of Mouth / Referral |
| 2 | `search` | Search | Search |
| 3 | `youtube` | YouTube | YouTube |
| 4 | `podcast_community` | Podcast Community | Podcast Community |
| 5 | `guest_on_riverside` | Guest on Riverside | **Guest on Riverside (PLG)** *(standalone)* |
| 6 | `existing_returning_user` | Existing / Returning User | Existing User |
| 7 | `linkedin` | LinkedIn | Social Media |
| 8 | `facebook` | Facebook | Social Media |
| 9 | `instagram` | Instagram | Social Media |
| 10 | `tiktok` | TikTok | Social Media |
| 11 | `x_twitter` | X / Twitter | Social Media |
| 12 | `reddit` | Reddit | Social Media |
| 13 | `social_media` | Social Media (unspecified) | Social Media |
| 14 | `blog_content` | Blog / Content | **Blog / Content** *(standalone)* |
| 15 | `event_conference` | Event / Conference | **Event / Conference** *(standalone)* |
| 16 | `email_owned` | Email (Owned) | **Email (Owned)** *(standalone)* |
| 17 | `paid_ads` | Paid Ads | Paid Ads |
| 18 | `ai_tools` | LLMs | AI Tools (LLMs) |
| 19 | `internal_work` | Internal / Work | Internal / Work |
| 20 | `not_sure` | Not Sure / Don't Remember | **Not Sure** *(own line; see §G)* |
| 21 | `other` | Other | Other |
| 22 | `test_junk` | Test / Junk | Test / Junk |

`guest_on_riverside` is a first-class Riverside PLG/viral channel (~10% of self-serve; recorded as a guest → signs up) with no home in the enterprise taxonomy. It gets its **own rollup value now** - never buried inside Other.

### C.2 Rollup semantics and reconciliation

- **Direct rollups** to existing enterprise groups: WOM/Referral, Search, YouTube, Podcast Community, Existing User, Paid Ads, AI Tools (LLMs), Internal / Work, Other, Test / Junk. The seven social values (7-13) collapse to **Social Media**.
- **Five values keep their own standalone rollup line** rather than folding into Other: `guest_on_riverside`, `blog_content`, `event_conference`, `email_owned`, and `not_sure`. (This is a deliberate fix: folding them into Other would make the flagship PLG "Guest on Riverside" channel invisible in the natural reporting dimension.)
- **`not_sure`** is excluded from **both** the known-channel denominator **and** the Other bucket - it's a *known non-answer*, counted separately so you can measure how often the question fails to elicit signal.
- **Reconciliation identity** (state it explicitly so numbers tie out):
  `self-report total = Σ(enterprise groups) + Guest + Blog + Event + Email + Not-Sure + null`.
- Row-level reconciliation against `enterprise_form_attribution_channel` is only meaningful over the **sub-population that carries an enterprise-form value** - the 519K onboarding contacts mostly have none, so this is *taxonomy convergence*, not whole-base row reconciliation. The permanent fix (add four enterprise groups, §J) turns the five standalone rollups into direct ones.

## D. Normalization (synonym → canonical, grounded in observed values)

**Parse first (strict).** Treat a value as a picklist array **only** when it strict-`JSON.parse`s to a `string[]` (anchored `^\[".*"\]$`). Then: take the element(s), lowercase, collapse internal whitespace, strip surrounding quotes and trailing punctuation (`.…!?,;:`). Explicit edge cases (unit-tested, §I rollout):
- `[]`, `[""]`, blank, whitespace-only → **null** (`source = none`) - *not* `other`.
- A bare string that merely *contains* brackets (e.g. `saw it on [a podcast]`) is **free text**, not an array - do not strip its content.
- A multi-value array (defensive; not seen in the sample): map each element, drop Other/Not-Sure/Junk, keep the highest-precedence specific channel as primary and serialize the rest into `sr_attribution_secondary_json`.

**Deterministic picklist picks use a static crosswalk** (fast, free, exact) inside the Ops Hub action. **Only the bare free-text tail and Gong quotes need fuzzy/LLM classification, and that runs in the warehouse in batch - never as a synchronous per-record API call inside the Ops Hub action** (see §H.3; this is the 519K-scale fix). Unmatched free text lands as `other` + flagged; a warehouse batch pass proposes new crosswalk entries for human review → next `normalizer_version`.

### D.1 Observed onboarding picklist values → canonical

| Raw stored value (count) | Canonical | Confidence |
|---|---|---|
| `["Word of mouth"]` (72) | `word_of_mouth_referral` | **0.50 - picklist default; sets `..._default_suspect = true`** |
| `["Google"]` (34) | `search` | 0.80 |
| `["Youtube"]` (24) | `youtube` | 0.80 |
| `["Guest on Riverside"]` (19) | `guest_on_riverside` | 0.80 |
| `["Returning customer"]` (14) | `existing_returning_user` | 0.80 |
| `["LinkedIn"]` (4) | `linkedin` | 0.80 |
| `["Facebook"]` (3) | `facebook` | 0.80 |
| `["Blog post"]` (3) | `blog_content` | 0.80 |
| `["Event"]` (3) | `event_conference` | 0.80 |
| `["Reddit"]` (3) | `reddit` | 0.80 |
| `["Instagram"]` (3) | `instagram` | 0.80 |
| `["Email"]` (2) | `email_owned` | 0.80 |
| `["TikTok"]` (1) | `tiktok` | 0.80 |
| `["Twitter"]` (1) | `x_twitter` | 0.80 |

**Default-suspect is set only for the picklist default `["Word of mouth"]`** - not for the canonical WOM category in general. Free-text WOM (below) keeps its real confidence and is *not* stamped suspect. This is deliberate: a lazy default click and a typed-out referral must not be discounted identically.

### D.2 Observed free-text "Other" tail (every verbatim value) → canonical

| Verbatim free text | Canonical | Confidence / note |
|---|---|---|
| "Spotify" (5) / "spotify" (1) | `podcast_community` | 0.70 - case-folds to one key; dupe merged |
| "Podcast" | `podcast_community` | 0.70 |
| "Podcast (marketing against the grain)" | `podcast_community` | 0.70 - named show |
| "Anchor" | `podcast_community` | 0.70 - podcast hosting platform |
| "A friend" | `word_of_mouth_referral` | 0.70 - *not* default_suspect |
| "Friend uses you for his podcast" | `word_of_mouth_referral` | 0.70 - the friend is the channel |
| "Through our podcast agency" | `word_of_mouth_referral` | 0.40 - partner/agency referral; **candidate future "Partner / Agency"** |
| "Stephen Robles: the man, the myth, the legend…" | `word_of_mouth_referral` | 0.40 - a real followed creator; jokey ≠ junk; **candidate future "Creator / Influencer"** |
| "Don't remember. I know a bunch of other people use you." | `not_sure` | explicit non-recall wins over the faint WOM hint |

### D.3 Forward-looking synonyms (not in sample; for the warehouse fuzzy/LLM layer)

`googled / search engine → search` · `google ad / your ad / saw an ad → paid_ads` · `yt → youtube` · `x / tweet → x_twitter` · `ig → instagram` · `referral / recommended by a friend / colleague → word_of_mouth_referral` · `chatgpt / claude / gemini / perplexity / llm / ai → ai_tools` · `newsletter → email_owned` · `conference / meetup / webinar / trade show → event_conference` · `at work / my company uses it / coworker → internal_work` · `saw it online on social → social_media` · `idk / not sure / n/a / no idea / can't remember → not_sure` · `test / asdf / punctuation-only → test_junk`.

## E. Source-priority waterfall

**Core decision: a confidence-gated waterfall - the considered answer does NOT automatically win.** A lossy rep paraphrase extracted at Medium confidence must not overturn a fresh, clean, specific onboarding pick - but the disagreement is recorded. We reject the blunt "Gong always wins."

**Reasoning behind the shape:**
- Onboarding is *fresher* (captured at signup, closest to the discovery moment) but individually *noisy* (36% default WOM). The considered answer is *later* (memory-decay risk) but *deliberate* and can be probed by the rep. Freshness of a default click is worthless - so we gate on **confidence and specificity**, not recency.
- A channel named unprompted in a considered sales conversation is the gold standard of self-report and is immune to the onboarding default bias - so a **High**, specific considered answer beats even a clean onboarding pick.
- But a **Medium** paraphrase must *not* overturn a clean, specific, non-default onboarding value - it only wins when onboarding is untrustworthy. Disagreements are flagged either way.

**Definitions:**
- `specific(x)` = `x.channel ∉ {other, not_sure, test_junk, null}`.
- `onb_untrustworthy` = `onb.channel ∈ {null, not_sure, other}` **or** `onb.default_suspect == true` (the picklist WOM default). *Free-text WOM at 0.70 is trustworthy.*
- `considered` = the higher-confidence **specific** value among {sales_call, enterprise_form}, chosen **after** pairwise conflict evaluation (§F). Tie-break: confidence desc → recency desc (`call_date`) → fixed `sales_call > enterprise_form`.
- Any source resolving to `test_junk` is dropped from candidacy; the merged value is `test_junk` only if *all* signals are junk.

**Evaluate top to bottom; first match wins. Winner confidence is the source's own confidence unless noted.**

| # | Condition | Winner | Confidence |
|---|---|---|---|
| 1 | `considered` specific **and** conf ≥ 0.80 | **considered** | its conf (→ 0.95, `source = reconciled` if `onb` corroborates same rollup) |
| 2 | `considered` specific **and** 0.50-0.79 **and** `onb_untrustworthy` | **considered** | its conf |
| 3 | `onb` specific **and not** `default_suspect` | **onboarding** | its conf (0.80 clean pick / 0.70 free-text WOM; → 0.95 `reconciled` if `considered` corroborates same rollup) |
| 4 | `considered` specific (any conf, **incl. Low**) | **considered** | its conf (marked Low if < 0.50) |
| 5 | `onb.default_suspect` (picklist WOM) | **onboarding → WOM** | 0.50, `conflict/secondary` per §F |
| 6 | any source = `other` | **other** | low |
| 7 | any source = `not_sure` | **not_sure** | - (no channel; §G) |
| 8 | else | **none → null** | null |

Rule 4 is genuinely reachable: a Low-confidence Gong answer **does populate the feeder** (marked Low, §I), so a contact whose only signal is a Low Gong answer resolves to that channel (marked Low) rather than silently dropping to null - while still being routed to review.

## F. Conflict handling

**Definition: `sr_attribution_conflict` fires on a ROLLUP-level mismatch between two *specific* sources.** LinkedIn (onboarding) vs Instagram (Gong) both roll up to Social Media → **not** a conflict (family-level corroboration; the waterfall still picks the more-trusted specific value). YouTube vs Search → different rollups → **conflict**. Conflict is always on the canonical category, never raw text - this avoids over-flagging while catching real disagreements.

**Explicitly NOT a conflict:** one side null / `not_sure` (a fill, not a disagreement); one side `other`; same rollup with a different specific platform; a considered value matching an onboarding multi-select element.

**Handling (evaluate conflict pairwise across all three specific sources *before* collapsing `considered`, so a 3-way disagreement drops nothing):**
- The winner is set by the §E waterfall regardless.
- On any rollup-level conflict: `sr_attribution_conflict = true`; the highest-confidence loser → `sr_attribution_secondary_channel` / `_secondary_source`; and **every** losing `(source, channel, confidence)` tuple → `sr_attribution_secondary_json`.
- When two specific sources **agree** at the rollup level: `sr_attribution_source = reconciled`, confidence promoted to 0.95.

**Hard idempotency rule:** every `sr_attribution_*` output field (`conflict`, `secondary_channel`, `secondary_source`, `secondary_json`, `default_suspect`, …) is **written or explicitly cleared on every actual compute** - never left stale. A conflict that later resolves must flip `conflict` back to `false`, or the RevOps QA view (which filters `conflict = true`) rots.

Conflict rows **are** the high-value self-serve→sales overlap segment. Route `conflict = true` to a RevOps QA view; the stored call pointer makes each case adjudicable in Gong, and a rep-disposition correction becomes a training label for the classifier (§I).

## G. Coverage handling (the common case is exactly one source)

Because the two populations are largely complementary, **most contacts have exactly one source.** Four terminal states are kept distinct at store time and collapsed only at report time:

| State | Meaning | Reporting treatment |
|---|---|---|
| **null** (`source = none`) | No self-report at all (blank after strict parse, or nothing on any source) | Missing data; excluded from known-channel denominators |
| **`not_sure`** | A real, explicit non-recall ("don't remember", "idk", "n/a") | Known *non-answer*; excluded from the channel denominator **and** from Other, but counted so you can measure recall quality |
| **`other`** | A real, parseable answer that fits no bucket | Counted as Other; reviewed monthly to promote recurring entries |
| **`test_junk`** | Gibberish / test / employee tests | Excluded from all denominators |

**Cases:**
- **Only onboarding (dominant, ~519K).** Normalize and take it. `source = onboarding`. Confidence per §D. This alone yields a merged field across the whole self-serve base and **ships before Gong exists**.
- **Only Gong / only enterprise form.** Take the considered value at its extraction confidence. `source = sales_call` / `enterprise_form`.
- **Neither.** `channel = null`, `source = none`. **Never coerce to `other`** - null is missing, `other` is a real uncategorized answer; conflating them makes the long tail unreadable.

**Self-report complements, never replaces, click/UTM.** Self-report over-credits WOM and under-credits Paid (people don't recall ads); click under-credits organic/offline/viral and is broken for PLG contacts. Report both axes and reconcile per-channel: trust self-report for WOM / podcast / Guest / organic-YouTube and for PLG contacts; trust first-touch / warehouse-reconstructed click for Paid and specific-campaign credit. Never let one overwrite the other.

## H. Implementation approach in HubSpot

**Mechanism: Operations Hub custom-coded action for parse + normalize + merge; external Snowflake extraction + Hightouch sync for structuring Gong.** Both dependencies already exist at Riverside (Ops Hub custom-coded actions per `self-serve-lead-scoring.md`; Hightouch Snowflake→HubSpot syncs). Only the Snowflake dbt/LLM extraction model is net-new. **No new procurement.**

| Option | Verdict | Why |
|---|---|---|
| Pure workflow if/then | **Rejected** | Can't `JSON.parse`/strip `["…"]`, can't tell bracketed picks from bare text, and hundreds of synonyms would need hundreds of unmaintainable branches. |
| **Ops Hub custom-coded action** | **Chosen for normalize + merge** | Parses the JSON-array string, handles bare strings, runs the static crosswalk, and emits canonical + rollup + raw + confidence + conflict + secondary in one deterministic pass. In-portal → low-latency recompute on change. |
| **External enrichment (Snowflake + Hightouch)** | **Chosen only for Gong structuring + the free-text fuzzy/LLM tail** | LLM work belongs in the warehouse where Gong data lives and where batch scale is safe. Not used for the merge itself - keeping the merge in-portal gives immediate recompute when onboarding changes. |

### H.1 Recompute triggers (workflow, re-enrollment ON)

Re-enroll when **any** of: `onboarding__how_did_you_hear_about_us_` is known/changes; **`sr_attribution_salescall_synced_at` changes** (the Gong barrier field, *not* individual Gong fields); `enterprise_form_attribution_channel` changes; or `sr_attribution_normalizer_version < N` (map-change recompute).

### H.2 Idempotency (and the split-writer blocker fix)

The action is a pure deterministic function of `{onboarding_raw, salescall_channel, salescall_confidence, salescall_call_date, enterprise_channel, enterprise_confidence, normalizer_version}`. **Blocker fix:** Hightouch writes the Gong component fields first and `sr_attribution_salescall_synced_at` **last**; both the trigger (H.1) and the signature key on `synced_at` (and the signature includes salescall confidence + call_date). This guarantees the merge never fires on a half-written Gong payload - the original design keyed only on the raw field, so a `raw`-before-`confidence` race could permanently freeze the wrong confidence for the overlap cohort.

At entry, compute `sr_attribution_input_signature = hash(inputs)`; if it equals the stored signature, **skip all writes and return**. `sr_attribution_computed_at` is stamped only on an actual write.

### H.3 Single shared, versioned normalizer

Factor the enterprise field's free-text→canonical logic into one versioned function `attribution_normalize(rawText, version) → { channel, rollup, confidence, matched_rule }`. The onboarding parse and the enterprise raw call it in-portal against the **static crosswalk only** (no external call). Gong quotes and the onboarding free-text tail are classified in the **warehouse in batch** and pass their `raw_phrase` through the same crosswalk logic there. One map, one place. **Scale fix:** the in-portal action never makes a per-record LLM/API call - at 519K contacts with re-enrollment on, that would blow the ~10s action timeout and execution quotas.

### H.4 Re-normalization via stored raw (no source re-read)

- **Onboarding + enterprise:** raw is the contact's own answer, persisted on-record. To change the map: bump `normalizer_version` to N, enroll an active list `sr_attribution_normalizer_version < N`, and the action re-reads only the persisted `_raw` fields → re-normalizes in-portal. No source re-read.
- **Gong:** verbatim quotes are **not** stored in HubSpot (PII, §F). Gong re-normalization = re-run the warehouse normalizer over warehouse-held quotes and re-sync via Hightouch - cheap, no re-transcription, no re-classification of the audio.

### H.5 Originals stay intact (hard contract)

The action and Hightouch **read** the three source fields and **write only** to the `sr_attribution_*` namespace (+ `onboarding_persona_segment`). Enforce with a code comment and a property-history spot check via `/hubspot-workflow-qa` confirming the source fields show no writes from this workflow's actor.

### H.6 PII / consent (Gong quotes)

Verbatim prospect speech routinely names third parties (the sample tail itself contains "Stephen Robles…" and named referrers). **Default: keep verbatim quotes in the warehouse behind Gong's access controls; store only a pointer (`call_id` + `call_url` + `captured_at`) in HubSpot** as the drill-back audit trail. If a quote must ever live in HubSpot, classify those properties as sensitive / field-level-restricted, set a retention TTL, and add them to the GDPR/CCPA deletion/DSAR workflow (a subject request must be able to purge quotes, including where a referrer is named on another contact).

## I. Gong structuring (the hard constraint: structured *before* it can feed the merge)

**Primary + fallback:** a Gong Smart Tracker detects/bounds the "how did you hear" moment → a warehouse LLM classifies that span → the shared normalizer produces the canonical value → Hightouch syncs. A **rep-disposition dropdown** is the human-in-the-loop fallback for Low-confidence/conflict, and rep corrections become training labels.

**Object placement:** the warehouse is source of truth; per-call results mirror to the **Pre-Op** (`sr_attribution_gong_*`) for rep visibility and drill-back; the best call per contact rolls up to the **Contact** feeder (`sr_attribution_salescall_*`) that actually feeds the merge. Attribution is a person-level truth (merge on Contact, where onboarding + the enterprise precedent live), but a call is 1:1 with a Pre-Op cycle and sits next to the authoritative `Last Touch Source`.

**Pipeline:**
1. **Detect** - a Gong Smart Tracker ("HDYH-Question") flags calls + timestamps of the moment, so we don't classify every call.
2. **Pull** - a scheduled warehouse job (transcripts already land in Snowflake) reads flagged calls + the Gong→CRM Contact/Deal mapping.
3. **Classify** - the LLM reads the span around the tracker hit, **targeting the prospect's speaker turn**, and emits `{ raw_quote, channel_guess, confidence, call_id, call_url, call_date, contact_id, deal_id, question_detected }`. The canonical value comes from running `raw_quote` through the shared normalizer, not the LLM's free-text guess. The verbatim quote stays in the warehouse (§H.6).
4. **Per-contact selection** - rollup winner = the **earliest** qualifying call (min memory decay) on the **current** Pre-Op cycle; ties → highest confidence → earliest. Low-confidence calls **still populate** the feeder (marked Low) so a Low-only contact isn't silently dropped, but they're routed to review. `sr_attribution_gong_call_id` makes the choice auditable.
5. **Write** - Hightouch mirrors per-call results (pointer only) to Pre-Op `sr_attribution_gong_*`, then writes the winner's channel + confidence + call_date + call_url to the Contact feeder, and finally stamps `sr_attribution_salescall_synced_at` (barrier, §H.2). If no Pre-Op exists yet (creation workflow has a ~5-min delay, see `preop-data-intelligence`), **hold-and-retry** rather than mis-write.
6. **Merge** - the Ops Hub action folds the Contact feeder into the §E waterfall.

**One confidence rubric across all sources:** High (≥0.80) = a specific unambiguous channel in the person's own words, single clean mapping; Medium (0.50-0.79) = paraphrased / rep-summarized / vague WOM without a named source; Low (<0.50) = weak/indirect/uncertain or "don't remember" (stored, marked, routed to review; wins only as the sole signal).

**Failure-mode guards:** classify the *prospect's* turn (if only the rep names the channel, cap at Medium); require a **named referrer or specific detail** for High confidence on `word_of_mouth_referral` (social-desirability guard, mirrors the onboarding default bias); treat onboarding-vs-call disagreement as complementary (agree → reconciled/High; disagree → conflict + adjudication).

**Owner / RACI:** taxonomy, confidence rules, strategy sign-off → **Hanan Amos**. Build (Gong tracker, warehouse model, Hightouch sync, Ops Hub action, fields, merge workflow) → **Jonathan Galili**. Rep-disposition dropdown + enablement → **RevOps** (Dan Markel / Daniel Weisfelner - *confirm*). Early dependency: a **Gong admin** is required for Smart Tracker creation + API access.

**Rollout sequence:**
1. Ratify taxonomy (§C) + publish the crosswalk (§D); add the warning + rename to the persona field.
2. Create all `sr_attribution_*` fields (+ Pre-Op mirror, Pre-Op Gong fields, `onboarding_persona_segment`) - no writes yet. Factor the shared normalizer; **unit-test the parser** against §D, including `[]`, `[""]`, blank, brackets-in-free-text, and the `Spotify`/`spotify` dupe.
3. **Ship onboarding-parse + merge first** (deterministic, no Gong dependency) → merged field across ~519K; validate against `enterprise_form_attribution_channel` where both exist.
4. Build + backtest the Gong Smart Tracker; measure question-detected precision/recall.
5. Build the warehouse LLM classifier over historical flagged calls; human-label a sample to calibrate the High/Med/Low thresholds on a held-out set.
6. Wire classifier → Pre-Op → Contact feeder (with the `synced_at` barrier); extend the merge action to fold in Gong + conflict + the confidence gate.
7. Add the rep-disposition dropdown (fallback + correction); feed corrections back as training labels.
8. Backfill once; verify the WOM share drops appropriately once Gong/enterprise override on the overlap segment. QA via `/hubspot-workflow-qa`. Run `/retro` to capture the final crosswalk + the Blog/Event/Email bucketing decision.

## J. Open questions / decisions for the team

1. **Enterprise-taxonomy governance.** Propose adding four groups to `enterprise_form_attribution_channel` so canonical values stop being standalone-only: **Guest on Riverside / PLG Viral**, **Event / Conference**, **Content / Blog**, **Email (Owned)**. After they ship, the five standalone rollups become direct. Needs the enterprise-field owner's sign-off - converge, don't fork.
2. **Deprecate the legacy enums** `how_did_they_hear_about_us` and `how_did_they_hear_about_us_` - the exact sprawl this design supersedes. Confirm nothing live reads/writes them, then deprecate.
3. **Persona field rename.** Rename `onboarding_questions_acquisition_sources` → `onboarding_persona_segment` and fix its description (or add a hard description warning if a rename is risky). Confirm downstream consumers first.
4. **Fix the onboarding WOM default bias** in the product widget (no pre-selection / randomize order / require an explicit tap). Re-baseline `default_suspect` rates once shipped. Needs product/PLG buy-in.
5. **Two emerging canonical candidates:** **Creator / Influencer** (the "Stephen Robles" case) and **Partner / Agency** (the "through our podcast agency" case) - currently folded into `word_of_mouth_referral`. Promote when recurring.
6. **Confidence bands + gate thresholds** (High ≥ 0.80 to override a clean onboarding pick; Medium ≥ 0.50 to override untrustworthy onboarding; enterprise-form default 0.80) are proposed defaults - calibrate against the held-out Gong label set (rollout step 5).
7. **Confirm RevOps owners** for the rep-disposition dropdown and secure the **Gong admin** dependency.
8. **Enterprise-form re-derivation.** Once the shared normalizer is stable, consider re-deriving `enterprise_form_attribution_channel` through it and retiring its bespoke logic - one map for all sources. Decide now vs after the merge stabilizes.
9. **Monthly hygiene.** Review `other` and `not_sure` buckets; promote recurring `other` values; monitor conflict rate, WOM share (social-desirability watch), coverage, and classifier drift.

## Pointers

- **Onboarding source field:** `onboarding__how_did_you_hear_about_us_` (Contact, 519,742 populated).
- **Sales source:** Gong transcripts/notes → `gong_calls` topic in Omni (see `gong-calls-explorer`); transcripts land in Snowflake.
- **Precedent to converge on:** `enterprise_form_attribution_channel` (derived from `how_did_they_hear_about_us__enterprise_form_`).
- **Related systems:** `systems/owned/hubspot.md`, `systems/owned/self-serve-lead-scoring.md`, `systems/owned/omni-bi.md`; skills `/preop-data-intelligence`, `/hubspot-workflow-qa`, `/gong-calls-explorer`, `/measurement-agent`.
- **Owner:** Hanan Amos (strategy/taxonomy), Jonathan Galili (build/infra). Portal `9154210`.
