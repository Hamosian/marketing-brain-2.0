# Dashboard spec - Hanan's chief of staff

The live artifact is the second surface of `/hanan-chief-of-staff`. Same rows as the chat
brief, clickable, refreshed in place. It is deliberately smaller than Nir's team-tasks board
(`.claude/skills/growth-marketing-team-tasks/knowledge/dashboard-spec.md`): one person, one
day, nine sections. Reuse its hard-won rules where they apply; they are listed at the end.

## Canonical artifact - update in place

- **Canonical URL:** `https://claude.ai/artifact/WN2rx5HhDxPgqR9GKAYaD3`
- Same conversation that published it: republish the same file path (`assets/dashboard.html`).
- Any other run: pass the canonical URL as `url` to the Artifact tool. Never mint a new one.
- Favicon `🗂️` is fixed for the life of the artifact; omit it on redeploys.

## Sections (top to bottom)

1. **Header.** Riverside logo (base64, inverted on dark), "Hanan's chief of staff", the date,
   `REFRESHED_AT`, and one **source chip per source** (Slack, Gmail, Calendar, Granola, Monday,
   Nir's ledgers): green "read" or red "not read: <reason>". A source not read is said, never hidden.
2. **Snapshot.** One status strip, not five tiles: five segments reading as a sentence
   ("11 actions today · 2 waiting on my reply · ..."), each a button that scrolls to its
   section, red numerals where past-due > 0. Stacks to rows under 640px.
3. **Act today.** Numbered cards from `data/today-actions.md`: title (links to the source),
   clock in red, who is waiting, age chip, the move in a quiet row. A done checkbox per card
   (localStorage; surfaces in "Copy my changes").
4. **Waiting on my reply** and **Waiting on others**, side by side on desktop, stacked on a
   phone. Tables from `data/waiting-on-me.md` and `data/waiting-on-others.md`.
5. **What I owe Nir.** Table baked from Nir's ledger
   (`.claude/skills/growth-marketing-team-tasks/data/mops.md`, Owner = Hanan, Status not Done
   or Watch list). Days past due computed at render time against the viewer's date.
   `1-1 notes` rows render with a teal chip, no due-date ageing.
6. **Boards.** Five collapsible tiles from `data/board-snapshot.md`: My tasks (Owner Hanan),
   Jonathan's P0 to P2, Unowned New Requests (MOPs P1 and P2 with no owner), Website Dev, and
   mvpGrow. Each row: task (linked to the real pulse),
   status, priority chip, ETA with days late. The tile header carries the `as-of` stamp and
   the `source` line verbatim, so a snapshot never passes as a live read.
7. **Tomorrow, prep.** Rows from `data/meetings.md`.
8. **1-1 pack.** Collapsible, the draft message text from `data/1-1-packs/<date>-jonathan.md`,
   with a "not sent" label. The pack is approved in chat, never on the page.
9. **Footer.** Sync bar ("N changes not yet in the ledger", **Copy my changes** producing a
   text block with `SYNC_TOKEN`), theme toggle, and the AI diligence line.

## Build

```bash
python3 .claude/skills/hanan-chief-of-staff/scripts/build_dashboard.py
```

Parses every `data/*.md` table plus Nir's MOPs ledger (path in SKILL.md, Step 1.E), serialises them as one `DATA` object
between the `/*DATA-START*/` and `/*DATA-END*/` markers in `assets/dashboard.html`, stamps
`REFRESHED_AT` from the system clock (`TZ=Asia/Jerusalem`), bumps `DATA_VERSION` only when the
baked data changed, and runs a JavaScriptCore syntax check on the whole script block
(`osascript -l JavaScript`; node is not installed on this Mac). Refuses to write on a parse
error. `--check` exits 1 if a rebuild would change the data (CI-style drift check).

## Live refresh: what the Refresh button actually does (2026-09-23, widened 2026-09-27)

The page was a pure snapshot, so a refresh changed nothing. On 2026-09-23 the boards went
live, but they sit far down the page, so on 2026-09-27 Hanan pressed Refresh again and saw
the same 23 Sep header and actions: the fix had worked and was invisible. Rule: **a refresh
must change something visible near the top.** The Refresh button now re-reads everything the
page can read on its own, with the viewer's credentials, and toasts a one-line summary.

| Section | Connector and tool | What Refresh does |
|---------|--------------------|-------------------|
| Boards | `monday.com` / `get_board_items_page` | The brief's four board reads (Hanan-owned MOPs, MOPs P0 to P2, Website Dev active groups, mvpGrow), replacing the baked snapshot |
| Today and tomorrow | `Google Calendar` / `list_events` | Meetings with at least one other person, not declined, focus and nudge blocks dropped; prep notes matched from the brief by title; "not answered" chip on pending invites |
| New since the brief | `Slack` / `slack_search_public_and_private`, `Gmail` / `search_threads` | Mentions, DMs and email that arrived after the brief was built; bots, Hanan's own messages, calendar mail and notifications dropped |
| Reply check on rows | `Slack` / `slack_read_thread`, `slack_read_channel` | For every action and waiting-on-me row with a Slack link: a "you replied" chip when Hanan posted there after the brief |

- **The cut-off is the brief's own stamp**, `<!-- built: ... -->` in `data/today-actions.md`,
  baked as `DATA.builtAt`. Never `REFRESHED_AT`: that moves on every rebuild, including a
  design-only one, and would hide what arrived in between. The run writes `built` with the
  time the sources were read.
- **What stays a brief run.** The action list, its moves, waiting lanes and the pack need
  judgment (thread checks, Granola, lanes). When the brief's date is not today, the amber line
  under the date says how old it is and to ask Claude for "my brief".
- **Publish with the full declaration** on every republish, or omit `capabilities` to keep it:
  `{mcp: {servers: [{server: "monday.com", tools: ["get_board_items_page"]}, {server: "Google Calendar", tools: ["list_events"]}, {server: "Slack", tools: ["slack_search_public_and_private", "slack_read_thread", "slack_read_channel"]}, {server: "Gmail", tools: ["search_threads"]}]}}`.
  All read tools. The first open asks the viewer once per connector; the page renders without
  them and lights each section up as it is allowed. The declaration keeps the artifact internal.
- **Errors branch by code and connector** (reconnect, add, not allowed for this page, policy,
  unavailable), one retry only on retryable errors, per-section notes, and a chip per source in
  the "Live check" line under the date.
- **Test against a mock before publishing.** The published frame is cross-origin to the
  session. Serve the page with the `cos-dashboard` preview entry and inject a mock
  `window.claude.use("mcp")` that returns payloads in the connectors' observed shapes (Slack
  returns markdown text inside `results` or `messages`; Gmail and Calendar return JSON). Delete
  the mock copy before committing.

## Design decisions from the Impeccable polish pass (2026-09-16)

Applied with the `impeccable` skill's craft floor and Operate-mode depth (on branch
`claude/impeccable-repo-72a6f1`; its launcher was not run, the playbooks were read directly).
Keep these on any rebuild; they are the difference between a page that was built and one
that was assembled:

- **Operate mode.** One family (Instrument Sans), a fixed rem-ish role scale in `--t-*`
  tokens (12 / 13 / 15 / 16 / 20 / 24), motion only for state (150 to 250 ms), density allowed.
- **No eyebrow labels.** "First move" is a run-in bold lead on a hairline-ruled paragraph, not
  an uppercase kicker over a box. The heading carries its own weight.
- **No hero-metric tiles.** The snapshot is a status strip (number + phrase per segment).
- **No colored left borders above 1px** on callouts. The Move line sits under a hairline; the
  board Source note is plain muted text with a run-in label.
- **Icons are SVG**, one stroke weight (1.75), via the `ICON` map. Never a Unicode glyph or
  emoji standing in for an icon.
- **Accent text has its own tokens.** `--accent-text` (`#A99AFF` on dark, `#5B3FE0` on light)
  is what links, card numbers and run-in labels use; `--accent` stays for fills and borders.
  Riverside purple on Near Black is 4.4:1, under the 4.5:1 body floor.
- **Browser surfaces are themed:** selection, scrollbar, caret, focus ring, underline offset,
  tabular numerals.
- **Headers use the team's words**, not abbreviations ("Waiting", "Priority"; "ETA" is the
  team's own term).
- **The template carries its own charset and viewport meta** so the local preview renders
  the same as the published frame.

## Layout: a fixed shell, not a sticky bar (2026-09-16)

The artifact iframe is scrolled by the host, so `position: sticky` on the top bar never
pinned. The page is an app shell instead: `html, body { height: 100%; overflow: hidden }`,
the bar outside a dedicated `.scroll` container that does the scrolling. The scroll-spy,
jump links and back-to-top all target that container. Keep it that way; a sticky bar inside
the document will look right in a local preview and fail in the published frame.

**Verify the page in a local preview, not in the published frame.** The published iframe is
cross-origin, so `javascript_tool` cannot reach its DOM. `.claude/launch.json` has a
`cos-dashboard` entry that serves `assets/` on port 8766: `preview_start` it, open
`/dashboard.html`, and inspect the real DOM there before publishing.

## Rules inherited from Nir's dashboard (all verified there, all apply here)

- `REFRESHED_AT` comes from the system clock, never an estimate.
- `window.confirm()` / `alert()` / `prompt()` are blocked in the artifact iframe; never gate an
  action on them. Two-click arm/confirm on the button itself.
- Browser edits live in the viewer's `localStorage` inside the sandboxed frame; the run cannot
  read them. The paste of "Copy my changes" is the primary channel back. When a paste carries
  `SYNC_TOKEN: N`, set `ACK_TOKEN = max(old, N)` in the asset, bump `DATA_VERSION`, republish;
  the page then drops exactly the items stamped `<= ACK_TOKEN`.
- A `DATA_VERSION` bump must not wipe unsynced edits: the page reconciles field by field and
  keeps anything that still differs from the baked value.
- No `nowrap` on card titles (a grid item will not shrink below its content width).
- Publishing is one call to the canonical URL. Do not screenshot the published page from a
  background tab; the frame does not paint there.

## Branding

Tokens from `riverside-brand-guidelines`: Near Black `#0F0F14` ground, Dark Gray `#1C1C24`
surface, Mid Gray `#2A2A35` lines, White / Light Gray `#E6E6EB` text, Riverside Purple
`#7C5CFF` accent (hover `#8F73FF`), Purple Mist `#F7F5FF` light ground. Semantic: red
`#E5484D` overdue and blocked, amber `#F5A623` due soon, green `#3DBE7A` done. Instrument
Sans via Google Fonts with a system fallback. Purple is an accent, never a fill; body text is
never small purple. Dark is the default look; the light theme is the Spotlight inversion.
