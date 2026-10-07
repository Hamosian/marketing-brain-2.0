<!-- Formerly PART 3 of SKILL.md. Moved out for progressive disclosure: loaded only when drafting an email or Slack handoff (see SKILL.md 'What to read, and when'). Every "PART 3" reference in SKILL.md means this file. -->

# PART 3: EMAIL DRAFTING RULES

Apply to ALL emails, daily batch or single reply.

## Structure (always one short paragraph + sign-off)

```
Hi [First Name],

[1-2 sentences personalized context] [1-2 sentences moving forward] If you want a walkthrough you can grab time [here](https://riverside.chilipiper.com/concierge-router/link/sdr-router?id=<EMAIL%20encoded>&meeting_source_cp=ai_sdr&meeting_campaign_cp=qbd_hs&utm_medium=email_nir), or is there a specific question I can help with?

Nir
```

One paragraph. No bullets, no feature lists, no P.S., no multi-section emails. The booking link is INLINE on the word "here" as a markdown link (Gmail draft creation converts it to `<a>`); never a separate "Booking link:" block.

**Recipients block sits above the body, only when there are multiple recipients:**
```
To: primary@example.com
Cc: secondary@example.com, work@example.com
```
Omit the To/Cc block if there's only a single address.

## Hard rules (canonical - every rule stated once here)

- **Keep the body short and coherent.** One clean idea per sentence. Don't stack clauses into a run-on (e.g. "you've been on the Webinar plan for a while, so there's a good amount on the Business plan that isn't in the self-serve experience once a few people are recording"). Cut to opener + one use-case sentence + CTA. If a Business nod is genuinely needed, keep it to one short clause. Read the middle sentence aloud: if it needs a breath mid-sentence, split it or cut it.
- **Never state the licence count back to them.** No "With 50+ people needing access…", "with 6 to 10 people needing access…", "you flagged 2-5 licences…", in any position. They filled the field; repeating it tells them nothing and burns the sentence. This is the ONLY thing the 2+ licence override means by "acknowledge the team-size signal": let the count decide that you write to a team rather than a solo creator, and that you pitch Business. Never put the number in the body.
- **The role-anchored noun must be a real category, never a lift of their job-title string.** Use "Content teams", "Marketing teams", "Producers", "Production teams", "Instructional design teams". A title like "Sports Original Content" becomes "Content teams", not "Original content teams" - pasting the title into the noun slot reads like a mail-merge.
- **No stated use case? Read the Intent Read (Step 4.5.5), don't jump to "Brands".** When the form is blank, the Intent Read has already walked signup answers, prior-meeting Gong, current plan, product events, and the entry page. Use its use_case to write the descriptive sentence exactly as if the lead had stated it, in the shape its confidence picks (Email shapes below). **On a blend (two candidate use cases), name both in the 2-3 slot sentence, strongest first** ("Brands usually use Riverside for webinars and podcasts, and the clips cut from the same recording"), with the guess-check line. The data behind the inference is never quoted back: no "saw you visited the webinar page", no "since you've been recording", nothing the lead didn't give us; only their own account state (plan, being a Riverside user) is referenceable, as the existing-customer templates already do. Only when the Intent Read returns `unknown` do you fall back to "Brands usually use Riverside for…", and even then **run light enrichment first for a qualified lead**: check the company's website/domain to infer the likely use case, use it only to choose the angle, and never mention anything you couldn't know from the form.
  - **A use case the lead stated on the form always wins. Weak POSITIONING of it is the failure, not the use case (hard rule per Nir).** When `content_goal_dropdown` / `content_audience_dropdown` / `content_audience_specify` name what they want (customer education, internal comms, training, client work), use it: they told us. What's banned is describing it dully. "record once, then cut it into shorter pieces", "internal updates", "training content" undersell an end-to-end production studio and give the lead no reason to book. **Express the stated use case through the main-use-case vocabulary** Riverside actually wins on: podcasts, webinars, customer interviews, and the clips and repurposing cut from the same recording. Shape: `Brands usually use Riverside for customer education: webinars and interviews recorded once, then repurposed into clips.` Only when the form says nothing at all do you fall back to the generic list: `Brands usually use Riverside for podcasts, customer interviews, and the social clips cut from the same recording.`
- **Every sentence must earn its place.** Acknowledging HDYHAU signals or form fields ("Saw the referral from X and the 2-5 license request") usually reads as forced personalization that adds zero information - cut it. The middle sentence should either (a) answer a question they asked, (b) reference something specific they wrote, or (c) describe how their role uses Riverside - not read back facts they already gave the form. Rule of thumb: if the sentence would still be true and useful with the personalization removed, cut the personalization.
- **Never open a reply to a complaint on a negative note (hard rule per Nir, 2026-08-31).** No "Sorry, that shouldn't be this hard", "Sorry you're having trouble", "That sounds frustrating", or any opening that leads on the problem. Open on the fact that resolves it, then steps, then the caveat, then support. Warmth after the answer, never as the lede. Canonical copy in SKILL.md PART 3.
- **Never appraise what the lead wrote. Answer it with value.** When you reference something from their form, do NOT grade, validate, or characterise their thinking. Banned: "which is a fair way to approach it", "that's a smart way to think about it", "you're right to look at it that way", "makes sense", "good question", and every variant that scores their approach instead of advancing it. It reads condescending from a vendor, and it burns the one sentence that should have been doing work. Replace the appraisal with what Riverside would actually show them, phrased as something we want to do: "We'd love to show you how the Business plan could enhance the content and programming you're already running." Rule of thumb: if the sentence evaluates the lead, cut it and state the value instead.
- **Name a concrete Business-plan edge, not "there's a good amount on the Business plan."** Every booking-push email must give one specific reason the demo is worth their time, drawn from what Business actually adds over self-serve. The verified Business-only list (source: the plan-tier breakdown in `references/product/help-center-reference.md`): the producer role and a producer running the session from backstage, async recording, team roles across owner/admin/director/editor, SSO and SCIM, the Business API, Salesforce integration, custom frame rates, XML/AAF timeline export, book-a-producer on demand, a dedicated CSM, priority support, SOC 2 report access under NDA, unlimited shows and hosting.
  - **Match the edge to the role with `business-edge-hooks.md` (in this skill's directory).** It maps the verified edges to four buyer motivations (team collaboration, production control, enterprise security, white-glove service), each with a pre-cleared benefit-led anchor line and two trailing edges. Read it to pick the anchor for a lead's role, and read its "do not ship" list before writing any security or integration edge: security certifications (SOC 2, ISO 27001, encryption) are company-wide posture, NOT a Pro-vs-Business gate, so never frame them as one; only Salesforce and the Business API are verified Business-gated integrations, not Marketo/HubSpot.
  - **Shape: one anchored edge, then two named without explanation.** Pick the ONE that best fits their use case, chosen from their `form_comment` first and their job title second, and give it a short clause of substance so they can picture it. Then name two more from the verified list as a bare list, no explanation, no benefit clause. The anchor earns the reply; the other two signal there's more without turning the email into a feature dump. Never explain all three, and never let the trailing two grow past a few words each. Shape: `What isn't in the self-serve experience is [anchor edge + short clause]. [Edge two] and [edge three] are on there too.`
    - **The anchor clause states the benefit, not the feature's parts (per Nir).** Say what the team gets, not how the feature is built. Do NOT enumerate a feature's sub-components: for team roles, write "team collaboration" or "everyone records and edits in one shared account", never "owner, admin, director and editor". Do NOT write "instead of separate logins": Business members each sign in as themselves (SSO/SCIM, per-member roles), so that phrasing is contradicted. The contrast that is true is one shared account instead of each person paying for their own. Producer role → "you run the session from backstage without appearing on camera", not a list of controls. If the clause reads like a spec line, it's a feature; rewrite it as the outcome. The trailing two edges use the plain benefit noun too ("team collaboration", "the producer role", "async recording"), never a parts list.
  - **Studio branding is NOT on that list, and must not be used at all without a fresh check.** The plan-tier reference puts basic branding on Free (live streaming) and image/text overlays on Standard, so "the Business plan adds your own branding" is unverified and probably wrong. Same discipline for any capability not named above, in the anchor slot or the two short mentions: if it is not in the verified list, run the Step 4.2 confidence gate before it goes in an email. A named edge the lead can disprove in one click costs more than a vague one. Vague gestures at "a good amount that isn't in the self-serve experience" are still a fail: they tell the lead nothing and give them no reason to book.
  - **This applies to current customers too, and matters most there.** An existing free, Pro, Grow or Webinar user already knows what Riverside does, so "you've seen the basics" is the setup, never the whole middle. Follow it immediately with the specific thing their plan doesn't have. Same for anyone mid-trial.
    - **Above ~200 employees, never state what their current self-serve plan already does (hard rule per Nir).** Write only about Business. Do NOT tell a large-company lead that a feature they asked about is already covered on Pro, Grow or Webinar, even when it is true and even when it answers their form comment: it argues them back down a tier, and at this size the self-serve plan was never the destination. Answer the intent through the Business capability instead (their teleprompter ask becomes "on Business a producer can drive the script and prompter during the session"). **The only exception is when the lead raises the comparison themselves** - they explicitly ask which plan has a feature, ask whether Pro is enough, or name their current tier as the benchmark. Naming a specific feature is NOT raising the comparison. Below ~200 employees the honest "you already have that on Pro" answer still applies, since a real self-serve fit should not be pushed to Business.
  - **Anchor the edge on their title.** A producer or show designer cares about the producer role and backstage control; a marketing or content lead cares about async recording and team roles across the org; an IT or ops buyer cares about SSO/SCIM, the Business API, and Salesforce. Match the anchor to the role you're writing to, pick the two short mentions from the same neighbourhood, and pair the whole thing with the peer bridge for that role rather than repeating the default opener.
- **Opener.** Include "I run growth and marketing operations here at Riverside." Default opener: `"I run growth and marketing operations here at Riverside and thought I'd reach out directly."` then 1-2 sentences of personalized context. Don't repeat the subject line - the subject already says "Saw your Riverside request…", so don't also open with "Saw your business demo request come through" (says the same thing twice). Only lead with "Saw your X…" when X IS the personalized hook on a FIRST touch (e.g. "Saw your question about frame rate support").
- **Peer bridge (honest, varies by use case).** Keep the true anchor "I run growth and marketing operations here at Riverside" every time. When the lead's use case is clear, add ONE honest half-clause that shows you live in their world, drawn from what marketing genuinely does: webinars → "and we run a lot of our own webinars on Riverside"; podcasts → "and we produce our own shows on it"; content/social/repurposing → "and my team lives in clips and repurposing all day". Only when the lead's title maps to a function you actually own (Growth, Marketing Ops, Demand Gen, SEO, Paid) go the full literal peer match: "I run marketing ops here, so I've built the exact stack you're evaluating." Never claim a title or function that isn't real (you do NOT "run the webinar program"). No clear use case → plain default opener, no invented bridge.
- **HDYHAU can set the angle, only when it's real.** When `how_did_they_hear_about_us__enterprise_form_` names something concrete (a specific podcast, community, conference, or referral), let it pick the peer bridge or use-case angle. Boring/blocklist answers (Google, LinkedIn, search) never touch the email. It informs the angle only: never quote it back and never write "I saw you found us via X."
- **Read for the concern under the words, never echo them back (hard rule per Nir).** A lead's message is a symptom, not a spec. Before drafting, name the real thing they are worried about and answer THAT, even when they never said it outright. "Should I still take the tutoring?" is not a question about tutoring, it is "will the effort be wasted if the product changes." "I want a one-stop-shop" after a browser complaint is "will I actually get record-plus-edit in one place." Reusing the lead's own noun ("yes, do the tutoring", "our one-stop-shop") proves you skimmed and answers nothing. Restate their concern in your own terms, answer the underlying worry, and cut any sentence that only parrots a word they used.
- **Casual inbound reply: answer it, don't announce it.** When the lead has replied in an existing thread, especially in a short or informal way, drop the opener entirely: no "I run growth and marketing operations here at Riverside", and no "Saw your question about X" restatement of what they just wrote. They know what they asked. Open on the answer itself ("Yep, all four.", "Yes, that works on the Business plan."), then give the detail. Restating their question back at them reads like a ticket auto-reply; matching their register reads like a person. This applies to every reply-mode email, not only product questions.
- **"I run growth and marketing operations here at Riverside" placement - ONLY at the start.** It's the opener line: very first or second sentence after "Hi [Name]," - or omitted entirely if the opener is a "Saw your question about X" product hook. NEVER in the middle or end, never after a product answer, never as a mid-email reintroduction. If a product-question draft answers the question first, drop the line entirely (the signature already identifies Nir).
- **"here" hyperlink placement.** "here" in "here at Riverside" is PLAIN TEXT, never a link. The ONLY hyperlinked "here" is in "grab time [here]" at the end. Hard rule.
- **NO DEMO PROMISES - zero exceptions.** Nir does NOT do the demo; demos route via Chili Piper to an AE. Never imply Nir personally walks the lead through anything. Banned phrases include: "I can walk you through", "I'd love to show you", "let me give you a demo", "happy to walk through" (any form), "happy to dig into", "happy to show you", "I can show you" / "let me show you", "let me run through", "I'll walk you through", and any "happy to [demo/explain verb]" or "I [demo/explain verb]". Rule of thumb: if it sounds like Nir is offering to personally explain/show/walk through anything, it's banned. The body sentence is for context (describe the use case, state a product fact, name what teams do). The walkthrough offer lives ONLY in the CTA "If you want a walkthrough you can grab time [here]" - delivered by the AE. Good replacements: "Marketing teams usually use Riverside for [X].", "Interviews are exactly what we're built for.", "There's a good amount on the Business plan that isn't in the self-serve experience.", or skip the body intro and go straight to CTA.
- **NO UNVERIFIED CLAIMS.** Never invent stats about the customer base, setup time, user count, or capabilities. If it's not a fact from riverside-intel or product-details, don't say it.
- **No Business trial - zero exceptions.** Only self-serve plans (Pro, Grow, Webinar) have trials. The `business_trial_started` field is misleadingly named - it marks self-serve trial starts even when the user submits the Business demo form. NEVER write "your Business trial", "you just started a Business trial", "since you're on the Business trial", or any variant implying a Business-plan trial. If `business_trial_started=true` AND the plan state is not a `business` customer, treat it as a self-serve trial - and don't reference "the trial" in the email unless it's directly relevant, and never call it a Business trial. Don't say "Business Plan trial"; name the specific plan (Pro/Grow/Webinar) from `customer_plan`, then `product_plan_raw`, and if both are unpopulated just say "trial".
- **No em dashes or en dashes** in the email body - use a colon, period, or split sentence.
- Contractions always.
- No feature lists, no bullet points, no P.S.
- **"Business plan" not "Business side" - zero exceptions.** "Side" is internal shorthand that leaks the two-product architecture and reads like AI copy. Say "the Business plan" or "Business" as the noun, in descriptive sentences, CTA framing, and follow-ups.
- **No industry framing in the descriptive sentence.** Don't lead with "Content teams in pharma usually…", "Marketing teams at fintechs…". It reads AI-generated (role + industry + use case is the LLM default). Anchor on role alone: "Content teams usually use Riverside for X". If industry matters, name it via a specific form detail (their use case, company name), not a demographic tag.
- **Don't use "events".** Correct use cases: webinars, podcasts, social content, interviews, internal comms, testimonials, courses.
- **Never write a name in ALL CAPS, and don't name the lead's podcast or company in the body (per Nir).** If a first name or company comes through in caps (e.g. "ZAKI'S PERSPECTIVE", "CLAUDE MATAR"), normalize it to proper case in the greeting and body - all-caps reads like a mail-merge. And don't reference the lead's specific podcast/company name in the body ("for a podcast like <name>"): it sounds scripted. Keep it generic ("for a podcast setup", "your team").
- **Don't say "demo request" - say "business demo request"** to acknowledge they're looking at the business tier.
- **Self-serve plan tiers.** There is NO "Live" plan - it's now **Grow**. The ladder above Pro: **Grow (20 hours/month) → Webinar (25 hours/month)**. When pointing Pro users to higher tiers for more recording/transcription hours, name Grow and Webinar with these allocations. Never reference "Live".
- **"team collaboration" not "team seats"/"multi-seat".** "Seats" is a billing word; "collaboration" describes what the user gets. E.g. "team collaboration, branded sessions, and admin controls".
- **Never frame a plan or feature negatively.** No "overkill", "too much", "way more than you need", "wasted on". Frame Business positively ("built for larger teams") and recommend the lower tier as a fit: "the Business plan is built for larger teams, but for a solo creator setup our Pro trial covers what you need."
- **Never offer to send examples, case studies, or materials.** No "I'll send a few customer examples", "I can share some samples/videos", or any variant. The CTA is always the booking link (and the University link for self-serve/exploring leads).
- **Don't repeat the same idea three ways.** One tight sentence wins.
- Don't use LinkedIn bio / company description verbatim, and don't mention things you couldn't naturally know from a form submission.
- Don't use sales qualification language: "what's driving the upgrade", "what specifically caught your attention", "curious what brought you in".
- Don't reinterpret what they asked for. If they asked for a demo, keep it about the demo.
- **Sign off as "Nir"** (not "Nik", not "NIr").
- **ALWAYS end every email with "or is there a specific question I can help with?"** - after the booking CTA, or after the self-serve links for trial replies. If the structure doesn't land there naturally, restructure so it does. **The one exception: an ongoing casual thread.** Once the lead has written back more than once in short, informal messages, drop the closer entirely and stop re-sending anything they already have. Repeating the same sign-off question on every reply is the single clearest tell that a bot is answering. Same goes for the 24/7-support line and any link already sent earlier in the thread: send it once, never twice. On these threads answer the question, match their length and register, and stop.

## Subject line

- Always includes "Riverside". No contact name. Must feel personal, not transactional.
- Default: "Saw your Riverside request, wanted to reach out".
- Alternatives: "Quick one about your Riverside request" / "Fair point on the Riverside form".
- For DQ self-serve invites (body opener references the request), use a variant that does NOT repeat "Saw your Riverside request": `About your Riverside request`, `Quick option for your Riverside setup`, `Re: your Riverside form`.

## Standard links

- **Booking (Chili Piper):** `https://riverside.chilipiper.com/concierge-router/link/sdr-router?id=[EMAIL with @ as %40]&meeting_source_cp=ai_sdr&meeting_campaign_cp=qbd_hs&utm_medium=email_nir` - for "grab time [here]".
- **Trial signup** (push for self-serve fits, never the free tier): `https://riverside.com/start`.
- **Riverside University:** `https://riverside.com/university` - **self-serve replies ONLY.** Never include when the lead asked for a demo or is a Business candidate (then the CTA is the booking link, period).
- **Podcast hosting:** `https://riverside.com/podcast-hosting` - when a lead asks whether Riverside hosts podcasts, or assumes we do and we confirm.
- **Help Center articles:** `https://support.riverside.com/hc/en-us/articles/...` - include the specific article(s) behind a product answer when the lead is self-serve or the answer has real setup steps, so they can read the detail themselves. Use the exact URL from the IKB article you sourced the answer from, never a guessed or constructed one. Link the article's topic as the anchor text ("[Instagram](url)", "[what each platform requires](url)"), cap it at three links, and put them in one sentence near the end. Never send Help Center links to a Business candidate whose CTA is the booking link.

**Self-serve guidance:** for a clear solo/1-license/individual creator fit, always push the trial at `riverside.com/start` (never the free tier), paired with the University link.

**Product facts (don't get wrong):**
- **On-brand positioning - always (per Nir):** Riverside is an **end-to-end production studio** for creating studio-quality video and podcasts: recording, editing, clipping/repurposing, transcription, and distribution, all with AI. Describe it that way. NEVER undersell it as "just a recording tool" or "a recording studio" alone. When you state a limitation, frame it against this full positioning (e.g. "we're an end-to-end production studio built around capturing participants in a session, so X isn't a fit"), not by shrinking what Riverside is.
- **How to position the Business plan itself - the seriousness axis (canonical framing per Nir):** Business is *the same platform, at a higher grade*, not a different product and not "the expensive one". Nir's framing, to work from rather than paste:

  > "Our Business product is the stronger, more professional, more collaborative, and more secure version of our platform for those who are really implementing a serious and robust content strategy versus doing more of a hobbyist podcast or livestream series."

  Four adjectives, and each one maps to a pillar in `business-edge-hooks.md`: **stronger and more professional** → production control, **more collaborative** → team collaboration, **more secure** → SSO/SCIM and the security review, with white-glove service as the layer that supports a serious rollout. Use it to pick which pillar to anchor on, and to set the altitude of the whole email: you are writing to someone running a content operation, not selling them software.

  **This beats "built for larger teams" whenever you are pitching UP to Business.** Headcount invites the lead to disqualify themselves ("we're only three people"), and the data agrees that is where deals die: "need does not justify enterprise cost" is 47% of all losses. Seriousness of the content operation is the better qualifier, because a three-person team publishing weekly is a real Business fit and a twenty-person company recording twice a year is not.

  **Two hard limits on it:**
  - **Never characterise the lead, only the product.** Say what Business is. Never say or imply what the lead is. "Hobbyist" is an internal word for the altitude of the offer: it never appears in anything a lead reads, in any form, however softened.
  - **Do NOT use the seriousness axis when routing a lead DOWN to self-serve.** In a DQ self-serve invite you are telling someone they don't qualify, so "Business is for serious content strategies" lands as "yours isn't". Keep the headcount frame there ("the Business plan is built for larger teams"), which is about fit rather than ambition and is why it is already the wording in those templates. Pitching up: seriousness. Routing down: team size.
- Riverside DOES host podcasts (`riverside.com/podcast-hosting`). Never claim we aren't a podcast host or send people to Buzzsprout/Transistor/Spotify for Podcasters.
- When unsure about a feature, check `riverside-intel` + `references/product-details.md` before claiming we don't support it.

## Self-review checklist (mechanical final checks; nik-voice / writing-optimizer / de-ai run separately)

**First, before any other check:** run a literal string search for the em dash (U+2014) and en dash (U+2013) characters in the email body. Replace any with a colon, period, or split sentence. (Report section dividers may use `-`; the email body may not.)

Then verify the Hard-rules items that are easy to miss:
1. Sign-off is "Nir".
2. "here at Riverside" NOT linked; only "grab time here" linked.
3. Demo-promise check - no "I can walk you through" or any banned phrase.
4. Unverified-claims check - no invented stats.
5. "I run growth and marketing operations here at Riverside" appears at the START or not at all. On a reply to an existing thread, it should not appear at all, and the email must not open by restating the lead's own question back to them.
6. No Business-trial reference - search for "Business trial", "Business plan trial", "started a trial".
7. Subject line: no name, includes "Riverside", not transactional.
8. Use-case accuracy (no "events"); "Business plan" not "Business side"; no industry framing.
9. Guess-check closer: if the middle sentence is a role-anchored guess at the use case, include "Is that what you have in mind?" between it and the CTA (see below). Skip if the middle sentence is a definitive statement or product answer.
10. Appraisal check: no sentence grades or validates what the lead wrote ("a fair way to approach it", "smart way to think about it", "makes sense"). State the value instead.
11. **Licence-count check:** search the body for a seat/licence number ("50+", "6 to 10", "2-5"). If one appears, cut the clause.
12. **Role-noun check:** the role-anchored noun is a real category, not their job-title string. No use-case signal anywhere? It reads "Brands", not "Teams".
13. **Front-clause check:** no sentence opens with a form-fact clause ("With X people…", "You flagged…", "Since you selected…"). Start on the value.
14. **Business-edge check:** the email anchors on ONE concrete thing Business adds, matched to their comment or title, then names exactly two more with no explanation. All three must be on the verified Business-only list in Hard rules (producer role/backstage, async recording, team roles, SSO/SCIM, Business API, Salesforce, custom frame rates, XML/AAF export, book-a-producer, dedicated CSM). **Studio branding fails this check** - it is available in some form below Business. Fails also if: the trailing two carry benefit clauses instead of bare names, more than three are named, or the middle reads "there's a good amount on the Business plan that isn't in the self-serve experience" and stops there. Applies to current self-serve customers too.
15. **Fact-check gate (blocking):** run the `demo-reply-fact-check` skill over every drafted email before the report is presented. Any claim it returns as `UNVERIFIED` or `CONTRADICTED` must be cut or replaced before the draft ships. See Step 4.6.
16. Style pass against `drafting-style-digest.md` (Smart Brevity + Gary Provost Rhythm, distilled). Check every draft sentence-by-sentence against the digest - its stacked-front-clause check is explicit, so a one-line gloss is no longer the fallback. Open the full references in `plugin-skills/writing-optimizer/references/` only per the Step 4.6 escalation rule.
17. **Intent Read check:** the descriptive or pain sentence matches the Step 4.5.5 use_case, the template matches the stage, and the shape matches the confidence (pain-led only on stated or corroborated intent; blends and single-source inferences carry the verbatim guess-check line). No usage, page-view, or signup-answer fact is quoted back; only the lead's own account state may be referenced. The report line and the `Intent` / `Intent Source` log values match what the draft actually used.

## Email shapes: pain-led (A) vs descriptive (B) - the Intent Read's confidence picks one

The Intent Read (Step 4.5.5) hands every draft a confidence, and confidence decides whether the middle of the email names a pain or describes a use case. Tag the shape in the `Variant` format tag (e.g. `intent-shapeA-v1 | podcast · fragmentation`) so the learning loop can compare the two.

**Shape A - pain-led. Only when confidence is stated (form or meeting) or inferred with two agreeing rungs.** You may only name a pain you're confident the lead has: a guessed pain from a vendor reads presumptuous. Shape: opener (with peer bridge when honest) → one sentence naming the friction teams hit running THEIR use case, taken from the lead's pain-map cluster and always framed as tool fragmentation plus collaboration, never billing → the Business edge that removes it (one anchor + two bare, per Hard rules) → CTA → closer. Example middle for a confident podcast power-user: `Most podcast teams at your stage hit the same wall: the show gets recorded in one place, edited in another, and clipped in a third, and nobody can work on it together. That's what the Business plan removes: everyone records, edits, and clips from one shared account, with the producer role and async recording on there too.` All pain rules stand: never billing-shaped, never mirror "record remote interviews", never quote map verbatims, seriousness axis when pitching up.

**Shape B - descriptive. For single-source inference, any blend, and title guesses.** The existing shape: opener → descriptive use-case sentence (one noun, or the 2-3 slot blend on conflict) → the verbatim guess-check line → Business edge → CTA → closer. A blend is always Shape B.

Stage still picks the template first (existing-user, self-serve trial, DQ invite, choice email); the shape governs the middle sentences inside whichever template fires. Templates with their own fixed body (seat add-on, complaint, loop-in, follow-up email 2) are exempt from both shapes.

## When the descriptive sentence is a guess - end with "Is that what you have in mind?"

When the middle sentence is a *guess* at the use case (the "X usually use Riverside for Y, Z, and W" pattern, inferred from role because they left no form_comment), follow it with **"Is that what you have in mind?"** - placed right after the descriptive sentence, before the CTA. It gives the lead a chance to correct the guess; it does NOT replace the required closer.

**Use that sentence verbatim. It is a fixed line, not a paraphrase slot (hard rule per Nir).** No variants: not "Is that what you're hitting?", not "Is that what you're after?", not "Does that sound right?". The improvised versions read like sales-speak and land outside Nir's voice. Nine words, exactly as written, or drop the guess-check entirely.

```
[Opener]. [Descriptive guess: "Advisors usually use Riverside for X, Y, and Z."] Is that what you have in mind? If you want a walkthrough you can grab time [here], or is there a specific question I can help with?
```

**Use it** whenever the middle sentence is a role-anchored generalization ("Founders usually…", "Content teams usually…", "Producers usually…", "Advisors usually…"). **Don't use it** when the middle sentence states a product fact or references something the lead explicitly wrote (e.g. "Oral histories are exactly what we're built for.", "Saw your question about frame rate support - [answer].", "You've been on the Webinar plan for a while…"). Don't stack three question marks in one email - keep the guess-check tight.

## Scenario templates

**General question** (e.g. "How complicated is international podcasting?"):
> Saw your question about recording with international guests, it's simpler than you'd expect. Your guests in the US, Sweden, wherever, just click a link from their browser, no downloads or setup on their end...

**Specific product question, answer is yes** (check riverside-intel / product-details for accuracy):
> Saw your question about frame rate support. Yes, the business product lets you lock recordings at 24, 25, or 29.97fps (constant frame rate), so your post-production workflow stays clean. I run growth and marketing operations here at Riverside. If you want a full walkthrough you can grab time [here], or is there a specific question I can help with?

**Product question, answer is no** (be honest, don't dodge):
> Saw your question about [feature]. That's not something we support right now. [Brief context if relevant.] I run growth and marketing operations here at Riverside. If you want to see what we do have and whether it fits, you can grab time [here], or is there a specific question I can help with?

**Form feedback/complaint about the form** (e.g. "That licenses question makes no sense"):
> Saw your comment on the demo form. You're right, that licenses question doesn't make sense if you haven't used the platform yet. A license is basically a seat, one per person who needs to record or edit...

**No form comment, role gives peer connection:**
> I run growth and marketing operations here at Riverside and thought I'd reach out directly. Are you looking at this for podcasts, webinars, or something else?...

**No form comment, specific use case from page visited:**
> Saw your question about hosting webinars on Riverside. The setup is pretty seamless: your attendees just click a link to join, no downloads or installs...

**Existing user who asked for a demo:**
> I run growth and marketing operations here at Riverside and thought I'd reach out directly. You've been using Riverside for a while so you probably know the product better than most. If you want a proper walkthrough you can grab time [here], or is there a specific question I can help with?

**Someone on a self-serve trial who submitted a business demo request:**
> I run growth and marketing operations here at Riverside and thought I'd reach out directly. You've already started a trial so you've seen the basics, but there's a good amount on the Business plan that isn't in the self-serve experience. If you want a walkthrough you can grab time [here], or is there a specific question I can help with?

**Existing self-serve user asking a feature / paywall / plan question (PLG fit, NOT a Business candidate):**
Solo/small operator on Free/Pro/Grow/Webinar/Standard asking "can I do X on my plan?" or "what plan unlocks this?" - DO NOT push the booking link. Answer in one tight sentence, name the correct plan once, tell them to upgrade from their account, and route anything specific to their setup to 24/7 support. Nir does not troubleshoot self-serve setups.
> Hi [First Name],
>
> I run growth and marketing operations here at Riverside. You can do all of that on the [correct plan] plan: [feature 1], [feature 2], [feature 3]. You can upgrade right from your account. If anything specific isn't working in your setup, our 24/7 support team can help: reach them from the in-app chat or at support@riverside.com. Or is there a specific question I can help with?
>
> Nir

Rules: one sentence to answer; name the plan once (don't explain why their current plan blocks them); direct them to upgrade from their account, not a sales call; NEVER offer Nir's personal troubleshooting ("tell me what you're seeing and I'll look into it") - always route setup-specific issues to 24/7 support; skip the booking link entirely.

**User wants to add ONE more seat / editor (seat add-on flow):**
When `form_comment` is specifically about adding ONE seat (host, editor, co-host) to an existing self-serve account - it's an in-product add-on. Do NOT push the booking link, do NOT recommend upgrading, do NOT mention Business. Exact answer (adapt only the noun host/editor/co-host, keep the rest verbatim):
> Hi [First Name],
>
> I run growth and marketing operations here at Riverside. If you just want to add another seat you can get it as an add-on: it's on Pro, Grow and Webinar. Go to account settings, then Team, then Members, put the editor's email in, and you buy the seat as part of the invite. One catch: a trial account can't invite an editor at all. Anything else that comes up, our 24/7 support team can help from the in-app chat or at support@riverside.com. Or is there a specific question I can help with?
>
> Nir

Use even if HubSpot has them as DQ. Skip the booking link and the Pro-trial invite.

**Form complaint about the product itself** ("hard to navigate", "not happy", "frustrating"):
The lead is venting, not asking for a demo. Don't push the walkthrough/booking link (tone-deaf after a complaint). Acknowledge briefly, ask what tripped them up, end with the closer.
> Hi [First Name],
>
> I run growth and marketing operations here at Riverside. Saw your note that the platform's been frustrating, that's useful feedback and I'd rather hear it than not. What specifically tripped you up, or is there a specific question I can help with?
>
> Nir

No booking link, no walkthrough offer, no feature dump. If they reply with a specific question, answer in single-reply mode.

**Disqualified lead with a real (small-scale) use case - self-serve invite:**
Apply when `booking_status_cp__c = Disqualified` AND plan state is not paid (see SKILL.md Step 1, Plan state) AND `business_trial_started` is not `true` AND `content_audience_specify` or `content_goal_dropdown` shows a real but small-scale use case. Don't push the booking link; push Pro trial + Riverside University. **Keep it simple:** acknowledge they asked for a Business demo, note Business is built for larger teams, and point them to the Pro trial as the better starting point. Don't hook on their specific content focus (the "your form mentioned X, so..." construction reads clunky). **Always tell them to open the links on desktop** (the trial and University don't work cleanly on mobile).
> Hi [First Name],
>
> I run growth and marketing operations here at Riverside. You asked for a demo of the Business plan, which is built for larger teams. For a setup like yours the best place to start is our Pro trial, free for 14 days: record, edit, and publish from one place. Open these on desktop: [riverside.com/start] to start the trial, and [Riverside University] has walkthroughs to get you up and running. Or is there a specific question I can help with?
>
> Nir

**Special case `content_goal_dropdown = "Just exploring or testing"`** (or "Other"/"Not sure yet"): don't lead with "Business is built for larger teams" - frame the trial as the way to test. Example: *"Your form said you're just exploring, so the easiest way to actually test it is our Pro trial: [features]. You can start it at riverside.com/start..."*

**Short DQ self-serve invite (no content fields, friendly form_comment):**
Apply when DQ + 1 license + personal email + no `content_audience_specify`/`content_goal_dropdown` + `form_comment` friendly but not buyer-quality. Keep it to 2 sentences. Subject: `Quick option for your Riverside setup` or `About your Riverside form`.
> Hi [First Name],
>
> I run growth and marketing operations here at Riverside. You asked for a demo of the Business plan, which is built for larger teams. For a solo setup the best place to start is our Pro trial, free for 14 days: record, edit, and publish from one place. Open these on desktop: [riverside.com/start] to start the trial, and [Riverside University] walks you through the basics. Or is there a specific question I can help with?
>
> Nir

## Adapting by role

Tone by role:

- **CEO / Founder:** very direct, get to the point fast.
- **Marketing Ops / Marketing Manager:** peer-to-peer framing.
- **Content / Creative roles:** can reference their content work if publicly visible.
- **Event Coordinator / Comms:** seamless setup and branded experience angle.
- **Technical roles:** keep it simple, don't assume they care about the creative side.

### Pain by role - routing into `pain-map.md`

`pain-map.md` holds the pain each requester type is actually solving, drawn from 2,149 form comments and 3,095 closed deals over Feb-Aug 2026. Map the title to one cluster, read that section only, take its email insert.

| If the job title looks like | Read this cluster | Confidence |
|---|---|---|
| Founder, CEO, Owner, President, Managing Director, Principal, COO, GM | Founder / CEO / Owner | High |
| Marketing Manager/Director, Head of Marketing, VP Marketing, CMO, Product Marketing | Marketing (generalist) | High |
| Producer, Exec Producer, Production Manager, Post-Production, Audio Engineer | Producer / Production | High |
| Agency Owner, Studio Manager, Lead Producer, or company named Studios/Productions/Media | Agency / Production Company | High |
| Host, Co-Host, Podcaster, Talk Show Host, Radio Host | Podcast host | High |
| Social Media Manager, Video Editor, Videographer, Creative Director, Brand Manager | Social / Video | High |
| Content Marketing Manager, Content Strategist, Head of Content, Editor, Editorial Director | Content Marketer / Editorial | High |
| Marketing Ops, Demand Gen, Head/Director of Growth, RevOps | Marketing Ops / Demand Gen | Directional (n=32) |
| CTO, CIO, Head of IT, IT Manager, Procurement | Enterprise / IT buyer | Directional (n=29) |
| L&D Manager, Training Manager, Enablement | L&D / Training | Directional (n=23) |
| Director/Head of Communications, Comms Manager, Internal Comms, PR | Internal Comms / Corp Comms | Directional (n=23) |
| Anything else, or academic | Skip the map, draft from the form comment | No pattern |

**High-confidence clusters:** use the insert as written. It's backed by 66 to 629 real comments.

**Directional clusters:** the pain is real but thin, so treat the insert as a hypothesis. If the form comment points elsewhere, follow the comment. These four stay thin because those titles rarely fill the form, not because the window was short, so don't expect them to firm up on their own.

### The one finding that changes what you name

**Do not mirror "record remote interviews" back at a lead.** It's the pain most correlated with losing: it appears in 42.1% of lost deals against 33.4% of won, because it's a Pro-shaped need and the top lost reason is "Need does not justify enterprise cost" (47% of all losses).

When the comment says only that, look for the adjacent scale signal instead - team size, licence count, cadence, audience size, number of shows or clients - and name that. What correlates with winning: webinars and live (+8.8 points), recording quality (+8.7), editing throughput (+6.6), API and SSO (+6.5), repurposing (+5.8).

Still never state the licence count back to them (see Hard rules). The count tells you to write to a team and pitch Business. It never appears in the body.

## Key product points (weave in naturally, never list)

- **Seamless setup:** guests just click a link to join, no downloads.
- **Branded experience:** webinars and recordings carry the company's branding.
- **Local recording:** each participant records locally, quality doesn't depend on internet.
- **All-in-one:** recording, editing, clipping, and publishing in one platform.
  - **Name publishing, not transcription, when you list the workflow (per Nir).** Transcription is a commodity every tool ships, so it makes the all-in-one claim sound small. Publishing is where the fragmentation actually hurts: the team records in one tool, edits in another, then hands off to a separate hosting platform. Riverside hosts the podcast and distributes to Apple Podcasts, Spotify, and YouTube, so recording through publishing stays in one place. That is the stronger use case for editorial, content, and podcast leads. Only lead with transcription when the lead asked for it by name.
- **International guests:** works across time zones with no friction.

Only mention the ones relevant to what the person asked about. **When the use case maps cleanly to Riverside (warm/obvious fits), one line is enough** - if role + form_comment already point at a textbook use case (oral histories, podcasts, B2B thought-leadership, executive comms), don't explain how local recording or link-joining works. A clean one-liner ("Oral histories are exactly what we're built for.") beats a paragraph of feature claims. The booking-link CTA does the rest.

## Broden loop-in email (ONLY when the regional sales lead explicitly directs it)

Broden is NOT the default AE for pricing/quote asks. Route those via the regional Slack DM (below) and use this template only after the regional lead explicitly says to loop Broden in - they may want a different AE, especially outside the US.
- **Recipients:** To = the lead's primary email AND `broden.stewart@riverside.fm` (both in To, so it reads as an intro).
- **Subject:** `About your Riverside quote request` (or `Re: [existing thread subject]`).
- **Sign-off:** `Thanks, Nir` (matches Nir's real loop-in pattern - different from the standard `Nir`).
- No booking link, no walkthrough offer, no product context, no "I run growth and marketing operations" opener. It's a loop-in, not a positioning email.
- Log status: `Sent - loop-in to Broden Stewart (pricing quote)`.

```
Hi [First Name],

Thanks for your interest in Riverside. Saw you asked for a quote on the form. I'm adding @Broden Stewart from our team who can help you with that.

Thanks,
Nir
```

## Sales handoff via Slack (canonical routing + templates)

For all AE-handoff scenarios - mid-conversation pricing rejecters, "who can I talk to" replies, specific meet-time requests, broken booking-link reports, vendor-onboarding/procurement asks, AND initial-form pricing/quote asks - Nir does not handle it. Hand off via Slack DM to the regional sales lead so they assign the AE (including Broden, only if the regional lead directs it).

**Booked-meeting check - run this BEFORE any handoff (hard rule per Nir).** First pull the lead's `booking_status_cp__c` and `number_of_meeting_records`. If they already have a booked meeting, do NOT DM a regional lead and do NOT route: the assigned AE already owns the pricing conversation and covers it on that call. Instead reply kindly acknowledging the meeting - name the host and date (host from the associated meeting's `hubspot_owner_id`, title from `hs_meeting_title`, time from `first_meeting_start_time`), reassure them the AE will handle pricing and their specific needs on the call, and close. Applies to every handoff trigger, including a reply that asks for pricing after the lead has quietly booked (leads often reply "what's the cost?" and book an intro call minutes apart). Log status `Booked`, not `Awaiting routing`. Route to the regional lead only when there is no booked meeting. This is a reply-mode email, so follow the casual-reply opener rule (drop the "I run growth and marketing operations" opener).

**Routing table (canonical - referenced by Step 0a, 4.2, 4.5):**

**US and Canada → post in `#US Demo requests routing` (`C0BQ1RJH32Q`), never a DM (per Nir).** Nikki, Andrew, and Erin are all in it. One channel message per lead, and **@-mention the owner the tier picks** so the ask lands on a person rather than the room:
- **company `numberofemployees` >= 1000** → mention Erin Neal (`<@U09K1D3HQSG>`). Erin alone owns the 1000+ tier.
- **company `numberofemployees` < 1000** → mention Andrew Sweeney (`<@U0A6YGNREUC>`) AND Nikki Nahoum (`<@U04J07AHQ2X>`)
- `numberofemployees` empty or unknown → mention Andrew and Nikki (smaller bucket) and say in the message that the size is unknown so they can re-route.

One message per lead, never one message covering several leads: each lead needs its own thread so the reply attaches to the right person. Never split a lead across parallel DMs, which hides each recipient's answer from the other.

Non-US routing stays on DMs:
- **LATAM (all countries)** → Nikki Nahoum (`U04J07AHQ2X`)
- **Everywhere else** (EMEA, APAC, etc.) → Louie Libbert (`U07FAKNSZHN`)

Determine geo from company HQ, email TLD, or stated location; when ambiguous, use the company's primary market. If a known US org has a `.com` email but the user is clearly EMEA-based, route by user location. For the US/Canada employee-count split, pull `numberofemployees` from the associated company record; if empty/unknown, default to Nikki (smaller bucket) and note the assumption in the DM so they can re-route. The split applies to ALL handoff types here.

**Which template:** specific times given → meet-time template; booking link broken → booking-link-broken template; vendor onboarding → vendor-onboarding template; replied asking for pricing/salesperson without naming times, or initial-form pricing/quote → pricing-rejecter template.

### Step 1: Slack draft
Tool: `slack_send_message_draft`. `channel_id`: the routed lead's ID (both IDs for the Andrew+Erin case). Message: short and direct - who the lead is (name, company, role), what they want, relevant context (existing customer? deal size? license count? employee count if it drove the Andrew+Erin routing?), and the ask "who should I loop in?" Don't fill it with sales-pitch context; give facts and the lead's own words.

**HubSpot owner in every Slack handoff - hard rule.** Every DM MUST include the current owner NAME (resolved from `hubspot_owner_id` via `search_owners`, NOT the raw ID) on its own line: `Owner: [Full Name]` (or `Owner: unassigned`). Applies to ALL templates below.

**Send time - 7am in the RECIPIENT's local time, never 9am.** Look up the recipient's timezone (`slack_read_user_profile`, or `slack_search_users` which returns it) and compute the Unix timestamp for 07:00 local. If 07:00 local today is already past, send immediately rather than holding it to tomorrow: a same-day handoff beats a tidy send time. If it is still ahead, schedule with `slack_schedule_message` at that timestamp. Never schedule off Nir's own timezone.

**Scheduled Slack messages cannot be cancelled or edited through the MCP** (`slack_schedule_message` is create-only). Once one is queued the only way to pull it is Nir deleting it from Slack's "Drafts & sent". So get the send time right the first time, and always report the scheduled local time back in the report so Nir can intercept before it fires.

Pricing-rejecter template:
```
Hey, got a lead who replied that they don't want a demo, just pricing.

[First Last] · [Title] at [Company]
[Email]
Owner: [Full Name or "unassigned"]
Existing [Pro/Free/etc.] customer (or: new lead). Wants [X licenses / shared seats / specific feature]. HubSpot: [link]

Their exact ask:
> [paste the relevant part of their reply]

Who should I loop in?
```

Meet-time request template:
```
Hey, got a lead who replied wanting to meet and gave specific times.

[First Last] · [Title] at [Company]
[Email]
Owner: [Full Name or "unassigned"]
[New lead / existing Pro/Free customer]. [X licenses / use case]. HubSpot: [link]

Times they offered:
> [paste the times verbatim from their reply]

Who should I loop in?
```

Booking-link-broken template:
```
Hey, got a lead who tried to book but the ChiliPiper link is looping / broken on their end.

[First Last] · [Title] at [Company]
[Email]
Owner: [Full Name or "unassigned"]
[New lead / existing Pro/Free customer]. [X licenses / use case]. HubSpot: [link]

What they wrote:
> [paste the relevant part of their reply, including any times they suggested]

Who should I loop in?
```

Vendor-onboarding template (note company size + country so the regional lead can prioritize):
```
Hey, got a lead from [Company] asking for vendor onboarding info so they can add us as a vendor in their procurement system. Not a demo or pricing ask.

[First Last] · [Title] at [Company] ([Country], [X] emp)
[Email]
Owner: [Full Name or "unassigned"]
Status: [DQ / Not Booked / etc.]. HubSpot: [link]

Their exact ask:
> [paste form_comment verbatim]

Who can help with vendor onboarding info?
```

### Step 2: Surface in the daily report under "Sales handoffs needed via Slack"
**Recipient label - hard rule.** Every surfaced Slack draft MUST begin with a labeled recipient line ABOVE the fenced code block (so it isn't pasted into Slack): `**→ Slack DM to [Full Name] (Slack ID: [UXXXXXXXX])**` - e.g. `**→ Slack DM to Nikki Nahoum (U04J07AHQ2X)**`, `**→ Slack DM to Erin Neal (U09K1D3HQSG)**`, or `**→ Slack DM to Louie Libbert (U07FAKNSZHN)**`. Include the Slack draft text and the Slack thread link (after Nir sends). The lead gets no email until the regional lead routes; then draft the loop-in email per PART 3.

### Step 3: Update the outreach log
Add the lead with status `Awaiting routing`. Once routed, update to `Replied - handed off to [AE name]` and draft the email (Broden-style two-sentence loop-in, adapted to the AE name).

## Gmail draft creation (only after approval)

- Use `text/html` so "here" is a proper `<a>` hyperlink. No CDATA wrappers; pass clean HTML.
- **A drafted row that has left the drafts folder means Nir sent it, not that the tool misfired.** `create_draft` drafts; it does not send. When a later check shows the message carrying the `SENT` label and absent from `in:draft`, that is the normal end state of the workflow. Read the send timestamps before concluding anything went wrong: sends in reverse creation order are Nir working down a newest-first drafts list.
- To = primary email. If `hs_additional_emails` (comma-separated) or `work_email` is non-empty, put them in Cc.
- Use the approved subject line.
- Must start with `Hi [First Name],<br><br>` and end with `<br><br>Nir`. Verify greeting and sign-off before creating.

**Property reminders:** never use `message` when you mean `form_comment`; never treat `enterprise_form_submission_date` alone as proof of a demo request (check `recent_conversion_event_name`); never auto-skip on `number_of_meeting_records` alone; never invent HubSpot contact IDs (pull `hs_object_id`, re-query if missing).
