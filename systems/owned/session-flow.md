<!-- last-reviewed: 2026-07-21 -->
# Session Flow

> Riverside-branded visualizer for LLM sessions - Claude Code, ChatGPT, and Claude.ai. A single self-contained HTML file: open it in any browser, drop a session file in (or point Live mode at `~/.claude/projects` to watch a running session in real time), and get an animated agent flow graph, a timeline, a synced transcript, and a stats/cost panel. Our owned alternative to the third-party Agent Flow tool (`systems/reference/agent-flow.md`), built because Agent Flow is Claude-only, requires a local relay + hooks install, and cannot render ChatGPT sessions at all.

## Overview

Agent Flow shows a session while it happens, on the one machine that has the relay and hooks installed. Session Flow works from the files the platforms already produce - post-hoc from exports and transcripts anywhere, and live by tailing a local Claude Code transcript as it grows. No install, no relay, no hooks, no settings.json changes, no server - the file is the app.

- **File:** `tools/session-flow.html` (this repo). Open locally or from a checkout; everything runs client-side.
- **Owner:** Marketing Ops (Hanan). Repo-owned, unlike Agent Flow which is third-party.
- **Data never leaves the browser.** No network calls except the Google Fonts stylesheet (falls back to system fonts offline). Sessions are parsed in-memory; nothing is uploaded or stored.

## Supported inputs

| Source | File | Where to get it |
|--------|------|-----------------|
| Claude Code | per-session `.jsonl` transcript | `~/.claude/projects/<project-slug>/<session-id>.jsonl` on any machine that ran the session |
| ChatGPT | `conversations.json` (whole export or a single conversation object) | ChatGPT Settings → Data controls → Export data |
| Claude.ai | `conversations.json` export | Claude.ai Settings → Privacy → Export data |

Load by drag-and-drop, the file picker, or pasting JSON. Multiple files at once are fine; a ChatGPT export becomes one session per conversation (sorted newest first) in the session switcher. Format detection is automatic.

## What it renders

| View | What it shows |
|------|---------------|
| Flow graph | User → main agent → per-tool nodes; subagents (Claude Code `Task` sidechains) as their own lanes with their own tools, labeled from the Task description and showing their own model. Edge thickness = call count, dashed edge = spawn, red = errors. Pan/zoom; click any node to filter the transcript + timeline. |
| Timeline (Gantt) | One lane per actor. Tool calls are duration bars (matched `tool_use` → `tool_result`, or ChatGPT tool round-trips); messages are dots, thinking is a diamond; failures get a red ring + ✕. Wheel-zoom, drag-pan, double-click reset. |
| Transcript | Every event as a card: role, tool chips, model chip, timestamps, durations, collapsible tool input/output, expandable long text, full-text search. Synced both ways with the graph and timeline. |
| Stats & cost | Stat tiles (duration, messages, tool calls + failures, agents, branches, tokens, est. cost, models), tool-usage breakdown with per-tool error counts and total runtime, and a per-agent table (model, events, tools, errors, tokens, cost). |

ChatGPT specifics: the export's `mapping` tree is walked from `current_node`, so regenerated answers are detected as **alternate branches** - hidden by default, toggleable ("alt branches" / `B`), counted in the stats. Tool use (web, python/code interpreter) is reconstructed from `recipient` + `tool` role messages. ChatGPT exports carry no token counts, so tokens/cost show n/a rather than a made-up number.

Cost is an **estimate**: public list prices by Claude model family (Opus/Sonnet/Haiku), with cache reads at 10% and cache writes at 125% of the input rate, computed from the per-message `usage` blocks in Claude Code transcripts.

## Live mode

**Go live** watches a Claude Code session update in real time - no relay, no hooks. It uses the browser's File System Access API: pick `~/.claude/projects` (or a project folder, or a single `.jsonl`), and the page polls the newest transcript every 1.5s, re-parsing and re-rendering as the file grows. With a folder selected it hops to newer session files as they start.

- A pulsing **LIVE** chip shows the watched file and how fresh it is; stop with its × button.
- The currently running tool's node pulses amber; new events fire expanding ping rings and temporarily speed up that edge's particle stream; the timeline gets a moving red "now" line and follows the right edge.
- Your view survives refreshes: pan/zoom on the graph or timeline "pins" it (live updates stop re-fitting), open tool cards stay open, and the transcript follows the bottom only if you were already there. Double-click the timeline or press `F` on the graph to resume following.
- **Chromium-only** (Chrome/Edge/Arc - Firefox/Safari lack the API) and the page must be opened directly in a tab; sandboxed frames (e.g. the hosted artifact copy) block the file picker.
- Live mode reads whatever transcript files your machine has. Remote/cloud Claude Code sessions write their transcript inside the cloud container, not on your laptop - live-watch those from a browser running where the transcript is, or load the file post-hoc.

## Flow animation

The graph is animated so data flow reads at a glance: particles stream along every edge (count scales with call volume), spawn edges march their dashes, and in live mode fresh events ping their nodes (amber for tool starts, red for failures) and heat up their edges for ~8 seconds. Animation fully respects `prefers-reduced-motion` (static rendering) and pauses in hidden tabs.

## Keyboard

`←`/`→` cycle events · `[`/`]` switch sessions · `T` transcript · `S` stats · `F` zoom fit · `B` alt branches · `Esc` clear/close · `?` shortcuts overlay.

## Design system

Exact Riverside Design System tokens (`references/design-system/`): `#151515` canvas, `#222222` surfaces, `#fafafa` text, `#9671ff` primary accent, status ramps for tool/success/error states, Instrument Sans. The categorical actor palette (`#9671ff`, `#0aa4c8`, `#cc6a00`, `#d63ef2`, `#22ab72`) is the brand purple plus darkened steps of the brand's common accent hues, validated against the dark surface with the dataviz six-checks palette validator (lightness band, chroma, CVD separation, normal-vision floor, contrast) - actors are additionally always identified by label, never color alone.

## Demo mode

The **Demo** button loads two embedded sample sessions - a Claude Code run (subagent spawn, a failed-then-retried Bash call, cache-heavy token usage) and a ChatGPT conversation (web + python tool calls and a regenerated branch). The demo Claude session is stored as real JSONL text and run through the real parser, so it doubles as a self-test of the ingestion path.

## Vs. Agent Flow

| | Agent Flow (reference) | Session Flow (owned) |
|--|--|--|
| When | Live, while the session runs | Post-hoc from files, or live by tailing the transcript |
| Live plumbing | Hooks → forwarder → relay → SSE | Browser reads the `.jsonl` directly (File System Access API, Chromium) |
| Sources | Claude Code (+ Codex) | Claude Code (post-hoc + live), ChatGPT, Claude.ai |
| Install | Clone + pnpm + hooks + relay, per machine | None - open one HTML file |
| Ownership | Third-party (we keep a local theme/UX patch) | Ours, in this repo |
| Sharing | Screen only | Send someone the file + a session file |

They complement each other: Agent Flow's event stream still has richer live semantics (per-hook events, permission prompts); Session Flow covers everyone without an install, everything already finished, ChatGPT work, and live local sessions at 1.5s freshness.

## Gotchas

- **Claude Code transcripts only exist on the machine that ran the session.** Cloud/web sessions write `~/.claude/projects/...jsonl` inside their cloud container, not on your laptop - so Live mode covers local CLI/desktop sessions; for remote sessions, obtain the JSONL (or have the remote agent export it) and load it post-hoc.
- **Subagent lanes come from two transcript conventions.** Older Claude Code interleaves subagent traffic in the main `.jsonl` as `isSidechain: true` rows (grouped by walking to the chain root); newer versions write each subagent to a sibling file at `<session-id>/subagents/agent-<id>.jsonl` (rows carry an `agentId`) and spawn via a tool named `Agent` rather than `Task`. Session Flow handles both: Live mode folded over a folder merges the `subagents/` files automatically, and for manual loading you can multi-select the main transcript together with its `agent-*.jsonl` files (they merge into the one session). Lanes are labeled from the spawning Task/Agent call's `description` by matching its prompt to the subagent's first message; unmatched lanes fall back to "Subagent n". A single-file live pick can't see sibling folders, so prefer picking the folder.
- **ChatGPT timestamps can be missing** on some nodes; the parser interpolates a small offset so ordering survives, which means sub-second timing in ChatGPT timelines is approximate.
- **Very large exports:** a full multi-year `conversations.json` parses, but every conversation lands in the session switcher; load time is dominated by `JSON.parse`. If it ever feels slow, split the export or paste a single conversation object.
- **Fonts:** offline or CSP-restricted contexts fall back from Instrument Sans to system fonts by design.

## Pointers

- **File:** `tools/session-flow.html`
- **Agent Flow (third-party live visualizer we consume):** `systems/reference/agent-flow.md`
- **Design tokens used:** `references/design-system/`
