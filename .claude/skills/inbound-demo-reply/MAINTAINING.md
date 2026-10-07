<!-- Formerly PART 7 of SKILL.md. Read this before editing the skill or pain-map.md. Not needed during a run. -->

# PART 7: MAINTAINING THIS SKILL (read before you edit it)

This file states the **current rules**, not their history. When Nir gives new feedback, distill it into the rule; do not append the story. This is a hard convention, because ignoring it is exactly how this file bloated to 1000+ lines of duplicated, contradictory rules before.

**When you get new feedback, do this:**

1. **Find the rule it changes** and edit that rule in place. Do not add a new dated bullet next to the old one. If the feedback contradicts an existing rule, replace the old wording, don't stack a newer note on top of it.
2. **Extract the rule, drop the narrative.** "Cat Rotolo at Together AI was wrongly marked borderline on 2026-06-16" is not a rule. The rule is "in-product demo request + real company + buyer-signal title = draft." Write the rule. Delete the anecdote.
3. **Keep at most a one-clause parenthetical** when it disambiguates a boundary the rule can't state cleanly, e.g. `(a well-known-in-its-vertical law firm doesn't count as Tier-1)`. No names, no dates, no email/company/license details, no PII.
4. **Provenance lives in git, not here.** Who asked and when is in the commit history and PR. Do not encode it as `(2026-07-09 update per Nir)` tags in the operating text.
5. **Deduplicate.** If a rule already exists elsewhere (routing table, email hard-rules, self-review checklist), edit the one canonical copy and reference it. Never restate the same rule in three sections.

**Litmus test before saving an edit:** could a new reader follow this rule without knowing the story behind it? If yes, you've distilled correctly. If the text only makes sense as a war story, you haven't turned it into a rule yet.

## Maintaining `pain-map.md`

The pain map is generated data, not hand-authored rules. Do not edit its clusters or verbatims by hand, and never add a quote to it that didn't come out of a HubSpot `form_comment` query.

- **Regenerate, don't patch.** A refresh means re-running the source queries over a new window and rebuilding the file. Its own "Open questions for the next refresh" section carries the recipe.
- **Refresh on packaging changes, not on a calendar.** Most pains in it are artefacts of current tier boundaries. Move a feature between Pro and Business and the top pain in several clusters changes, which makes the map wrong faster than time does. A quarterly rerun over the same sources mostly produces a longer file saying the same things.
- **Volume is not the gap.** The four directional clusters are thin because those titles rarely fill the form. Waiting doesn't fix them. What would: Gong call content modelled into Omni (the map has zero call verbatims because that topic exposes metadata only), unblocking `query_crm_data` on the HubSpot connector so deals join to job titles, and a role dropdown on the demo form to kill the 31% unclassifiable-title residual.
- **If a rule emerges from the map, write it here.** The map records what buyers say. Anything that changes how we draft belongs in PART 3, not in the data file.
