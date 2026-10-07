<!-- last-reviewed: 2026-10-06 -->
# Customer.io

> R&D's email platform for Riverside's product and system emails (account, auth, invites, file notifications). Marketing builds inside it but does not own it. When someone forwards a "what is this email?" from a customer, it is usually from here, not HubSpot.

## Overview

Workspace `120243` sends the product's transactional email, triggered by the backend through the transactional API. Workspace `124365` holds a few product test workflows. Marketing has build access and owns one automation there (review collection, `systems/owned/review-collection.md`). Lifecycle and marketing email lives in HubSpot (`systems/owned/hubspot.md`).

## How Claude Works With This

| Action | How |
|--------|-----|
| Investigate | Customer.io MCP (`cio_*` tools), read-only. Call `cio_prime` first, then `cio_schema` before any path |
| Identify a forwarded email | See "Tracing a forwarded email" below |
| Make changes | Customer.io UI or API. Transactional messages are R&D's: agree the change with R&D first, then confirm before any write |
| Deploy | No deploy step. A saved change to a transactional template is live on the next send |

## Tracing a forwarded email

A customer reply forwarded by CS or Nir usually still carries the original body. To find which message sent it:

1. **Confirm it is Customer.io.** Every tracked link goes through `e.customeriomail.com`, and the footer has `e.customeriomail.com/unsubscribe/<delivery id>`.
2. **Take the delivery id** from the unsubscribe URL (for example `RLOrBwUAAaENelZ-ayQ61zw4NQWMpA==`). The tracked-link URLs carry the same id as `email_id` in their base64 JSON.
3. **Read the delivery:** `GET /v1/environments/120243/deliveries/{id}`. It returns the recipient, the send time, opens and clicks, and either `transactional_message_id` or `campaign_id`. A 404 in `120243` means try `124365`.
4. **Read the message:** `GET /v1/environments/120243/transactional_messages/{id}`. The response includes every language template's full HTML and runs past 200K characters, so filter with `jq` and drop `preview` and the template bodies.
5. **Read the sender:** the template's `from_identity_id` resolves in `GET /v1/environments/120243/identities`. `reply_to_identity_id: null` means replies go to the from address.
6. **Check volume:** `GET .../transactional_messages/{id}/metrics?period=days&steps=N` returns daily `sent`, `delivered`, `human_opened`, `human_clicked` arrays. The last element is today, partial.

## Known messages

| Message | Trigger | What it is | Sender and replies |
|---|---|---|---|
| Transactional `42` "Support User Authentication Email" (subject "Authenticate your account"; es, pt, fr, de copies) | `SUPPORT_USER_AUTHENTICATION` | Asks the user to confirm their account for a support ticket. The link is `riverside.com/api/v4/auth/support/authorize-user?userId=...&ticketId=...`. The description in Customer.io says it covers an email-change request | Identity `13`, "Riverside Team <csm@riverside.fm>". No reply-to on any language template, so every reply lands in the CS inbox |

Message `42` sends about 40 to 107 a day; 3,011 in the 45 days to 2026-10-06, and about 70% of delivered recipients click the link. On 2026-10-06 the Head of Customer Success flagged confused replies from non-business users reaching CS. Volume showed no spike, so the cause was the missing reply-to, not a burst of sends. Pavel (R&D) last edited the message, in February 2025.

## What the Team Owns

- Review collection automation `16` (SEO team owns the behavior; Marketing Ops builds it)
- Answering "is this HubSpot or Customer.io?" for Nir and CS, read-only

## What the Team Does NOT Own

- The platform, sender identities and domains (R&D)
- Every transactional message and the backend triggers that fire them (R&D)

## When It Breaks

- **Customers reply to a system email and confuse CS:** trace the message as above and check its reply-to. A fix is an R&D change; bring them the message id, the sender identity, and the daily volume.
- **A "spike" is reported:** read the daily metrics before agreeing it is one. Steady volume points at the reply path or the inbox, not the sending.

## Related Systems

- **Upstream:** the Riverside product backend (transactional triggers), Appcues (NPS events into automation `16`)
- **Downstream:** the CS inbox at `csm@riverside.fm` for replies to identity `13`
- **Sibling:** HubSpot, which sends lifecycle and marketing email

## Pointers

- Workspace: <https://fly.customer.io/workspaces/120243>
- Review collection automation: `systems/owned/review-collection.md`
- Escalation: R&D owns the platform; for message `42`, start with Pavel
