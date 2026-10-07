# Red-Team Claims - regression fixtures for the fact-check gate

Claims that shipped, or nearly shipped, and were wrong. Each one is a test of the **gate**, not of the copy.

Run every fixture whenever `verified-claims.md` changes, whenever plan tiers or packaging change, and whenever `SKILL.md` rules change (Step 7). A fixture that does not return its expected verdict is a live regression: fix the rule before shipping anything else.

**Add a fixture every time a wrong claim reaches a draft**, whoever catches it. Record what the gate did wrong, not just what the claim said. The failure mode is the reusable part.

Format:

```
### <short name>
- **Claim as drafted:** <verbatim>
- **Expected verdict:** CONTRADICTED | UNVERIFIED · **Level:** claim | answer
- **Why it fails:** <one line>
- **Rule that must catch it:** <SKILL.md step and rule name>
- **Gate's original failure:** <why the gate let it through>
```

---

### branding-as-business-edge
- **Claim as drafted:** "the Business plan adds your own branding on the studio"
- **Expected verdict:** CONTRADICTED · **Level:** claim
- **Why it fails:** Placing a logo, background, brand colour, or image/text overlay is All plans, in both the studio and the editor.
- **Rule that must catch it:** Step 2, Tier precision.
- **Gate's original failure:** Confirmed the capability exists and stopped there, without confirming the tier.

### teleprompter-as-business-edge
- **Claim as drafted:** "the teleprompter for host and guests is on the Business plan"
- **Expected verdict:** CONTRADICTED · **Level:** claim
- **Why it fails:** The teleprompter is listed on Pro. Business includes it, so it cannot be the Business differentiator.
- **Rule that must catch it:** Step 2, Tier precision.
- **Gate's original failure:** "Business has it" was treated as "Business-only has it". Inclusion is not exclusivity.

### most-of-it-is-on-your-plan
- **Claim as drafted:** "Most of it is already on your plan." (to a free-account lead asking how to get all her content branded)
- **Expected verdict:** CONTRADICTED · **Level:** answer
- **Why it fails:** She cannot publish anything unbranded-by-Riverside on free. The export watermark only lifts on Pro, and the brand kit starts on Pro. Both gates sit between her and the outcome she described; the draft named neither.
- **Rule that must catch it:** Step 1, aggregate and quantifier claims; Step 3, answer-level verdict.
- **Gate's original failure:** Verified each atomic feature line against "Plan: All plans" and never verified the sentence wrapping them. A stack of VERIFIED parts was read as a VERIFIED whole.

### grow-hour-allocation
- **Claim as drafted:** "Grow gives you 20 hours of recording a month"
- **Expected verdict:** UNVERIFIED · **Level:** claim
- **Why it fails:** Two internal sources disagree on tier naming and no source confirms the allocation against the live pricing page.
- **Rule that must catch it:** Step 2, Source conflict; ledger entry under Limits and numbers.
- **Gate's original failure:** A number stated confidently in a skill file was treated as a source. A skill file is an instruction, not evidence.

### shared-account-instead-of-separate-logins
- **Claim as drafted:** "everyone works in one shared account instead of separate logins"
- **Expected verdict:** CONTRADICTED · **Level:** claim
- **Why it fails:** Business team members do each log in as themselves - per-member roles, invite-pending seats, SCIM, and org SSO all assume individual identities. What Business replaces is separate *accounts and licences*, not separate logins.
- **Rule that must catch it:** Step 2, Restatement rule (search the concept in Riverside's vocabulary: workspace, roles, seats, licences) plus Tier precision.
- **Gate's original failure:** The clause is sanctioned wording in `.claude/skills/inbound-demo-reply/SKILL.md` line 492, and a skill file was treated as a source. A skill file is an instruction, not evidence - same failure mode as `grow-hour-allocation`.

### vague-business-nod
- **Claim as drafted:** "there's a good amount on the Business plan that isn't in the self-serve experience"
- **Expected verdict:** UNVERIFIED · **Level:** claim
- **Why it fails:** Asserts a difference without naming it, so nothing is checkable and the lead gets no reason to book.
- **Rule that must catch it:** Step 5, never ship a hedge in place of a fact.
- **Gate's original failure:** Treated vagueness as safety. An unfalsifiable claim is not a passing claim.
