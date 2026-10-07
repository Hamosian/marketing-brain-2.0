# Option A - Native HubSpot Workflow Webhook Action

A no-code alternative to `scripts/webinar-registrant-sync.js`'s `backfillJoinUrls()`: call Riverside's Create Registrant endpoint directly from the HubSpot workflow, instead of polling. Documented here as a fallback/comparison - **default to the script (Option B) for v1** (see recommendation at the bottom); build this only if instant registration turns out to matter.

**Verify against your actual HubSpot subscription before relying on this** - workflow action availability and the response-mapping feature are tier-gated and change over time; nothing below has been tested against a live account.

## Where it goes in the existing workflow

Same master workflow template the Playbook already clones per event (Step 6). Insert one new action:

```text
Form submission (trigger)
  → [NEW] Webhook action - call Riverside create-registrant
  → Send email: registration
  → Delay: day before
  → Send email: first reminder
  → Delay: event day
  → Send email: second reminder
```

## Webhook action configuration

| Field | Value |
|---|---|
| Method | `POST` |
| URL | `https://platform.riverside.com/api/v3/events/{eventId}/registrants` - `{eventId}` is a static value, set once per cloned workflow (same ID currently copied manually) |
| Headers | `Authorization: Bearer <token>` - **never paste the raw Riverside API key into a HubSpot workflow.** Route the call through a secret-managed relay (e.g. a serverless function that holds the key) so the credential stays inside the documented `.env`/secret boundary. |
| Body | `{"email": "{{ contact.email }}", "first_name": "{{ contact.firstname }}", "last_name": "{{ contact.lastname }}"}` |

**Response mapping** (if your workflow tier supports "use webhook response to update properties" - confirm this exists on your account): map response field `join_url` → contact property `riverside_join_url` (or whichever name Galilei's pilot settles on - see `galilei-audit-questions.md`).

**If response mapping isn't available:** fall back to Option B's script running right after, picking up the newly-created registrant via `GET .../registrants` and writing `join_url` back - a hybrid where the workflow handles registration timing and the script only handles the write-back.

## Failure handling

Two known failure modes the workflow needs a branch for:

- **409 (already registered)** - happens on any workflow re-enrollment or test resend. The branch must NOT skip straight to the send: it must first reconcile via `GET .../registrants`, fetch the existing registrant's `join_url`, and write it to the contact. Only continue once `riverside_join_url` is verifiably populated - the email CTA depends on it.
- **401/5xx** - relay credential invalid or Riverside outage. Do NOT continue to the send (the email would carry an empty or stale join link): halt the workflow at this step and alert (Slack notification via a workflow action). Resume only after registration succeeds and the property is populated.

Confirm your workflow tier actually exposes conditional branching off a webhook action's success/failure before committing to this design - some tiers only support success paths.

## Option A vs. Option B comparison

| | A: Native workflow webhook | B: Polling script |
|---|---|---|
| Registration latency | Near-instant | Up to the poll interval (e.g. 15-30 min) |
| Setup effort | One-time template edit, no code | Script + config + scheduling (already built) |
| Tier dependency | Needs webhook action + response-mapping on your HubSpot subscription (unconfirmed) | None - works on any tier via API token |
| Error visibility | Limited to what the workflow's branching UI exposes | Full console/log output, easy to extend (Slack alert, retry, dedupe) |
| Idempotency (409 handling) | Needs a manual failure-branch | Already built in - only processes contacts missing `join_url` |
| Attendance sync-back | Still needs Option B (or a second webhook on `webinar.ended`, which needs a public receiver) | Already built in (`syncAttendance()`) |

## Recommendation

Ship Option B first - it already handles both registration and attendance sync, needs no HubSpot tier verification, and gives real error logging. Revisit Option A later only if the team specifically wants sub-minute registration (e.g. so a "join now" link is valid within seconds of form submit rather than tens of minutes) - and even then, keep Option B's attendance-sync half, since that part has no native-workflow equivalent without standing up a public webhook receiver.
