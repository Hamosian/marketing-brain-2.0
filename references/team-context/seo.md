# SEO & AI Search - team context

**Lead:** Erika Varangouli · **Function:** SEO & AI Search
**Source type:** `feed` team → `.claude/skills/growth-marketing-team-tasks/data/seo.md` (see `references/team-task-registry.md`)
**Last updated:** 2026-08-12 · first report ingested (Q2 FY26)

> Point-in-time digest, not live data. Every number below is quoted from the source
> report and goes stale. For a current figure, route to `/rivermind:ask`; for the
> live artifact, see `/organic-dashboard` and `systems/owned/seo-organic-dashboard.md`.

## Trajectory

Organic is in a **rebuild, not a growth phase**. Non-brand organic has declined
since the December 2025 core update, compounded by the riverside.fm → riverside.com
migration and brand-entity ambiguity (Google conflating Riverside and riverside.fm,
flagged by Abel in May 2026). The Algorythmic audit was commissioned in July 2026 to
find the root cause. Revenue has held up because AI surfaces and brand demand filled
the gap, not because non-brand recovered.

## Q2 FY26 (May-July 2026)

**Source:** [Organic Search - Q2 FY26 report](https://claude.ai/code/artifact/1c2e4669-564c-4c38-8e1d-b73d5edb79f6) ·
file `references/team-context/reports/organic-search-q2-fy26.html` · prepared by Erika for Nir.
Not filed to the Drive report library (there is no Quarterly folder under `Year 2026/`).

### Performance

- **Organic new MRR $194.7K**, +8.7% YoY, −3.3% vs prior quarter.
- **Composition inverted.** Non-brand $51.7K (−42.4% YoY), brand $80.2K (+14.4%),
  LLM $62.8K (+227.1%). A year ago non-brand was half of organic revenue; it is now
  a quarter. The part SEO work most directly controls is the part that shrank.
- **Non-brand clicks 71,173**, −43.8% vs prior quarter. Impressions fell harder,
  36.7m → 18.3m (−50%), which is an eligibility problem rather than a CTR problem.
  Clicks bottomed in June (20,172) and recovered 23% in July (24,810).
- **The commercial cluster fell out of the top 10.** "Best podcast recording
  software" and neighbours slid from positions 5-10 into the high 20s. Top-3
  presence nearly doubled (8 → 14) while 4-10 emptied out (93 → 50).
- **AI visibility 63.4%**, rank 1 share of voice (10.0%) in the category, second
  most-cited domain behind YouTube only. Weakest on Perplexity (53.1%).
- **The blog is the epicentre of the decline.** Non-brand blog revenue −61.6% YoY
  ($43.4K → $16.7K), versus product pages −30.8% and Studio/Tools near flat.

### Insights

- **LLM revenue is mostly self-reported, not observed.** Only 25% of Q2 LLM signups
  came from an observed AI referral; 75% are onboarding-survey self-reports. Of the
  $62.8K LLM MRR, **$12.3K is observed and $50.5K self-reported**. A year ago the
  split was 63/37 observed. This is the report's own caveat and it is the open
  measurement question (see below).
- **LLM traffic lands on the homepage, not on articles**, which reads as brand
  behaviour rather than content discovery.
- **AI referral growth is entirely OpenAI** (73% of AI referral traffic, +28.3%).
  Every other platform declined. Single-vendor concentration risk.
- **Microsoft crawled us ~503K times and cited us zero times**, ramping 42x across
  the quarter. Either an indexing pipeline we are invisible to or a licensing gap.

### Blockers

- **Localisation is structurally blocked.** Crowdin is the source of truth and
  overrides Webflow, so German SEOs cannot edit localised pages directly; changes
  route through Google Sheets. French never went live, blocked on a Webflow
  publishing issue. See `systems/owned/localization-workflow.md`.
- **German produces zero non-brand conversions**, two quarters running, despite
  being the fifth-largest market by clicks with the highest top-ten CTR (5.42%).
- **All six product page rewrites shipped nothing to production.** Briefs and
  content complete, every design/build/staging subitem unstarted. Largest planned
  initiative of the quarter. The bottleneck is design and build capacity, not SEO.
- **Help Center upgrade stuck** since early July on hiring a freelance dev.
- Pruned pages still discoverable in blog catalogue and search pages despite
  301/410 (flagged 14 July, unresolved). 302 redirect loop on the language selector.

### Big bets / next

Nir's review notes on this report and the Q3 asks (LLM measurement fix, German plan,
product-page retro, Bing WMT) are tracked as `seo-29` in
`.claude/skills/growth-marketing-team-tasks/data/seo.md`, with a 30-minute review
booked for **2026-08-25**.

## Known gaps in this digest

- **No GSC year-over-year exists.** The riverside.com property holds ~17 days of
  data in May-July 2025 because of the migration, so all GSC comparisons are versus
  the prior quarter. Snowflake business results are user-level and do carry a true YoY.
- **58.8% of signups are unattributed**, so every channel figure is a floor.
- **Attribution basis** is `best_attributed_first_visit_channel_group` (the July 2026
  first-visit fix). Numbers will not match reports built on the pre-fix field.
- One report ingested so far, so there is no quarter-over-quarter trend in this file yet.
