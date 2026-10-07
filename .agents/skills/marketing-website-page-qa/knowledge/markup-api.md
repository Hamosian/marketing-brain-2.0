# Markup.io API - verified contract for page QA

Everything here was verified live against the `riversidefm` workspace on 2026-08-23.
Where the published docs and observed behaviour disagree, observed behaviour wins and the
difference is called out.

**Client:** `scripts/markup_client.py` (stdlib only). It already encodes every gotcha below -
prefer it over hand-rolled requests.

## Connection

| | |
|---|---|
| Base URL | `https://api.markup.io` (**not** `app.markup.io` - that host rejects the Bearer header) |
| Auth | `Authorization: Bearer $MARKUP_API_KEY` (workspace key, `sk_…`) |
| Required header | `Markup-API-Version: 2023-02-22` - the **only** accepted value; other dates return 400 |
| User-Agent | Must be set. urllib's default is blocked by Cloudflare with `error code: 1010`, which looks like an auth failure but is a WAF block |
| Workspace ID | `f0a09d81-1a9e-45f7-afc6-bb53537b7c97` - the `lXGdASJ8` in the workspace URL is a **slug** and is rejected with `403 workspaceId ID in query and API key don't match`. The key is workspace-scoped, so the ID can usually be omitted |
| Secret handling | `MARKUP_API_KEY` in the environment. **Never** in the repo, a QA doc, or a ticket |
| Where the key lives | macOS Keychain, exported from `~/.zshenv`: `export MARKUP_API_KEY="$(security find-generic-password -s MARKUP_API_KEY -w 2>/dev/null)"`. Not a session scratchpad: `/private/tmp` is wiped on restart, which is how the key went missing on 2026-09-24. To add it, copy the key and run `security add-generic-password -U -a "$USER" -s MARKUP_API_KEY -w "$(pbpaste \| tr -d '\n')"`, then `pbcopy < /dev/null`. The Claude desktop terminal pane cannot take the hidden prompt of a bare `-w` |

## Quota

`GET /api/v2/markups/usage` → `{scope, used, limit, remaining, periodStart, periodEnd, enforcementEnabled}`.
The workspace allowance is **50 markups/month**. Check it before a bulk run, and **reuse the
markup already linked on the ticket** on a re-QA rather than creating a second.

## Endpoints used by page QA

| Purpose | Call |
|---|---|
| Create a markup from a page URL | `POST /api/v2/markups/url` - `{url, name, workspaceId?}` → response carries **`markupUrl`** (`https://app.markup.io/markup/<id>`), the link the QA process writes to the MarkUp column (see Limits for who can open it) |
| List view modes | `GET /api/v2/markups/:id/view-modes` → `desktop` / `tablet` (576×768) / `mobile` (375×667) |
| Create a pin | `POST /api/v2/threads` - see the payload below |
| Read all pins + comments | `GET /api/v2/threads?markupId=<id>` |
| Reply on a pin | `POST /api/v2/threads/:threadId/messages` - `{content: "..."}` (a plain string **is** fine here) |
| Resolve / reopen | `POST /api/v2/threads/:id/resolve` · `POST /api/v2/threads/:id/unresolve` |

## Creating a pin - the two gotchas

Both of these fail with an opaque **`500 INTERNAL_SERVER_ERROR`**, never a 400. That is why
they are easy to mistake for a broken endpoint; a bare-minimum body also 500s rather than
reporting the missing field.

1. **`message` must be a Quill Delta object**, not a string:
   `{"ops": [{"insert": "text\n"}]}`. A plain string → 500.
2. **`elementParents` must be present as a key**, even as `[]`. Omitting it → 500.
   (`[]` is accepted, so the ancestor chain is optional; the *key* is not.)

`osVersionName` in `browserContext` is documented but **not** required - omitting it returns 200.

Working payload:

```json
{
  "isImageThread": false,
  "projectId": "<markupId>",
  "url": "<page url as markupped>",
  "canonicalUrl": "<production equivalent>",
  "viewModeId": "<from view-modes>",
  "offsetXPercentage": 0.5, "offsetYPercentage": 0.4,
  "viewportXPercentage": 0.5, "viewportYPercentage": 0.4,
  "elements": [{"elementPath": ".hero > :nth-child(2)",
                "offsetXPercentage": 0.5, "offsetYPercentage": 0.4}],
  "elementParents": [],
  "message": {"ops": [{"insert": "P2 - ...\n"}]},
  "browserContext": {"browserName": "Chrome", "browserVersion": "151.0.0.0",
                     "os": "macOS", "osVersion": "10.15.7", "platform": "desktop",
                     "screenWidth": 1920, "screenHeight": 1080,
                     "viewportWidth": 1280, "viewportHeight": 900}
}
```

### Pin geometry

`elementPath` is a **CSS selector chain** (e.g. `.home-hero__checkbox-wrapper > :nth-child(5) > :nth-child(2)`),
and all `*Percentage` values are **0-1 fractions, not 0-100**. Both are computable from the
Step 2 browser pass: you already have the element, so take its selector and the click point as
a fraction of its bounding box. On read, `elements` comes back as an array of the element plus
its ancestors, each with its own offsets - a re-anchoring fallback chain the UI builds. Sending
just the target element is accepted.

## Limits worth knowing before you design around them

- **Who can open `markupUrl`.** The API identity (`marketing-os-v1`) owns every markup it
  creates. `app.markup.io/markup/<id>` opens for an anonymous visitor (verified in incognito), and
  a browser holding a guest session from any invite link also gets in, but a person signed in to
  Markup who is not a member gets a "this markup is private" page (seen in a signed-in Chrome,
  2026-09-27). The fix the team chose is membership: the people who hit it were invited as Markup
  users, and the process keeps writing `markupUrl` to the MarkUp column. A hand-made
  `app.markup.io/invite/accept/<token>` link (8-character token, one per markup) also works for
  everyone, because accepting it adds the visitor.
- **No API call returns the invite link.** It is not in `GET /api/v2/markups/:id` (fields:
  `activeThreads, createdAt, hasRetainedOriginal, id, markupUrl, modifiedAt, name, readOnly,
  retainOriginal, scopes, status, thumbnailUrl, type, url`; `?include=invites` changes nothing),
  and every sharing path tried returns 404: `/invites`, `/invite`, `/invite-link(s)`,
  `/public-invite-link(s)`, `/share`, `/share-links`, `/links`, `/users`, `/members`,
  `/collaborators`, `/invitations` under `/api/v2/markups/:id`, plus `/api/v2/invites` and
  `/api/v2/invite-links` with `?markupId=`. This is despite the markup object listing `invite`,
  `manage-invites` and `toggle-public-invite-links` in its `scopes`. There is no public OpenAPI
  spec to check against.
- **Reading it from the UI is not viable either.** Opened in Claude in Chrome with a signed-in
  session, the markup app renders a blank page with no accessible Share control, and its data
  calls do not show up in the network log. In a browser without a Markup account, Share asks the
  visitor to "Continue as Guest" or sign up first, which an agent should not do. So an invite
  link, when one is wanted, comes from a person.
- **An invite link on the ticket cannot be resolved back to a markup.** `app.markup.io/invite/accept/...`
  carries no markup id, so there is no way to look up which markup a hand-made invite points at.
  To reuse it, match on the page URL you reviewed with `markup_client.py find-markup --url <staging-url>`
  rather than creating a second markup for the same page.
- **The markup list only reaches the ~99 most recently active markups.** `GET /api/v2/markups`
  returns `{data, hasMore, nextCursor}` sorted by last activity, but nothing advances the cursor:
  `cursor`, `nextCursor`, `after`, `startingAfter`, `starting_after`, `startCursor`, `pageToken`,
  `from`, `next`, `afterId`, `startingAfterId`, `offset`, `page`, `skip` and `Cursor` /
  `X-Cursor` headers all return the first page again (tested 2026-09-27), and `search`, `q`,
  `name`, `url` and `query` do not filter. A page under active QA is almost always in that
  window; `find-markup` says so when it comes back empty with `hasMore` set, and the skill then
  asks a person before creating a duplicate. And if the
  column already holds a value a human put there, leave it: write only into an empty column, and
  confirm it is empty by reading it immediately before the write.
- **Gated `/dev/` pages work, with a step.** Markup's proxy loads the page but is not carrying
  the Webflow gate cookie, so the markup first renders the password screen. Each reviewer
  enters the shared `/dev/` password once inside the markup and then sees the page. The
  thumbnail will show the password screen - cosmetic only.
- **Attribution.** Threads created with the API key are authored by the key's identity
  (type `api`, shown as e.g. `marketing-os-v1`), not a person. Lead each pin with its severity
  so the comment stands on its own.
- **`@ceros-dev/markup-sdk-core` (1.0.0-rc.1) cannot create threads.** Its `threads.create` is a
  pass-through - `this.http.post(THREADS.CREATE, input)` - so it POSTs its own friendly
  `{projectId, message, position}` façade verbatim instead of mapping it to the API body, and
  always 500s. Its typed input is **not** evidence of the required shape. Use the REST API.
- **Exchange tokens** (`POST /api/v2/auth/exchange`, `X-Markup-Public-Key` header, RS256 JWT with
  `iss: https://api.markup.io`, `aud: https://api.markup.io/v2/auth/exchange`, `sub`, `iat`,
  `exp`, `jti`) work and attribute to a real user, but are **short-lived (~5 min)** and need an
  SDK installation that can only be created in the workspace UI. The workspace API key is
  simpler and sufficient for QA. Expired-token 401s are easy to misread as payload failures.
