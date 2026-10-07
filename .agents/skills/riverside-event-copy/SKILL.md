---
name: riverside-event-copy
description: >
  Drafts a Riverside webinar or community workshop in Kendall Breitman's voice (Head of
  Community): the Webinars CMS fields (title, preview text, page body) and the three
  automated webinar emails (registration confirmation, day-before reminder, day-of
  reminder), in the slots the webinar pipeline fills. Stage 1 for webinar writing; de-ai
  and critique run after it. Called by /launch-webinar, or directly to draft or redo a
  webinar's page text or reminder emails. Trigger on "write the webinar copy", "draft the
  workshop emails", "redo the webinar reminder email", "Kendall's event emails". NOT the
  webinar setup itself (launch-webinar), NOT a general marketing page (page-cro), NOT
  prospect email (inbound-demo-reply).
---

# Riverside Event Copy

Adapted from the `riverside-event-copy` skill Kendall Breitman (Head of Community) wrote
for her own events. Her voice rules and email structures are kept. What changed is where
the copy goes: instead of a chat answer to paste by hand, it lands as fields the webinar
pipeline writes into Webflow and HubSpot.

## What it produces

| Output | Lands in |
|---|---|
| Title | Webinars CMS item `name` (and it must equal the Riverside event title, see Output 1) |
| Preview text | Webinars CMS item `description` |
| Landing page body | Webinars CMS item `content` (rich text) |
| Registration confirmation | HubSpot email, role `registration` (sent on sign-up) |
| Day-before reminder | HubSpot email, role `firstReminder` (10:00 ET the day before) |
| Day-of reminder | HubSpot email, role `secondReminder` (two hours before start) |

No invite email: the pipeline builds only these three, and nobody needs a fourth.
No .ics file and no calendar widget: the pipeline computes the add-to-calendar links from
the event schedule and drops them into the placeholders below.

## Inputs

From the `/launch-webinar` intake. When this skill is called directly and a required input
is missing, ask for all the missing ones in one message before drafting anything.

**Required**
1. **Event title**, as it stands on the Riverside event.
2. **Subject**: what the session covers.
3. **Guest**: name and role (company or credential). A bio line is optional and helps P3.
4. **Date and start time**, with timezone.
5. **Format**: workshop or webinar. Default to webinar unless the requestor or the title
   says workshop.

**Optional**
- **Landing page copy.** If the requestor provides it, use it **verbatim**: same phrasing,
  same bullets. Do not rewrite or improve it, and pull the email bullets from it instead of
  writing new ones.
- Key takeaways, who it's for, tone notes.

**Not needed: a join link.** Each registrant gets a personal join link through
`[[JOIN_URL]]`, and the shared studio link, if the requestor gave one, is the pipeline's
fallback. Kendall's original asked for the link before anything else; that step is gone.

## Kendall's voice

The single most important rule: Kendall doesn't write like a marketer. She writes like **a
creator talking to other creators**.

It should feel like *"I found something useful and thought you'd want to know about it."*
Not *"Here is an event we are promoting."* Every piece reads like Kendall emailing a creator
friend.

**Always**
- Lead with the problem or the outcome, never with the guest's name or bio.
- Be specific over vague.
- Use "you," "we," "us."
- Keep paragraphs short: 2-3 sentences at most.
- Fragments are welcome.

**Never**
- "Join us for...", "Don't miss...", "Exciting opportunity..."
- Marketing jargon, buzzwords, exaggerated claims.
- Em dashes or en dashes. Use "and", a comma, a colon or a full stop instead. (The
  pipeline rejects copy that contains either.)
- Emojis.

## Times

- **Pick the display time zone first.** New York time is the default, because Kendall's
  community is mostly US creators. When the audience is outside the US (a regional or
  non-English webinar, or an internal Riverside session), show the time zone the requestor
  gave instead, labelled as a GMT offset (`GMT+3`). If it is unclear which applies, ask.
  `/launch-webinar` names the choice in its plan, and every email and the page use the one
  zone.
- **Never hardcode the label.** New York is on EDT from the second Sunday of March to the
  first Sunday of November and on EST the rest of the year, and other zones shift too
  (Israel moves from GMT+3 to GMT+2 in late October). Compute the label, the clock time
  and the day of the week with code, passing the zone's IANA name:

  ```bash
  node -e 'const [iso,tz]=process.argv.slice(1); const ny=tz==="America/New_York"; console.log(new Intl.DateTimeFormat("en-US",{timeZone:tz,weekday:"long",month:"long",day:"numeric",hour:"numeric",minute:"2-digit",timeZoneName:ny?"short":"shortOffset"}).format(new Date(iso)))' 2026-10-22T16:00:00Z America/New_York
  ```

- Use the current year unless the input names another one. Never assume a past year.
- Emails say `12:00 PM EDT` (or `11:00 AM GMT+3`). The CMS item's `hour` field takes the
  same time in 24-hour form (`12:00`), and `time-zone` takes the same label (`page-build`
  sets both, from the same computation).

## Output 1: Title

The **Riverside event title is the title.** The emails, the HubSpot records and the
webinar's tracking property are all named from it, so a page title that differs from it
splits one webinar into two names.

Check it against Kendall's format:
- **Workshops:** `Community Workshop: [Action-Oriented Outcome]`
- **Webinars:** stands on its own, no required prefix.
- The topic part is short (4-6 words), clear, outcome-driven, action-oriented.

If it meets the format, use it as is. If it falls short, propose 2-3 options and stop: the
chosen title has to be set on the Riverside event in Studio **before** the build runs, in the
registration form's title field (that is the title the pipeline reads, not the event title).
Never put a title on the page or in the emails that the Riverside event does not carry.

## Output 2: Preview text

One sentence, shown under the event thumbnail and stored as the CMS `description` (a
single-line field).

- Always starts with "Learn".
- Focuses on one specific outcome.
- Does not repeat the title.
- No marketing language.

## Output 3: Landing page body

If the requestor provided landing page copy, reproduce it **verbatim**.

Otherwise, this structure:

- **P1, the problem** (1-2 sentences). Start with the problem and make it feel real.
- **P2, expand the pain** (1-2 sentences). Validate the frustration.
- **P3, introduce the guest** (1-2 sentences): name, role, what they'll do.
- **P4, set expectations** (1-2 sentences): what the session is really about.
- **Bullets, 4-5 outcome-focused points.** Each starts with "How to...", "Ways to...",
  "Tips for..." or "What actually..."
- **Closing paragraph:** who it's for, the practical takeaway, and that they can watch live
  or get the replay.

Format: HTML for a rich text field, `<p>` paragraphs and exactly one `<ul>` of `<li>`
bullets. No headings, no emojis, no inline styles.

**Workshops** are hands-on and skills-focused: "walk away with," "try it live,"
"tactical," "actionable." **Webinars** are watch-and-learn: "see it in action," "live
walkthrough," "inside look," "ask questions live."

## The three emails

### How a draft maps onto the email

The pipeline's email template renders, top to bottom: a centered **headline**, the
**body**, one **button**, then the **secondary** block. Every email is written into those
slots:

| Slot | Content |
|---|---|
| `subject` | Subject line. Lowercase and conversational is Kendall's style. |
| `preheader` | 40-90 characters. Never repeats the subject. |
| `headline` | The event title as an `<h2>` (style below). Never the subject line. |
| `body` | HTML. The opener and everything above the button. |
| `cta` | `{ "text": "...", "url": "[[PLACEHOLDER]]" }`. The one CTA. |
| `secondary` | HTML. Everything below the button, ending with the sign-off. |

Headline markup, for all three: `<h2 style="text-align:center; font-size:28px; line-height:125%;">[Event Title]</h2>`.

Placeholders the pipeline resolves at build time. Use them exactly; any other `[[...]]` is
rejected.

| Placeholder | Becomes |
|---|---|
| `[[JOIN_URL]]` | The registrant's personal join link (shared studio link as fallback) |
| `[[GOOGLE_CALENDAR_URL]]` | Add to Google Calendar |
| `[[OUTLOOK_CALENDAR_URL]]` | Add to Outlook.com |
| `[[OFFICE365_CALENDAR_URL]]` | Add to Outlook for work or school (Office 365) |

Rules for all three:
- No emojis, no em or en dashes.
- One CTA per email: the button. Any other link is a calendar link in the confirmation.
- Body plus secondary under 200 words; the day-before reminder under 100.
- Signed by Kendall, always: `<p>Kendall<br>Head of Community, Riverside</p>`, except the
  day-of reminder, which signs on one line.
- No HubL statements (`{% ... %}`). Personalization tokens are allowed but Kendall's emails
  do not use them: she opens with "Hey!", not a first name.

### `registration`: confirmation

Tone: "You're in, here's what to expect."

- **Subject:** "you're in, here's what to expect" or "you're registered, see you [day]".
- **Preheader:** confirms the event name and date.
- **Body:**
  1. "Hey!"
  2. "You're all set to join us for [Event Title]."
  3. One sentence on what the session covers.
  4. 3-4 bullets, each a label, a colon and a short description (e.g. "Studio and Editor:
     Our fully rebuilt recording Studio and Editor").
  5. "Date: [Day, Month Date]" and "Time: [Time] [zone label]" on separate lines.
- **Button:** "Save to Google Calendar" → `[[GOOGLE_CALENDAR_URL]]`.
- **Secondary:**
  1. "Save to Outlook" linked to `[[OUTLOOK_CALENDAR_URL]]`, on its own line.
  2. "We'll send a reminder with a studio link before we go live."
  3. "If you can't make it, no worries. We'll send the replay to everyone who registers."
  4. "Looking forward to having you there." (no exclamation point)
  5. Sign-off.

The confirmation carries **no join link** on purpose. It goes out the moment someone
registers, before their personal link exists; the reminders carry it.

### `firstReminder`: day before

Tone: "Quick reminder, and why it's worth showing up."

- **Subject:** "quick reminder for tomorrow", "see you tomorrow" or "don't forget".
- **Preheader:** reinforces the time and the value.
- **Body:**
  1. "Hey there!" (the only email that uses this opener)
  2. "Just a quick reminder that tomorrow we're going live for [Event Title]."
  3. One sentence on the value.
  4. "Date: Tomorrow, [Month Date] Time: [Time] [zone label]" on one line.
- **Button:** "Join the studio live here" → `[[JOIN_URL]]`.
- **Secondary:** "Hope to see you there!", then the sign-off.
- No bullets, no calendar links, under 100 words.

### `secondReminder`: day of

Tone: "We're starting soon, here's how to join." The shortest email: get to the link fast.

- **Subject:** "we're live in a few hours", "happening today" or "we're starting soon".
- **Preheader:** states the time and leads with the join link.
- **Body:**
  1. "Hey!"
  2. "Just a quick reminder: We're going live in just a few hours for [Event Title]."
- **Button:** "Join the studio here" → `[[JOIN_URL]]`, right after the opener.
- **Secondary:**
  1. 3-4 bullets, the feature or topic name only, no descriptions. The last can be "A lot more."
  2. "Can't make it live? We'll send the replay after."
  3. "See you soon!"
  4. `<p>Kendall, Head of Community, Riverside</p>` on one line.

## Quality pass, before anyone approves it

1. **Self-check** every output against the rules above: no dashes, no emojis, word limits,
   one CTA, the right opener per email, "Learn" first in the preview text.
2. **Product claims.** Any sentence that says what Riverside does goes through
   `/demo-reply-fact-check`. A claim it marks contradicted is rewritten; in verbatim
   requestor copy it is flagged to the requestor instead, never silently changed.
3. **`/de-ai`, then `/critique`.** This skill is stage 1 for webinar copy, in place of a
   `nik-voice` register, because the voice is Kendall's, not Nir's. Verbatim requestor copy
   is not rewritten at either stage; `/critique` may still flag it.
4. **Human approval** of the review render. Nothing is built from unapproved copy.

## Output format

**A. The review render**, for the human to read and approve, with no commentary around it:

```
TITLE
[the Riverside title, or 2-3 options and a note that Studio must change first]

PREVIEW TEXT
[one sentence]

LANDING PAGE COPY
[rendered as plain text]

EMAIL 1: REGISTRATION CONFIRMATION
Subject: ...
Preheader: ...
[body] [BUTTON: text] [secondary]

EMAIL 2: DAY-BEFORE REMINDER
...

EMAIL 3: DAY-OF REMINDER
...
```

**B. The copy file**, written to the scratchpad as `webinar-copy-<eventId>.json`. Its
`emailCopy` object is exactly what the pipeline validates and applies; `landingPage` feeds
`page-build`.

```json
{
  "landingPage": {
    "name": "Community Workshop: Better Audio Without New Gear",
    "description": "Learn the room and mic tweaks that make a home setup sound like a studio.",
    "content": "<p>Your episode is great. Your audio is not. ...</p><ul><li>How to ...</li></ul><p>Whether you record ...</p>"
  },
  "emailCopy": {
    "registration": {
      "subject": "you're in, here's what to expect",
      "preheader": "Your spot for Better Audio Without New Gear is saved for Oct 22.",
      "headline": "<h2 style=\"text-align:center; font-size:28px; line-height:125%;\">Community Workshop: Better Audio Without New Gear</h2>",
      "body": "<p>Hey!</p><p>You're all set to join us for Community Workshop: Better Audio Without New Gear.</p><p>We'll fix the sound of the setup you already have.</p><ul><li>Room treatment: What to hang, move and stuff</li><li>Mic placement: Where it actually goes</li><li>Levels: How loud is loud enough</li></ul><p>Date: Thursday, October 22<br>Time: 12:00 PM EDT</p>",
      "cta": { "text": "Save to Google Calendar", "url": "[[GOOGLE_CALENDAR_URL]]" },
      "secondary": "<p><a href=\"[[OUTLOOK_CALENDAR_URL]]\">Save to Outlook</a></p><p>We'll send a reminder with a studio link before we go live.</p><p>If you can't make it, no worries. We'll send the replay to everyone who registers.</p><p>Looking forward to having you there.</p><p>Kendall<br>Head of Community, Riverside</p>"
    },
    "firstReminder": {
      "subject": "quick reminder for tomorrow",
      "preheader": "Tomorrow at 12:00 PM EDT: studio sound from the gear you own.",
      "headline": "<h2 style=\"text-align:center; font-size:28px; line-height:125%;\">Community Workshop: Better Audio Without New Gear</h2>",
      "body": "<p>Hey there!</p><p>Just a quick reminder that tomorrow we're going live for Community Workshop: Better Audio Without New Gear.</p><p>Bring your mic and we'll fix your sound live, no new gear needed.</p><p>Date: Tomorrow, October 22 Time: 12:00 PM EDT</p>",
      "cta": { "text": "Join the studio live here", "url": "[[JOIN_URL]]" },
      "secondary": "<p>Hope to see you there!</p><p>Kendall<br>Head of Community, Riverside</p>"
    },
    "secondReminder": {
      "subject": "we're live in a few hours",
      "preheader": "We go live at 12:00 PM EDT. Your studio link is right inside.",
      "headline": "<h2 style=\"text-align:center; font-size:28px; line-height:125%;\">Community Workshop: Better Audio Without New Gear</h2>",
      "body": "<p>Hey!</p><p>Just a quick reminder: We're going live in just a few hours for Community Workshop: Better Audio Without New Gear.</p>",
      "cta": { "text": "Join the studio here", "url": "[[JOIN_URL]]" },
      "secondary": "<ul><li>Room treatment</li><li>Mic placement</li><li>Levels</li><li>A lot more.</li></ul><p>Can't make it live? We'll send the replay after.</p><p>See you soon!</p><p>Kendall, Head of Community, Riverside</p>"
    }
  }
}
```

Check the file before handing it on. The same validator the pipeline runs at build time:

```bash
node -e 'const {validateCopy}=require("./tools/webinar-automation/scripts/email-copy");const r=validateCopy(require(process.argv[1]).emailCopy);console.log(JSON.stringify(r,null,2));process.exit(r.errors.length?1:0)' /absolute/path/to/webinar-copy-<eventId>.json
```

Errors block the build; fix them here, not in HubSpot. Warnings (preheader length, word
count) go in front of the reviewer.

## Done when

The review render is approved, the copy file passes the validator with no errors, every
product claim has a verdict, and the title equals the Riverside event title.
