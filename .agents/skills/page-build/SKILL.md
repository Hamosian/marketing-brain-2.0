---
name: page-build
description: Clone an approved riverside.com page in Webflow and source the new page's content from its Figma and brief, producing a built draft. Use when the design already exists and construction in Webflow is what remains. Handles PPC landing pages and webinar landing pages (a draft Webinars CMS item duplicated from its template, called by /launch-webinar) today, and other page types as their profiles are defined. Triggered by "build the PPC landing page", "build this LP", "build the PPC LP", "build it in Webflow", "clone /home for this", "draft the webinar landing page", or "turn this brief into a built draft".
---

# Page Build

Turns a Website Development ticket into a built page on riverside.com. The job is
**clone an approved page of the right type, then swap in the brief's content** -
not assemble a page from elements. One workflow, many page types; what varies per
type lives in `references/page-type-registry.md`.

**Some page types are CMS items, not pages.** A webinar landing page is an item in
the Webinars collection, rendered by the collection's template page. For those, the
clone is a duplicated item and the content is field values; the profile in the
registry names the template item, the intake that replaces the ticket, and the field
map. Where a step below reads differently for a CMS-item type, it says so.

You source content, you do not invent it, and you never publish.

**Not this skill.** Filing or writing the ticket is `pm-story`. Triaging website
work generally is `website-agent`. Constructing from a bare Figma spec with no
brief is `webflow-build-agent` (this skill calls it). Auditing an existing page
for conversion is `page-cro`. Reviewing an already-built page before launch is
`marketing-website-page-qa` (this skill calls it at G4).

## Inputs and context to load

- `knowledge/prerequisites.md` - the G0 preflight checks and how to fix each
  one. Always, first.
- `references/page-type-registry.md` - the page-type profile. Always.
- `systems/owned/marketing-website.md` - the component kit, build failure modes,
  and the publishing rule. Always.
- The ticket on **Website Development** (`18397093471`).
- `page-cro` only when the brief leaves a section's intent unclear and you need
  the page type's conversion goal to interpret it.

## The six gates

The run advances through named gates. Today **every gate needs a human to
advance it**; the end state is that G0-G4 advance on their own. G5 never does.

| Gate | What it means | Advances today |
|---|---|---|
| G0 Preflight | Tools and access confirmed, or a fix list handed over | Human |
| G1 Intake | Ticket resolved, brief and Figma in hand, page type known | Human |
| G2 Clone | The new page exists as a draft copy of the clone source | Human |
| G3 Content | Brief content placed, gaps listed | Human |
| G4 Verified | `marketing-website-page-qa` pass is clean | Human |
| G5 Publish | The page goes live | **Human, always** |

## Steps

### G0 - Preflight
- Run the checks in `knowledge/prerequisites.md` **before reading the ticket**.
  They are cheap, and each one has blocked a real run.
- Report them as one short table, then move on. If everything passes, say so in
  a line - do not narrate the checks.
- On a failure, stop and hand over the fix list from that file: plain language,
  one concrete thing to do, and what it unlocks. Do not start building around a
  missing input and discover it at G3.
- Check only what this run needs. A brief-only text change needs no Figma, so a
  Figma failure is not a blocker for it - say which checks you skipped and why.
- Two things are **never** preflight failures: the Data API cannot create Grid,
  Container or `HtmlEmbed` elements, and the asset endpoint rate-limits. Those
  are platform limits with known workarounds, not missing access. Do not ask
  anyone to fix them.

### G1 - Intake
**CMS-item types skip steps 1-3.** Their intake is the one the profile names (a webinar
landing page comes from `/launch-webinar`, with an approved copy file instead of a
brief, and no Figma because the template page owns the layout). Check that every input
the profile's field map needs is present, then go to step 4.

1. Read the ticket. Pull Figma (`link_mm05q7wr`) and the brief from **either**
   Brief column: `link_mm05cxb3` (link) or `doc_mm77q17p` (monday Doc - read its
   content with `read_docs` on the `objectId`). Two columns share that title;
   checking one and reporting "no brief" is a known false blocker.
2. **Decide whether the inputs are enough.** The Figma is the strong input; a
   brief on its own almost never is.

   | Brief | Figma | Verdict |
   |---|---|---|
   | yes | yes | Build. The normal case. |
   | no | yes | Build. A Figma alone is sufficient. |
   | yes | no | Only a crystal-clear text change - see 3. Otherwise stop and ask for the Figma. |
   | no | no | Stop. There is nothing to build from. |

3. **The brief-only exception is narrow.** It applies only when *every* one of
   these holds:
   - it updates an **existing** page, not a new one;
   - it changes **text only** - no layout, no new element, no image, no
     component, no CTA target;
   - the element **already exists** on the page;
   - the replacement text is **stated verbatim**, not described;
   - exactly **one** element on the page matches.

   **If you are weighing whether it qualifies, it does not.** Ask for the Figma.
   Asking costs a message; guessing costs a wrong production page.
4. Resolve the page type and read its row in the registry. If **Clone source is
   `undefined`**, stop and ask which existing page to base it on. Never pick one.
5. Restate what you are about to build and wait. Include the target slug.

### G2 - Clone
**CMS-item type:** read the template item's `fieldData` (`list_collection_items`
filtered by `id`), then `create_collection_items` one new item from it with the
profile's overrides applied, `isDraft: true`, primary locale only. There is no
duplicate call, and the template item is never written. Any companion item the
profile names (the guest's Speaker item) is looked up, reused or created first, as a
draft too. Steps 5-6 do not apply.

5. Duplicate the clone source with `create_page` (`duplicateOf`), `draft: true`.
   Never build the structure from elements - cloning is what gets you a compliant
   page shell. The clone arrives with `/home`'s **native Webflow Navbar**, which
   cannot be rebuilt through the Data API; that does not mean you are stuck with
   it. Acquisition LPs use the `nav-basic-lp` component, which
   `insert_component_instance` places - see the registry's Nav row.
6. Set the page's slug, SEO title and description from the brief.

### G3 - Content
**CMS-item type:** the content is the field map's values, written in the G2 create.
Source every string from the approved copy file; anything it lacks is left as the
profile says and listed under `## Gaps`. Steps 7-8 do not apply; steps 9-10 do.

7. Pull the Figma spec **per frame**, never a whole page node - a page-level node
   exceeds the MCP transport limit and fails mid-stream. A brief may link a
   **FigJam board** (`figma.com/board/...`) for copy, which the design-file tools
   cannot read; use `get_figjam` for those. Design and copy are often two
   different Figma products in the same ticket.
8. Place the brief's content through `webflow-build-agent` - it owns the Data API
   failure modes. **Build with `data_whtml_builder`, not `data_element_builder`:**
   the element builder silently discards `styleNames` and `text` (you get unstyled
   nodes, `h1` "Heading" and Lorem ipsum), cannot create `Grid` elements at all,
   and leaves most combo classes unappliable afterwards. The HTML builder resolves
   classes by their hyphenated CSS form and lands a whole section in one call.
   What it cannot do: write `HtmlEmbed` code, or accept a media query outside
   Webflow's six standard breakpoints - both stay a human paste. Full trade-off:
   `systems/owned/marketing-website.md`. Do not drive those tools directly from here.
9. **Source, don't invent.** Every string and asset on the page traces to the
   brief, the Figma, or the clone. Where no source covers a section, leave the
   clone's content and list it as a gap. Do not compose prospect-facing claims
   for a paid page.
10. Apply the profile's indexing policy and leave inherited quirks alone - the
    registry names them, and a clone is expected to carry them.

### G4 - Verify
11. Hand to `marketing-website-page-qa` for the rendered pass, plus the profile's
    QA additions. Structural checks are not visual checks.
    **CMS-item type:** a draft item does not render anywhere an agent can reach, so
    G4 is the profile's field-level re-read plus the human's Designer preview. Say
    plainly that the rendered pass happens on the live URL after the human publishes.

### G5 - Publish
12. **You do not publish.** Hand the human the exact publish to run - full site,
    single page (`publish_site` takes an optional `pageId`), or collection items -
    with the target domains named. Approval to build is never approval to publish.

## Constraints

- Every claim on the page comes from the brief, the Figma, or the clone source. For a
  CMS-item type the approved copy file is the brief.
- If the page type is unknown or its clone source is `undefined`, stop and ask.
- If the brief and the Figma disagree, the Figma marketing design system wins,
  except the footer, where the live Webflow component wins. A genuinely new
  conflict is raised, not silently resolved.
- Confirm before every mutating call. Cloning a page is a mutation.
- Never de-duplicate or tidy something the registry says to leave alone.
- **Verify what landed, not what you sent.** Re-read every element you created and
  confirm its `styleNames`, text and tag are actually present. A builder returning
  success is not evidence the styling applied, and matching text is not evidence a
  section matches its design - that mistake is what put four "placed" sections in
  front of a reviewer who could see they matched nothing.
- Report a section as placed only after that re-read. Anything short of it belongs
  under `## Gaps`, named, not rounded up to done.
- **A clean element read is not a rendered page.** The defect that hides best is
  a rebuilt `Grid`: its class carries the column tracks but not `display: grid`,
  so the tree reads perfectly and the page renders as one tall column. That fix,
  and where embed code has to live instead, are in
  `systems/owned/marketing-website.md`. Check both before handing to QA.
- **Diff the served HTML against the DOM before blaming the build.** A site head
  script rewrites `/start` CTAs at runtime, so a link can be correct in the
  source and doubled in the DOM. Same class of trap as the console errors below:
  the build gets blamed for what the site does to every page.
- **Verify at more than one width.** A structural read and a 1280px check both
  passed while the testimonials section sat flush left at 1600 - `margin: auto`
  computes to `0` below an element's `max-width`, so the defect is invisible at
  the width you probably tested. Check wide, 1280 and mobile, and re-assert the
  viewport each time: the browser pane clears it between turns, which produced
  two false "this did not publish" calls in one session.
- **Say in the handover that the page is not Designer-native.** A page built this
  way is correct published and degraded in the canvas: Grid and Container come
  out as plain divs, and anything that had to go in page custom code does not
  render in the Designer at all. Whoever maintains it next will open the canvas
  and see a broken layout. Name it rather than letting them find it.
- **Do not try to migrate variant CSS into the style system.** Layout that an
  approved page applies through an ancestor-scoped embed (`.is-acq .thing`) is
  overriding shared classes that other pages depend on for the *other* variant.
  Webflow classes cannot express that scoping, so it stays as CSS - the reference
  page does the same. Only move a declaration when every element carrying that
  class wants that value.
- **Prefer a combo class over editing a shared one.** Both write real Webflow
  styles, but the risk is not comparable: a combo touches only what you apply it
  to, while a shared class reaches every page using it and the damage is *latent* -
 other pages keep the old value until someone republishes them. Edit a shared
  class only after enumerating its users and confirming they all want the new
  value; the how is in `systems/owned/marketing-website.md`.
- **Classify every console error against the clone source before reporting it.**
  A clone inherits the parent's scripts, so errors from elements that only exist
  on the parent follow it over. On the 2026-09-17 pass all four console errors on
  the built page reproduced identically on `/home` - none were the build's.

## Output schema

## Build result
- Ticket / page type / target slug:
- Clone source used:
- Gate reached: (G1-G5)
## Content placed
- (section → source; write "None" if nothing was placed)
## Gaps
- (sections the brief did not cover; write "None")
## Verification
- (what page-QA checked, and what it could not - embeds, custom code, blur, mobile widths; for a CMS item, that nothing was rendered before publish)
## For the human to do
- (the exact publish, or the blocker to clear; write "None")

## Done when

The page exists as a draft, every brief section is either placed or listed as a
gap, page-QA has run, and the human has been handed the publish. The run is
finished **before** the page is live, always.
