<!-- last-reviewed: 2026-09-29 (added Redirects and Cookie consent sections, read live from Webflow and CookieHub) -->
<!-- prior: 2026-09-29 (login status on marketing pages via /api/v4/pricing/plans: the three response shapes, the empty-string priceId trap for Free users, testing only on riverside.com hosts, and /pricing/switch always redirecting) -->
<!-- prior: 2026-09-27 (staging pages no longer password-gated; /dev/ gate password moved to 1Password. Previous: 2026-09-23 Marketing Website onboarding for Jonathan Ydov) -->
<!-- prior: 2026-09-23 (the sitemap omits /lp/* entirely, so a sitemap-driven crawl reports clean on the paid landing pages; locale equivalence should be read from each page's own EN hrefLang rather than a slug map, and the global language redirect preserves the query string across the EN to DE hop). Previous 2026-09-17 (agentic page build, ticket 13050711075: the HTML builder is the right primitive, native Grid/Container/HtmlEmbed cannot be created, styles belong in the style system but a shared class needs its users enumerated first, and publish behaviour differs for element vs style writes) -->
<!-- prior: 2026-09-17 (agentic page build, ticket 13050711075: the HTML builder is the right primitive, native Grid/Container/HtmlEmbed cannot be created, styles belong in the style system but a shared class needs its users enumerated first, and publish behaviour differs for element vs style writes) -->
<!-- prior: 2026-09-15 (recorded the second Brief column on Website Development - two columns share that title and the repo knew only the link one, so every brief check could report a false blocker) -->
<!-- prior: 2026-09-15 (added the PPC landing-page component kit derived from the clone source - five components, the Main Button prop contract, the native-Navbar constraint, and the duplicate hero-get-started ids left deliberately untouched pending investigation) -->
<!-- prior: 2026-09-15 (recorded the marketing web design-system sources - the Figma library key the repo previously named but could not resolve - the PPC LP clone source, brief ownership, and the Figma-vs-Webflow precedence rule with the footer as its one exception) -->
<!-- prior: 2026-09-15 (added the CDN and edge routing section - the Cloudflare to CloudFront migration and the marketing/app path split - and the GTM container + Segment loading facts under site tracking; found while speccing Google Tag Gateway) -->
<!-- prior: 2026-08-30 (split Convert Experiences behavior out into systems/owned/convert-experiences.md and pointed to it from the tracking + Related Systems sections) -->
<!-- prior: 2026-08-23 (added the Paid (PPC) landing pages conventions - noindex/nofollow on all paid pages, and paid variants sitting alongside rather than replacing their organic equivalent - found during the Business Owners Request a Demo LP QA) -->
# Marketing Website

> riverside.com marketing pages, SEO program, accessibility, localization, and web monitoring. Owned by the Marketing Website role within Marketing Operations (Jonathan Ydov, Web Developer, from 2026-09-27; covered interim by Jonathan Galili until then; previously Yuval Tsabar).

## Overview
The marketing website covers riverside.com page production, conversion experiments, SEO surfaces, localization, accessibility remediation, and live-site monitoring. It is a distinct sub-stream inside Marketing Operations because it has its own board, channels, owners, and recurring operational load.

## Ownership
- **Lead:** Jonathan Ydov (Web Developer, reports to Hanan) from 2026-09-27. Until then covered interim by Jonathan Galili (Senior Marketing Tech Manager, reports to Hanan); previously Yuval Tsabar, who has left. Day-to-day execution is carried by the Webflow agency Flow Ninja (see Working with Flow Ninja).
- **Function:** Sub-stream of Marketing Operations, with its own monday board and primary Slack channel because the workflow (page builds, A/B tests, localization) is distinct from the rest of MOps.
- **Onboarding:** the Marketing Website onboarding doc (2026-09-23) is the new-hire walkthrough of this system: <https://docs.google.com/document/d/1784KKtEBrMuejeWRW0AEZtrfc9dGtEGT/edit>. Access owners for every tool it uses are in `references/other_teams.md` → Access provisioning.

## Working with Flow Ninja (as of 2026-09-23)

- **One Webflow agency: Flow Ninja.** Milutin and Dusan develop; Andrija Djuric ("Djura") leads their team (Jonathan Galili, 2026-09-23). Flowout (Davor), the second agency, finishes the week of 2026-09-20, so older board items and threads name Davor.
- **Where to reach them:** `#website-dev`, where they post as external members. Priority changes go there with the monday ticket link, and status updates are requested there (observed pattern).
- **Publishing norms** (Milutin, `#website-dev`, 2026-09-16): staging publishes are open at any time; **production publishes are agreed with Flow Ninja first**; and any change made on the site by someone else is posted in `#website-dev`, because a full-site publish takes everyone's in-progress work live, not only the publisher's. These norms sit on top of the human-only publish rule in Publishing safely below, they do not replace it.
- **Before a production deploy, every developer working on Webflow confirms it is safe.** A full-site publish ships everyone's in-progress work, so the "is it safe to deploy?" check is a conversation between all developers currently working in the site, not a sign-off from one named person (Jonathan Galili, 2026-09-23). Until September 2026 Flow Ninja asked Flowout's Davor; from then it runs in `#website-dev` between Flow Ninja, the Web Developer, and anyone else with work in flight.
- **Large page work is built on Webflow branches** (`branch--<name>-riversidefm-design-com-....webflow.io` review URLs, e.g. the 2026-09 transcription page and the 2026-08 navbar update) and merged after review. Review on the branch URL, and expect that some live behaviour (for example running a transcription) does not work there.

## How Claude Works With This
| Action | How |
|--------|-----|
| Page changes / dev tickets | monday: Website Development board (`18397093471`) |
| Day-to-day discussion | Slack: `#website-dev` (`C0AM2HQMY49`) |
| Accessibility work | Ticketed on the Website Development board; `webflow-accessibility-audit` for a headless WCAG pass. `#website-accessibility` is no longer used (2026-09-23) |
| Investigate live issues | Slack: `#marketing-website-monitoring` (`C05FK3G82H4`); synthetic 404 checks in Groundcover (see Monitoring) |
| Website infrastructure asks to R&D/DevOps (robots.txt, sitemap, DNS, CDN paths) | Discuss in `#marketing-dev` (`C0AA8HABQKG`); file new DevOps work through the `#devops-help` form (`references/other_teams.md`) |
| SEO analysis | `seo-ai-search-agent`; source tools include Ahrefs and Search Console when access is available |
| CRO analysis | `website-agent` plus `page-cro`; confirm tracking before launch |
| Direct site data ops (CMS, pages, schema markup, sitemap flags, forms, assets, custom code, site analytics) | Webflow MCP (v2.0) via `website-agent` - no Designer session needed for most operations; all writes gated per the safety rule |
| Locale publish queuing (stage localized CMS items for next site publish) | `webflow-locale-publish-queue` - Designer UI via Claude in Chrome; still not expressible via the API/MCP (see Platforms & Tools) |

## Accessing Staging

**New staging pages are not password-gated** (decided by Jonathan Galili, 2026-09-27). The `/dev/` gate stopped agentic page QA, because the agent does not enter passwords, and it added a manual unlock step to every review. Staging stays out of search regardless: `riversidefm-design-com-domain-staging.webflow.io/robots.txt` is `Disallow: /` (checked 2026-09-27). Pages built before the decision may still live under `/dev/`.

Staging pages are public, but two gotchas block browser/agent access:

- **VPN-gated `stg.riverside.com`.** The `stg.riverside.com` subdomain sits behind Cloudflare Warp (VPN). A browser or agent without the VPN gets a **403**. Workaround: replace the host `stg.riverside.com` with the Webflow staging host `riversidefm-design-com-domain-staging.webflow.io` (keep the path) and retry - it serves the same pages without the VPN.
- **Password-protected `/dev/` paths.** Any staging URL whose path contains `/dev/` is Webflow password-protected. The shared password is intentionally kept out of this repo; it lives in 1Password: [staging `/dev/` gate](https://start.1password.com/open/i?a=KX2C2OYDZVE6XPI5VH5ZP2PEYE&v=izs333ln5c75dpdd5ftokek3na&i=r2wuehmimnvxldg65vxkg5yovu&h=riversidefm.1password.com) (opens only with vault access). An agent never types it: a person unlocks the page once per host in the browser the agent is using.
  - The host the team hands out for these is **`marketing.riverside.com/dev/<path>`**, which resolves to `riverside.com/dev/<path>`. Because that is the production host, staging-host-only artifacts (the two 404s in Known Issues below) do **not** apply to a `/dev/` review - `/api/v4/pricing/plans` returns 200 there.
  - **The gate cookie is per-domain.** Unlocking `riverside.com` does not unlock `riversidefm-design-com-domain-staging.webflow.io`, and vice versa. Expect to re-enter the password when you switch hosts mid-review.
  - **Dropping the `/dev/` prefix does not reliably give you the same page un-gated.** `/dev/university-search` and `/university-search` were unrelated pages on 2026-08-09 - the un-prefixed one is a stale published page that redirects into the gate (see Known Issues). Verify the `<title>`/H1 matches the page you meant to open.

## Platforms & Tools
| Tool | Use | Owner |
|------|-----|-------|
| Website Development monday board | Page builds, fixes, tests, localization, accessibility | Marketing Website role (Jonathan Ydov from 2026-09-27) |
| Slack: `#website-dev` | Day-to-day website delivery discussion, including with Flow Ninja | Marketing Website role |
| Slack: `#marketing-website-monitoring` | Alerts and live-site monitoring | Marketing Ops |
| Groundcover | Synthetic checks on public site pages (404 monitoring on high-value pages); see Monitoring | DevOps owns the tool and grants access |
| PagerDuty | The "Marketing" service that receives the Groundcover site alerts, and its on-call shifts | IT grants access; responders were being added by Jonathan Galili (2026-05-11) |
| Ahrefs | SEO research and competitive intel | Erika / SEO function |
| Google Search Console | Indexing and organic performance | Erika / SEO function |
| Convert Experiences | Website A/B + split-URL testing. Used **department-wide**, not just Growth (e.g. homepage tests). Installed via site head custom code; several failure modes are silent - see `systems/owned/convert-experiences.md` before debugging a test that "isn't firing" | Marketing Operations (platform admin; Jonathan Galili, 2026-09-23); tests run by teams across the department |
| CMS / repo | Page authoring and deployment path | Knowledge gap: capture before automating page changes |
| Webflow MCP (v2.0) | Direct API access to the site: CMS collections/items, pages (create, settings, JSON-LD schema markup), elements/components/styles/variables, assets (folders + webp/avif compression), forms + submissions, custom fonts, sitemap indexing (`includeInSitemap` per page/item), site + page custom code, localization content writes (secondary locales), branch management, and read-only site analytics (Analyze reports). Since MCP 2.0 (2026-07-21) most operations no longer need an open Designer session or the Bridge app; workspace permissions are enforced and every agent action is audit-logged. Writes are gated per the repo safety rule. See the locale-publish caveat in the next row. | Marketing Website role |
| Webflow Designer (CMS collections) | Localized CMS item authoring; per-locale publish staging. The API/MCP still has no "queue for next site publish" action, cannot stage a single locale for the next publish, and misses some Designer-only items (not returned by the API locale query) - so locale publish queuing is done via the Designer UI (Claude in Chrome) - see `webflow-locale-publish-queue`. Designer URL (staging): `https://riversidefm-design-com-domain-staging.design.webflow.com/?workflow=cms` | Marketing Website role; SEO team for localized SEO pages |

## Vendor Contract & Billing (Webflow, Inc.)

Contract terms, payment terms, and AP/invoicing contacts for Webflow as a paid vendor now live in `systems/reference/webflow-vendor.md` (volatile finance/vendor data, not website-system behavior).

## Webflow site IDs

Two sites exist in the workspace - never assume which one a request means. Resolve with
`data_sites_tool > list_sites` if in doubt.

| Site | Site ID | Domain(s) |
|------|---------|-----------|
| **Riverside.com** (the marketing site - default target for website/SEO/asset work) | `685be7dcd32275d3830651d3` | `marketing.riverside.com`; staging short name `riversidefm-design-com-domain-staging` |
| Riverside Careers | `67684da2e173c24cb8897649` | `careers.riverside.com`, `careers.riverside.fm` |

## CDN and edge routing (as of 2026-09-15)

riverside.com is **mid-migration from Cloudflare to AWS CloudFront** (Linear project
*Cloudflare - CDN Migration: Cloudflare to AWS CloudFront & WAF*, DevOps team). What is live
today is the hybrid state, and it splits by path:

| Path | Served by | How to tell |
|------|-----------|-------------|
| Marketing pages (`/`, `/pricing`, `/blog`, and anything unmatched) | CloudFront -> Cloudflare -> Webflow | Response carries `cf-ray` and `server: cloudflare` |
| Web app (`/login`, `/dashboard`, `/api/*`) | CloudFront -> Istio, bypassing Cloudflare entirely | Response carries `server: istio-envoy` and **no** `cf-ray` |

- **The apex is DNS-only.** `riverside.com` A records are CloudFront (Amazon-owned
  `13.224.245.x`). DNS is hosted on Cloudflare nameservers but the apex is not proxied, so
  Cloudflare answers `530` for `Host: riverside.com`.
- **Cloudflare serves the marketing origin as `marketing.riverside.com`** (`104.18.x.x`).
  CloudFront calls it with that Host and `User-Agent: Amazon CloudFront`.
- **That host 301s to `riverside.com` for browser user-agents** but serves content for
  `Amazon CloudFront`. A bare `curl` against the Cloudflare IP therefore looks like a redirect
  and tells you nothing; add `-A "Amazon CloudFront"` to see what CloudFront sees.
- **Verify the layer, never infer it from headers alone.** `https://riverside.com/cdn-cgi/trace`
  is answered by Cloudflare and reports who *it* received the request from (`uag=Amazon
  CloudFront`, and an AWS client IP). Reading `server:` alone is misleading, because CloudFront
  passes the origin's header through.
- **Unmatched paths fall through to Webflow and return a Webflow 404.** Any new path that must
  not hit Webflow needs its own CloudFront behavior.
- **`/new/*` does not go to Webflow: CloudFront routes it to a Lovable campaigns app.** Announced
  by DevOps in `#marketing-dev` on 2026-07-16 and verified live on 2026-09-23 (`/new/ai-avatars`
  serves a Lovable build: `/__l5e/` asset paths and Lovable-hosted images, no Webflow markup). A
  campaign page goes live at `riverside.com/new/<campaign-name>` by adding the route in that one
  Lovable project and publishing it, with no DevOps change. Only that single Lovable project is
  wired, and a Webflow page given a `/new/` slug would never be served.

## Monitoring (as of 2026-09-23)

- **Groundcover synthetics watch the high-value public pages.** DevOps (Avital Siani) set up 404
  checks on key riverside.com pages (home, pricing, business, blog, legal and others) and routed
  them to a **PagerDuty "Marketing" service**, announced in `#marketing-dev` on 2026-05-11. How
  to view the checks and create new ones: the Confluence guide *Monitor public site pages -
  Synthetics Groundcover*
  (<https://riversidefm.atlassian.net/wiki/spaces/EN/pages/1895071747/Monitor+public+site+pages+-+Synthetics+Groundcover>).
- **Whether alerts reach a person depends on the PagerDuty responders.** At the announcement,
  on-call responders still had to be added (Jonathan Galili was on it). The current rotation is
  not recorded here, so confirm it before assuming an outage will page anyone. The Web Developer
  needs PagerDuty (IT grants it) and Groundcover (DevOps grants it) to be on it.
- **Slack stays the human channel.** `#marketing-website-monitoring` is still where live-site
  issues are discussed. Whether Groundcover also posts there is not recorded.
- **A new high-value page should get a check.** Adding one is self-serve per the Confluence
  guide; it is the cheapest way to hear about a broken page before a requester does.

## Site tracking / custom code (as of 2026-07-27)

All of riverside.com's tracking lives in **freeform head/footer custom-code blocks**, not
in Webflow's registered-scripts system. Consequences when auditing tracking:

- **`get_site_scripts` returns 404 `"Custom code block not found"`, and
  `get_registered_scripts` returns an empty list.** Neither is a fault - as of the date
  above there were zero registered scripts. Read `data_scripts_tool >
  get_site_freeform_code` (and `get_page_freeform_code` per page) for where the tags
  actually are. **Still call `get_registered_scripts` on each audit** rather than
  assuming the zero holds: the moment anyone registers a script, a freeform-only read
  would miss it silently.
- **Block sizes:** ~18.3K chars in head (14 `<script>` tags), ~33.2K in footer (14 tags),
  ~51.5K total. Too large to read into context - inventory with a grep/script.
- **Vendors present site-wide:** Convert Experiences (A/B testing), HubSpot, and the
  Meta/Facebook pixel in head; session recording (Hotjar/Clarity-class) in footer.
  Convert's own behavior - how to debug a test from the page, how audience rules are
  evaluated, and the failure modes that fail *silently* - is in
  `systems/owned/convert-experiences.md`. Load it before diagnosing any A/B test that
  "isn't firing"; several of its failure modes are indistinguishable from low traffic.
- **There is a hard ordering dependency in `<head>`.** The first script preserves the
  original referrer and UTM params into `sessionStorage` with a 30-minute TTL, and its
  own comment states it must run **before** the language-redirect logic and the Convert
  Experiences script - either can navigate away and wipe `document.referrer`. Page-level
  head code inserted ahead of it silently breaks attribution on that page.
- **Writes replace the entire block.** `set_site_freeform_code` /
  `set_page_freeform_code` overwrite the whole head or footer block, so a partial write
  silently drops every other tag in it. Read → modify → write the full content, and treat
  it as a high-blast-radius change. Migration to registered scripts is not a workaround:
  `register_inline_script` caps at 2,000 chars.

Consumed by `marketing-website-page-qa` ("Verifying tracking"), which previously deferred
the whole tracking check to Growth/Data.

### Google tags: two containers, loaded by Segment (as of 2026-09-15)

- **Two GTM containers, one per surface.** Marketing `GTM-PHP5JPNS`, web app `GTM-NDH4PM5`.
  Both register the same GA4 property (`G-PF9PK8DC9Z`) and the same five Google Ads conversion
  IDs (`AW-362810309`, `AW-362439714`, `AW-363139307`, `AW-618455135`, `AW-10903690226`). They
  never appear together today, and must not: a page loading both would report every conversion
  twice.
- **Segment loads the container, not the page.** It is injected at runtime by Segment's Google
  Tag Manager destination (v2.5.3), so `googletagmanager.com` appears nowhere in page source and
  a static grep of the HTML finds nothing. Execute the page and read
  `window.google_tag_manager` instead. Each surface is a separate Segment source.
- **That destination also feeds the data layer.** It pushes Segment Page and custom events into
  `dataLayer`, and many GTM triggers on both the marketing site and the web app depend on those
  events. Disabling it breaks them.
- **The container load can be repointed to a first-party path** via the destination's
  `fullURLpath` option, surfaced in the Segment UI as a custom domain field. The template is
  `//{{fullURLpath}}?id={{containerId}}&l=dataLayer`, concatenated with no separator, so the
  value must be host **and** full path with a trailing slash (`riverside.com/rs-measure/`). A
  bare domain produces `//riverside.com?id=...`, which silently keeps loading from Google. Empty
  falls back to `www.googletagmanager.com`.
- **A Segment settings payload only returns keys that have values.**
  `https://cdn.segment.com/v1/projects/<writeKey>/settings` omits unset options entirely, so an
  option missing there is not evidence it does not exist. Read the shipped integration bundle
  (`https://cdn.segment.com/next-integrations/integrations/<name>/<version>/...`) before
  concluding a setting is unavailable. This one cost a wrong answer on 2026-09-15.

### Login status on marketing pages: the plans API (as of 2026-09-29)

Marketing pages tell a logged-in visitor from a logged-out one by calling the app's payments
service at `/api/v4/pricing/plans` from the browser. It is the same host, so the app's session
cookie rides along. The site-wide head script already makes this call on every page, to decide
whether to show the Google One Tap sign-in prompt.

| Visitor | Response | `plan.priceId` |
|---|---|---|
| Logged out | `{"plan":{"currency":"usd","countryCode":"IL"}}` | absent |
| Logged in, Free plan | adds `priceId`, `isEnterprise`, `isTrialing`, `hasAlreadyUsedTheFreeTrial`, `language` | `""` |
| Logged in, paid plan | not captured yet | expected to be a real price ID |

- **Test for the key, never its value.** A Free user's `priceId` is an empty string, which is
  falsy, so `if (!data.plan.priceId)` treats every Free user as logged out. The site-wide script
  gets this right with `typeof data.plan.priceId === 'undefined'`.
- **It is a display signal, not access control.** It runs in the visitor's browser and returns
  no user ID or email. Use it to choose what to render. It cannot protect anything that is
  already in the page HTML.
- **`countryCode` comes back for logged-out visitors too.** It looks location-based (two
  anonymous calls from Israel both returned `IL`); the source is not confirmed.
- **It only answers on riverside.com hosts.** It returns 404 on the Webflow staging domain (see
  Known Issues), where every visitor therefore looks logged out. Test login-dependent behaviour
  on `stg.riverside.com` (VPN) or on a `/dev/` page on `marketing.riverside.com`.
- **`/pricing/switch` always redirects to `/pricing`.** Its page head code (`redirectUser()`)
  calls this API, but the logged-in branch is commented out ("Always redirect for now"), so every
  visitor lands on `/pricing` whatever their login state. Same code in the Designer and on the
  published page, checked 2026-09-29.

Evidence: the logged-out response is from an anonymous call on 2026-09-29; the Free response was
captured by Jonathan Galili from a logged-in Free account on 2026-09-29.

## Redirects (as of 2026-09-29)

Server-side redirects for the marketing site are **Webflow 301s** on the Riverside.com site
(`685be7dcd32275d3830651d3`): Designer > Site settings > Publishing > 301 redirects. On
2026-09-29 the list held **1,482 rules**.

- **Read and write them through the MCP.** `data_enterprise_tool` exposes
  `list_301_redirects` (paginated, 100 per page), `create_301_redirect`,
  `update_301_redirect` and `delete_301_redirect`. It only works because the workspace is
  on Enterprise. Any create, update or delete is a mutating call: confirm first, and
  publishing the site to make it take effect stays human-only.
- **Most of the list is wildcard cleanup, not page moves.** Rules like
  `/blog/(.*)?ba130cef_page=2` to `/blog/%1` strip Webflow collection-pagination query
  strings off `/blog/`, `/university/`, `/authors/`, `/category/` and root paths. Check
  whether an existing pattern already covers a path before adding a new rule.
- **Slug changes need a 301, never a 302.** The localization SOP enforces this for published
  pages (`systems/owned/localization-workflow.md`, step 10). `/webflow-link-checker` finds
  redirect chains, including the recurring DE `/de/de-*` one.
- **Not every redirect is a Webflow 301.** Three other layers redirect and are invisible
  from this list:
  - **CloudFront edge routing** (DevOps): `/new/*` goes to the Lovable campaigns app and the
    web-app paths go to Istio (see CDN and edge routing above). A Webflow 301 cannot change
    those paths.
  - **Client-side JS**: the EN to DE language redirect in the global head script, and stray
    page-level redirects like the `/university-search` one in Known Issues. An HTTP-level
    check reports these pages as 200; only a real browser sees them.
  - **The `marketing.riverside.com` origin** 301s browser user-agents to `riverside.com`.
    That is routing, not a content redirect.

## Cookie consent (as of 2026-09-29)

The consent banner is **CookieHub**. Its config (regions, categories, banner design,
integrations) lives in the **CookieHub dashboard**, not in Webflow; Webflow only holds the
loader. Who holds the dashboard login is not yet captured here.

- **The loader is in the site footer freeform block.** On `DOMContentLoaded` it injects
  `https://cdn.cookiehub.eu/c2/926fc84f.js` and calls `window.cookiehub.load()`. It is not a
  registered script, so `get_registered_scripts` will not show it.
- **Behavior differs by region** (read from the live CookieHub config):

  | Region | Framework | Banner actions | Default for non-necessary categories |
  |--------|-----------|----------------|---------------------------------------|
  | EU | default, explicit consent | Settings, Deny, Allow | Off until the visitor opts in |
  | California (`US-CA`) | CCPA | Notice | On, with opt-out |
  | Everywhere else | default, implicit consent | Settings, Allow | On |

- **Categories:** necessary, preferences, analytics, marketing, uncategorized.
- **Google Consent Mode is on, in advanced mode** (`dataLayer`, 700 ms delay). In advanced
  mode Google tags load before consent and send cookieless pings until the visitor chooses,
  so a pre-consent Google request is expected, not a leak.
- **CookieHub's script blocker is enabled; IAB TCF v2 is off; the HubSpot integration is
  off.** The "Learn more" link points to `riverside.com/cookies`.
- **Load order is an open question.** Convert Experiences is hard-coded in `<head>` and runs
  before CookieHub loads in the footer, so CookieHub cannot have blocked it on first page
  load. Whether that is intended (for example, classed as necessary) is not confirmed. Check
  with a real browser from an EU location before assuming EU visitors are fully gated.
- **Leftover CSS for HubSpot's own cookie banner** (`#hs-eu-cookie-confirmation`) is still in
  the head block. It is likely a remnant of an earlier setup; when auditing, confirm HubSpot's
  banner is disabled in HubSpot so EU visitors never see two banners.
- **Changes are Marketing Ops work.** Consent categories, new vendors and banner changes go
  on MOPs Tasks (`6257866754`) via `/pm-story` (routing per `/ticket-hygiene`).

## Design system sources (Figma)

Two distinct Figma libraries exist and they are not interchangeable. The repo previously named the marketing one in prose without a file key, so no agent could open it.

| Library | File key | Scope |
|---|---|---|
| **[Website] Marketing Web Design System_2026** | `mUETeqhnd2kbixWXcuTUsq` | The marketing website - page layouts and web components. Pages: `2615:26548` Web Layouts [New], `22:5844` Web Elements & components. Published team library; components maintained through 2026-02. This is the one to use for marketing-site and LP work. |
| 📖 Riverside Design System | `wXQnl6mSANal8DCbMssQkO` | The in-app **product** UI. Extracted locally to `references/design-system/`. Do not use for marketing pages. |

Access notes, all verified 2026-09-15:

- **`get_metadata` on a page-level node fails.** Both libraries' component pages exceed the MCP transport limit and die mid-stream with a JSON parse error (~44KB on `22:5844`). Query with `search_design_system` scoped by `includeLibraryKeys` instead - it returns structured results with `componentKey`s and never loads the file.
- The marketing library key is `lk-9c988df9a57947174c7bdebce04216714aaeaacd7f698d5cb91738be6bef94b8cf10516c5b34794ac70d9eaadd169848a9f5e31e4037cfbb820e4f6fa2212011`.
- **`search_design_system` batches are clamped to one query per call.** A 5-entry `queries` array returns 1 result with a warning that 4 were dropped. Issue discovery searches one term at a time.
- **Code Connect is unavailable** - it requires a Dev or Full seat on an Organization/Enterprise plan and returns a seat error. The Figma-component-to-Webflow-component mapping therefore cannot be generated and must be maintained by hand in this repo.

### Figma vs Webflow: which wins

**General rule: the Figma marketing design system wins** (Jonathan Galili, 2026-09-15). `[Website] Marketing Web Design System_2026` is the design authority for marketing pages.

- **Existing pages may not match it, and that is expected.** Do not retrofit a live page to the library just because they differ.
- **Close the gap on new pages.** Anything newly built should follow the Figma library.
- **A genuinely new conflict is a decision, not a judgement call.** When a new case arises where the library and the site disagree, raise it and let it be decided per case. Do not silently pick a side.
- **The footer is the standing exception**, decided above.
- This whole question is expected to be resolved by the **Marketing website rebuild**; the per-case rule is the interim position, not the end state.

## Webflow MCP: Building Pages via the Data API

Building or recreating a page (e.g. from a Figma spec) with the Webflow MCP's headless Data API tools (`data_element_builder`, `data_element_tool`, `data_style_tool`, `data_assets_tool`) has several non-obvious failure modes. All were hit building a pixel-perfect page from a Figma dev-mode handoff:

- **`TextBlock` silently drops its text.** `data_element_builder`'s `TextBlock` element type creates a plain, non-text-capable `<div>` - the `set_text` field is ignored at creation, and Webflow's own placeholder copy ("This is some text inside of a div block.") sticks permanently (a later `data_element_tool > set_text` call on it also fails with "This element doesn't support text"). Use `Paragraph`, `Button`, or `TextLink` instead - all three reliably accept `set_text` both at creation and after. Always verify with `get_all_elements` (checking the actual `String` child `textContent`) after a build call reports "success" - a successful build response does not guarantee the text landed.
- **Native `Button`/`TextLink` elements carry Webflow's built-in default styling underneath your custom class** - a default blue `.w-button` fill, a default `<a>` underline. Any CSS property your custom class doesn't explicitly declare (e.g. `background-color`, `text-decoration`) falls through to that default and *will* render, even though it looks like it should just be transparent/unstyled. Explicitly set `background-color: transparent` and `text-decoration: none` on custom link/button classes even when it seems redundant.
- **Asset uploads: the headless flow works. This entry used to say it did not - that was wrong.** Re-tested 2026-09-16: `data_assets_tool`'s `create_asset` → presigned S3 upload returns 201 with the correct ETag, `get_asset` then returns the asset, and the CDN serves the bytes. No Designer session is needed. The live-Designer bridge (`asset_tool > upload_image_by_url`, via `https://<site-shortname>.design.webflow.com?app=<token>` kept foregrounded) still works and remains the fallback if a headless upload ever fails to register - but verify with `get_asset` before reaching for it rather than assuming the headless path is broken. **Better still, do not upload at all when the asset already exists**: a section copied from another page should reuse that page's `assetId` via `data_element_tool > set_image_asset`.
- **Renaming an asset does NOT change its public URL - so renaming has no SEO value.** Webflow freezes the hosted filename at upload. Measured 2026-07-27 over a 200-asset sample: 49 assets had been renamed and every one still served its original upload filename (e.g. displayName `logo MCP TIM FERRISS.svg` → hostedUrl `.../Vector%20(20).svg`; `HP Hero Test_Desktop_2026_05 Final.avif` → `.../DSCF3865%201%20(2).avif`). Treat `display_name` as panel findability only. Also note `update_asset`'s `display_name` does **not** preserve the extension automatically - include it or the asset ends up extensionless. Alt text is where the real value is, and `alt_text: null` clears it and marks the asset decorative.
- **Asset-library scale: ~5,642 assets (57 pages at the 100/page max) as of 2026-07-27**, each page ~110-130KB of JSON. Listing pages into context does not fit - classify via `.claude/skills/webflow-asset-audit/scripts/classify_assets.py` instead. Baseline hygiene from that audit: **~58% of assets have no alt text** (52% newest page, 64% mid-library); the dominant junk-name patterns are Figma exports (`Frame 67296873`, `Group 596477`, `Button Text`), versioned duplicates (`… (1) 1 (6).avif`, 25% of sampled assets), and meaningless stubs (`dsadw.webp`, `ff23.webp`). Upstream's assumed patterns (`IMG_`, `screenshot`, `untitled` in display names) scored **zero** - camera names like `DSCF3865` survive only in the frozen URLs of already-renamed assets.
- **MCP 2.0.1 added native server-side image compression, which bypasses the broken upload path.** `data_assets_tool > compress_assets` (jpg/jpeg/png/webp → webp or avif) runs as an async task polled via `get_compression_task`; no client-side S3 upload is involved, so the failure mode above does not apply. **It is destructive:** it replaces each asset's hosted file in place (same asset ID, new hostedUrl/size) and does not retain the original - confirm before ever calling it. One pending task per site; svg fails with 400. This unblocks the compression use case that `webflow/webflow-skills`' `webflow-compress-cms-image` skill needed, though ~56% of recently-added assets are already avif.
- **Figma-exported images can be SVGs mislabeled with a `.png` URL/extension.** Check the actual file type (e.g. `file` command) before uploading - content-type mismatches cause silent upload failures. Fix the extension and re-upload with the correct `Content-Type`.
- **Figma asset/screenshot URLs expire (roughly a week) - download promptly**, don't leave them for a later pass. When embedding SVG markup directly (HTML Embed) rather than uploading as an asset: there's no hard size ceiling enforced by `set_settings` (a 20KB SVG can go through), but Designer's HTML Embed editor UI has a practical ~10K-character limit for a human to safely hand-edit or re-save without truncation. Strip Figma's export cruft before embedding - full-canvas backing `<rect>`s, page-fill paths (e.g. `#F4F1FD`/`#F3F5F7`), and dashed component-boundary rects (`stroke="#9747FF"`) - and export the actual artwork node, not its parent frame (frame exports pad the viewBox and shrink the visible artwork). If scripting the cleanup, match on `\sd="` not bare `d="` - an element's `id="X"` attribute can contain `d="X"` as a substring and false-match a naive regex.
- **Copying Figma's absolute x/y/width/height onto a fixed-width canvas is not responsive.** A literal pixel-for-pixel port (fixed 1440px canvas, `position: absolute` children) looks correct only at exactly that viewport width and breaks everywhere else (drifts left on wider screens, overflows/clips on narrower ones). Translate the Figma layout into flexbox (`gap`, `flex-wrap`, `max-width` + `margin: 0 auto`) instead - use Figma's absolute coordinates to inform spacing/sizing values, not as literal CSS positioning.
- **For repeating structured content (testimonials, cards, etc.), check whether a reference or sibling site already models the intended structure before hand-authoring static divs.** A reference build for this same page used a genuine CMS Collection List instead of one hand-built div per card - more maintainable, and it sidesteps several of the bugs above for free (e.g. rich text with embedded `<strong>` handles bold/regular runs natively, no manual text-splitting needed). Hand-authored static content should be a fallback, not the default, for anything that repeats.
- **Style only through `data_style_tool`, never a raw `css` param.** WHTML/element-builder `css` values land in Designer's "Custom properties" panel, not the native style controls - they don't behave like a real class and won't show up where a human editor would look. Bind a Webflow variable (color, spacing token, etc.) with `variable_as_value: "<variable_id>"` from `data_variable_tool`, not a raw `var(--token-name)` string - the raw string doesn't render as the native variable pill and can silently fail to update when the variable changes.
- **A class must exist before anything references it.** `data_style_tool > create_style` has to run first; naming a class in an element's class list (or in WHTML) before it's been created gets silently dropped - the element ends up unstyled with no error. Create every class up front, verify with `get_all_elements`/`get_settings`, then attach.
- **Webflow's native Navbar component cannot be built via the Data API or WHTML.** There's no API path to the built-in Navbar element. Build a semantic custom nav instead (a checkbox + sibling-selector CSS-only pattern for the mobile toggle - JS-driven toggles aren't supported this way), or tell the user to add the native Navbar manually in Designer.
- **Rendered CSS class names do not map to Webflow component names - never infer the component from the HTML.** The `Performance Footer` component renders with classes `c-section-tiny-footer` / `c-tiny-footer-block` / `c-tiny-footer-left`; nothing in the markup says "Performance Footer", and a `style: "tiny-footer"` element query against the page returns **zero** matches even though those exact classes are in the served HTML. Reading `/home`'s markup suggests a "tiny footer"; the page actually instances `Performance Footer`. Resolve the component with `data_element_tool > query_elements` using a `component_filter`, and treat any class-name-based identification as a guess.
- **Verifying a build has real blind spots - don't over-claim "confirmed."** `get_screenshot`-style snapshots are desktop-viewport only and don't execute embeds, WebGL, or `backdrop-filter` (transparent regions render solid black in isolation). The published `*.webflow.io` domain is robots-blocked, so the agent can never fetch and self-verify the live site either. For anything involving embeds, custom code, blur effects, WebGL, or mobile widths, explicitly ask the user to confirm rather than reporting it as verified.

### Publishing safely

> **Agents do not publish. A human does.** Standing safeguard set by Jonathan Galili on 2026-09-15, replacing the weaker confirmation-word rule it supersedes. No agent, skill, or routine may call `data_sites_tool > publish_site`, `data_cms_tool > publish_collection_items`, or `data_pages_tool > publish_branch` - not with approval, not on the word "publish", not to a staging domain, not for a single page. Prepare the change, verify it, then hand a person the exact publish to perform. This is deliberately temporary and may be relaxed later; until this paragraph says otherwise, treat it as absolute.

- **What the handoff must contain.** The site and page, what changed, what was verified and what was not, whether CMS items are involved, and the exact publish the human should run - full site, single page, or collection items - with the target domains named. State plainly that publishing is theirs to do.
- **Single-page publishing exists. The old "all-or-nothing" rule is retired** (corrected 2026-09-15; the prior text here claimed `publish_site` had no single-page path, and that was stale). `publish_site` accepts an optional `pageId`; when supplied only that page publishes. Live constraints: it requires an Enterprise site with single-page publishing enabled, and at least one prior full-site publish on the main branch, and **a single-page publish does not publish CMS items**. For riverside.com the evidence says it is available, though it was not confirmed by publishing, per the rule above:
  - `list_branches` fails with `branch_sync_pending` (503), a branch-feature error rather than a plan denial - branch actions require an Enterprise workspace, so the feature is reachable.
  - The custom domain's `fullSiteCompiledAt` (2026-09-10) lags its `lastPublished` (2026-09-15). Publishes happening without a full-site compile is what selective publishing looks like.
  - `fullSiteCompiledAt` is set, so the "at least one prior full-site publish" precondition is already met.
  This also removes the reason `webflow-locale-publish-queue` was described here as working around a site-wide-only limitation; that skill still exists for locale staging, which is a different gap.
- **`customDomains`**: the previous note said omitting it errors. The current MCP schema declares `default: []`, so that claim may be stale. Untestable under the human-only rule - tell the human to pass `[]` explicitly and it is correct either way.
- **Diff before the handoff.** Compare `lastUpdated` against `lastPublished`, and check for CMS items sitting in Draft, so the human is told exactly what will go live rather than discovering it after.
- **Coordinate a production publish with every developer working on Webflow first.** A full-site publish ships everyone's in-progress work, so the handoff should say whether Flow Ninja and anyone else with work in the site have confirmed it is safe in `#website-dev` (see Working with Flow Ninja). Staging publishes need no such check.

### CMS Collection Lists (dynamic, bound to a collection)

Binding a page element to live CMS data uses a different tool than building static structure - `data_element_settings_tool` (`get_settings` / `set_settings` / `get_bindable_sources`), not `data_element_builder`'s `set_text`/`set_image_asset`. Confirmed working end-to-end:

- Create the element with `type: "CMSCollection"` via `data_element_builder` - it auto-generates the whole skeleton: `DynamoWrapper > DynamoList > DynamoItem` (plus a `DynamoEmpty` "No items found" fallback). Build the repeating card's markup as children of the `DynamoItem`.
- **Bind the whole list to a collection**: `set_settings` on the `DynamoWrapper` with `key: "source"` and a `binding: {source_type: "cms", collection_id, field_id}`. Counterintuitively, `field_id` is required by the schema even though you're selecting the *collection*, not a field - any field ID belonging to that collection works. Confirm it took via `get_settings` (`all_raw_settings`) - `source` should read back as `{"collectionId": "..."}`, not `null`.
- **Bind individual descendant elements to specific fields** the same way, but the setting `key` differs by element type and isn't guessable - always discover it first with `get_settings` (`all_raw_settings`) on a plain (unbound) instance of that element type: a `Paragraph`'s text lives under key `"text"`, an `Image`'s asset under `"assetId"`, a `RichText`'s content under `"richText"` (not `"textContent"`). Once bound, `get_bindable_sources` on any descendant inside the `DynamoItem` lists every field of the bound collection as available sources - a good sanity check that the collection-level binding above actually worked.
- **CMS `Image` field writes need both `fileId` and `url`.** `create_collection_items` 400s with "Expected value to have a 'url' field" if you pass `{"fileId": "<assetId>"}` alone - pass `{"fileId": "<assetId>", "url": "<hostedUrl>"}` (the `hostedUrl` returned when the asset was uploaded).
- **Publish the site before publishing collection items.** `data_cms_tool > publish_collection_items` 409s with "site is not published" if the site has never been published. Publish the site first (even once), then publish items.
- **Wrapper divs need explicit layout overrides to match a custom (non-swiper) design.** The auto-generated `DynamoWrapper`/`DynamoList` are extra nesting levels not present in a static mockup - give the wrapper `display: contents` and the list `display: flex` (with whatever `gap`/`flex-wrap` the card row needs) so they don't disrupt an existing flex layout.
- **Collection limits to check before modeling data:** max **5 multi-reference fields per collection**; a multi-reference Collection List can only filter by one referenced value at a time and can't sort by a referenced field's value. Displaying more than the first referenced item requires a **nested Collection List** - binding straight to a multi-reference field only ever shows the first item. Plan-tier item caps also gate what a design can assume: Starter 1 collection / 50 items, Basic 2 / 200, CMS 20 / 2,000, Business 40 / 10,000 - confirm the site's plan before designing around "unlimited" CMS growth.
- **When looking up a specific CMS item, filter `list_collection_items` by `name`/`slug` rather than fetching everything and searching client-side** - cheaper and avoids pagination bugs on large collections. Batch CMS writes at ~50 items per call generally, ~20 for image-heavy items.

### Mapping live URLs back to Webflow page/item names (locale-aware)

Given a list of live riverside.com URLs (e.g. an SEO/localization audit sheet) and asked for each one's Webflow "name", the reliable path:

- **Match on `publishedPath`, not the slug.** `data_pages_tool > list_pages` with a `localeId` returns each page's localized `publishedPath` (e.g. `/de/de-podcast-app`) - that is the exact key to match a live URL against (strip the domain + trailing slash). The page `title` is the internal Webflow name; the Name is shared across locales even though slug/SEO are localized, so you don't need to re-fetch it per locale.
- **`/tools/*` (and other feature) URLs are usually CMS items, not static pages.** They're rendered by a collection template page, so they won't appear in `list_pages`. Resolve them via `data_cms_tool > list_collection_items` filtered by `slug` + `cmsLocaleId` on the **Tools** collection (`685be7dcd32275d383065738`); the item `name` (or `short-name`) is the Webflow name.
- **Localized slugs can differ from English - don't assume the EN slug in the other locale.** A DE item/page can live at a different slug than EN (real case: EN `/tools/podcast-maker` → DE `/de/tools/podcast-generator`, same CMS item id). A DE-locale lookup by the EN slug returns zero. When a locale match misses, retry against the primary (EN) locale by the EN slug (same item id resolves) and flag that the URL/slug in the source list is likely stale (this one 404'd live).
- **`list_pages` is paginated at 100** (`pagination.total` gives the count; page with `offset`) and its response is large enough to spill to a tool-results file as a single very long JSON line - slice it by character range in Python; `Read`'s offset/limit chunking fails on the long line.
- **riverside.com locale IDs:** DE page-locale `685be7dcd32275d383065236`, DE `cmsLocaleId` `685be7dcd32275d383065237`; primary (EN) page-locale `685be7dcd32275d38306522e`, `cmsLocaleId` `685be7dcd32275d38306522f`. Full locale set (fr/pt/es/de) is on the site object via `data_sites_tool > get_site`.

### Crawling the site: the sitemap is not the page list

`riverside.com/sitemap.xml` indexes two children, `sitemap-en.xml` (713 URLs) and
`sitemap-de.xml` (113), 826 in total. **Landing pages under `/lp/*` are in neither.**
Verified 2026-09-23: zero `/lp/` entries, while `/lp/business`, `/lp/webinars-lp`,
`/lp/riverside-vs-zoom-webinar` and `/lp/riverside-vs-goto-webinar` are all live and all
carry CTAs. A sitemap-driven crawl therefore reports clean on exactly the pages paid
campaigns point at.

Enumerate `/lp/*` from Webflow rather than the sitemap in any site-wide sweep -
`webflow-link-checker`, `webflow-asset-audit`, `webflow-accessibility-audit`, and any CTA or
tracking audit. Note also that `fr`/`es`/`pt` have no sitemap at all, though the site carries
locale machinery for them.

### Locale equivalence: read it off the page, never from a slug map

Every page carries its own `<link rel="alternate" hrefLang="en" href="...">`, translated ones
included. To map a localized URL to its canonical English section, read that tag instead of
maintaining a DE-to-EN slug table. Verified 2026-09-23 across all 66 DE pages carrying a
book-demo CTA: 100% coverage, `/de/unternehmen` to `/business`, `/de/preise` to `/pricing`,
`/de/blog/so-erstellst-du-einen-podcast` to `/blog/how-to-produce-a-podcast`.

This reuses the mechanism the site's own language redirect already depends on, so it fails
loudly rather than silently. That redirect, from the global head script:

- Locale comes from the **path prefix only** (`/^\/(de|es|fr|pt)(\/|$)/`). No prefix means `en`,
  so `/book-demo` renders the English form however the visitor got there.
- Preference is the `language` cookie, else `navigator.language` when that is `de`, which
  then sets the cookie for 365 days.
- A non-EN preference on an EN page redirects via that page's own hreflang alternate.
  `allowedLangs` is `['en','de']`; fr/es/pt are commented out.
- **The redirect preserves `location.search + location.hash`**, so query parameters survive
  the EN to DE hop.

> **The attribute is `hrefLang`, not `hreflang`.** A case-sensitive grep for `hreflang`
> returns nothing and reads as "this page has no alternates", which is wrong and on
> 2026-09-23 produced a confidently reported bug that did not exist. HTML attribute selectors
> are case-insensitive, so `querySelector('link[rel="alternate"][hreflang="en"]')` matches it
> fine. Only your grep does not.

## Key Pages
- Homepage / Home LP, including active or recent A/B tests
- Pricing and pricing-adjacent flows, including pricing quiz implications
- AI page, transcription page, editor page, marketers page
- Comparison pages and use-case pages
- Localized pages, especially DE paths where redirect issues have recurred
- Careers page, which has had navbar update issues
- Love & Labor landing pages and static assets from Q2 carryover
- `/book-demo` and `/de/buch-demo`: a HubSpot form plus a custom Chili Piper script, not a Webflow form. Five locale form ids, router `inbound-router`. Reads `meeting_*_cp` off its own URL; see `systems/owned/chilipiper.md`

### Paid (PPC) landing pages

Paid landing pages are a distinct class from the organic site and follow their own conventions:

- **They ship `noindex, nofollow`.** This applies to *all* Riverside PPC landing pages, and is the reason a paid variant can duplicate an existing organic page without competing with it in search. When QA'ing a paid page, check the directive is **present** rather than flagging its absence as an open question - a missing `robots` tag on a paid page is the finding.
- **A paid variant usually sits alongside its organic equivalent, not in place of it.** `/book-demo-new` (Business Owners, Meta campaign) was built as an additional variant while `/book-demo` stayed live. Do not assume a new page replaces the one it resembles; confirm on the ticket.
- Because they are excluded from search, the usual duplicate-content and canonical concerns do not apply between a paid variant and its organic counterpart.
- **The footer is the one place Webflow beats Figma.** Where the `[Website] Marketing Web Design System_2026` library and the built site disagree on a footer, build what Webflow already has. This is an explicit **exception** to the general precedence rule in "Figma vs Webflow: which wins" under Design system sources, not an example of it - do not generalise it to any other component (Jonathan Galili, Marketing Website owner, 2026-09-15).
- **`Performance Footer` is the default for every new PPC LP** (Jonathan Galili, 2026-09-15). A second footer is already in use on one older LP; it is an exception, not a choice to re-make per page. Verified 2026-09-15 by querying component instances, not by reading rendered markup:

| LP type | Component | Component ID | Notes |
|---|---|---|---|
| **Any PPC LP - the default** | **Performance Footer** | `b473f3ea-71c6-6b11-5430-acd8bfd5d2d7` | 36 instances site-wide; variants `Base` / `Small`. Verified on `/home` and `/lp/home`, both on `Base`. Use this unless the ticket says otherwise. |
| Demo-step LP (`/lp/watch-a-demo-1`) - the exception | **Small Footer** | `31b77736-8280-4225-9a06-74de55d2fb78` | 26 instances; no props or variants. Pre-existing; not a pattern to copy for new LPs. |

  `Small Footer` is a **separate component**, not the `Small` variant of `Performance Footer` - the name collision is real and was confirmed by querying both. Do not treat "the LP footer" as one thing.

**Clone source for a new PPC page: `https://riverside.com/home`** (Jonathan Galili, 2026-09-15). Webflow page id `69ca3c516830a7bb08862713`, internal name "Home SF - Home All In One". Build a new PPC LP by duplicating that page, not by assembling one from elements - cloning inherits the nav, footer, CTAs and tracking, and avoids most of the build failure modes above.

**Do not clone `/lp/home`.** It is a separate live page (id `69ba94df69e41d8eaf5456c7`, "Home All In One /lp/home") with the same title and the same `noindex, nofollow`. The two are easy to confuse and only `/home` is the source of record.

**Non-PPC page types have no defined clone source yet.** That mapping is open work; do not guess one. Ask the requestor which existing page a new non-PPC page should be based on.

### PPC landing-page component kit

Derived 2026-09-15 by querying component instances on the clone source `/home`. The kit is deliberately small: **nine instances, five distinct components.**

| Part | Webflow component | Component ID | On `/home` | Figma counterpart |
|---|---|---|---|---|
| Every CTA | **Main Button** | `27e28671-c8fc-53ae-693f-2af7ed6c5293` | x6 | `Button` component set (`61b03e68…`), plus the CTA taxonomy: Main Hero CTA, Desktop Main CTA + Disclaimer, Mobile Main CTA + disclaimer, Main + Secondary First Fold Desktop/Mobile |
| Page styles | **Global CSS** | `6333e517-5064-f717-b9ef-dc6da2b538f0` | x1 | none - implementation only |
| Social proof | **G2 Reviews - Text** | `e54d9bfa-1235-70a6-dd5f-d3edd2eb7a81` | x1 | not located |
| Footer | **Performance Footer** | `b473f3ea-71c6-6b11-5430-acd8bfd5d2d7` | x1 | none found - see below |
| Nav | *native Webflow Navbar* - **not a component** | n/a | x1 | `MAIN navbar` (`38c9df1a…`), `MAIN navbar (transparent)` (`4e223b15…`) |

**`Main Button` is the CTA interface the build process drives.** Props: `Variant`, `Link`, `Text`, `Button ID`, `Visibility`. Every instance on `/home` points at `https://riverside.com/start`.

**The nav can only be inherited, never rebuilt.** `/home`'s nav is a native Webflow Navbar (`w-nav` / `w-nav-brand` / `w-nav-menu`, custom class `c-updated-nav-desktop`) stripped to two links - logo to `/`, CTA to `/start`. It did not appear among the nine component instances because it is not a component. The Data API has no path to the native Navbar (see the build failure modes above), so **cloning `/home` is the only way to get a compliant LP nav.** Never try to build or replace it.

**Figma has no footer component, which is why Webflow is authoritative for the footer.** A component search for "footer" in the marketing library returns `MAIN navbar`, `MAIN navbar (transparent)` and `Comment Bubble` - no footer. The search is fuzzy, so treat this as strong evidence rather than proof; it means the footer exception recorded above is the only available answer, not a preference. The nav is the opposite case: Figma has a designed navbar, and Webflow implements it as a native element the API cannot touch.

**Five CTAs on `/home` share `id="hero-get-started"`.** Observed 2026-09-15 in the served HTML (`grep -c` returns exactly 5). Duplicate `id` values are invalid HTML and would collapse per-CTA attribution if that id is a tracking hook - **but this may be intentional and is being investigated separately.** Until that concludes: do not change it, do not de-duplicate it while cloning, and do not treat it as a bug to route around. If it needs handling in the build process, that will be requested as a change (Jonathan Galili, 2026-09-15). This note exists so the next agent or reviewer who notices it does not quietly "fix" it.

### Who writes the brief

**The task requestor owns the brief** (Jonathan Galili, 2026-09-15) - usually PMM, PPC, SEO, or Partnerships/Affiliates, and sometimes the Design Team directly when a design lands without a separate requestor. The brief is not the Marketing Website role's to write on their behalf.

A page-build agent has no input without a brief, so a missing one is a blocker to raise with the named requestor, not a gap to fill by inference. On 2026-09-15, 8 of 8 sampled Website Development tickets had no brief in either column.

**A brief and a Figma are a pair, and the Figma is the stronger input** (Jonathan
Galili, 2026-09-16). A ticket needs one of them, not always both:

| Brief | Figma | Startable |
|---|---|---|
| yes | yes | Yes - the normal case |
| no | yes | **Yes.** A Figma alone is enough; do not flag it as unready |
| yes | no | Only for a crystal-clear, simple text change (below) |
| no | no | No |

The brief-only case is narrow by design. It holds only when the request updates an
**existing** page, changes **text only** (no layout, new element, image, component
or CTA target), the element **already exists**, the replacement text is **stated
verbatim** rather than described, and exactly **one** element matches. If it is
arguable, it does not qualify - ask for the Figma. This is the same exception the
Definition-of-Ready matrix expresses by exempting copy swaps from its
"design-dependent" test.

**Two columns on the Website Development board are both titled "Brief", and only one was known to this repo until 2026-09-15.**

| Column | ID | Type |
|---|---|---|
| Brief | `link_mm05cxb3` | link |
| Brief | `doc_mm77q17p` | monday Doc - added later |

Either one holding a brief satisfies the requirement. Check **both** before reporting a brief missing: on 2026-09-15 the only real brief on the board sat in the doc column (ticket 13050711075), so a check against the link column alone would have called a genuinely ready ticket blocked. The doc column looks like the fix for briefs previously being parked wherever they fit - `marketing-website-page-qa` records one found squatting in the **QA Doc** column on ticket 12734037413. A brief in the doc column is the doc's content: resolve it with `read_docs` on the `objectId` in the column value.

## Known Issues / Failure Modes
| Issue | Symptoms | Resolution |
|-------|----------|------------|
| Cloudfront caching | Intermittent 404s on key pages (Q1 P0 carryover) | Investigation owned by Jonathan; check `#marketing-website-monitoring` and relevant monday item |
| Localization redirects (DE locale) | 301 chains breaking, /de/de-* duplicate paths returning 404 | Audit + cleanup, recurring Q1 issue; the localization SOP's production validation step (`systems/owned/localization-workflow.md`) requires a 301 whenever a slug changes on an already-published page, checked as part of every localization run |
| Careers page navbar | Not auto-updated when careers content changes | Capture exact CMS/deploy path before automating |
| Tracking risk on CRO changes | CTA, form, pricing quiz, or demo paths stop attributing correctly | Check HubSpot events, UTMs, ChiliPiper sync, and `page-cro` tracking requirements before launch |
| Language switcher requests `/undefined/en.json` | A **404 in console on every page load of the Webflow staging domain**. The switcher script builds the path from a variable that resolves to `undefined` there. | **Staging-domain only, as far as observed.** Reproduces on every `riversidefm-design-com-domain-staging.webflow.io` page; **not** reproduced on production - neither `riverside.com/university` nor `riverside.com/university/product-updates` requests it (checked 2026-08-06). Note the path *does* 404 if you fetch it on production, but nothing on production asks for it, so a 404 on that URL alone is not evidence of the bug. Not caused by whatever page you are reviewing - do not file it against a page QA. |
| `riverside.com/university-search` sends live visitors to a password gate | The published page runs a **client-side** redirect to `riverside.com/dev/university`, which returns 401 "Protected Page". Confirmed in-browser on production 2026-08-09 (referrer chain `/university-search` → `/dev/university`), not just as a string in the HTML. A server-side check misses it: `fetch()` with `redirect: "follow"` returns **200** at `/university-search`, because the redirect only fires when the page's JS runs. | **Reported 2026-08-09, under investigation** (Jonathan). Looks like a dev redirect left on a published page. When auditing for others like it, drive a real browser - an HTTP-level check will report the page healthy. |
| Webflow tabs component renders but never switches panes | Clicking a tab adds `w--current` to the tab **link**, but the pane keeps `display: none` and the previously active pane keeps `w--tab-active`. Looks like a broken tabs component; the markup is fine. | The Webflow tabs module never initialised on load. **Diagnostic:** run `Webflow.require('tabs').ready()` in the console, then click again - if it now switches, it is an init-order failure, not markup, and the fix belongs in whatever aborts init rather than in the component. Seen 2026-08-09 on both University video pages, correlating with an uncaught `TypeError: n[p] is not a function` during Webflow init. |
| A page-specific script loaded on a template that lacks its elements | An uncaught `TypeError: Cannot read properties of null` early in a page's inline script. Everything after that line in the same `<script>` block silently never runs. | Check whether the aborted block's target elements exist on the page **before** assigning severity. On 2026-08-09 the University search/listing script (613 lines: filters, pagination, clear-all, business switch, date formatting) was loaded on `/dev/university`, where **none** of its 13 target selectors exist - so the real impact was a console error and a wrong-script-loaded **P2**, not the functional **P0** it first appeared to be. Fix is a guard or removing it from that template. |
| `/api/v4/pricing/plans` 404s on the Webflow staging domain | Console shows a 404 plus a logged `Error loading API` from the site-level head script that fetches the user's plan. | **Staging-domain artifact only.** That API is served from the app domain, so it returns **200 on `riverside.com`** and 404 on `riversidefm-design-com-domain-staging.webflow.io` (confirmed 2026-08-06). Expected on staging; re-confirm during the post-live audit rather than reporting it as a page defect. |

## Related Systems
- **Upstream:** Design system, brand, content pipeline
- **Downstream:** HubSpot (form captures), Omni BI (web analytics), MOps automation (form routing)
- **A/B testing:** `systems/owned/convert-experiences.md` - Convert Experiences runs site-wide from this site's head code

## Pointers
- **Slack (primary):** `#website-dev` (`C0AM2HQMY49`)
- **Slack (monitoring):** `#marketing-website-monitoring` (`C05FK3G82H4`)
- **Slack (R&D/DevOps):** `#marketing-dev` (`C0AA8HABQKG`)
- **Slack (a11y):** `#website-accessibility` (`C0AE8HFK7R7`) is no longer used (2026-09-23); accessibility work is ticketed on the Website Development board
- **Monday board:** Website Development (`18397093471`)
- **Specialist skills:** `website-agent`, `page-cro`, `seo-ai-search-agent`, `content-agent`, `webflow-locale-publish-queue`, `webflow-build-agent`, `webflow-accessibility-audit`, `webflow-link-checker`, `webflow-asset-audit`
- **Localization SOP:** `systems/owned/localization-workflow.md`, full request-to-production process, RACI, and known-issue tracking for SEO page localization
- **External reference:** [`webflow/webflow-skills`](https://github.com/webflow/webflow-skills) - Webflow's own Agent Skills collection for the Webflow MCP (CMS management, site auditing, asset optimization, Code Components, University). Not vendored wholesale (pointers, not copies for the parts we don't use - the Code Components/CLI skills need a local Webflow dev project Riverside doesn't run); the MCP-compatible gotchas from its `figma-to-webflow`, `safe-publish`, and CMS skills were mined into this doc's build/publish/CMS sections above, and its `accessibility-audit`, `link-checker`, and `asset-audit` skills became `webflow-accessibility-audit`, `webflow-link-checker`, and `webflow-asset-audit` (see Specialist skills; asset-audit adopted 2026-07-27, re-fitted to metadata-only updates because of the headless-upload failure above, then corrected against a real 5,642-asset run - see the rename/URL and scale entries above). A 2026-07-27 re-review found the remaining candidates to be: `bulk-cms-update` (worth adopting if batch CMS edits become recurring), `custom-code-management` and `review-comments` (mine/fold rather than adopt), and `webflow-compress-cms-image` (**no longer blocked** - MCP 2.0.1's native `compress_assets` runs server-side, see above; adoptable if page-weight work becomes a priority, with a destructive-action gate). The 12 Code-Components/CLI skills, `site-activity` (Enterprise-only), `site-audit`, `flowkit-naming`, and the University onboarding skill remain not applicable.
- **Knowledge gaps to fill:** CMS/repo path, deployment process, SEO dashboard URLs, monitoring runbook (partly filled: see Monitoring; the PagerDuty rotation and alert routing are still open)

### Building sections: use the HTML builder, not the element builder

Two Webflow MCP tools can create elements. They are not equivalent, and the
obvious one is the wrong one.

`data_element_builder` takes a typed `element_schema`. It **silently discards
`styleNames` and `text`** - you get the right nesting with unstyled elements,
`h1` headings reading "Heading", and Lorem ipsum paragraphs. You then have to
re-apply everything through `data_element_tool` (`set_style`, `set_text`,
`set_heading_level`), and that path cannot express:

- **Grid elements.** `Grid` is not in the creatable type list at all.
- **Most combo classes.** `set_style` matches on the Webflow style *name*
  (spaces, original casing). Deep combos fail with "One or more styles not
  found" even when another page on the same site demonstrably uses that exact
  chain. `rs-button` + `is--purple 2` resolved; `max-width-fit 2 2`,
  `is--business-hero 2 2`, `btn-new-rounded` and `" Block-custom- 2"` all
  failed.

`data_whtml_builder` takes an `html` string and resolves classes by their
**hyphenated CSS form** - the same form Webflow exports. It applied all five
button classes and all three wrapper classes in one call, including the style
whose stored name begins with a space (`" Block-custom- 2"` ←
`class="block-custom--2"`). Name-to-selector is: lowercase, spaces become
hyphens (`is--solution-market-full-btn 2 2 2 2` → `.is--solution-market-full-btn-2-2-2-2`).

**Default to `data_whtml_builder` for anything with real styling.** Reach for
`data_element_builder` only for plain structural scaffolding you intend to style
afterwards.

Two related notes:

- `set_style` **does not create** missing styles - it errors. So a `set_style`
  that returns success did bind to the real site style; you do not need to
  re-verify that separately. (It is `create_style` that invents, and it requires
  a `properties` array, so creating a combo to satisfy a name produces a *blank*
  class that looks nothing like the original.)
- Batches of ~13 `set_style` actions time out partway, silently leaving the
  first N applied. Keep element-mutation batches to about 4 and re-read to
  confirm what landed.
- **`set_image_asset` is rate-limited harder than the other writes.** Binding 24
  checkbox icons in batches of four produced repeated timeouts and then a
  `GET /v2/assets 429`, which also breaks `query_elements` (it resolves assets on
  read). The writes still landed every time. Pace image binds, and expect a
  read-back to fail with 429 for a while after a burst - that is the limiter, not
  a lost write.

Two defects the HTML builder introduces that only show up on a rendered page.
Both were caught on the 2026-09-17 staging pass and both are cheap to fix once
you know to look:

- **A native Webflow element rebuilt as a plain div loses whatever Webflow's own
  base class supplied, and nothing in the read-back shows it.** This is the
  single most expensive trap in this whole surface, because the element tree
  looks correct and only the rendered page disagrees. Webflow splits styling
  between *your* class and a base class it attaches to the element **type**; the
  Data API cannot create those types, so the base class is what you lose:

  | Reference element type | Webflow base class | What it supplies |
  |---|---|---|
  | `Grid` | `.w-layout-grid` | `display: grid`, 16px row/column gap |
  | `Container` (reads as `BlockContainer`) | `.w-layout-blockcontainer`, `.w-contain` | auto left/right margins (the centring) |

  Your class still carries everything else - `grid-template-columns` including
  responsive tracks, `max-width` - which is why the failure is partial and easy
  to miss. A grid renders as one tall column; a container sits flush left while
  the rest of the page centres, **and only above its `max-width`**, so it looks
  fine at 1280 and wrong at 1600.
  Restore the missing properties in page custom code, reading the exact values
  off the reference page rather than guessing.
  Flex containers are unaffected: a `display: flex` class carries its own
  display, so a rebuilt flex row matches the reference exactly.
- **Check a rebuilt layout at more than one width.** The container bug is
  invisible at and below the container's own `max-width`. Compare geometry
  against the reference at a wide viewport (1600 works) as well as 1280 and
  mobile, or a whole class of centring defect ships unnoticed.
  **And re-assert the width every turn.** The in-app browser clears `resize_window`
  emulation when a turn ends, so a measurement taken later silently runs at the
  pane's own width (~1000px). `margin: auto` legitimately computes to `0px` below
  the element's `max-width`, so a working centring fix reads as broken. That cost
  two wrong "this did not publish" calls on 2026-09-17; both times the fix was
  live and the viewport was the bug.
- **Two kinds of write, two publish behaviours.** Verified 2026-09-17 with
  cache-busted fetches of both the page HTML and the site stylesheet:

  | Write | Reaches the live page without a publish? |
  |---|---|
  | Element structure, text, attributes, image assets | **Yes** |
  | Applying a class that already exists in the published stylesheet | **Yes** |
  | Creating a style, or changing a style's properties | **No** - needs a publish |

  A new class does not appear on the element in the served HTML *and* its rule is
  absent from the stylesheet until someone publishes, because publishing is what
  regenerates the stylesheet. So Webflow's backoffice reporting "nothing to
  publish" after a batch of element edits is correct, not a bug. Do not tell
  someone to republish on the strength of a rendered page looking stale - re-read
  it with the viewport set explicitly first, and check `get_page_metadata`'s
  `lastUpdated` against when you wrote.
- **The Designer reads the design state, not the published one.** A style change
  is visible in the canvas immediately, before any publish. That makes the
  Designer the place to check a style-level change, and the published page the
  place to check that nothing regressed.
- **An asset id on a reference page may belong to a different Webflow site.**
  `set_image_asset` returns "Asset not found" and `get_asset` returns "The site
  cannot be found". Riverside's live pages still reference icons from the old
  site (`61ae89c5da104e3746bf25c4`), so read the rendered `src` to see which site
  it is served from. Before uploading a replacement, call `create_asset` with the
  file's md5 - **Webflow dedupes by hash** and returns the existing asset record
  if this site already has the same bytes, which is how the play icon resolved
  without adding anything to a 5,600-asset library.
- **`data_whtml_builder` writes `href` twice: once as the link setting and once
  as a custom attribute.** Both hold the same value, and the element read shows
  them separately and both correct. It is redundant rather than broken - the
  served HTML is fine either way - but remove it as hygiene, because a later
  edit to the link setting will not touch the stale attribute: `get_attributes`
  the link, then `remove_attribute` the `href`.

### Component instances can be placed through the API

`data_component_tool > insert_component_instance` takes a `component_id`, a
`parent_element_id` and a `creation_position`, and drops a real instance onto a
page. This is the way to swap a clone's inherited native Navbar for the
`nav-basic-lp` component the acquisition LPs use - build the instance first,
confirm its props, then remove the old `NavbarWrapper`.

Read the returned prop list before assuming you need overrides. On the 2026-09-17
build every one of `nav-basic-lp`'s thirteen props already carried the same value
as the reference page's instance, with `hasOverride: false` throughout, so the
correct action was to set nothing.

### The HTML builder drops whitespace-only span content

Riverside's headings break lines with `<span class="is-line-break"> </span>` and
`is-line-break-mobile` - a span holding a **single space**. `data_whtml_builder`
creates the span but trims the space, and the element tree shows a span that
looks right. The rendered page then joins the words wherever that span is
`display: inline` at the current breakpoint: "Edit YouTube videos**without**
jumping", "Video editing,**without** the learning curve".

It hides well because `is-line-break` is `display: block` at desktop, so the
common case still breaks correctly and only the `-mobile` variant misbehaves -
until you check the other breakpoint, where the two swap.

Fix after building: `set_text` the span with `" "`, which does persist. Verify by
comparing the *rendered* `textContent` against the reference page, not the tree;
on the reference every one of these spans reads `" "`.

Related: `data_element_builder` + `set_text` cannot produce these spans at all,
since `set_text` replaces a heading's children with one string. A heading that
needs controlled line breaks has to be built as HTML.

### Prefer the style system over page custom code

`data_style_tool > update_style` takes a `style_name` and a `properties` array
(`property_name` / `property_value`), and **merges** - verified on
`.grid_3-cards`, which kept its `width`, `grid-template-columns`,
`grid-template-rows` and transitions while gaining three new properties. So a
write cannot silently wipe a class.

Anything expressible as a class's own properties belongs there, not in page
custom code, because a real style shows in the Style panel, renders in the
Designer canvas, travels with the section when it is copied, and costs nothing
against the page custom-code cap. Page custom code does none of that.

**Read the class before writing to it.** Two hazards, both hit on 2026-09-17:

- **Shorthand over longhand silently changes other pages.** `.home-hero__checkbox`
  already carried `border-*-width: 1px`, `border-*-color: rgba(255,255,255,.3)`
  and a 36px radius. Writing `border-width/style/color: 2px solid transparent`
  would have overridden all of it everywhere that class is used. The page needed
  the 2px transparent border; every other page needed the 1px one. That
  declaration stays page-scoped.
- **Most of what you are about to write may already be there.** Of the six
  declarations in that rule, four were byte-identical to the class. The relocated
  CSS was mostly re-stating the class to itself; only two lines were load-bearing.

So the rule is: put it on the base class when the class does not already define
it and every user of the class wants it; otherwise keep it page-scoped.

**Before writing to a shared class, find out who else uses it - and what the
class's real value is.** On 2026-09-17 writing `18px` to
`.home-hero__checkbox-icon-wrapper` silently changed it from its actual `15px`,
which `/lp/beehive` depends on for eight checkboxes. The relocated CSS said 18px
because the *reference page's embed overrode the class*; the class itself was
never 18px. Reverted.

Two techniques make this cheap:

- **Enumerate users by fetching published HTML and grepping for the class.**
  `list_pages` for the slugs, then fetch each published URL and match
  `class="[^"]*<class>"`. Scanning ~100 pages took two browser calls and found
  seven users of `.container-market-testimonials` and exactly two of
  `.grid_3-cards`. Note `/dev/**` and `/section-library/**` return 401 behind the
  shared password, so a scan is never complete - say so rather than claiming none.
- **A page that has not been republished since your change serves the old
  stylesheet, which is a free "before" snapshot.** Webflow regenerates CSS per
  publish, so an untouched page still has the original rule. Reading
  `.home-hero__checkbox-icon-wrapper` off `/lp/beehive` gave the exact pre-change
  declaration to restore. It also means a shared-class change is **latent**: other
  pages keep the old value until someone republishes them, so "nothing looks
  broken" right after the edit proves nothing.

The safe test is: does every current user of this class want the new value? If
the class already defines the property and any user relies on the old value, keep
it page-scoped.

**Some CSS is not meant to be a class property, and moving it is the mistake.**
The acquisition LP's testimonial section overrides seven shared classes from an
element embed scoped under an ancestor `.is-acq`. Those base classes are the
*other* variant and seven other live pages depend on them -
`.testimonial-image-2-2` is `180px` site-wide and `196px` on the acquisition
pages, `.custom-testimonials-slideshow-2-2` is `display: none` site-wide and
visible there. Webflow's style system is class-based and cannot express
"these properties, but only inside an `.is-acq` ancestor", so this styling
**belongs in CSS** - the reference page puts it in an embed for exactly that
reason. It is not an agent workaround and must not be migrated to the classes.

The test is not "can this be a class property" but "does every element carrying
this class want this value". Variant overrides fail that test by definition.
What is left after applying it honestly is small: variant overrides, interaction
states (`.active X`, `:hover Y`), pseudo-elements, and elements the API cannot
create. All of that is normal Webflow practice.

**Combo classes are the isolated alternative, at a price.** A combo matches on
its **exact parent chain**, so `is-x` created under `[grid_3-cards]` cannot be
applied to an element whose chain is `[grid_3-cards, is-acq]` - `set_style`
fails outright and you need a second combo. That is one combo per distinct
chain, not one per rule. Use combos when the base class is shared and the value
differs; use the base class when it does not.

### Element embed code has to go in page custom code

`HtmlEmbed` code is readable and **not writable**: `set_settings` accepts a
setting `key` but no value for it, `data_whtml_builder` rejects `<style>` tags
outright, and its `css` parameter only accepts Webflow's six standard
breakpoints (so a hand-written `@media (min-width: 992px)` is refused). When a
section's behaviour lives in an embed, relocate that code to the page's freeform
custom code via `data_scripts_tool > set_page_freeform_code`. Class-scoped CSS
and JS behave identically there. Leave a comment saying where it came from and
why, or the next person will move it back.

### A duplicated `redirect_to` on a `/start` CTA is expected, site-wide

A site-level head script holds a `campaignRedirectMap` and appends
`&redirect_to=<mapped path>` to every link whose `?campaign=` value it
recognises. It does **not** check whether the link already has one. So any CTA
that hardcodes both `campaign=` and `redirect_to=` ends up with the parameter
twice in the DOM, while the served HTML has it once.

Do not file this against a page you just built. Verified 2026-09-17: the live
`/lp/youtube-video-editing` reference page shows the identical duplication on
all four of its CTAs. Copy a `campaign=` CTA from an approved page and you
inherit the behaviour, which is the correct outcome - matching the reference.
Check the **served HTML** before calling any link malformed; a runtime
difference between source and DOM means a script did it, not the build.

**`set_page_freeform_code` replaces the whole block**, so always
`get_page_freeform_code` first and re-send the existing content with your
addition appended. Two things worth checking before you write: the page may
already load the library you were about to add (the YouTube LP already had
Swiper 8.4.7, CSS in head and JS in footer), and code moved from the body into
`head` now runs earlier, so wrap an init in `DOMContentLoaded` and guard on the
library being defined.
