# ticket-hygiene ledger

Two append-only records that make repeat runs safe and quiet. Git history is the audit
trail - never rewrite rows, only append or amend a status in place.

---

## Filed asks

One row per Slack message that INTAKE turned into a ticket. Keyed on **permalink** - that
is the dedupe key, so never file a row without one.

| Permalink | Channel | Author | Filed | Board | Item |
|-----------|---------|--------|-------|-------|------|
| [p1786517209998339](https://riversidefm.slack.com/archives/C07V6N3N5U1/p1786517209998339) | `#marketing-revops` | Daniel Nitsan (RevOps) | 2026-08-13 | MOPs `6257866754` | [12791564247](https://riversidefm.monday.com/boards/6257866754/pulses/12791564247) - audit private-email block on Business Plan forms |
| [p1786624918570059](https://riversidefm.slack.com/archives/C07V6N3N5U1/p1786624918570059) | `#marketing-revops` | Nir Taranto | 2026-08-14 | MOPs `6257866754` | [12801450250](https://riversidefm.monday.com/boards/6257866754/pulses/12801450250) - investigate why demo booking showed no slots |
| [p1786968575063189](https://riversidefm.slack.com/archives/C09HYP45X7T/p1786968575063189) | `#contact-martech` | Ann Tsunakawa | 2026-08-18 | MOPs `6257866754` | [12829098140](https://riversidefm.monday.com/boards/6257866754/pulses/12829098140) - add thomas@autoshopmedia.com to Business subscription list |
| [p1786002339745959](https://riversidefm.slack.com/archives/C09HYP45X7T/p1786002339745959) | `#contact-martech` | Galya Nash | 2026-08-21 | Website Dev `18397093471` | [12861743374](https://riversidefm.monday.com/boards/18397093471/pulses/12861743374) - fix pricing page CTAs for logged-in users |
| [p1786376526960039](https://riversidefm.slack.com/archives/C07V6N3N5U1/p1786376526960039) | `#marketing-revops` | Dan Markel (RevOps) | 2026-08-24 | MOPs `6257866754` | [12877952286](https://riversidefm.monday.com/boards/6257866754/pulses/12877952286) - audit workflow behind 900 riverside-domain new signups |
| [p1787339654435429](https://riversidefm.slack.com/archives/C05TRR8BWBX/p1787339654435429) | `#support-marketing` | Jonan Nicodemus Buot (Support, via `Request for Marketing` bot) | 2026-08-25 | MOPs `6257866754` | [12888737157](https://riversidefm.monday.com/boards/6257866754/pulses/12888737157) - investigate webinar registration emails not reaching signups |
| [p1787725166019109](https://riversidefm.slack.com/archives/C07V6N3N5U1/p1787725166019109) | `#marketing-revops` | Matan Rafic (RevOps) | 2026-08-27 | MOPs `6257866754` | [12908978642](https://riversidefm.monday.com/boards/6257866754/pulses/12908978642) - verify lead level scoring after seat question restored |
| [p1788067125287949](https://riversidefm.slack.com/archives/C07V6N3N5U1/p1788067125287949) | `#marketing-revops` | Daniel Nitsan (RevOps) | 2026-08-30 | MOPs `6257866754` | [12929041147](https://riversidefm.monday.com/boards/6257866754/pulses/12929041147) - audit public-domain reopen on Business Plan forms |
| [p1788093126354929](https://riversidefm.slack.com/archives/C07V6N3N5U1/p1788093126354929) | `#marketing-revops` | Matan Rafic (RevOps) | 2026-08-31 | Website Dev `18397093471` | [12932161611](https://riversidefm.monday.com/boards/18397093471/pulses/12932161611) - add meeting_source_cp params to site book-demo CTAs |
| [p1788215973220659](https://riversidefm.slack.com/archives/C05TRR8BWBX/p1788215973220659) | `#support-marketing` | Junelle Tumala (Support, via `Request for Marketing` bot) | 2026-09-01 | MOPs `6257866754` | [12943009640](https://riversidefm.monday.com/boards/6257866754/pulses/12943009640) - investigate broken unsubscribe link and process opt-out |
| [p1788458181953169](https://riversidefm.slack.com/archives/C07V6N3N5U1/p1788458181953169) | `#marketing-revops` | Daniel Nitsan (RevOps) | 2026-09-04 | MOPs `6257866754` | [12975027464](https://riversidefm.monday.com/boards/6257866754/pulses/12975027464) - check downstream impact of US Agency distribution split |
| [p1789050468568379](https://riversidefm.slack.com/archives/C05TRR8BWBX/p1789050468568379) | `#support-marketing` | Michael John Pepanio (Support, via `Request for Marketing` bot) | 2026-09-11 | MOPs `6257866754` | [13023721254](https://riversidefm.monday.com/boards/6257866754/pulses/13023721254) - confirm unsubscribe status for Zendesk ticket 784082 |
| [p1789375617789999](https://riversidefm.slack.com/archives/D0A4W65A80J/p1789375617789999) | DM to Hanan | Nir Taranto | 2026-09-14 | MOPs `6257866754` | [13038695358](https://riversidefm.monday.com/boards/6257866754/pulses/13038695358) - backfill QBD data and confirm field status |
| [p1789375617789999](https://riversidefm.slack.com/archives/D0A4W65A80J/p1789375617789999) | DM to Hanan | Nir Taranto | 2026-09-14 | MOPs `6257866754` | [13038706421](https://riversidefm.monday.com/boards/6257866754/pulses/13038706421) - route ChiliPiper from the form for ICP leads |
| [p1789375617789999](https://riversidefm.slack.com/archives/D0A4W65A80J/p1789375617789999) | DM to Hanan | Nir Taranto | 2026-09-14 | MOPs `6257866754` | [13038747650](https://riversidefm.monday.com/boards/6257866754/pulses/13038747650) - move HubSpot marketing emails to the .com sender |
| [p1789375617789999](https://riversidefm.slack.com/archives/D0A4W65A80J/p1789375617789999) | DM to Hanan | Nir Taranto | 2026-09-14 | MOPs `6257866754` | [13038748584](https://riversidefm.monday.com/boards/6257866754/pulses/13038748584) - dedup HubSpot contacts and companies |
| [p1789375617789999](https://riversidefm.slack.com/archives/D0A4W65A80J/p1789375617789999) | DM to Hanan | Nir Taranto | 2026-09-14 | MOPs `6257866754` | [13038748884](https://riversidefm.monday.com/boards/6257866754/pulses/13038748884) - collect help-center data for data quality |
| [p1789375617789999](https://riversidefm.slack.com/archives/D0A4W65A80J/p1789375617789999) | DM to Hanan | Nir Taranto | 2026-09-14 | MOPs `6257866754` | [13038736707](https://riversidefm.monday.com/boards/6257866754/pulses/13038736707) - fix industry and persona logic |
| [p1789375617789999](https://riversidefm.slack.com/archives/D0A4W65A80J/p1789375617789999) | DM to Hanan | Nir Taranto | 2026-09-14 | MOPs `6257866754` | [13038748771](https://riversidefm.monday.com/boards/6257866754/pulses/13038748771) - verify cost figures on the performance report |
| [p1789459767342669](https://riversidefm.slack.com/archives/C08DJ6BN3NX/p1789459767342669) | `#webflow-riverside` | Erika Varangouli | 2026-09-16 | Website Dev `18397093471` | [13056979737](https://riversidefm.monday.com/boards/18397093471/pulses/13056979737) - collect post-live fixes for refactored tools pages |
| [p1789543886351999](https://riversidefm.slack.com/archives/C08DJ6BN3NX/p1789543886351999) | `#webflow-riverside` | Ruben Aknin | 2026-09-17 | Website Dev `18397093471` | [13066512344](https://riversidefm.monday.com/boards/18397093471/pulses/13066512344) - embed the new YouTube transcript tool iframe |
| [p1789561613401309](https://riversidefm.slack.com/archives/C05TRR8BWBX/p1789561613401309) | `#support-marketing` | Marc Luigi Lalas (Support, via `Request for Marketing` bot) | 2026-09-17 | MOPs `6257866754` | [13066548936](https://riversidefm.monday.com/boards/6257866754/pulses/13066548936) - confirm unsubscribe status for Zendesk ticket 787856 |
| [p1789573178298899](https://riversidefm.slack.com/archives/C08DJ6BN3NX/p1789573178298899) | `#webflow-riverside` | Nir Taranto | 2026-09-20 | Website Dev `18397093471` | [13087888177](https://riversidefm.monday.com/boards/18397093471/pulses/13087888177) - fix unclickable CTA on the transcription page |
| [p1790040059313429](https://riversidefm.slack.com/archives/C05TRR8BWBX/p1790040059313429) | `#support-marketing` | Edward Vincent Thompson (Support, via `Request for Marketing` bot) | 2026-09-22 | MOPs `6257866754` | [13101389324](https://riversidefm.monday.com/boards/6257866754/pulses/13101389324) - scope Riya Bidani partnership and cohort signup incentive |
| [p1790255414543999](https://riversidefm.slack.com/archives/C0AM2HQMY49/p1790255414543999) | `#website-dev` | Automated page QA pass, commissioned by Jonathan Galili | 2026-09-25 | Website Dev `18397093471` | [13132929448](https://riversidefm.monday.com/boards/18397093471/pulses/13132929448) - fix Press and Product Videos nav links site-wide |
| [p1790255414543999](https://riversidefm.slack.com/archives/C0AM2HQMY49/p1790255414543999) | `#website-dev` | Automated page QA pass, commissioned by Jonathan Galili | 2026-09-25 | MOPs `6257866754` | [13132929674](https://riversidefm.monday.com/boards/6257866754/pulses/13132929674) - exclude staging hostname from Google Ads conversion tag |
| [p1790520473202849](https://riversidefm.slack.com/archives/C05TRR8BWBX/p1790520473202849) | `#support-marketing` | Daniel Santos (Support, via `Request for Marketing` bot) | 2026-09-28 | MOPs `6257866754` | [13146866474](https://riversidefm.monday.com/boards/6257866754/pulses/13146866474) - confirm unsubscribe status for Zendesk ticket 795548 |
| [p1790746552886069](https://riversidefm.slack.com/archives/C05TRR8BWBX/p1790746552886069) | `#support-marketing` | Yael Schechner (Support Knowledge) | 2026-09-30 | Website Dev `18397093471` | [13167532373](https://riversidefm.monday.com/boards/18397093471/pulses/13167532373) - remove lead capture from pricing page Webinar plan (deleted 2026-09-30, see Oct 1 note) |
| [p1790775877337319](https://riversidefm.slack.com/archives/C05TRR8BWBX/p1790775877337319) | `#support-marketing` | Rey Bjorn Castro (Support, via `Request for Marketing` bot) | 2026-10-01 | MOPs `6257866754` | [13178489860](https://riversidefm.monday.com/boards/6257866754/pulses/13178489860) - confirm unsubscribe status for Zendesk ticket 803201 |

> **The ledger on `main` is only as current as the PRs that carried it.** From 2026-08-27 to
> 2026-09-02 the rows for the Aug 27 filing (`12908978642`) and the Aug 30 filing
> (`12929041147`) sat unmerged while both tickets existed on the board, so this table skipped
> from Aug 25 straight to Aug 31 and `main` ran two filings behind. Nothing was double-filed,
> because Step 3 matches against the live boards and not against this file - but the ledger is
> the *permalink* dedupe key, and the boards cannot catch a re-file of an ask whose ticket was
> since closed. Treat an unmerged prior-run PR as a live risk, name it in the run summary, and
> never quietly re-file an ask a pending PR already claims.
>
> **Audit note, 2026-08-31 - not a filed ask, recorded so the decision survives.** Yael
> Schechner's `#support-marketing` request to remove `/blog/is-riverside-free`
> (`p1788100835324759`) was classified **already tracked** against MOPs
> [12930035566](https://riversidefm.monday.com/boards/6257866754/pulses/12930035566), created
> by a `@agent marketing-os` invocation earlier the same evening, so this run filed nothing
> for it. Erika Varangouli then questioned the removal itself in-thread and the decision is
> still open. No row above, because rows are reserved for asks this skill filed.
>
> **This note is deliberately not a dedupe key, and the permalink above is written bare for
> that reason.** Step 2's test is "permalink is not already in `data/ledger.md`" - a
> *file*-level match, not a table-level one - so an audit note can silently suppress a
> re-file. That matters here: `12791564247` was filed to watch for a change and then
> cancelled with no closing comment, and the change landed six days later untracked. If
> `12930035566` is closed without the blog decision actually being made, this ask is a valid
> candidate again. Match on the table rows, not on this paragraph.
>
> **Only rows for asks actually filed belong here.** An ask that was *identified* but not
> filed must stay out, or the next run skips it and it is lost forever. As of 2026-08-11
> two known-untracked asks were deliberately absent because nobody had filed them yet: the
> `#contact-martech` pricing-page CTA bug (Galya Nash, 2026-08-06) and the
> `#marketing-revops` 900-riverside-signups question (Dan Markel, 2026-08-10).
>
> **2026-08-21 - the pricing-page CTA bug is now filed** (row above, Website Dev
> `12861743374`).
>
> **2026-08-24 - the 900-riverside-signups question is now filed too** (row above, MOPs
> `12877952286`). It sat unfiled for 14 days: named as a known-untracked ask in this ledger
> on 2026-08-11 and never picked up, because a daily scan window cannot reach an ask that
> old. The Slack message still had no replies when it was filed. Both of the two asks this
> section originally recorded as deliberately-absent are now closed out, so the carry-over
> list is empty as of this date.
>
> **2026-08-25 - the webinar registration-email non-delivery is now filed** (row above, MOPs
> [12888737157](https://riversidefm.monday.com/boards/6257866754/pulses/12888737157)). Same
> shape again: named as needing a human in the Aug 22, Aug 23 and Aug 24 summaries, each time
> gated on someone checking send logs before it could be filed. The Aug 21 Slack thread still
> had zero replies four days on, so the gate was never going to open on its own. Filed as an
> investigation ticket rather than a fix, because **which system sends that email is itself
> unknown** - MOPs `12659164292` implies Riverside's own hosted webinar page issues the
> registration mail, which would make this Product/Support work. Routed to MOPs `New Requests`
> under the ambiguous-routing rule with the ambiguity stated in the body, not resolved silently.
>
> **2026-08-27 - the `#marketing-revops` lead-level thread is now filed** (row above, MOPs
> [12908978642](https://riversidefm.monday.com/boards/6257866754/pulses/12908978642)). The Aug 24,
> Aug 25 and Aug 26 summaries each carried it as *watch, not file*, on the correct reasoning that
> no remedy had been picked. On Aug 26 Matan Rafic picked one - he restored the license/seat
> question to the in-product forms - and that is the trigger those three summaries named. Filed
> under the `#marketing-revops` announcement inversion: nobody asked MOPs for anything, but a
> Product-side form change created dated MOPs work (does the restored field feed the property the
> lead-level rule reads, and what happens to the ~3 weeks of leads rated while the demotion path
> was dead).
>
> **The watch-list worked, and that is worth recording.** Unlike the pricing-CTA and
> webinar-email cases above, this ask did not rot: a prior run named the exact condition that
> would make it filable ("it lands on us the moment they pick one"), and the next run after that
> condition was met filed it, one day later. A watch flag with a **stated trigger** is a real
> instrument; a watch flag that just says "worth watching" is the thing that decays into a
> repeat-flag loop. Write the trigger.
>
> **2026-08-30 - the Business Plan public-domain reopen is filed** (row above, MOPs
> [12929041147](https://riversidefm.monday.com/boards/6257866754/pulses/12929041147)).
>
> **A closed predecessor ticket is not tracking anything.** MOPs `12791564247` was filed on
> Aug 13 precisely to "make sure the reopen actually lands", then set to **Cancelled** on
> Aug 24 with no closing comment. The reopen landed six days later. Because Step 3 matches
> only against *open* items (`status not_any_of [1, 3, 9]`), the cancelled predecessor never
> surfaced as a match - which is correct, and the reason this ask was filable rather than
> silently absorbed. The generalisation: when a ticket exists whose stated job is to watch for
> a future event, its being closed means the watch is gone, not that the event is handled. Say
> so in the new ticket body and let triage decide, rather than treating the old id as coverage.
>
> **The Thu-to-Sun run gap is real and needs no rule.** The previous run was Thu Aug 27 09:19;
> Fri and Sat are the Israeli weekend, so no run covered Aug 27 09:19 → Aug 29 00:00, and that
> hole recurs every week. It costs nothing: Step 1 searches the last **7 days**, so a two-day
> gap is absorbed with five to spare. Recorded because the Aug 30 run summary proposed fixing
> it with "scan back to the previous run's timestamp, not a fixed 24 hours" - that rule was
> written against a 24-hour window this skill has never had (7 days since `3c963a7`), and
> adopting it would have *narrowed* the window. Check the stated window before writing a rule
> to widen it.
>
> **Prior-run watch flags carried and re-checked, nothing to file:** the `#marketing-revops`
> no-show investigation is still analysis with no cadence/form/routing change proposed (its
> stated file trigger), and Matan's Aug 26 licence-question message is already tracked by
> `12908978642`.
>
> **Generalisation of the lesson below: a gate that depends on someone replying in Slack is
> not a gate, it is a way to never file.** Twice now (pricing-page CTAs, this) an ask sat
> because a prior run made filing conditional on a human first confirming something. If the
> confirmation has not arrived by the next run, file the *investigation* and put the unconfirmed
> thing in **Not yet confirmed**. Filing a question is cheap; a triage decision is the cost.
>
> **Lesson: a repeat "still untracked" flag is a filing failure, not a report.** That bug
> sat in Slack for 15 days while the daily intake runs on Aug 14, Aug 19 and Aug 20 each
> flagged it as untracked and asked a human to file it. A daily run's scan window never
> reaches back to an ask that old, so the ask can only ever be re-flagged, never filed, and
> nothing changes. When a prior run's summary names an ask as still untracked, treat it as
> an in-window candidate for this run: match it against the boards, and if it is still
> untracked, file it and say in the ticket body that it is an out-of-window carry-over.
>
> **2026-09-04 - the ledger-PR backlog is closed out.** The Aug 31, Sep 1, Sep 2 and Sep 3
> summaries each escalated open ledger PRs (`#260`, `#264`, `#273`) leaving `main` behind the
> dedupe key. When this run started **no prior ledger PR was open**, `main` carried every row
> through Sep 1, and `## Claimed by an unmerged PR` was empty on arrival. The escalation is
> resolved, not pending - do not carry it forward again. This run's own PR (`#295`) is of
> course open; its row is in the claimed table below, which is exactly where an unmerged
> run's row belongs.
>
> **2026-09-14 - seven rows, one permalink, and that is correct.** Nir DM'd Hanan a single
> message carrying 17 open items and asked for it to be worked off one list. Seven of the 17
> had no ticket on any board and were filed as seven tickets, so seven rows share one
> permalink. The dedupe key still behaves: the test is whether the permalink appears in this
> file, and after this run it does, so no later run re-files any part of that message. What
> the key cannot express is *partial* coverage - if Nir sends a follow-up naming an
> eighteenth item in the same thread, the permalink test will suppress it. Match on the item,
> not just the message, when an ask arrives as a numbered list.
>
> **This was not a channel-scan intake.** The source is a DM, which is not in the scanned
> channel table and never would have surfaced on the daily run. Recorded here anyway so a
> manual re-run of the same list does not double-file.
>
> **Column note, verified 2026-09-14.** `board_relation_mkrj2nbw` ("LInked Tickets") **cannot
> link two MOPs items.** Its `boardIds` are `[8739806205, 3830066160, 9782867747, 18399446834,
> 18399485085]` and `6257866754` is not among them, so writing a MOPs item id to it fails with
> `InvalidColumnIdException` / `missing_column`. The config's Pass A disposition ("link them")
> is not executable on this board for a same-board pair - reciprocal updates are, and are what
> was used. Same situation Website Dev is already documented as having.
>
> **A stated trigger guards a concern, not a literal condition - so it can be retired as well
> as fired.** The Sep 3 run put the DE Business + Book-a-demo locale content on watch with the
> trigger "still unpublished at the next run, or Nir asks a third time." Read literally the
> trigger fired: it is still unpublished, and Jonathan did ping a second time on Sep 3 13:52.
> But the concern the flag was guarding was *silence* - an unticketed fix with nobody
> answering. Milutin answered at 13:54 and Jonathan replied "It can wait for when there are
> more items to publish today." The requester de-prioritised his own ask, so filing a ticket
> would have been over-filing against his stated wish. Watch **retired**, not fired. The
> complement to "state the trigger" is "say what the trigger is protecting", or a later run
> mechanically fires a flag whose reason has evaporated.
>
> **New watch, trigger stated - the HeyGen pricing correction on two blog posts.** Support
> relayed a third party's factual correction on Sep 3 (`p1788426855572959`): `/blog/invideo-ai-alternative`
> and `/blog/best-ai-video-generators` cite outdated HeyGen pricing. Not filed, and the reason
> is the direction test plus an in-thread answer: Erika Varangouli owns the blog, took it
> explicitly ("it's on us"), and named a plan - the blog content-removal pass finishes this
> month, then the remaining pages get scheduled updates. Neither MOPs nor Website Dev executes
> a blog copy edit. **Trigger to file: October arrives with those two pages still citing the old
> figures, or a second external report lands on the same pages.** Recorded because the
> commitment is real and no ticket on any board records it.
>
> **2026-09-07 - an intake routing call was overturned, and the ledger should say so.** The
> Aug 31 run filed `add meeting_source_cp params to site book-demo CTAs` onto Website Dev, and
> the row above still reads `Website Dev 18397093471` because that is where it was filed. It is
> **now MOPs `12932161611`** - board activity shows a `move_pulse_into_board` seven minutes
> after filing, plus a Sep 1 update "Needs clarifications from Rev ops team (Matan R.)" and a
> Sep 6 move into the `0609 - 1009` week group. The row is left as-filed rather than rewritten,
> because a row records what a run did; the correction lives here and in SKILL.md Step 4. The
> run reasoned from two closed Website Dev precedent tickets instead of from the mechanism test
> its own ticket body had already flagged as the risk.
>
> **2026-09-07 - the Chrome v152 desync blast needs a person, not a ticket.** MOPs
> `12958379709` (`Email Blast - Chrome v152 desync re-processing notification`, P1, due Sep 2)
> was **set to Cancelled on Sep 6 07:24 UTC by its own owner, with zero updates and no closing
> comment.** Support asked on Sep 2 for ~152 affected users to be mailed via Customer.io "in the
> next few hours"; the ticket's stated Done When ended with reporting delivery numbers back
> in-thread, and the thread's last message is still the ticket-creation post. There is no
> evidence either way that the send happened.
>
> **Not re-filed, and the distinction from `12791564247` is the whole point.** That ticket's
> *job was to watch for a future event*, so cancelling it removed the watch. This one's job was
> a single send, and the person who owns the work cancelled it deliberately on Sep 6, four days
> after Support's Sep 2 request. Filing
> an investigation would put a ticket on his own board asking him why he cancelled his own
> ticket - over-filing against a stated decision, the error the retired Sep 3 locale watch
> avoided. A one-line answer ("sent" / "dropped") resolves it, so it is escalated in the run
> summary as *needs a human* rather than carried as a watch that can only ever be re-flagged.
>
> **The source permalink is deliberately not written anywhere in this file.** Step 2's dedupe
> test is a file-level permalink match, so recording it here would silently suppress a re-file
> if the blast turns out never to have gone out - exactly the hazard the audit-note paragraph
> above documents. Identified by ticket id and thread instead.
>
> **2026-09-09 - the `/blog/is-riverside-free` escalation is retired, and the check that retired
> it is `get_updates` on the ticket.** MOPs
> [12930035566](https://riversidefm.monday.com/boards/6257866754/pulses/12930035566) was carried
> as *needs a human* in the Sep 3, 4, 5, 6 and 8 summaries, each on the same two observations:
> the title still says "Remove and redirect" when Ortal Hadad settled on Sep 2 that the page gets
> *updated*, and the item looks neglected. The second observation is now false. The item carries a
> **Sep 7 05:45 update from its own former owner - "Pending decision on next steps and
> prioritisation by SEO team"** - written the same day he came off it. That is a deliberate park
> with the blocker named, not neglect, and `12984501131` (`Decide on remaining open SEO team
> website tasks`) is open on the board for that decision. The stale title is a cosmetic artifact
> of a ticket whose scope is deliberately under review, and re-raising it costs a human's
> attention for nothing.
>
> **This is the mirror image of the Step 6 rule and it needs saying, because Step 6 only names
> the Slack half.** There, the board read untouched while the work sat in a Slack thread
> (`12943009640`). Here the board did **not** read untouched and five summaries said it did,
> because every one of them reasoned from column state - title, owner, status - and none opened
> the item's updates. Both failures are the same failure: *asserting a ticket's state from
> anything other than its updates or its thread.* Read one of the two before carrying an
> escalation into a second run, and read them again before a third.
>
> **The complementary lesson, about escalation rather than filing.** The Chrome v152 desync blast
> (`12958379709`) is the honest counter-case: verified again on 2026-09-09, still Cancelled with
> **zero updates**. Its Sep 2 source thread carries **14 replies, and the last of the 14 - Sep 2
> 18:18 IDT - is the Marketing OS agent's own ticket-creation post.** Nobody has posted in that
> thread since, so there is genuinely no evidence either way that the send went out. State it
> that way round: "the last message is the ticket-creation post" and a reply count in the same
> breath reads as though the discussion continued *after* the ticket was opened, which would
> imply somebody is on it. Not re-filed,
> for the reason already recorded above. But it has now been escalated in three consecutive run
> summaries with no movement, and the ledger's own rule about repeat flags applies to escalations
> as well as to asks: **a "needs a human" line that three runs have produced nothing from is a
> failure of the channel, not a report.** A summary in `#mops-team-internal` is not reaching the
> one person who can answer it in a word. Escalate it to the run owner directly instead of
> spending a fourth summary line on it.
>
> **2026-09-11 - `#support-marketing` carries two bots pointing in opposite directions, and only one of
> them is somebody else's queue.** `Request for Support` (`B0B0F6ZESAG`) posts Marketing → Support and is
> what the config's direction rule is about: those are aimed at the Support team and filing them puts
> another team's work on our board. `Request for Marketing` (`B0B09FTHXU6`) posts Support → Marketing,
> and those **are** ours. Three filed rows above came through it (`12888737157`, `12943009640`, and
> today's `13023721254`), so the practice was already right; the config just never named the two bots,
> which left the channel's whole entry reading as "not ours" to anyone applying it literally. Named in
> `knowledge/config.md` now. The bot rule and the direction rule are separate tests and both still run:
> the tell for a relayed human request is `Requested by: @person` either way.
>
> **Today's filing is deliberately at the small end, and the reasoning is worth keeping.** The requester
> opened with "Not a request - Just checking to see if this user is unsubscribed." Taken literally that is
> a discard. It was filed anyway because the direction test passes (Support is asking Marketing), the
> answer needs HubSpot access nobody outside MOPs has, it sat overnight with zero replies, and a Zendesk
> ticket is open behind it. A requester downplaying their own ask is not the same as a requester
> **de-prioritising** it - that was the Sep 3 locale case, where Jonathan said out loud it could wait, and
> filing would have overridden him. Nobody has said that here. The ticket body says plainly that this may
> close with a one-line Slack answer, which is the cheap failure; the expensive one is a compliance-shaped
> question about a named contact evaporating into backscroll.
>
> **2026-09-13 - the industry-pages chase has hit the repeat-flag threshold and changes channel, not
> wording.** Ann Tsunakawa asked in `#webflow-riverside` on Sep 8 09:24 when the industry pages go live
> (`p1788848682148719`). Re-verified today by opening the thread, not by reading the channel list:
> **still zero replies, day 6.** The three tickets covering the work - Website Dev `12669844748`,
> `12482834849`, `12670245890` - are all `status New`, **due 2026-09-10**, and sit in the
> `14.09.26 - 25.09.26` group, so the due date is three days past while the work has not started.
>
> **Correctly never filed, and that is not the problem.** It is a chase under Step 2: the work is
> ticketed, so a new ticket would be a duplicate, and what Ann needs is a date. But the Sep 9, 10, 11
> and 12 summaries each carried it as *wants a reply* and produced nothing, which is precisely the
> condition the Chrome-v152 paragraph above names - **a "needs a human" line that three runs have
> produced nothing from is a failure of the channel, not a report.** A `#mops-team-internal` summary is
> not reaching the person who can answer Ann in one line. Escalated to the run owner directly instead.
> The next run should not spend a sixth summary line on it; if it is still silent, the honest read is
> that the *tickets* are the problem (a due-date reset), not the chase.
>
> **2026-09-15 - this file had two sections called `## Claimed by an unmerged PR`, and the second one
> was an accident.** The Sep 14 run (`#329`) appended its note *inside* the Sep 4 paragraph's inline
> code span, landing its text between the opening backtick and the closing one of
> `` `## Claimed by an unmerged PR` ``. That split one sentence across 25 lines and promoted its tail
> to a **level-2 heading**, because the orphaned text started at column 0 and began with `##`.
> Repaired this run: the Sep 4 sentence is whole again, the Sep 14 note follows it as its own
> paragraph, and the duplicate heading and its stray `---` are gone.
>
> **Why this is worth a paragraph and not just a fix.** The spurious heading sat directly above the
> real claim table, so for a day this file asserted two claim sections, the first of them empty. A run
> that reconciles "the claimed table" by finding the first heading of that name reads the empty one,
> concludes there is nothing to reconcile, and leaves live claim rows stranded in the real table below
> - the permanent-suppression failure this section's own preamble warns about, reached by a Markdown
> accident rather than by a judgement error. Nothing was actually mis-filed, because this run read the
> whole file. **An append into a notes block is a structural edit, not a text edit.** After writing
> this file, `grep -n '^## ' data/ledger.md` should return exactly four headings: `Filed asks`,
> `Claimed by an unmerged PR`, `Adjudicated pairs`, `Dismissed routing proposals`.
>
> **2026-09-16 - this run's own row is in `## Claimed by an unmerged PR` and deliberately NOT here,
> which is a change from the last three runs.** A review on `#341` caught the permalink sitting in
> both tables, and it was right: the claimed table's preamble says a permalink must never sit in both
> at once, and Step 6's own closing sentence - whoever merges *moves* the rows into `## Filed asks` -
> only parses if the row is not here yet. **Whoever merges `#341` moves the row down here and deletes
> the claimed one.**
>
> **A first draft of this note claimed "dedupe is unaffected". That was wrong, and a second review on
> `#341` caught it.** A run reads this file from `main`, and a row written on a PR branch - in
> *either* table - does not reach `main` until the PR merges. So moving the row between tables on the
> branch changes nothing about pre-merge exposure: it was uncovered before the move and is uncovered
> after it. What the claimed table actually is, is a **post-merge handoff marker**, not a pre-merge
> shield. The window between opening a ledger PR and merging it is covered by nothing but Step 3's
> live-board match, which misses an ask whose ticket has since closed - the `12791564247` shape,
> again.
>
> **Stated rather than fixed, deliberately.** Closing it means Step 1 reading claim rows out of open
> ticket-hygiene PRs, or publishing claims somewhere every run sees without a merge. Both are
> workflow changes with an external dependency, and a daily intake run's ledger PR is the wrong place
> for either. Step 6 now describes the gap accurately instead of asserting cover it does not have,
> and the choice is flagged for a human on `#341`. The rule this leaves behind: **when a mechanism
> only works after a merge, say so in the same breath as the mechanism** - the previous wording had
> three runs believing the claimed table protected a window it never touched.
>
> **Step 6's wording is what produced the violation, three runs running, so it is fixed rather than
> worked around.** It said to append the row to `## Filed asks`, then to add "the same permalinks" to
> the claimed table in the same commit - which reads as *both*, and that is what `#323`, `#329` and
> this run all did. The two cleanup notes under the claimed table are the same defect twice, each
> recorded as a surprise rather than as the predictable output of the instruction. SKILL.md now says
> the row goes to exactly one table, and which one.
>
> **2026-09-16 - the ask that six runs of channel-level reading could not see, because it was reply 36
> of 43.** Filed today: Website Dev
> [13056979737](https://riversidefm.monday.com/boards/18397093471/pulses/13056979737), from Erika
> Varangouli's "is anyone collecting them into a new task for post live?" in the Transcription QA
> thread. Nobody answered, and the page shipped to production 107 minutes later with the deferred
> fixes uncollected. Two separate decisions in that same thread - Nir's "go live now, fix it on round
> 2 with all the other fixes to the other tools" and Milutin's agreement with Jonathan that tool
> *functionality* becomes a separate task - both point at a follow-up ticket, and no such ticket
> existed on either board. Verified against all 343 open Website Dev items including subitems.
>
> **The generalisation is about where asks hide, and it cuts against how five prior runs read this
> channel.** Every previous summary classified `#webflow-riverside` wholesale as "QA and delivery
> chatter on open Website Dev tickets, already tracked" - which was true of the *parent* messages and
> is how the channel almost always behaves. But a delivery thread is exactly where a go-live decision
> gets made, and a go-live decision is exactly what strands the work it defers. Step 3 already says to
> open a thread before calling an ask unresolved; this is the other direction - **open the long
> delivery threads before calling them tracked.** A 43-reply thread on a tracked ticket is not
> evidence that everything in it is tracked; it is the most likely place in the channel for a new,
> untracked ask to be sitting. Cheap heuristic: a thread whose reply count grew materially since the
> last run, on a ticket that just shipped, is worth the one call.
>
> **Milutin's backend finding in the same thread is deliberately not filed, and the reason is the
> mechanism test.** A file with no audio track causes the transcription WebSocket to return neither
> FINISH nor FAIL, leaving the user stuck in "transcribing" forever; Jonathan called it legacy
> behaviour for another phase. No Webflow developer and no Marketing Ops change can ship that fix - it
> is a pipeline change - so neither board is its home and filing it on one would be a ticket nobody on
> that board can execute. Recorded in `13056979737`'s body as explicitly out of scope with the owner
> question named, and escalated in the run summary. **A real bug with no correct board is an
> escalation, not a ticket.** Its permalink is written nowhere in this file, so a later run is free to
> file it if Product/R&D turns out to be the wrong read.
>
> **2026-09-16 - a watch ticket's trigger fired, and the ticket is now retroactive.** MOPs
> [12975027464](https://riversidefm.monday.com/boards/6257866754/pulses/12975027464) was filed Sep 4
> to check what Marketing Ops needed to adjust *before* the US Agency distribution change landed.
> Daniel Nitsan announced on Sep 15 13:16 that the new distributions are **live**. Not re-filed - the
> ticket is open, in `New Requests`, and this is precisely the event it exists to catch, so Step 3
> matches it. But two things changed under it and triage should know: the split shipped **three** ways
> (0-1, 2-10, 11-50) where the ticket body records two (0-1, 2-50), and **EU and ANZ distributions
> were also updated** where the Sep 3 announcement promised they would stay unchanged. The ticket's
> own *Not yet confirmed* list asks whether anything filters on the literal "1-50" distribution name;
> there are now three new names plus EU/ANZ edits behind that question, and the check is happening
> after the fact rather than before it. Flagged to a human rather than rewritten - a run does not
> edit a ticket's body to match reality it discovered later.
>
> **New watch, trigger stated - the free transcription tool's data-retention answer.** Support relayed
> a user's deletion request on Sep 15 10:22 (`Request for Marketing`, Jannel Quiñonez Bruzon, Zendesk
> 787291) asking whether uploads to `riverside.com/transcription` are still deleted after 24 hours, as
> the product team said back in 2025. **Not filed**, and the reason is the Sep 3 locale shape rather
> than the Sep 10 unsubscribe shape: Jonathan picked it up within two hours and routed it to Roie
> Cohen, who owns the answer. Nobody is waiting on MOPs, and there is no MOPs or Webflow change behind
> it - only an answer from R&D. **Trigger to file: Roie has still not answered by the Sep 18 run, or
> Support chases it again.** At that point it becomes a MOPs ticket to get the retention behaviour
> confirmed and written down, because a compliance-shaped question about a named external user on an
> open Zendesk ticket should not evaporate into backscroll. The permalink is deliberately not written
> as a table row, so the trigger can actually fire.
>
> **2026-09-17 - that watch is retired one run early, trigger unfired.** Roie Cohen answered in the
> thread on Sep 16 09:15 ("they should be, but haven't checked it out for a very long time"), and when
> Jonathan pushed for a real check he went and did it: 09:24, "it's still correct I just checked we
> delete after 24 hours." Jannel had the answer at 09:31 and a follow-up answer about the other tools
> at 13:22. The trigger was "Roie has still not answered by the Sep 18 run, or Support chases it
> again" - he answered, nobody chased, so the watch **closes** rather than fires. Recorded because the
> Sep 3 locale note established that a watch can be retired as well as fired, and this is the clean
> case of it: the concern was a compliance question going unanswered, and it got answered.
>
> **A second-order note worth keeping: that answer now exists only in Slack.** Roie's "I just checked"
> is the sole record that `/transcription` uploads are still deleted after 24 hours, and the next
> person Support asks will re-ask him. That is a documentation gap, not an intake candidate - no MOPs
> or Webflow change sits behind it - so it is not filed. Named here so a later run recognises the
> shape instead of re-deriving it.
>
> **2026-09-17 - Nir's transcription CTA report is tracked, not filed, and the call is close enough to
> show its working.** He posted in `#webflow-riverside` on Sep 16 18:39: "note the the transcription
> page CTA is not working/clickable." Zero replies. Not filed, because three open Website Dev items
> plausibly match and one exists for exactly this: `13056979737` (`collect post-live fixes for
> refactored tools pages`), filed by yesterday's run, whose body already lists a main-CTA item and
> whose *Not yet confirmed* says in terms that "someone should re-QA the live page before this is
> scoped." Nir's message **is** that re-QA finding. A second ticket one day later duplicates the
> collection point this skill had just created.
>
> **The risk in that call is named rather than waved off.** `13056979737` is a scoping placeholder
> with no owner, no due date and no priority, and "the CTA is not clickable" on a live page is a
> conversion outage, not a deferred nicety. Absorbing a production defect into an unscoped backlog is
> how an ask evaporates - the failure this file documents repeatedly. So it is tracked on the board
> *and* escalated to a human in the run summary, which is the pairing Step 3 intends when it says to
> record a match "so a human can spot a bad match." **If `13056979737` is still unowned at the next
> run with the CTA unfixed, the honest read is that the collection ticket is not doing its job and
> the defect wants its own P1.**
>
> **2026-09-17 - the Business Plan form gate has flipped three times in five weeks and its audit has
> never started.** Daniel Nitsan announced on Sep 16 10:03 that he "blocked the option to submit Gmail
> addresses in our forms until the next cohort of reps joins us", and confirmed in-thread to Yaniv
> Barel that the gate had been open since **August 30th**, linking that exact announcement. Not filed:
> MOPs [12929041147](https://riversidefm.monday.com/boards/6257866754/pulses/12929041147) ("audit
> public-domain reopen on Business Plan forms") is open in `New Requests` and is the ticket for this
> gate. A third ticket for a third flip of the same toggle is over-filing.
>
> **What triage should take from it is the opposite of reassurance.** The sequence is Aug 12 block →
> Aug 30 open → Sep 16 block. The Aug 13 ticket for the first flip (`12791564247`) was **cancelled
> with no closing comment**; the Aug 30 ticket for the second is open and **untouched since it was
> auto-filed** - its only update is the filing body, verified with `get_updates` rather than read off
> the status column. The audit window is now bounded (Aug 30 → Sep 16) and finite, which makes the
> check *cheaper* than when it was filed, and nobody has started it. The finding is the oscillation,
> not any one flip: a gate that toggles faster than its own audit ticket gets triaged.
>
> **2026-09-17 - Erika Varangouli's legal question on the Magic Clips pages has no board and no
> answer.** QA-ing the four staged clip-maker pages on Sep 16 20:50 she wrote: "Checking with Jonathan
> that legal is aware we're giving people the capability to insert any yt link and generate clips with
> our legal statement being the yellow disclaimer at the bottom. Are we legally covered?" No reply.
> Not filed, on the mechanism test - no Webflow developer and no Marketing Ops change ships a legal
> sign-off - so it is the same shape as the Sep 16 transcription-WebSocket bug: a real question whose
> correct owner is outside both boards. **Its permalink is deliberately written nowhere in this file**,
> so a later run can file it if that read turns out to be wrong. Her other two findings in that thread
> (the "Drop a YouTube link" copy being wrong for these pages, and `tiktok-clip-maker` broken on
> landing) are QA delivery on the open ticket `13057347884` and are tracked.

> **2026-09-18 - the Magic Clips pages went to production with both of those findings still open, and
> the ticket that held them is now `Done`.** Sequence, all on Sep 17 in `#webflow-riverside`: Amir
> Bar-Tikva reported at 10:24 that the flow dead-ends - "you get to a screen with your clips where you
> have no options to continue other then go to sign up - no back no way to continue on site" - and
> pushed again at 10:40 after Milutin routed the app flow to Raman Matusevich: "we need to make sure
> the tool work flow works and alows the user to get all the way through like other tools, not sure if
> its a staging env. issue or not." Erika Varangouli re-asked her legal question at 11:06 and narrowed
> it at 11:14 to "only checking if legal is happy and we're covered." Neither was answered. At 13:11
> Jonathan Galili said "Let's go to prod please", Milutin published at 13:41, and Amir's 13:58 "so the
> clip tool went to production?" got no reply either. `13057347884` was set to `Done` at 15:08.
>
> **Neither is filed, and the reason is the mechanism test, not a judgement that they do not matter.**
> The dead-end is inside the embedded product app - Jonathan's own QA post says "we have absolutely no
> control over it, besides adding to our pages with an iframe", and Milutin named Raman Matusevich as
> the owner. No Webflow developer and no Marketing Ops change ships it, and neither does a legal
> sign-off. Same shape as the Sep 16 transcription-WebSocket bug and the Sep 17 read of the legal
> question, and filing either onto Website Dev would be the mis-route the config's "does a Webflow
> developer have to touch this?" test exists to prevent.
>
> **What is new is that the go-live removed the last thing holding them.** On Sep 17 both sat inside an
> open ticket, which is why that run could leave them as escalations. That ticket is closed, so the
> only open collection point is `13056979737` ("collect post-live fixes for refactored tools pages"),
> which is `New` in `New Tasks` with **no owner, no priority and no due date** - read live off the
> board this run, not carried from a prior summary. It is now the nominal home of three separate
> unowned post-live findings: Nir Taranto's unclickable transcription CTA (Sep 16 18:39, still zero
> replies on day 2), Erika's `/tools/video-resizer` misalignment (Sep 17 17:49), and this dead-end. A
> collection ticket nobody owns is a list, not a plan. Escalated rather than re-filed; the permalinks
> for the dead-end and the legal question are deliberately written nowhere as table rows, so a later
> run can still file either if this read turns out to be wrong.
>
> **2026-09-18 - the Sep 17 unsubscribe ticket can close.** `13066548936` was answered in-thread by
> Jonathan on Sep 17 09:41 ("The user is already unsubscribed, following their own action to do so.
> There is no issue with unsubscribe functionality") and Anne Vera Candelaria thanked him at 18:05.
> Recorded because Step 6 makes a run re-verify a carried item against its source thread before
> escalating it again, and this is the cheap outcome of that check: the ask is answered, not stalled.
> Worth one line for triage, though - this was the **second** independent user in three weeks, and the
> answer given is the same one that closed `12943009640` on Sep 7. Two users reporting that a button
> did not take, answered twice with "the record says they are unsubscribed", is the pattern that
> ticket's own body named, and nobody has yet tested the control itself.
>
> **2026-09-20 - Nir's transcription CTA is filed at last, and this run is reversing two of its own
> prior adjudications on purpose.** The Sep 17 and Sep 18 runs both read his Sep 16 18:39 report - *"note
> the the transcription page CTA is not working/clickable"* - as tracked by `13056979737`, whose body
> does list a main-CTA item and does ask for the live page to be re-QA'd. The Sep 17 note wrote the
> trigger for undoing that call in terms: *if `13056979737` is still unowned at the next run with the CTA
> unfixed, the collection ticket is not doing its job and the defect wants its own P1.* Checked live this
> run rather than carried: `13056979737` still has **no owner, no priority and no due date**, its only
> update is its own filing body from Sep 16, and the thread still has **zero replies on day 4**. Filed as
> Website Dev [13087888177](https://riversidefm.monday.com/boards/18397093471/pulses/13087888177).
>
> **What tipped it was not the age, it was `12966651648` going `Done` on Sep 17.** While the Transcription
> refactor ticket was open there was an owned, P1, dated ticket on the same page that a CTA defect could
> plausibly land on. It is closed now, so the only nominal home is an unowned stub in the intake queue,
> and "tracked by a ticket that cannot move" is the failure this file has recorded three times under
> other names. Priority is left empty because automation does not set it on this board; the P1 case is
> made in the ticket body and in the summary, where a human can overrule it.
>
> **The risk in filing is named too: this may be a duplicate of an item already listed on `13056979737`.**
> That ticket's known-items list carries "main CTA cut off on mobile", and Nir did not say which CTA or
> which breakpoint. If triage finds they are the same defect, the right move is to close `13087888177`
> and give that line an owner - the point was never a second ticket, it was an owner.
>
> **2026-09-20 - Erika's second `/video-resizer` finding is tracked, and the tracking ticket is one step
> from repeating the Magic Clips sequence.** She posted Sep 18 19:14 in `#webflow-riverside`: the first
> screen is still misaligned on desktop (a re-post of her Sep 17 17:49 report), and *"when in the tool,
> the pop up gets cut on desktop (Macbook Air, 13'') - users can't click the CTA."* The popup half is new;
> the misalignment is not. Not filed: `12955357564` is open, owned by Davor, P1, and covers this tool.
> Correct on the mechanism test and on the over-filing rule both.
>
> **But that ticket's status read live this run is `Ready for live`, and her message has zero replies.**
> That is the Magic Clips shape exactly - a ticket at the edge of go-live with an unanswered desktop
> blocker on it, which on Sep 17 went to prod anyway and closed at 15:08 with the findings still open.
> Recorded here so the next run can tell whether the pattern held: **if `12955357564` reaches `Done`
> without Erika's cut-off popup being answered in the thread or on the ticket, the finding needs its own
> ticket the way the transcription CTA just did.**
>
> **2026-09-21 - that trigger has not fired, and the "zero replies" half of it was wrong in a way worth
> recording.** `12955357564` reads `Ready for live` live this run, not `Done`, so the condition above is
> not met and nothing is filed. But the premise needs correcting: Erika's cut-off popup **was** answered,
> just not anywhere a channel read can see. Jonathan DM'd Ruben Aknin on Sep 20 09:14 with a link to her
> Sep 18 19:14 message ("more rejects from the SEO team on Resizer"), Ruben acknowledged at 10:28, and
> Ruben had already replied "will be fixed shortly" at 09:13 in the Sep 16 Amir thread where her Sep 17
> misalignment report sits. Both halves of her finding are with the person who builds the tool.
>
> **The generalisation is the one this file keeps relearning from the other side.** Step 3 says open a
> thread before calling an ask *unresolved*; the Sep 16 run added "open the long delivery threads before
> calling them *tracked*". This is the third face of it: **a top-level message showing zero replies is not
> evidence that nobody acted** - on this team the routing frequently happens by DM, and `slack_search_*`
> and `slack_read_channel` both show only what landed in the channel. "Zero replies" is a statement about
> the channel, not about the work, and a summary should say it that way. The Sep 20 escalation was still
> the right call on the ticket state; only its supporting sentence was overstated.

> **2026-09-21 - the highest-value thing this run found is untracked, and it is deliberately not filed.**
> Jarred Berman DM'd Jonathan Galili on Sep 20 11:25 and 11:26: *"What was our action item about adding a
> submission form straight to this LP? Sorry I forgot"*, then *"This Meta campaign is getting lots of
> clicks but not a lot of submissions wo we spoke about adding the form directly in the hero."* Still
> unanswered a day later. Checked against all 280 open MOPs items and all 93 open Website Dev items,
> subitems included - nothing covers it. The nearest item, Website Dev `18388587546` ("Pricing section
> embedded on the PPC home LPs"), is `HOLD` and is different work.
>
> **Three reasons it is reported rather than filed, and the first is the one that binds.** (1) It is a
> **DM**, and the config's channel table is INTAKE's scan surface - DMs are not on it. A daily unattended
> run widening its own source list is a scope change for a human, not a judgement call for the run that
> noticed. (2) The message is a question to Jonathan, not a work request with a stated scope: both parties
> are reconstructing a verbal agreement, and neither the LP nor the mechanism (a Webflow hero edit versus
> a HubSpot form embed, which route to different boards) is stated anywhere. A stub would carry a title
> and no scope. (3) Under-file rather than over-file. One line from Jonathan turns this into a real ask
> with a real board; a ticket filed first would be triaged into the same question.
>
> **The config gap is real and is named here rather than closed.** `data/ledger.md` already carries seven
> filed rows sourced from a DM (`D0A4W65A80J`, Nir to Hanan, Sep 14), so DMs have produced filings before
> - but through a directed invocation, not through a scheduled scan, and the channel table was never
> updated to match. So the skill's own record is inconsistent with its own scan surface. Deciding whether
> scheduled INTAKE should read named DMs is a change-control call with a privacy dimension; raised in the
> PR, not made here.

---

## Claimed by an unmerged PR

Rows here are **dedupe inputs exactly like `## Filed asks`**, for exactly the same reason:
Step 2's test is "permalink is not already in `data/ledger.md`". An ask listed here has already
been filed by a run whose PR has not merged yet, so it must not be re-filed - including after
its board item is closed, which is the case Step 3's live-board match cannot cover on its own
(it matches only *open* items).

**These are table rows, and that is load-bearing.** The audit-note paragraph under `## Filed
asks` is deliberately *not* a dedupe key and says so; these rows deliberately are. The rule
stays "match on the table rows" - this is simply a second table of them.

Delete a row only when its PR has merged and the ask has landed in `## Filed asks`. A permalink
must never sit in both tables at once.

| Permalink | Channel | Author | Filed | Board | Item | Claimed by |
|-----------|---------|--------|-------|-------|------|------------|
| [p1790885843750799](https://riversidefm.slack.com/archives/C05TRR8BWBX/p1790885843750799) | `#support-marketing` | Joshua Nathaniel Rodillas Santos (Support, via `Request for Marketing` bot) | 2026-10-02 | MOPs `6257866754` | [13189815036](https://riversidefm.monday.com/boards/6257866754/pulses/13189815036) - resubscribe user for Zendesk ticket 806245 | `#439` |

> **2026-10-04 - filed 0. The one new ask was a blog copy fix, already handed to named owners.**
> `#424` and `#430` are merged and `#439` (the Oct 2 run) was still open on arrival, so this branch is cut from its
> head: merging this one carries both runs, and `#439` can close as superseded. No claim row added today.
>
> **Checked, not filed: Adobe asks for a blog post update (Zendesk 806135).** `Request for Marketing` relay, Oct 2
> 21:45, Rey Bjorn Castro (Support): an Adobe representative says Premiere Rush, named in
> `/blog/best-video-editing-software-for-youtube`, has been replaced by Premiere Mobile Apps, and asks for the post to
> be updated. Thread re-read: Sivan Mazuz replied Oct 4 09:03 tagging Erika Varangouli and Ortal Hadad, which is a
> handoff. A blog-post copy edit is content work done in the CMS by its owners, and neither a Webflow developer nor
> Marketing Ops implements it, so it is neither board's. No open item on either board (subitems included) names the
> post. No row, so a later run sees it again: if the thread shows nothing from Erika or Ortal by about Oct 9, raise it
> as `handed to Erika and Ortal, not yet confirmed`, never as untracked.
>
> **Checked and not filed.** `#website-dev`: Dusan's Oct 2 review links are delivery on `13143578931` and
> `13143516668`, and Milutin's Oct 2 reply on the tools re-ticketing is delivery on `13159469942` and `13183533230`.
> `#mops-priority-room`: Web Dev due-date reminder bot posts and HubSpot Last Touch Source alerts, all notifications.
> `#webflow-riverside`: QA handoffs on tracked tickets, nothing new since Oct 1. `#marketing-revops`: only Abel's Sep 28
> question to Data. `#contact-martech` silent since Aug 17. `#marketing-internal`: social posts.
>
> **Agent-directed text: none new.** Jonathan's Sep 29 `@agent marketing-os please open a ticket for the above`
> (Ruben's thread) is still in window, already reported, not executed.

> **2026-10-02 - filed 1, reconciled two merged claims, and retired the Creator partnership escalation.**
> `#424` and `#430` both merged on Oct 1, so their claimed rows (`p1790746552886069`, `p1790775877337319`) moved
> into `## Filed asks`. Today's ask takes the one claimed row.
>
> **Filed: `13189815036`**, MOPs `New Requests`. `Request for Marketing` relay, Oct 1 23:17, Joshua Nathaniel
> Rodillas Santos (Support): resubscribe `don.hicks@vensure.com` (Zendesk 806245) to marketing and notification
> emails, a sales prospect with an active deal. Only reply is Joshua CC'ing Jonathan. No open item or ledger row
> names the address or ticket. Type `HubSpot`, `Planned?` Unplanned, POC empty (Joshua does not resolve to a monday
> user), Zendesk link attached. Read-back clean. The body asks Support to name which email types are meant and to
> confirm the user expects to opt back in, since he unsubscribed himself.
>
> **Retired: the Creator partnership follow-up (Zendesk 803368).** Thread re-read: Nir tagged Savion, and Dalit
> answered on Oct 1 (no request found under that address, user to write to partnerships@). Karen acknowledged. Owned
> and closed in Slack, so it is not raised again.
>
> **Both unsubscribe relays are answered and Done.** Jonathan replied in both threads on Oct 1 (`13146866474`:
> already unsubscribed on her own; `13178489860`: now unsubscribed), and both items read `Done`.

> **2026-10-01 - filed 1, claimed one permalink, escalated one, and yesterday's filing was deleted as a non-issue.**
> `#424` (the Sep 30 run) was still open on arrival, so its claimed row stays and this branch is cut from its head:
> merging this one (`#430`) carries both, and `#424` can close as superseded.
>
> **Filed: `13178489860`**, MOPs `New Requests`. `Request for Marketing` relay, Sep 30 16:44, Rey Bjorn Castro
> (Support): unsubscribe `gilai85@gmail.com` (Zendesk 803201, "escalated user") from all emails. No reply in thread.
> No open item names the address or ticket. Type `HubSpot`, `Planned?` Unplanned after a planning-board search,
> POC resolved to monday user `76993344` (the first Support requester that has resolved), Zendesk link attached as
> an asset. Read-back clean: columns set, asset present, body renders as HTML. Fifth Support unsubscribe relay since
> Sep 1, and `13146866474` (Sep 27) is still `New` and unowned, so the body suggests handling the two together.
>
> **Escalated, no board and no row: a Creator partnership application follow-up.** `Request for Marketing` relay,
> Sep 30 17:58, Rey Bjorn Castro: a user is following up on their application for Creator partnerships
> (Zendesk 803368, `info@grasspink.com`). No reply in thread. Under the Riya rule this is a partnership decision,
> not buildable work, so it goes to Creator Marketing (most likely Savion Ron Shemesh, who took both Riya threads).
> No ledger row on purpose, so it comes back until the thread shows an owner.
>
> **Yesterday's filing `13167532373` was deleted, and the deletion is correct.** Sivan Mazuz answered in Yael's
> thread on Sep 30: "this isn't a mistake". On the pricing page, "lead capture" under Webinar means the registration
> form and collecting details on join, and the Business-only HC article covers embedded videos. Yael asked for a
> rename to remove the ambiguity, and Sivan declined (the tooltip already clarifies it). Jonathan deleted the item at
> 15:32 IDT (`delete_pulse` in board activity). The claimed row stays, marked deleted, because the ask is resolved and
> must not be re-filed. Lesson already in the ticket body: the product claim was unverified at filing, and the
> pricing page owner answered within four hours.
>
> **Magic Clips legal question: trigger fired, now handed to Nir, and retired from intake.** Re-read the thread
> (`#webflow-riverside`, Sep 16): still no reply after Amir's Sep 17 "so the clip tool went to production?", and no
> Legal owner named anywhere in Slack search. Per the Sep 24 trigger, this stops being an intake item: the feature has
> been live two weeks on an unanswered legal question, which is a conversation with Nir, not a queue item. Not raised
> again after today.
>
> **Milutin's Sep 23 unpublish question: final raise, then dropped.** Thread re-read, still zero replies. He said no
> work is blocked, so from tomorrow it is his to chase. Not carried further.
>
> **Checked and not filed.** `#webflow-riverside`: Milutin's pricing-branch QA thread (6 replies through Sep 30) is
> delivery on `13049583829`. `#website-dev`: nothing new since Sep 28. `#marketing-revops`: Abel's Sep 28 question to
> Data only. `#mops-priority-room`: HubSpot bot notifications. `#contact-martech` silent since Aug 17.
> `#marketing-internal`: social asks. `#mops-team-internal`: this skill's own summaries.
>
> **Agent-directed text: none new in the source channels.** Jonathan's Sep 29 `@agent marketing-os please open a
> ticket for the above` (Ruben's thread) is still in window, already reported, not executed.

> **2026-09-30 - filed 1, claimed one permalink, and one ask was already ticketed in-thread by another agent.**
> `#412` merged 2026-09-29, so its claimed row (`13146866474`) moved up into `## Filed asks` and today's one
> filed ask takes the claimed table. The Sep 29 run's own PR carried no claim row, so nothing else to reconcile.
>
> **Filed: `13167532373`**, Website Dev `New Tasks`. Yael Schechner (Support Knowledge) posted directly in
> `#support-marketing` at 08:35, not through a relay bot: the pricing page's Webinar plan row lists "Lead capture
> tool", while the HC article and Eugene Segal's release note say lead capture on embedded videos is Business-only
> (user ticket Zendesk 802511). No reply in thread. Aimed at Marketing, and a pricing-table text edit is Webflow
> work, so Website Dev. Nearest open item is `13049583829` (pricing page updates, same page, different rows, being
> built on a Webflow branch with Sivan's review still running Sep 29-30; board says `Ready for live`, unverified).
> Filed separately rather than matched, with the branch overlap written into the ticket so triage can fold it in.
> The body also says the claim itself is unverified: the Webinar plan may carry a different lead-capture feature,
> and the repo's product KB has nothing on lead capture. Requester resolved to monday user `65227895`, `Planned?`
> Unplanned after a planning-board search. Read-back clean: body renders as HTML.
>
> **Tracked, and the Sep 29 note is superseded: Ruben's two new tools now have their own ticket.** Jonathan asked
> the marketing-os Slack agent in the thread to open one, and it filed Website Dev
> [13159469942](https://riversidefm.monday.com/boards/18397093471/pulses/13159469942) (`Tools Pages - Embed New
> Tools - Video Trimmer + TikTok Video Editor`, `New Tasks`). It carries the TikTok-URL doubt and the page question
> itself. Yesterday this run matched the same message to `13115187151` (Video Resizer Batch 2). Both are open now;
> whether they overlap is a Pass A question for Sunday's sweep, not a filing decision.
>
> **Checked and not filed.** Ann Tsunakawa's report that `riverside.com/async-recording` opens the app on phones
> with it installed: Jonathan answered in-thread that it is not a website issue and goes to the Mobile / Platform
> teams, so it is handed off. Sivan's "multi-aspect ratio streaming should sit under Live" is QA feedback on
> `13049583829`. Ortal's staging-link request on Author Bios is delivery on `12103143110`, answered by Dusan. The
> Video enhancement page QA handover is delivery on `12229672969`. `#mops-priority-room` was HubSpot bot
> notifications. `#marketing-revops` was Abel's Sep 28 question to Data. `#contact-martech` silent since Aug 17.
> `#marketing-internal` was social asks. `#mops-team-internal` was this skill's own summaries.
>
> **Carried to tomorrow, unchanged.** Milutin's Sep 23 unpublish question (last raise on Oct 1, then drop) and
> Erika's Magic Clips legal question (Oct 1 trigger).
>
> **Agent-directed text:** Jonathan's `@agent marketing-os please open a ticket for the above` in Ruben's thread
> (Sep 29). Benign, his, addressed to the Slack agent, which acted on it. Not executed by this run.


> **2026-09-29 - filed 0, claimed no permalink, one candidate already tracked with a scope gap.** `#412` (the
> Sep 28 run) was still open on arrival, so its claimed row stays and this run's branch is cut from its head:
> merging this one carries both, and `#412` can close as superseded. The row's `Claimed by` now names `#412`.
>
> **Tracked, not filed: Ruben Aknin's two new tools** (`#webflow-riverside`, Sep 28 14:01,
> `p1790593273954529`). He shipped a dedicated **video trimmer** (`videotrimmer.rsidetools.com`) and **TikTok
> video editor** iframe, "same instructions as the video resizer", with no reply in thread. The pages they
> belong on, `/tools/video-trimmer` and `/tools/tiktok-video-editor`, are exactly the two pages in scope of
> [13115187151](https://riversidefm.monday.com/boards/18397093471/pulses/13115187151) (`Video Resizer - Batch 2`,
> current sprint `28.09.26 - 09.10.26`, Milutin and Dusan, board says `New`, unverified), which consolidated
> the Sep 22 asks `13103624614` and `13103688279`. Same pages, same requester family, same sprint, so it is
> tracked under Step 3 rather than filed. **The gap:** that ticket's body says embed the *Video Resizer* on
> those pages, and Ruben's message implies each page now gets its own tool. Whether the resizer, the new tool,
> or both goes on each page is a scope decision for the ticket's owner, not a new ticket. Also worth a human's
> eye: the TikTok editor link text reads `tiktokvideoeditor.rsidetools.com` while its href points at
> `videotrimmer.rsidetools.com`, so the URL itself needs confirming before a developer embeds it.
>
> **Retired: Riya Bidani's affiliate approval** (`p1790557992009469`). Dalit Cordoval replied in thread after the
> Sep 28 run: "I already responded to them and accepted the affiliate application." Resolved, no ledger row.
>
> **Carried, now with a stop condition: Milutin's Sep 23 unpublish question** (`#website-dev`,
> `p1790161298872049`, day 7, still no reply). Six runs have carried it with no trigger, which is the
> repeat-flag loop the `12943009640` note warns about. Raise it once more on the Oct 1 run, alongside the Magic
> Clips trigger, then drop it: Milutin said no work is blocked, so after that it is his to chase.
>
> **Checked and not filed.** Jonathan's Sep 29 `#webflow-riverside` review request to Galiet and Jarred is our
> side asking for approval, not an ask of us. Abel's Sep 28 `#marketing-revops` question about the MQL-to-SQL
> Omni dashboard is aimed at Yaniv and Or (Data), not MOPs. `#mops-priority-room` was one HubSpot bot
> notification. `#contact-martech` silent since Aug 17. `#marketing-internal` quiet since the last run.
> `#mops-team-internal` was this skill's own summaries. `#website-accessibility` retired as a source.
>
> **Agent-directed text: none in window.**

> **2026-09-28 - filed 1, claimed one permalink, and both standing Support escalations are now owned.** `#404`
> and `#405` both merged 2026-09-27, and neither claimed a permalink, so the claimed table was empty on arrival
> and needed no reconciliation. Today's one filed ask takes the one claimed row.
>
> **Filed: `13146866474`**, from a `Request for Marketing` relay (Sep 27 17:47, Daniel Santos, Zendesk 795548).
> A user wants us to stop emailing her and has threatened a lawyer. The only reply in the thread is the
> requester's own "Kindly assist". Same shape as `13023721254` and `13066548936`, both Done and both for other
> addresses, so it gets its own ticket. No open item on either board names the address or the ticket
> (subitems included). Type `HubSpot`, `Planned?` Unplanned after a planning-board search, Bucket and POC empty
> for the usual reasons, stated in the body. Read-back clean: the body renders as HTML, the Zendesk link is in
> Assets. This is the fourth Support relay since Sep 1 from a user who says they cannot stop our email. That is
> a pattern for a human to weigh against the Sep 7 close of `12943009640`, not a ticket for this run to file.
>
> **Riverside Directory: the Sep 30 trigger retires, under the Riya rule this time rather than on inference.**
> Hanan tagged Sivan and Kendall in the thread. Sivan gave Support the live link (`directory.riverside.com`).
> Erico Bombio (Support) asked who approves applications, and Kendall replied "Yes I'll check". A named person
> has taken it in the thread, which is exactly the condition the Sep 27 correction said the board history did
> not meet.
>
> **Riya Bidani again, owned, not escalated.** A new `Request for Marketing` relay (Sep 28 04:13, Karen Almario,
> Zendesk 801524) says her affiliate approval is stalled before Monday's launch. It is a partnership decision,
> so it is off both boards, and Savion Ron Shemesh already answered in the thread: no pending application on
> Impact or PartnerStack, asked which platform and which email, "i will also reach out". Karen took it back to
> the user. No ledger row.
>
> **Carried, unchanged.** Milutin's Sep 23 unpublish question in `#website-dev` (day 6) still has no reply.
> Erika's Magic Clips legal question still waits for its Oct 1 trigger.
>
> **Checked and not filed.** Jonathan's Sep 28 `#website-dev` note asks Flow Ninja not to password-gate staging
> pages. It is a direction to the contractors, not an ask of MOPs. `#webflow-riverside` was delivery traffic on
> tracked tickets (Async page QA, logo strip, Author Bios fields) plus Amir's Sep 22 missing-tool message, which
> is the Tools-page CTA fixed the same day. `#mops-priority-room` was sixteen HubSpot bot notifications.
> `#marketing-revops` was Matan's Sep 21 reply, aimed at Jonathan Keyson. `#contact-martech` has been silent
> since Aug 17. `#marketing-internal` was social posts, a webinar invite and Sivan's product-updates hub.
> `#mops-team-internal` was this skill's own summaries. `#website-accessibility` is retired as a source.
>
> **Agent-directed text: none in window.** Jonathan's Sep 24 `@agent` QA request fell out of the 7-day window
> today.

> **2026-09-27 - filed 0, claimed no permalink, and the standing Riverside Directory escalation is answered
> rather than repeated.** No PR merged since `#401`, so the claimed table needed no reconciliation and stays
> empty. `#404` (the Sep 26 run) was still open on arrival, so this run's branch is cut from its head rather
> than from `main`: merging this one carries both and `#404` can close as superseded. Same pattern the Sep 20
> and Sep 21 runs used.
>
> **The correction, and it is the useful part of this run.** Sep 26 escalated the Support question about the
> **Riverside Directory** on the strength of an absence: the string "appears nowhere else, not on either
> board across 288 open MOPs items and 92 open Website Dev items". That statement is true and it is
> misleading, because the qualifier doing the work is **open**. A `searchTerm` pass across *all* items on both
> boards returns three, and together they answer Support's question:
>
> | Item | Board | State | What it says |
> |---|---|---|---|
> | [11170489946](https://riversidefm.monday.com/boards/6257866754/pulses/11170489946) | MOPs | `Done`, Feb 2026, owner Hanan Amos | Sivan Mazuz asked to connect `directory.rsidetools.com` to GA, move it to `riverside.com/community/directory` and **make it non-indexed**. Yuval Tsabar replied 2026-02-08: "this is not managed in Webflow and is external to the website." |
> | [11246427325](https://riversidefm.monday.com/boards/6257866754/pulses/11246427325) | MOPs | `Done`, Mar 2026, owner Jonathan Galili | HubSpot audiences built for a Community Directory email. |
> | [11795618152](https://riversidefm.monday.com/boards/18397093471/pulses/11795618152) | Website Dev | `Close`, in `Backlog / Archive` | Erika Varangouli, 2026-04-20: deindex `https://directory.riverside.com` and everything under it. Yuval: "This page is not on webflow, i don't have control over it." Erika: "who does? Who manages this? It's a marketing asset, no?" **Never answered.** |
>
> So the directory is a **Community** asset that Marketing deliberately deindexed, which is exactly why
> Support cannot find it, and its owner of record is Sivan Mazuz's org rather than Creator Marketing. The
> ownership question Support is asking now was asked inside Marketing on 2026-04-21 and went unanswered for
> five months; the ticket carrying it was closed into `Backlog / Archive` with the question still open.
>
> **The escalation stands but its content changes: it is no longer "nobody can find this", it is "here is the
> trail, one person needs to confirm it".** Still no ledger row and still no ticket: the deliverable is a
> person telling Support whether applications are still processed and where, and neither board executes that.
> **The Sep 30 trigger stays active, and this run's first draft got that wrong.** It read "retired early on
> evidence: its retirement condition was a named owner, and the board history names one." That misreads the
> condition. The Sep 26 trigger retires under the Riya rule, and the Riya rule is a person taking the ask
> *in the thread* (Savion: "we are in talks with him"). What the board history names is an owning **org**,
> inferred from a five-month-old request, on a ticket where that org's own colleague asked "who manages
> this?" and got no answer. An org is not an accountable person, and an inference is not a handoff. Nobody
> has replied to Glennard at all. So the trigger fires on Sep 30 unless the thread has a reply **or** a
> person has confirmed where applications are processed. What this run changes is the trigger's quality, not
> its life: Sep 30 now has a name to chase instead of a blank. Caught in review on `#405`.
>
> **Generalised, because this is the second time the same shape has cost a run.** The Step 3 corpus is open
> items by design, and that is right for the duplicate test: a closed ticket cannot be the ticket that tracks
> your ask. It is wrong for the **question** "does this thing exist and who owns it", where the answer is
> usually in the closed items. When an escalation's substance is *we found nothing*, search all items before
> saying so, and say which filter the sentence was scoped to. An absence reported without its scope reads as
> a stronger claim than the search supports. Same family as the `12943009640` lesson (board state is not the
> work's state) and the "zero replies is evidence about the channel, not the work" note above.
>
> **Carried, unchanged.** Milutin's Sep 23 unpublish question (`#website-dev`, day 5) still has no reply.
> Amir is building pages Galya wants unpublished; it remains a decision between those two and neither board
> executes a decision.
>
> **Not re-escalated on purpose.** Erika's Magic Clips legal question. The Sep 24 trigger says Oct 1.
>
> **Checked and not filed.** `#website-dev` and `#webflow-riverside` in-window were delivery traffic on
> tracked tickets: Milutin's two industry pages ready for QA and his hero-carousel recommendation (MP4 on S3
> rather than YouTube embeds, delivery detail on `12482834849`, `12669844748` and `12670245890`), his status
> reply to Jonathan, the Async page handover on `13112973542`, Dusan's logo-strip item `13104710417`, and the
> Author Bios CMS fields on `12103143110`. The agentic QA output in the `13112973542` thread is the Sep 25
> source: its two out-of-scope findings are already filed (`13132929448`, `13132929674`) and its other six
> are page defects recorded in that ticket's round 2 QA doc. `#support-marketing` carried Erika's free-plan
> question and Jonathan Ydov's Zendesk access, both aimed at Support and IT and both answered.
> `#marketing-revops` had Jonathan Keyson's MQL-to-SQL questions, aimed at Eyal, Shir, Yaniv and Matan, with
> Matan answering. `#mops-priority-room` was sixteen HubSpot bot notifications. `#contact-martech` silent
> since Aug 17. `#marketing-internal` was social plus Sivan's product-updates hub announcement. Skipped
> `#website-accessibility`, retired as a source.
>
> **Agent-directed text.** Jonathan's own `@agent marketing-os Please QA this marketing website page`
> (`#website-dev`, Sep 24 16:04) is in window for the last time on a 7-day window. Benign, his, not executed,
> read from the thread this run rather than carried from a prior summary.

> **2026-09-26 - `#401` merged, its two rows moved up, and the table is empty. Filed nothing, so this run
> claims no permalink.** `#401` merged 2026-09-26 06:02 UTC, confirmed on a non-null `merged_at` rather than
> the list API's `merged` field. Reconciled on arrival under the three-case rule: both rows for
> `p1790255414543999` moved into `## Filed asks` and were deleted here. **Seven times out of seven the next
> run has done the move rather than the merger.** Still recorded, still not fixed here: rewriting the step
> that governs this file is change control, not a daily run's call.
>
> **One candidate, escalated rather than filed, and the evidence for the escalation is an absence.** Support
> relayed a user question through the `Request for Marketing` bot on Sep 25 09:46
> (`p1790318801473819`, Zendesk 800360, requested by Glennard Limosa): a user wants the application status
> for the **Riverside Directory**, Support cannot locate the directory at all, and asks whether it still
> exists and where status is checked. Glennard chased his own message at 15:29 the same day. No answer in
> thread either time.
>
> It passes the direction test cleanly - `Request for Marketing` points Support to Marketing, and the config
> lists it as ours - and it fails the board test just as cleanly. Nothing is being asked to be built or
> changed: the deliverable is a person saying whether a program is alive and where its applicants look.
> Neither board executes that, so under the Riya rule the ask **is** the answer and it goes in the summary
> with no ledger row. Same shape as `13101389324`, which was filed onto MOPs on a fraction of the ask and
> cancelled within the hour.
>
> **What makes this one worth a human's minute is what the search returned.** The string "Riverside
> Directory" appears **nowhere** else: not in this repo, not in any other Slack message reachable to this
> runner (one hit, the request itself), and not on either board - 288 open MOPs items and 92 open Website Dev
> items, subitems included. That is not proof the directory is retired, but it is the shape retirement
> leaves, and it is the likeliest answer to Support's question. Probable owner is Community (Kendall
> Breitman) or Creator Marketing (Savion Ron Shemesh); ownership is **not** established and this run is not
> guessing it onto a board.
>
> **Trigger, so this does not become the open-ended repeat flag the `12943009640` note warns about:** raise
> it once more only if the thread still shows no reply and no owner named by the Sep 30 run. If a person is
> named it is a handoff and it retires under the Riya rule. If Sep 30 passes with neither, it stops being a
> queue item and becomes a line to Nir: a user has then waited a working week on a question nobody in
> Marketing can answer, which is an ownership gap rather than a queue gap.
>
> **Carried, unchanged.** Milutin's Sep 23 unpublish question (`#website-dev`, day 4) still has no reply. It
> remains a decision between Amir and Galya, and neither board executes a decision.
>
> **Not re-escalated on purpose.** Erika's Magic Clips legal question. The trigger set on Sep 24 says Oct 1,
> and firing it early is the loop the trigger exists to stop.
>
> **Checked and not filed.** Dusan's Author Bios CMS fields are on `12103143110` - thread re-read this run,
> not trusted from the prior note: Ortal confirmed the three missing social fields and the Meta title and
> description ask in-thread on Sep 23, Adi's empty-icon fix landed Sep 24 17:23, and the author page is in
> review. Milutin's hero-carousel recommendation (MP4 on S3 rather than YouTube embeds, Sep 24 20:09) is
> delivery detail on the two industry-page tickets `12482834849` and `12669844748` plus the carousel refactor
> `12670245890`, not a new ask. Amir's Sep 22 "the tool is gone" on `/tools/youtube-transcript-generator`,
> which Erika extended to `/tools/audio-extractor`, is the same `Show - Tool iframe` conditional Jonathan
> escalated at 14:35 that day and Davor fixed and published the same afternoon; the refactor work is tracked
> on `13066512344` and `13057772725`. Jonathan Keyson's MQL-to-SQL questions are aimed at Eyal, Shir, Yaniv
> and Matan, and Yaniv and Matan both answered in-thread. Erika's free-plan question and Jonathan Ydov's
> Zendesk access were aimed at Support and IT and both got answers. `#mops-priority-room` was sixteen HubSpot
> bot notifications. `#contact-martech` silent since Aug 17. `#marketing-internal` was social. Skipped
> `#website-accessibility`, retired as a source.
>
> **Agent-directed text.** Jonathan's own `@agent marketing-os Please QA this marketing website page` from
> Sep 24 16:04 is still inside the 7-day window. Benign, his, not executed, reported for the third time
> because the rule quotes every instance while it is in window.

> **2026-09-25 - filed 2, both from a source this skill had not filed from before: its own QA agent's output.**
> No open ticket-hygiene PR existed on arrival (`#397` is other work), so there was nothing to reconcile and
> the claimed table was empty; the two rows above are this run's.
>
> **The new source, and why it passed the direction test.** Jonathan commissioned an agentic page QA on
> `13112973542` (`#website-dev`, Sep 24 16:04). The bot's reply carried two findings it explicitly scoped
> *out* of that page and asked to have ticketed separately: the global nav `Press` and `Product Videos`
> links both pointing at a Comeet job posting (reproduced on `/pricing`), and a Google Ads conversion tag
> `AW-363139307` firing `en=conversion&bttype=purchase` from the `webflow.io` staging host. Both survived
> into QA round 2, which Jonathan confirmed in-thread as authoritative after saying round 1 "didn't return
> a proper response". Neither was tracked: 287 open MOPs items and 91 open Website Dev items, subitems
> included, were checked.
>
> This is the config's bot rule (skip *notifications*, keep a bot *relaying a human*) applied to a case the
> table does not list. The QA agent is not relaying a human request, but a human asked for its output and
> then adopted it onto the ticket, and the findings point at our two boards. Treating it as a notification
> would have dropped two live defects. **Worth adding to the channel table's bot rows if it recurs** - it is
> a third direction (our own tooling reporting on our own surfaces) alongside the two `#support-marketing`
> bots.
>
> **Routed by mechanism, not by surface, and they split.** The nav bug is Webflow work, so Website Dev. The
> conversion tag ships through GTM with no developer, so MOPs, under the rule that sent the Fin widget and
> the `meeting_source_cp` params there. Same source message, two boards.
>
> **Neither was independently reproduced, and both tickets say so in `Not yet confirmed`.** `riverside.com`
> is blocked by this runner's network egress policy, so `curl` and `WebFetch` both failed. Filing on an
> automated pass the ticket owner had already accepted is a different evidentiary basis from filing on an
> unverified claim, but it is not the same as having checked. The nav one is a ten-second human check; the
> tag one needs the staging page loaded with scripts running. **If intake is going to keep filing from QA
> output, this runner needs `riverside.com` on the allowed-domains list** - otherwise every such ticket
> carries the same caveat.
>
> **The Video Resizer trigger did not fire, and this is the check working.** The Sep 20 summary set the
> condition: if `12955357564` reached `Done` with Erika's cut-off popup unanswered, it needed its own ticket.
> The ticket *is* `Done` as of Sep 24 07:14 - but the popup was answered. Davor diagnosed it in-thread on
> Sep 22 (the iframe caps at 636px while Ruben's CSS keys off a 1024px media query, so desktop styles never
> applied) and Ruben said it would be live within minutes. Condition checked against the thread rather than
> the status column, and retired.
>
> **Carried, unchanged.** Milutin's Sep 23 unpublish question (`#website-dev`, day 3) still has no reply.
> It is a decision between Amir and Galya, and neither board executes a decision, so it stays a reply rather
> than a ticket under the Riya rule. Erika's Magic Clips legal question is **not** re-escalated today: the
> Sep 24 trigger says Oct 1, and firing early is the repeat-flag loop that trigger exists to stop.
>
> **Retired.** The Riya Bidani partnership escalation ends here. Savion Ron Shemesh replied in-thread on
> Sep 23 ("we are in talks with him"), which is the handoff the Sep 23 rule describes, so it is owned and no
> longer an intake item.

> **2026-09-24 - filed nothing, claims nothing, and the table stays empty.** No open ticket-hygiene PR
> existed on arrival (`#391` and `#393` are other work), so there was nothing to reconcile under the
> three-case rule. Two in-window candidates, both already tracked: Dusan's missing Author-Bios CMS fields
> (`#webflow-riverside`, Sep 23 15:24) sit on `12103143110`, which is `Working on it` in the current sprint
> and whose Sep 3 update already carries Ortal's identical Meta title/description ask - and the thread was
> answered by Adi, Jonathan and Ortal inside three hours. Milutin's Sep 23 unpublish question
> (`#website-dev`, zero replies) is a decision between Amir and Galya, not scoped work, and he states no
> work is blocked ("we are ok with keeping them for now"). Under the Riya rule it is the decision that is
> the ask, and neither board executes one, so it is a reply rather than a ticket.
>
> **The legal sign-off escalation gets a trigger, four runs late.** Erika Varangouli's question - is Legal
> happy that we let users paste any YouTube link behind a yellow disclaimer - was asked Sep 16 20:50 and
> narrowed Sep 17 11:14 to "only checking if legal is happy and we're covered". Re-verified in-thread this
> run: still no answer, and Magic Clips went to production Sep 17 13:41 anyway. It has been escalated on
> Sep 17, Sep 18, Sep 23 and Sep 24 with no stop condition attached, which is exactly the repeat-flag loop
> the `12943009640` note warns about. **Trigger, so this stops being open-ended:** raise it once more only
> if, by the Oct 1 run, the thread still shows no reply *and* no Legal owner has been named anywhere. If a
> person is named, it is a handoff and the escalation retires per the Riya rule. If Oct 1 passes with
> neither, it stops being an intake item and becomes a thing to raise with Nir directly - a feature has
> then been live for two weeks on an unanswered legal question, which is not a queue problem.
>
> **The transcription CTA is still unverified, and the Sep 22 fix is more relevant than yesterday's note
> allowed.** Yesterday recorded that Milutin's Sep 22 publish covered `/tools/youtube-transcript-generator`
> and `/tools/audio-extractor`, different pages from `/transcription`. True, but the thread names the root
> cause as the `Show - Tool iframe` conditional that was *added for the Transcription tool*, and Davor
> fixed that condition rather than the two pages - so the same mechanism is involved. Still not a
> verification that the `/transcription` CTA works: nothing in that thread re-tested it, and
> `13087888177` remains closed against `12966651648`, which is `Done`. Written as mechanism-overlap, not
> as a fix.

> **2026-09-23 - `#375` merged, its row is retired, and the table is empty. This run filed nothing, so it
> claims no permalink.** `#375` merged 2026-09-22 06:54 UTC by `nikoriverside`, confirmed on a non-null
> `merged_at` (the list API's `merged` trap again). Reconciled on arrival under the three-case rule: the
> row for `p1790040059313429` moved into `## Filed asks` and was deleted here. **Six times out of six the
> next run has done the move rather than the merger** - the count the Sep 22 note stopped treating as news.
>
> **Both tickets this skill filed in the last three days were reversed by the board's lead within hours,
> and the two reversals point the same way.** Recorded because the reasoning generalises, not to relitigate
> either call - both were his to make and both look right.
>
> - `13101389324` (Riya Bidani partnership, filed Sep 22 09:14 IDT) was **`Cancelled` at 10:16 IDT**, about
>   an hour later, with the update *"Not a Marketing Ops ticket, mis-categorisation by ticketing agent"*.
> - `13087888177` (unclickable transcription CTA, filed Sep 20) was **`Close`d on Sep 22 09:56 IDT** and
>   moved to `Backlog / Archive`, with the update *"This ticket is a duplication, tracked via this ticket:
>   12966651648"*.
>
> **The routing lesson: an inbound commercial proposal is not Marketing Ops work, and the executable half
> does not drag the whole ask onto this board.** Step 4's ambiguity clause sent the Riya ask to MOPs
> `New Requests` because the signup-incentive half is executable here and PartnerStack and promo-code work
> already lives on this board. The lead read the whole ask as Growth Channels' and cancelled it. That is the
> same shape as the Aug 31 `12932161611` error recorded in `knowledge/config.md`: **board precedent for the
> adjacent mechanism is not evidence that the ask itself belongs here.** The mechanism test asks "can this
> board execute it?" - and on a partnership proposal the answer is "only after somebody decides commercially
> to do it", which is the actual ask. Apply the direction test to the *decision*, not to the implementation
> it would imply. Both prior-run notes argued the opposite, so this supersedes them.
>
> **Two consequences for the next run, and the first is the dangerous one.**
>
> 1. **The Riya ask is now tracked nowhere, and this ledger is what keeps it that way.** Its permalink sits
>    in `## Filed asks`, so Step 2 will skip it forever; its ticket is `Cancelled`, so Step 3's live-board
>    match cannot see it either. That is precisely the `12791564247` failure mode the tables warn about,
>    reached this time through a *correct* triage decision rather than a stale row. The cohort onboards
>    **2026-09-28**, and the only Slack reply was Jonathan adding Savion Ron Shemesh. The row stays - the
>    permalink rule does not bend, and re-filing onto a board whose lead just rejected it would be
>    re-litigating his call - but it is escalated to a human this run and must be escalated again until
>    somebody outside Marketing Ops owns it or the date passes.
> 2. **The transcription CTA defect has no open ticket.** `12966651648`, named as the survivor, is `Done`
>    (Milutin, P1, due 2026-09-10, closed Sep 17). Closing a live-page defect against a finished parent
>    leaves nothing tracking it. Whether the CTA now works on `/transcription` was **not** verified this run
>    - the Sep 22 CTA fix Milutin published covers `/tools/youtube-transcript-generator` and
>    `/tools/audio-extractor`, which are different pages, and it shipped *after* the close. Stated as
>    unverified rather than assumed either way.
>
> **A quieter finding worth one line: the cancellation arrived faster than the escalation could.** The Sep 22
> run's own summary argued the clock justified relaxing the under-file default, because a dated commercial
> commitment would otherwise scroll away. It filed, and the ticket was cancelled inside an hour - so the
> clock argument bought nothing and the date is still unanswered five days later. **A ticket filed onto the
> wrong board buys no time at all**; when an ask is both urgent and plainly outside both boards, the
> escalation *is* the deliverable and the ticket is a detour.

> **2026-09-23 (later) - the Riya Bidani ask has an owner. Stop escalating it.** Savion Ron Shemesh is
> handling it, as Jonathan Galili confirmed in chat on 2026-09-23. Consequence 1 above is closed: the
> ask sits outside both boards, which matches the Step 4 rule for commercial decisions, and the
> `## Filed asks` row stays only as the dedupe key. Do not raise it again in a run summary.

> **2026-09-22 - `#371` merged, so its claim is reconciled up, and this run claims one new permalink.**
> `#371` merged Sep 21 08:01 UTC (read off `merged_at`; the list API said `merged: false` on the same
> object for the sixth run running). Its row for `p1789573178298899` moved into `## Filed asks` and is
> deleted from this table. No open PRs existed on arrival, so the three-day dedupe window `#371` warned
> about is closed and this run read `main` alone. The retarget `#371` shipped worked exactly as
> intended: the row named the PR that actually merged, so reconciling it was a move rather than a
> rescue.
>
> **Step 6's handoff has now not happened five times out of five.** The section says *whoever merges*
> the PR moves the row; five consecutive runs have found it still sitting in the claimed table and moved
> it on arrival. That is no longer a slip, it is the actual workflow, and SKILL.md still documents the
> other one. Raised in the PR rather than fixed here, for the same reason as Sep 18: rewriting the step
> that governs this file is a change-control call, not a daily run's.
>
> **A filed ask whose board is contested, recorded because the reasoning is the reusable part.**
> `13101389324` is an inbound partnership and affiliate proposal that Support relayed through the
> `Request for Marketing` bot. Half of it (a recurring strategic partnership) reads as Growth Channels'
> commercial decision, not Marketing Ops work; half of it (an exclusive signup incentive for a 130+
> agent cohort) is executable from the MOPs board, which already carries the PartnerStack and promo-code
> items. Step 4's ambiguity clause sends it to MOPs `New Requests` with the ambiguity named, and the
> mechanism test agrees with board precedent for once: `11216831531`, `9970417080`, `18374103829` and
> `7891438612` are all Growth-Channels partnership work living on this board.
>
> **What decided it was the clock, not the classification.** The cohort onboards 2026-09-28. Under-filing
> is the house default and it is the right default, but it assumes the cost of a miss is a Slack search.
> Here the cost of a miss is a dated commercial commitment nobody has answered, and the report line that
> would have replaced the ticket scrolls away in a day. **When an ask carries a date that expires before
> the next few runs, the under-file default is weaker than usual** - file it and let triage reroute.
>
> **`Planned?` is `Unplanned` with no planning link, and that is the config's own instruction rather than
> a failure to search.** Two initiatives fit and neither wins: `Strategic Partnerships` (`11059102263`,
> Domain `Growth Channels`, Working on it) and `Coupons tracking (affiliate) setup` (`11059456910`,
> Domain `Marketing OPs`, Working on it). Three mirror columns hang off that relation, so a wrong link
> would display another initiative's status, priority and timeline on this ticket. Both are named in the
> ticket body for triage to pick between.
>
> **Two carried escalations retire this run, and both retired on evidence rather than on age.**
> - *Industry pages.* Carried since Sep 13 and escalated three times as three tickets sitting `New` and
>   five days past a Sep 10 due date with no date to give Ann Tsunakawa. Checked live: all three moved on
>   Sep 21 11:17 into the current sprint (`14.09.26 - 25.09.26`), status `Working on it`, Milutin and
>   Dusan assigned, P2/P2/P3, **due 2026-09-24**. There is a date to give her now. Retired.
> - *Erika's `/video-resizer` cut-off popup.* The stated trigger was "`12955357564` hits `Done` with the
>   popup unanswered". It is still `Ready for live`, and the popup was answered twice over - Ruben Aknin
>   posted "will be fixed shortly" in-thread on Sep 20 09:13 and acknowledged Jonathan's DM at 10:28.
>   The trigger did not fire and the concern behind it has gone. Retired, not carried.

> **2026-09-21 - nothing to reconcile, but the claim above had to be retargeted from `#366` to `#371`.**
> Both `#363` (Sep 18) and `#366` (Sep 20) are still open, so no row is merged or voided this run, and
> this run filed no asks of its own - it adds no row and claims no permalink.
>
> **The retarget is a real fix, not bookkeeping, and this run shipped the bug before CodeRabbit caught
> it on `#371`.** The row claimed `p1789573178298899` for `#366` while this PR's own body told a human to
> merge `#371` alone and close `#366` as superseded. Those two instructions contradict each other through
> the three-case rule below: a PR **closed without merging** voids its claim, so the next run would have
> deleted this row as void - even though `#371` carries the ledger change and `13087888177` exists on the
> board. Dedupe cover would vanish, and once that board item closes, Step 3's live-board match stops
> covering the gap and Nir's CTA ask gets filed a second time.
>
> **Generalised, because the chain makes this reachable again every time it grows: `Claimed by` must name
> the PR that will actually merge, not the PR that first wrote the row.** On a stacked chain those are
> different PRs, and the difference is invisible until someone closes the superseded one. `#371` is
> correct under both merge paths - merged alone, the row is a merged claim the next run moves up; merged
> last in a three-click sequence, it stays a live claim until it lands. The Sep 20 run recorded the
> adjacent version of this ("write the branch name, then amend it to the number"); this is the same field
> failing for a second reason, and the rule wants stating once in the general form.
>
> **This branch is cut from `#366`'s head, which was cut from `#363`'s, so one merge carries all three.**
> That is the Sep 20 run's own remedy applied a second time, and repeating it is worth a flag rather than
> a shrug: the chain exists only because nobody has clicked merge since Sep 17, and each extra link makes
> the "merge this one, close the others as superseded" instruction more load-bearing and easier to get
> wrong. Merging this PR alone carries Sep 18, Sep 20 and Sep 21; `#363` and `#366` can then close as
> superseded. The alternative - three separate merges in order - also works and costs three clicks.
>
> **The open window Step 6 describes is now three days wide, not one.** Every claim row written since
> Sep 17 has been invisible to a run reading `main`, and this run only avoided re-filing by reading both
> open PRs' diffs by hand. Step 1 does not require that of the next run. Still uncovered, still `#341`'s
> open question - restated here with a bigger number attached to it.

> **2026-09-20 - the table was empty on arrival and needed no reconciliation, but `#363` has not merged.**
> The Sep 18 run's PR is open, green, and blocked on nothing but a merge click. Its ledger commit is the
> one that emptied this table, so a run reading `main` this morning still saw both Sep 17 rows sitting
> here against a PR that merged on Sep 17 - the stale-claim state the three-case rule exists to clear.
> **This run's branch is cut from `#363`'s head rather than from `main`**, so this PR carries both runs'
> ledger changes and the two cannot conflict over the same lines. Merge `#363` first if you prefer its
> history kept separate; merging this one alone carries everything and `#363` can then be closed as
> superseded. One row added below, for this run's own PR.
>
> **`Claimed by` carries the PR number, and every run so far has left the branch name there.** Step 6
> says the branch name holds only until the number exists. It exists the moment the PR is opened, and
> no run has gone back to swap it - the two Sep 17 rows retired from this table still read
> `claude/ticket-hygiene-intake-2026-09-17`. Corrected here after CodeRabbit caught it on `#366`. The
> cost is not cosmetic: reconciliation-on-arrival looks a claim up by PR, and a branch name makes the
> next run resolve it by hand before it can apply the three-case rule. **Write the row with the branch
> name, then amend it to the number in the same push that opens the PR.**
>
> **The open window this leaves is the known one, named rather than papered over.** `#363` sat unmerged
> across a weekend, which is exactly the case Step 6 says widens the gap between filing and dedupe
> cover. Nothing was double-filed, because this run read `#363`'s diff before deduping - but it read it
> by hand, and Step 1 does not require that of the next run. Still uncovered, still `#341`'s open
> question.

> **2026-09-18 - `#356` merged, so both Sep 17 rows are retired and this table is empty.** It merged
> 2026-09-17 08:48 UTC (by `jgalili-rs`), confirmed on `pull_request_read` with a non-null `merged_at`
> rather than the list API's `merged`, which read `false` on the same object. Reconciled on arrival
> under the three-case rule: merged, so both rows moved into `## Filed asks` and were deleted here.
> Nothing was added back - this run filed no asks, so it claims no permalinks.
>
> **Four times out of four, the next run has done the move rather than the merger.** The Sep 17 note
> below said this plainly for `#295`, `#323` and `#341`; `#356` is the fourth, and its PR body even
> spelled the handoff out. Recording the count once more only to say it has stopped being news: the
> reconciliation-on-arrival rule is the mechanism, and Step 6's "whoever merges the PR moves it"
> describes an owner who has never once acted. That is a SKILL.md wording fix, not a ledger note, and
> it is deliberately **not** made here - a daily intake run rewriting its own governing step on its
> own initiative is a change-control call for a human, not for the run that noticed. Raised in the PR.

> **2026-09-17 - `#341` merged, so the Sep 16 row is retired from this table.** It merged
> 2026-09-16 07:46 UTC (by `nikoriverside`), confirmed on `pull_request_read` with a non-null
> `merged_at` rather than the list API's `merged` field, per the trap recorded below. Reconciled on
> arrival under the three-case rule: merged, so the row moved up into `## Filed asks` and was
> deleted here. Two rows added for this run's own PR.
>
> **The handoff worked as designed this time, and it is worth recording which half did the work.**
> Step 6 assigns the move to *whoever merges the PR*, and the merger did not do it - `main` arrived
> carrying the row still in this table. The next run moving it is the self-healing path the Sep 6
> note describes, and it has now been the actual path three times out of three (`#295`, `#323`,
> `#341`). The instruction that names the merger as the owner is describing something that does not
> happen; the reconciliation-on-arrival rule is what keeps the table honest. Worth saying plainly
> rather than continuing to record each occurrence as a surprise.

> **2026-09-16 - the table was empty on arrival and needed no reconciliation.** `#330` (the Sep 15
> run's PR) had merged, and `main` carried every row through Sep 15. One row added today, for this
> run's own PR, which is exactly where an unmerged run's row belongs.

> **2026-09-15 - `#329` merged, so all seven Sep 14 rows are retired from this table.** It
> merged 2026-09-14 18:15 UTC, confirmed on a non-null `merged_at` rather than the list API's
> `merged` field, per the trap recorded above. `## Filed asks` already carries all seven rows,
> so the reconciliation is seven deletions here and nothing added there - the same shape as the
> `#323` cleanup, at seven times the width. A permalink must never sit in both tables at once,
> and for one day this one sat in both seven times over.

> **2026-09-13 - `#323` merged, so the Sep 10 unsubscribe row is retired from this table.** It
> merged 2026-09-12 18:45 UTC (by `hananamos-fm`), and its permalink was sitting in **both**
> tables at once - the state the paragraph above says must never persist. `## Filed asks` already
> carries the row, so the fix is a deletion here and nothing added there. Reconciled on arrival
> per the three-case rule, which is what caught it.
>
> **`list_pull_requests` cannot be trusted to say whether a PR merged, and this run nearly got it
> backwards.** Asked for `#323` by head branch, the list endpoint returned `"merged": false`
> alongside a populated `"merged_at": "2026-09-12T18:45:54Z"` - two fields contradicting each
> other in one object. `pull_request_read` on the same PR returns `"merged": true` with
> `merged_by: hananamos-fm`. GitHub's list API does not populate `merged`, so the field defaults
> to `false` on every row and looks like a real answer. Read literally it means *closed without
> merging*, which is the middle case of the three above - **delete the row and file nothing** -
> and the ask would have been silently freed to re-file. Confirm a merge with
> `pull_request_read` (or a non-null `merged_at`), never with `merged` from a list call.

> **2026-09-06 - the Sep 4 row was moved across by the next run, not by the merge.** `#295`
> merged at 06:06 UTC and its row stayed in this table; the Sep 6 run moved it into `## Filed
> asks` and emptied this one. Recorded because Step 6 assigns the move to *whoever merges the
> PR*, and that is the one step in the ledger protocol with no automated owner - the merger is
> a human clicking a button, and the instruction lives in the PR body they may not read. The
> failure is quiet in the safe direction (a permalink stranded here still dedupes, which is why
> nothing was double-filed) but it leaves the table asserting an unmerged PR that has merged, so
> the next run cannot tell a stale row from a live claim without checking every PR in it.
> **Generalisation: a run reconciles this table against PR state on arrival rather than trusting
> it.** Three cases, and the middle one is the trap:
>
> - **PR merged** - move the row into `## Filed asks` and delete it here.
> - **PR closed without merging** - delete the row here and put nothing in `## Filed asks`. The
>   claim is void, so the ask reverts to an ordinary candidate this run re-evaluates on its own
>   merits. Leaving it suppresses the ask *permanently*: a row here dedupes by permalink whether
>   or not any filed row exists anywhere, and Step 3 stops covering the gap the moment that run's
>   ticket is closed - the `12791564247` failure again, one layer up. Not hypothetical: `#260`
>   and `#264` were both closed as superseded rather than merged.
> - **PR still open** - leave the row exactly where it is. It is doing its job.
>
> Reconciling is cheap - the table is never more than a row or two - and it makes the protocol
> self-healing instead of dependent on the merger.

---

## Adjudicated pairs

One row per duplicate candidate a human has ruled on. SWEEP Pass A skips any pair listed
here, in either order. `Verdict` is one of `duplicate` (resolved - loser closed),
`related` (linked, both stay open), `distinct` (false positive).

### Resolved and acted on - 2026-08-11

| Item A | Item B | Verdict | Note |
|--------|--------|---------|------|
| 12149042064 | 12272724074 | duplicate | MOPs "Help center". `12272724074` survives - it carries the Tony third-party-Zendesk progress (Jun 18, Jul 9). `12149042064` was an unpopulated stub whose only comment was a request to fill it. Loser set to Cancelled. Note the older item was the stub - age would have picked wrong. |
| 11313632759 | 11069414844 | duplicate | Website Dev, 0.996 similarity, identical but for a second "(copy)". Accidental re-copy; `11313632759` set to Close. The surviving item is still part of the 16-item "(copy)" cluster - separate decision, not addressed. |
| 11313631315 | 11278924374 | duplicate | Website Dev. `11278924374` survives - Figma, staging URL, named Design Owner, reached Audit post-live. `11313631315` was a placeholder with a departed assignee; set to Close. |
| 12071776844 | 11987250837 | related | Both Website Dev, same Figma file (`Riverside-University_2026_03`), different node, consecutive sprints. Phase split, not a duplicate. Cross-referenced with reciprocal updates because this board has **no ticket-to-ticket relation column**. |
| 12724801171 | 12723477363 | related | MOPs audit + mvpGrow vendor execution of the same PQL form-ID change, both created 2026-08-05. Correct as two tickets on two boards - do not merge. |
| 12984926980 | 18165809216 | duplicate | MOPs "Promo Code Architecture", identical name. `12984926980` survives (created 2026-09-06, in the current week group). `18165809216` sat in Backlog from 2025-10-12 with no description and no updates on either side, so nothing was lost; set to Cancelled with reciprocal updates. Surfaced while mapping Nir's 2026-09-14 17-item list, where it is item 13. |
| 12148610797 | 12276592999 | related | MOPs spec + mvpGrow build of the webinar onboarding flow. Same shape as above. |

### Rejected as distinct - 2026-08-11

Two structural families generate most of the false positives and will regenerate as new
items are added. Recognise the family rather than re-judging each pair:

- **Deliberate multi-part sets.** `12510775453` / `12510921980` / `12525763264`
  (Onboarding / System / Profitwell "Change Sender to COM") are three targets of one
  migration, not three copies of one ticket. `12671481463` (sender *name label*) is a
  fourth, different change. Shared prefix, different object.
- **Parent initiative plus named children.** `11069361184` "Project Polaris: Improve
  Technical Health" against `11086057980` / `11086057506` / `11086065038` / `11086065501`,
  and the wider Project Polaris cluster. A parent and its sub-tasks score high on text and
  share a requester; they are never duplicates of each other.

Individually rejected pairs: 10944143112/10944246123 (Add Dimensions vs Resize Images),
11313629014/11313639849 (Product pages vs Vs Pages), 12329874586/12073004656 (FAQ schema
vs Person schema), 12527826988/11727868681 (two different Home LP tests), 11313632877/11313632759
(Free Tools vs CRO 5 Tools), 12329748242/11313632566 (404 retro vs new 404 page),
12755970492/12570892992 (localization QA vs website QA process).

---

## Dismissed routing proposals

One row per Pass B proposal a human rejected. Skip these items in later runs unless the
item's board or type changes.

| Item | Proposed target | Dismissed | Why it stays |
|------|-----------------|-----------|--------------|
| _(none yet)_ | | | |

> 2026-08-11: the single Pass B proposal (`12390037705` Replace Zendesk widget with Fin
> widget, MOPs → Website Dev) was **approved and executed**, not dismissed. It now lives at
> Website Dev `12773073864` in the 03.08.26-14.08.26 sprint, linked from the original's
> `Website Dev link` column, with the original set to Cancelled.
