---
name: onboarding-doc-builder
description: >-
  Writes a new hire's onboarding document: a Riverside-branded .docx in the manager's voice
  (then a Google Doc once approved) with a welcome letter, an access checklist naming who
  grants each tool, the people to meet, phased To dos, a week-by-week first month and a days
  31 to 90 draft, built from our own docs and checked in HiBob. Afterwards it diffs the
  manager's edits to the doc and routes the facts into the knowledge base. Use when someone
  asks to write, create or update an onboarding doc, welcome doc or first-90-days plan for a
  person joining, or says "prepare onboarding for our new X starting on Y" or "here is an
  example onboarding doc, make one for Z". NOT for talking a new joiner through the team in
  chat (that is team-intro) and NOT for a hiring assessment (candidate-brief).
---

# Onboarding Doc Builder

Turn "someone joins on Sunday" into the document their manager sends before day 1: personal,
specific to the role, and built only from what the repo knows now. **Load
`knowledge/playbook.md` first**: it holds the section structure, the repo source for each
section, and the rules. This file holds the steps.

## Step 1: Feasibility, then the interview

Lead with a feasibility verdict and a one-paragraph restatement of the ask: what the repo
covers, what it does not (people outside Marketing, unrecorded access owners, facts that live
only in Slack), and any access blocker. Then ask with `AskUserQuestion`, batched (up to four
cards), only what the request leaves open:

- **Signer and voice:** the manager (default), the person handing the role over, or both.
- **Format:** .docx plus a Google Doc once approved (default), .docx only, or Google Doc only.
- **Time frame:** the first month by week plus a days 31 to 90 draft the hire shapes (default).
- **Culture section:** included from current material (default), or left out.

If a reference doc is attached, read it for shape and tone only, never for facts or links. If
a card goes unanswered, use the default and say so.

## Step 2: Gather, from the repo and live checks only

Follow the playbook's source map. Load `references/team.md`, `references/other_teams.md`
(Access provisioning), `references/slack.md`, and the `systems/owned/*.md` docs for the role.
Load the signer's recorded style if one exists (for Hanan, his `hanan-chief-of-staff`
preferences). Then:

- **Verify people in HiBob** through Claude in Chrome (the HiBob note in `references/team.md`): name,
  title, department, site. Read nothing else.
- **Verify every link** (Drive metadata for docs, a live fetch for pages). Data links go to
  Omni dashboards and Rivermind only.
- **Read the role's working Slack channels** for facts the repo lacks, and note each one for
  Step 6.

Keep large reads in the scratchpad, not the context.

## Step 3: Draft and build

1. Invoke `/riverside-brand-guidelines` before drafting.
2. Copy this skill's `scripts/build_skeleton.py` to the scratchpad and fill its `SPEC`, section by section,
   in the signer's voice. Write "(to confirm)" for anything unverified, and never guess.
3. Cover: `scripts/web_screenshot.sh https://riverside.com/ <cover>.jpg` (repo root). Org
   chart: edit `knowledge/orgchart_template.html`, render it at scale 2 with the same script,
   and crop it (playbook, Build notes).
4. Build with `--draft` while filling; build the final file without it, which refuses while
   any `[Replace: ...]` marker or an em or en dash is left.

## Step 4: Review before anyone sees it

- **Content pipeline:** run `/de-ai` inline, then `/critique` as a **separate agent pass** on
  the extracted text. Its verdict is binding: revise on REVISE and re-run, for at most two
  rounds per body of content, plus one focused round on anything substantially new.
- **Render and look:** `scripts/render_docx.sh <file>.docx` and read every page. Fix stranded
  headings, orphaned list items and table widths. If Pages cannot export (exit 4), read the
  Quick Look page and say the rest was verified structurally only.
- **Check:** every intro is 30 minutes at most and appears once; "Schedule" means book it and
  "In our 1:1" is an agenda item; no link or figure carried over from an older doc; the
  signer's style rules hold (for example, no exclamation marks for Hanan).

## Step 5: Deliver

Send the .docx (`SendUserFile`, display `attach`) and the PDF preview. Reply with the schema
below. Put nothing in Drive until the requester says yes, then copy the file into the synced
Drive folder (`~/Library/CloudStorage/GoogleDrive-<email>/My Drive/`). If there is none, use the
Drive connector's `create_file` after `slim()`.

## Step 6: Pick up the manager's edits

When the manager edits the doc and hands it back:

1. Diff it: `python3 scripts/docx_diff.py <sent>.docx <edited>.docx` (repo root), reading the
   edited file from the synced Drive folder, not Drive's text export.
2. Classify each change as doc only or repo fact (playbook, After the manager edits it), and
   add the Slack facts noted in Step 2.
3. Ask about ambiguous removals with `AskUserQuestion` before recording anything.
4. Route the facts per `CLAUDE.md` Knowledge Routing on a branch, show the diff, run
   `bash scripts/preflight.sh`, and open the PR only on an explicit go.

## Constraints

- **Grounding:** every name, title, owner, channel and link comes from the repo, HiBob or a
  live check made this run. A figure is a pointer to a dashboard, never a number in the doc.
- **Gates:** Drive, a repo PR, and any Slack message each need an explicit yes. This skill
  sends nothing to the new hire.
- **Fallbacks:** HiBob unreachable: use Slack profile titles and say so. Person not found: write
  "(to confirm)". Pages unavailable: Quick Look page 1, plus structural checks, and say so. A
  link that will not resolve: leave it out.
- **The doc describes the role, not its drafting.** Revision history, corrections and how the
  research went stay in chat (`CLAUDE.md`).

## Output schema (chat reply at delivery)

```
Built: <file name>, <pages> pages. <one line on what it covers>
To confirm with <signer>: numbered list, or "None"
Doc-only notes: bullets, or "None"
Next step: the Drive question, or "Waiting for your edits"
```

## Done when

The .docx and preview are delivered, every page has been looked at, `/critique` returned SHIP,
and the "to confirm" list is with the requester. After the manager's edits: every fact is
routed, and its PR is open or merged.

## Example

Jonathan Ydov, Web Developer, Marketing Website (2026-09-23): a 16-page doc signed by Hanan
Amos, built from a 2020 CRM Ops template, then refined across three rounds of manager feedback.
The diff of the manager's edits fed PR #388. The finished doc:
<https://docs.google.com/document/d/1784KKtEBrMuejeWRW0AEZtrfc9dGtEGT/edit>.
