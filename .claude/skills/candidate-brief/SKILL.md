---
name: candidate-brief
description: Generate a Riverside-branded executive candidate brief as a standalone HTML artifact from a hiring assessment writeup and an optional CV/resume file. Produces a competency radar chart (0-5 scale, hoverable, with an accessible table fallback), executive summary, strengths and risks, interview focus areas per interviewer, a validation checklist, and a final recommendation banner, plus an optional collapsible "View Full CV" section built from the resume. Trigger with "build a candidate brief for X", "turn this CV into a hiring brief", "candidate scorecard", "create a competency radar for this candidate", or "/candidate-brief".
---

# Candidate Brief

Turn a candidate assessment (ratings, strengths, risks, recommendation) plus an optional CV/resume into a single self-contained, Riverside-branded HTML artifact: a competency radar chart, an executive summary, strengths and risks, per-interviewer focus areas, a validation checklist, and a final recommendation banner.

This is a **read + generate** workflow. It never writes to HubSpot, monday, or Slack. The only output is the published artifact.

## Inputs and context to load

- Load the `riverside-brand-guidelines` skill for the color palette, logo assets, and typography rules (dark theme, `#7C5CFF` purple accent, Inter font, no em dashes) before writing any HTML.
- Load the `dataviz` skill before touching the radar chart or any other chart on the page; follow its color and interaction guidance even though the reference template already encodes a working chart.
- Read `knowledge/template.html` in this skill: it is the full working scaffold (CSS + SVG radar + JS), built and hardened in a real session. Copy it, don't rewrite it from scratch.
- Read `knowledge/authoring-guide.md` for the placeholder map, the fill rules per section, and the failure modes this skill exists to avoid.
- If a CV/resume file was provided (PDF, docx, etc.), read it in full before filling the CV section. If none was provided, omit that card entirely (see the guide).

## Steps

1. **Gather** - read the assessment writeup and, if present, the CV. Identify: candidate name, role title, recommendation, competency ratings (0-5 each), executive summary, strengths, risks, named interviewers and their focus areas, what's confirmed vs. still open, and the final recommendation (score + verdict + rationale).
2. **Copy the template** - copy `knowledge/template.html` to a scratch path. Do not retype the embedded base64 logos by hand; they must survive byte-for-byte (see the guide's "Never retype base64" rule).
3. **Fill every `<PLACEHOLDER>` token** from the gathered source, following `knowledge/authoring-guide.md` section by section. Repeat the marked repeatable blocks (`.cv-role`, `.item.strength`, `.interviewer-card`, etc.) to fit the actual source; don't pad or invent content to fill a fixed number of slots.
4. **Validate before publishing**: run the logo-decode check from `knowledge/authoring-guide.md` ("Never retype the base64 logo by hand") against the filled file, confirm no em dash (U+2014) characters remain, and confirm div/tag balance. Screenshot-check the layout if you changed any CSS (see the guide's "Layout regressions to re-check" list) rather than assuming a text-only fill can't break layout.
5. **Publish** via the Artifact tool. Pick a distinct favicon; do not reuse the URL of a different candidate's brief (each candidate gets a new artifact unless the user is explicitly updating one already published for this same candidate).

## Constraints

- Ground every section in the source. Do not invent employers, dates, skills, ratings, or open questions that the assessment/CV didn't provide.
- No em dash character anywhere in generated content (Riverside brand rule). Use a comma, colon, period, or "to" for ranges instead.
- If the source gives fewer strengths than risks (or vice versa) or only one interviewer, leave the shorter side shorter. Don't pad either side to match a layout expectation.
- If no CV was supplied, omit the CV card entirely rather than leaving it empty or inventing placeholder content.
- Default to omitting direct contact details (email, phone) from the CV card unless the requester has confirmed the brief's audience should have them (see the guide's "Contact details in the CV card"). Never invent or guess a candidate's contact info.
- Filled-in text can contain characters that are significant in HTML or JS (`&`, `<`, `>`, quotes). Escape them per the guide's "Escaping source-derived text" rather than writing them in raw; the radar chart's tooltip already renders via `textContent`, not `innerHTML`, so don't reintroduce string-interpolated `innerHTML` there.
- The recommendation pill and final banner take a `<RECOMMENDATION_TONE>` class (`hire` / `conditional` / `no-hire`) that must match the actual verdict. Never leave both defaulted to `hire`; a "No hire" or "Hire with reservations" must render in its own color, not green.
- Never mutate a live system. If a downstream request asks to file this onto a monday board or Slack it out, hand off to `/pm-story` or `/slack-agent` rather than doing it inline.

## Output schema

The published artifact, in order:
1. Masthead - candidate name, role, recommendation pill, assessment fit score
2. CV card (omit if no CV was supplied)
3. Competency Assessment - radar chart + table fallback
4. Executive Summary - 1-2 paragraphs + positive tags
5. Strengths & Risks - two-up list
6. Areas to Probe: Final Interview - one card per interviewer
7. What We Know vs. What's Left - confirmed/open checklist
8. Final recommendation banner

Every card must render even if a section has only one item (the CSS collapses to single-column responsively; verified across desktop/tablet/mobile in the reference build).

## Done when

The artifact is published, every placeholder is filled from real source content (no `<PLACEHOLDER>` markers remain), no em dashes remain, the logo renders in both light and dark theme, and the layout has been checked at least once at a narrow viewport (or the user has confirmed they don't need that check).
