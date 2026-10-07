# Pain-by-Title Map - Inbound Demo Requests

Messaging asset for cold replies to inbound demo requesters. For each type of person who fills the demo form, this records the pain they're actually trying to solve, the words they use for it, and a ready one-clause insert that names it back to them.

**This is not a pricing analysis.** Plan and price questions appear constantly in the data and are recorded as pain signals, but nothing here recommends a price or a discount.

- **Data window:** 2026-02-07 to 2026-08-07 (6 months)
- **Built:** 2026-08-07
- **Refresh:** re-run quarterly. Verbatims decay fast once packaging changes.

## How to use this file

Read **one cluster at a time**. Find the requester's title, jump to that `##` section, and use:

1. The **top pain** that matches their form comment.
2. The **email insert** verbatim, or lightly reshaped.
3. A **verbatim** only as internal calibration. Never quote another customer back at a prospect.

Then read **Cross-cutting findings** below once. It changes which pain you should lead with, regardless of cluster.

## Data provenance and limits

Read this before trusting any number here.

| Source | What it gave | n |
|---|---|---|
| HubSpot `form_comment` on demo-request contacts, `enterprise_form_submission_date` in window | **Every verbatim in this file.** Title, company, seat count, booking status, buyer's own words | 2,149 (2,206 pulled, 57 internal/test/QA records stripped) |
| HubSpot closed deals + pre-opps, `closedate` in window, `pain_points` populated | Pain ranking and the won-vs-lost comparison | 3,095 (808 won, 2,287 lost) |
| Gong via Omni (`omni_dbt_mrt__dim_meetings`) | Cluster sizing and firmographics only | 300 intro/discovery calls |

**Three limits that matter:**

1. **No Gong verbatims exist in this file, and that is not an oversight.** Omni's Gong topic exposes meeting metadata only: title, date, owner, activity type, outcome, form job title, company, industry, employee count. There is no call brief, summary, key-points, tracker, or transcript field. `pickTopic` for "call briefs, summaries, transcripts" resolves to `Hubspot Contacts`, confirming no call-content topic is modelled. Gong is therefore used for sizing, never for quotes. **To get real call verbatims, someone has to read calls in the Gong UI or the analytics team has to model call content into Omni.**
2. **Deal `pain_points` is AE-authored or AI-summarised text, not buyer words.** It's excellent for ranking pain and comparing won against lost. It is never quoted here as a verbatim. Same for `clay_close_lost_reasoning`, which HubSpot documents as an AI-generated narrative.
3. **`query_crm_data` (SQL) is permission-blocked on this connector**, so deals could not be joined to contact job titles. Deal-level pain is therefore clustered by use case, not by title. Title clusters come from the form-comment corpus. Fixing the connector permission would let a future run tie deal outcomes directly to titles.

Quotes are reproduced exactly as submitted, typos and all. Plan gating described in the "how Riverside solves it" lines is **verify-before-publish**: it reflects what these buyers report hitting, not a pricing-page audit.

---

## Cross-cutting findings

Read once. These override cluster-level instinct.

### 1. The demo form is a packaging triage surface, not a pain confession

The single most common theme in **every cluster** is some version of "which plan do I need, how many licenses, what does it cost." Across the corpus, 24% to 39% of comments per cluster carry **no pain signal at all** beyond wanting to talk.

Most inbound demo requesters are not greenfield buyers with an unnamed pain. They're **existing or near-existing users who hit a wall**: a feature moved behind Business, a webinar cap, a second seat they can't add. Several are openly annoyed the form is in the way.

> "this is annoying AF just let me upgrade without booking a demo" - Marketing Lead @ Clarify Inc. (form comment)

> "I didn't realise we need the Business level account to access Producer mode - we have a recording scheduled on Friday so would like to upgrade ASAP please!" - Marketing Manager @ STRAT7 (form comment)

> "Not really starting out on the right foot here that I can’t get an answer on price immediately and no ability to talk to someone immediately." - CEO @ Sideline Sports and Entertainment (form comment)

**Implication for cold replies:** the highest-converting move is often to remove friction, not to name a deep pain. When the comment is a packaging question, answer it and get out of the way.

### 2. Where won and lost deals disagree on the pain

From 3,095 closed records with pain text. Percentages are share of won (n=808) vs share of lost (n=2,287).

| Pain theme | Won | Lost | Gap |
|---|---|---|---|
| Live streaming / webinars | 40.8% | 32.1% | **+8.8** |
| Recording quality / reliability | 49.4% | 40.7% | **+8.7** |
| Editing speed / post-production | 69.8% | 63.2% | +6.6 |
| API / integration / SSO | 15.5% | 9.0% | +6.5 |
| Repurposing / clips / social | 28.0% | 22.1% | +5.8 |
| Storage / hours / limits | 29.5% | 24.3% | +5.1 |
| Training / internal comms | 11.4% | 13.2% | -1.9 |
| Pricing / budget | 12.0% | 14.5% | -2.5 |
| **Remote guests / interviews** | 33.4% | 42.1% | **-8.7** |

Top lost reasons: **"Need does not justify enterprise cost" (1,073 of 2,287 losses, 47%)**, "Went dark" (220), "Use Case - No Enterprise Features Needed" (131), "No Budget" (115), "No need for multiple licenses" (84).

**The actionable read:** "I want to record remote interviews" is the **weakest** hook in the file. It's the pain most associated with losing, because it's a Pro-shaped need that doesn't justify Business. Scale, throughput, quality at volume, and integration are the pains that correlate with winning.

So when a form comment says only "record remote interviews," don't mirror that back. Look for the adjacent scale signal (team size, seat count, cadence, audience size) and name **that** instead.

### 3. Named competitors

In form comments the recurring displacement targets are **Zoom** (dominant, especially for webinars and quality), **StreamYard**, **Squadcast/Descript** (post-acquisition instability is a live tailwind), **Teams + OBS**, and **Goldcast** (enterprise webinar). In the deal `competitor` field only 15 records were populated at all (Goldcast 13, Zencastr 1, Contrast 1), so competitor data lives in the comments, not the CRM field.

### 4. Cluster index

| Cluster | Form comments | Gong intro calls | Confidence |
|---|---|---|---|
| [Founder / CEO / Owner](#founder--ceo--owner) | 629 | 74 | High |
| [Marketing (generalist)](#marketing-generalist) | 200 | 25 | High |
| [Producer / Production](#producer--production) | 136 | 23 | High |
| [Agency / Production Company](#agency--production-company) | 118 | 13 | High |
| [Podcast host](#podcast-host) | 86 | 5 | High |
| [Social / Video](#social--video) | 78 | 20 | High |
| [Content Marketer / Editorial](#content-marketer--editorial) | 66 | 8 | High |
| [Marketing Ops / Demand Gen](#marketing-ops--demand-gen) | 32 | 6 | Medium |
| [Enterprise / IT buyer](#enterprise--it-buyer) | 29 | 3 | Medium |
| [L&D / Training](#ld--training) | 23 | 4 | Medium-low |
| [Internal Comms / Corp Comms](#internal-comms--corp-comms) | 23 | 18 | Medium |
| [Education / Academic](#education--academic) | 54 | n/a | See section |
| [Unclustered residual](#unclustered-residual) | 672 | 101 | n/a |

No cluster fell below the ~5 low-confidence threshold on form comments. Gong counts are thin for several clusters and are used for sizing only.

---

## Founder / CEO / Owner

**Sample:** 629 form comments, 74 Gong intro calls. 470 of 629 booked. Confidence: high.

Titles: Founder, CEO, Chief Executive, Owner, President, Managing Director, Principal, COO, General Manager, Geschäftsführer, Inhaber, Chairman, Executive Director.

The broadest cluster and the least homogeneous. Many are solo or very small operators whose title outranks their team size. Treat firmographics, not title, as the qualifier here.

### Pain 1 - They can't work out what they need to buy (103 of 629, 16%)

The licence model doesn't map to how they think about their business. They ask whether a licence is per show, per person, or per device.

> "No idea how many licences I need. Want to begin a webinar series for my 40 person marketing agency." - Managing Director @ Amplified (form comment)

> "I'm unsure how many licenses I need. I am building a podcast agency and will host several shows. Is the license per show or per user?" - VP Community Access @ Cactus Jade (form comment)

> "I am not sure what the licenses mean or how many we'd need." - Founder/Lead Curator @ Change Narratives (form comment)

**How Riverside solves it:** licences are per person, not per show or per guest. Guests never need a licence. Business adds admin control over who holds which seat.

**Email insert:** `Founders usually come to us when the licence maths stops matching how their team actually works.`

### Pain 2 - Pricing and packaging opacity blocks the decision (128 of 629, 20%)

They want a number before a conversation. Being routed to a sales call reads as friction, and some say so bluntly.

> "Not really starting out on the right foot here that I can’t get an answer on price immediately and no ability to talk to someone immediately." - CEO @ Sideline Sports and Entertainment (form comment)

> "I need a short video demo. 1-2 minutes that shows me what custom layout options exist and what pricing would be. I'm not ready for a sales call yet" - Co-owner @ New Thresholds (form comment)

> "We are a non profit and want to start a pod cast" - CEO @ Crossroads4Hope (form comment)

**How Riverside solves it:** self-serve tiers are published and buyable without a call. Business is quoted because seat mix and features vary.

**Email insert:** `Founders usually come to us wanting a number before a meeting, not after one.`

### Pain 3 - A single gated feature is blocking a dated commitment (119 of 629, 19% webinar/live; overlaps seats)

There's a recording or webinar on the calendar, one capability is behind a tier, and the deadline is days away. This is the highest-urgency pattern in the whole corpus.

> "All I want is to get higher limit than 100 audience for one live recording im hosting. I need it by friday..." - Founder @ Phoenix Learning (form comment)

> "This is a rush request- we need to open more seats for our webinar- we have almost hit 100!" - Co-Founder @ CLF•A Collective (form comment)

> "I need to be able to upload PowerPoints to teach from in the recordings. How much would it cost to add the single feature? Riverside is worthless to me without it." - Founder @ LEO LAW (form comment)

**How Riverside solves it:** registrant capacity scales by webinar tier, and upgrades take effect immediately rather than at renewal.

**Email insert:** `Founders usually come to us with a date on the calendar and one setting in the way.`

### Pain 4 - Editing is the bottleneck they personally absorb (77 of 629, 12%)

No production team, so the founder does post themselves, or is trying to hand it to one other person.

> "Looking to create before an after of jobs, Educational content, and social media content. Looking for AI editing so I don’t have to learn the editing process" - General Manager @ Pella Gateway (form comment)

> "I'm actively using this and just want to get a second editor seat ASAP. Our editor is standing by for access." - CEO @ PowerOutage.com (form comment)

> "I need the possibility to have a producer and an editor working together in one studio (one project) - especially for post production." - Founder @ wishler GmbH (form comment)

**How Riverside solves it:** recording, AI-assisted editing, clips, and transcripts happen in one place, so nothing gets exported to a separate editor first. Editor and producer seats let a second person work without sharing the owner's login.

**Email insert:** `Founders usually come to us when they're still the one doing the edit.`

### Pain 5 - Interview-format shows, at genuinely small scale (61 of 629, 9%)

**Flag this pain as a downgrade signal.** It's the pain most correlated with losing (see cross-cutting finding 2). Real, frequently stated, and usually Pro-shaped.

> "We want to launch an interview style Podcast" - Operating Partner @ Sounder Partners (form comment)

> "Just need to use this for myself to record podcast episodes with guests." - Founder @ AppSecFamily (form comment)

**How Riverside solves it:** separate local tracks per participant at up to 4K, so guest internet quality doesn't degrade the recording. Fully covered on self-serve tiers.

**Email insert:** `Founders usually come to us when guest audio quality starts costing them episodes.`

---

## Marketing (generalist)

**Sample:** 200 form comments, 25 Gong intro calls. 173 of 200 booked. Confidence: high.

Titles: Marketing Manager, Marketing Director, Head of Marketing, VP Marketing, CMO, Marketing Lead, Marketing Coordinator, Marketing Specialist, Product Marketing.

The strongest-converting cluster relative to size, and the one where webinars dominate hardest.

### Pain 1 - Webinar attendee caps block the programme (73 of 200, 36%)

The most concentrated single pain of any cluster. They've outgrown a 100-attendee ceiling, usually Zoom's or Riverside Pro's, and they're sizing the next tier.

> "I'm curious how much you would charge for the business tier of your software. We would like to host webinars for between 1,000 and 3,000 people." - Marketing Associate @ Cotality (form comment)

> "Podcast + webinar capabilities over 100+ attendee cap for Pro." - CMO @ Silent Push (form comment)

> "Currently have a basic plan but looking to use Riverside to run webinars for up to 250 ish people. Need about 5 seats." - Marketing Leader @ Lokalise (form comment)

**How Riverside solves it:** webinar tiers scale registrant and attendee capacity well past 100, with registration pages and reminder emails built in.

**Email insert:** `Marketing teams usually come to us the month their webinar outgrows the attendee cap.`

### Pain 2 - Zoom output isn't usable as marketing content (20 of 200 switching, plus quality mentions)

Zoom is the incumbent and the complaint is consistent: the recording that comes out isn't good enough to publish or cut up.

> "Interested in replacing Zoom and our current video editing software so am curious to see a demo of the product." - Communications & Marketing Manager @ Osterweis Capital Management (form comment)

> "Nutzen derzeit Zoom für Webinare (Paket bis 500 Teilnehmer pro Webinar) und sind an einem vergleichbaren Paket interessiert." - Senior Field Marketing Manager @ Operations1 (form comment)

> "We are using StreamYard for webinars. Looking to consolidate." - Marketing and Web Manager @ Lean Enterprise Institute (form comment)

**How Riverside solves it:** records locally per participant at up to 4K instead of capturing the compressed call stream, so the master is publishable without a re-shoot.

**Email insert:** `Marketing teams usually come to us when the Zoom recording isn't good enough to publish.`

### Pain 3 - One tool instead of a recording plus editing plus hosting stack (24 of 200, 12%)

They're paying for and stitching together three or four tools and want the chain collapsed.

> "Hi there - I want a single solution for editing video for social media, for recording podcasts, and for hosting webinars. This looks perfect" - Head of Marketing & Communications @ Vintners' Federation of Ireland (form comment)

> "Needing to generate webinars, podcasts, and high quality demo videos from sales for website, youtube, etc." - Chief Marketing Officer @ Avantra (form comment)

> "starting a podcast, weekly! Need an easy and professional way to record, edit and publish." - Senior Marketing Manager @ Minoan (form comment)

**How Riverside solves it:** record, edit, clip, caption, and publish in one platform, so no handoff between a recorder, an editor, and a host.

**Email insert:** `Marketing teams usually come to us when three tools are doing the job of one.`

### Pain 4 - CRM and registration integration is a hard requirement (19 of 200, 9%)

Salesforce or HubSpot sync isn't a nice-to-have. Several say a solution is disqualified without it.

> "I am interested in the cost of the Business tier. This tier probably is over spec'd for our needs, but a Salesforce integration is key to any solution we go for." - Marketing Manager @ Groupe Atlantic UK (form comment)

> "Interested in live and simulive webinars incl recording, editing, managing registration + sync with our Salesforce CRM" - Senior Global Customer Marketing @ LinkedIn (form comment)

> "I would like to host webinars with the plaform that supports form embed, video recording quality enhancement and support for integration with Pipedrive" - Lead - Product Marketing @ Kovai.co (form comment)

**How Riverside solves it:** Business supports registration data flowing to the CRM plus API access, so webinar attendance lands against records instead of a CSV.

**Email insert:** `Marketing teams usually come to us when webinar attendance never makes it into the CRM.`

### Pain 5 - Just let them upgrade (39 of 200, 19%)

A large share want to buy and resent the gate. Several already know what they want.

> "I don't think I want a demo - I just want to upgrade to a business account" - Chief Marketing Officer @ RedOwl (form comment)

> "Please just share price for one year. No interested in a long process sales pitch" - Marketing Communications Sr Manager @ Novus International (form comment)

**How Riverside solves it:** the seat and tier change can be quoted and applied without a discovery call.

**Email insert:** `Marketing teams usually come to us already knowing what they want to buy.`

---

## Producer / Production

**Sample:** 136 form comments, 23 Gong intro calls. 103 of 136 booked. Confidence: high.

Titles: Producer, Executive Producer, Podcast Producer, Video Producer, Production Manager, Head of Post-Production, Audio Engineer, Technical Director, Showrunner.

The most technically specific cluster in the corpus. They name features precisely, which makes them the easiest to reply to well.

### Pain 1 - They need producer control and it's behind Business (many state it explicitly)

The defining pain of this cluster. They want to run the session without being on camera: manage guest inputs, stay hidden, control the waiting room.

> "I've used the features on Riverside for Business before and need producer access to manage guests settings and waiting rooms. Would love to know the price to upgrade our 'Pro' account!" - Producer @ Blind Nil Media (form comment)

> "i just need myself and producer to have production access as we interview 1 person. i hvae access as a host but i need my producer ot have acess to other features, get hidden, etc." - Senior Producer @ psh mag (form comment)

> "With one license, will I be able to have the separate host stream and myself produce on the backend?" - Video Producer @ uRun (form comment)

**How Riverside solves it:** the producer role on Business lets a non-participant run the session, control each guest's inputs and outputs, and stay off the recording.

**Email insert:** `Producers usually come to us when they need to run the session without being in it.`

### Pain 2 - Seat model doesn't map to a production crew (38 of 136, 27%)

They think in roles: host, producer, editor, guest. They can't tell which roles consume a licence.

> "I’m assuming I’ll need 1 license per guest on the podcast? Or is this something we only need 1 license for?" - Senior Media Producer @ Banner Athletic (form comment)

> "I'm not sure how many licenses we need. There will be two of us that will need to be able to log in and either record or edit content." - Podcast Producer @ Shift Happens Here (form comment)

> "Need to understand pricing structure to add additional team members to our current license." - Podcasts Producer @ SET THE PIPE (form comment)

**How Riverside solves it:** guests are never licensed. Producer and editor seats are separate roles, so a crew can be assembled without everyone holding a full owner seat.

**Email insert:** `Producers usually come to us when the seat model doesn't match the crew.`

### Pain 3 - Teams and Zoom quality won't survive post (15 of 136 switching, plus quality mentions)

They're being handed footage from a call platform and can't cut broadcast-grade material out of it.

> "Our need is to record video of a doctor using his webcam. We need better quality than is possible through Teams/Zoom." - Producer and Videographer @ Geisinger (form comment)

> "We are looking to replace our current setup (MS Teams + OBS Studio) with a solution like Riverside." - Senior content producer @ The Access Group (form comment)

> "I am a current Squadcast customer. Squadcast video recordings have always been unreliable." - Media Producer @ Predictive Fitness (form comment)

**How Riverside solves it:** separate local tracks per participant at up to 4K, uploaded progressively, so a guest's connection drop doesn't cost the take.

**Email insert:** `Producers usually come to us after a Teams recording couldn't be saved in post.`

### Pain 4 - Teleprompter and script control for guests, not just hosts (16 of 136 editing, overlapping)

They're directing people who aren't performers and need script support pushed to the guest.

> "I need the business license so I can have guests see and record a script read from the prompter function." - Producer, Videographer and Photographer @ Terry Lowenthal (form comment)

> "As a Producer, I would like to add the option to have share and edit the teleprompter with my host(s) as well as share a script/presentation." - Producer @ Patois Production LLC (form comment)

> "Hello! I'm particularly interested in the teleprompter feature, and being able to control guests' inputs and outputs." - Producer @ Realm (form comment)

**How Riverside solves it:** the teleprompter can be shared with guests and co-hosts and driven by the producer during the session.

**Email insert:** `Producers usually come to us when the guest needs the script on screen, not just the host.`

### Pain 5 - Export must land cleanly in a real NLE (16 of 136, 12%)

Riverside is one step in a pipeline that ends in Premiere, Resolve, or Final Cut. Timeline export and frame rate control decide whether it fits.

> "Currently: we live stream our in studio multi-cam podcast using OBS. We record some podcasts remotely using Riverside and edit with DaVinci Resolve." - Producer @ Smilodon (form comment)

> "I'm now at a non-profit and need 29.97fps and producer mode for a project." - Producer @ Real Life Catholic (form comment)

**How Riverside solves it:** Business adds custom frame rates and timeline export, so the material drops into an existing NLE pipeline instead of being re-conformed.

**Email insert:** `Producers usually come to us when the export doesn't drop cleanly into Resolve.`

---

## Agency / Production Company

**Sample:** 118 form comments, 13 Gong intro calls. 87 of 118 booked. Confidence: high.

Titles and orgs: Agency Owner, Studio Manager, Managing Director, Lead Producer, Director, plus company names containing Studios, Productions, Media, Consulting.

Distinct from Producer because the work is **for clients**. Every pain here has a client-boundary shape.

### Pain 1 - They need separate, self-serve workspaces per client (22 of 118, 19%)

The defining agency pain. One account, many clients, each needing their own space without seeing each other.

> "1 Person agency in need to provide up to 5 clients with async-recording option, so they can record with their guests by themselves, while giving me access to all files" - Gründer @ Podcast-Schneiderei (form comment)

> "Looking to have one main account for my business and setup Studios for each client, who can host their own recordings and invite guests without me." - Franchise Owner @ Dolphin Podcasting (form comment)

> "I need to be able to set up workspaces on a per client basis" - Lead Producer @ East Coast Studio (form comment)

**How Riverside solves it:** Business supports multiple studios and workspaces under one account, so each client records independently while the agency keeps access to every file.

**Email insert:** `Agencies usually come to us when every client needs their own studio under one roof.`

### Pain 2 - Producer access is what they're actually buying (26 of 118, 22%)

Same producer-mode pain as in-house producers, but sharper: they're on the hook for the client's session and can't run it from a Pro seat.

> "I need producer access. I was removed from my Pro plan. I have multiple clients for whom I produce podcast episodes." - Business Owner @ Jim Ray Consulting Services (form comment)

> "Would love to demo the producer role in the business plan. We have been using the other plans for years." - Co-Founder @ Podhead Studios (form comment)

> "Hello - I'd like to enquire about adding the input and output control, and custom frame rate options to our plan." - Managing Director @ Liverpool Podcast Studio (form comment)

**How Riverside solves it:** the producer role plus guest input/output control on Business lets the agency run a client's session end to end without appearing on camera.

**Email insert:** `Agencies usually come to us when they're running the client's session but can't control the room.`

### Pain 3 - Brand control, because the output ships under someone else's name (22 of 118, 19%)

Logos, lower thirds, custom fonts, branded captions. Not vanity; it's the deliverable.

> "I currently use Streamyard. I want to switch assuming I can learn how to use Teleprompter, branding, and lower-thirds on Riverside and the editing is easy enough to do." - Owner @ ZAHN Consulting (form comment)

> "What I need added to my plan is an additional studio and ability to download HTML video for daVinci resolve and Custom branding." - Podcaster @ Intimate Walk Global (form comment)

**How Riverside solves it:** Business adds custom branding, fonts, and caption styling, so the output ships in the client's identity rather than Riverside's defaults.

**Email insert:** `Agencies usually come to us when the output has to ship in the client's brand, not ours.`

### Pain 4 - The current setup is too many moving pieces (18 of 118, 15%)

Local recording, remote guests, file transfer, editing, delivery. Each client multiplies the coordination.

> "Currently we are recording everything locally except any out of town guests and it is a lot of moving pieces." - Director of Marketing and Strategy @ Stoking Fire Productions (form comment)

> "Looking to possibly set up an account to record some of my clients shows. We're a podcast production company that edits/mixes shows for clients." - Agency Owner @ The Podcast Haven (form comment)

**How Riverside solves it:** guests join by link with no install, tracks upload during the session, and files land in the agency's workspace automatically.

**Email insert:** `Agencies usually come to us when coordinating each client's recording costs more than the edit.`

### Pain 5 - Licence model doesn't fit a one-person shop serving many clients (26 of 118, 22%)

Sole proprietors with real client volume. Genuinely unsure whether licences are per device, per account, or per client.

> "does the number of licenses apply to the number of devices or is it accounts?" - Studio Manager/Technical Director @ The Wellness Way (form comment)

> "how do the licenses work? I am not quite sure how many I need. I am the owner of a sole proprietorship." - Producer owner @ BOB Stefanov Productions (form comment)

**How Riverside solves it:** licences attach to people, not devices or clients, so one operator can serve many clients on one seat while clients hold their own studios.

**Email insert:** `Agencies usually come to us unsure whether they're buying seats, studios, or clients.`

---

## Podcast host

**Sample:** 86 form comments, 5 Gong intro calls. 63 of 86 booked. Confidence: high on comments, low on Gong.

Titles: Host, Co-Host, Podcaster, Talk Show Host, Radio Host, On-Air Host.

Mostly existing Pro customers. The pain is almost never "how do I record a podcast." It's "the thing I had stopped working" or "I need one more person in here."

### Pain 2 - A capability they used to have moved behind Business (22 of 86 seats, 26%)

The sharpest emotional signal in the corpus. These are loyal users who feel something was taken.

> "We’ve been on the Riverside Pro plan, which has worked very well for us. Unfortunately, we just lost access to host control of the guests’ microphones and inputs." - Host @ The Cribsiders Podcast (form comment)

> "Arrg.. the support team told me that I can't add another Editor unless I switch to a business plan." - Network Engineer @ On Boards Podcast (form comment)

**How Riverside solves it:** host and guest input control now sits with the producer role on Business. Worth handling with care: this cohort reads it as a loss, not an upgrade.

**Email insert:** `Podcast hosts usually come to us when something that used to work is suddenly behind a plan.`

### Pain 1 - They need a second person in the account (22 of 86, 26%)

A co-host or an editor needs their own login. This is the most common Business trigger in the cluster.

> "happy with pro plan just need to add a 2nd editor" - podcast host @ deal diaries (form comment)

> "I'm already a customer. I would just like to add one additional license so that my editor can access the full account. How much would this cost?" - CEO & Co-Host @ Modern People Leader (form comment)

> "Looking to upgrade current plan to business so both myself and co-host can access riverside through our own accounts" - @ 4th and Ward Podcast (form comment)

**How Riverside solves it:** editor and producer seats give a second person their own login and scoped permissions instead of sharing the owner's credentials.

**Email insert:** `Podcast hosts usually come to us the week a co-host or editor needs their own login.`

### Pain 3 - Licence vocabulary means nothing to them (22 of 86, 26%)

"Seats" and "licences" are enterprise words. Several say plainly they don't know what they're being asked.

> "I'm not sure how many licenses we need because I'm not actually sure what we need them for" - podcast host/parent coach @ Parent Coaches Unleashed (form comment)

> "Not sure what seats refers to but no more than 2 logins needed" - Founder, Host @ Barrel LLC (form comment)

> "We are small podcast trying to get going. I don't know how many licenses I will need ??" - CEO @ MANE AF PODCAST (form comment)

**How Riverside solves it:** one seat per person who logs in. Guests are free and unlimited.

**Email insert:** `Podcast hosts usually come to us because "how many seats" isn't a question they can answer yet.`

### Pain 4 - Turning long episodes into short content, fast (21 of 86, 24%)

They have the episode. Getting clips and shorts out of it is the unpaid second job.

> "Looking at using your editor to take long form videos (1-2 hours) in length to make shorts content" - Syndicated Talk Radio Host @ Guadalupe Radio Network (form comment)

> "assist with sound quality, after editing still hearing popping noises. Also how to do it faster, quicker." - Senior Director @ Work Besties Who Podcast (form comment)

**How Riverside solves it:** AI clip generation pulls short vertical cuts from the full episode inside the same platform, with captions applied automatically.

**Email insert:** `Podcast hosts usually come to us when cutting clips takes longer than recording the episode.`

### Pain 5 - Clean handoff to their real editing tool (21 of 86, 24%)

Some hosts edit elsewhere and need the export to behave.

> "I currently have an account I need to update strictly because I need the abiliity to edit in Final Cut Pro seamlessly" - Talk Show Host @ Jason Matheson Media (form comment)

**How Riverside solves it:** Business adds timeline export so the session opens in Final Cut, Premiere, or Resolve with tracks intact.

**Email insert:** `Podcast hosts usually come to us when the export fights their editing app.`

---

## Social / Video

**Sample:** 78 form comments, 20 Gong intro calls. 59 of 78 booked. Confidence: high.

Titles: Social Media Manager, Social Media Strategist, Video Editor, Videographer, Creative Director, Brand Manager, Content Creator, Multimedia Coordinator.

Two distinct sub-shapes: people running webinars that must become social content, and video people who want session control.

### Pain 1 - Webinar capacity, usually against a client or campaign deadline (20 of 78, 26%)

They're sizing capacity for a specific upcoming event and want a number now.

> "We just need to be able to expand webinar sign-ups to 200, we don't need anything else. How much is this, we need to upgrade asap." - Content and Community Manager @ Twirl (form comment)

> "I need to budget a a webinar for a client that requires 500-1000 attendees. My current plan only allows for 100." - Video Editor & Colorist @ Groovy Like a Movie (form comment)

> "I need some guidance ASAP, webinar this Wednesday" - Head of Social Media & Partnerships @ Botika (form comment)

**How Riverside solves it:** webinar tiers scale registrant and attendee limits well past 100, and the change applies immediately.

**Email insert:** `Social and video teams usually come to us with a webinar on Wednesday and a 100-attendee cap.`

### Pain 2 - Full production control over guest devices (14 of 78, 18%)

Video people want to fix a guest's camera or mic mid-session rather than lose the take. They name the feature by its product name.

> "I'm really only interested in "full production control" so that I can switch guest devices and make similar adjustments during a session. I don't have much of a budget but am curious enough to ask." - Creative Director @ Executive Video (form comment)

> "Have the Pro plan but are interested in the full production control feature that allows you to control inputs of guests." - Video Editor @ Trifilm, Inc (form comment)

> "We only need the teleprompter feature for guests. We don't need anything else." - Social Media Strategist @ Pearl Insurance (form comment)

**How Riverside solves it:** full production control on Business lets the host or producer switch a guest's camera, mic, and output during the session.

**Email insert:** `Video teams usually come to us when they can see the guest's mic is wrong and can't fix it.`

### Pain 3 - They're stuck with whatever Zoom hands them (10 of 78, 13%)

They're downstream of someone else's recording choice and can't make it look like brand content.

> "We have a number of people in our company who run webinars. They screen record them and we're stuck with what Zoom delivers." - Video Editor @ MDVIP (form comment)

> "looking for an alternative to zoom to record our podcasts we are a fertility clinic" - Brand Manager @ RMA of New York (form comment)

> "Ich würde gerne Zoom ersetzen durch Ihr Produkt." - Content Creator @ Gorus Media GmbH (form comment)

**How Riverside solves it:** local per-participant recording at up to 4K plus individual tracks, so the editor gets isolated sources rather than a baked composite.

**Email insert:** `Video teams usually come to us because they're editing whatever Zoom decided to hand them.`

### Pain 4 - Interviews and testimonials as a content supply line (14 of 78, 18%)

Customer stories and talking heads, recorded remotely, feeding social and web.

> "need to record remote interviews for social media" - President/Exec Creative Director @ McClure Marketing (form comment)

> "Hoping to use Riverside to capture customer success story interviews. Just looking for a basic demo to get started." - Corporate Design and Brand Manager @ Scale Computing (form comment)

> "I would like to record Q&A sessions, podcasts and video clips for our social channels. (Hopefully move into webinars after that)" - Social Media Manager @ Envigore (form comment)

**How Riverside solves it:** guests join by link with no install and are recorded locally at full quality, so a remote testimonial cuts like a studio one.

**Email insert:** `Social teams usually come to us when customer interviews became a weekly content commitment.`

### Pain 5 - Pricing is hard to find and that itself is friction (17 of 78, 22%)

> "I need pricing. i cannot find anywhere, and thats not a good start :) Pricing will be my first question to save your time." - Founder / Creative Director @ Bird Real Estate media (form comment)

> "I don't need a demo. I am happy with the product. I just need business pricing." - Video Content Creator @ SmartContract, Inc. (form comment)

**How Riverside solves it:** self-serve tiers are published; Business is quoted because seat mix varies.

**Email insert:** `Social teams usually come to us wanting the number first and the demo later.`

---

## Content Marketer / Editorial

**Sample:** 66 form comments, 8 Gong intro calls. 53 of 66 booked. Confidence: high on comments, low on Gong.

Titles: Content Marketing Manager, Content Strategist, Head of Content, Content Lead, Editor, Editor in Chief, Editorial Director, Managing Editor.

Highest booking rate in the corpus (53 of 66). Two sub-shapes: B2B content marketers running webinars, and editorial teams at publishers.

### Pain 1 - Webinar programme outgrew the tooling (18 of 66, 27%)

They're running a real webinar programme and the platform is the constraint. Attendee counts are specific.

> "I produce webinars for a number of organizations. A lot of my events get 150-250 live attendees so I need something bigger than your webinar package" - Content Lead / Content Specialist @ Talk Coded (form comment)

> "I currently use StreamYard to produce our webinars. I'm looking for an alternative." - Senior Content Strategist, Partner Ads @ Google (form comment)

> "Looking to see how this would work for webinars, online summits, demos, and SMM clips from recordings." - Content Marketing Team Lead @ GotPhoto.com (form comment)

**How Riverside solves it:** webinar tiers handle several hundred to several thousand attendees, and the same recording feeds clips without a separate export.

**Email insert:** `Content teams usually come to us when the webinar programme outgrew the webinar tool.`

### Pain 2 - Getting a distributed editorial team into one account (17 of 66, 26%)

Publishers with real headcount need several named people recording and editing. They ask for seat quotes directly.

> "We are familiar with the platform and really would just like a quote on a 7 seat business plan." - Editor, Branded Content @ JAMA (form comment)

> "One of my editors has a paid account with you and I'm interested in having other members of the team move to your platform. Can you give me a quote for a business license for seven users?" - Editor in Chief @ Science and Medicine Group (form comment)

> "I don't need a lot of licenses. But there are features in the Business Package that would be valuable for a single user/producer like myself" - Editor @ SVG Europe (form comment)

**How Riverside solves it:** Business consolidates individual paid accounts into one workspace with per-person seats, shared assets, and central admin.

**Email insert:** `Content teams usually come to us when three editors are each paying for their own account.`

### Pain 3 - Multi-location recording then publish, as one workflow (16 of 66, 24%)

Contributors in different cities, one show, and a publishing deadline.

> "We need a podcast recording platform that allows 4 of us to record from 4 different locations and then edit and publish our podcast." - Editor @ Podcaster (form comment)

> "Mainly looking to onboard a small team for editing purposes" - Editor-in-Chief, CARS @ Ontarioduplex (form comment)

> "Looking to use riverside initially to record / edit one-on-one interviews for publication on Sustainable Investor, but later other group titles" - Editorial Director @ Whitehall Financial Media (form comment)

**How Riverside solves it:** every participant records locally in their own location, tracks land in one project, and editing plus publishing happen in the same place.

**Email insert:** `Content teams usually come to us when four contributors in four cities have to ship one episode.`

### Pain 4 - Brand consistency on published assets (overlaps guests, 11 of 66, 17%)

Captions, fonts, and teleprompter for both host and guest, because the output carries a masthead.

> "already a user just want custom branding for captions and teleprompter for host and guest." - Digital Content Manager @ Quorum (form comment)

**How Riverside solves it:** Business adds custom fonts, branded captions, and a teleprompter shareable with guests.

**Email insert:** `Content teams usually come to us when published video has to match the brand exactly.`

### Pain 5 - Repurposing one recording into many assets (18 of 66 webinar/clip overlap)

The recording is raw material for clips, social, and written derivatives.

> "Interested in leveraging Riverside for webinars, video content production, AI highlights and editing, possible other use cases. Would love to move quickly :)" - Content Lead @ Zip (form comment)

> "We would like to look at podcasts, webinars and tutorial videos." - Digital Content Strategist, APAC @ LexisNexis Australia (form comment)

**How Riverside solves it:** AI highlights, clips, transcripts, and captions come off the same recording, so one session produces the full asset set.

**Email insert:** `Content teams usually come to us when one recording has to become eight assets.`

---

## Marketing Ops / Demand Gen

**Sample:** 32 form comments, 6 Gong intro calls. 27 of 32 booked. Confidence: medium. Small but exceptionally coherent.

Titles: Marketing Operations Manager, Demand Generation Manager, Head of Growth, Director of Growth, Revenue Operations Manager, Growth Marketing Manager.

The most focused cluster in the file. Webinars appear in 17 of 32 comments (51%), the highest concentration anywhere.

### Pain 1 - Scaling a webinar programme past its current ceiling (17 of 32, 51%)

They own webinars as a pipeline channel and are hitting registrant limits. They quantify precisely.

> "We would like to understand how riverside can help in terms of scaling our webinars." - Senior Specialist, Marketing Ops @ FutureBridge (form comment)

> "Just want to know, what the pricing is for the webinar package with around 200 registrants. We are close to 100 right now and want to get an overview what it would cost to scale." - Revenue Operations Manager @ paretos GmbH (form comment)

> "I've used Riverside in the past. I don't want a demo. Just want business plan pricing for 1,000 webinar registrants." - Head of Demand Generation @ Flowhub (form comment)

**How Riverside solves it:** registrant capacity scales by tier with registration pages, reminders, and attendance data included.

**Email insert:** `Demand gen teams usually come to us the quarter webinars became a pipeline number.`

### Pain 2 - Webinar data has to reach the CRM (8 of 32, 25%)

Salesforce sync, API access, and embedded registration forms. Without them the channel can't be attributed.

> "We need Salesforce integration, and high attentance numbers." - Marketing Operations Manager @ AG Grid (form comment)

> "want to have access to an API with my current account" - Marketing Operations Manager @ Thoropass (form comment)

> "Love the free trial however I am looking for API and registration form embed capabilities" - Director of Growth @ Innovative Communication Solutions (form comment)

**How Riverside solves it:** Business adds API access and CRM-bound registration, so attendance lands on records instead of a spreadsheet.

**Email insert:** `Demand gen teams usually come to us when webinar attendance can't be attributed to pipeline.`

### Pain 3 - Displacing Zoom or Goldcast on production quality (5 of 32, 16%)

They're in an active evaluation, often against a renewal date, and quality is the differentiator.

> "Considering switching from Zoom for upcoming webinar (need decision by end of week). Audience usually 3-5k." - Growth Marketing @ Predict Wind (form comment)

> "We’re evaluating Riverside as a potential alternative to Goldcast for live and simu-live webinars, with a focus on higher production quality" - Senior Marketing Operations Manager @ Calendly (form comment)

> "Currently using Zoom for webinars, but video quality is low." - Demand Generation Manager @ Marchex (form comment)

**How Riverside solves it:** studio-quality local recording plus live and simulive delivery, so the webinar and the post-event asset come from one session.

**Email insert:** `Demand gen teams usually come to us with a Goldcast renewal date and a quality problem.`

### Pain 4 - Turning webinars into short-form assets (3 of 32, 9%)

Low count, but unambiguous when present.

> "Mainly looking to clip lon-form webinars into 2-5 minute videos" - Growth Marketing Manager @ FormAssembly (form comment)

> "We would like to find out more information on pricing for use with webinars and editing the video after the webinar has taken place so we can reuse these clips for social promotion" - Sr. Demand Generation Program Strategist @ iCIMS (form comment)

**How Riverside solves it:** AI clips and in-platform editing run off the webinar recording, so promotion assets don't need a separate edit cycle.

**Email insert:** `Demand gen teams usually come to us when the webinar recording never becomes promo clips.`

---

## Enterprise / IT buyer

**Sample:** 29 form comments, 3 Gong intro calls. 23 of 29 booked. Confidence: medium on comments, too low on Gong to characterise.

Titles: CTO, CIO, Head of IT, IT Manager, IT Director, Procurement, Procurement Manager, Technology Procurement.

Not the user. They're buying, securing, or administering on someone else's behalf, so the pain is never about recording.

### Pain 1 - Certifications gate the purchase (3 of 29 explicit, high stakes)

SOC 2 Type II and ISO 27001 are stated as preconditions, not questions.

> "Inquiring about pricing for business plan because we need the SOC2 type II & ISO27001 certification in order to use your services." - Information Technology Manager @ Blue Horizons Group (form comment)

> "I am interested in getting more information about Riverside, including pricing and SOC2 reports. We are nearing a decision soon." - Director Of Information Technology @ WaterFurnace International (form comment)

> "I would like to understand the costs and security/privacy protections applied to business accounts" - Head of IT @ PEI Group (form comment)

**How Riverside solves it:** Business is the tier that carries enterprise security controls and the compliance documentation review requires. **Route these to the regional sales lead. Do not answer certification scope from marketing.**

**Email insert:** `IT teams usually come to us because a security review is holding up a tool their content team already picked.`

### Pain 2 - Central licence administration (10 of 29, 34%)

They need to assign and revoke seats centrally. Individual credit-card accounts across a company is the problem they're solving.

> "Want to know if you have business accounts that allow us to manage (assign/unassign) licenses for our employees." - CTO @ Empower AI 365 (form comment)

> "We are a small non-profit looking to manage riverside use for just a few users. I'd like to know what pricing looks like, as I'd like to manage this as a group, rather than individual licenses." - CTO @ Global Healthy Living Foundation (form comment)

> "I’d like to know the pricing for a business account. We’d like to have multiple people edit and manage content." - CTO @ Yamaha Music Innovations (form comment)

**How Riverside solves it:** Business provides central seat administration and SSO, so IT assigns and revokes access instead of chasing individual subscriptions.

**Email insert:** `IT teams usually come to us to replace a handful of personal subscriptions with one managed account.`

### Pain 3 - Formal procurement process (11 of 29 pricing-shaped, 38%)

Structured, unemotional, sometimes an RFP. They want a quote and a contact, not a discovery call.

> "Hello, I would like to book a demo and understand pricing for 2 - 5 licenses for Steelcase Inc." - Procurement @ Steelcase (form comment)

> "We are sending out an RFP soon for Webinar and Livestream services. please provide us a contact email that should receive the RFP." - Procurement Manager @ Lisinski Law Firm (form comment)

**How Riverside solves it:** Business is quoted and contracted, with named commercial contacts for RFP and vendor onboarding. **Route vendor-onboarding and RFP asks to the regional lead per the skill's handoff table.**

**Email insert:** `Procurement teams usually come to us needing a quote and a contract owner, not a demo.`

### Pain 4 - Consolidating a tool their content team already chose (5 of 29, 17%)

The business unit picked Riverside; IT is evaluating after the fact.

> "we’re currently reviewing podcast/video recording and editing platforms for our content team" - Director, Technology Procurement @ Computershare (form comment)

> "I already have a Pro account, but it would be great if I could have someone external editing some of the content for me." - CTO @ Avona GmbH (form comment)

**How Riverside solves it:** Business consolidates existing self-serve accounts into one administered workspace without losing the content already recorded.

**Email insert:** `IT teams usually come to us after the content team already made the choice.`

---

## L&D / Training

**Sample:** 23 form comments, 4 Gong intro calls. 16 of 23 booked. **Confidence: medium-low.** Above the ~5 threshold but thin, and Gong is too small to characterise. Treat these pains as directional. Re-check next refresh.

Titles: Manager Learning and Development, Senior Training & Enablement Manager, Sales Enablement Lead, Client Enablement Specialist, Head of Customer Communications, Training and Events Manager.

Note the overlap: L&D people frequently self-describe as enablement, and enablement titles behave like Internal Comms. Read both sections together.

### Pain 1 - Simulive: pre-record the expert, deliver it live (8 of 23, 35%)

The defining L&D shape. Senior speakers can't attend live, so the session must be recorded ahead and played as if live.

> "We are looking to use this software for our Simulive webinars. This will allow us to capture our Keynote speakers before hand and edit and upload their sections to our platform." - Senior Training & Enablement Manager @ Alianza (form comment)

> "Looking for a platform to record podcasts/webinars with global speaker guests." - Manager, Learning and Development @ American Express (form comment)

**How Riverside solves it:** record contributors in advance, edit, then run the session as simulive with live Q&A alongside.

**Email insert:** `L&D teams usually come to us because the expert can't make the live session.`

### Pain 2 - More director or admin seats across the organisation (8 of 23, 35%)

Training content is produced by many people in different departments. A single Pro account doesn't cover it.

> "Currently have a Pro subscription but wish to get a Business profile as we require more director seats within the organisation." - Manager Learning and Development @ Australian Dental Association (form comment)

> "We are looking to add licenses and would like to discuss some of the differences between our current webinar plan and the business plan." - Client Enablement Specialist @ Evosus (form comment)

> "i'm trying to understand whether we are charged per user or per workspace. trying to find the best package based on that." - Loan Officer & Sales Enablement Lead @ eLEND® (form comment)

**How Riverside solves it:** seats are per person with role-scoped permissions, so training content can be produced across departments under one administered account.

**Email insert:** `L&D teams usually come to us when training content is being made by more people than the plan allows.`

### Pain 3 - Async recording with a script, for non-presenters (small n, clearly stated)

They're recording people who aren't comfortable on camera and need script support plus no scheduling overhead.

> "We're an existing customer of Pro and Live however our needs have adapted, and want to be able to async record with our customer with a teleprompter/script." - Head of Customer Communications @ Data Literacy Academy (form comment)

**How Riverside solves it:** async recording lets a contributor record themselves on their own time with a teleprompter script, and the file lands in the team's workspace.

**Email insert:** `L&D teams usually come to us when scheduling everyone live stopped being realistic.`

### Pain 4 - Replacing Zoom for training delivery (3 of 23, 13%)

> "looking at upgrading current plan to replace zoom for webinars, and would require a customised plan for participants." - Sales Enablement Lead @ Y Soft (form comment)

> "We’re exploring alternative platforms for our online events, as we already use you for our podcast seems sensible to start here!" - Training and events manager @ Music Mark (form comment)

**How Riverside solves it:** one platform covers live delivery and the reusable recording, so training sessions become a library rather than a Zoom archive.

**Email insert:** `L&D teams usually come to us when Zoom recordings aren't reusable as training material.`

---

## Internal Comms / Corp Comms

**Sample:** 23 form comments, 18 Gong intro calls. 20 of 23 booked. Confidence: medium.

Titles: Director of Communications, Head of Communications, Communications Manager, Communications Coordinator, Communications Specialist, Internal Communications, Comms and PR Manager.

Note: 18 Gong intro calls against 23 form comments is the highest call-to-comment ratio in the file. This cohort books and shows up.

### Pain 1 - Budget is genuinely constrained, and nonprofit status is the lead detail (8 of 23, 35%)

The most budget-sensitive cluster proportionally. Many are nonprofits, associations, or public sector, and they open with it.

> "Hello! I'd like to know if you offer a non-profit discount. Thank you!" - Director of Communications @ Methods Innovation (form comment)

> "We're a nonprofit, if there's a discount available." - Marketing and Communications Director @ American Society for Reproductive Medicine (form comment)

> "We're a public school district, and hoping we can dip our toe into this experience. Any discounts or extended trial periods would be appreciated." - Director Of Communications @ Perkins Local School District (form comment)

**How Riverside solves it:** **do not answer discount questions.** Route to the regional sales lead per the skill's pricing rule. Acknowledge the constraint, hand off.

**Email insert:** `Comms teams usually come to us with a real content mandate and a budget that hasn't caught up.`

### Pain 2 - Their security team is the actual gatekeeper (3 of 23, 13%)

Comms wants the tool; security decides. SSO and certifications get named in the first message.

> "Could you please provide a SOC 2 Type II report, ISO 27001 certificate and the corresponding certification report." - Internal Communications @ nextbike (form comment)

> "We contacted you because or security team needed extra information about security standards and you suggested getting a business subscription." - Head of Communications @ Trans.eu Group (form comment)

> "The main concern is the pricing, as our cybersecurity team said we are required to have the SSO feature." - Communications Coordinator @ 1-800-GOT-JUNK? (form comment)

**How Riverside solves it:** SSO and enterprise security controls sit on Business, with compliance documentation available through sales. **Route certification requests to the regional lead.**

**Email insert:** `Comms teams usually come to us because security won't sign off without SSO.`

### Pain 3 - Producing internal video faster than an agency cycle (2 of 23, 9%)

Speed and self-sufficiency. They want to stop waiting on external production.

> "We're looking for a video editing tool to speed up our process. The video hosting and analytics function is also useful." - Communications Coordinator @ 1-800-GOT-JUNK? (form comment)

> "We're expanding video production for webinars, live demos and others. Need to understand if "Business" option is worth it" - Marketing and Communications Specialist @ Coreflux (form comment)

**How Riverside solves it:** record, edit, caption, and host in one place, so internal video ships in a day without an external editor.

**Email insert:** `Comms teams usually come to us when internal video takes three weeks to turn around.`

### Pain 4 - Returning after a competitor broke (small n, but a live tailwind)

Squadcast's wind-down and Descript instability are actively pushing this cohort back.

> "We are a nonprofit that used Riverside a few years ago. We had multiple studios then. It worked great, but our editing tool, Descript, bought Squadcast, so we dropped Riverside. Squadcast is shutting down, and Descript is buggy." - Director of Communications @ Renovaré (form comment)

> "My firm Hashgraph, formerly Swirlds Labs, had a contract with Riverside a year or two ago and we are looking to engage again asap." - Senior Marketing & Communications Manager @ Hashgraph (form comment)

**How Riverside solves it:** recording plus editing plus hosting in one platform removes the dependency that broke last time.

**Email insert:** `Comms teams usually come back to us when the tool they left for stopped being maintained.`

### Pain 5 - Volume-based capacity questions (small n)

> "We anticipate needing about 20 to 30 hours per month for multi tracks. Curious to know pricing" - communications manager @ Society of Actuaries (form comment)

> "need webinar ability for more than 100 registrants." - Comms and PR Manager @ Ferrum Health (form comment)

**Email insert:** `Comms teams usually come to us once monthly recording volume outgrew the plan.`

---

## Education / Academic

**Sample:** 54 form comments. Not in the requested cluster list, but it's the fifth-largest real cluster and worth flagging.

**No clean pain signal.** 38% of comments carry no theme at all, the highest share in the file, and the rest split thinly across pricing (24%) and webinars (20%). Only 36 of 54 booked, the weakest rate among sizeable clusters.

Per the skill's own filter rules, academic domains with 1 licence are auto-filtered as DQ. Treat this cluster as **routing information, not messaging material.** Do not build an insert for it. The 2+ licence override still applies where a real department is buying.

---

## Unclustered residual

**Sample:** 672 form comments (31% of corpus), 101 Gong intro calls.

658 distinct job titles with a long tail: Project Manager, Executive Director, Realtor, Pastor, Attorney, Chief of Staff, Software Engineer, Life Coach, Board Member. No stable pain pattern, and 29% carry no theme at all.

**Do not write messaging against this group.** Its size is a measurement artefact of free-text job titles, not a segment. If a requester's title lands here, fall back to the **cross-cutting findings**: check for a packaging question first, then look for a scale signal in company size or seat count.

**Worth noting for the form itself:** 31% of demo requesters having an unclassifiable title is a data-quality finding. A structured role dropdown on the demo form would make the next version of this map materially sharper.

---

## Open questions for the next refresh

1. **Get real Gong verbatims.** The single biggest gap. Either read calls in the Gong UI for the top clusters, or ask the analytics team to model call briefs and summaries into Omni. Everything here is written language from a form, which is more considered and less emotional than speech.
2. **Unblock `query_crm_data`** on the HubSpot connector so deal outcomes can be joined to job titles. That would turn the won/lost comparison from use-case level into title level.
3. **Validate the interview-pain downgrade signal.** Cross-cutting finding 2 says "remote interviews" correlates with losing. Worth confirming against a title-level join before it drives routing.
4. **Add a role dropdown to the demo form.** Would cut the 31% unclustered residual.
5. **Re-pull after any packaging change.** A large share of these pains are artefacts of current tier boundaries. Move a feature and the top pain in three clusters changes.

---

**How this was built:** generated with Claude (Opus 5) on 2026-08-07 from live HubSpot and Omni queries over 2026-02-07 to 2026-08-07. All verbatims are unedited `form_comment` text from HubSpot contact records. Deal pain rankings derive from AE-authored and AI-summarised `pain_points` fields and are labelled as such rather than quoted. No quote in this file was paraphrased, composited, or invented. Plan-gating statements reflect what buyers reported encountering and are verify-before-publish; pricing and discount questions route to the regional sales lead and are never answered from this file.
