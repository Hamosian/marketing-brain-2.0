# Marketing website page-type registry

The source-of-truth for how each riverside.com page type gets built or updated:
its clone source, component kit, indexing policy, and the QA it needs on top of
the standard pass. Read by `/page-build`. **When a page type's convention
changes, edit this one file - not the skill.**

The skill is one workflow; this registry is what varies. Adding a page type is a
row here, not a new skill.

## How a profile is used

`/page-build` resolves the page type from the ticket, reads that row, and uses
it to pick the page to duplicate and the checks to run. A row whose **Clone
source** is `undefined` cannot be built by the skill - it stops and asks, rather
than guessing a source. Guessing one would seed every future page of that type
from the wrong parent.

## Registry

| Page type | Clone source | Indexing | Board | Status |
|---|---|---|---|---|
| **PPC landing page** | `/home` - Webflow page id `69ca3c516830a7bb08862713`, internal name "Home SF - Home All In One" | `noindex, nofollow` - **required**, its absence is the finding | Website Development (`18397093471`) | **Defined** (2026-09-15) |
| **Webinar landing page (CMS item)** | Webinars CMS item `687657b161f1ac622a212865` ("Riverside Demo: Get a tour of your studio") - an **item**, not a page; the collection's template page renders it | indexable, like every published webinar | None - intake is `/launch-webinar` | **Defined** (2026-10-05) |
| Feature page | `undefined` | indexable | Website Development (`18397093471`) | Needs mapping |
| Comparison / vs page | `undefined` | indexable | Website Development (`18397093471`) | Needs mapping |
| Use-case page | `undefined` | indexable | Website Development (`18397093471`) | Needs mapping |
| Industry page | `undefined` | indexable | Website Development (`18397093471`) | Needs mapping |
| Tools page | `undefined` - these are **CMS items** on the Tools collection (`685be7dcd32275d383065738`), rendered by a template page, so "cloning a page" may not be the right shape at all | indexable | Website Development (`18397093471`) | Needs mapping |
| University page | `undefined` | indexable | Website Development (`18397093471`) | Needs mapping |
| Pricing page | `undefined` - heavy custom JS (plan switches, pricing scripts); likely never a clone target | indexable | Website Development (`18397093471`) | Needs mapping |

Only the PPC and Webinar rows are decided. The rest are listed so the gap is
visible and so a new type is added by filling a row rather than inventing a
convention. Clone sources for the other types are open work (Jonathan Galili,
2026-09-15).

## PPC landing page - full profile

- **Clone source:** `/home` (id above). **Not `/lp/home`** - a separate live page
  with the same title and the same robots directive, and easy to grab by mistake.
- **Component kit:** the components recorded in `systems/owned/marketing-website.md`
  ("PPC landing-page component kit") - `Main Button`, `Global CSS`,
  `G2 Reviews - Text`, `Performance Footer`, and `nav-basic-lp` for the nav.
- **Nav:** a `/home` clone arrives with the **native Webflow Navbar**, which is not
  a component and genuinely cannot be rebuilt through the Data API. That does not
  mean you are stuck with it. The approved acquisition LPs use the `nav-basic-lp`
  **component** instead, and `data_component_tool > insert_component_instance`
  places it (verified 2026-09-17 on the YouTube test page: inserted into the
  `nav-wrapper`, then the inherited `NavbarWrapper` removed). The instance's
  default prop values already matched the reference page's on all thirteen props,
  so no overrides were needed - check that before setting any. The wrapper also
  needs `is--fixed` alongside `nav-wrapper is--transparent`.
  An earlier version of this row said the native Navbar "must never be replaced";
  that was too strong, and it is what left the first build of this page with the
  wrong nav.
- **CTA contract:** `Main Button` props are `Variant`, `Link`, `Text`,
  `Button ID`, `Visibility`. On the clone source every instance reads
  "Get Started" and points at `https://riverside.com/start`.
- **Do not de-duplicate the CTA ids.** Five CTAs on `/home` share
  `id="hero-get-started"`. This may be intentional and is under investigation;
  `systems/owned/marketing-website.md` carries the standing instruction to leave
  it alone. A clone inherits it, and that is expected.
- **Footer:** `Performance Footer`, variant `Base`. Webflow is authoritative for
  the footer, which is the one exception to the Figma-wins rule.
- **QA additions** on top of `marketing-website-page-qa`'s standard pass:
  `noindex, nofollow` **present** (a missing robots tag is the finding, not an
  open question); UTM parameters preserved through the CTA path; form routing to
  HubSpot/ChiliPiper if the page carries a form; no collision with a running
  Convert Experiences test; and message match between the ad promise and the
  page's first fold.

## Webinar landing page (CMS item) - full profile

Every riverside.com webinar page is an item in the **Webinars** collection
(`685be7dcd32275d38306553f`, site `685be7dcd32275d3830651d3`), rendered by the
collection's template page. So "cloning" here means duplicating an item, not a page.
The Webflow API has no duplicate call: read the template item's `fieldData`, then
`create_collection_items` a new item from it with the overrides below, `isDraft: true`,
primary (EN) locale only. Never `create_page`, never edit the template item, never
touch the collection template page.

- **Clone source:** item `687657b161f1ac622a212865`, "Riverside Demo: Get a tour of
  your studio". It carries the current layout switches (`webinar-v2` on) and Kendall
  as host. It is a live, recurring page, so it is read, never written.
- **Intake:** `/launch-webinar`, not a Website Development ticket. There is no Figma:
  the template page owns the layout, so G1's brief and Figma table does not apply.
  The source for every string is the approved copy file from `/riverside-event-copy`
  (its `landingPage` object), plus the event schedule, the guest, and the HubSpot form
  GUID the Webinar Launch Action created.
- **Field map.**

  | Field | Set to | Source |
  |---|---|---|
  | `name` | The event title | `landingPage.name`; must equal the Riverside event title |
  | `slug` | The title, slugified | Must be unique in the collection: check with `list_collection_items` filtered by `slug`. If taken, append `-<mon>-<yyyy>` of the event date; if that is taken too, stop and ask |
  | `description` | Preview text | `landingPage.description` (single line) |
  | `content` | Landing page body | `landingPage.content` (rich text HTML) |
  | `date` | The event's calendar date in the display time zone, written as `YYYY-MM-DDT12:00:00.000Z` | Noon UTC lands on the same calendar day across the Americas, Europe and Israel. The page shows the time from `hour` and `time-zone`, not from this field |
  | `hour` | 24-hour start time in the display time zone, `HH:MM` | Computed from the event start; never typed. The display zone is New York unless the audience is outside the US (`/riverside-event-copy`, Times) |
  | `time-zone` | `EDT` or `EST` for New York, otherwise the GMT offset (`GMT+3`) | Computed for the event date; never hardcoded. Must match the times in the emails |
  | `hubspot-form-id` | The new webinar's form GUID | `tools/webinar-automation/config/webinars.json` on `origin/main`, after the Action's `create` run. A `TODO` value means the form does not exist yet: stop |
  | `speakers` | The guest's Speaker item, then Kendall (`685be7dcd32275d3830676cb`) | Max 5, shown in this order |
  | `show-speakers` | `true` | Kept from the template |
  | `related-webinars` | The 3 most recent **published** Webinars items, excluding this one | Max 3 |
  | `youtube-id` | `null` | The template's would play the demo video on the new page. Set it when the stream or replay exists |
  | `thumbnail-image` | The requestor's image, uploaded; otherwise `null` | `null` is a **pre-publish blocker** in the handover: the template's demo thumbnail would mislabel the webinar everywhere it is listed |
  | `form-title`, `webinar-v1`, `webinar-v2` | Kept from the template | |
  | `video-length`, `hero----background-image`, `cover-image`, `thumbnail-border-color` | `null` | As on the template |

- **The guest's Speaker item** (Speakers collection `685be7dcd32275d383065563`). Look
  the guest up by name first. One match: reuse it, and **never edit it**, because a
  Speaker item is shared by every page that lists that person. Several matches: ask
  which. None: create a draft Speaker item with `name`, `slug`, `role`, `description`
  (the bio, one line), `linkedin`, and `photo` if a headshot was given (upload it with
  `data_assets_tool > create_asset`; an Image field needs both `fileId` and `url`). A
  missing headshot is listed as a gap, not a blocker.
- **Indexing:** indexable, like every published webinar. Do not change robots or sitemap
  settings.
- **QA additions** (this type's G4). Re-read every item you created and compare each
  field with the map: the form GUID equals the config's, the slug is unique, the
  speakers resolve, `name`/`description`/`content` contain no em or en dashes, and both
  items are still drafts. **A draft CMS item cannot be rendered before it is published**,
  and agents may not publish, not even to staging. So the rendered check is the
  human's preview in the Designer (CMS, the Webinars collection, the item, then preview),
  and the full `marketing-website-page-qa` pass runs on the live URL after the human
  publishes, including one test registration that lands in the webinar's intake list.
- **Publish (G5, human).** `data_cms_tool > publish_collection_items` on Webinars
  `685be7dcd32275d38306553f` for the new item id, primary locale; if a Speaker item was
  created, publish it first in Speakers `685be7dcd32275d383065563`, or the page shows no
  guest. A single-page `publish_site` does **not** publish CMS items.
- **Locales:** primary (EN) only. The template item exists in EN alone (checked
  2026-10-05).
