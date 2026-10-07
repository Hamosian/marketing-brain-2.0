# Ziff Davis meeting outcomes, February to September 2026 (baseline for the rubric)

Built 2026-09-19 from the SWZD campaign tracker (105 rows, 67 held), HubSpot Pre-Ops on the 153 contacts tagged `meeting_source_cp = ziffdavis` (134 Pre-Ops since February), and the 69 Gong calls Charles Green joined that carry a Spotlight brief. Figures are as of 19 September 2026; re-pull rather than reuse them.

## What a held meeting turned into

| Outcome | Count of 67 held |
|---|---|
| Closed lost at Pre-Op | 27 |
| Still in Follow-Up or active | 15 |
| Promoted to a deal | 9 (10 across all Ziff Pre-Ops: WTax, Inner Circle Consulting, Agile Mind, FirstOntario, Bond Brand Loyalty, Think Publishing, British Board of Agrément, Inflection Point, Kingsley Napley, Fotoware) |
| Won | 5 (WTax $1,130, Inner Circle $1,283, Agile Mind $1,155, Inflection Point $600, British Board of Agrément $1,563) |
| Still at Meeting Booked, meeting long past | 6 (stage hygiene, not outcome) |
| No Pre-Op found | 9 (Thomas International, Carlisle, Kameleoon, Carleton, MG OMD, AJW, Nodor, Fiery, ASM Global): the calendar-sync gap in `preop-data-intelligence`, or a company-name mismatch |

Promoted rate 15%. Win rate 7%. Average won deal about $1,150 a year against $750 per held meeting. The economics only work if the promoted rate roughly doubles, which is why the score targets the next-day label and not the win.

## What did not separate winners from losers

- **Seniority level.** Managers: 46 held, 7 promoted. Directors: 12 held, 2 promoted. Heads, VPs and the one CMO: 8 held, 0 promoted. Level is noise at this sample size.
- **Company size.** 51 to 200: 33 held, 5 promoted. 201 to 500: 13 held, 2. 501 to 1,000: 9 held, 2. 1,000+: 9 held, 0. Under 50: 3 held, 0. Mid-size does slightly better; the enterprise bookings have produced nothing yet.
- **Country.** UK 33 held, 6 promoted. Canada 16 held, 2. US 10 held, 1. Germany 5 held, 0.
- **Industry.** Too fragmented to read: no industry has more than five held meetings.

So the structured fields Ziff already supplies (title, size, country, industry) carry little signal, which is why they are worth 10 of 100 in the rubric and the three discovery answers are worth 80.

## What the promoted briefs had in common (from the Gong briefs)

Every promoted or won call names a **specific existing programme and the tool it runs on**: podcasts and webinars on StreamYard and Wavecast (Think), social clips from existing recordings (FirstOntario), podcasts and webinars in an expanding content strategy (BBA), long-form to short-form repurposing during a brand relaunch (Inflection Point). The prospect could describe what they record before anyone from Riverside spoke. That is Nir's 16 September finding, and the backfill agrees with it.

## What the closed-lost briefs had in common

- A programme that exists but a blocker the first call cannot remove: a locked incumbent (IntegrityNext on Contrast), budget in 2027 (Lumera), a decision deferred to a full review (illumin).
- No programme: a podcast "initiative" (London Chamber), on-site product demos rather than recordings (International Pool and Spa), training content in manual processes (Canada Guaranty).
- Off-fit asks: AI text-to-podcast and auto-generated presentations (Nokia), animations (Smoltek), connectivity (United Airlines).

## Brief availability

Charles began emailing handover documents on 5 August 2026; there are 51 emails with a PDF between then and 17 September (47 unique briefs, 4 duplicate sends). Before August there were no handover emails, so the February to July meetings exist only in Ziff's own documents. The Gmail connector cannot open attachments, so the PDFs were downloaded by Nir on 19 September and read from disk. From 18 September Charles sends the brief in the email body, so no attachment route is needed. All 47 are scored in `data/ziff-scores.csv` and form calibration batch 1 (`rubric.md`).

## Vendor data defects seen in batch 1

- 39 of 47 briefs missing at least one of the three agreed answers; owner and team size are the usual gaps.
- Employee size absent on 5 briefs (Clearwater, Electro Rent, Encircle and two others).
- Implen's brief carries the Metro Wallcoverings prospect's name against Implen's email.
- Two briefs state two different meeting times in the same body.
- Qualtrics' contact email is a personal domain (girotto.com), which is why the LHO Log flagged the company mismatch.
- Two prospects were existing or prior Riverside users (Beat Media, Saskatoon) and the brief did not say so.
- Pre-Op stages are not moved by AEs after the meeting: 23 of 47 still read Meeting Booked weeks after the call. The Gong brief, not the stage, is the next-day evidence.

## Pre-Op stage ids seen on Ziff records

| Pipeline | Meeting Booked | Follow-Up / active | Closed Lost | Promoted |
|---|---|---|---|---|
| US Agency `29354026` | `1033613941` | `69180237` (also `67154602`) | `67154608` | `67154607` |
| EU Agency `89765536` | `1033614704` | `166509139` | `166509143` | `166509142` |
| US Enterprise `29152011` | `1031377048` | `69198923`, `66605110` | `66605113` | |
| EU Enterprise `916013614` | `1397905040` | | `1397905045` | |

Read from the records, not from a stage export. Confirm against `preop-data-intelligence` before using a stage id in a filter.
