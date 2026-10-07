# HubSpot Naming Conventions - Riverside Marketing Ops

> **Based on audit of**: 2,136 lists, ~100 workflows, ~90 marketing emails from Riverside's HubSpot (April 2026)

---

## Table of Contents

1. [Universal Rules](#universal-rules)
2. [List Naming](#list-naming)
3. [Workflow Naming](#workflow-naming)
4. [Marketing Email Naming](#marketing-email-naming)
5. [Language Variants](#language-variants)
6. [Audit Findings Summary](#audit-findings-summary)

---

## Universal Rules

These apply to ALL HubSpot assets - lists, workflows, and marketing emails.

### Rule 1: Category prefix in square brackets is mandatory

Every asset name starts with a bracketed category tag. Workflows already partially use this (about 40% of workflows have bracket prefixes); the goal is 100% adoption.

**Standard prefixes (shared across all asset types):**

| Prefix | Meaning | Use for |
|---|---|---|
| `[MKT]` | Marketing (general) | Cross-motion campaign assets, marketing-owned segments, general send lists |
| `[PLG]` | Self Serve motion (PLG) | Product usage segments, self-serve behavioral assets, freemium/paid-SS audiences |
| `[B2B]` | Business / Enterprise motion | Sales-assisted marketing assets, enterprise audience segments, B2B campaign lists |
| `[BD]` | Business Development (team) | BD team-specific operational assets: signup notifications, rep assignments, outreach lists |
| `[OPS]` | Marketing/Sales Ops | Operational lists, data hygiene, internal reporting |
| `[ICP]` | Ideal Customer Profile | Tier lists, scoring segments |
| `[EXCL]` | Exclusion / Suppression | Do-not-email, competitor, invalid contact lists |
| `[TEST]` | Test / Temporary | Must include an expiry date |
| `[ARCHIVE]` | Deprecated / Legacy | Kept for historical data, no longer active |

> **`[PLG]` vs `[B2B]` vs `[BD]` - how to choose:**
> - **`[PLG]`** = targets or supports the **Self Serve motion** (freemium, paid self-serve, product-led growth)
> - **`[B2B]`** = targets or supports the **Business/Enterprise motion** (sales-assisted, enterprise customers)
> - **`[BD]`** = for **Business Development team operations** (rep routing, signup notifications, sequence assignment)
> - If the audience is "Business" or "Enterprise", use `[B2B]`. If the asset is about how the BD team operates, use `[BD]`.

**Additional prefixes for workflows only:**

| Prefix | Meaning | Examples from current data |
|---|---|---|
| `[Lead Routing]` | Lead assignment and routing | Meeting booked routing, MQL followup |
| `[Property]` | Property sync/update automation | BD Team updates, timestamp stamping |
| `[Sync Data]` | Cross-object data sync | Contact-to-deal copies, association workflows |
| `[CSM]` | Customer Success | CSM assignment, renewal management |
| `[AE Automation]` | Account Executive automation | AI summaries, call scoring |
| `[Pre-Opps]` | Pre-opportunity pipeline | Meeting outcomes, status updates |
| `[Outreach Sync]` | External tool sync | Outreach prospects/companies sync |
| `[Deduplication]` | Data dedup workflows | Company dedup checks |

**Additional prefixes for emails only:**

| Prefix | Meaning | Examples |
|---|---|---|
| `[WF]` | Workflow-dependent email | Emails used inside a specific workflow |
| `[Inbound SDR]` | SDR automation emails | MQL followup emails |
| `[Vendor]` | Partner/vendor automated emails | Meeting completed/no-show vendor notifications |

### Rule 2: Use hyphens as the standard delimiter

Separate name segments with ` - ` (space-hyphen-space). Never use `AND` as a delimiter. Use `+` for combining filter criteria in shorthand.

### Rule 3: Never put person names in asset names

Person names appear in ~8% of lists and ~12% of workflows. These become stale when people change roles.

| Instead of | Write |
|---|---|
| `Notify Gal for every 2000$+ Onboarding meeting is scheduled with Lior` | `[CSM] Notify - High MRR Onboarding Meeting Scheduled` |
| `Renewal Save Opportunity - Escalate to Gal and Jonathan` | `[CSM] Renewal Save Opportunity - Escalate to Management` |
| `[MKT] Sets the "Last Touch Source" property to "Inbound" for contacts owned by Lauren Mitchell` | `[MKT] Set Last Touch Source - Inbound - BD Owner Filter` |
| `Growth Ruben - Matchmaking hosts` | `[MKT] Matchmaking Hosts - Premium + Never Recorded` |

Put the actual person/email in the workflow **description** field, not the name.

### Rule 4: Standardize protection warnings

Use `⛔ LOCKED` as a suffix. Put the reason in the HubSpot description field.

| Instead of | Write |
|---|---|
| `Dont Touch - Contacts with Open Pre-Opp or Deal` | `[OPS] Contacts with Open Pre-Opp or Deal ⛔ LOCKED` |
| `QBD - DONT TOUCH - Contact with open Deal Entity` | `[OPS] QBD - Open Deal Entity Contacts ⛔ LOCKED` |
| `Pre Opps with past intro meetings (DO NOT EDIT - used in deal tags)` | `[OPS] PreOpps - Past Intro Meetings ⛔ LOCKED` |

### Rule 5: Date and version formatting

| Element | Format | Example |
|---|---|---|
| Creation/reference date | `YYYY-MM` | `2025-08` |
| Quarter reference | `YYYY-Q#` | `2025-Q1` |
| Version | `v#` | `v2` |
| Time window | `Last #d` | `Last 30d`, `Last 180d` |
| Test expiry | `Expires YYYY-MM-DD` | `Expires 2025-06-01` |

### Rule 6: Clean up immediately after cloning

Never leave `(cloned)`, `(Clone)`, `(Copy of...)`, auto-generated timestamps, `(probably remove)`, or `To be deleted` in production names. Rename within 24 hours.

---

## List Naming

**Pattern**: `[Category] Description - Qualifier`

**Examples of correct naming:**

| Current (from audit) | Recommended |
|---|---|
| `Paid Self Serve AND Logged in Last 30 Days AND Webinar Intent` | `[PLG] Paid SS - Login Last 30d + Webinar Intent` |
| `BD New Signup notifications - All enrollments` | `[BD] New Signup Notifications - All Enrollments` |
| `Marketing Comms Contact History - Received Freemium Onboarding Email 1` | `[MKT] Comms History - Freemium Onboarding Email 01` |
| `Live product demo #36` | `[MKT] Live Product Demo - Registrants #36` (or archive if legacy) |
| `Steven Bot users in BD companies (cloned)` | `[BD] Bot Users in BD Companies` |
| `[Workflows] - Tue Mar 31 2026 09:33:39 GMT-0500 - Pre-Opp - ...` | `[WF] PreOpp Meeting-to-Deal Association - Initiator` |

**Workflow-dependent lists use the `[WF]` prefix and reference their parent workflow:**

| Pattern | Example |
|---|---|
| `[WF] [Short WF Name] - Enrollment` | `[WF] MQL Onboarding - Enrollment` |
| `[WF] [Short WF Name] - Suppression` | `[WF] Self Serve Winback - Suppression` |
| `[WF] [Short WF Name] - Goal` | `[WF] PLG Upgrade Nurture - Goal` |

---

## Workflow Naming

**Pattern**: `[Category] Object Type Hint - Purpose - v#`

Workflows already have the best adoption of bracket prefixes (~40%). The goal is to standardize what's already working and extend it to the remaining 60%.

### What's working well (keep these patterns):

These prefix patterns from your current workflows are good - standardize on them:

- `[MKT]` - Marketing automation (PLG lifecycle, score generation, affiliate routing)
- `[Lead Routing]` - Lead assignment and meeting routing
- `[Property]` - Property update/sync automation
- `[Sync Data]` / `[Outreach Sync]` - Data sync between objects or systems
- `[Pre-Opps]` - Pre-opportunity pipeline management
- `[CSM]` - Customer success workflows
- `[AE Automation]` / `[CSM Automation]` - Role-specific automation with AI/Gong
- `[Deduplication]` - Data quality

### What needs fixing:

| Current (from audit) | Recommended |
|---|---|
| `Copy Intro Meeting Timestamps on Pre Opp properties (2025 Pre Opp Build)` | `[Pre-Opps] Copy Intro Meeting Timestamps - 2025 Build` |
| `Contact / Company / Deal Original Source` | `[Property] Original Source - Contact + Company + Deal` |
| `Reach out before call - AE` | `[AE Automation] Pre-Call Outreach Notification` |
| `fix contract end date on Company` | `[CSM] Fix Contract End Date - Company` |
| `Associated Company ID deal property update` | `[Sync Data] Company ID - Deal Property Update` |
| `Automated_Self_Serve_Winback_Cancelled_3_Months_V2` | `[MKT] Self Serve Winback - Cancelled 3mo - v2` |
| `👑 Pre-Opp (raw score>17) \| Deal Promotion` | `[Pre-Opps] Deal Promotion - Raw Score 17+` |
| `Set - Pre-Opp Relevant Score (A-F) (cloned)` | `[Pre-Opps] Set Relevant Score A-F - v2` |
| `BD New Signup notifications - Rep Assignments` | `[BD] New Signup - Rep Assignment Routing` |
| `Smartlead Riverside Email Sent` | `[Outreach Sync] Smartlead - Email Sent Logging` |
| `Webinar workflow: B2B YouTube Webinar 2026` | `[B2B] Webinar - YouTube 2026-04` |
| `Workshop workflow: Monetization` | `[MKT] Workshop - Monetization` |
| `NAB Dinner Event 2026 Event workflow` | `[MKT] Event - NAB Dinner 2026` |

### No emojis, pipes, or arrows in workflow names

While `➝` (arrow) characters appear in several workflow names and are visually helpful, they can cause issues in exports, search, and tooling. Use ` to ` or ` > ` instead.

| Instead of | Write |
|---|---|
| `Source Deal ➝ Renewal Deal Association With Labels` | `[Sync Data] Source Deal to Renewal Deal - Association Labels` |
| `Upsell <> Renewall Deal: Delete Upsell Line items from Renewal` | `[CSM Renewals] Upsell to Renewal - Delete Stale Line Items` |

---

## Marketing Email Naming

**Two main patterns based on email type:**

### 1. One-time sends (blasts, newsletters, announcements)

**Pattern**: `[MKT] BLAST - [Topic] - [Audience]`

The existing `BLAST:` prefix is a good instinct - it clearly identifies one-time sends. Standardize the format:

| Current (from audit) | Recommended |
|---|---|
| `BLAST: Webinar Intent - Self Serve Upgrade - Segment 4` | `[MKT] BLAST - Webinar Intent SS Upgrade - Seg 4` |
| `BLAST: March 2026 Business Newsletter` | `[B2B] BLAST - Newsletter Business - 2026-03` |
| `BLAST: March 2026 Freemium Newsletter` | `[MKT] BLAST - Newsletter Freemium - 2026-03` |
| `BLAST: March 2026 Paid Self Serve Newsletter` | `[MKT] BLAST - Newsletter Paid SS - 2026-03` |
| `BLAST: NAB 2026 Invite - Business` | `[B2B] BLAST - NAB 2026 Invite` |
| `BLAST: Podcast Expert Directory - Not Opened` | `[MKT] BLAST - Podcast Expert Directory - Resend Unopened` |
| `Blast: Workshop: Monetization (invite)` | `[MKT] BLAST - Workshop Monetization - Invite` |
| `March 30 2026 Community Newsletter 014 - Blast 2026` | `[MKT] BLAST - Community Newsletter #014 - 2026-03` |
| `To be deleted` | Delete it or rename to `[TEST] [Purpose] - Expires YYYY-MM-DD` |

### 2. Automated / workflow emails

**Pattern**: `[WF] [Short WF Name] - ##. [Description]`

The existing `EM-YYYY-MM` prefix is a strong pattern for lifecycle/onboarding emails. Keep it for those sequences and extend `[WF]` for all other workflow emails.

| Current (from audit) | Recommended |
|---|---|
| `EM-2024-11 Paid Welcome 2b. - Monthly Demo Webinar Invite` | `EM-2024-11 Paid Welcome - 2b. Monthly Demo Webinar Invite` (keep - this pattern works) |
| `EM-2023-01 Trial Signup 1e. Need help with your setup? We've got you covered - NEW Design 238661715; 238662709` | `EM-2023-01 Trial Signup - 1e. Setup Help` (drop internal IDs from name) |
| `[Inbound SDR] Automated email #2 to MQL without Meeting No owner (de)` | `[Inbound SDR] MQL No Meeting - Email 02 - No Owner (de)` |
| `[Lead Routing] Enterprise Email 1: No Show Workflow` | `[Lead Routing] No Show - Enterprise Email 01` |
| `ZiffDavis - Vendors automatic Meeting Completed` | `[Vendor] ZiffDavis - Meeting Completed` |
| `Pursuit - Vendors automatic No-Show` | `[Vendor] Pursuit - No Show` |
| `Live Streaming Onboarding - email 5 (fr)` | `[WF] Live Streaming Onboarding - 05. (fr)` |

### 3. Event/webinar emails

**Pattern**: `[MKT] [Event Type] - [Event Name] - [Stage]`

| Current (from audit) | Recommended |
|---|---|
| `Webinar: YouTube (registration)` | `[B2B] Webinar - YouTube 2026-04 - Registration` |
| `Webinar: B2B YouTube 04/26 (first reminder)` | `[B2B] Webinar - YouTube 2026-04 - Reminder 1` |
| `Workshop: Monetization (second reminder)` | `[MKT] Workshop - Monetization - Reminder 2` |
| `Workshop: Monetization (postpone)` | `[MKT] Workshop - Monetization - Postpone Notice` |
| `NAB Dinner Event 2026 - Registration Confirmation` | `[MKT] Event - NAB Dinner 2026 - Reg Confirmation` |

---

## Language Variants

Localized emails currently use a `(lang)` suffix inconsistently - sometimes `(fr)`, sometimes `(es)`, sometimes embedded in the name. Standardize:

**Pattern**: Append ` (xx)` as the very last element, using ISO 639-1 codes.

| Language | Code | Example |
|---|---|---|
| English (default) | Omit - English is the default, no suffix needed | `EM-2024-11 Paid Welcome - 2b. Demo Webinar` |
| French | `(fr)` | `EM-2024-11 Paid Welcome - 2b. Demo Webinar (fr)` |
| Spanish | `(es)` | `EM-2024-11 Paid Welcome - 2b. Demo Webinar (es)` |
| Portuguese | `(pt)` | `EM-2024-11 Paid Welcome - 2b. Demo Webinar (pt)` |
| German | `(de)` | `EM-2024-11 Paid Welcome - 2b. Demo Webinar (de)` |

Never mix languages and `(Clone)` - if cloning for localization, rename immediately.

---

## Audit Findings Summary

### Lists (2,136 total)
| Issue | Count/Severity | Fix |
|---|---|---|
| No bracket prefix | ~80% of lists | Add appropriate prefix |
| `AND` used as delimiter | ~10% | Replace with `+` shorthand |
| Person names in names | 4+ found | Move to ownership metadata |
| "Don't touch" in 5+ formats | 5 variants | Standardize to `⛔ LOCKED` |
| Auto-generated timestamps | 1+ found | Rename immediately |
| `(cloned)` / `(probably remove)` | 2+ found | Clean up or archive |
| Inconsistent date formats | 4+ formats | Standardize to `YYYY-MM` |
| Sequential numbers without context | `Live product demo #11-#38` | Add context or archive |

### Workflows (~100 sampled)
| Issue | Count/Severity | Fix |
|---|---|---|
| No bracket prefix | ~60% of workflows | Add appropriate prefix |
| Person names in names/descriptions | ~12% | Move to description field |
| `(cloned)` not cleaned up | 1+ found | Rename with `v#` |
| Emoji in names | 1 found (`👑`) | Remove |
| Arrow characters (`➝`, `<>`) | 5+ found | Use `to` or `>` |
| Informal/ad-hoc names | ~5% (`fix contract end date`) | Formalize |
| Underscore naming | 1 found | Use hyphens |
| Internal IDs in names | 0 in workflows | Good - maintain |

### Marketing Emails (~90 sampled)
| Issue | Count/Severity | Fix |
|---|---|---|
| `BLAST:` vs `Blast:` case inconsistency | 2 variants | Standardize to `[MKT] BLAST -` |
| Internal HubSpot IDs in names | ~10 emails | Remove from name |
| `(Clone)` not cleaned up | 5+ found | Rename |
| `To be deleted` placeholder | 1 found | Delete or rename |
| No prefix on many automated emails | ~30% | Add `[WF]` or `EM-YYYY-MM` |
| Vendor names without `[Vendor]` prefix | 4+ found | Add prefix |
| Inconsistent event email naming | Multiple patterns | Standardize to `[MKT] [Type] - [Name] - [Stage]` |
