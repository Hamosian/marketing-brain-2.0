---
name: riverside-product-knowledge
description: >
  Answers how the Riverside product works - recording, studio settings, participant roles
  (Guest, Producer), AI/Magic tools, editing, transcription and captions, hosting/publishing,
  podcast hosting, mobile/desktop apps, account/subscription/billing, affiliate program, and
  Riverside for Business (team roles, SSO/SCIM, async recording, API). Trigger on "does Riverside
  do X", "how does [feature] work", "what plan is [feature] on", role/plan/limit questions, and
  "help center", "support article", "product FAQ", or any customer-support/sales-enablement
  product question. Reference/knowledge only - no live system access, so it can't check a live
  account's actual plan or usage.
---

# Riverside Product Knowledge

This skill is Marketing's copy of Riverside's Help Center - organized the same way the real
help center is, so answers stay traceable back to a real article. Use it to answer any question
about what the Riverside product does, how it's organized, and what's gated by plan.

The full reference lives at `references/product/help-center-reference.md`. **Load that file
before answering** - don't rely on memory or guess at feature details, plan gating, or numbers.
It covers all 8 help-center categories, the full AI feature matrix, the Riverside-specific
glossary, and a plan-tier breakdown.

## How to answer

1. Load `references/product/help-center-reference.md`.
2. Find the category/section/article that covers the question (the Details section mirrors the
   real help center's structure, so search by category first, then article name).
3. Answer using the definitions and facts documented there. Don't improvise plan gating, feature
   names, or numbers that aren't in the file.
4. If the question is about a specific account's actual plan, usage, or billing state, say so -
   this skill only knows the *product*, not any customer's account. Route account-specific
   questions to Support or, if the question is really a CRM/lifecycle question, to `/hubspot-agent`.
5. **Never state a specific price as current fact.** Every price in the reference file is flagged
   third-party-derived and unverified against the live pricing page. If asked for pricing, give
   the plan/feature breakdown, note that riverside.fm/pricing is the source of truth, and don't
   assert a number as confirmed unless the user explicitly says they've already checked it.
6. If a question touches a beta feature (AI credits, AI B-roll, VideoDub as of this snapshot),
   flag that availability may vary by account/region and roll out gradually.

## Quick orientation (see the reference file for full detail)

- **Core architecture:** Riverside records each participant locally in a separate high-quality
  track (video up to 4K/2160p, audio at 44.1 or 48 kHz), so quality isn't degraded by internet
  bandwidth. Tracks upload to the cloud during/after the session. This is the top-of-funnel
  differentiator versus meeting tools like Zoom/Meet.
- **AI is opt-in vs. built-in.** Opt-in (must be actively applied): Magic Audio, Find Fluff,
  Filler Words, AI Voice, VideoDub, AI Translation, AI B-roll, Eye Contact, Enhance video, AI
  Co-Creator, AI Chapters. Built-in (core to the platform): Transcriptions, and the "Made for
  You" suite (Magic Clips, Magic Segments, Magic Episodes, Hooks, AI Show Notes, Posts).
- **AI credits** (beta) pay for AI Translation (1 credit = 1 minute) and AI B-roll (1 credit =
  one 5-second clip). Available on Pro/Live/Webinar/Business; purchased separately from the
  subscription; don't renew monthly; only account owners/admins can buy them.
- **Plan tiers** (Free → Standard → Pro → Live/Webinar → Business/Enterprise) gate resolution,
  download hours, watermark removal, Magic Audio, the producer role, async recording, custom
  frame rates, higher bit rates, and enterprise features (SSO/SCIM/API). Exact tier names and
  prices are **not** published by Riverside directly - always point to riverside.fm/pricing for
  the current source of truth rather than quoting a number from this skill as final.
- **Security posture:** SOC 2 Type 2 compliant, ISO/IEC 27001 certified (since May 2022),
  encrypted connections, secure cloud storage, GDPR/CCPA aligned. Full SOC 2 report available
  under NDA to Enterprise customers via security@riverside.fm.
- **Participant roles:** Host (starts/stops recording, one per session), Guest (recorded),
  Producer (Business only - manages the session, seen but not recorded), Audience member
  (watches live, not recorded unless promoted via Live Call-In).
- **Riverside for Business:** four team roles (Account Owner, Admin, Director, Editor), SSO
  (Google, Microsoft Azure/Entra ID, Okta, others) + SCIM provisioning, async recording, the
  Business API, XML/AAF timeline export to Premiere/Final Cut.
- **Affiliate program:** 20% recurring commission via Impact.com, no payout cap, commissions
  roughly 60 days after the referral link is used.

## When this isn't the right skill

- Questions about a specific customer's Pre-Op, deal, or lifecycle stage → `/preop-data-intelligence`
  or `/hubspot-agent`.
- Questions needing live usage/behavior data (how many users used feature X) → `/riverside-user-intelligence`.
- Writing external-facing copy about the product (positioning, tone, ICP framing) → `references/messaging/`
  and `/content-agent`.
- Visual identity / how something should look → `/riverside-brand-guidelines`.

## Keeping this current

The reference file is a snapshot (see its header for the date) and should be re-verified
quarterly - Riverside ships AI features frequently and plan gating changes. If you learn
something that contradicts the reference file, update `references/product/help-center-reference.md`
directly and open a PR; don't just answer once from memory. Consider suggesting `/retro` after
a substantive correction.
