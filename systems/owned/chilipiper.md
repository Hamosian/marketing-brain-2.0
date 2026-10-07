<!-- last-reviewed: 2026-09-24 (Nir asked to open Ziff AE availability to 2-3 weeks: all three ranges re-read live through `slots/span`, which takes any current timestamp as `meetingTypeVersion`. `_10d_` still 14 days, the EU router type 35 days, and the enterprise website type measured for the first time at 6 days. So the EU link is not what caps Ziff there, and the US `_10d_` range is the one setting to lengthen. Previous 2026-09-23: the website /book-demo path documented: a HubSpot form plus a custom script reads the three *_cp params off the page's own URL and hands them to ChiliPiper.submit, so the parameters never need to reach a chilipiper.com link; also the chat-widget path captures nothing, and an untagged arrival sends three empty strings into overwrite:true mappings). Previous 2026-09-23 (two Ziff EU enterprise bookings landed with `utm_*` set but all three `*_cp` fields empty; the bookings showed the tags in `sourceUrlParams` but not in `guestData`, the data fields themselves were correct, and the cause was the `sales_intro_bd_outbound_enterprise_new` meeting type's guest form not carrying the three fields. Hanan added them as hidden fields in the web app and the live form was verified. The MCP cannot read or edit guest forms. Previous 2026-09-20: ten Ziff-stamped bookings from 16-18 Sept with no LHO were traced to their source links in one pass through the public meeting endpoint, which returns the whole booking with no auth; all ten were Ziff's own placements with the partner rep as a guest from booking, none came through the 1000+ link, and five Chili Piper host ids got names. Previous 2026-09-17: a Ziff Davis booking on the US 1000+ placement landed with all three `*_cp` fields empty; the link record and two bookings 49 minutes apart showed the link's own meeting type is the enterprise website one and the `meetingTypeId` override is what makes a Ziff booking stamp `_10d_` and capture the tags. Previous 2026-09-16: a Ziff Davis affiliate meeting turned up on six unrelated Pre-Ops and Clay wrote one company's close-lost story onto another's record, both from the partner rep attending every affiliate booking as a calendar guest. Created 2026-09-09 after two affiliate booking links served a 5-day calendar instead of the configured 2 weeks - the repo had ChiliPiper knowledge only as HubSpot `*_cp` fields, so nothing explained how a link picks its meeting type and every theory about the URL was wrong Same day, second trace: a Ziff meeting with no Chili Piper record at all: the rep handed the prospect to the AE by email and the AE sent his own invite, so there is no booking to read and the evidence lives in HubSpot. Previous 2026-09-17: a Ziff Davis booking on the US 1000+ placement landed with all three `*_cp` fields empty; the link record and two bookings 49 minutes apart showed the link's own meeting type is the enterprise website one and the `meetingTypeId` override is what makes a Ziff booking stamp `_10d_` and capture the tags. Previous 2026-09-16: a Ziff Davis affiliate meeting turned up on six unrelated Pre-Ops and Clay wrote one company's close-lost story onto another's record, both from the partner rep attending every affiliate booking as a calendar guest. Created 2026-09-09 after two affiliate booking links served a 5-day calendar instead of the configured 2 weeks - the repo had ChiliPiper knowledge only as HubSpot `*_cp` fields, so nothing explained how a link picks its meeting type and every theory about the URL was wrong) -->
# Chili Piper (Meeting Booking & Routing)

> The platform that books every sales intro meeting. It owns the calendar a prospect sees, the round-robin assignment behind it, and the `*_cp` fields it stamps onto the HubSpot contact at booking time. Operated by Marketing Operations.

## Overview

A prospect hits a scheduling link, Chili Piper renders available slots from the assigned hosts' calendars, and on booking it writes the meeting into Google Calendar and stamps attribution fields onto the HubSpot contact. Those stamps are what makes an MQL attributable, so a misconfigured link is an attribution problem, not just a booking-experience problem.

**The most useful thing in this doc:** on a round-robin link, the **meeting type comes from the link record, never from the URL path**. Anything meeting-type-shaped in the URL path is inert. The one thing in the URL that does select a type is the `meetingTypeId=<uuid>` **query parameter**, verified through a completed booking on 2026-09-17 (it stamps `meeting_type_cp__c` and decides whether the `*_cp` tags are captured, see Known Issues). Almost every wrong theory about a booking link starts by assuming the path does that job. See "How a link picks its meeting type" before changing any URL.

## Ownership

**Platform:** Marketing Operations. Links, meeting types and distributions are configured in ChiliCal by MOPs; the AE/BD hosts own only their own working hours.

**Tenant:** `riverside.fm`. **Workspace:** `ac65a549-773f-4b27-9fdb-22233242dc9a`.

**Riverside is served by Chili Piper's `canary` deployment ring**, not the stable one (`x-cluster: canary`, assets under `/static/canary/booking-app/`). Treat vendor docs as approximately right and verify behaviour against the live app.

## Object model

Four objects, and confusing them is the usual cause of a wrong diagnosis:

| Object | What it decides |
|---|---|
| **Scheduling link** (round-robin) | Which meeting type(s) and which distribution. Addressed by slug in the URL. |
| **Meeting type** | Duration, guest form, invite template, **availability range**, minimum notice, increments. |
| **Distribution** | The host pool and the round-robin rotation. |
| **Router** (concierge) | Form-based qualification then routing. A different URL family entirely. |

URL families - these are distinct and not interchangeable:

```
https://riverside.chilipiper.com/round-robin/<link-slug>          # one path segment only
https://riverside.chilipiper.com/concierge-router/link/<router>   # e.g. sdr-router
https://riverside.chilipiper.com/reschedule/<booking-uuid>
```

## How a link picks its meeting type

Loading `/round-robin/<slug>` fires exactly one lookup:

```
GET /api/team-scheduling/v3/guest-external/tenant/riverside.fm/round-robin-scheduling-links/find-by-slug/<slug>
```

The response carries `meetingTypeIds` and the `assignments[].distributionId`. **The meeting type is resolved from that array.** Nothing in the URL path contributes.

**`/round-robin/<link>/<meeting-type>` is not a route.** It renders "Something went wrong, try again later". Do not "fix" a malformed link by inserting a slash between the two segments.

**The documented override is a query parameter and it needs a UUID.** `?meetingTypeId=<uuid>` passes a specific meeting type "even if the Scheduling Link is associated with a different one" (Chili Piper, Smart Scheduling Links). The booking app does read it on round-robin links. Passing the **slug** instead of the UUID breaks the page with `400 Invalid value for: body (Failed to decode json at 'ids[0]')`.

### Known meeting types

| Name | UUID | `slots/span` duration | Effective range |
|---|---|---|---|
| `sales_intro_inbound_agency__` | `7aeacbe1-a021-4684-9651-74eb90472346` | 421,200,000 ms (117 h) | **5 days** |
| `sales_intro_inbound_agency_10d_` | `66abce29-0a03-4774-b012-b2ad8706af2c` | 1,198,800,000 ms (333 h) | **14 days** |
| `sales_intro_bd_outbound_enterprise_new` | `e8462d33-09c6-45a8-b0d7-be3c82407155` | 3,013,200,000 ms (837 h) | **35 days** |
| `sales_intro_inbound_enterprise__` | `fc4c0e5b-f097-496c-b94b-ee02da60de08` | 507,600,000 ms (141 h) | **6 days** |

The first two were measured live 2026-09-09, the third 2026-09-16 and the fourth (the enterprise website type, the one `us_enterprise__1-license_website_` resolves without the `meetingTypeId` override) 2026-09-24, all with a 3-hour minimum scheduling notice. All four were re-read 2026-09-24 and the first three were unchanged. **The `_10d_` type is shared by every placement that carries the `meetingTypeId=66abce29-...` override, so lengthening its range lengthens it for every affiliate on that override, not only Ziff.** The `_10d_` type is the affiliate/vendor one; the plain type is the website one. They also differ in default location: `_10d_` uses `CalendarPlatformConference` (Google Meet), the plain type uses `HostsDefaultConferenceDetails`. The BD outbound type is the **router/handoff** one: 30 minutes (the agency types are the inbound intro), Google Meet, and its guest form makes **phone number required** on top of name and email - a friction point worth knowing before anyone blames drop-off on the calendar.

### Known round-robin links

| Slug | linkId | Meeting type | Distribution |
|---|---|---|---|
| `eu_agency_51-200__website_` | `363e4098-ced3-4820-9270-3dc234c222ff` | plain (5-day) | `3823ce6d-4908-4093-a75e-006412c7e784` |
| `eu_agency_201-1000__website_` | `f526e4bc-9026-4410-820c-72864c9c0d3f` | plain (5-day) | `f1bd486c-665d-4965-86e6-de1359c58c2e` |
| `us_enterprise__1-license_website_` | `b8176cd1-55f4-45f2-bea2-a49e8b109b65` | **`sales_intro_inbound_enterprise__`** (`fc4c0e5b-f097-496c-b94b-ee02da60de08`), the enterprise website type. Stamps `_10d_` only when the URL carries `meetingTypeId=66abce29-...` (read from the link record 2026-09-17) | `8f3842e4-d0eb-4a88-bf3b-1131c21e6077`, 8 hosts: Maté Baker, Ryan Fratesi, Tom Lepage, Aaron Baird, Stacey Elman, Carley Cowman, Jillian Jones, Hagai Benziman |
| `bd-handoff-europe-enterprise` | `6483c8b4-a19f-4587-9b25-627fc6687dd4` | `sales_intro_bd_outbound_enterprise_new` (`e8462d33-09c6-45a8-b0d7-be3c82407155`), 30 min, **35-day** range | `fae7e32b-0ce3-4eca-9b0d-993ae3d9a30a`, 5 hosts |
| `sales_intro_inbound_agency_10d_` | `c0ccd71c-7838-4148-9693-0c1ac16e3877` | `_10d_` (14-day) | `d902cb3f-42ce-42ad-af25-1fc79f208723`, **0 members** - the link cannot book anything until hosts are assigned (read 2026-09-17) |
| `sales_intro_inbound_agency_10d_-1` | `8f37b866-7cd0-4019-ae99-5bd1ef0e6b61` | `_10d_` (14-day) | `5a1179e1-f79a-49ce-90c0-3dca9316301d`, 8 hosts: Nicole Passarelli, Shayan Habibi, Eric Irvin, Broden Stewart, Connor MacLeod, Mitchell Vickers, Diego Sotorivero, Luke Ley (read 2026-09-17) |
| `us_agency_51-200_1-license__` | `ea439337-7461-4465-9fae-3722d30b5fce` (confirmed from booking records 2026-09-20) | own type not read; Ziff bookings through it carry the `meetingTypeId=66abce29-...` override and stamp `_10d_` | `5a1179e1-f79a-49ce-90c0-3dca9316301d` (same pool as `_10d_-1`), seen on bookings 2026-09-01, 2026-09-15, and three on 2026-09-16 to 2026-09-18 hosted by Shayan Habibi (2) and Nicole Passarelli (1), both in that pool |

**A link's slug does not describe what it does, and neither do its bookings on their own.** `us_enterprise__1-license_website_` is the ZiffDavis "1000+ employees" placement. Its link record offers exactly one meeting type, `sales_intro_inbound_enterprise__` (`fc4c0e5b-...`), the plain enterprise website type. The 132 ZiffDavis contacts measured 2026-09-15 that all carried `_10d_` got it from the `meetingTypeId=66abce29-...` query parameter on the placed URL, not from the link. Proof, two bookings on this link 49 minutes apart on 2026-09-15: Adam Pickering (Starr, meeting `80c8ba8f-cca5-4cff-b094-1cfe1c02e2ba`, 11:38 UTC) came through `.../form?meetingTypeId=66abce29-...&utm_...&meeting_*_cp=...`, stamped `_10d_`, and all three `*_cp` values landed in `guestData`; Shaun Claude (Obsidian Group, meeting `5d8d4c43-7fce-403f-b12a-d5c176381bec`, 12:27 UTC) came through `.../form?sales_intro_inbound_agency_10d_%3Futm_medium=affiliate&utm_source=ziffdavis&...&meeting_*_cp=...` with **no** `meetingTypeId`, stamped `sales_intro_inbound_enterprise__`, and `guestData` held only first name, last name and email. Read the routing from the link record (`scheduling-link-list-round-robin`, `filterLinkSlugs`) and the booking's `sourceUrl` (`meeting-get`); never from the slug's words or from `meeting_type_cp__c` alone.

**ZiffDavis is not one link, and the EU router books a different meeting type.** The 132-contact measurement above is the **US** 1000+ placement. ZiffDavis EU enterprise traffic goes to `bd-handoff-europe-enterprise` ("BD Handoff - Europe Enterprise"), which resolves a **third** meeting type, `sales_intro_bd_outbound_enterprise_new` - not either agency type. Confirmed from the link record 2026-09-16 (link supplied by Nir). Never generalise a ZiffDavis routing finding from one placement to the affiliate as a whole.

**The ZiffDavis EU enterprise URL, as placed:**

```
https://riverside.chilipiper.com/round-robin/bd-handoff-europe-enterprise
  ?utm_medium=affiliate&utm_medium=affiliate&utm_source=ziffdavis&utm_campaign=bookmeet
  &meeting_source_cp=ziffdavis&meeting_campaign_cp=bookmeeting&meeting_medium_cp=affiliate
```

Two things to know about it. `utm_medium=affiliate` appears **twice** - harmless here, because Chili Piper reads only the three `*_cp` parameters and ignores `utm_*` on this link family, but any other consumer that parses the query string sees a repeated key and picks one arbitrarily. And the `*_cp` values do not match each other in style: `meeting_campaign_cp=bookmeeting` here against `utm_campaign=bookmeet`, so a report that joins on campaign will split these bookings in two. Fix both at the placement, not in the link record.

**Non-website links use a different naming convention.** The `__website_` links are underscore-delimited and size-banded; the router links are kebab-case and descriptive (`bd-handoff-europe-enterprise`). That is why seven underscore-style slug guesses 404'd on 2026-09-09. Guess in kebab-case for anything that is not a website placement.


**Two links are literally named after the `_10d_` meeting type, and at least one affiliate booking still does not use them.** `sales_intro_inbound_agency_10d_` and `sales_intro_inbound_agency_10d_-1` exist in the link list (read via the MCP 2026-09-16). That does **not** settle the gap above about which link ZiffDavis actually books through: a ZiffDavis booking on 2026-09-16 (Le Ski, meeting `66724a18-f7f4-49c2-9577-a3e9363cb47c`) came through `eu_agency_51-200__website_` with `&meetingTypeId=66abce29-...` appended, i.e. the query-parameter workaround rather than a dedicated link. So ZiffDavis spreads across at least three placements, and the structural fix in Known Issues is still open.

Slugs confirmed **not** to exist (probed 2026-09-09, clean 404s): `eu_agency_1-50__website_`, `eu_agency_1000__website_`, `eu_agency_1000+__website_`, `us_agency_51-200__website_`, `eu_agency_51-200_`, `eu_agency_201-1000_`, `eu_agency_51-200__affiliate_`. Those guesses all assumed the underscore convention; the router links are kebab-case (see above).

## Reading availability: the span formula

```
GET /api/availability/v1/public/tenant/riverside.fm/slots/span?meetingTypeId=<uuid>&meetingTypeVersion=<iso>
-> {"startsAt": "<iso>", "duration": "<n> milliseconds"}
```

Decode it as:

- `startsAt` = page load + **minimum scheduling notice**
- `duration` = **availability range** minus the minimum scheduling notice

So a 2-week range with a 3-hour notice reads as 333 h, and a 5-day range as 117 h. `meetingTypeVersion` is required (a 400 without it) but any current ISO timestamp works, since it resolves the version live at that moment; a timestamp from before the type existed fails with `meeting-type-api-call-failed`. So plain `curl` with a browser `User-Agent` reads the range without the booking page (verified 2026-09-24). Convert before believing a complaint: this endpoint is the only place the *live, published* range is observable without admin access.

`PUT /api/availability/v1/public/tenant/riverside.fm/meeting/slots` then returns every bookable start time, which is the ground truth for "which days does the prospect actually see". Prefer it over clicking through the widget, whose "Next Week" button is unreliable to drive.

**The widget renders a 14-day ribbon regardless of the real horizon.** It shows the current week plus next week, Sunday-aligned, caps there, and greys out unavailable days. A 5-day window therefore presents as a half-filled two weeks, which is exactly what makes this class of bug read as "the calendar is ignoring my 2-week setting".

**The slots call is not practical to replay by hand.** Its body needs `expectedHost`, `attendees`, `meetingTypeRef`, `meetingTypeOverride`, `interval`, `linkMeetingLimit` and `availabilityChecks`, several of them tagged unions whose `type` values are not documented, so a hand-built body fails to decode (tried 2026-09-24). Read the slots from the booking page's own network trace instead.

**Distributions can cap each host per day, which thins slots without shortening the range.** The public distribution endpoint returns `assignmentTypeConfig.limits`. Read 2026-09-24: the US agency pool (`5a1179e1-...`, 13 users) has a daily cap of **1 meeting per host** on four of its hosts and 10 on one, resetting midnight New York (two more caps name users no longer in the pool); the US enterprise pool (`8f3842e4-...`) has a daily limit configured but no per-user caps, and one host on vacation; the EU router pool (`fae7e32b-...`, 5 users) has no limit. A capped host who takes one meeting shows no more slots that day.

**The range is a ceiling, not a promise.** These meeting types use Availability Schedule = "Let the Host decide", so the meeting type contributes no availability of its own and the window is filled entirely from each host's working hours and connected calendar. Weekends are disabled by default. A short calendar can therefore be a host-availability problem with a perfectly correct range, so always check the span *and* the returned slots.

## Which query parameters Chili Piper actually reads

On these links Chili Piper resolves exactly three, confirmed from `POST /api/customization-settings/v1/guest-external/.../smart-parameters/by-values`:

| Parameter | Guest-form data field reference |
|---|---|
| `meeting_source_cp` | `4f70a7e4-1740-4bab-a8fe-763cb8b1220b` |
| `meeting_campaign_cp` | `3484a23f-a348-4a1b-8d8f-b4ecdf9a52f4` |
| `meeting_medium_cp` | `6b467335-3c2d-4033-b024-c0334ced8da1` |

The `utm_*` parameters are captured separately: Chili Piper stores them on the meeting as `utmParameters` and HubSpot's `utm_source` / `utm_campaign` contact fields get them, independent of whether the three `*_cp` data fields were captured (corrected 2026-09-17; this doc previously said `utm_*` was not read at all). So a contact with `utm_source = ziffdavis` and empty `*_cp` fields is a Chili Piper booking whose tag capture failed, not an off-link booking. A missing `utm_medium` alone is still not proof the link was broken.

### The website `/book-demo` page passes them too, by its own code

The three parameters reach Chili Piper on **two independent paths**, and only one of them is
a Chili Piper-hosted link. Verified 2026-09-23 from live page source.

On `riverside.com/book-demo` (and `/de/buch-demo`) the booking is a **HubSpot form plus a
custom script**, not a Chili Piper link. The form's `onFormSubmit` reads the three parameters
off the *page's own* URL and puts them in the lead object it hands to Chili Piper:

```js
const urlParams = new URLSearchParams(window.location.search);
formData = { /* ... */ meeting_source_cp: urlParams.get('meeting_source_cp') || '' /* ... */ };
// onFormSubmitted -> openChiliPiperFromLead(formData)
//   -> ChiliPiper.submit("riverside", "inbound-router", { trigger: "ThirdPartyForm", lead })
```

So a parameter on the **page** URL is enough; nothing has to reach a `chilipiper.com` link.
One `hbspt.forms.create` call serves five locale form ids (EN default plus de/fr/es/pt) and
they all share this handler, so capture is locale-independent. `/de/buch-demo` carries the
same wiring and the same router.

Two consequences before you debug a blank field:

- **The page always sends all three keys.** `urlParams.get(x) || ''` means an untagged
  arrival submits three empty strings, and all three HubSpot mappings are `overwrite: true`.
  An empty value from a later website booking can clear what an earlier tagged touch wrote.
- **The chat path bypasses this entirely.** The closed-state UI's `.contact-sales` link opens
  the **HubSpot Conversations widget**, not Chili Piper, so a demo booked through chat
  carries no `*_cp` values at all and no amount of link tagging reaches it.

## Reading live config

**For a single booking, the public meeting endpoint is faster than either and needs no auth.** Verified 2026-09-20 on ten bookings:

```
GET https://riverside.chilipiper.com/api/meetings/v1/public/tenant/riverside.fm/meeting/<booking-uuid>
```

The `<booking-uuid>` is the one in the reschedule link, which HubSpot keeps in the MEETING object's `hs_meeting_body`. Plain `curl` with a browser `User-Agent` returns 200 (the edge guard that 403s `guest-external` routes does not sit on this one). The response carries `scheduleOrigin.productFeature.sourceUrl` (the exact URL the booking came through, query string included) and `.linkId`, `meetingTypeId`, `hostId` (a Chili Piper user id), `assignment.distributionId`, the full `attendees` list with response status, `primaryGuest`, `dateTime` and `meetingStatus`. It does not carry `history`, `guestData` or the CRM sync report; for those use the MCP's `meeting-get`. This is the route that answers "which link and which booker did these contacts come through" for a list of contacts in one loop, and it is what closed the 2026-09-20 Ziff question below.

**Use the Chili Piper MCP connector first.** One exists as of 2026-09-16 (it did not on 2026-09-09) and it reaches the admin surface directly, so the browser trace below is now the fallback rather than the only route. The calls that answer most questions:

| Tool | Gives you |
|---|---|
| `meeting-get` (meetingId = the reschedule-URL UUID) | the whole booking: `attendees`, `guestData`, `sourceUrl`, `meetingTypeId`, host, CRM sync report, full `history` |
| `meeting-type-get` | invite title and description templates, duration, reminders, location |
| `scheduling-link-list-round-robin` | every link with its `linkId`, `slug`, `meetingTypeIds` and members |

Two gotchas worth the warning. Schemas arrive via `describe-tools`, and that payload and the link list both blow the tool-output limit, so save to a file and query it with `jq`. And on a scheduling link the id field is `linkId`, **not** `id`; a `jq 'select(.id==...)'` returns empty and reads as a missing link.

**The MCP cannot see or change a meeting type's guest form.** `meeting-type-get` and `meeting-type-update` cover the invite, duration, location, buffers, limits and reminders only; which data fields sit on the form (and whether they are hidden) is web-app only (Admin, Meeting Types, the type, Guest Form, then publish). `data-field-get` does show the tenant-wide half: each field's `smartParameters` (the URL tag it reads) and its HubSpot mapping. To verify a form without admin access, load the public link with its query string, pick a slot, and read the page's inputs: hidden fields render as `<input type="hidden" name="<data-field-uuid>">` pre-filled from the URL. Picking a slot books nothing until the form is submitted. Replaying the page's `PUT .../meeting-types` from page JavaScript is refused by the Claude Code auto-mode classifier as a write, so read the DOM instead.

### Fallback: reading config from a public booking page

Where the MCP cannot answer, **load a public booking page in a browser and read its network trace**:

| Request | Gives you |
|---|---|
| `find-by-slug/<slug>` | the link's `meetingTypeIds` and `distributionId` |
| `PUT /api/meeting-types/v2/public/.../meeting-types` | id to **name**, guest form, invite template |
| `slots/span` | the live published availability range |
| `PUT .../meeting/slots` | every bookable start time |
| `smart-parameters/by-values` | which query params are resolved |

**When the booking app is unreachable, read the link's *effective* behaviour out of HubSpot instead.** It answers "which meeting type does this link book" and "who hosts the result", which is usually the real question:

| Question | Where to read it |
|---|---|
| Which meeting type did this link book | Contact `meeting_type_cp__c` (carries the meeting-type slug) |
| Which placement sent the traffic | Contact `meeting_source_cp` / `meeting_campaign_cp` / `meeting_medium_cp` |
| **Who actually hosted the meeting** | **MEETING object `hubspot_owner_id`** - this is the Chili Piper host |
| Which rep ended up owning the person | Contact `hubspot_owner_id` - **not the host**, and frequently a different rep |

That last distinction matters: on ZiffDavis bookings the contact owner and the meeting host disagree often enough that using the contact owner to answer "who is getting these meetings" gives the wrong names. Observed host pool on `sales_intro_inbound_agency_10d_`, 31 meetings between 2026-08-15 and 2026-09-15: Ori Tal 7, Alan Kirschberg 6, Jared Wight 4, Hagai Benziman 3, Vincent Katz 3, Jillian Jones 3, Nicole Passarelli 2, then Ellie Horder, Koby Shufman, Connor MacLeod and Shayan Habibi 1 each. A pool that mixes Agency and Enterprise AEs, so a complaint that "an Enterprise AE is getting agency-looking meetings" from this link is the round-robin working as configured, not a stray.

**To inspect a meeting type no public link exposes, go in through a reschedule URL.** Find a booking that used it (`hs_activity_type` on the HubSpot MEETING object carries the meeting-type slug, but not reliably: on 2026-09-23 the Asahi Photoproducts meeting `117018147073` read `sales_intro_inbound_agency__` while its Chili Piper booking was on `sales_intro_bd_outbound_enterprise_new`, so confirm the type with `meeting-get` before relying on it), take the reschedule link out of `hs_meeting_body`, and load it. That is how the `_10d_` type's UUID and 14-day range were obtained. Loading a reschedule page is read-only and does not alter the booking.

## Known Issues / Failure Modes

| Symptom | Cause | Fix |
|---|---|---|
| A meeting appears on Pre-Ops belonging to other companies, and Clay writes one company's close-lost story onto another's record | **The Ziff Davis partner rep rides along on the booking.** In the one booking read in full (Le Ski, `66724a18-f7f4-49c2-9577-a3e9363cb47c`, 2026-09-16) `charles.green@swzd.com` is in `attendees` from the moment it is booked, so he lands on the Google Calendar event; HubSpot's calendar sync logs him, matches the existing contact, and then associates the meeting with every deal that contact is on. Measured 2026-09-16: he carries **58 Pre-Ops** and **17 meetings**, that one meeting fanned out to **6 unrelated Pre-Ops**, and 3 new bad associations appeared that day. Anything reading a deal's evidence through its associated contacts and meetings, Clay included, then blends unrelated companies. How many of the 17 carry him from booking rather than a later edit was not checked per meeting. Also seen from booking time on the enterprise-type bookings (Shaun Claude 2026-09-15, Lynn Girotto 2026-08-27), so it is not specific to the `_10d_` type. Confirmed at scale 2026-09-20: all ten Ziff-stamped bookings from 16-18 Sept carry him in `attendees` (status `NeedsAction`) across three different links, so it is the Ziff booking process, not one link's config. | **He is not configured on the `_10d_` meeting type (`66abce29-...`) or on `eu_agency_51-200__website_`** - both read 2026-09-16, zero matches. The other links, the EU router and the tenant's routing rules were not checked, so "he adds himself" is the reading those two rule out a config cause for, not a tenant-wide finding. On that reading the durable fix is partner-side. Note Chili Piper synced only the *primary* guest to HubSpot (`crm.guest`), so the extra association is HubSpot's calendar sync and that is the other lever. Cleanup alone recurs. Open as of 2026-09-16. |
| Contacts carry the full Ziff stamp (`ziffdavis` / `affiliate` / `_10d_`) but no LHO arrived, so the question is whether Ziff booked them at all | **Read each booking's `sourceUrl` and `attendees` from the public meeting endpoint (Reading live config).** Checked 2026-09-20 for the ten stamped contacts booked 16-18 Sept: all ten came through Ziff's own placed URLs (six `eu_agency_51-200__website_`, three `us_agency_51-200_1-license__`, one `eu_agency_201-1000__website_`, every one with the `meetingTypeId=66abce29-...` override and all six tags), none through the US 1000+ link, and `charles.green@swzd.com` was a guest on all ten from booking. So the stamp was right and the gap was the handover, not the booking. Chili Piper records no named booker on a round-robin link; the guest is the booker, and the partner rep in `attendees` is the tell. The two LHOs logged on 2026-09-18 (`.claude/skills/vendor-meeting-quality/data/ziff-scores.csv`) arrived 3-4 days before their meetings, and these ten meetings ran 2026-09-23 to 2026-09-29, so an LHO that has not arrived a week out is not yet evidence of a miss. | Do not backfill or dispute anything on the stamp alone. Trace the bookings first (one `curl` per contact), then chase the vendor for the missing handovers with the list. Recorded 2026-09-20. |
| A vendor booking has `utm_source` / `utm_medium` / `utm_campaign` set on the Contact but all three `*_cp` fields empty, and the booking's `sourceUrlParams` **does** show the three `*_cp` values | **The meeting type's guest form does not carry the three data fields**, so Chili Piper parses the tags from the URL and drops them; `guestData` holds only what the form collects. Capture is per meeting type: the data fields themselves (`4f70a7e4-...` source, `6b467335-...` medium, `3484a23f-...` campaign) are tenant-wide, each reading its same-named URL tag and writing its same-named HubSpot Contact property with overwrite on, and they were correct throughout. Found 2026-09-23 on the two Ziff EU enterprise bookings through `bd-handoff-europe-enterprise` (Dieter Niederstadt / Asahi Photoproducts, `0f157761-60d8-4066-bcf4-145fb017514a`, booked 2026-09-17; Patrick McManus / Humaneva, `21707a65-6cef-492e-8c03-8c4e79374173`, booked 2026-09-22), which were the whole population of Ziff contacts on `sales_intro_bd_outbound_enterprise_new`: 0 of 2 captured. Both were Ziff's (placed URL, `charles.green@swzd.com` in `attendees` from booking, LHO received). Do not compare such a contact against `_10d_` Ziff contacts: the EU router always books the BD outbound type. | Add the three fields to that meeting type's guest form as **hidden** fields, choosing the existing data fields (never create new ones, which would have no HubSpot mapping), then publish the meeting type. Web app only (see Reading live config). Done for `sales_intro_bd_outbound_enterprise_new` 2026-09-23 by Hanan: the live form was verified to render all three as hidden inputs pre-filled from the link (new meeting-type version 2026-09-23T07:26:40Z), and the first real booking after the fix has not yet been checked end to end in HubSpot. Backfill the affected Contacts per the claim rule in `systems/owned/hubspot.md`; both above were backfilled 2026-09-23. When adding any new vendor link or meeting type, check its form for these fields before the vendor uses it. |
| Invites on the `_10d_` type are titled ` <> Riverside: Intro Call` with a blank company | The `_10d_` invite title is `{!CP.DataField.Company} <> Riverside: Intro Call`, and the ZiffDavis form feeding it does not collect Company, so the token resolves empty. Only `PersonFirstName`, `PersonLastName`, `PersonEmail` and the three `*_cp` fields arrive. Scoped to `_10d_` bookings, which is what was read; ZiffDavis also routes through `sales_intro_bd_outbound_enterprise_new` (see Known round-robin links), and that type has the same problem: its invite title is `  {!CP.DataField.Company} // Riverside: Intro Call` and the form collects no Company, so Ziff EU invites read `   // Riverside: Intro Call` (read 2026-09-23). | Collect Company on the affiliate form, or give the affiliate an invite title that does not depend on it. Cosmetic on the invite, but it also leaves the meeting unidentifiable in a HubSpot list. Open as of 2026-09-16. |
| Calendar shows ~5 days when the meeting type says 2 weeks | The link is wired to the plain 5-day meeting type. The 2-week setting belongs to a meeting type the link never resolves. | Append `&meetingTypeId=66abce29-0a03-4774-b012-b2ad8706af2c`, or give the affiliate its own link wired to `_10d_`. Verified 2026-09-09 on both `__website_` links. |
| A booking URL contains two `?` characters (or `%3F`) | Someone appended the meeting-type slug expecting the path to select it. Per RFC 3986 the query starts at the *first* `?` and `?` is legal inside a query, so the result is a parameter literally named `sales_intro_inbound_agency_10d_?utm_medium` and `utm_medium` is destroyed. Worse, the URL then carries no `meetingTypeId`, so the booking falls to the link's own meeting type, and on that path the three `*_cp` values were **not** captured into `guestData` even though Chili Piper parsed them (`sourceUrlParams` shows them). The likelier cause is now the per-meeting-type guest form (see the `*_cp` in `sourceUrlParams` but not `guestData` row): on 2026-09-23 a clean URL on the EU router lost the tags the same way, and the cause there was the form. The enterprise website type's (`fc4c0e5b-...`) form was not checked. The fix below is still right, because the override moves the booking onto the `_10d_` type, whose form carries the fields. | Replace the stray segment with `?meetingTypeId=<uuid>&`. **Never** swap the `?` for a `/`; that is not a route and the page errors. |
| A ZiffDavis contact has `utm_source = ziffdavis`, `utm_medium` empty, all three `*_cp` fields empty, and `meeting_type_cp__c = sales_intro_inbound_enterprise__` | **The US 1000+ placement as Ziff has it is the double-`?` URL above, without `meetingTypeId`.** Two bookings found on `us_enterprise__1-license_website_` with this signature: Lynn Girotto / Qualtrics (2026-08-27, meeting `14ebd4d7-bc35-4d7f-a5da-7bc2595e01e9`, contact `244765888081`, `*_cp` since hand-filled) and Shaun Claude / Obsidian Group (2026-09-15, meeting `5d8d4c43-7fce-403f-b12a-d5c176381bec`, contact `248602780935`). Scan covered 120 bookings on the enterprise type, 2026-08-24 to 2026-09-17. Same link, same hour, with `meetingTypeId=66abce29-...` present, the tags land (Adam Pickering, above). | Give Ziff the working form of the link: `https://riverside.chilipiper.com/round-robin/us_enterprise__1-license_website_/form?meetingTypeId=66abce29-0a03-4774-b012-b2ad8706af2c&utm_medium=affiliate&utm_source=ziffdavis&utm_campaign=bookmeet&meeting_source_cp=ziffdavis&meeting_campaign_cp=bookmeeting&meeting_medium_cp=affiliate` (verified by a completed booking 2026-09-15). Backfill the affected contacts per the rule in `systems/owned/hubspot.md` (vendor claim first): the Chili Piper `meeting-get` record showing Ziff's own `sourceUrlParams` and `charles.green@swzd.com` in `attendees`, plus the SWZD tracker row, is that claim. The 18:56 IDT 2026-09-15 "US 1000+" link Nir relayed still lacks `meetingTypeId` and will fail the same way if Ziff uses it. |
| A vendor meeting has **no Chili Piper record at all** (no booking under the prospect email in any status, HubSpot meeting `BIDIRECTIONAL_SYNC`, every `*_cp` field empty) | The vendor rep handed the prospect to the AE **by email** and the AE sent his own calendar invite. Nothing here ran, so there is no `sourceUrl`, no `guestData` and no link record to read. Exhibition Place, 2026-09-16: `charles.green@swzd.com` looped Spencer Herbst in by email after rescheduling the prospect; confirmed 2026-09-20. | Do not look for the booking here. The evidence is on the HubSpot Contact: the logged email thread with the vendor rep, the Gong participant list, and the `[PREOPP NOT CREATED]` note. Claim rule and backfill: `systems/owned/hubspot.md`. Prevention is the same as every other row: the vendor books on its tagged link. |
| Affiliate traffic lands on the website meeting type | Affiliate placements reuse the `__website_` links with affiliate params bolted on, inheriting the website's 5-day window. | Structural: dedicated affiliate links wired to `_10d_`. Do not repoint the `__website_` links, which would change the window for ordinary site traffic. |
| `Meeting_Medium` records blank on a `_10d_` booking | **Template bug.** The `_10d_` invite description ends `Meeting_Medium - // ` with no merge token, while Meeting_Source and Meeting_Campaign both have theirs. | Append `{!CP.DataField.6b467335-3c2d-4033-b024-c0334ced8da1}` to that line, then publish. Open as of 2026-09-09. |
| Direct `curl`/`fetch` to a `guest-external` endpoint returns 403 | An edge guard on non-app requests, not a real answer. It returns a byte-identical 403 for a slug that returns 200 through the app. | Probe by navigating the booking app instead, where 404 and 200 discriminate cleanly. See `references/integration-debugging.md`. |
| Config screen shows one value, live link behaves differently | Meeting types, scheduling links, teams and individual working hours each have their **own publish gate**. An unpublished edit does not reach live links. | Check for the "Unpublished Changes" flag, and confirm the live value via `slots/span` rather than the config screen. |
| A demo booked **from the website** has all three `*_cp` fields empty | No CTA on riverside.com carries the parameters. Verified 2026-09-23: 489 of 826 sitemap pages hold a book-demo CTA, 526 link instances, none tagged. The page and Chili Piper are both already wired, so this is not a Chili Piper defect. | Tag the CTAs, not the page. Implementation on Website Dev [`13114930275`](https://riversidefm.monday.com/boards/18397093471/pulses/13114930275); convention and RevOps sign-off on MOPs [`12932161611`](https://riversidefm.monday.com/boards/6257866754/pulses/12932161611). |

## Knowledge Gaps

- **There is no dedicated ZiffDavis link.** Closed 2026-09-17, replacing the earlier "probably `us_enterprise__1-license_website_`" reading: that link offers only the enterprise website type, and every Ziff placement observed in bookings is a website link plus the `meetingTypeId=66abce29-...` override (`us_enterprise__1-license_website_`, `us_agency_51-200_1-license__`, `eu_agency_51-200__website_`, `eu_agency_201-1000__website_`) or the EU router `bd-handoff-europe-enterprise`. Of the two links named after `_10d_`, `sales_intro_inbound_agency_10d_` has zero members and cannot book, and `sales_intro_inbound_agency_10d_-1` has 8 Agency hosts and no Ziff traffic. That `-1` link is the natural candidate for the structural fix in Known Issues; whether its pool matches what Ziff should get is a sales decision, not read here.
- **Host pools: the MCP puts names to them.** `scheduling-link-list-round-robin` with `filterLinkSlugs` returns each link's `members` with name and email, which closed the opaque-ids problem on 2026-09-17 (pools for the five links in Known round-robin links are recorded there). The remainder of this gap stands for links not yet listed. Original note: **Host pools read from config for one link only, and the members are opaque ids.** `GET /api/distribution-service/v1/public/tenant/riverside.fm/distribution/<distributionId>/users?productFeature=RoundRobinSchedulingLink` fires on page load and returns the permitted pool, which is what a "is this link restricted to region X" question actually needs - HubSpot can only ever show who *did* host. For `bd-handoff-europe-enterprise` it returns five users (`66fc07e2a3efd5618919327e`, `69ca5f735b8c70352c480f46`, `69f701ed492f0690d85f33b2`, `6770fd665680873184acfbe9`, `66e934e0a8ff1b4d103fe32c`), reassignment `SameUser`, and `allowPickingAssignee: true`. Those ids are ChiliPiper user ids with no name in any public response and no mapping to HubSpot owner ids. **Untried lead:** the MCP connector exposes `user-find-by-ids` and `user-read`, which should put names to them without ChiliCal - not yet attempted. The other links' pools have not been read. **Five ids now have names**, joined 2026-09-20 from the public meeting endpoint's `hostId` against the host name in the same booking's HubSpot `hs_meeting_body`: `69f9b0c279566997ebfa81ca` Alan Kirschberg, `6882337e249ddb0e576bbf0a` Ori Tal, `64d28ecaadd7ec5090cc7403` Shayan Habibi, `68dbea3c8408bb380f4d213c` Nicole Passarelli, `69d3c9e3312a228f737d8510` Vincent Katz. The same join works for any host who has one Chili Piper booking in HubSpot.
- **The full inventory of affiliate links is not captured.** Ziff's five placements are now listed (Known round-robin links); other affiliates' are not. Other affiliates (Pursuit, SmartReachAI, memoryBlue, Boscia) may carry the same malformation.
- **Whether other affiliate reps also attend every booking is unmeasured.** The Ziff Davis case in Known Issues was found from one complaint, not a sweep. The check is cheap: a contact with a high `num_associated_deals` spanning unrelated companies. On 2026-09-16 only six contacts portal-wide had 15 or more, and `charles.green@swzd.com` led at 58 against 25 for the next.

Closed 2026-09-17: "the `meetingTypeId` override is verified at the calendar level only" (a completed booking with it stamped `_10d_` and captured the `*_cp` tags; one without it stamped the link's own type and lost them). Closed 2026-09-16: "no Chili Piper MCP connector exists" (one does, and this doc's Reading live config now leads with it), and "admin routes are gated for `hanan.amos@riverside.fm`" (access confirmed working).

## Related Systems

- `systems/owned/hubspot.md` - the `*_cp` fields Chili Piper stamps, and vendor attribution
- `systems/owned/marketing-website.md` - where the `__website_` links are embedded
- `references/integration-debugging.md` - the network-trace and edge-guard techniques used here
- `.claude/skills/inbound-demo-reply/` - uses the concierge-router link family
