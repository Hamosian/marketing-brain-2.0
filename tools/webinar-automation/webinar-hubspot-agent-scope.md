# Webinar → HubSpot Sync Agent - v1 Scope

Scoped 2026-07-29, based on the 2026-07-29 webinar-setup call and a review of `docs.riverside.fm` (API + webhooks) and the Webinar Setup Playbook (Google Doc). Covers only what's automatable **today**, without waiting on Galilei's Riverside API audit.

## Credentials: HubSpot private app scopes (verified via token introspection 2026-07-30)

One private app token (app `47374002`, portal `9154210`) runs the whole pipeline. Scopes on the token today and what each powers:

| Scope | Powers |
|---|---|
| `content` | Coded email template creation (Design Manager `POST /content/api/v2/templates`) |
| `marketing-email` | Clone/edit/publish the 3 automated emails (`/marketing/v3/emails`) |
| `automation` | Create + update the Flows v4 workflow (`/automation/v4/flows`) |
| `crm.lists.read`, `crm.lists.write` | The 3 dynamic lists; list-membership reads in the sync agent |
| `crm.objects.contacts.read`, `crm.objects.contacts.write` | Contact search, `webinar_*` field + join-URL writes, contact-creation backstop |
| `crm.schemas.contacts.write` | Creating the custom `webinar_*` contact properties |
| `oauth` | Token introspection only |

**Missing: `forms`** - the one scope keeping the registration-form clone manual (see "What stays manual" below). Add it to the private app to unlock the clone recipe. The non-HubSpot credential is `RIVERSIDE_API_KEY` (Business API bearer, via CSM) for registrant creation + attendance sync.

**Visual overview (shareable):** https://claude.ai/code/artifact/6cf64399-a82e-4ab4-85b7-87bcf80a8013 - end-to-end showcase of the pipeline: stages, the 7 new contact fields, live proof, and remaining decisions. Private by default; share from the page's share menu before sending to teammates.

**v1 build artifacts:** [`scripts/webinar-registrant-sync.js`](scripts/webinar-registrant-sync.js) (the agent itself), [`galilei-audit-questions.md`](galilei-audit-questions.md) (open items to fold into the audit), and [`hubspot-workflow-webhook-action.md`](hubspot-workflow-webhook-action.md) (a no-code fallback/comparison - native HubSpot workflow webhook instead of the polling script; not recommended as the default, see its bottom section for why).

**Live finding while scoping this:** the HubSpot portal already has a contact property `test_gal__webinar_join_url`, populated on 2 contacts with values like `https://riverside.fm/studio/gal---external?audienceToken=<uuid>`. Someone (Galilei, per the naming) has already manually piloted the exact join-URL-personalization idea below. There are also existing properties (`guest_joined_studio`, `riverside_last_webinar_date`, `riverside_last_webinar_last_viewed_at`, several `riverside_webinar_custom_field_*` including the consent checkbox text) that suggest *some* registrant/custom-field sync already reaches HubSpot today. **Talk to Galilei about this pilot and whatever populates those fields before building v1** - this may already be partly solved or actively in progress. See `galilei-audit-questions.md` for the specific questions.

## The real integration gap (not just "list sync")

Reading the Playbook closely: registrants don't go through Riverside's registration API at all today. They fill out the **HubSpot form embedded on the Webflow page** (creates a HubSpot contact, triggers the email workflow). The reminder emails then link out to a **separate Riverside Studio registration/join URL** - Riverside's own registration surface.

That means an attendee coming through the intended funnel (the Webflow form) effectively registers twice, in two systems whose only native bridge is a thin contact-creation sync (see the live-verified finding below). An attendee who signs up directly on the Riverside page registers once, but misses the email workflow entirely:
1. HubSpot contact (from the Webflow form) - owns email automation, CRM data, branding.
2. Riverside registrant (from clicking through to Riverside's own page) - owns the live join experience and attendance data.

This is exactly the "data and branding issues" and "clunky, basic list syncing only" from the call. The native integration creates bare contacts (that's the "basic list syncing"), but attendance data (did they show up, how long, no-show), join URLs, and workflow enrollment never make it across without the agent - attendance previously required a manual export.

**Live-verified 2026-07-30: Riverside's native HubSpot integration DOES auto-create contacts for registration-page signups.** A test registration on the Riverside-hosted page created the HubSpot contact ~3 minutes later (`hs_object_source: INTEGRATION`, `hs_object_source_detail_1: Riverside`) with name + email only - no `webinar_*` fields, no join URL, no list membership, and critically **no workflow enrollment** (the form-based flow trigger never fires because a Riverside-page registrant never touches the HubSpot form). So the two registration paths differ: Webflow-form signups get the email workflow and land in the form list but need the sync agent to become Riverside registrants; Riverside-page signups exist in both systems from the start (bare contact via the native integration) but need the sync agent for `webinar_*` fields, the join URL, and - via the flow's property-based second enrollment branch (`webinar_name` equals the event) - the reminder sequence. Consequences: (a) the sync script's create-contact-for-unmatched-registrants path mostly acts as a backstop, but it must still tolerate the native integration racing it; (b) without that second enrollment branch, Riverside-page registrants get no emails at all; (c) `webinar_*` field population for such registrants lags by up to one sync-cron interval.

**The v1 agent's job: eliminate the second registration entirely, and pipe attendance data back automatically.**

## Design: register-once, bridge attendance back

### 1. Auto-register into Riverside, on a schedule - no workflow changes needed
Originally scoped this as a Webhook/Custom Code action added to the HubSpot workflow itself. Turns out it doesn't need to touch the workflow at all: `GET .../registrants` returns `join_url` per registrant too, so **the same polling agent that syncs attendance can also own registration**, by running one extra pass first:

- Search the webinar's HubSpot list for contacts missing the join-url property (i.e. registered in HubSpot, not yet registered in Riverside).
- Call Riverside `POST /api/v3/events/{eventId}/registrants` for each (email, first/last name + any custom fields already on the HubSpot form).
- `{eventId}` is a single static config value per webinar - the same ID the team already copies manually today, just entered once in the agent's config instead of pasted around.
- Write the returned `join_url` straight back to the contact property.

This drops the "does the HubSpot workflow tier support webhook actions with response-mapping" dependency entirely - it was the shakiest assumption in the original design, and it's no longer needed. `scripts/webinar-registrant-sync.js` implements this as `backfillJoinUrls()`.

### 2. Personalize every CTA with that join_url
Registration + both reminder emails use `{{ contact.riverside_join_url }}` as the CTA instead of the shared/generic Riverside registration link. Effects:
- The attendee never sees a second, Riverside-branded registration form - single branded experience end to end.
- Each attendee gets a unique, trackable join link (cleaner attendance attribution, no shared-link ambiguity).
- This fix lives in the **template**, so once built it costs zero extra manual work per webinar - it's inherited automatically every time Step 6 ("clone the workflow") happens.

### 3. Sync attendance data back to HubSpot (replaces the manual CSV export)
Scheduled agent (cron-based, see Architecture below) polls Riverside per active/recent event:
- `GET /api/v3/events/{eventId}/registrants?updated_after={last_sync_ts}` - cursor-paginated, incremental.
- For each changed registrant, match by email to the HubSpot contact and update properties:
  - `webinar_attended` (bool, from `participated`)
  - `webinar_attendance_duration`, `webinar_attendance_rate`
  - `webinar_no_show` (bool, from `registrant.did_not_attend` / `participated: false`)
  - `webinar_registered_at`
- One run ~1 hour after the event's `webinar.ended` time does a final sweep to catch late data.
- Track `last_sync_ts` per event as simple state (a HubSpot property on a "webinar" record, or a small state file) so re-runs are idempotent.

### 4. Generate calendar links directly - drop the Customer.io tool
Google/Outlook/Office 365 "add to calendar" links are just URL templates (`calendar.google.com/calendar/render?action=TEMPLATE&text=...`, etc.) - no API or third-party tool needed. The agent builds all three from the event title/description/location(join_url)/start/end/timezone at workflow-setup time. Removes an entire manual step (and an extra system) from the Playbook's Step 7.

## What stays manual in v1 - and why

| Step | Why it's not in v1 |
|---|---|
| Creating the Riverside Studio event itself | **Definitively impossible via API - proven at the router level 2026-07-29.** Systematic probe of every plausible route (`GET/POST /api/v3/events`, `/webinars`, `/studios/{id}/events`, etc.) returned NestJS router-level 404s ("Cannot POST /api/v3/events") - the "route not registered" signature, not auth/method/validation errors. No hidden endpoint exists. Remains one click in Riverside UI, **or browser automation via Claude-in-Chrome** (user's logged-in session). Bonus finding: `GET /api/v3/productions` works and returns the full workspace tree (productions → studios → projects) - useful for discovery. Webhook management is dashboard-only (no CRUD API). |
| Publishing the Webflow CMS webinar item + speaker record | **Drafting is agent-owned since 2026-10-05; publishing stays human.** Site id `685be7dcd32275d3830651d3`, Webinars collection `685be7dcd32275d38306553f`, Speakers `685be7dcd32275d383065563`. `/launch-webinar` step 7 drafts the item through `/page-build`'s "Webinar landing page (CMS item)" profile (`references/page-type-registry.md`), duplicated from template item `687657b161f1ac622a212865` with the new `hubspot-form-id`. Create lands items as drafts, invisible until publish; `publish_collection_items` goes straight to live riverside.com, and agents never call it. First supervised write 2026-10-06, in the test launch. |
| ~~Cloning the HubSpot form itself~~ | **SOLVED 2026-07-30 - `forms` scope added to the private app, clone recipe live-verified.** See "Form clone + intake list factory" below. |
| Turning the workflow ON | Intentional human gate - the Playbook is explicit that "built" ≠ "ready." Keep this a manual decision regardless of what else is automated. |
| ~~Creating each email's layout~~ | **SOLVED 2026-07-29 - no longer manual.** See "Coded-template email factory" above. The earlier flexAreas findings still hold for dnd templates, but coded templates don't use flexAreas at all. |

## Form clone + intake list factory (live-verified 2026-07-30, first production run)

With the `forms` scope on the private app, the per-webinar registration form and its intake list are fully agent-created - no HubSpot UI clicks:

1. **Clone the seed form:** `GET /marketing/v3/forms/{seedGuid}` (any previous webinar's `hubspotFormId` from `config/webinars.json` works as seed) → strip **only `id` and `archived`** → set the new `name` (convention: `Webinar: <event title>`) → `POST /marketing/v3/forms`. **Gotcha:** do NOT strip `createdAt`/`updatedAt` - the POST schema requires them present (returns 400 `Some required fields were not set: [createdAt]`); HubSpot ignores their values and stamps its own. Stripping `archived` is fine - the POST succeeds without it (verified live 2026-07-30, despite API schemas that suggest it is required).
2. **Create the intake list** (`hubspotListId`, the list `webinar-registrant-sync.js` polls): `POST /crm/v3/lists` with `processingType: "DYNAMIC"`, `objectTypeId: "0-1"`, and a filter branch of `{ filterType: "FORM_SUBMISSION", formId: <new GUID>, operator: "FILLED_OUT" }` in the standard OR→AND nesting. Submissions then land in the list automatically. (The original Hanan Test list 23096 was a MANUAL/static test shortcut - don't copy that shape for production.)
3. Write both IDs into the webinar's config entry (`hubspotFormId`, `hubspotListId`).

**Resumability:** these POSTs are not idempotent. Write each ID into `config/webinars.json` immediately after its POST succeeds (form first, then list), and on any retry search HubSpot by name (`Webinar: <event title>` / `<eventStem> - Form Submissions`) before POSTing, so a half-completed run reconciles instead of creating duplicates.

First production use: "Happy Webinar Agent Showcase" - form `4d23e3cb-6e42-41a0-b621-1d8656d607a4`, list `23143`.

## Coded-template email factory (SUPERSEDES the reusable-masters plan - zero clicks)

Probe-verified 2026-07-29 (parallel workflow run, all test objects deleted): the layout gap is closed **entirely via API** by sidestepping drag-and-drop templates altogether.

1. **Create a CODED email template via the Design Manager API** - `POST /content/api/v2/templates` with `template_type: 2, category_id: 2`, source = fixed brand HTML (logo, colors, footer) + named HubL module slots (`{% module "headline" path="@hubspot/rich_text" ... %}` etc., incl. `@hubspot/email_footer` for CAN-SPAM/unsubscribe). Works with the existing token, no extra scope. Coded templates carry layout in the HTML file - `flexAreas` is simply null/irrelevant. **Gotcha:** HubSpot rewrites the stored `path` from the *label* (spaces kept, `.html` stripped) - always re-GET the template and use the returned `path`. **Second gotcha (hit live 2026-07-30):** the stored *label* itself comes back with `.html` APPENDED (`"...v1.html"` for a template created as `"...v1"`), so any dedupe scan matching on the exact label misses the existing template and the re-POST 409s on the path. `new-webinar.js` matches both label forms since 2026-07-30.
2. **Get an AUTOMATED_EMAIL shell by cloning any existing automated email** (`POST /marketing/v3/emails/clone`). This is the *only* route to the AUTOMATED type - `POST` and `PATCH` both silently ignore `type`/`subcategory` (confirmed twice, fresh-GET verified).
3. **Re-point the clone to the coded template** - `PATCH` with `content.templatePath` (persists!) + full `widgets` keyed by the template's module names. The clone's old dnd widgets are cleanly replaced.
4. Verify by fresh GET; publish when approved (`POST .../publish` - keep human-gated); full rollback surface exists (`/revisions`, `/revisions/{id}/restore`, `/unpublish`, `/draft/reset`).

Template is created once per design and reused for every webinar. `scripts/new-webinar.js` implements the whole pipeline (template → 3 emails → flow → lists → calendar links) with dry-run default and explicit `--create` / `--publish-emails` gates.

## Workflow automation: use Flows v4, not legacy v3

First attempt used `/automation/v3/workflows` - `enabled: false` persisted, but the enrollment trigger (`segmentCriteria`) silently came back empty on re-fetch, same failure shape as the email layout bug. Root cause: v3 is HubSpot's *old* workflow system. Reading a real, live, enabled production webinar workflow directly (`GET /automation/v4/flows/{id}`) confirmed current workflows run on the newer **Flows v4 API**, with a different but fully-working schema:
- `enrollmentCriteria.listFilterBranch` (same nested OR→AND filter-branch shape as List creation) instead of `segmentCriteria`
- `actions` use `actionTypeId` codes (`"0-4"` = send email, referencing the email's own `content_id`; `"0-35"` = delay) instead of the old `type: EMAIL`/`type: DELAY` shape
- Webinar reminders use an **absolute scheduled timestamp** (`date.staticValue`, epoch ms) for the delay, not a relative delay from enrollment - everyone gets reminded at the same calendar moment, not N days after their own signup

Recreated the test workflow via v4 (id `1858980931`) with a real form-submission enrollment trigger and a real send-email action - both independently verified to persist correctly. So workflow creation, triggers, and email-send actions are all genuinely automatable - and since the coded-template factory above closed the layout gap, the entire email + workflow chain is zero-click.

**Updating an existing v4 flow (live-verified 2026-07-30):** `PATCH /automation/v4/flows/{id}` returns 405 - partial updates don't exist. The working recipe is GET the full flow, mutate it, and `PUT /automation/v4/flows/{id}` with the complete object (including the `revisionId` you fetched); success bumps `revisionId` and a fresh GET confirms persistence. Used this to add a second OR enrollment branch (`PROPERTY webinar_name IS_EQUAL_TO <eventStem>`) alongside the form-submission trigger, so Riverside-page registrants - who never touch the HubSpot form - still get the reminder sequence once the sync agent stamps `webinar_name` on them. `new-webinar.js` now creates flows with both branches by default. Caveat: property-branch enrollees skip the "instant" confirmation feel - enrollment lags registration by up to one sync-cron interval, and the confirmation email still sends as action 1 on enrollment.

## Architecture: polling vs. webhook relay

**v1 recommendation: polling, via a scheduled cron agent.** Riverside webhooks need a publicly reachable HTTPS endpoint to push to - that's infrastructure beyond what a Claude Code agent runs natively. A cron-scheduled agent (e.g. every 30 min during a live registration window, plus one sweep an hour after the event ends) hitting `GET .../registrants?updated_after=...` gets the same outcome with no new infra, at the cost of some minutes of latency. Good enough for CRM sync and post-event reporting.

**v2, only if near-real-time matters:** a small hosted webhook receiver (Cloudflare Worker / Vercel function) that verifies Riverside's HMAC signature and relays `attendee.joined` / `webinar.ended` events immediately - worth it only if the team wants a live "who just joined" view during the event itself. Not needed for the CRM-sync use case.

## Open items to verify - full list in `galilei-audit-questions.md`

Top priority: find out what `test_gal__webinar_join_url` and the existing `riverside_last_webinar_*` / `riverside_webinar_custom_field_*` properties already do before building on top of them. Beyond that: whether `join_url` can fully substitute for Riverside's hosted registration page, whether webhooks actually fire reliably today, and how to handle a registrant whose HubSpot and Riverside emails don't match.

## Suggested build order

1. Sync with Galilei on the existing pilot property and whatever populates `guest_joined_studio` / `riverside_last_webinar_*` today - avoid duplicating or clobbering it.
2. Wire up real credentials (`RIVERSIDE_API_KEY`, `RIVERSIDE_API_BASE`, `HUBSPOT_PRIVATE_APP_TOKEN`) and a `config/webinars.json` entry for one real webinar; dry-run `scripts/webinar-registrant-sync.js` against it.
3. Decide whether to productionize `test_gal__webinar_join_url` (rename) or create a fresh property - either way, add it as the CTA personalization token in the registration + reminder emails.
4. Schedule the script (CronCreate / GitHub Actions / existing infra) - every 15-30 min during a live registration window, plus a sweep ~1hr after `webinar.ended`.
5. Swap in generated calendar links, drop the Customer.io tool from the Playbook.
6. Re-time the Playbook: steps 3-5 (Webflow) are agent-drafted and human-published as of 2026-10-05, and 11 (test + enable) remains manual; everything else - form clone, emails, workflow, lists - is agent-owned as of 2026-07-30.
