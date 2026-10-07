<!-- last-reviewed: 2026-10-06 -->
# Webinar Automation (Riverside ↔ HubSpot ↔ Webflow)

**Status:** In production (first full run 2026-07-30; moved to GitHub Actions 2026-09-15, awaiting repo secrets before the first CI run, both still missing on 2026-10-06; live webinar entries and their HubSpot IDs live in [`tools/webinar-automation/config/webinars.json`](../../tools/webinar-automation/config/webinars.json)) · **Owners:** Hanan Amos, Jonathan Galili (API audit)

## What it is

The agent-driven replacement for the manual webinar setup playbook (11 steps, ~26 min across HubSpot, Webflow, Riverside Studio, and Customer.io).

Four human actions remain, and the README states the same four:

1. **Create the event in Riverside Studio** and hand over the link, the date and time, the subject and the guest. No API exists for event creation, proven at the router level, not assumed.
2. **Approve the drafted copy.** `/riverside-event-copy` writes the landing page fields and the three emails in Kendall's voice; nothing is built from unapproved copy.
3. **Preview and publish the Webflow landing page.** The agent drafts it as a Webinars CMS item duplicated from template item `687657b161f1ac622a212865` (`/page-build`, profile in `references/page-type-registry.md`); publishing stays human. First supervised write 2026-10-06, in the test launch.
4. **Turn the reminder workflow on**, after QA. A flow is created disabled every time.

`mode=create` leaves the emails as drafts carrying the approved copy and builds the reminder flow, disabled, pointing at those drafts. Until 2026-10-06 the pipeline skipped the flow until the emails were published, on the belief that a flow cannot reference an unpublished email; the first test launch showed HubSpot accepts it (flow `1897261642`, three draft emails, read back intact). Re-running with `mode=publish` publishes the emails and reuses the flow. The emails must be published before a person turns the flow on. Redrafted copy re-runs `mode=create`: it updates drafts, never a published email, and skips a draft someone edited in HubSpot unless `force_copy` is set.

As of 2026-09-15 it is wired to run in CI rather than on one laptop: credentials become repository secrets, any collaborator can launch a webinar, and the job commits the config entry back to `main` instead of leaving it in the launcher's worktree. **Not yet exercised.** The secrets do not exist yet, so no CI run has happened; until one does, treat the workflows as written but not proven.

## What runs

| Piece | Where | Status |
|---|---|---|
| Registrant + attendance sync agent | [`tools/webinar-automation/scripts/webinar-registrant-sync.js`](../../tools/webinar-automation/scripts/webinar-registrant-sync.js) | Proven on real contacts (portal 9154210) |
| Webinar orchestrator (emails, workflow, lists) | [`tools/webinar-automation/scripts/new-webinar.js`](../../tools/webinar-automation/scripts/new-webinar.js) | In production since 2026-07-30; per-webinar state in `tools/webinar-automation/config/webinars.json` (`created.*`) |
| Conversational launcher (A-to-Z entry point) | [`.claude/skills/launch-webinar/SKILL.md`](../../.claude/skills/launch-webinar/SKILL.md) | Live - paste a registration link or event ID, it drives intake → form clone → list → orchestrator with human gates |
| Webinar copy (landing page + 3 emails) | [`.claude/skills/riverside-event-copy/SKILL.md`](../../.claude/skills/riverside-event-copy/SKILL.md), applied by [`tools/webinar-automation/scripts/email-copy.js`](../../tools/webinar-automation/scripts/email-copy.js) | Added 2026-10-05, adapted from Kendall Breitman's skill. Copy reaches the Action as the `email_copy` input and is validated twice (intake and build). Offline tests: `scripts/test-email-copy.js`. Live-tested 2026-10-06 on a test event (local run of the branch code): draft emails created with the copy, a redraft applied to drafts, a hand edit protected, `--force-copy` overwrote it |
| Landing page draft | [`.claude/skills/page-build/SKILL.md`](../../.claude/skills/page-build/SKILL.md), "Webinar landing page (CMS item)" profile | Added 2026-10-05. Runs in the operator's Claude session via the Webflow MCP, after the `create` run commits the form GUID. First supervised write 2026-10-06 (test launch): a draft Webinars item and a draft Speaker item, every field re-read and matched |
| 7 contact properties + 3 dynamic lists | HubSpot portal | Live (`riverside_join_url`, `webinar_*` ×6; lists 23097-23099) |
| Launch workflow (anyone with repo access) | [`.github/workflows/webinar-launch.yml`](../../.github/workflows/webinar-launch.yml) | Added 2026-09-15, blocked on `HUBSPOT_PRIVATE_APP_TOKEN` as a repo secret. `workflow_dispatch` with plan/create/publish modes; refuses to write if the HubSpot token is not portal 9154210 |
| Sync schedule | [`.github/workflows/webinar-sync.yml`](../../.github/workflows/webinar-sync.yml) | Added 2026-09-15, every 30 min, blocked on both repo secrets. Replaces the desktop scheduled task, which only ran while the desktop app was open and has been disabled since 2026-08-12 |
| Form + intake list factory | [`tools/webinar-automation/scripts/ensure-hubspot-intake.js`](../../tools/webinar-automation/scripts/ensure-hubspot-intake.js) | Added 2026-09-15. Was an agent typing API calls by hand; now scripted, so an unattended run needs no operator. Dry-run paths tested locally; the create paths have not run against HubSpot yet |

## Key facts (hard-won, save yourself the failed runs)

- Riverside Business API base is `https://platform.riverside.com`, not what the docs imply. Registrant create/get is the entire webinar API surface; event creation is UI-only.
- HubSpot email layout can't be written via API for drag-and-drop templates; **coded templates** (created via the Design Manager API) carry layout in their own HTML and sidestep it entirely. `AUTOMATED_EMAIL` type is clone-only.
- Workflows must use **Flows v4** (`/automation/v4/flows`); the legacy v3 API silently drops enrollment triggers.
- Registration form + intake list are agent-created since 2026-07-30 (`forms` scope on the private app): clone the previous webinar's form (keep `createdAt`/`updatedAt` in the POST - stripping them 400s), then a DYNAMIC list on `FORM_SUBMISSION`/`FILLED_OUT` of the new GUID.
- HubSpot stores coded-template *labels* with an .html suffix appended - exact-label dedupe scans miss the existing template and 409 on the path (`new-webinar.js` matches both forms since 2026-07-30).
- `.env` is only for local debugging now. CI reads repo secrets, so the old advice to copy `.env` between worktrees is retired. Setup: [`tools/webinar-automation/docs/github-actions-setup.md`](../../tools/webinar-automation/docs/github-actions-setup.md).
- **Open blocker (2026-08-12):** the Riverside key returns `403 Event does not belong to this account` for the company's real webinars, so registration and attendance sync do nothing until a key on the hosting account is issued. The HubSpot half of the pipeline is unaffected.
- **Personal join links arrive late, or not at all.** The sync stamps `riverside_join_url` every 30 minutes, while the registration email sends the moment someone registers, so a form registrant's confirmation can never carry a personal link; with the 403 above, real webinars get none. Two mitigations since 2026-10-05: the drafted confirmation carries calendar links instead of a join button, and the optional `join_link_fallback` (the shared studio audience link) fills `[[JOIN_URL]]` through HubL `|default(..., true)` when the property is empty. The fallback is unverified against a real send; the job summary asks for a test send to a contact without a personal link.
- **Webinars CMS conventions** (read 2026-10-05 across the six most recent items): the page's time comes from the plain-text `hour` (24-hour) and `time-zone` fields, not from `date`; `youtube-id` holds the stream or replay and is empty until one exists; Kendall (`685be7dcd32275d3830676cb`) is a speaker on nearly every webinar.
- **The Riverside Claude connector (`mcp.riverside.com`) has no webinar or event tools** (checked 2026-10-06: 86 tools across editing, exports, hosting, media, social, and read-only productions, studios, projects and recordings). It also sees only the connecting user's own productions. Event details keep coming from the public `publicWebinarRegistrationData` lookup, and event creation stays in Studio.
- **The pipeline's event title is the registration form's title, not the event title** (found 2026-10-06 in the first test launch). `publicWebinarRegistrationData.title` kept the old name after the event itself was renamed in Studio, and changed only once the registration form's title field was updated. Its `description` arrives as editor HTML, which intake converts to plain text.
- **The Webinar Launch Action cannot test a pull request.** Its checkout step pins `ref: main`, so a dispatch runs the merged scripts whatever branch it starts from, and a `create` run commits back to `main`. Test a pipeline change before merge by running the branch's scripts locally against a test event (`/launch-webinar`, "Running the scripts directly"), as the 2026-10-06 test launch did.
- **No Apple Calendar link.** The pipeline builds Google, Outlook.com and Office 365 links. An .ics file would need hosting, and the private app has no file-upload scope.
- Full recipes and evidence: [`tools/webinar-automation/webinar-hubspot-agent-scope.md`](../../tools/webinar-automation/webinar-hubspot-agent-scope.md)

## Links

- Visual overview (artifact): https://claude.ai/code/artifact/6cf64399-a82e-4ab4-85b7-87bcf80a8013
- Open questions / API audit pack for Galili: [`tools/webinar-automation/galilei-audit-questions.md`](../../tools/webinar-automation/galilei-audit-questions.md)
- Monday task: https://riversidefm.monday.com/boards/18413613511/pulses/12659164292
