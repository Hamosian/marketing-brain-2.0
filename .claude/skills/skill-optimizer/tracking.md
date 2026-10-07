# Skill optimizer - ledger

State for `/skill-optimizer`. The loop reads this before picking a batch (SKILL.md rule 7):
a skill with a `KEEP` in the last 30 days, or an `escalated` row a human has not cleared,
is skipped. This is what stops the loop from re-polishing the same skill every run or
retrying a fix that already failed twice.

## Attempts

`gap` is the scoreboard item the edit aimed at (`routing`, `examples`, `done_when`,
`boundary`, `grounding`, `output_schema`, `hard`, `no_case`). `verdict` is the judge's
output: `KEEP`, `REVERT`, `NO-CHANGE`, or `escalated` / `skipped: needs owner`. To clear an
escalation, change its verdict to `cleared` and say by whom.

| Date | Skill | Gap | Change | Verdict | Reason |
|------|-------|-----|--------|---------|--------|
| 2026-09-27 | team-intro | examples, done_when, boundary, grounding, output_schema | Boundary vs onboarding-doc-builder / access-welcome, five fixed output sections, example; reviewer narrowed the monday line | KEEP | +5 signals |
| 2026-09-27 | team-intro | routing | Case "onboard a new marketer onto this repo" still ranks access-welcome first; a trigger phrase that fixed it echoed the case and was removed | escalated | Needs the owner to decide if access-welcome is the right answer |
| 2026-09-27 | gsc-freshness-check | done_when, boundary, grounding, output_schema, no_case | Done-when bar, boundary vs weekly-seo-report / organic-dashboard, dates quoted from source, first routing case | KEEP | +4 signals, first case |
| 2026-09-27 | gsc-freshness-check | routing | "feed" added to description | REVERT | Stole "feed these tasks into the paid acquisition team board" |
| 2026-09-27 | gsc-freshness-check | routing | "(frozen numbers, missing days)" added to description | REVERT | Reviewer: echoed the eval case; removed. Case lands weak-trigger, confirm with /skill-eval |
| 2026-09-27 | marketing-psychology | examples, done_when, boundary, grounding, output_schema | Output format, grounding rule, example; replaced dead pointers copywriting / popup-cro / ab-test-setup; reviewer fixed Decoy -> Default effect and removed an echoing description phrase | KEEP | +5 signals, dead links fixed |
| 2026-09-27 | retro | done_when, boundary, grounding, output_schema | /pr-ship (not installed here) replaced with branch + preflight + gh; example from PR #374 | KEEP | +4 signals, dead path fixed |
| 2026-09-27 | agent-builder | done_when, boundary, output_schema | /marketing-os -> /marketing-brain; sync-codex + preflight added before the deploy PR | KEEP | +3 signals, deploy gap fixed |
| 2026-09-27 | skill-optimizer | routing | Cases reworded after reviewer found they echoed the description; one lands weak-trigger | escalated | Confirm with /skill-eval model tier |
| 2026-09-28 | hubspot-agent | boundary, done_when, examples, grounding | Retired 3-pipeline list replaced with the 4 market pipelines (pointer to preop-data-intelligence); 3 campaign tools not in the connector replaced with read_campaign_data / get_campaign_attribution_reports; boundary vs inbound-demo-reply / nir-mql-live-report | KEEP | +4 signals, routing case clear, 2 stale facts fixed |
| 2026-09-28 | measurement-agent | boundary, done_when, examples | Required context now sends data questions and definitions to /rivermind:ask first (was data-agent), per CLAUDE.md; boundary vs nir-weekly-report / weekly-seo-report; an echoing description phrase removed before judging | KEEP | +3 signals, directive conflict fixed |
| 2026-09-28 | nik-voice | done_when, grounding, output_schema | Done-when, no-invention guard on invariant 4, register-choice example, output line; reviewer added the report-to-nir exception | KEEP | +3 signals |
| 2026-09-28 | ste | done_when, grounding | Dead riverside-intel pointer removed, pipeline now names critique, rule 18 no longer invites invented values, retired-framing history cut | KEEP | +2 signals, dead pointer fixed |
| 2026-09-28 | curious-intern | boundary, done_when, output_schema | /pr-ship replaced with the repo PR path (carried from run 1); fictional Airflow example replaced with real repo paths; grounding rule | KEEP | +3 signals, dead path fixed |
| 2026-09-28 | inbound-demo-reply, win-loss-pricing-analyzer, link-triage | grounding (not scored) | riverside-intel (a personal skill, not in this repo) kept where installed, with /riverside-product-knowledge or an in-sample taxonomy as the named fallback; dead /deep-gtm-research and pricing-teardown fallbacks replaced with web search | NO-CHANGE, kept | Rule 4: dead pointers the scoreboard cannot see |
| 2026-09-28 | hubspot-agent, measurement-agent | examples | Worked examples no longer copy eval requests word for word (reviewer follow-up) | NO-CHANGE, kept | Examples teach more than one phrasing |
| 2026-10-04 | preop-data-intelligence | boundary, done_when, grounding | Three stale "three pipelines" lines in the analytical layer fixed to the four market pipelines; answer bar with source and as-of date; boundary vs rivermind:ask, hubspot-agent, nir-mql-live-report, inbound-demo-reply, lifecycle-agent; reviewer narrowed the BD SQL example to section 9's full filter | KEEP | +3 signals, stale fact fixed |
| 2026-10-04 | value-proposition-canvas | boundary, done_when, examples, grounding | FIT example quoting the pain map's won-vs-lost figures (noted as not split by title), done-when bar, boundary vs page-cro, marketing-psychology, win-loss-pricing-analyzer, are-we-really-different, persona-panel, marketing-council, curious-intern; description untouched (1018 chars) | KEEP | +4 signals |
| 2026-10-04 | marketing-brain | boundary, grounding, routing | Grounding section, boundary section, description sentence on multi-system diagnosis; reviewer narrowed "moved" (collided with a gsc-freshness-check case), replaced with "changed" rather than the suggested "dropped", which echoes eval case 175 | KEEP | +2 signals; its two routing cases still not clear (line 61 rank 5 -> 7, line 175 rank 4 -> 3); the graphify case clearing is description dilution, not a gain |
| 2026-10-04 | access-welcome | boundary, done_when, examples, grounding | Rule 5: never welcome a departed person (timseneker-source case from tracking.md), done-when bar, boundary vs onboarding-doc-builder / team-intro, fixed report format; reviewer fixed the handle typo and the departure source | KEEP | +4 signals, departed-person gap closed |
| 2026-10-04 | gong-calls-explorer | boundary, done_when, examples, grounding | ask_user_input_v0 / visualize:show_widget scoped to claude.ai with AskUserQuestion for Claude Code; getData substitution and date-rewrite checks from omni-bi.md; done-when, output example, boundary vs win-loss-pricing-analyzer, vendor-meeting-quality, preop-data-intelligence, data-agent | KEEP | +4 signals, tool names fixed |
<!-- appended by /skill-optimizer; newest at the bottom -->

## Runs

| Date | Batch | Kept | Reverted | Escalated | Priority before -> after | PR |
|------|-------|------|----------|-----------|--------------------------|----|
| 2026-09-27 | team-intro, gsc-freshness-check, marketing-psychology, retro, agent-builder | 5 | 2 | 3 | 1668 -> 1568 | #409 |
| 2026-09-28 | hubspot-agent, measurement-agent, nik-voice, ste, curious-intern | 5 | 0 | 0 | 1573 -> 1490 | pending |
| 2026-10-04 | preop-data-intelligence, value-proposition-canvas, marketing-brain, access-welcome, gong-calls-explorer | 5 | 0 | 0 | 1513 -> 1420 | pending |
