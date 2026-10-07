---
name: win-loss-pricing-analyzer
description: Turn Riverside's own Gong calls and HubSpot deal data into a defensible win-loss picture, focused on why deals are won or lost on price. Produces a coded deal-level table and a written report with verbatims, segment/product concentration, trend over time, and recommendations for PMM, paid, and CRO. Triggered by "win-loss", "win loss analysis", "why are we losing deals", "losing on price", "closed lost reasons", "price objections", "pricing objections", "discount analysis", "competitive losses", "win rate trend", "pricing sentiment", or "/win-loss-pricing-analyzer".
---

# Win-Loss Pricing Analyzer

Turns Riverside's closed-deal data and sales conversations into a defensible view of why we win and lose, with a dedicated lens on price. The output is meant to feed messaging (PMM), paid and CRO copy, and the pricing conversation with Product and Finance. It does **not** recommend a price change on its own; pricing is a cross-functional, verify-before-publish decision.

## When to run it

- Quarterly at minimum, monthly for competitive or fast-moving segments (Kyle Poyar's cadence).
- Ad hoc when a segment's win rate moves, a competitor shows up repeatedly, or discounting spikes.

## What good looks like

Two artifacts, every time:

1. **Coded deal table** - one row per deal in the period. Columns: deal name, segment (Agency / Mid Market / Enterprise), deal type, won/lost, ACV or MRR, primary loss reason, `price_related` flag (true/false), competitor (if any), discount off list, and a short verbatim snippet or note.
2. **Written win-loss report** - the narrative below, built from that table.

## The rule of thumb (frame the price finding)

Aim to lose roughly **20% of deals on price**. Below ~10% usually means prices are too low (little pushback is a signal, not a win). Above ~40% means something changed in the market or the packaging. Report where we actually sit against that band, by segment, not just the blended number.

## Data sources (in order)

Always pull live. Never estimate a number, and attach source + as-of date to every figure (`references/evidence-standards.md`).

1. **HubSpot deals** - via the `hubspot-agent` (don't call the API directly). Pull closed-won and closed-lost deals for the period with: segment, deal type, amount (ACV/MRR), close date, competitor field, discount, and the closed-lost reason. **Discover the real property names first** (closed-lost reason and competitor fields vary); ask `hubspot-agent` to confirm them rather than hardcoding.
2. **Gong call metadata** - via the `data-agent` against Omni topic `gong_calls` (model `RS Snowflake`, id `48d89fd2-ce24-44e1-bfe5-f3e30334c6dc`). Use it to see which lost deals had late-stage calls (pricing usually surfaces there) and to link reviewers to the actual calls for verbatims. See `/gong-calls-explorer` for the field list.
3. **Verbatims** - the highest-value evidence. Pull the actual buyer language on price from Gong call review and HubSpot notes on the flagged deals. Quote what the prospect said, not a paraphrase.
4. **Objection taxonomy** - the `riverside-intel` skill (1,120 B2B deals, battle cards, and its `b2b-buyer-voice` reference) for the standard objection and competitor patterns to code against. It is a personal skill, not in this repo. When it is not installed, code the objections from this period's verbatims instead, and say in the report that the taxonomy was built from this sample rather than the standard one.

**Fallback when deal/call data is thin:** summarize external pricing sentiment for the category from Reddit, G2, and LinkedIn with web search, and say clearly in the report that this is external signal, not our own pipeline.

## Workflow

### Step 1 - Scope
Ask (use `ask_user_input_v0`): time period (default last full quarter), segment(s), deal type (New Sales / Renewals / Upsell / All), and whether they want the full report or just the price cut.

### Step 2 - Pull and code the deals
Get closed-won + closed-lost deals from `hubspot-agent`. Build the coded table. Set `price_related = true` only when the loss reason, notes, or a call verbatim actually names price, budget, or discount. Don't infer price from "went with competitor" alone; competitors are lost for reasons other than price.

### Step 3 - Enrich with calls and verbatims
For price-flagged and competitive losses, use the `gong_calls` topic to find the relevant calls and pull the buyer's own words. Aim for two or three real verbatims per key finding.

### Step 4 - Write the report
Structure:
- **Headline** - win rate this period and % of losses on price, vs the 20% band, with the trend vs prior period.
- **Where price is the problem** - is price loss concentrated in one segment or product, or broad? Concentration is the actionable finding.
- **Verbatims** - what prospects actually said.
- **Competitive** - who we lose to and on what (price vs feature vs trust).
- **Pains and unmet gains** - restate the top loss reasons as customer pains (undesired outcomes, obstacles, risks) and unmet gains, per segment, with n. This is the section `/value-proposition-canvas` consumes; loss reasons are the only pain evidence that comes with a revenue outcome attached, so tag them `Observed` with the deal count. "Need does not justify enterprise cost" is a fit failure (the Value Map addresses pains the segment does not rank), not only a price objection.
- **What changed** - vs last period; call out discounting drift and ACV movement.
- **Recommendations** - split into: messaging/CRO fixes we own now, and pricing/packaging questions to take to Product + Finance. Never present a price change as a decided marketing action.

### Step 5 - Deliver
- Render the coded table and win-rate trend with `visualize:show_widget` (read `dataviz` / `read_me` module `chart` first). Riverside-branded.
- For a shareable doc, hand off to `content-agent` so it lands on-brand and runs the `nik-voice → de-ai` pass (`references/messaging/ai-writing-tells.md`).

## Guardrails

- **Every number carries source + as-of date.** If HubSpot and Gong disagree on deal counts, surface both and note the gap; never silently pick one (`references/evidence-standards.md`).
- **Pricing is verify-before-publish** and owned with Product/Finance. This skill informs the decision; it doesn't make it.
- **No fabricated verbatims.** If you can't find real buyer language on a point, say the evidence is thin rather than inventing a quote. AI-invented quotes cluster on generic names and are a credibility risk.
- **Read-only.** This skill analyzes; it doesn't write to HubSpot or move deals.
