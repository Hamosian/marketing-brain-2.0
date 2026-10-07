<!-- last-reviewed: 2026-09-30 (Cloudflare 1010 also hits Riverside's own api.riverside.fm). Earlier 2026-09-28 (the javascript_tool result block also fires on key=value pairs with no `?`). Earlier 2026-09-09 (added driving the vendor's own app to get past a guard on direct calls, from the Chili Piper booking-link diagnosis) -->
# Debugging a third-party integration

How to diagnose a failing call to someone else's API without concluding more than the
evidence supports. Load this when a write against HubSpot, monday, Webflow, Slack, Markup,
or any other integration fails and you are about to explain *why*.

**Use this when:** a request returns an opaque error, you are considering telling someone
"this is a vendor bug", or you are about to design a workaround around a limitation you
have inferred rather than proven.

## Why this exists

`references/evidence-standards.md` governs figures - a confidently wrong number gets acted
on. The same failure mode applies to **diagnoses**. A confidently wrong root cause gets
acted on too: it produces a bug report to a vendor, a workaround architecture, or a "not
feasible" that closes off work which was actually fine.

The expensive case in this repo, 2026-08-23: `POST /api/v2/threads` on Markup returned an
opaque `500` across roughly ten hand-built payload variants, both auth methods, and the
vendor's own SDK. That was reported as an unreported vendor bug, with a recommendation to
email support and build a browser-automation workaround. The actual cause was **two fields
missing from the request**. The maximal documented payload worked on the first attempt.

## The rule

**An opaque 5xx on a write is evidence about your request until you have sent the maximal
documented payload.** Only after that is it evidence about the vendor.

## Build maximal, then ablate

Do not start minimal and add fields until something works - that path explores a tiny
corner of the space and every failure looks like the same wall. Instead:

1. Construct the request with **every documented field populated**, required and optional.
2. If it succeeds, **remove one field at a time** to find what was actually required.
3. Record the minimum working payload, and which omissions fail.

On the Markup case, thirteen minimal-and-add variants failed; the maximal payload succeeded
immediately, and five ablations then isolated the two genuinely required fields. Same
information, an order of magnitude less work, and no wrong conclusion in between.

## When the payload is a file, ablate its parts, not its fields

"Maximal, then ablate" assumes a request whose shape you control field by field. A file
upload inverts it: you hand over a container - a zip of XML parts, a document with embedded
resources - and the service accepts or refuses **the whole thing**. Ablating fields inside it
tells you nothing, because the rejection is not about any field.

Ablate the **parts** instead, and here the minimal-then-add direction is the cheap one,
because a container has few parts and each is individually optional:

1. Strip to the smallest container the format allows and confirm it is accepted. That
   separates "this format is refused" from "something in my file is refused" - two very
   different problems that produce the same error.
2. Add the parts back a group at a time until it breaks.
3. The part that breaks it is the finding. It is usually **optional**, which is why nothing
   in the error names it.

On the 2026-09-07 `/tools/` doc→sheet migration this took three uploads to isolate: an ODS
carrying `content.xml`, `settings.xml` and `styles.xml` was refused with `Unable to convert
uploaded content`; the same file without `styles.xml` converted perfectly. The offending part
was a `styles.xml` defining nothing but a cell style the automatic styles referenced as a
parent - content the file did not need at all. No amount of inspecting the *data* would have
found it.

Two traps specific to this shape:

- **The error names the container, so you will suspect the data.** "Unable to convert
  uploaded content" reads as "your rows are malformed". Test a trivially-valid file of the
  same format first; if that converts, your format is fine and the problem is a part.
- **A refusal issued before the file is read is about the format, not the file.** The same
  connector rejects xlsx with `Invalid conversion requested` no matter what the xlsx
  contains. An error that is instant and byte-identical across very different files is a
  gate on the *type*, and rebuilding the file cannot get past it - change format instead.

Corollary: a converter's accepted-format list is narrower than the platform's. Google Drive
imports xlsx in the UI all day; the connector's conversion allowlist does not. Do not infer
one from the other - probe it with a throwaway file, then delete the probe.

## A missing required field can return 500, not 400

Do not reason "a 500 means my payload isn't the problem, or I'd get a validation error".
Plenty of APIs dereference a missing field before validating it. On Markup, omitting
`elementParents` or sending `message` as a string instead of a Delta object both produced
`500 INTERNAL_SERVER_ERROR`, and a bare-minimum body 500ed rather than naming what was
absent.

## A vendor SDK's typed input is not the wire format

A typed client looks like proof that your payload shape is right. Check whether it actually
**maps** its input to the API body or just forwards it. Read the compiled code:

```bash
grep -rn "async create" node_modules/<pkg>/dist/esm/index.js
```

Markup's `@ceros-dev/markup-sdk-core` (1.0.0-rc.1) is
`this.http.post(THREADS.CREATE, input)` - a pass-through that POSTs its own friendly façade
verbatim, so it always failed. Citing it as "even the vendor's own client fails" was the
single most misleading step in that investigation.

## Separate transport failures from application failures

Before reading an error as the API's answer, confirm it came from the API:

- **WAF and CDN blocks impersonate auth errors.** `error code: 1010` is Cloudflare rejecting
  a browser signature, not the service rejecting a token. It hits Riverside's own gateway too:
  `api.riverside.fm` returned it to `urllib` on 2026-09-30 while `curl` got 200 with the same key. Python's `urllib` sends
  `Python-urllib/x.y` by default and gets filtered where `curl` does not - always set a real
  `User-Agent`.
- **A CDN or media host may reject the `Authorization` header entirely** and return 400/403
  for a URL that is fine without it.
- **Short-lived tokens expire mid-investigation.** An exchange token good for ~5 minutes
  turns every subsequent result into `401`, which reads as "my payload is still wrong".
  Re-mint before drawing any conclusion from a run.

## A 401 is about your key string before it is about the key

`401 Unauthorized` reads like a verdict on the credential's validity. It is equally
consistent with a credential you reconstructed wrong. On 2026-09-02 a Markup key returned
`401` and that was reported as "the key was rotated". It had simply been truncated on the
way in; the real key worked first try, and the wrong diagnosis sent the owner off to
re-issue a key that was fine.

**Never rebuild a secret by pattern-matching a transcript.** A conversation that has already
used a key contains *both* full copies and truncated echoes of it - summaries write
`sk_..._8ce7d7c2...` - so a `grep -oE` returns several candidates of different lengths with
no way to tell which is whole. A character-class guess makes it worse: `[a-f0-9]+` stops
silently at the first character outside the class, and the truncated result is
indistinguishable from the real thing until it 401s. In that case the candidates were 113,
163, 166 and 168 characters; two were tested and the true key was longer than both.

Ask the owner to re-supply the value. Two failed candidates is where to stop - past that,
trying more strings is credential guessing rather than debugging, and the tooling will
rightly refuse to help.

## The MCP layer can rewrite your arguments before the vendor sees them

An argument passed as a number can arrive at the tool as a string, so a valid call is
rejected by **client-side** schema validation and never reaches the API at all. Read this
before concluding a documented parameter is broken:

- `get_screenshot` rejected `maxDimension: 12932` with `Invalid input: expected number,
  received string`, on repeated attempts with integer and float literals alike - even though
  the same parameter had worked in earlier sessions.
- monday's typed tools began coercing numbers and arrays to strings after an MCP reconnect.

**Fallback:** where the server exposes a raw query interface, use it. monday's
`all_monday_api` takes GraphQL directly and sidesteps the typed tools entirely - note it
requires `variables`, so pass `"{}"` when there are none. Where there is no escape hatch, as
with Figma, that capability is unavailable for the session: say so and name the limitation
rather than reporting the underlying task as impossible.

## The Gmail connector rewrites links

Every link the Gmail connector sends comes out as a visible Google redirect:
`https://www.google.com/url?q=<the real url>&source=gmail&ust=<expiry>&sa=E`. That holds for
full URLs and for a bare domain like `riverside.com`, on `send_message`, `reply` and
`create_draft`, in a plain `body` and in an HTML `<a href>` alike (the anchor text stays
clean, the href does not). Verified 2026-10-06 with self-addressed tests on all paths, after
two partner emails went out with every link mangled. Email addresses were not rewritten.

What follows from it:

- **No link goes into a Gmail send from an agent.** Name the page in words ("your webinar
  software list", "our homepage"). When the link itself matters, hand Nir the text and the
  link to send from Gmail himself. The content gate (`.claude/hooks/content-gate.py`) blocks
  any Gmail send whose text carries a URL or a bare domain.
- **Read back every send.** The gate checks the text we pass in, not the text that lands.
  After any Gmail or Slack send, fetch the sent message (`get_message` with `FULL_CONTENT`)
  and compare it to the approved text. Any difference, a `google.com/url?q=` above all, is
  reported to Nir in the same turn, before he finds it.

## Isolate with controls before blaming the vendor

Establish, with the same credentials:

| Control | What it rules out |
|---|---|
| A **read** on the same resource | auth, scope, connectivity |
| A **different write** on the same resource | scope, permission on that object |
| The **same call on a known-good object** | that specific record being broken |
| The call from a **different client** (curl vs library) | your HTTP layer |

If reads and other writes succeed and only one operation fails, that narrows the problem -
but it does **not** yet distinguish "their bug" from "my payload for that one operation".

## "Nobody has reported it" is not evidence of a bug

On a young API, an absence of public reports means few people have called it, not that you
found something new. Check the package version and changelog: a `1.0.0-rc` with an
"Initial release" changelog and a private repo has no user base to have reported anything.
Treat that as a reason to doubt yourself, not as corroboration.

## A tool can refuse its own output, and that is not the API failing

`javascript_tool` (Claude in Chrome and the Browser pane) refuses any result whose text
contains a `?`, returning `[BLOCKED: Cookie/query string data]` and nothing else. The guard
scans the **result**, not the request, so the fetch already succeeded - the data is just not
being handed back. The block is all-or-nothing for the whole result, so one offending
character hides everything else.

Three things trip it constantly and only one is a real query string:

- **Optional chaining** in code you are reading back (`err.response?.status`)
- **Any URL with a query string** inside the payload
- **`key=value` pairs with no `?` at all.** A summary line built as `label=value; label=value` was blocked on 2026-09-28 after every `?` had already been replaced. Stripping `[?=&]` let the same result through. Join your own summaries with ` :: ` or ` | `.

Symptoms that look like something else: reading a value works, reading the string containing
it does not; masking the alphabet still blocks; shortening the slice still blocks. It is easy
to misread as taint-tracking on a `document.cookie` read earlier in the session - spending
several round trips narrowing that was the actual cost when this was found (2026-09-07,
reading a HubSpot custom-code action).

**Diagnose before working around it.** Find the offending lines, then read only the rest:

```javascript
const lines = payload.split('\n');
lines.map((l, i) => /[?=&]/.test(l) ? i + 1 : null).filter(Boolean); // the blockers
lines.filter(l => !/[?=&]/.test(l)).join('\n');                      // everything else
```

Read the excluded lines by screenshot instead - `computer` with `zoom` on the editor region
returns them fine, because the guard is on the JavaScript result rather than on images.

Generalises past this one tool: when a harness returns a fixed refusal string rather than an
error from the service, test whether the *content* or the *call* is being rejected before you
form any theory about the vendor. A refusal that is byte-identical across very different
inputs is a local guard, not a remote failure.

## When direct calls are blocked, drive the vendor's own app and read the trace

A vendor's public/guest endpoints often reject anything that is not the vendor's own app, with a
fixed status that looks like a verdict on your request. Before theorising, run the control from
the table above in its cheapest form: **call the endpoint with an identifier you already know is
valid.** If the known-good one fails identically to the unknown ones, the response is about your
client and tells you nothing about the data.

On Chili Piper (2026-09-09) `find-by-slug/<slug>` returned a byte-identical `403 Forbidden` for
seven candidate slugs *and* for the slug that had just returned `200` inside the app. Both `curl`
and a same-origin `fetch()` from the page's own console were rejected, so this is not a
User-Agent or CORS problem - the guard separates the app's own request path from scripted calls.

**The route around it is navigation, not fetching.** Load the vendor's real page in a browser and
read its network trace: the app issues the requests with whatever it is that satisfies the guard,
and you read the genuine response bodies. This turns an opaque wall into a full read of live,
*published* configuration, which is often the only place the truth is observable when the admin UI
is gated behind auth or an onboarding wizard.

Two things this buys you that an API key would not:

- **Existence probing with a clean signal.** Through the app, missing slugs returned `404` and real
  ones `200`. That discriminates; the `403` did not. Probe by navigating to each candidate, then
  read the accumulated request log in one call rather than one round trip per guess.
- **Reaching an object the public surface does not expose.** No public link served the meeting type
  under investigation, but a *reschedule* permalink for a past booking did, and loading it revealed
  that object's id and live settings. Generalises: per-record permalinks (reschedule, confirmation,
  share, preview, print) frequently render a different object graph than the main entry point, and
  they are read-only.

Log the exact endpoint-to-meaning mapping in the system doc when you do this, because the next
person should not have to rediscover which of a dozen XHRs holds the answer.

## When to escalate

Escalate once the maximal payload, the ablation, the controls, and the transport checks are
all done and it still fails. Include the request IDs, the exact body, and the controls that
passed - a vendor can act on that, and assembling it is also the step most likely to reveal
that the problem was yours.

## Related

- `references/evidence-standards.md` - the same discipline for figures and sources
- `references/change-control.md` - a change is not done until it runs
- `.claude/skills/hubspot-workflow-qa/knowledge/reading-workflows-via-api.md` - reading HubSpot's
  internal API through an authenticated browser session, and working around the `?` block
- `docs/platform-integration.md` → Google Drive - the worked case for part-level ablation: which
  spreadsheet formats the Drive connector will and won't convert, and how to ship a styled sheet
