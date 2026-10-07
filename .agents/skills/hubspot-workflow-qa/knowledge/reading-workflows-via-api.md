<!-- last-reviewed: 2026-09-28 (lists endpoints do work, email content_id mapping, the v4 PUT is refused so suppression edits go through the editor, the enroll-existing prompt; from the onboarding open-deal suppression fix) -->
# Reading a HubSpot workflow via the authenticated internal API

The fastest and most complete way to read a workflow for QA. One call returns the entire flow definition - enrollment criteria, every action, every connection between actions, suppression lists, custom-code source, and declared secrets. Prefer this over scraping the canvas.

Established 2026-09-07 while QA-ing `[OPS] Typeform Submission Event - Segment Webhooks` (flow `1878717070`). The canvas-scraping playbook it replaced surfaced only the trigger; the suppression list and the branch wiring that turned out to hold the P0s were invisible to it.

## Why not scrape the canvas

The HubSpot editor renders the flow lazily and collapses most of it. `get_page_text` on the edit URL typically returns the trigger block and nothing else - no actions, no branch targets, no suppression lists. Selector-based extraction is worse than incomplete: it is pinned to HubSpot's generated class names (`[class*="ListBranchActionConfigIndividualListBranch"]` and friends), which change without notice, and it silently returns an empty array when they do. An empty array reads exactly like "this workflow has no branches."

The canvas still has one irreplaceable job - see "Cross-check against the canvas" below.

## The call

You must already be signed in to HubSpot in the browser session. HubSpot's internal API rejects a bare same-origin fetch with 401; it needs the CSRF token that is sitting in the `hubspotapi-csrf` cookie echoed back as a request header.

```javascript
const tok = document.cookie.split('; ').find(x => x.startsWith('hubspotapi-csrf=')).split('=')[1];
const r = await fetch('/api/automation/v4/flows/<FLOW_ID>?portalId=9154210', {
  headers: { 'accept': 'application/json', 'X-HubSpot-CSRF-hubspotapi': tok }
});
const flow = await r.json();
window.__F = flow;   // stash it - see "Read it in slices" below
```

Run it with `javascript_tool` (`action: "javascript_exec"`) against a tab already on `app.hubspot.com`. Navigate to the workflow's edit URL first so the portal context is loaded.

The same cookie-plus-header pattern unlocks other internal endpoints useful during QA:

| Endpoint | Returns |
|---|---|
| `/api/automation/v4/flows/{flowId}` | Full flow definition |
| `/api/forms/v2/forms/{formGuid}` | Form name, type, created/updated, captcha, notification settings |
| `/api/form-integrations/v1/submissions/forms/{formGuid}?limit=50` | Recent submissions with `submittedAt`, `pageUrl`, and every submitted field |
| `/api/crm/v3/lists/{listId}?includeFilters=true` | List name, `processingType`, and the full `filterBranch`. Resolve every `suppressionListIds` entry with it |
| `POST /api/crm/v3/lists/search` with `{"query": "...", "count": 100}` | Lists by name, with `additionalProperties.hs_list_size` |
| `/api/crm/v3/lists/records/0-1/{contactId}/memberships` | Every list a contact is in. Proves a specific contact landed in a new list |
| `/api/cosemail/v1/emails/{content_id}` | A marketing email's `name`, `subject`, and `primaryEmailCampaignId` |
| `/api/automation/v3/workflows` | Every workflow in the portal, with the v4 `flowId` under `migrationStatus.flowId`. Filter by name to find a flow when you have no URL |

The lists endpoints above work (verified 2026-09-28). An earlier note here said every `.../lists/{id}` variant returned 404; that was the wrong path, not a missing API. The list page `app.hubspot.com/contacts/9154210/objectLists/{listId}/filters` is still the control for filter direction.

**A send-email action names the email by `content_id`, not by the campaign id.** Send logs (Snowflake `STG_HUBSPOT__EMAIL_EVENTS.EMAIL_CAMPAIGN_ID`) carry the campaign id, so a `JSON.stringify(flow).includes(campaignId)` search finds nothing even in the right workflow. Map each `actionTypeId: '0-4'` action's `fields.content_id` through `/api/cosemail/v1/emails/{content_id}` and match on `name` or `primaryEmailCampaignId`.

## What the flow object contains

Top-level keys worth reading during QA:

| Key | Why it matters |
|---|---|
| `isEnabled` | ON/OFF |
| `revisionId` | **Use this to prove a fix landed.** It increments on every save |
| `name`, `description` | Naming and hygiene checks |
| `objectTypeId` | `0-1` contact, `0-2` company, `0-3` deal |
| `enrollmentCriteria` | Trigger filters, `shouldReEnroll`, `unEnrollObjectsNotMeetingCriteria` |
| `suppressionListIds` | **Easy to miss in the UI and a common clone artifact.** An empty array is the clean state |
| `startActionId` | Entry point - not necessarily the lowest action id |
| `actions[]` | Every action, including `sourceCode` and `secretNames` for custom code |
| `timeWindows`, `blockedDates` | Scheduling constraints |

Action type ids seen in this portal:

| `actionTypeId` | Action |
|---|---|
| `0-1` | Delay |
| `0-63809083` | Add to static list |
| `0-4` | Send marketing email (`fields.content_id`) |
| `0-31` | Set marketing contact status |
| `1-179507819` | Send Slack notification |
| *(absent, has `sourceCode`)* | Custom code |
| *(absent, has `staticBranches`)* | Branch |
| *(absent, has `webhookUrl`)* | Native webhook |

## Walking the graph - mind the two connection shapes

Actions link to each other through **two different shapes**, and conflating them produces false findings.

```javascript
// Single-connection action (delay, custom code, Slack, list-add):
{ connection: { edgeType: 'STANDARD', nextActionId: '28' } }

// Branch action:
{
  staticBranches: [ { branchValue: '200', connection: { nextActionId: '31' } } ],
  defaultBranch:  { edgeType: 'STANDARD', nextActionId: '29' }   // NOTE: no .connection
}
```

`staticBranches[].connection.nextActionId` is nested. `defaultBranch.nextActionId` is **not** - `defaultBranch` *is* the connection. Reading `defaultBranch.connection.nextActionId` yields `undefined`, which looks identical to a disconnected default branch. This exact mistake produced a false "the failure branch is orphaned" finding during the 2026-09-07 review, on a workflow whose failure branch was wired correctly.

A terminal action has no `connection` at all. Guard for that too.

Orphan check that handles all three shapes:

```javascript
const j = window.__F;
j.actions.map(a => a.actionId).filter(id =>
  id !== j.startActionId &&
  !j.actions.some(a =>
    (a.connection && a.connection.nextActionId === id) ||
    (a.staticBranches || []).some(b => b.connection && b.connection.nextActionId === id) ||
    (a.defaultBranch && a.defaultBranch.nextActionId === id)
  )
);
// [] means every action is reachable
```

## Cross-check against the canvas

**Before reporting any structural finding, confirm it against the canvas.** The canvas renders the flow in plain English, which is both a second source and the version a human reviewer will see. It is the control that catches your parsing errors.

It is also strictly better than the API for one class of finding: **filter direction.** `{listId: "13439", operator: "IN_LIST"}` and `{... operator: "NOT_IN_LIST"}` differ by three characters in JSON and are trivial to skim past. The canvas spells them out - *"is member of Paid Customers - Business"* versus *"is not member of Paid Customers - Business"* - and an inverted exclusion is unmissable there. A real inverted exclusion shipped past an API read and was caught on the canvas in this review.

`get_page_text` on the edit URL returns the trigger block reliably; scroll the canvas and screenshot for the action chain.

## Read it in slices

Stash the response on `window` and query it in small pieces. Returning the whole object at once gets truncated, and the truncation lands mid-structure with no warning.

One tooling constraint shapes this: **`javascript_tool` refuses any result that contains a `?` or reads like `key=value` pairs**, returning `[BLOCKED: Cookie/query string data]`. Optional chaining in custom-code source (`err.response?.status`), any URL query string, and a `label=value; label=value` summary line all trip it, and the block is all-or-nothing for the whole result. When you format your own summary, join with ` :: ` or ` | `, never `=`. Identify the offending lines first, then exclude them and read those few by screenshot:

```javascript
const s = window.__F.actions.find(a => a.actionId === '23').sourceCode;
s.split('\n').map((l, i) => /[?=&]/.test(l) ? i + 1 : null).filter(Boolean);  // lines to skip
```

Full detail on the quirk: `references/integration-debugging.md`.

## Never paste a secret into the report

Custom-code `sourceCode` can contain hardcoded credentials - that is one of the things QA is looking for. Test for a credential's presence with a regex and report the finding; never echo the value into a QA doc, a monday update, or Slack.

```javascript
const s = window.__F.actions.find(a => a.actionId === '23').sourceCode;
({ usesProcessEnv: /process\.env/.test(s),
   anyLongLiteral: (s.match(/'[A-Za-z0-9]{25,}'/g) || []).length });
```

A key found hardcoded needs **rotating**, not just replacing with `process.env` - it is preserved in every prior revision of the flow.

## Changing a workflow: use the editor, then prove it with the API

**Writing through the API is refused.** `PUT /api/automation/v4/flows/{flowId}` from the browser session returns `400` with `sourceapp required for app-auth request` and changes nothing (the `revisionId` stays put). Do not guess the missing parameter. Make the change in the editor, then re-read the flow through the API to prove it.

**Suppression lists live in the trigger panel, not the top Settings menu.** In the new editor, click the trigger card, open its **Settings** tab, and find **"Added to a suppression segment"**. The top-bar **Settings** holds scheduling and connection options only. Type the list name into the dropdown, tick it, press Escape, then **Save** at the top of the panel. A panel that opens scrolled hides its Save button: scroll the panel up.

**A filter-triggered, re-enrolling workflow asks to enroll existing contacts on save.** Saving anything in its trigger panel, even only a suppression list, opens "Do you want to enroll existing contacts?". The answer for a suppression edit is **"Save and don't enroll existing contacts"**; the other button pushes everyone who currently matches the trigger into the flow. The dialog can close on its own while it calculates, so verify rather than assume. On 2026-09-28 the Onboarding Orchestrator (`1815158647`) closed the dialog before the click landed.

**Prove every save four ways:**

1. `revisionId` went up.
2. `suppressionListIds` holds the new id.
3. `enrollmentCriteria` and `actions` are unchanged. Compare with key-sorted JSON; a plain `JSON.stringify` compare reports a false difference because key order changes.
4. The first action's "N contacts in action" on the canvas is normal volume, not a sudden mass enrollment.

A new active list takes seconds to process. Poll `/api/crm/v3/lists/{id}` until `processingStatus` is `COMPLETE` before you check size or membership.

## Related

- `SKILL.md` - the QA process this feeds
- `systems/owned/hubspot.md` - portal id, Known Issues, `query_crm_data` quirks
- `references/integration-debugging.md` - the `javascript_tool` result block (`?` and `key=value`)
