---
name: marketing-website-page-qa
description: Guide Riverside Marketing team members through a structured web page QA review of marketing-website pages before launch. Use this skill whenever someone mentions reviewing, checking, QA-ing, or signing off on a web page -- including staging reviews, pre-launch checks, post-deploy verification, or any QA handoff from a developer. Also trigger when someone asks for a web-page QA checklist, wants to log page issues on the Website Development board, or needs to know how to escalate a web problem. Even if the user doesn't say "QA", if they're reviewing a marketing-website page before it goes live, use this skill.
---

# Marketing Website Page QA Skill

This skill guides you through Riverside's official web page QA process. Apply it whenever a developer marks a page ready for review, or whenever a Marketing team member needs to approve a web page before launch.

---

## QA Process (4 Steps)

**Step 1 -- Intake (auto-discover, then ask only what is missing)**

Most page QA runs against an existing **Website Development** ticket (`18397093471`) that the developer has moved to **Ready for QA** - start from the ticket, not a blank slate:

- **Given a ticket** (ID or URL): read its columns to pull the **Staging URL** (`link_mm06h542`), **Production URL** (`link_mm067vh2`), **Figma Design** (`link_mm05q7wr`), **Brief** - check **both** `link_mm05cxb3` (link) and `doc_mm77q17p` (monday Doc), since two columns share that title and either may hold it - Requester, and Assignee. Attach the QA doc to this ticket - do **not** create a separate QA ticket.
- **Check the Staging URL is this ticket's page before you QA it.** Compare the page's `<title>` and H1 with the ticket name. On 2026-09-27 the two industry tickets (Financial Services, Technology) had their Staging URLs swapped; each column pointed at the other page.
- **Read links from an update's `body`, not its text.** `get_updates` returns `text_body`, where monday shortens long links with `...`. Two Figma node IDs came back cut short that way (`607-6502...` for `607-65023`), and the short ID either 404s or resolves to a 1px node. Query `updates(ids:[...]) { body }` over GraphQL for the full `href`.
- **Given only a staging URL**: search the board for the matching ticket and use it. If none exists, confirm with the requester before creating one - substantive page work is filed via `/pm-story`, and the QA doc attaches to that ticket.
- **Understand what changed**: read the Brief and Figma so QA is scoped to the actual change, not a full-site audit. A brief in `doc_mm77q17p` is a monday Doc - read its content with `read_docs` on the `objectId` in the column value, rather than treating the column as a link. Never report "no brief" from one column alone.

Ask the user only for what the ticket cannot tell you (e.g. "which breakpoints matter most here?", "is this replacing a live page?"). Never ask for the staging URL, Figma, or brief when they are already on the ticket.

**Whether QA lives on the ticket or on a sub-item depends on the ticket's scope - check before you file anything.**

- **One page in the ticket** - QA goes on the **ticket itself**, using the parent columns below. Sub-items are unnecessary here; do not create them.
- **More than one page** - the ticket carries a `QA - <page>` sub-item per page on **Subitems of Website Development** (`18397201974`), each with its own staging URL, Figma frame and QA Doc. **Each page's QA output belongs on its own sub-item**, and the parent holds only what spans them.

Either way, read the staging URL and Figma link from **the item you are reviewing**. Reading the parent's links for a page that has its own sub-item is how you end up reviewing the wrong thing - it is what caused the 2026-08-09 Figma miss. The two boards use different column IDs:

| Field | Sub-item (`18397201974`) | Parent (`18397093471`) |
|---|---|---|
| Figma Design | `link_mm6234qq` | `link_mm05q7wr` |
| Staging URL | `link_mm62dge3` | `link_mm06h542` |
| Production URL | `link_mm626s4k` | `link_mm067vh2` |
| Brief (link) | - | `link_mm05cxb3` |
| Brief (doc) | - | `doc_mm77q17p` |
| MarkUp link | `link_mm624jtc` | - |
| QA Doc | `doc_mm62gjnk` | `doc_mm5fsegr` |
| Priority | `color_mm0e8ykb` | `color_mm051fmh` |

Sub-items also use a **different status vocabulary** from the parent - `Working on it`, `Done`, `Stuck`, `Ready on QA`, `Good`, `New`, `Audit post-live`. The QA lifecycle in Step 4 (`Ready for QA` -> `QA` -> `Ready for live` -> `Published`) is the **parent's**; do not try to apply those labels to a sub-item.

On a multi-page ticket, **new sub-items can appear after you have already QA'd others** - check the current sub-item list at the start of every round rather than assuming the set is fixed. On the 2026-08 University ticket a fourth page arrived days after the first three were reviewed, and it was the page an earlier round had reported as not built.

**Step 2 -- Review (automated pass, then human judgment)**

Run the automated browser pass (see **Browser-Based QA (automated)** below) across all four breakpoints:
- Desktop: 1280px+
- Tablet: 768px
- Mobile: 390px and 375px

Claude drives the browser for everything machine-checkable (responsiveness, console errors, broken links/404s, SEO metadata, rendered content); a human judges the subjective items (visual polish, brand feel, image licensing, copy quality). Always review the **staging** URL -- never the live site; confirm the production URL only at final sign-off.

**Step 3 -- Report (QA Doc + Markup)**

Findings split across two surfaces, and nothing appears in both:

- **Markup** takes the findings anchored to a *place on the page* - layout, spacing, a wrong or off-brand asset, a visible copy error, a mismatched component state. Stakeholders (designers, PMMs, requesters) review and reply there, which is why the ticket has a MarkUp column.
- **The QA Doc** takes everything non-positional - metadata and SEO, console and network errors, tracking, environment vs site-wide classification, findings you checked and ruled out, cross-page items, and anything needing a human decision.

The QA Doc links the markup; the ticket update points at both. See **Posting visual findings to Markup** below for the mechanics.

Log every issue in the **QA Doc column of the item you reviewed** - the ticket itself (`doc_mm5fsegr`) for single-page work, or the page's sub-item (`doc_mm62gjnk`) on a multi-page ticket - each with a screenshot, the device/breakpoint, and a severity label (P0/P1/P2/P3). Link the review conversation in the parent's **Slack Thread** column so the developer has full context.

**Step 4 -- Sign-off (drive the board status)**

**Do not write the ticket's Status column programmatically.** Like Priority below, status is a human transition for now - report the verdict and let Marketing Ops move the ticket. Recording a verdict is QA's job; moving the board is not.

The lifecycle below is the process **a human** follows, and is here so QA can describe where a ticket should go next - not so the agent can drive it. **Only Marketing Ops or the developer ever change ticket status** - never other marketing stakeholders. QA is run by (or on behalf of) Marketing Ops, which drives the QA-side transitions; the developer owns the **Published** step. On starting the review, Marketing Ops sets status to **QA** (`7`) if the developer left it at **Ready for QA** (`11`). On a **pass** (no open P0/P1), Marketing Ops sets **Ready for live** (`10`), posts approval in `#webflow-riverside` (`C08DJ6BN3NX`) - **an agent cannot post there, only draft; see the Slack Connect note below** - and notifies the developer to publish; after the developer publishes (**Published** `8`), Marketing Ops runs a quick **Audit post-live** (`13`) on production. On a **fail** (open P0/P1), status stays at **QA** (`7`) and nothing is approved.

**Do not write to the ticket's Priority column** (`color_mm051fmh` on the parent, `color_mm0e8ykb` on sub-items). This instruction used to say "set Priority to the highest severity found"; that was wrong and produced changes the team reverted on the 2026-08 Riverside University ticket. **Priority and severity are different axes.** Priority is how urgent the *work* is, weighed against everything else in flight - a planning decision owned by the requester and Marketing Ops. Severity is how bad the worst *defect* is, and the QA Doc already records it where people read it. Overwriting the first with the second destroys a field someone set deliberately. If QA genuinely thinks priority should change, say so in the ticket update and let a human make the call. (Label IDs, for reading or for a human-approved change: P0 `1`, P1 `110`, P2 `109`, P3 `7` - not the legacy Urgent/High/Mid labels.)

---

## Browser-Based QA (automated)

Claude performs the QA itself in the browser and only flags what genuinely needs a human. Staging is public, so use the **in-app Browser** (`mcp__Claude_Browser__*`).

### Accessing staging (full runbook in `systems/owned/marketing-website.md`)

**New staging pages are not password-gated** (team decision, Jonathan Galili, 2026-09-27). The `/dev/` gate blocked agentic QA, and the agent will not enter a password however widely it is shared. If a new page under review arrives behind a gate, flag it in the QA Doc as a process item for the developer to move it out of `/dev/`. The staging domain's `robots.txt` disallows all crawling, so an ungated page is not indexed. Pages built before the change may still sit under `/dev/`; the gate notes below cover those.

- **VPN / 403 on `stg.riverside.com`.** That subdomain sits behind Cloudflare Warp (VPN), which the browser does not have, so it may return **403**. Workaround: in the staging URL, replace the host `stg.riverside.com` with `riversidefm-design-com-domain-staging.webflow.io` (keep the path) and retry - the Webflow staging domain serves the same pages without the VPN.
- **Password-gated pages (any Webflow "Protected Page").** New pages should not be gated, but older ones are (`/dev/`, `/section-library/`), and a gate can turn up anywhere. **Recognise it:** the `<title>` is "Protected page", the body is just "Protected Page / Password", or `fetch()` returns **401**. **Handle it the same way every time:**
  1. Do **not** store, guess or type the password - the agent never enters one, however widely it is shared. The `/dev/` password lives in 1Password (see `systems/owned/marketing-website.md`); for any other gate, ask who owns it.
  2. **Start everything that does not need the browser, before anyone unlocks the page.** The Webflow MCP reads a gated page without the password (verified 2026-09-27 on the gated Technology page). Get the page ID from `data_pages_tool > list_pages`, then:
     - `data_pages_tool > get_page_metadata`: SEO title, meta description, Open Graph (title/description copied or not, image set or not), slug and folder, draft state.
     - `data_pages_tool > query_pages_schema_markup`: the page's JSON-LD.
     - `data_scripts_tool > get_page_freeform_code`: page-level head and footer code, for the tracking-duplication check.
     - `data_element_tool > query_elements` with `element_filter: {type: "Heading"}`: heading structure (one `h1`, levels in order).
     - `data_element_tool > query_elements` with `element_filter: {text: "<word>"}`: returns matching text with its `textContent`. Search for the source page's subject, "Lorem" and placeholder names. This found both Technology-page leftovers ("Stop shorting your own content", "Kellen Williams, Wealth Advisor") with the gate still up.
     Record these findings as they come. What this cannot cover: layout and breakpoints, console and network errors, whether tracking actually fires, and text bound from the CMS. Those wait for the unlock.
  3. Pause and ask the person running the QA to enter it once in the browser you are using (the Browser pane by default). The unlock holds for every page on that host for the rest of the session, so ask once per host, not once per page. If they have already unlocked it in their own Chrome, run the pass through Claude in Chrome instead.
  4. Reload and confirm the page's `<title>` and H1 match the ticket before you QA it.
  5. On a page that should be ungated (anything new), also file the gate in the QA Doc as a process item for the developer.
  6. Expect the same gate inside Markup (step 7 under **Posting visual findings to Markup**): its proxy does not carry the unlock, so pins read "pinned to a missing element" until a reviewer enters the password inside the markup.
  `/dev/` pages are also served from **`marketing.riverside.com/dev/<path>`** (which resolves to `riverside.com/dev/<path>`); that host is what the team hands out, and being on the production host means environment-only staging artifacts do not apply there. **The gate cookie is per-domain** - unlocking `riverside.com` does not unlock `riversidefm-design-com-domain-staging.webflow.io`, so a page you just opened can gate again on the other host.
- **A `/dev/` page can move to its final slug mid-review - but the un-prefixed slug may be a *different page entirely*.** Devs republish during QA, which drops the `/dev/` prefix and 404s the URL you started on (and the ticket's Staging URL column, which nobody updates). When a `/dev/` path starts 404ing, try the same slug without the prefix (`/dev/whats-new` → `/whats-new`) - the page is often live at the production slug, now un-gated. **Confirm it is actually the page under review before you QA it.** On 2026-08-09, `/dev/university-search` and `/university-search` were unrelated pages: the un-prefixed one was a stale published page that redirects to `/dev/university`. Check the `<title>` and H1 against the ticket before proceeding. Re-verify every finding against the new build, note the move in the QA Doc, and flag the stale Staging URL column.

### The automated pass

1. **Navigate** to the staging URL (apply the access workarounds above if blocked).
2. **Each breakpoint** - `resize_window` to 1280, then 768, then 390, then 375; screenshot each for evidence and check layout, text overflow, and overlapping elements.
3. **Console** - `read_console_messages` at load; report console errors (-> Performance & Technical checklist).
4. **Network** - `read_network_requests`; flag 404s, failed requests, and broken link destinations (-> Links & CTAs checklist).
5. **SEO metadata** - read `<title>`, meta description, OG tags (og:title / og:description / og:image), canonical, and the H1 via `read_page` (or a short `javascript_tool` snippet) (-> SEO & Metadata checklist). Optionally cross-check the rendered values against the page's configured settings in Webflow via the Webflow MCP (v2.0: `data_pages_tool` for page/SEO/OG settings and JSON-LD schema markup; `data_sitemap_tool` for the `includeInSitemap` flag) - a mismatch means the staged page and the CMS config have diverged.
6. **Content & structure** - `read_page` / `get_page_text` to verify copy is final (no Lorem Ipsum), headings and CTAs are present, and links resolve.

### Posting visual findings to Markup

Markup is where stakeholders consolidate visual feedback, and every Website Development ticket has a **MarkUp** column for it (`link_mm0c74hx` on a ticket, `link_mm624jtc` on a sub-item). Use `scripts/markup_client.py`; the full verified API contract, including two gotchas that return an opaque 500, is in `knowledge/markup-api.md`. Requires `MARKUP_API_KEY` in the environment - never in the repo, a QA doc, or a ticket.

1. **Reuse before you create.** Run `find-markup --url <staging-url>` first. If a markup for that page already exists, pin into it - even when the MarkUp column holds a hand-made invite link, which carries no markup id, so the page URL is the only way to match it. The API only reaches the ~99 most recently active markups, so if `find-markup` comes back empty while the column already holds a link, ask the reviewer which markup that is instead of creating a second. Only create one when nothing matches - the workspace allowance is 50 markups/month, and a re-QA should not consume a second. When you pin into a markup from an earlier round, start each pin with the QA date (`P1 - QA 2026-09-27: ...`) so it reads apart from the old threads, and list the earlier round's still-open threads in the QA Doc for the requester to close - the Financial Services markup carried 7 open threads from a design that no longer exists.
2. **One markup per page**, created from the same staging URL you reviewed:
   `create-markup --url <staging-url> --name "<page> - QA <YYYY-MM-DD>"`. Write the returned `markupUrl` to the MarkUp column (only when the column is empty - a link a person put there stays), and link it from the QA Doc and the ticket update.
3. **Access is by Markup membership.** The API identity (`marketing-os-v1`) owns every markup the agent creates, so a person signed in to Markup who is not a member sees "this markup is private" on the `markupUrl`. The fix is to invite them as a Markup user, not to change the link. If someone reports the private page, say so in the handoff: a Markup admin invites them (done for the Flow Ninja developers and requesters on 2026-09-27).
4. **One pin per visual finding**, at the breakpoint where it appears:
   `create-pin --markup-id <id> --page-url <staging-url> --selector "<css chain>" --x <0-1> --y <0-1> --breakpoint desktop|tablet|mobile --message "<severity> - <what is wrong -> what it should be>"`.
   You already have the element from the Step 2 DOM audit, so take its selector and the point as a **fraction of its bounding box** - offsets are 0-1, not 0-100. Lead the message with the severity, because pins are authored by the API identity rather than a person and need to stand alone.
5. **Derive the selector, do not hand-write it.** A pin is only useful if its selector
   resolves to exactly one element in Markup's own render. Walk up from the target building a
   class-and-`nth-of-type` chain and stop at the first chain that is unique, then assert it:

   ```js
   const sel = el => { const parts = []; let c = el;
     while (c && c !== document.body && parts.length < 6) {
       let s = c.tagName.toLowerCase();
       const cls = (c.className||'').toString().trim().split(/\s+/).filter(x => x && !/^w-/.test(x));
       if (cls.length) s += '.' + cls.slice(0,2).join('.');
       const sibs = c.parentElement ? [...c.parentElement.children].filter(x => x.tagName === c.tagName) : [];
       if (sibs.length > 1) s += `:nth-of-type(${sibs.indexOf(c)+1})`;
       parts.unshift(s);
       if (document.querySelectorAll(parts.join(' > ')).length === 1) return parts.join(' > ');
       c = c.parentElement; }
     return null; };
   ```

   Drop Webflow's generated `w-` classes - they are not stable. Verify every selector returns
   `1` before you spend a pin on it.
6. **Do not mirror non-visual findings into pins.** A missing meta tag or a console error has no place on the page to point at; it belongs in the QA Doc.
7. **Gated pages need one manual step.** Markup's proxy does not carry the Webflow gate cookie, so the markup opens on the password screen and every pin reads "This comment is pinned to a missing element" until the page is unlocked there - that is the gate, not a bad selector. Say so when you hand over the link: each reviewer enters the shared `/dev/` password once inside the markup. Do not put the password itself in the ticket or the doc.
8. **Reading feedback back.** `list-threads --markup-id <id>` returns every pin, its author, and reply count - use it to fold stakeholder comments into the ticket rather than asking people to restate them. `add-message --thread-id <id>` replies in place.

**Invite links cannot be generated via the API** - it returns only `markupUrl`, which is what the process uses (step 2). Some older tickets carry hand-made `app.markup.io/invite/accept/...` links instead; leave those in place and reuse the markup through `find-markup`.

### Browser-session hygiene (or you will report findings that aren't real)

The in-app Browser will hand you convincing false positives unless you control the session. Every rule below cost a false finding on the 2026-08-06 What's-new run:

- **Console and network buffers are cumulative per tab, not per page load.** After navigating, `read_console_messages` still returns errors from *previous* pages in that tab - including the `401` from a `/dev/` password gate. Two "uncaught TypeError" findings turned out to be leftovers from an earlier build plus the agent's own synthetic clicks. Before you attribute any console or network error to the page, load it in a **fresh tab** (`tabs_create` → `navigate`) and read the buffer from that single load.
- **Do your measurements before you interact.** Filter/search tests mutate the DOM (a left-over filter can hide every card), so a layout or alt-text audit run afterwards measures the filtered state. Audit first, interact second, or reload between the two.
- **A background tab has `innerWidth: 0`.** Tabs that aren't fronted are never laid out, so every rect is zero and everything reads as "not visible" - expect nonsense like `cards: 0, visibleImgs: 1`. Call `tabs_select` and `resize_window` before measuring, and sanity-check that `innerWidth` matches the breakpoint you think you're on.
- **Scroll-driven sections render empty in a tall capture.** A section that swaps its visual as you scroll (the industry pages' Record / Live Stream / Edit list) shows only its background in a `1280 × 6000` screenshot, and card images can look missing too. Before filing "image missing", check the element in the DOM: rendered size, cumulative opacity, `naturalWidth`. On 2026-09-27 every one of those gaps was a capture artifact.
- **Screenshots go blank or composite wrongly after scripted scrolling.** Once you scroll via `javascript_tool` (or the pane is hidden), captures come back blank or with the sticky nav stamped mid-page. For whole-page evidence, `resize_window` to the breakpoint width with a very tall height (e.g. `1280 × 3100`) and capture without scrolling.
- **Prefer a DOM audit over eyeballing screenshots for layout facts.** A short `javascript_tool` snippet that reports `documentElement.scrollWidth` vs `innerWidth`, elements whose `right` exceeds the viewport, and `scrollWidth > clientWidth` text nodes catches overflow and clipping deterministically, at every breakpoint, in one call.
- **Re-check anything that looks broken before you file it - and re-check the severity, not just the existence.** Two apparent P1s (an "empty Release Type filter", a "Clear button that doesn't reset") both evaporated on a second look - the first was a raced query, the second is the intended Clear-then-Apply pattern. On the 2026-08-09 run a console error looked like it killed 613 lines of filter/pagination JS until a check showed **none of that script's 13 target elements exist on that page** - a wrong-script-loaded P2, not a functional P0. Confirm the element, re-run the interaction, and confirm the blast radius before assigning severity.
- **`navigate` can be denied on an origin while `preview_start` works.** Throughout the 2026-08-09 run `navigate` returned "navigation ... was denied or failed" on the staging origin, while `preview_start {url: "..."}` loaded the same URL every time. Use `preview_start` as the navigation primitive - it also opens a **fresh tab**, which satisfies the fresh-buffer rule above for free. There is a tab cap; free slots with `tabs_close` rather than letting the cap block a page load.
- **`computer` clicks use screenshot-pixel space; `getBoundingClientRect` returns CSS pixels.** At a `1280 × 2400` viewport the screenshot came back `800 × 1518`, so JS-derived coordinates had to be scaled by `screenshot_width / viewport_width` (0.625) to land. An unscaled click hits empty space and reads exactly like "this control does nothing" - a false P0 waiting to be filed. Prefer `read_page` refs and click by `ref`, or scale deliberately and verify the element actually received the click.

### Is it this page, or the whole site? Check before you file

Site-level scripts throw errors on every page, and the `webflow.io` staging host breaks things that work in production. Filing either against the page under review sends the developer chasing a bug they didn't write. For each console error or failed request, do both checks:

1. **Another staging page** (e.g. `/university`) - if it reproduces there, it is site-wide, not this page's.
2. **Production** - `fetch()` the same path from a `riverside.com` tab and compare the status.

Worked examples from the 2026-08-06 staging and production passes, all three logged in `systems/owned/marketing-website.md`:

- **Site-wide (production).** `Uncaught (in promise) TypeError: c.call is not a function`, plus two Google One Tap / FedCM errors, appear identically on `riverside.com/university` - site-level Google Identity code, not the page under review.
- **Staging-host only.** `/api/v4/pricing/plans` → 404 on `webflow.io` but **200 on `riverside.com`**, because that API is served only from the app domain. The 404 also makes the head script log `Error loading API` and skip everything after it, so code paths downstream of it go untested on staging - check them again post-live.
- **Staging-host only, and beware the sloppy check.** The language switcher requests `/undefined/en.json` → 404 on every staging page, but on production no page requests it at all. Fetching that path on production *does* return 404 - which proves only that the path doesn't exist, not that the bug reproduces. Confirm the **request is actually made** in the environment you are judging, not just that the URL 404s.

Report site-wide and environment-only items in their own section of the QA Doc so the page's own verdict stays clean.

### A duplicated page keeps the original's invisible layer

Most new comparison, locale, and PPC pages start as duplicates of an existing page. The
visible copy gets rewritten; the parts nobody sees on screen do not. On the 2026-09-02
Riverside-vs-OpenReel round the rendered body contained **zero** occurrences of "Zoom" while
the entire machine-readable layer still described the Zoom page. Check each of these
explicitly - reading the page will not surface any of them:

| Where to look | What the leftover looks like |
|---|---|
| `meta[name=description]`, `og:description`, `og:title`, `og:image`, `og:url` | names the source page's subject, or ships its share image from a legacy site ID |
| WebPage / FAQ JSON-LD | `@id`, `url` and `name` still point at the source page's URL |
| `hreflang` alternates | point at `*-copy` slugs of the source (`/es/dev/riverside-o-zoom-copy`) |
| `canonical` | the source slug, or a leftover `/dev/` prefix |
| A duplicated section | two footers, two heroes - compare their **text**, not just their count |
| Stale hardcoded values | a copyright year that differs from the other copy's |
| CSS state classes | `is--webinars is--hosting-2-2` on a page that is neither: harmless in itself, but a reliable tell that the page was duplicated |
| CTA tracking parameters | every CTA still carries the source page's tag (`book-demo?utm_term=business_lp` on both industry pages), so conversions report as the source page |
| Visible sections left unrewritten | a testimonial, a closing headline or a pun from the source page (Technology shipped "Stop shorting your own content" and a wealth-advisor quote from Financial Services) - diff each section's copy against Figma, not just the hero |
| Hidden leftovers | `display: none` blocks from the source still in the DOM (a second logo set with a typo in its alt text) - invisible, but they ship |
| Shared components across sibling pages | one component instance feeding several pages, so a per-page asset swap never happened (both industry pages rendered the Technology hero carousel). Check the sibling page before filing, and say the fix must not break it |

A clean body is not evidence of a clean page, so grep the rendered text for the source
brand's name **and** read the `<head>` separately. Where a section is duplicated the two
copies are often *nearly* identical - on that run the two footers matched link-for-link
across all 106 links and differed only in the copyright year, so counting found them but
only a diff identified which copy was the stale one.

### Comparing against Figma

**Do the comparison. `get_metadata` failing is not a reason to skip it** - that mistake was made on the 2026-08-09 University run, where design fidelity was reported as unverified on all three pages and then turned out to be checkable in full, surfacing a P0 (an entire sidebar navigation missing from the build) that no amount of browser QA would have found.

Two rules, in order:

1. **Read the *sub-item's* Figma link, not the parent ticket's.** On the Website Development subitems board each QA sub-item carries its own `Figma Design` link (`link_mm6234qq`) pointing at that page's frame. The parent ticket's link often points at a whole board - judging the sub-item links by the parent's is what caused the 2026-08-09 miss.
2. **When `get_metadata` fails, go straight to `get_screenshot` on the same node.** Large nodes still fail `get_metadata` with an SSE/JSON parse error, but `get_screenshot` renders them fine. It is the way in, not a fallback.

```text
get_screenshot  fileKey=<from URL>  nodeId=1325:15082  maxDimension=1400   # overview read
get_screenshot  fileKey=<from URL>  nodeId=1325:15082  maxDimension=7580   # full res for detail
```

`get_screenshot` returns a short-lived URL plus the node's `original_width`/`original_height`. For fine detail (placeholder copy, field labels, search placeholders) pull the full-res PNG with `curl` and crop regions locally with `sips` - a 3248 × 7580 frame is unreadable at `maxDimension: 1024` but its hero crops cleanly. A frame typically holds the desktop *and* mobile artboards side by side plus dev annotation callouts; read the callouts, they carry instructions ("Add underline on hover on each Text CTA").

**A full-page frame may be unreadable at any `maxDimension`.** A whole-page design (e.g.
1440 × 12932) has roughly a 1:9 aspect ratio, so the render is clamped on its long edge and
arrives ~115px wide - enough for section order and presence, useless for type, spacing or
colour. `get_metadata` also fails on such a node, so you cannot enumerate its children to
screenshot them one at a time. And if `maxDimension` is itself rejected with `expected
number, received string`, the MCP layer is rewriting numeric arguments
(`references/integration-debugging.md`) and there is no way in during that session. Report
design fidelity as **structural only**, name the three failures, and say what a human would
need to do - rather than either claiming fidelity was verified or quietly omitting it.

What the comparison reliably catches that the browser pass cannot: whole components absent from the build, mislabelled navigation, and **which on-page values are the mockup's placeholders**. On the University run, `1h 35m` / `6.2k` / `Lorem ipsum` all appeared in the design too - proving the developer shipped the mockup as drawn and reassigning those findings from "dev bug" to "content gap", which changes who fixes them.

Only if the sub-item genuinely has no frame-specific link: say design fidelity is unverified, explain why, and ask for one (right-click the frame → Copy link to selection). Visual polish, hierarchy, and brand feel remain human-judgment calls regardless.

### Two findings that are usually false positives - check the distinction first

**`alt=""` is not missing alt text.** An explicit empty alt is the *correct* WCAG treatment for a decorative image that sits beside its own visible title and description - a card thumbnail in a listing grid, for example. It tells screen readers to skip the image instead of announcing a filename. A **missing** `alt` attribute is the actual defect. Audit them separately or you will report a large fake failure - on the 2026-08-12 University Search run a check written as `!img.getAttribute('alt') || !img.getAttribute('alt').trim()` reported "106 of 131 images missing alt text" when 105 of those were a deliberate `alt=""` on card thumbnails and only **one** genuinely lacked the attribute:

```js
const imgs = [...document.querySelectorAll('img')];
const missing = imgs.filter(i => i.getAttribute('alt') === null);          // the real finding
const decorative = imgs.filter(i => (i.getAttribute('alt') ?? 'x').trim() === ''); // usually correct
```

Only flag `missing`, and sanity-check `decorative` against whether those images really do sit next to equivalent text.

**hreflang alternates that 404 are only a defect if that locale is in scope.** Before filing a missing localised page, ask whether localised versions are launching with this page - on the University pages they were explicitly not. When the locale is out of scope the finding is not "build the German page"; it is the much smaller "remove the `hreflang` tag before publish, so production does not advertise an alternate that 404s". File it that way, at P2, and say plainly that it is not a localisation request.

### What to flag vs. what to check yourself

Never flag as "needs manual review" anything you can extract in the browser - a missing meta tag, a console error, a 404, an overflow at 375px are all findings you check and report, not defer. Reserve "needs human review" for genuinely subjective calls: visual polish and hierarchy, brand/tone feel, whether an image is on-brand or properly licensed, and copy quality.

---

## Issue Severity Guide

| Label | Meaning | Examples |
|---|---|---|
| P0 -- Blocker | Page cannot go live | Broken layout, missing key content, broken CTA, wrong production URL |
| P1 -- High | Must fix before launch | Typos in headlines, wrong brand colors, broken links, missing meta tags |
| P2 -- Medium | Should fix soon; can launch if timeline is tight | Minor copy edits, spacing inconsistencies |
| P3 -- Low | Nice-to-have; log for next iteration | Minor pixel adjustments, enhancement ideas |

---

## QA Checklist

### 1. Content & Copy

| Check Item | Priority |
|---|---|
| All headlines, subheadings, and body copy are final (no Lorem Ipsum) | P0 |
| Spelling and grammar are correct (spell-check + read aloud) | P1 |
| Brand voice is consistent: professional, empowering, creator-focused | P1 |
| CTAs are compelling and use approved copy (e.g. "Start for free", "Try Riverside") | P1 |
| Pricing, feature names, and product descriptions are accurate and up to date | P0 |
| Legal copy (disclaimers, copyright, terms links) is present where required | P1 |
| Claims about a competitor or third party carry a named source and an as-of date (review scores, pricing, feature gaps) | P1 |

### 2. Branding & Visual Design

<!-- REVIEW (future): the Purple #7C5CFF hex below is hardcoded here for reviewer convenience. Canonical brand tokens live in `.claude/skills/riverside-brand-guidelines/SKILL.md` and `references/design-system/tokens/`. Revisit and consider replacing the inline hex with a pointer to avoid drift. -->

| Check Item | Priority |
|---|---|
| Riverside logo displayed correctly -- correct version, correct placement | P0 |
| Brand colors used correctly (Purple #7C5CFF for accents; dark backgrounds for hero sections) | P1 |
| Typography matches brand guidelines: Instrument Sans, correct sizes and weights (fallback Arial/Helvetica only if Instrument Sans cannot load) | P1 |
| Images and videos are high quality, on-brand, and properly licensed | P1 |
| No unapproved stock photos, off-brand visuals, or placeholder images | P0 |
| Whitespace, layout proportions, and visual hierarchy look polished | P2 |

### 3. Links & CTAs

| Check Item | Priority |
|---|---|
| All links open the correct destination URL | P0 |
| External links open in a new tab; internal links stay in the same tab | P2 |
| No broken links (404s) | P0 |
| Primary CTA is prominent, above the fold, and functional | P0 |
| Sign-up/Start trial flows work end-to-end | P0 |
| UTM parameters or tracking links present on paid traffic CTAs (confirm with Growth) | P1 |

### 4. Responsiveness & Layout

| Check Item | Priority |
|---|---|
| Layout is clean and readable on desktop (1280px+) | P0 |
| Layout is clean and readable on mobile (375px, 390px) | P0 |
| No text overflow, broken grids, or overlapping elements on any breakpoint | P0 |
| Images resize and crop correctly at all breakpoints | P1 |
| Navigation/header and footer render correctly on all sizes | P1 |
| Modals, pop-ups, or banners (if any) work correctly and are dismissible on mobile | P1 |
| Nothing renders twice at any breakpoint -- a responsive variant shown without hiding the default duplicates it (seen with `show-mobile-landscape` on an FAQ heading, visible only at 375/390) | P2 |

### 5. SEO & Metadata

| Check Item | Priority |
|---|---|
| Page title is set, descriptive, and includes "Riverside" or the relevant keyword | P1 |
| Meta description is present, 150-160 characters, accurately summarizes the page | P1 |
| OG/Social share tags are set (og:title, og:description, og:image) | P1 |
| Canonical URL is correct -- no duplicate or conflicting canonicals | P1 |
| **Paid (PPC) landing page:** `robots` is set to `noindex, nofollow`. All Riverside paid pages ship this, so a **missing** directive is the finding - do not raise its absence as an open question, and do not raise duplicate-content concerns against the organic equivalent (see `systems/owned/marketing-website.md`) | P1 |
| Image alt text is present and descriptive for all non-decorative images - **`alt=""` is a pass, not a fail; see below** | P2 |
| H1 tag is present, unique, and matches the page's primary topic | P1 |

### 6. Performance & Technical

| Check Item | Priority |
|---|---|
| Page loads in under 3 seconds on a fast connection (Chrome DevTools or GTmetrix) | P1 |
| No console errors (F12 -> Console tab) | P1 |
| Tracking pixels and analytics events fire correctly -- see "Verifying tracking" below: inventory the deployed tags headlessly, then confirm each one actually fires via network requests during the Step 2 browser pass | P1 |
| Page-level custom code doesn't duplicate or shadow a site-level tag (double-counted conversions) -- see "Verifying tracking" | P1 |
| Forms (if any) submit successfully and trigger correct confirmation or redirect | P0 |
| Page is accessible: keyboard-navigable, sufficient color contrast, no Axe/Lighthouse errors | P2 |

#### Verifying tracking (don't just defer it)

This checklist used to punt the tracking line entirely to Growth/Data. Split it instead:
**what is deployed** is answerable headlessly via the Webflow MCP, **whether it fires**
needs the rendered page - and this skill already runs a browser pass in Step 2, so that
half costs nothing extra. Growth/Data is the escalation for neither of those, only for
"is this tag configured the way the campaign expects".

**Inventory both places scripts can live - don't assume, check.** As of 2026-07-27
riverside.com had **0** registered scripts and kept everything in freeform head/footer
blocks, but that can change the moment someone registers one, so run both reads and
treat an empty registered list as the expected-but-verified case rather than a given:

```text
data_scripts_tool > get_registered_scripts     (site_id)   # expect empty today - if NOT, inventory these too
data_scripts_tool > get_site_scripts           (site_id)   # 404 "Custom code block not found" = none applied, not broken
data_scripts_tool > get_site_freeform_code     (site_id)   # where the tags actually are today
data_scripts_tool > get_page_freeform_code     (page_id)   # page-level additions
```

Pass the resolved IDs (site ID in `systems/owned/marketing-website.md`; page ID from
`data_pages_tool > list_pages`). The site blocks are large (~18K chars head / ~33K
footer, 14 `<script>` tags each), so inventory them with a grep/script rather than
reading them into context whole.

What to check, in order:

1. **Ordering in `<head>`.** The first script in the site head preserves the original
   referrer and UTM params into `sessionStorage`, and its own comment says it **must**
   run before the language-redirect and Convert Experiences scripts, either of which
   can navigate away and wipe `document.referrer`. If a page adds head code that lands
   ahead of it, attribution silently breaks on that page - flag it P1.
2. **Duplication.** Site-level already carries Convert Experiences (A/B), HubSpot, and
   the Meta pixel in head, plus session-recording in footer. A page block re-adding any
   of those double-fires it. Compare the page inventory against the site inventory.
3. **Firing, during the Step 2 browser pass.** Presence in a block is never proof of
   firing - a tag can be present and still dead (wrong container ID, a JS error earlier
   in the block, consent gating). You are already in the browser for Step 2, so check
   `read_network_requests` for a request to each vendor you inventoried above. An
   inventoried tag with no matching request is a P1 finding, not a deferral. Escalate to
   Growth/Data only for what neither pass can settle - e.g. whether a tag that *is*
   firing is configured for the right campaign, property, or conversion event.

Never *edit* custom code as part of QA. `set_site_freeform_code` /
`set_page_freeform_code` replace the whole block, so a careless write drops every other
tag in it - QA reports the problem and hands the fix to the Marketing Website owner.
(For context: `register_inline_script` caps at 2,000 chars, so these 18-33K blocks
can't be migrated to registered scripts as-is either.)

---

## Escalation & Sign-off Rules

| Situation | Action |
|---|---|
| P0 issues found | **Do not approve.** Status stays at **QA** (`7`) - a human sets it. Notify the developer in `#webflow-riverside` with screenshots + description. Re-review after fix. |
| P1 issues found | **Do not approve until resolved.** Status stays **QA** (`7`); log details in the QA Doc. Developer fixes before launch. |
| P2/P3 issues | Log in the QA Doc for the next sprint. Page may launch at Marketing Ops' discretion. |
| Pass / all resolved | **Marketing Ops** (not the agent) sets status **Ready for live** (`10`), posts approval in `#webflow-riverside` (`C08DJ6BN3NX`) with the page URL (agents **draft**, humans send - see below), and notifies the developer to publish. After the developer publishes (**Published** `8`), Marketing Ops runs a quick **Audit post-live** (`13`) on production. |
| Uncertain about severity | Escalate to the **Marketing Website owner** (currently Jonathan Galili); for anything beyond a routine QA call, **Hanan Amos** (Head of Marketing Operations). |

---

## Quick Tips

- Review with fresh eyes -- take a break before your QA session if you were involved in creating the content.
- Open the page in an incognito window to see it as a new visitor (no cached assets, no logged-in session).
- Claude checks all four breakpoints automatically (1280 / 768 / 390 / 375); the human only spot-checks the subjective, on-device feel where it matters.
- Screenshot or record everything -- attach visuals to every issue for faster turnaround.

Questions? Post in **#webflow-riverside** (`C08DJ6BN3NX`) on Slack or reach out to the **Marketing Website owner** (currently **Jonathan Galili**, `U06NC1VQN7R`).

### `#webflow-riverside` is Slack Connect - agents draft, humans send

The channel is **externally shared** (the Webflow devs are contractors), so `slack_send_message` fails with `mcp_externally_shared_channel_restricted` every time. Use `slack_send_message_draft` (same channel ID) and hand the draft to the reviewer to send. This applies to the pass/fail approval post and any other message this skill would put in the channel - do not treat the error as an outage or a wrong channel ID, and do not fall back to a different channel. Get the wording right first time: there is no tool to edit or delete a Slack draft, and a second draft stacks rather than replacing the first (details under `#it-support` in `references/other_teams.md`).

---

## Output Format

Every QA review produces a **Monday QA Doc** by default; a branded `.docx` is generated only on request.

### Default - Monday QA Doc (every review)

Write findings to a **QA Doc on the Website Development ticket** (`18397093471`) - the working record the developer and stakeholders act on, matching how `hubspot-workflow-qa` logs findings. Create the doc attached to the ticket (`monday.com:create_doc`, `location: "item"`, `item_id: [ticket ID]`), title it `Page QA: [page name]`, and link/attach it in the ticket's **QA Doc** column. Then post a ticket update per the rules below, draft the `#webflow-riverside` message, and set the ticket's status per **Escalation & Sign-off** above - but **not** its priority.

#### Post the update on the item that holds the QA Doc

The verdict and the report belong side by side. On a **single-page ticket** that is the ticket itself - one doc, one update, done.

On a **multi-page ticket** it is the page's sub-item. On the 2026-08 Riverside University rounds every update went to the parent while the QA Docs sat on the sub-items, so each sub-item held a report with no verdict beside it and anyone following a single page got no notification. Add a parent update **only** for something genuinely cross-page: a round covering several pages, or a finding that spans sub-items (e.g. "the missing sidebar is confirmed on all four"). Keep it a roll-up pointing at the sub-items - never a repeat of a sub-item update, and never one per page.

#### The update is three lines, not a report

**The doc is the report; the update is a pointer to it.** This instruction used to ask for "verdict + issue counts by severity + top findings", which produced walls of text the team called out on the 2026-08 Riverside University ticket. Write exactly:

1. **Verdict line** - QA round done, which page, PASS / PASS WITH NOTES / FAIL, and the counts by severity.
2. **One or two lines** of what actually matters - the blocker, and anything notably good.
3. **A link to the QA Doc**, plus the `_Posted by the Marketing OS agent_` footer.

No severity-by-severity breakdown, no per-finding detail, no root causes, no tables, no restating what is already in the doc. If you are tempted to explain a finding, that belongs in the doc.

**One update per QA round.** When findings change - a correction, a new discovery, a scope answer - **revise the QA Doc**, do not post a second update. A running commentary on the ticket is noise, and the doc is the thing people act on.

**You cannot edit or delete a ticket update.** Same constraint as the Slack draft below: get the wording right the first time. A replacement update leaves the original sitting above it, and removing it needs a human. Draft the update in your head against the three rules above *before* calling `create_update`.

**The QA Doc column may already hold something that is not a QA doc.** The column takes one
doc, so `create_doc` fails with `CellLimitExceededException` - but that failure does **not**
mean a previous round wrote a report there. On ticket 12734037413 the column held a 25-block
"Brief template" authored by one of the ticket's own *requesters*, even though the board has a
dedicated **Brief** link column (`link_mm05cxb3`). Read the doc's `name` and `created_by`
before touching it. If it belongs to someone else, ask where the report should go instead of
rebuilding over their content - appending under a clear `# Page QA: <page>` heading is the
usual answer, and it leaves their blocks untouched:

```graphql
query { items (ids: [<id>]) { column_values(ids: ["doc_mm5fsegr"]) {
  ... on DocValue { file { doc { id object_id name created_by { name } } } } } } }
```

Append with `add_content_to_doc_from_markdown(docId, markdown, afterBlockId)`, passing the
existing doc's **last** block as `afterBlockId` so the report lands below their content.

**Revising a QA Doc (second pass, or new findings after the first write).** The QA Doc column holds **one doc per item** - `create_doc` against an item that already has one fails with `CellLimitExceededException` (`limit: 1`). So a revision is an in-place `update_doc`, never a replacement doc, and the doc URL stays stable. Rather than bolting an "Addendum" onto the end, rebuild the doc as one coherent version - renumber severities, fold new evidence into the finding it supports, and delete stale claims. Mechanics that bite:

- **Append first, delete second.** Put `add_markdown_content` ahead of the `delete_blocks` operations in the same `update_doc` call, so the doc is never momentarily empty and a failed delete leaves the new content intact.
- **Delete only top-level blocks.** `delete_blocks` rejects the **entire batch** with `BAD_USER_INPUT` if it contains table `cell` children. Filter to blocks whose `parent_block_id` is null; deleting a `table` removes its cells with it. Max 100 IDs per operation.
- **Get the block IDs with `jq`, not by eye.** `read_docs` with `include_blocks: true` blows the token cap and is written to a file instead; pull the IDs from there (`jq -c '[.data[0].blocks[] | select(.parent_block_id==null) | .id]'`) rather than transcribing UUIDs.
- **`blocks` is paginated, and ordered by id rather than document position.** `docs { blocks }`
  returns 25 by default, so a doc you have just appended 200 blocks to still reports 25 and
  looks like the write silently failed - pass `limit`/`page` before concluding anything. Because
  the order is by block id, you cannot reach "the last block" by paging to the end either. To
  find one block, request them all (the oversized result is written to a file) and search the
  saved JSON - but note a `test()` over raw content also matches block **ids**, so a hit on
  `401` came from a table block holding the child id `38833b5f-609b-4019-...`:
  `jq -r '.docs[0].blocks[] | select(.content|test("<text>")) | .id' <saved-result>.txt`
- **To replace one paragraph, use `update_doc_block`.** A fresh `content` payload
  (`{"deltaFormat":[{"insert":"...","attributes":{"bold":true}},{"insert":" ..."}]}`) edits it in
  place and keeps the block id. The append-then-delete dance above is only for rebuilding whole
  sections. Correcting a stale claim this way is also what keeps the doc a clean report rather
  than a changelog - the QA Doc describes the page, never the review's own revisions.
- **Verify afterwards** by re-reading and confirming zero old block IDs survive.

Use this structure for the doc:

```
# Page QA: [page name]
Staging URL: [link]   Production URL: [link]   Figma: [link]
Date: [date]   Reviewer: [name]
Verdict: PASS / PASS WITH NOTES / FAIL

## Summary
[1-2 sentence assessment + issue counts by severity]

## Issues by severity
### [Issue title]
- Severity: P0 / P1 / P2 / P3
- Device / breakpoint: Desktop 1280 / Tablet 768 / Mobile 390 / Mobile 375
- Location: [section / element]
- Current vs expected: [what is wrong -> what it should be]
- Evidence: [screenshot link]

## Checklist summary
[Category / Status / Notes]

## SEO metadata audit
[Tag / Value / Status]

## Recommended next steps
[Prioritized action items]
```

### Optional - Branded .docx Report (on request)

Generate a branded `.docx` **only when a formal or shareable report is requested** (e.g. a sign-off record for senior management). It carries the same content as the Monday QA Doc, styled to brand.

#### Before Writing the .docx

Read these three skills in order - each one adds a layer the report needs:

1. **`riverside-brand-guidelines`** (`.claude/skills/riverside-brand-guidelines/SKILL.md`) - Riverside's color palette, typography, and design patterns. This is the visual foundation.
2. **`docx`** (invoke the `anthropic-skills:docx` skill) - The technical guide for creating .docx files with the `docx` npm package. Follow its rules exactly (dual widths on tables, ShadingType.CLEAR, US Letter page size, etc.).
3. **`ai-diligence-statement`** (invoke the `anthropic-skills:ai-diligence-statement` skill) - The branded AI Diligence Statement that goes at the end of every deliverable.

#### File Naming

```
QA-Report_[page-name]_[YYYY-MM-DD].docx
```

#### Report Styling (Quick Reference)

These come from the brand guidelines - read the full skill for details, but here's the essential mapping for QA reports:

| Element | Style |
|---|---|
| Page size | US Letter (12240 × 15840 DXA), 1-inch margins |
| Header | "Riverside.fm" in Purple `#7C5CFF`, page title in Mid Gray `#2A2A35` |
| Footer | Page numbers in Mid Gray `#2A2A35` |
| H1 | 18pt Arial Bold, Near Black `#0F0F14`, with Purple accent bar underneath |
| H2 | 14pt Arial Bold, Riverside Purple `#7C5CFF` |
| H3 | 12pt Arial Bold, Dark Gray `#1C1C24` |
| Body text | 10.5pt Arial Regular, Near Black `#0F0F14` |
| Table headers | Near Black `#0F0F14` fill, White `#FFFFFF` text, Bold |
| Table rows | Alternating White / Purple Light `#EDE8FF`; Light Gray `#E6E6EB` borders |
| Verdict cell | Green fill for PASS, Red fill for FAIL, White bold text |
| AI Diligence | Last section, preceded by Purple accent bar, per ai-diligence-statement skill |

#### Report Structure

The .docx should contain these sections in order:

1. **Title page info** - Page URL, Figma URL, date, reviewer, verdict (as a colored badge)
2. **Issue summary table** - Severity counts
3. **Issues by severity** - Each issue with: severity, device, location, current vs expected, impact
4. **Checklist summary** - Category / Status / Notes table
5. **SEO metadata audit** - Tag / Value / Status table
6. **Recommended next steps** - Prioritized action items
7. **AI Diligence Statement** - Branded per the ai-diligence-statement skill
