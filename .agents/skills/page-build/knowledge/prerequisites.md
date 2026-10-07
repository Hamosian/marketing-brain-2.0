# Preflight: what a page build needs before it starts

Read at **G0**, before the ticket. Every item here blocked a real run; none is
hypothetical. The point is to fail in the first minute with a list Nir can act
on, instead of forty minutes in with half a page built.

Run the checks in order and stop at the first failure that blocks the work you
were asked to do. Not every run needs every item - the **Needed for** column says
when to care.

## The checks

| # | Capability | Check | Needed for |
|---|---|---|---|
| 1 | Webflow access | `webflow_guide_tool` once per session, then `data_sites_tool > get_site` on the site id | Always |
| 2 | Webflow write | `data_pages_tool > get_page_metadata` on the clone source returns a page | G2 onward |
| 3 | monday ticket | Read the ticket on Website Development (`18397093471`) | Always |
| 4 | Figma design | `get_metadata` on the file key in the ticket's Figma column | Whenever a Figma is the input |
| 5 | Staging visibility | Fetch the staging URL in the browser | G4 |
| 6 | Markup | `MARKUP_API_KEY` present in the environment | G4, only if pinning visual findings |
| 7 | A human | Someone available to publish | G5, always |

Report the result as a short table before doing anything else. If everything
passes, say so in one line and move to G1 - do not narrate the checks.

## Fixing each one

Written for the person, not the agent. One concrete action each, in the style
`CLAUDE.md` requires: plain language, no tool names, no error strings.

**1-2. Webflow.** If the check fails, the Webflow connector is not authorised for
this session. Open Claude's connector settings and connect Webflow, then say
"ready". Unlocks: everything.

**3. The ticket.** If monday cannot be read, the monday connector is not
authorised. Open Claude's connector settings and connect monday.com, then say
"ready". Unlocks: reading the brief, the Figma link and the staging URL, and
posting the build summary back. Without it you can still build from a Figma link
pasted into chat - offer that rather than stopping.

**4. Figma.** Two separate things go wrong here, and they need different fixes:

- *Nothing responds at all.* The Figma Dev Mode connection runs through the
  **Figma desktop app**, not the browser. Open the Figma desktop app, open the
  file, and leave it open. Unlocks: reading the design.
- *It responds but refuses the file.* That is access, not tooling - the file is
  in a workspace the account cannot see. Ask for view access to that specific
  file. Unlocks: reading that design.

Worth knowing before you promise anything: a **Full seat** is enough to read
designs and export assets. Some Figma features are gated on the workspace's
**plan tier** rather than the seat, so "I have a Full seat" does not settle
every refusal - check which of the two you are actually hitting before asking
anyone to change a licence.

**5. Staging.** Three known gates, in the order you will meet them:

- `stg.riverside.com` may return **403** - that host sits behind the VPN, which
  the browser does not have. Use the Webflow staging host instead: swap
  `stg.riverside.com` for `riversidefm-design-com-domain-staging.webflow.io`,
  keep the path. No one needs to do anything.
- **Do not build new pages under `/dev/`.** Staging pages are no longer
  password-gated (team decision, 2026-09-27): the gate blocked agentic QA.
  The staging domain's `robots.txt` disallows all crawling, so an ungated
  page stays out of search.
- Older pages may still sit behind a Webflow password page (`/dev/`, or
  anywhere else: the `<title>` reads "Protected page" and `fetch()` returns
  401). Never store, guess or type the password, even though it is shared
  (the `/dev/` one is in 1Password; see `systems/owned/marketing-website.md`).
  Ask the person you are working with to unlock the page once in your
  browser; the unlock holds for that host for the session. The full
  procedure is in `marketing-website-page-qa` (Accessing staging).
- `/section-library/**` is gated the same way, which matters when checking who
  else uses a shared class - say the scan is incomplete rather than claiming
  none.

**6. Markup.** If the key is absent, QA still runs; only the visual pins are
unavailable. Put the findings in the QA doc instead and say the pins were
skipped. Ask for the key only if someone wants pins.

**7. Publishing.** There is nothing to unblock. Publishing is human-only by a
standing rule in `CLAUDE.md`, and no approval in chat changes it. Confirm before
you start that someone will be available to publish, so a finished build does
not sit unannounced.

## Two limits that are not access problems

Do not raise these as blockers or ask anyone to fix them - they are properties of
the platform, and the workarounds are in `systems/owned/marketing-website.md`:

- **Grid and Container elements, and `HtmlEmbed` code, cannot be created through
  the Data API.** Plan for the workaround rather than asking for permissions.
- **The asset endpoint rate-limits** under a burst of image binds, which surfaces
  as timeouts and then a `429` that also breaks element reads. Pace the writes;
  they land even when the call reports a timeout.
