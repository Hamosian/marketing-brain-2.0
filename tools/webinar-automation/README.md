# Marketing Agents OS

Automation agents for Riverside's marketing operations.

## Webinar automation pipeline (Riverside ↔ HubSpot ↔ Webflow)

Replaces the manual ~26-minute, 11-step webinar setup with an agent-driven pipeline. Four human actions remain: create the event in Riverside Studio (no API exists), approve the copy `/riverside-event-copy` drafts, preview and publish the Webflow landing page the agent drafts as a CMS item (first supervised write 2026-10-06), and switch the workflow on after QA. As of 2026-09-15 it is wired to run as GitHub Actions rather than local scripts, so anyone with repo access can launch a webinar. That path is not proven yet: it needs the repo secrets in `docs/github-actions-setup.md`. Everything else runs itself - live-verified 2026-07-29, first full production run 2026-07-30. The HubSpot registration form clone and its intake list are agent-created since 2026-07-30 (`forms` scope added; recipe in the scope doc).

| Piece | Path | What it does |
|---|---|---|
| Sync agent | `scripts/webinar-registrant-sync.js` | Auto-registers HubSpot contacts into Riverside, backfills personalized join links, syncs attendance back, auto-creates contacts for registrants HubSpot has never seen |
| Intake | `scripts/add-webinar.js` | Paste a registration link (or event ID): resolves title, host, and exact schedule from Riverside's public registration data and writes the config entry. Optional `--expect-start` (stops on a mismatch with the requestor's time), `--copy-file`, `--join-fallback`. Conversational wrapper: the `launch-webinar` skill |
| Intake (HubSpot) | `scripts/ensure-hubspot-intake.js` | Clones the registration form from the most recent webinar's form and creates its DYNAMIC intake list. Reconciles by name before every create, so a retry never duplicates. Dry-run by default; `--create` executes |
| Orchestrator | `scripts/new-webinar.js` | One command per webinar: branded coded email template → 3 automated emails → disabled Flows v4 workflow → 3 dynamic lists → calendar links. Dry-run by default; `--create` and `--publish-emails` are explicit gates; never enables a flow. Applies the entry's `emailCopy` when present; changed copy updates drafts only, and `--force-copy` is needed to overwrite a hand edit |
| Email copy rules | `scripts/email-copy.js` | Validates drafted copy (all three emails, no em or en dashes, no emojis, no HubL statements, known placeholders only) and resolves `[[JOIN_URL]]` and the calendar-link placeholders. Shared by intake and orchestrator |
| Tests | `scripts/test-email-copy.js` | Offline: fakes HubSpot and Riverside, runs in a temp copy of this folder. `node scripts/test-email-copy.js` |
| Config | `config/webinars.json` | One entry per webinar: event ID, form ID, schedule, reminder times, property mapping |
| Architecture & verified API recipes | `webinar-hubspot-agent-scope.md` | The full design, every live-verified recipe, and the confirmed platform limitations |
| Audit questions | `galilei-audit-questions.md` | Open questions + evidence pack for the Riverside API audit and CSM conversation |
| Workflow-webhook alternative | `hubspot-workflow-webhook-action.md` | Documented no-code fallback (not the recommended path) |

### Setup

**In CI, which is how this normally runs, there is nothing to set up.** Both workflows read
`HUBSPOT_PRIVATE_APP_TOKEN` and `RIVERSIDE_API_KEY` from repository secrets, so every
collaborator can launch a webinar without holding a credential. See
[`docs/github-actions-setup.md`](docs/github-actions-setup.md).

For local debugging only: Node >= 18 and a `.env` file (never committed) in this directory.
`scripts/load-env.js` parses it as literal KEY=VALUE text with no shell evaluation, and
values already present in the environment win, which is exactly how the Action injects
secrets.

```dotenv
RIVERSIDE_API_BASE=https://platform.riverside.com
RIVERSIDE_API_KEY=<Riverside Business API key, via CSM>
HUBSPOT_PRIVATE_APP_TOKEN=<private app token, see scopes in webinar-hubspot-agent-scope.md>
```

Do not hunt for a `.env` in sibling worktrees and copy it. That was the workaround for a
laptop-bound pipeline, and it is retired: run the Action instead.

The HubSpot private app needs the `forms` granular scope (added 2026-07-30) on top of the
marketing-email, lists, CRM-contacts, automation, and design-manager scopes already in use.

### Reminder time semantics

`reminders.*.date` is a calendar date sent to HubSpot as a midnight-UTC epoch (`date.staticValue`); `hour`/`minute` are clock time interpreted by HubSpot in the portal's default timezone (Flows v4 `time_of_day` semantics, matching the team's production webinar workflows). Neither depends on the machine's local timezone.

### Scheduling

The sync runs every 30 minutes from `.github/workflows/webinar-sync.yml`. The desktop
scheduled task that used to do this is superseded: it only ticked while the Claude desktop
app was open, and it has been disabled since 2026-08-12.

### Visual overview

End-to-end showcase (pipeline, contact tracking fields, live proof): https://claude.ai/code/artifact/6cf64399-a82e-4ab4-85b7-87bcf80a8013
