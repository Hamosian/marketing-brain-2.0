<!-- last-reviewed: 2026-09-24 (moved from references/ into /onboarding-doc-builder; build steps now point to the shared scripts) -->
# Onboarding playbook: a new hire's onboarding doc

The reference `/onboarding-doc-builder` loads before drafting: what goes in each section, where
in the repo it comes from, and the rules the doc has to follow. The skill's `SKILL.md` holds the
steps; this file holds the substance. Distilled from
building Jonathan Ydov's (Web Developer, Marketing Website, starting 2026-09-27) with Jonathan
Galili and Hanan Amos on 2026-09-23, then routing Jonathan Galili's manual edits back into the
repo (PR #388). The finished example is the reference:
<https://docs.google.com/document/d/1784KKtEBrMuejeWRW0AEZtrfc9dGtEGT/edit>.

The shape comes from a CRM Operations onboarding doc Jonathan Galili wrote in 2020 at a previous
company: a personal welcome letter from the manager, then phased "Know the X" sections, each a
short intro plus a To do list. It works because a new hire can walk it top to bottom in their
first month.

## Settle these with the requester first

- **Feasibility and a restated ask.** The repo covers most of it (roster, systems, channels,
  access owners). Name the gaps up front: people outside Marketing, access owners nobody has
  recorded, facts that only live in Slack.
- **Who signs it, and in whose voice.** Usually the manager. Load that person's recorded style
  before drafting. Hanan's is in `.claude/skills/hanan-chief-of-staff/knowledge/hanan-preferences.md`
  (no exclamation marks, no em or en dashes, no decorative emoji, sentence-case headings), so
  the energy has to come from wording, not punctuation.
- **Format.** A branded .docx from the builder, then a Google Doc (see Build).
- **Time frame.** The first month week by week, plus a draft for days 31 to 90 that the hire
  brings their own version of by the end of week 4 and agrees with the manager in their 1:1.
- **A culture section.** Yes, but only from material that still holds (see Rules).

## Structure and where each part comes from

| Section | What it holds | Source |
|---------|---------------|--------|
| Cover | A screenshot of the live riverside.com hero, then "<Name>, Welcome to the <team> team at Riverside." | Headless Chrome (Build) |
| Welcome letter | What the team owns (bold-led bullets), why the role matters, the main goal, a short sign-off | The role's `systems/owned/*.md`; the functional split in `references/team.md` |
| Who we are | What Riverside is, framed as the few things our pages have to explain; department, sub-org and team goals, each named by what it is measured on; an org chart from the VP down to the hire; the team; the wider sub-org | `references/product/`, `systems/reference/marketing-operating-model.md`, `references/team.md` |
| Prerequisites | An access checklist (what, why, who grants it) and the Slack channels to join | `references/other_teams.md` → Access provisioning; `references/slack.md` |
| Phase 1: Know the people | The intro table: who, team, title, duration and week | `references/team.md`, `references/other_teams.md`, checked in HiBob |
| Phases 2 to 6 | Know Riverside, the numbers, the product, our customers, our competitors | `references/messaging/`; Omni and Rivermind; the Help Center reference; `/are-we-really-different` |
| Phase 7 | The role's systems and practices: how it is built, how work flows, the gotchas, the skills that help | The role's `systems/owned/*.md` |
| Phase 8 | Role and responsibilities, the handover, the references the role relies on | |
| First 90 days | A week-by-week table, then the days 31 to 90 draft | |
| Culture and ways of working | How we work, feedback, meetings, working hours | Working pattern and locations in `references/team.md` |
| Documents, sign-off, AI diligence statement | | `diligence()` in the builder |

## Rules

- **Current sources only.** Never carry a link, name or figure over from an older onboarding
  doc. Re-derive each from the repo and re-verify every link (Drive metadata for docs, a live
  fetch for pages). Data and analytics links go to Omni dashboards and Rivermind only, and the
  doc points to numbers rather than quoting them.
- **Intros are 30 minutes at most.** The requester curates the list: in the 2026-09 edit they
  cut the Creative Directors, all of Creator Marketing but its head, and Social, so propose and
  expect cuts.
- **One row per meeting.** When an intro doubles as a working session, name the topic in the
  table and have the later phase say "In your intro with X, ...". "Schedule ..." means book it;
  "In our 1:1, ..." is an agenda item for the manager's weekly 1:1.
- **Check every name and title in HiBob** (the HiBob note in `references/team.md`). A manager's
  correction outranks HiBob, which trails reorgs. Note who works outside Israel, and any holiday
  in week 1 (Sukkot fell on Ydov's).
- **Don't transplant a previous manager's personal notes** ("I'll always have your back") into
  another person's letter. What still holds from Abel's playbook for the Marketing org goes in as
  "How we work": start from the objective; execute with excellence and urgency; own it (share
  status, flag a blocker early with what you need to clear it); weigh effort against upside;
  figure it out; question habits.
- **Run it through the content pipeline.** Another person reads it, so it gets `/de-ai` and
  then `/critique` as a separate agent pass, not the author's self-score. The independent pass
  caught a wrong claim about Webflow deploys that the author had missed.
- **Read the role's working Slack channels for what the repo lacks.** In 2026-09, `#marketing-dev`
  held the Groundcover to PagerDuty monitoring and the `/new/*` Lovable route, and neither was
  documented anywhere. Put such a fact in the doc and route it into the repo (Step 6).
- **Mark what you cannot confirm, don't guess it.** Write "(to confirm)" in the doc and list it
  for the manager in chat. When a detail lacks context, such as a migration's status, leave it
  out. Drafting history never goes in the doc (`CLAUDE.md`).

## Build notes

The steps are in `SKILL.md`. What the steps do not say:

- **Builder helpers:** `h1` for each section (a real Heading 1 with the accent bar), `h2`/`h3`
  inside it, `rich` and parts-list `bullets` for bold labels and working links, `picture` for
  images, `table(..., widths=[0.4, ...], check_col=True)` for the access checklist, `callout`
  for the "this part is a draft" box, `label_para` for the days 31 to 60 and 61 to 90 lines.
  `scripts/build_skeleton.py` wires all of it to one spec.
- **Cover:** `scripts/web_screenshot.sh https://riverside.com/ <cover>.jpg` (repo root). The
  hero at 1920x760 reads well at 6.5in.
- **Org chart:** edit the `ORG` object in `knowledge/orgchart_template.html` (the chain from the
  VP to the hire in dark, context dimmed, the team in accent, the hire in purple, agencies and
  contractors dashed), render it with `scripts/web_screenshot.sh <file> <out>.png 1600 560 2`,
  then crop the empty margin with `sips -c <h> <w> --cropOffset <y> <x>` so the chart text stays
  legible at page width.
- **Pagination:** section titles start a new page only where the structure table puts one (the
  letter, Prerequisites, the first 90 days). A short closing list uses `keep_together=True`.

## After the manager edits it

- The diff (`scripts/docx_diff.py`) is exact; the judgement is in classifying each change. A
  changed access owner, a new channel, a renamed team or a new tool is a repo fact. A reworded
  sentence, a cut intro or an added example is doc-only.
- A deleted line is ambiguous: it can mean "wrong" or only "not for this doc". Ask before
  recording it (in 2026-09 a removed CDN-migration line meant "not enough context to state",
  not "finished").
