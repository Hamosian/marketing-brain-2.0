# GitHub Actions setup for the webinar pipeline

Two workflows run the webinar automation. Both read their credentials from repository
secrets, which is what makes the pipeline available to every collaborator instead of to one
laptop.

| Workflow | Trigger | What it does |
|---|---|---|
| [`webinar-launch.yml`](../../../.github/workflows/webinar-launch.yml) | Manual (`workflow_dispatch`) | Full setup for one webinar: config entry, registration form, intake list, 3 branded emails, reminder workflow (disabled), 3 follow-up lists. Commits the config entry back to `main`. |
| [`webinar-sync.yml`](../../../.github/workflows/webinar-sync.yml) | Every 30 minutes | Registers HubSpot list members into Riverside, backfills personalized join URLs, syncs attendance back to HubSpot. |

## Secrets to add

**Settings > Secrets and variables > Actions > New repository secret**, on
`riversidefm/marketing-brain`. Repo admin rights are required.

| Secret | Used by | Where the value comes from |
|---|---|---|
| `HUBSPOT_PRIVATE_APP_TOKEN` | both workflows | The existing HubSpot private app on portal `9154210`. Needs the granular scopes already in use: `forms`, marketing-email, lists, CRM-contacts, automation, design-manager. |
| `RIVERSIDE_API_KEY` | sync only | Riverside Business API key, issued through the CSM. See the account caveat below. |

`RIVERSIDE_API_BASE` is not a secret. It is set in the workflow to
`https://platform.riverside.com`, which is the real base despite what the public docs imply.

## The Riverside key has to be on the right account

As of 2026-08-12 the key in use returns `403 Event does not belong to this account` for
Riverside's own company webinars. It resolves fine for events created under the account the
key belongs to, which is why the test webinars worked and the first real one did not.

The consequence is worth stating plainly: the launch half of the pipeline works with the
HubSpot secret alone, but nobody gets registered into Riverside, and no attendance comes
back, until the key matches the account that hosts the real events. So
`HUBSPOT_PRIVATE_APP_TOKEN` unblocks most of the value immediately, and `RIVERSIDE_API_KEY`
is worth adding only once the account question is settled.

## Verifying it worked

1. Run **Webinar Launch** from the Actions tab with any registration link and `mode=plan`.
   A dry run writes nothing anywhere.
2. The first step fails loudly if the HubSpot token is missing or resolves to a portal
   other than `9154210`, so a wrong-portal token can never reach a write.
3. For the sync, run **Webinar Registrant Sync** manually once and read the log. Each
   webinar reports separately; one failing event does not stop the others.

## What still is not automated

- Creating the event in Riverside Studio. There is no API for it - confirmed by a
  router-level probe, not by guesswork.
- Turning the reminder workflow on. Deliberate gate, stays human.
- The Webflow landing page, inside the Action. It is drafted from the operator's own
  Claude session instead (`/launch-webinar` step 7, through the Webflow MCP), so the
  Action needs no `WEBFLOW_API_TOKEN`. Publishing it stays human either way.
