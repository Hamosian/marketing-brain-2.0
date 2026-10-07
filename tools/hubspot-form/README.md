# HubSpot lead-capture form

A self-contained, Riverside-branded form that captures **First name, Last name, Email, Company name** and submits directly into HubSpot via the public [Forms Submission API v3](https://developers.hubspot.com/docs/reference/api/marketing/forms).

- **File:** `index.html` - one file, no build step, no dependencies (Instrument Sans loads from Google Fonts).
- **Portal ID:** `9154210` (Riverside) - already wired in.
- **Endpoint:** `POST https://api.hsforms.com/submissions/v3/integration/submit/9154210/{FORM_GUID}`

## Field mapping

The form field names are HubSpot's default **Contact** property internal names, so submissions land on the right CRM fields with no extra mapping:

| Form field    | HubSpot property (internal name) | Required |
|---------------|----------------------------------|----------|
| First name    | `firstname`                      | Yes      |
| Last name     | `lastname`                       | Yes      |
| Work email    | `email`                          | Yes      |
| Company name  | `company`                        | Yes      |

`company` is the standard Contact property "Company name". HubSpot's company-association automation propagates it to the associated Company record.

## One manual step (connector-blocked)

The HubSpot MCP connector available to the agent **cannot create or edit HubSpot form objects** (`FORM` write is `NOT_AVAILABLE`), so the form GUID has to be minted once in the HubSpot UI:

1. HubSpot → **Marketing → Forms → Create form** (an embedded regular form).
2. Add exactly these fields: **First name, Last name, Email, Company name**, each marked **Required**. (These are default contact properties - no custom properties needed.)
3. Publish, then copy the form's **GUID** (it's in the form's share/embed code, and in the editor URL).
4. In `index.html`, replace `REPLACE_WITH_HUBSPOT_FORM_GUID` with that GUID.

The submit endpoint validates against that form's field definitions, which is why the matching HubSpot form must exist. Until the GUID is set, the form validates input client-side and shows a "not connected yet" message instead of posting.

## Deploy

- **Embed:** drop the contents of `index.html` (the `.rs-form-wrap` markup + `<style>` + `<script>`) into any page, or iframe the file directly.
- **Standalone:** host `index.html` as-is.

The form styling uses Riverside tokens (primary `#9671ff` / `#7848ff`, Instrument Sans) pulled from `references/design-system`.

## Notes

- No API key or private token is used - the v3 integration submit endpoint is the public, CORS-enabled path intended for client-side forms.
- Submissions include `pageUri` and `pageName` context so HubSpot records where the form was filled.
- On success the form is replaced by a thank-you state; on a HubSpot validation error the returned message is shown inline.
