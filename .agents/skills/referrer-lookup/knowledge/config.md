# Referrer Lookup config

IDs, columns and search rules for `/referrer-lookup`. Verified 2026-09-27 against the live boards.

## Sources

| Source | ID | Notes |
|--------|----|-------|
| Partnerships group DM (Slack) | `C0C0UNPKMHN` | Nir, Savion, Dalit, Gili, Ofra. Where `inbound-demo-reply` posts named referrers |
| monday workspace "Partnership CRM" | `16715366` | Scope for the workspace-wide item search |
| Creators board | `18423812254` | Contacts. Groups: Active Contacts, Inactive Contacts |
| Partnership Management board | `18423812251` | Deals / applications, including monday-form applicants |
| Agencies board | `18423812252` | Linked from Creators via the Agency column |
| HubSpot portal | `9154210` | Contact record URL: `app.hubspot.com/contacts/9154210/record/0-1/<id>` |

## HubSpot contact properties to fetch

`firstname`, `lastname`, `company`, `jobtitle`, `email`, `hs_analytics_source`, `hs_analytics_source_data_1`, `hs_analytics_source_data_2`, `hs_latest_source`, `hs_latest_source_data_1`, `lifecyclestage`, `hubspot_owner_id`, `createdate`, `first_conversion_event_name`.

`hs_analytics_source = REFERRALS` plus a domain in `hs_analytics_source_data_1` is the referring site. `mn.co` subdomains are Mighty Networks communities.

## Creators board columns that matter

| Column | Key |
|--------|-----|
| Channel link | `link_mm5nrnj0` |
| Email | `contact_email` |
| Type | `dropdown_mm5sk2m7` |
| Status (Active / Don't reach out) | `color_mm6hcphe` |
| Comments | `long_text4` |
| HubSpot URL | `link_mm6tzrcf` |

Partnership Management: status is `lead_status` (e.g. "Not interested", "Applied by form"); main link `link_mm5sk1gp`; form answers in `long_text_mm71j4zz`.

## Search set (run all of them)

1. Creators board `searchTerm` with the name as written ("7 Figure Podcast").
2. The same with digits spelled out or vice versa ("Seven Figure").
3. The shortest distinctive form ("7 Figure").
4. Creators board filter: `link_mm5nrnj0` `contains_text` the referral domain (e.g. `mn.co`, or the full host).
5. Name filter on both boards: `name` `contains_text` the distinctive surname or word (e.g. `Bledsoe`, `Figure`) on Creators and on Partnership Management. This is the only reliable negative: fuzzy `searchTerm` returns loose look-alikes ("Tyler Stalman" for "Ty Bledsoe") and can hide a true zero.
6. Workspace item search (`searchType: ITEMS`, workspace `16715366`) with the name.
7. Open every candidate from 1-6 that is plausibly the same entity and confirm on its link, email, or form text.

Search is fuzzy and returns loose matches (e.g. "Seven Media", "7 figure brand" in someone's form text). A candidate counts only if its link, email or name identifies the same show, community or person.
