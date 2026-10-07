# Moon at Dawn: IDs, roster and data quirks

## Where things live

| What | ID |
|------|----|
| Agencies board (Partnership CRM workspace `16715366`) | `18423812252` |
| Moon at Dawn item on it (column `account_contact` links the creators) | `12638699008` |
| Deliverables board | `18423812249` |
| Creators board | `18423812254` |
| Shared Slack channel `#moonatdawn-riverside` | `C0ASHCWEHGA` |
| Report owner: Savion Ron Shemesh | `U09340B5HCM` |

Deliverables columns used: `project_status` (Status), `board_relation_mm5xc4gp` (Creator), `date_mm5ndssr` (Post Date), `numeric_mm5ns47f` (Engagement %), `text_mm5s1607` (UTM), `link_mm5ny888` (Link). Live = `Posted` or `Results`. `Views` (`numeric_mm5nhm2t`) is almost never filled for LinkedIn, so it is not in the report.

Filter the Deliverables board with `board_relation_mm5xc4gp` `any_of` the roster's creator item ids; a search on the agency name matches nothing.

## Slugs

The roster and each creator's UTM spellings are the `VALUES` list at the top of `funnel.sql`; that list is the one to edit. A creator's `utm_campaign` is normally their full name, lowercased, no spaces. Known misspellings in live links, kept as aliases so the traffic is not lost:

| Creator | Also tracked as |
|---------|-----------------|
| Jason Vana | `jasanvana` |
| Phill Agnew | `philagnew` |
| Christine Goos | `christinegoeoes` |
| Sonke Venjacob | `soenkevenjacob` |

To find a new misspelling, list `ORIGINAL_UTM_CAMPAIGN` values with `utm_medium=creator` and `utm_source=linkedin` for the last 30 days and look for near-matches to roster names.

## Quirks seen on the first build (2026-09-28)

- **Placeholder post dates.** Phill Agnew, Allison Rossi, Christine Goos and Arpit Singh were marked Posted with a Post Date of Sep 30 or Oct 1 (placeholders). The report dates each post by its first tracked visitor, never by the board date.
- **Pre-launch clicks.** Draft links get clicked in review before the post is live (Lottie Unwin Aug and Sep, Jeremy Laight Sep, Kobi Omenaka Sep, Adam Knorr, Lindsay Rios). The live-post rule in SKILL.md step 6 drops them.
- **Only Andrew Tindall's link goes through Bitly** (`creators.riverside.com/AndrewTindall`). The rest link straight to riverside.com with UTMs, so clicks come from site visitors, not Bitly.
- **The B2B stages stop before revenue so far.** As of 2026-09-28: 5 SQLs, 4 of them Closed Lost and 1 at SQL stage with no SQL record; 0 won. The one paid customer is self-serve (about $32 MRR). The report shows counts only; the detail stays internal.
- **Some posts in the Moon at Dawn roster have no link at all** (reposts, a podcast mid-roll). They count as live posts on the board but produce no funnel row.
