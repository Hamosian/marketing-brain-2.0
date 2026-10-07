# Questions for Galilei - Riverside API audit

Context: while scoping the v1 webinar→HubSpot sync agent (see `webinar-hubspot-agent-scope.md`), I found a HubSpot contact property called **`test_gal__webinar_join_url`**, populated on exactly 2 contacts (two internal test contacts; record identifiers redacted, available in HubSpot on request) with values like `https://riverside.fm/studio/gal---external?audienceToken=<uuid>`. That looks like a manual pilot of the exact idea below - personalizing each attendee's join link via the API instead of sending everyone to Riverside's shared registration page.

**Ask this first, before anything else:** what was `test_gal__webinar_join_url` testing, what came out of it, and is it safe to build on top of / rename for production use? No point re-deriving what's already been tried.

## On the core idea (auto-register + personalized join link)

1. Can a contact be registered via `create-registrant` and receive a working `join_url` **without ever visiting Riverside's own hosted registration page** - i.e. can that page be fully bypassed for all traffic, with HubSpot's form as the only registration surface?
2. In your `gal---external` test, did the `audienceToken` link work end-to-end (joins the live studio, tracks attendance under that identity)?
3. Is `/api/v3/events/{eventId}/registrants` (create + get) rate-limited at 1 req/sec as documented, and does that hold in practice for a webinar with a large registration spike right before start time?

## On API access itself

4. Is API access already provisioned for our account, or still pending CSM setup? (The quickstart says it's "restricted to select Business accounts" - the existing test property suggests *someone* already has a working key.)
5. Beyond the documented registrant create/get endpoints and webhooks, does the CSM confirm there's no private/beta endpoint for creating or scheduling the webinar event itself? That's the one gap that keeps event creation manual in v1.
6. Do webhooks (`registrant.created`, `attendee.joined`, `webinar.ended`) actually fire reliably in your account today, or are they unconfigured/untested?

## On data we already have

7. `guest_joined_studio`, `riverside_last_webinar_date`, and `riverside_last_webinar_last_viewed_at` already exist as HubSpot contact properties. Is something already syncing these today (a native integration, Zapier, manual import)? If so, what - so the new agent doesn't duplicate or conflict with an existing write path.
8. The `riverside_webinar_custom_field_*` properties (including the legal/consent checkbox text) suggest registrant custom fields already flow into HubSpot somehow. Same question - via what mechanism, and is it reliable enough to keep using?

## On the open branding/legal question from the call

9. If bypassing Riverside's hosted registration page (per #1) works, does that resolve the "how do we handle the consent checkbox / branding on Riverside's landing page" question from the call - since attendees would never see that page at all?

## FYI, not a question - confirmed HubSpot-side limitation (2026-07-29)

While testing whether an agent could build the registration/reminder emails end-to-end (content *and* layout) from the "Webinar 2026 agent" template: HubSpot's Marketing Email API will not accept a written `flexAreas` value (the field that defines which content block sits where on the page) - confirmed across 4 separate attempts (PATCH on an existing email, an isolated PATCH of just that field, POST-create referencing the template path only, and POST-create with a full known-good payload). All four silently returned an empty layout even though the *content* of each block saved correctly. So an email's visual layout can only be set by HubSpot's own visual editor, not by API - cloning or starting a new email from a template still has to be a manual UI click. Once that email exists, though, patching its subject/headline/body/button copy via API works perfectly and safely (draft-only). Worth mentioning if this comes up with HubSpot support/your rep, since it's a real product-API gap, not something we were doing wrong.

**Update 2 (later 2026-07-29) - the email-layout limitation is SOLVED too.** Coded email templates (created via the Design Manager API, `POST /content/api/v2/templates`) carry their layout in the template HTML itself, so `flexAreas` never comes into play; combined with clone-then-repoint (cloning any AUTOMATED email preserves its type, and `templatePath` persists on PATCH), the entire email pipeline is now API-pure. Verified end-to-end with throwaway objects, all deleted. The dnd-template limitation below still stands but no longer matters.

**For the CSM conversation - stronger evidence on Riverside:** a systematic router-level probe (empty-body POSTs, status-code signatures) confirmed NO hidden event-creation/read/webhook-management endpoints exist on our key: every candidate route 404s at the router ("Cannot POST /api/v3/events"), which is the route-not-registered signature, not an auth or validation error. Also: `GET /api/v3/productions` works (full workspace tree). So the asks are precisely: (a) an event create/read API, (b) a webhook-subscription CRUD API (setup today is dashboard-only - where is that dashboard for our account, and who has access?).

**Update - workflow automation turned out to be fully possible, just needed the right API.** First attempt used the legacy `/automation/v3/workflows` API and hit what looked like the same kind of silent-drop bug (the enrollment trigger came back empty after creation, even though `enabled: false` correctly persisted). Root cause: v3 is the *old* workflow system. Reading a real, live, enabled webinar workflow directly (`/automation/v4/flows/{id}`) confirmed current production workflows run on the newer **Flows v4 API**, which has a different but fully-working schema for both enrollment criteria and actions. Rebuilt the test workflow via v4 and everything - enrollment trigger, email-send action - persisted correctly on independent re-verification. So: only the email *layout* (not the workflow itself) is the real automation gap.
