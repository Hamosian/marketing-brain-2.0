# Teams We Work With

Teams outside Riverside Growth that we regularly interact with.

| Team | Slack channels | On-call alias | Lead | Context repo | Notes |
|------|---------------|--------------|------|-------------|-------|
| Data Team | `#data-marketing` (`C08283QUCNM`) | n/a | Eyal Solnik (Head of Data) | n/a - see `systems/reference/data-team.md` for their monday boards (request intake, schema, workflow) | Sits under Business Operations, not Marketing/Growth. Marketing is their largest requester outside the Data org itself. **Provisions Rivermind access and the Snowflake access it runs on** (Jonathan Galili, 2026-09-23) |
| IT | `#it-support` (`C07CMP7EFM1`) | IT Service Bot (`U09F7RQ61NW`) - auto-opens a ticket on every top-level post | Eden Shoshe (`U06HTTU4ALX`, Director of IT) resolves most tickets | n/a | **Externally shared (Slack Connect) channel** - Slack integrations cannot post to it (`mcp_externally_shared_channel_restricted`). An agent must create a *draft* for the human to send; it cannot file the request itself. Owns Claude workspace administration - see the connector-request process below |
| R&D / DevOps | `#devops-help` (`C086J2JL6FM`) for requests; `#marketing-dev` (`C0AA8HABQKG`) for website-infrastructure discussion | n/a - every request goes through the channel's Slack workflow form | David Vaknin (Head of DevOps). Requests land in the Linear **DevOps** team (`b625dafe-bcb7-41ae-9450-06cfe3f6d580`) in Triage | n/a | **Never create the Linear issue directly.** A Slack workflow form creates it. Fields and gotchas below. Other R&D contacts for website work: Eyal Eizenberg (Director of Engineering), Yoav Avidan (Platform Group Lead), and Alex Eisen (Director of Engineering Operations), who has routed marketing asks to owners in `#marketing-dev` (observed) |
| Platform Enablement | `#platform-enablement-requests` (`C0B1FN9HS9J`) for requests; `#platform-enablement-fyi` (`C0B455UBVH6`); `#platform-enablement-code-review` (`C0B55JTM49W`) | n/a | Not recorded. Requests land in the Linear **Platform Enablement** team (`c60ff78f-ce48-4ed6-ae85-2bc43b25593b`) in Triage | n/a - see `systems/reference/backoffice-coupons-api.md` | Owns the Backoffice Marketing Coupons API, its gateway and our API key. **File by posting in `#platform-enablement-requests`**, which creates the Linear issue; don't open one by hand, the same rule as DevOps above. Our open ask is ENB-1142. **There is no `#platform-enablement` channel** despite older pointers in this repo (verified 2026-10-06) |
| Product | `#product` (`C01V860MANM`) | n/a | Max Benezra (Senior Product Manager); Asaf Fox (Head of Localization) | n/a | HiBob files Product under R&D. Asaf also owns Crowdin in the localization SOP (`systems/owned/localization-workflow.md`) |
| Customer Experience (Support) | `#support-marketing` (`C05TRR8BWBX`) for asks to Support; `#crisis-escalation` (`C01CK54HWJU`) when users cannot use the product | n/a | Gil Perlman (Head of Customer Experience); Daniel Schlaen (CX Business Strategy and Operations Partner) | n/a | HiBob department: COS. The route for a new hire to shadow a support shift |
| RevOps | `#marketing-revops` (`C07V6N3N5U1`) | n/a | Matan Rafic (Head of Revenue Operations) | n/a | Sits in the Sales department (HiBob) |

Titles and departments above were checked against HiBob on 2026-09-23 (see the HiBob note in `references/team.md`).

### Org structure

- **Shira Sadoth Zafrir** - VP Business Operations
  - **Eyal Solnik** - Head of Data
    - Data Analysts: Yaniv Barel, Shir Sarusi
    - Data Engineers: Ariella Dako's team (Ariella Dako, Director of Analytics Engineering)

HiBob (2026-09-23) lists the data people's department as R&D; the reporting line above is from the source org chart. Do not re-parent the team on the strength of the HiBob department field alone.

**Knowledge gaps to fill:** SLA/prioritization criteria for data requests.

## Access provisioning: who grants what

From the Marketing Website onboarding checklist, confirmed by Jonathan Galili on 2026-09-23. Use it when onboarding anyone into Marketing Operations or the website role, and to route an "I can't get into X" question to the right owner.

| Access | Granted by |
|--------|-----------|
| Laptop, Google account and email, Slack, 1Password, Cloudflare WARP (VPN, needed for `stg.riverside.com`), Figma, Gong, Mixpanel, Claude and Claude Code, PagerDuty, Granola | IT (`#it-support`) |
| HiBob | HR |
| Groundcover (site monitoring) | DevOps |
| Rivermind, and the Snowflake access it runs on | Data team |
| monday.com boards | Hanan Amos |
| Webflow, Convert Experiences, GA4 / Google Tag Manager / Segment, HubSpot, Omni BI, the `riversidefm/marketing-brain` GitHub repo | Jonathan Galili |
| Google Search Console, Ahrefs | Erika Varangouli or Amir Bar-Tikva |
| Crowdin | Asaf Fox |

Adding someone to the GitHub repo triggers `/access-welcome`, which DMs them the repo activation guide.

## Requesting a Claude connector (MCP server) from IT

Riverside runs more than one Claude org. Marketing/GTM people sit in the **GTM workspace (Claude)**; connectors must be installed *and published to members* by an admin, so an individual cannot self-serve one for the team. IT owns this.

Process (established pattern, e.g. ticket #3650 - Mindtickle MCP):

1. Post a top-level message in `#it-support` naming the workspace, the connector URL, what it does, and why. The IT Service Bot opens a ticket automatically and replies with a ticket link.
2. Because `#it-support` is Slack Connect, an agent cannot post there. Draft the message (`slack_send_message_draft`) and hand it to the requester to send.

   **Get the draft right the first time.** There is no tool to edit or delete a Slack draft, only to create one. The tool docs claim a second draft in the same channel fails with `draft_already_exists`, but in practice the call returns success with a new id and you end up with two drafts stacked in the channel, the stale one included. If a draft needs revising, say so and let the requester delete the old one by hand; do not re-issue `slack_send_message_draft` and assume it overwrote.

3. Verify the endpoint before asking so the ticket carries real detail rather than just a URL. A streamable-HTTP MCP server returns `405` to a plain `GET`; `POST` an `initialize` call instead to get its real `serverInfo` (name, version) and instructions:

   ```bash
   curl -sS -X POST <server-url> \
     -H "Content-Type: application/json" \
     -H "Accept: application/json, text/event-stream" \
     -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"probe","version":"1.0"}}}'
   ```

   **A successful `initialize` does not mean the server needs no credentials.** Servers routinely accept an unauthenticated handshake and only enforce auth on the calls that actually touch data. Follow up with an unauthenticated `tools/list` (same headers, `"method":"tools/list","params":{}`) and, where it is safe to do so, one read-only `tools/call`. Report what each probe returned rather than generalising from the handshake:

   - `initialize` accepted without authentication
   - `tools/list` returned real tool definitions without authentication (or returned `401`/`403`, in which case the server *does* require credentials)

   IT asks about credentials first, so give them the observed result per probe, not a conclusion.
4. State whether the server is read-only and whether any Riverside data leaves the org. Public-dataset servers that stay unauthenticated across the probes above are the easy approvals; anything requesting OAuth against a Riverside system will get security review.

## Requesting DevOps / R&D work

DevOps work is requested through a **Slack workflow form in `#devops-help`** (`C086J2JL6FM`),
not by opening a Linear issue. The form creates the issue on the Linear **DevOps** team in
Triage and attaches a link back to the originating Slack message.

Workflow shortcut: `https://slack.com/shortcuts/Ft09ECB22MBK/0468027e11b248a908c8718cf324858a`

The form has five fields, in this order:

| Field | What it takes |
|-------|---------------|
| Description | One line. The ask, stated plainly |
| More information | Detail, context and links. Routinely left empty on trivial asks |
| Severity | `Low` / `Medium` / `High`. Marketing infra requests are conventionally `Low` - nothing is broken, we are recovering something |
| Summary | Short title-like line. Becomes the readable headline on the Linear issue |
| Who's effected by the problem? | `Only Me` / `Not Only Me` |

**Write every field as plain text.** Markdown tables, headings and `[label](url)` links do not
render through the form; they arrive as literal syntax. Use labelled lines and bare URLs.

**Long input can be truncated on submission.** `DEV-4462` (2026-09-15) lost its final block -
the spec link, the marketing ticket link, and the "what we need back" ask - somewhere between
paste and submit. Put the links and the actual ask **before** any long reference material, and
read the created issue back to confirm what landed.

**Define vendor jargon; do not explain Riverside's own systems back to them.** A request naming a
vendor concept (Google's "measurement path", say) has to say what it is and what happens on it. A
request walking DevOps through our own CDN topology, or telling them which cache policy to set,
is noise - they own that. Established marketing precedent in this channel: `410 Gone` page lists,
sitemap uploads, new page-path whitelisting, and `DEV-4462`.

**Knowledge gaps to fill:** SLA/prioritization criteria, and who triages the DevOps queue.
