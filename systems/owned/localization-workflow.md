<!-- last-reviewed: 2026-09-24 (qualified every bare "Jonathan" as Jonathan Galili now that there are two Jonathans, and recorded the planned Webflow Connection Owner handover to Jonathan Ydov) -->
<!-- prior: 2026-07-26 -->
# Localization SOP (SEO Pages → Crowdin → Webflow)

> End-to-end standard operating procedure for localizing riverside.com marketing pages: request intake, batch translation, staging QA, and production publish.

## Overview

This SOP formalizes the localization workflow after a July 2026 team review of the process as it had been running informally, and a subsequent pass from Amir (SEO Manager) that cut steps the first draft had added and that would have slowed the process down. The review's finding stands: the team was **not** trying to redesign the pipeline. Crowdin → translate → Webflow → staging → production was already broadly right. The gaps were structural: no single owner, translations requested page-by-page and language-by-language instead of by batch, no ETA commitment, and issues ping-ponging directly between SEO, Localization, and Dev instead of routing through one person.

Amir's correction to the first draft: don't turn Webflow-component coverage into a new per-request gate that routes every batch through Jonathan Galili before Asaf can even start pulling pages. That adds a hop and slows every single request down. Component coverage should instead be solved once, structurally, as a standing sync between Webflow and Crowdin, so Asaf's normal page pull already includes every component. If a specific component keeps failing to pull, that's a standing defect to fix outside the per-request flow, not a reason to add a gate to every batch.

This doc is the source of truth for the process. `systems/owned/marketing-website.md` covers the wider Marketing Website system (of which localization is one workflow) and should link here rather than duplicate this content.

## Ownership (RACI)

| Role | Person | Responsible for |
|------|--------|------------------|
| **Orchestration Owner** | Hanan Amos | Owns end-to-end delivery: tracks every request, dependency, blocker, and ETA, and is the point cross-team communication routes through (see Escalation below). Not a doer of the technical steps; the single accountable point of contact. |
| **SEO Manager** | Amir Bar Tikva | Defines the input package (brief) for every localization request; reviews staging, writes the change report, and updates Crowdin directly; owns final requirements sign-off before production. |
| **Crowdin Owner** | Asaf Fox | Manages the Crowdin platform and translator assignment; pulls pages (and, once the standing sync below is live, their components) from Webflow into Crowdin; commits the batch ETA; runs AI + human translation and QA. |
| **Webflow Connection Owner** | Jonathan Galili (Marketing Website role, interim; handover to Jonathan Ydov, Web Developer, planned after he starts on 2026-09-27, per his onboarding plan) | Builds and maintains the standing Webflow ⇄ Crowdin component sync (one-time infra, not a per-request step); imports translated content back into Webflow; manages staging and production publish. |

No step in this SOP should be executed by someone other than its named owner without Hanan (orchestration owner) knowing; that's what "route through the orchestration owner" means in practice, not that Hanan personally performs every step.

## Infrastructure (one-time, outside the per-request flow)

**Webflow ⇄ Crowdin component sync**, owner: the Webflow Connection Owner (Jonathan Galili until the handover), with Asaf.

Every shared Webflow component (nav, footer, CTAs, cards, forms, repeated sections) needs to already be wired into the Crowdin export before any localization request runs, so that when Asaf pulls a page, its components come with it automatically. This is built and maintained **once**, generally, not rebuilt or re-validated per batch. Per-request component discovery was the first draft's mistake: it turned a one-time integration problem into a recurring gate that every single request had to route through Jonathan Galili for.

If a specific component **recurringly** fails to pull cleanly, that is a defect in this sync, not a per-batch blocker: log it and fix it here (outside the live request flow), so it stops recurring, rather than working around it request by request.

## The process, end to end

```text
SEO (Amir)
    │  brief: pages, languages, priority, publish date, SEO requirements
    ▼
Marketing Ops (Hanan): orchestration - tracks the brief, confirms it's complete, hands off, tracks ETA and blockers
    ▼
Localization (Asaf)
    ├─ pull pages (with components, via the standing Webflow⇄Crowdin sync) directly into Crowdin
    ├─ commit an ETA for the whole batch, all target languages together
    ├─ AI-translate, then human QA/fix
    └─ deliver the completed batch
          │
          ▼
Webflow (Jonathan Galili)
    ├─ import translations from Crowdin
    └─ publish to staging, staging links provided
          │
          ▼
SEO Review + Change Report (Amir): review staging, write the change report, update Crowdin directly
          │
          ▼
Fixes (loop until clean) → Final Approval (Amir) → Production (Jonathan Galili) → Production Validation (Amir)
```

This is intentionally shorter than the first SOP draft: no separate component-discovery gate, and no separate string/localization review round-trip. Amir updates Crowdin directly off his own change report; Asaf spot-checks that update for translation-side conflicts as part of his normal QA, not as a formal second handoff.

## Step-by-step SOP

### 1. Localization request (brief), Owner: Amir
Amir sends a **complete brief**, not just a page list. Required fields:
- Pages to localize (URLs or Webflow page IDs)
- List of components per page (which shared Webflow components each page uses)
- Target languages (all languages needed for this batch; see Step 2)
- Priority
- Desired publish date
- SEO requirements (meta, schema, target keywords per locale)

The per-page component list is a heads-up for Asaf's pull, not a new gate: it doesn't require Jonathan Galili's sign-off and doesn't block the brief from moving forward. It complements the standing Webflow⇄Crowdin component sync (see Infrastructure above), giving Asaf a known list to check his pull against rather than discovering gaps after the fact.

An incomplete brief (e.g. pages only, no target languages/date) is not ready to enter the pipeline; send it back to Amir rather than guessing.

### 2. Batch pull + translation request, Owner: Asaf
Asaf pulls the requested pages directly from Webflow into Crowdin, all target languages in **one batch**, not a separate round per language (German, then French, then Spanish, ...). Thanks to the standing component sync (see Infrastructure above), the pull already includes the pages' shared components; Asaf doesn't wait on a separate discovery step from Jonathan Galili to do this.

### 3. ETA commitment, Owner: Asaf
Asaf estimates and commits a completion date for the batch before translation starts, and shares it with Hanan for tracking. No batch begins translation without a committed ETA.

### 4. Translate + human QA, Owner: Asaf / Localization team
AI (Crowdin) translation, followed by human localization-translator QA and fixes. Deliver the completed batch back as a unit.

### 5. Import to Webflow + publish to staging, Owner: Webflow Connection Owner (Jonathan Galili until the handover)
Translated content is pulled from Crowdin into Webflow and published to staging with staging links provided. Jonathan Galili validates that staging links actually resolve **before** handing off to SEO; previously SEO discovered broken staging links themselves and had to bounce back to Dev. This handoff (waiting on working staging links) is the process's biggest current pain point; see Automation priority below.

### 6. SEO review + change report, Owner: Amir
Amir reviews the translated pages via staging links against the brief's SEO requirements, writes a **change report** documenting what needs to change, and updates Crowdin directly with those changes rather than routing them through a separate handoff. Asaf spot-checks the update for translation-side conflicts as part of his normal QA pass, not as a formal second review round.

### 7. Fixes (iterate until clean), Owners: Asaf / Jonathan Galili / Amir loop
Fix issues in Crowdin → re-sync to Webflow → re-publish to staging → re-review. Loop until clean. Route any cross-team disagreement about a fix through Hanan rather than resolving it directly between Localization and Dev.

### 8. Final approval, Owner: Amir
Confirms all requirements from the original brief are met before production publish is authorized.

### 9. Publish to production, Owner: Webflow Connection Owner (Jonathan Galili until the handover)
Publish the approved localized pages live.

### 10. Production validation, Owner: Amir, with Jonathan Galili
- Check that every permanent slug change on an already-published page has a 301 redirect (a 302 does not satisfy this); if one is missing, file it as a Dev task via `/pm-story`.
- Check for broken links and 404s on the live localized pages.
- Validate SEO (meta, indexing, schema) is live as specced.
- Visual and functional QA pass.

### 11. Localization complete, Owner: Hanan
Sign-off and documentation. Share learnings and update this SOP if the run surfaced a new failure mode (see `/retro`).

## Escalation: route issues through the orchestration owner

```text
Issue
  │
  ▼
Hanan (orchestration owner)
  │
  ▼
Correct owner (Amir / Asaf / Jonathan Galili)
  │
  ▼
Resolution
```

Do not resolve cross-team issues by going directly SEO ↔ Localization ↔ Dev. This was explicitly called out as a source of ping-pong and dropped context in the prior process, and Amir flagged shortening this ping-pong as a priority in his review of the first SOP draft. Bring the issue to Hanan; he routes it to the right owner and tracks it to resolution.

## Known issues in the current process (fix before scaling)

These are carried over from the pre-SOP process audit and remain open. Do not treat them as resolved just because this SOP exists.

| Issue | Symptom | Status / next step |
|-------|---------|---------------------|
| Webflow pages pulled to Crowdin don't always contain every translatable element | Missing translations discovered only in staging | Addressed structurally by the standing Webflow⇄Crowdin component sync (Infrastructure, above), owned by Jonathan Galili with Asaf, not a per-batch step. A component that recurringly fails to pull is a defect in that sync to fix directly, not a per-request workaround. |
| **Duplicate Crowdin domains/projects** | Risk of translating into or reading from the wrong project | Must be cleaned up; see "Automation priority" below |
| Translation Memory (TM) inconsistencies | Re-translation drift, inconsistent terminology across pages | Part of the same Crowdin cleanup effort |
| Waiting on staging links | Amir's #1 pain point: the gap between translation delivery and a working staging link to review | Highest-priority automation target, see "Automation priority" below |
| Crowdin → Webflow re-upload sometimes silently fails for some pages | Localization has to reconnect and re-upload individual pages | Localization to keep investigating; blocks unattended automation until reliable (see below) |
| Slug changes on live pages without a 301 | 404s / broken SEO equity on production | Step 10 (production validation) now explicitly checks for this and files the redirect task |

## Automation priority: Webflow ⇄ Crowdin publish sync

Amir named the wait for working staging links as the single biggest pain point in the current process. Automating the Webflow ⇄ Crowdin publish sync (so translated content lands in staging without a manual re-upload/re-publish step) is therefore the **top priority** infra improvement for this workflow, not a someday item.

It still needs the underlying Crowdin data problems resolved first, or the automation just automates bad data:

- Duplicate domains/projects
- Duplicate Crowdin projects
- Translation Memory inconsistencies
- Sync inconsistencies between Crowdin and Webflow

Sequence: clean up Crowdin (Asaf, ongoing), then build the publish automation (Jonathan Galili) as the next infra project after the component sync above. Once live, decide deliberately whether a schedule publishes *all* pending pages or only specific ones (open question from the prior process discussion, not yet decided).

## What changed vs. the prior (informal) process

1. Added a single orchestration owner (Hanan) for the full pipeline; previously responsibility was split across SEO, Localization, Webflow, and QA with nobody owning end-to-end delivery.
2. Amir's request became a full brief (pages, languages, priority, publish date, SEO requirements), not just a page list.
3. Translation moves by **batch** (all languages together) instead of one round per language.
4. Added a formal ETA commitment from Localization before translation starts.
5. Webflow component coverage is solved once, structurally, as a standing Webflow ⇄ Crowdin sync, not as a per-request discovery gate. Amir cut the first SOP draft's per-batch component-discovery and Crowdin-validation steps for exactly this reason: they added a hop and slowed every request down without fixing the underlying (recurring, structural) problem.
6. SEO review and Crowdin updates are now one step: Amir writes a change report and updates Crowdin directly, instead of a separate SEO-review-then-string-review round-trip.
7. Automating the Webflow ⇄ Crowdin publish sync (staging links) is named the top-priority infra project, gated only on the Crowdin cleanup above, not deferred indefinitely.
8. All cross-team issues route through the orchestration owner instead of direct SEO ↔ Localization ↔ Dev back-and-forth.

## Related

- **System doc:** `systems/owned/marketing-website.md`, the wider Marketing Website system; see its Known Issues table for the DE-locale redirect-chain problem this SOP's Step 10 is meant to catch going forward.
- **Skills:** `webflow-locale-publish-queue` (bulk-queues localized CMS items for publish), `webflow-link-checker` (redirect-chain / 404 crawl across locales), `seo-ai-search-agent` (SEO analysis), `.claude/agents/marketing/marketing-localization-strategist.md` (deep-dive specialist for locale architecture, hreflang, translation QA; no live system access, invoke via `website-agent` or `seo-ai-search-agent`).
- **Slack:** `#localization-qa`, `#localization-updates`, `#webapp-localization-issues` (product-side localization; marketing SEO/Webflow localization discussion is not yet centralized in a single channel, flagged as a gap).
- **Source:** July 2026 localization process review (Amir's as-of-now process writeup + team discussion on proposed changes), plus Amir's follow-up feedback on the first SOP draft cutting the per-request component-discovery gate and merging the review steps. If this SOP and practice drift apart, update this file and run `/retro`.
