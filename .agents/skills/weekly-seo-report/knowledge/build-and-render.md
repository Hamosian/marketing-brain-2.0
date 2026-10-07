# Build and render - the report's shape, and the rules that keep a week honest

## The artifact

One self-contained HTML file, **two tabs**, published to the stable URL in
[`stable-url.md`](stable-url.md). Dark Riverside theme (`--bg:#0F0F14`,
`--accent:#7C5CFF`), Instrument Sans from Google Fonts, aggregated data embedded
as JSON, no runtime fetches (the artifact CSP blocks them).

**Do not redesign it.** The layout is settled and its value is week-to-week
comparability: a reader should be able to put two editions side by side. Read
the last published version first and rebuild from it, keeping the CSS, the tab
script and the section order identical. Load `riverside-brand-guidelines` before
drafting, per the department rule.

### Tab 1 - Snowflake funnel

1. **Overall organic search** - five tiles (first visits, sign-ups, trials, new
   subscriptions, first MRR), each with WoW percentage and absolute, then a
   short lede saying what actually moved.
2. **Split by channel** - non-brand / brand / LLM across all five metrics, with
   a total row that must foot to the tiles.
3. **Top 25 landing pages by sign-ups** - sign-ups, first visits, trials,
   subscriptions, MRR. Homepage merged. Footer subtotal.
4. **Biggest sign-up movers** - two tables of 10, gained and lost, ranked by
   absolute change.
5. **Top 20 landing pages by new subscriptions** - the revenue view.
6. **Data notes and issues** - ordered by how much each would change a decision.

### Tab 2 - Search Console

Its own window (see the two-window rule in the data dictionary), announced in a
`.srcnote` banner at the top. **Seven sections, in this order, and no others.**
Fixed by Amir on 2026-09-17; earlier editions carried brand/non-brand, device,
`/blog` and `/de` breakdowns, and he asked for them out.

1. **Search Console overview** - four tiles (clicks, impressions, CTR, average
   position) with WoW chips, plus a lede.
2. **Top 25 queries by clicks** - clicks, prior, Δ, Δ%.
3. **Top 10 non-brand queries, clicks improved.**
4. **Top 10 non-brand queries, clicks declined.**
5. **Top 25 pages by clicks.**
6. **Top 10 pages, clicks increased** and **Top 10 pages, clicks decreased** -
   two sections, same shape.
7. **Top 10 countries** - clicks and impressions side by side, each with prior
   and Δ%, plus CTR current vs prior.

Then one short method-notes section. Everything the tab needs to caveat -
the `date`-rollup defect, numeric-filter distortion, why query and page rows do
not foot to the property total, and any open impression anomaly - goes in that
one section, as prose. Do not give a connector problem its own section with
evidence tables; that crowds out the analysis the reader came for.

**Rank ties at the cut must be named.** On 2026-09-17 ranks 25 and 26 were both
114 clicks, so the table's cut was arbitrary. Say which page fell out and at
what value, in the lede under the table.

### Every edition ends with

A method paragraph naming the exact SQL shape and window, a Search Console
method paragraph, the "no Ahrefs or Omni" line, and the AI diligence statement
(`ai-diligence-statement`, styled per `riverside-brand-guidelines`).

---

## The rules that keep a week honest

The monthly's safeguards all apply (homepage canonicalization, never dropping
NULL dimension keys, no runtime fetches, update in place). Read
[`../../organic-dashboard/knowledge/safeguards-and-gotchas.md`](../../organic-dashboard/knowledge/safeguards-and-gotchas.md)
once. These are the ones a **7-day window** adds.

### 1. The thin-base floor

At weekly volume a page goes 2 subscriptions to 6 and posts "+200%". That is a
small denominator, not a finding. Show the **absolute move in a grey chip**
instead of a percentage wherever the prior window held **under 5 subscriptions
or under $100 MRR**, and title the chip so hovering explains why. Sign-up
percentages are fine at this grain: sign-ups run about 14x subscriptions.

State the count in the table's lede ("13 of the 20 pages held under 5
subscriptions a week earlier"), so nobody reads the grey chips as missing data.

### 2. Windows must be a multiple of 7, and holidays checked separately

Weekend organic traffic is roughly half a weekday, so two windows holding
different numbers of weekend days measure the calendar. Seven days against
seven days handles that automatically.

It does **not** handle public holidays. [`../scripts/resolve_week.py`](../scripts/resolve_week.py) flags the movable
Mondays that actually move these numbers, and a hit is a prompt to check rather
than an explanation. Sep 7 2026 (US Labor Day) cost about 830 first visits
against the previous Monday; the week still grew, which is the more interesting
read and only visible once the holiday is named. Say which market: the US is
roughly four times the UK here, so two windows each holding "a holiday Monday"
are not equivalent.

### 3. The table restates, so a WoW figure depends on when you compute it

`marketing_rollover` keeps filling in for at least a week. The window
Aug 27 to Sep 2, published on Sep 3, re-queried on Sep 10:

| Metric | Published | A week later | Move |
|---|---|---|---|
| First visits | 33,190 | 33,118 | -72 |
| Sign-ups | 6,377 | 6,400 | +23 |
| Trials | 1,289 | 1,297 | +8 |
| New subscriptions | 452 | 463 | +11 (+2.4%) |
| First MRR | $14,272.01 | $14,678.63 | +$406.62 (+2.8%) |

Late-arriving conversions explain the rises; the small visit decline suggests
reprocessing too. **Always query both windows in the same run** so the
comparison inside one edition is internally consistent, and say so in the
method note. When a headline differs from what last week's edition implied, name
both figures rather than letting the reader assume one is wrong.

### 4. Auth and in-product pages are not acquisition pages

`/dashboard/mcp`, `/login`, `/register`, `/verify-email`, `/sso`,
`/dashboard/start-actions` land in the top tables and have topped the movers
list. A sign-up recorded there reflects the page the user was on when the event
fired, not the page that brought them in. Mark every one with the `.flagdot`
span and say in the notes how many there are and what they carry, so nobody
prioritizes SEO work off them.

### 5. Stage counts in a window are not a cohort

Each row is one user hitting one stage, dated when that stage happened. A
sign-up this week can follow a first visit from weeks ago, so sign-ups divided
by first visits is not a conversion rate, and a page can show more sign-ups than
visits. Show the counts side by side; never render a rate.

### 6. Two-stage pull: low threshold to find candidates, exact match to publish

Numeric filters change the values of the rows they return, not just which rows
come back (see the data dictionary). But an unfiltered pull of every query is
too large to be practical. So:

1. **Candidate pass** - pull with a low numeric threshold (`clicks >= 4` worked)
   to get the shortlist of pages and queries worth showing.
2. **Exact pass** - re-pull exactly those keys with a dimension filter
   (`["query","in",[...]]`, `["pagepath","in",[...]]`), unfiltered on metrics,
   for both windows. Publish only these values.

The distortion is not uniform, which is what makes stage 2 non-optional. At
`clicks >= 25` on 2026-09-17: `streaming setup` returned 68 against a true 151;
`ai transcription free` returned 30 against a true 103, 3.4× understated. At
threshold 4 the large values came back exact (`clipper video` 63 = 63) while
small ones still understated (`transcribe` 4 against a true 12). Worse for a
movers table, a filtered pull renders an absent row as a zero:
`transcribe audio to text free online` showed as 0 and was actually 23, which
would have published a fake collapse.

### 7. Say when nothing moved

If the movers tail is thin (everything below the top few tied at the same small
delta), say that plainly. "There is no broad decline this week" is a real
finding and stops a reader hunting for a story in noise.

---

## Before publishing

1. `node --check` the extracted inline script.
2. Confirm `/` is present and top of the pages table. If it is missing, the
   NULL-drop bug is back: stop.
3. Cross-foot the channel table to the tiles, and every table footer to an
   independently computed sum. A footer typed rather than computed is the
   easiest error to ship.
4. Confirm every thin-base cell renders a grey chip, not a percentage.
5. Render it once and look at both tabs.
