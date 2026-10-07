# Routine ideas: candidates not yet built

A shortlist of recurring checks worth turning into cloud routines, filtered
from the 43-entry loop catalog in Corey Haines's
[marketingskills](https://github.com/coreyhaines31/marketingskills) (MIT,
read 2026-09-08) down to the ones that read a platform this department already
has and belong to a Growth Marketing function. Cadences follow the rule in
`routine-design.md`. None of these is scheduled; each is a candidate for
`/agent-builder`, and every one stages output for a person rather than writing
to a live platform.

Owners are the functions in the `CLAUDE.md` department table, not people.

## Candidates

| Idea | Check | Acts when | Reads | Stages | Owner function | Nearest existing skill |
|------|-------|-----------|-------|--------|----------------|------------------------|
| Ranking-drop watch | Weekly | A priority page or keyword drops past N positions vs baseline | Search Console (via the weekly SEO report's sources) | A regression note with likely cause | SEO & AI Search | `weekly-seo-report` (reports; does not alert on drops) |
| Content decay | Monthly | A page's trailing-90-day clicks decline materially | Search Console, Omni | A prioritized refresh list | SEO & AI Search | `organic-dashboard` |
| Ad fatigue | Every 2 to 3 days | Frequency up and CTR/CVR down past a significance bar, ad out of learning phase | Ad platforms via `paid-acquisition-agent` | Fresh variants off the winning angle plus a recommended budget move; never shifts budget | Paid | `paid-acquisition-agent`, `ad-creative` |
| Paid-search query mining | Weekly | Search terms show waste or new intent above a click threshold | Google Ads search-terms report | Negatives, new exact-match, landing-page mismatches | Paid | `paid-acquisition-agent` |
| Landing-page regression | Weekly, and on deploy | A top acquisition page regresses on conversion, speed, form or tracking | Omni signups by landing page, Convert | A regression alert with cause; escalates a revenue-page break immediately | Growth Channels / Website | `page-cro`, `marketing-website-page-qa` |
| Signup-funnel leak | Weekly | A signup step regresses vs baseline after ruling out tracking breakage | Omni funnel (figures through `/rivermind:ask`) | One experiment brief | Growth Channels | `/marketing-brain` depth-first diagnosis |
| Competitor watch | Weekly | A tracked competitor changes pricing, positioning or a comparison claim | Competitor pages (the battle-card set) | A change digest and which comparison page to update | Growth Marketing with PMM | `are-we-really-different` (on demand today) |
| Tracking QA | Weekly, and on deploy or campaign launch | A key event, pixel or UTM convention is missing or misfiring | GTM, GA4, HubSpot form events | A fix list; escalates a broken conversion event immediately | Marketing Ops | `analytics-tracking`, `hubspot-workflow-qa` |
| Analytics anomaly | Daily | A tracked metric leaves its normal band | Omni "Daily Campaign Signup Attribution" | Nothing when in band; one routed alert when not | Marketing Ops | `measurement-agent` |
| Directory and AI-index submission | Monthly | A relevant new directory, AI tool index or MCP registry lacks a listing | The submitted-directories ledger, web | Prepared listings for a person to submit | SEO & AI Search | `seo-ai-search-agent` |
| Campaign postmortem | On campaign end | A campaign closes | Omni, HubSpot campaign objects | A postmortem plus backlog inputs; one per campaign | Growth Channels | `campaign-agent` |

## Already running (do not rebuild)

| Catalog idea | What covers it here |
|--------------|---------------------|
| Weekly marketing review | `/chief-of-staff` (daily) and `/nir-weekly-report` |
| PQL / upgrade-intent | `/nir-mql-live-report` (inbound demo MQLs, daily); the PQL model itself is analytics-owned (`docs/platform-integration.md`) |
| Experiment backlog | Convert Experiences is the source of record (`systems/owned/convert-experiences.md`) |
| Backlog hygiene | `/mops-backlog-review` (monthly), `/ticket-hygiene` |

## Not Growth Marketing's to build

Churn signal, dunning, expansion and upsell (CS, RevOps, Product), lifecycle
email refresh (check `lifecycle-agent` ownership before assuming), newsjacking,
social listening, community engagement and review-site responses (Sivan
Mazuz's org). List them when asked; do not scaffold them here without the owning
team.
