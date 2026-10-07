---
name: launch-webinar
description: >
  End-to-end webinar setup that anyone with repo access can run. Give it a Riverside
  webinar registration link (or a bare 24-hex event ID) plus the date and time, subject
  and guest. It resolves the event from Riverside's public registration data, checks the
  time against what the requestor gave, drafts the landing page and email copy in
  Kendall's voice, shows one plan, and on your go-ahead dispatches the Webinar Launch
  GitHub Action (registration form, intake list, three emails carrying the drafted copy,
  the reminder workflow always disabled, follow-up lists), then drafts the Webflow landing
  page from the Webinars CMS template. Nothing is published by an agent.
  Trigger on: "launch a webinar", "set up a webinar", "new webinar", "webinar autopilot",
  or any riverside.com/webinar/registration/ link pasted into chat.
---

# Launch Webinar

One request, one plan, one yes. The human creates the event in Riverside Studio (no API
exists for that) and hands over the link and three facts about it. Everything downstream
is this skill's job, up to the publish buttons, which stay human.

## How this runs

Two halves, run from two places, on purpose:

- **HubSpot** (form, intake list, emails, workflow, lists) runs in the **Webinar Launch**
  GitHub Action ([`.github/workflows/webinar-launch.yml`](../../../.github/workflows/webinar-launch.yml)).
  The credentials are repo secrets, so every collaborator can launch a webinar without a
  local `.env`, and the job commits the config entry back to `main` itself.
- **Webflow** (the landing page) runs in your own Claude session through the Webflow MCP,
  via `/page-build`. It needs the HubSpot form the Action creates, so it comes second.

You need `gh` authenticated against `riversidefm/marketing-brain` and the Webflow MCP
connected. You do **not** need Node, a `.env`, or HubSpot access of your own. Never copy a
credentials file between worktrees; that pattern is retired.

## Flow

1. **Get the inputs.** Required:

   | Input | Why |
   |---|---|
   | Registration link (or event ID) from Riverside Studio | Identifies the event |
   | Date and start time, with timezone | Cross-checked against Riverside in step 2 |
   | Subject: what the session covers | Riverside holds only a title; the copy needs the topic |
   | Guest: name and role | Landing page speaker and the copy's guest line |

   Optional: guest bio, headshot and LinkedIn; the **shared studio audience link** (the
   fallback join link); landing page copy to use verbatim; a thumbnail image; workshop vs
   webinar.

   If anything required is missing, **name exactly the missing items in one message and
   wait.** Do not resolve, draft or plan around a gap. Ask about the shared studio link in
   the same message, as optional: without it, a reminder sent to someone whose personal
   link has not synced yet carries an empty join button.

2. **Resolve the event and check the time.** Riverside's `publicWebinarRegistrationData`
   GraphQL is unauthenticated:

   ```
   curl -s https://riverside.com/graphql -H 'Content-Type: application/json' \
     -d '{"query":"query { publicWebinarRegistrationData(eventId: \"<24-hex>\") { title description hostedBy startDate endDate language } }"}'
   ```

   For a registration link the event ID is base64 JSON inside the URL path, not plain
   text; decode it the way `scripts/add-webinar.js` does (`parseInput`).

   Convert the requestor's date and time to ISO 8601 and compare it with `startDate`.
   **If they differ, stop.** Show both and ask which is right; if Riverside is wrong, the
   event gets fixed in Studio first. Never pick one. The ISO value goes to the Action as
   `expected_start`, which fails the run on the same mismatch, so the check holds even if
   this step is skipped.

   Check the title against Kendall's format (`/riverside-event-copy`, Output 1). If it needs
   changing, it changes **on the Riverside event, before the build**: the emails, the HubSpot
   records and the `webinar_name` tracking property are all named from it. The title this
   lookup returns is the **registration form's title field** in Studio, not the event title,
   so the rename goes there; re-run the lookup and confirm it before building. Intake follows
   a rename only while nothing is built, and stops with `Title mismatch` after that.

3. **Draft the copy.** Run `/riverside-event-copy` with the inputs. It returns a review
   render and a copy file (`webinar-copy-<eventId>.json`, in the scratchpad) and runs its own
   quality pass: product claims through `/demo-reply-fact-check`, then `/de-ai`, then
   `/critique`. **The human approves the review render before anything is built.** A change
   request goes back through the skill, not into the JSON by hand.

4. **Show one plan and get one yes.** In plain language: title, host and guest, start and
   end in the portal timezone, the derived reminder times (day-before 10:00, day-of two
   hours before start), the **display time zone** the page and emails use (New York unless
   the audience is outside the US), the copy that was approved, whether a shared studio link is set,
   and what will be created: form, intake list, three emails as drafts with the approved
   copy, three lists, then the landing page as a Webflow draft. These are defaults, not
   decisions; invite the human to correct any line. Flag it explicitly if the event starts
   in the past or within 24 hours, because the reminder schedule will be wrong.

5. **Dry run first.** Dispatch with `mode=plan`; nothing is written. Its log prints each
   email's subject, preheader, button and word count, so it doubles as the copy check.

   ```bash
   gh workflow run webinar-launch.yml -f event="<link-or-id>" -f mode=plan -f expected_start="<ISO>" -f join_link_fallback="<shared studio link, or omit>" -f email_copy="$(node -e 'process.stdout.write(Buffer.from(JSON.stringify(require(process.argv[1]).emailCopy)).toString("base64"))' /absolute/path/to/webinar-copy-<eventId>.json)"
   ```

   Then follow the run (`gh run watch`) and show the human the output.

6. **Build, on the human's explicit go-ahead.** Same command with `mode=create`. The two
   build modes are not the same thing with one extra step, so say which one you are
   running and why:

   - `mode=create` builds the form, the three emails as **drafts carrying the approved
     copy**, the reminder workflow (**disabled**, pointing at the draft emails), and the
     three lists. HubSpot accepts a workflow on draft emails (verified 2026-10-06).
   - `mode=publish` publishes the emails; the workflow already exists and is reused. The
     emails must be published **before** anyone turns the workflow on, so a webinar
     launched with `mode=create` needs a `mode=publish` run before it can send anything.

   Publishing sends nothing on its own: the emails are AUTOMATED type and only go out
   through the workflow, which is always created disabled.

   **Redrafted copy** is applied by re-running `mode=create` with the new `email_copy`. It
   updates drafts only. A published email is never rewritten, and a draft someone edited in
   HubSpot since the last update is skipped with a `copy NOT updated` line in the log;
   `force_copy=true` overwrites those edits, and only on the human's word.

7. **Draft the landing page.** Once the `create` run has committed the config entry, read
   the new form's GUID from `main`, not from the run log:

   ```bash
   git fetch origin main && git show origin/main:tools/webinar-automation/config/webinars.json | node -e 'let d="";process.stdin.on("data",c=>d+=c).on("end",()=>{const e=JSON.parse(d).find(x=>x.riversideEventId===process.argv[1]);console.log(e?e.hubspotFormId:"NOT FOUND")})' <eventId>
   ```

   A value starting with `TODO`, or `NOT FOUND`, means the form does not exist yet: stop
   and say so. Otherwise run `/page-build` with page type **Webinar landing page (CMS
   item)**, handing it the copy file's `landingPage`, the event start, the guest, the form
   GUID and any thumbnail. Its registry profile owns the field map, and it confirms before
   each Webflow write.

8. **Hand back the gates.** The run's job summary is addressed to whoever dispatched it,
   and the same person owns the follow-through. Say it out loud rather than assuming the
   summary gets read:
   - Preview the landing page draft in the Webflow Designer, then publish the Webinars item
     (and the guest's Speaker item, if `/page-build` created one) yourself. `/page-build`
     names the exact publish.
   - QA the three emails, including a test send of a reminder to a contact with no personal
     join link.
   - Re-run with `mode=publish`, then turn the workflow on in the HubSpot UI. Until someone
     flips it, the webinar sends nothing.

## Hard rules

- **A flow is never enabled by a machine.** It is created disabled every time. That gate is
  the only thing between "built" and "sending", and it stays human.
- **Nothing on the website is published by an agent.** The landing page is a CMS draft
  until a person publishes it (`CLAUDE.md`, "Publishing a website is human-only").
- `mode=publish` needs the human's explicit go-ahead on the step 4 plan, and the plan must
  say that publishing is included.
- **No build from unapproved copy.** The copy that reaches `email_copy` is the copy the human
  approved in step 3, unchanged.
- **The page and the emails carry the Riverside event title.** A new title is set in Studio
  (the registration form's title field) before the build, never only on the page.
- Re-runs are safe. Intake is keyed by event ID; the form and intake list reconcile by name
  before creating; the orchestrator reuses anything already recorded under `created.*`.
- If the Action fails, read the run log and say what broke in plain language. A `403
  Event does not belong to this account` from Riverside means the API key is scoped to a
  different Riverside account than the one hosting the event; that is a credentials
  problem for Jonathan Galili or the CSM, not something to retry. A `Start time mismatch`
  goes back to the requestor (step 2). An `emailCopy ... is invalid` goes back to
  `/riverside-event-copy`.
- **Overlapping audiences.** The `webinar_name` property holds only the MOST RECENT
  webinar, so a contact who attends webinar B drops out of webinar A's dynamic lists. Until
  per-event tracking lands, snapshot a webinar's lists to static lists after it ends if the
  team needs durable audiences.

## Running the scripts directly

Only for debugging, and only with credentials you already hold. From
`tools/webinar-automation/`, each script takes an event ID or the config's `eventStem`:

```
node scripts/add-webinar.js "<link-or-id>" [--expect-start <ISO>] [--copy-file <path>] [--join-fallback <url>]
node scripts/ensure-hubspot-intake.js "<id>" --create # registration form + intake list
node scripts/new-webinar.js "<id>" --create [--force-copy]  # template, emails, flow, lists
node scripts/test-email-copy.js                       # offline tests, no token needed
```

Until the repo secret exists, this local path is how a launch runs (first used 2026-10-06).
The person holding the token writes it into `tools/webinar-automation/.env` from their own
terminal, so it never passes through chat or an agent's output, and the file is deleted
after the run. Write the file from the same terminal tab the token was read into: an
exported variable is invisible to a `!` command in the chat and to any new tab, which is
where every agent-started command runs, so a check from there sees an empty token and
HubSpot answers 401. A paste into a silent `read -rs` prompt can capture arrow keys and repeated
pastes as escape codes; before any write, check the token is a single `pat-` value and that
`account-info/v3/details` returns portal `9154210`.

Never `source` or `eval` the `.env` file; that executes it as shell code. The scripts load
it themselves via `scripts/load-env.js` (literal KEY=VALUE parsing), and values already in
the environment win, which is how the Action injects secrets.

## Source of truth

- [`tools/webinar-automation/webinar-hubspot-agent-scope.md`](../../../tools/webinar-automation/webinar-hubspot-agent-scope.md) - every verified API recipe and limitation.
- [`tools/webinar-automation/docs/github-actions-setup.md`](../../../tools/webinar-automation/docs/github-actions-setup.md) - the repo secrets this depends on.
- [`systems/owned/webinar-automation.md`](../../../systems/owned/webinar-automation.md) - the system map.
- [`references/page-type-registry.md`](../../../references/page-type-registry.md) - the Webinar landing page profile `/page-build` follows.
