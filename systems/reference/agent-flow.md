<!-- last-reviewed: 2026-07-14 -->
# Agent Flow

> Real-time visualizer for Claude Code (and Codex) agent orchestration. Renders a live session as an interactive node graph so you can watch tool calls, subagent spawns, branching, and returns as they happen. Third-party open source (Apache 2.0), run locally, opt-in. We consume it, we do not own it.

## Overview

Claude Code normally shows you the result, not the path it took. Agent Flow makes the path visible: it taps the event streams the runtime emits and draws them as a graph, with a timeline, a file-attention heatmap, and a message transcript. It is useful for debugging tool-call chains, spotting slow or redundant work, and building prompt intuition.

It is a developer and observability tool, not a marketing system. It is optional. Any teammate who works in Claude Code can run it; nothing in the Marketing OS depends on it.

Repo: https://github.com/patoles/agent-flow (Simon Patole, for CraftMyGame). Local clone on Hanan's machine: `~/agent-flow`.

## How Claude Works With This

| Action | How |
|--------|-----|
| Watch a session | Open the web app at `http://localhost:3000` while the relay runs |
| Capture events | Claude Code fires hooks, the installed forwarder POSTs them to the local relay, the relay pushes to the browser over SSE |
| Make changes to Agent Flow | We don't. It is third-party. File issues or PRs upstream |
| Change what we capture | Set the relay workspace (see Running It). The relay only sees sessions inside its workspace |

## What the Team Owns

- Our local install and config only: the clone at `~/agent-flow`, the hook forwarder, and the hook entries in `~/.claude/settings.json`.
- A local cosmetic re-skin on the `riverside-theme` branch of the clone (see Local Riverside Theme below). This is a local customization, not an upstream contribution.
- A local UX layer on the `riverside-ux` branch (off `riverside-theme`), adding a keyboard-shortcuts overlay and control discoverability (see Local UX Layer below). Also local-only, also not upstream.

## What the Team Does NOT Own

- The Agent Flow code, the VS Code extension, the relay, and the npx binary. All upstream.

## How It Is Wired

The data path for the from-source dev setup:

1. Claude Code fires a hook on session and tool events.
2. The hook runs `~/.claude/agent-flow/hook.js`, a local-only forwarder installed by setup.
3. The forwarder reads discovery files in `~/.claude/agent-flow/*.json`, each written by a running relay with its `{port, pid, workspace}`.
4. It matches the session's `cwd` against each relay's `workspace` and POSTs the event to the matching relay's hook port (a random local port).
5. The relay transforms the raw hook payload into its event format and broadcasts over SSE on `http://127.0.0.1:3001/events`.
6. The web app on `:3000` subscribes to that SSE stream and renders the graph.

**Key behavior to remember: the relay only forwards events for Claude Code sessions whose `cwd` is inside the relay's workspace.** That is the single most non-obvious thing about it. If you do not see your session, the relay's workspace does not cover your session's directory.

## Setup (reproducible from scratch)

Prerequisites: Node 20+ (Hanan's machine ran Node 26), and pnpm.

1. Install pnpm. Homebrew's Node ships without corepack, so `corepack enable` does not work here. Use npm instead:
   `npm install -g pnpm`
2. Clone the repo:
   `git clone https://github.com/patoles/agent-flow.git ~/agent-flow`
3. Acknowledge the native build scripts. pnpm 11 blocks unapproved native builds (esbuild, sharp) and, worse, its pre-run deps check exits non-zero while they are unacknowledged, which blocks every `pnpm run`. In `~/agent-flow/pnpm-workspace.yaml`, set the placeholder `allowBuilds` values to real booleans:
   ```yaml
   allowBuilds:
     esbuild: false
     sharp: false
   ```
   `false` acknowledges the decision without running the build scripts. esbuild works without its build (its binary ships via an optional dependency), and sharp degrades gracefully in Next.js dev.
4. Install dependencies:
   `cd ~/agent-flow && pnpm i`
5. Back up your Claude settings, then configure hooks:
   `cp ~/.claude/settings.json ~/.claude/settings.json.bak-agentflow`
   `node scripts/setup.js`
   Run the script directly with node. `pnpm run setup` fails on the same pre-run deps check described above. The setup script is dependency-free.

## Running It

The dev server is two processes: a relay and the Next.js web app.

- **Documented path (watches only `~/agent-flow`):**
  `cd ~/agent-flow && pnpm run dev`
  Web on `:3000`, relay on `:3001`. The relay workspace defaults to the launch directory, so you only see sessions run from inside `~/agent-flow`.

- **Watch every session under your home directory:** build the relay first, then run it with an explicit workspace and the web app separately:
  ```bash
  cd ~/agent-flow
  node scripts/build-relay.js          # generates scripts/.dev-relay.js - required before first run and after pulling
  node scripts/.dev-relay.js "$HOME" &
  NEXT_PUBLIC_DEMO=0 NEXT_PUBLIC_RELAY_PORT=3001 pnpm run dev:web &
  ```
  This is the setup Hanan is running. With workspace `$HOME`, all home-rooted Claude Code sessions forward to the local relay. `scripts/.dev-relay.js` is a build artifact (not committed); `node scripts/build-relay.js` regenerates it. If you see "Cannot find module '.dev-relay.js'", you skipped the build step.

- **Demo mode (mock data, no hooks, no config changes):**
  `pnpm run dev:demo`
  With the Riverside UX layer applied, the demo scenario loops continuously by default (showcase/kiosk mode) - toggle with `L` or the `⋮` menu → Loop demo.

Logs: `~/agent-flow/.relay.log` and `~/agent-flow/.web.log`.

Stop it (manual run only): `pkill -f 'dev-relay.js'; pkill -f 'next dev'`. If the launchd keep-alive below is installed, `pkill` does nothing lasting - launchd restarts the process within seconds. Stop via `launchctl bootout` instead.

## Keeping It Always On (launchd)

Since 2026-07-07, Hanan's machine runs both processes as macOS LaunchAgents so `http://localhost:3000` survives reboots, logouts, and crashes. Two plists in `~/Library/LaunchAgents/`:

| Plist | Runs | Key settings |
|-------|------|--------------|
| `com.riverside.agentflow.relay.plist` | `/opt/homebrew/bin/node ~/agent-flow/scripts/.dev-relay.js $HOME` | `RunAtLoad` + `KeepAlive`, logs to `.relay.log` |
| `com.riverside.agentflow.web.plist` | `/opt/homebrew/bin/pnpm run dev:web` in `~/agent-flow` | Same, plus `NEXT_PUBLIC_DEMO=0` and `NEXT_PUBLIC_RELAY_PORT=3001`; logs to `.web.log` |

Both set an explicit `PATH` (`/opt/homebrew/bin:...`) because launchd does not inherit a shell profile - without it, pnpm cannot find node.

Operate them:

```bash
# status (PID column non-dash = running, second column 0 = healthy)
launchctl list | grep agentflow

# stop / start / restart one service
launchctl bootout gui/$(id -u)/com.riverside.agentflow.web
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.riverside.agentflow.web.plist
launchctl kickstart -k gui/$(id -u)/com.riverside.agentflow.relay

# uninstall the keep-alive entirely
launchctl bootout gui/$(id -u)/com.riverside.agentflow.relay
launchctl bootout gui/$(id -u)/com.riverside.agentflow.web
rm ~/Library/LaunchAgents/com.riverside.agentflow.*.plist
```

Gotchas specific to this setup:

- **`KeepAlive` means `pkill` is not a stop button.** launchd restarts killed processes in seconds (verified). Use `bootout` to actually stop.
- **After `git pull` in `~/agent-flow`**, rebuild the relay artifact (`node scripts/build-relay.js`) then `launchctl kickstart -k` both services - launchd keeps running the old code otherwise.
- **The web service runs `next dev`, not a production build.** Fine for a local observability tool; if it ever feels slow or leaky, the fix is `next build` + `next start` in the plist, not more restarts.
- **Don't also start `pnpm run dev` manually** while the agents are loaded - the second web process fights over port 3000 and `.next/dev/lock`.

## What Setup Changes On Your Machine

| Change | Location | Scope | Undo |
|--------|----------|-------|------|
| Hook forwarder script | `~/.claude/agent-flow/hook.js` | Global | `rm -rf ~/.claude/agent-flow` |
| 9 hook entries (`SessionStart`, `PreToolUse`, `PostToolUse`, `PostToolUseFailure`, `SubagentStart`, `SubagentStop`, `Notification`, `Stop`, `SessionEnd`) | `~/.claude/settings.json` | Global | Restore the backup |
| pnpm | global npm packages | Global | `npm rm -g pnpm` |
| `allowBuilds` booleans | `~/agent-flow/pnpm-workspace.yaml` | Local clone | n/a |

The hook merge is non-destructive: setup filters out only prior Agent Flow entries before appending, so existing hooks are preserved. The hook fires on every Claude Code session globally, but when no relay is running it reads an empty discovery dir and exits in milliseconds.

Uninstall the hooks entirely:
`cp ~/.claude/settings.json.bak-agentflow ~/.claude/settings.json && rm -rf ~/.claude/agent-flow`

## Local Riverside Theme

A local cosmetic re-skin lives on the `riverside-theme` branch of the clone. It swaps Agent Flow's default cyan "holographic" identity for exact Riverside Design System tokens (see `references/design-system/` in this repo): primary.c600 (`#9671ff`) accent on a secondary.c1000 (`#151515`) canvas, secondary.c800 (`#222222`) surfaces, secondary.c100 (`#fafafa`) text, Instrument Sans (the single design-system typeface), and a "Riverside Agent Flow" title. Transparent purple washes use `rgba(120, 72, 255, x)`, the design system's c800-based transparent p-layer base. Functional state colors stay visually distinct (the graph needs distinguishable categories) but sit on the design-system status ramps since 2026-07-11: tool call status_warning.c700 (`#f2c94c`), complete status_success.c600 (`#6fcf97`), error status_error.c600 (`#f25757`), live/red status_error.c700 (`#e04040`). Before that alignment the theme used an approximated palette (`#7C5CFF` purple, `#0F0F14` canvas, Inter) that predated the design-system extraction.

> **The `riverside-theme` branch exists only on Hanan's local clone - it was never pushed upstream (it is internal, and `patoles/agent-flow` is third-party).** A teammate cloning fresh from GitHub will not have it, so `git checkout riverside-theme` fails for them. The branch is not recoverable from the public repo; recreate it from the spec below.

It is a palette and font change only. No rendering logic is touched. Nearly the whole palette is centralized in one file, so the diff is small.

| Aspect | Detail |
|--------|--------|
| Branch | `riverside-theme` (off `main`, **local-only on Hanan's clone - never pushed**) |
| Files changed | `web/lib/colors.ts` (core palette), `web/app/globals.css` (Instrument Sans font + brand `.dark` vars + glass-card), `web/app/layout.tsx` (bg + title + `suppressHydrationWarning` on `<body>` to silence the browser-extension hydration mismatch), plus two stray literals in `web/components/agent-visualizer/index.tsx` and `file-attention-panel.tsx` |
| Apply (if you already have the branch) | `cd ~/agent-flow && git checkout riverside-theme`, then run the dev server as usual |
| Get it on a fresh clone | The branch is not on GitHub - apply the checked-in patch (see Rebuilding the Theme below) |
| Revert to upstream look | `git checkout main` |
| Pull upstream updates | Pull on `main`, then `git rebase main` on `riverside-theme` (expect occasional conflicts in `colors.ts`) |

Keep the theme on its own branch so `main` stays clean for upstream `git pull`s. Do not push it upstream; it is internal.

### Rebuilding the Theme (fresh clone, branch not present)

The branch lives only on Hanan's machine and was never pushed (upstream is public third-party - internal branding must not go there). So instead of pushing the branch, the full theme is checked into this repo as a patch: [`assets/agent-flow-riverside-theme.patch`](assets/agent-flow-riverside-theme.patch) (details in [`assets/agent-flow-riverside-theme.patch.md`](assets/agent-flow-riverside-theme.patch.md)). It captures all three theme commits (initial re-skin, text-legibility refinements, design-system token alignment), scoped to the five theme files only (it excludes the local `pnpm-workspace.yaml` setup change).

Recreate the branch on a fresh clone:

```bash
# point this at your local marketing-brain checkout (the patch lives in that repo, not in ~/agent-flow)
BRAIN=~/marketing-brain
cd ~/agent-flow
git checkout main
git checkout -b riverside-theme
git apply "$BRAIN/systems/reference/assets/agent-flow-riverside-theme.patch"
git commit -am "Apply Riverside brand theme to Agent Flow visualizer"
```

Then run the dev server as usual. Verified to apply cleanly against upstream `main` on 2026-07-11. No rendering logic changes; it is a palette and font swap only. The functional state colors stay categorically distinct but use the design-system status ramps. If the theme changes again, regenerate the patch per the instructions in the `.patch.md` file.

## Local UX Layer

A second local branch, `riverside-ux` (branched off `riverside-theme`), adds functional UI/UX on top of the cosmetic re-skin. Unlike the theme, this touches component behavior, so it is kept on its own branch to keep `riverside-theme` a clean palette-and-font swap.

What it adds (mostly chrome; the only canvas-rendering touches are the brand watermark and the per-agent model line below):

| Change | Detail |
|--------|--------|
| Keyboard-shortcuts overlay | New `web/components/agent-visualizer/shortcuts-overlay.tsx`. Centered glass-card modal listing every shortcut (Playback / Panels / View / Selection) with kbd-style chips. Toggled with `?` or a new top-bar help button; closes on `?`, `Esc`, backdrop click, or close button. While open it is modal: all other shortcuts are gated so they can't mutate state behind it. The app previously surfaced none of its 12+ shortcuts. |
| Top-bar discoverability | `top-bar.tsx`: `title` tooltips with key hints on every control, a `?` help button, and affordance polish (cursor, hover, wider hit area). |
| Top-bar segmented groups | `top-bar.tsx`: the bar reorganized into four segmented groups with one container and one 22px button style - read-only stats (connection, agents menu, tokens ~cost with thin rules), panels (Files, Chat, $ Cost, Timeline), view modes (Director, Fleet), meta icons (mute, ?). Session tabs on the left share the group container and shrink with internal scroll so many tabs can't push the controls off screen. |
| Bottom-bar icon menu | `control-bar.tsx`: a `⋮` button at the right end of the control bar opens a glass-card popover with three view controls - Grid (G), Stats (S), Zoom fit (Shift+F) - each with its SVG icon, label, and keyboard hint. Active state reflects current canvas state. Available in both live and review modes. |
| Riverside brand mark | `background-layer.ts`: full Riverside logo + wordmark drawn as Path2D at 7% white opacity, centered in the canvas viewport, painted right after the void fill so it sits behind the graph nodes, particles, and grid (moved from a bottom-left DOM overlay in `index.tsx` on 2026-07-07). |
| Riverside favicon | `web/public/icon.svg`: replaces Agent Flow's default favicon with the Riverside logo mark (white mark on Riverside-purple). |
| View-preference persistence | New `web/hooks/use-persistent-toggle.ts`: grid, stats, cost, timeline, files, and transcript toggles persist to localStorage (`agent-flow.view.*`) and sync across open tabs via storage events. Wired into `index.tsx`. |
| Scrubber event tooltips | `control-bar.tsx`: the event dots on the bottom scrubber get a wider invisible hit area and a glass-card hover tooltip showing the event's state color, label, and timestamp. Works in both live and review modes; seeking over a dot still works. |
| Session tab tooltips | `session-tabs.tsx`: hovering a session tab shows the label plus status (Active/Completed) and start time. Labels are truncated to 14 chars by the relay before reaching the browser, so the full prompt is not available without an upstream relay change. |
| Keyboard agent cycling | `use-keyboard-shortcuts.ts` + `index.tsx`: Left/Right arrows cycle selection through agents, opening the detail card and chat panel. Listed in the shortcuts overlay. |
| Agent roster menu | `top-bar.tsx`: the "N agents" label opens a live roster of the session's agents (state dot, name, MAIN badge, current tool or state, model, tokens). Clicking a row selects that agent, same as arrow cycling. |
| Timeline drill-down Gantt | `timeline-panel.tsx`: the timeline panel redesigned as an interactive Gantt - fat lanes with tool icons and a per-lane time-split bar; clicking a lane drills into that agent's log grouped into per-tool runs, led by an Outcomes digest; level-of-detail rendering keeps long sessions readable. |
| Director mode (camera follows the action) | New `canvas/camera-director.ts` + `use-canvas-camera.ts`: toggled with `D`, the top-bar Director chip, or the `⋮` icon menu, the camera flies to the highest-priority live event (needs-input > error > fresh subagent spawn > running tool > thinking) with dwell hysteresis, a clamped focus zoom, and a slower cinematic lerp. Manual pan/zoom suspends it; re-toggling or Zoom fit re-engages. Falls back to auto-fit when nothing qualifies. Persisted like other view prefs. |
| Event pings | `detect-state-changes.ts` + `draw-effects.ts`: a short expanding ring marks each tool start (amber, ~350ms) and tool error (red, larger, echoed on the owning agent), so discrete events read as staged signals per the animation-perception guidance. |
| History trails | `canvas.tsx` + `draw-edges.ts` + `draw-agents.ts`: recently trafficked edges stay warm and recently active nodes keep a residual glow, both decaying over 30s - a glance (or a PNG export) shows where the work just happened. Render-side only. |
| Calm at rest | `canvas.tsx` + `background-layer.ts` + `draw-agents.ts`: background depth-particle drift slows to 30% when no agent is active, and settled (idle/complete) nodes drop their scanline, so remaining motion means state change. |
| Agent-node shape | `canvas/draw-misc.ts` + `draw-agents.ts` + `draw-effects.ts` + `background-layer.ts`: agent nodes go from a sharp hexagon to a soft-cornered (rounded) hexagon, and the faint background honeycomb becomes a rounded-square grid. All node layers route through one `drawNodeShape` (replacing `drawHexagon`) so shadow, glow, fill, scanline clip, state ring, and spawn ripple restyle together; sizing unchanged. Rounded-square nodes and a rounded-hex grid were the two other picks previewed. |
| Fleet attention reasons | `use-fleet-stats.ts` + `fleet-view.tsx`: NEEDS INPUT cards say what the session is blocked on (the permission notification text) and ERROR cards carry the failing tool and message, on the card and in its tooltip - encoding the needed information directly in the alert. |
| Demo permission beat | `mock-scenario.ts`: the demo scenario gains a 3s permission gate before the final Bash type-check, so the waiting state (amber lock, ripples, director fly-to) is demoable end-to-end. |
| Demo showcase loop | `use-agent-simulation.ts` + `simulation/types.ts` + `index.tsx` + `control-bar.tsx` + `use-keyboard-shortcuts.ts` + `shortcuts-overlay.tsx` + `canvas.tsx`: in demo mode the mock scenario replays continuously - when it plays out (last event + the 8s end buffer), the simulation restarts from a clean slate instead of stopping, so the demo playground runs hands-off (kiosk/showcase screens). Toggled with `L` or the `⋮` menu → Loop demo; on by default, persisted like other view prefs (`agent-flow.view.demoLoop`); the menu item and shortcut are inert in live mode. Toggling it off restores upstream play-once-then-stop. A sim-clock rewind (loop restart, manual restart, backward seek) also clears the canvas-local history caches (edge warmth, agent heat, prev-state maps) so each replay starts visually clean. |
| Auto-highlight video export | New `web/hooks/use-highlight-export.ts` (`R` or the `⋮` menu): scores timeline events (errors loudest), picks the most eventful 12s window, replays it in review mode with the director driving while recording the canvas (MediaRecorder + captureStream), downloads `agent-flow-highlight.webm` (`.mp4` on Safari, which cannot record WebM), and restores the prior playback state. The menu entry hides when MediaRecorder is unsupported. A DOM banner marks recording without appearing in the frames. Grounded in the demo research: 10-15s clips, wow moment first. |
| Session poster export | New `web/components/agent-visualizer/poster-export.ts` (`⋮` menu → Save poster): a 3200x1800 PNG share card - Riverside-styled stats column (duration, agents, tools, errors, tokens, est. cost, model chips, logo mark) beside a cover-fit snapshot of the live canvas with trails and watermark. |
| Relay-disconnect banner | New `reconnect-banner.tsx`: top-center "RELAY DISCONNECTED" banner when the SSE connection drops for 3s+ in web live mode. The web app previously had no disconnect signal (the top-bar indicator renders only inside VS Code). |
| Interactive cost panel | New `cost-panel.tsx` (+ `canvas.tsx`): the cost toggle opens a sortable per-agent DOM table with share bars and by-tool breakdown, replacing the canvas-drawn summary HUD. Per-node floating cost pills remain canvas-drawn. |
| Export actions | `control-bar.tsx`: the `⋮` icon menu gains copy-markdown-session-summary and save-canvas-PNG export items. |
| Fleet view | New `fleet-view.tsx` + `web/hooks/use-fleet-stats.ts`: a mission-control overlay (toggled with `V` or a top-bar Fleet button) showing every session as a card - status badge (NEEDS INPUT / ERROR / STALLED / RUNNING / DONE), schematic mini graph of the session's agents colored by live state, tool/error/token/cost stats, model chip, and last-activity age. Cards are attention-sorted (waiting for input first, then errored, stalled, running, done); the order freezes while the overlay is open so the `1`-`9` jump-to-session hotkeys always match what's on screen, while badges and stats keep updating live. Click a card or press its digit to switch to that session and zoom to fit. Stats come from a 1Hz incremental reduction over the bridge's per-session event buffers (`getSessionEvents`, a new bridge accessor) - the physics simulation still only runs for the selected session. A session with no events for 2+ minutes while active is flagged STALLED (the initial historical buffer doesn't count as fresh activity, so already-idle sessions read STALLED right after page load). The top-bar Fleet button shows a pulsing count of sessions needing attention (waiting/errored). Known limitation: stats are built from events received since the page loaded - after a browser reload, background sessions show sparse cards until they emit again (the relay does not replay history). Web-only; no relay changes. |
| Per-agent model visibility | Every agent shows which model it runs on, live. Canvas: model line under the node name (`canvas/draw-agents.ts`, context bar moved down to make room). Detail card: model chip next to the agent name (`agent-detail-card.tsx`). Cost panel: model label per agent row (`cost-panel.tsx`). Backed by a parser change (`extension/src/transcript-parser.ts` + `protocol.ts` + `session-watcher.ts` + `scripts/relay.ts`): `model_detected` was once-per-session, now tracked per agent and re-emitted on change, so subagents report their own model and mid-session `/model` switches update live. `formatModelName` in `web/lib/utils.ts` compacts IDs ("claude-opus-4-8-20260115" → "Opus 4.8"). **Parser changes require `node scripts/build-relay.js` + relay restart to take effect.** |
| Design-system literal sweep | `icon.svg`, `cost-panel.tsx`, `control-bar.tsx`, `canvas-constants.ts`: the UX layer's few hardcoded colors aligned to the same design-system tokens as the theme (2026-07-11). |
| Disable dev indicator | `next.config.mjs`: `devIndicators: false` removes the floating "N" build-status button from the dev server. |
| Wiring | `use-keyboard-shortcuts.ts` and `index.tsx`: `?` / `Esc` handling, overlay state, and control-bar icon menu props. |
| Demo-coexistence fix | `next.config.mjs` builds demo mode into `.next-demo` instead of `.next` (plus `tsconfig.json` includes and a `.gitignore` entry), so a `dev:demo` server can run alongside a live `dev:web` without fighting over `.next/dev/lock`. Dev-workflow convenience, not UI. |

> **Like `riverside-theme`, the `riverside-ux` branch exists only on Hanan's local clone - never pushed upstream.** A fresh clone will not have it. The full layer is checked into this repo as a patch: [`assets/agent-flow-riverside-ux.patch`](assets/agent-flow-riverside-ux.patch) (details in [`assets/agent-flow-riverside-ux.patch.md`](assets/agent-flow-riverside-ux.patch.md)). It is layered: apply the theme patch first, then the UX patch. Verified on 2026-07-11 to apply cleanly on top of `riverside-theme` and to reproduce the `riverside-ux` branch tree (patch regenerated after the per-agent model visibility and design-system alignment work).

To preview the UI with mock data while a live session keeps running, start the demo server (`pnpm run dev:demo`) - the `.next-demo` distDir lets it coexist with your live `:3000` instance on an auto-assigned port.

## Privacy

- The from-source `pnpm run dev` path and the VS Code extension send no telemetry.
- The published `npx agent-flow-app` binary ships opt-out anonymous telemetry (aggregate counts only, never prompts, paths, or tool calls). Disable with `AGENT_FLOW_TELEMETRY=false` or `DO_NOT_TRACK=1`.

## Gotchas

- **The relay workspace gates everything.** No events usually means the relay workspace does not cover your session's `cwd`.
- **pnpm 11 pre-run deps check.** Unacknowledged native builds make `pnpm run anything` exit non-zero. Fix it once via `allowBuilds` in `pnpm-workspace.yaml` (see Setup step 3). For one-off scripts, run them directly with node to bypass the check.
- **No corepack in Homebrew Node.** Install pnpm with `npm install -g pnpm`.
- **Running from source executes third-party code** (install, build, hook setup, dev server). This is fine for an Apache-2.0 project you trust, but the global hook write into `~/.claude/settings.json` is a deliberate, persistent change. Back up first.
- **Hydration mismatch on `<body>` (browser-extension attributes).** A Next.js console error - *"A tree hydrated but some attributes of the server rendered HTML didn't match the client properties"* - pointing at `web/app/layout.tsx`'s `<body>`, with the diffed attributes being `data-new-gr-c-s-check-loaded` and `data-gr-ext-installed`, is **benign**: those attributes are injected by the **Grammarly** browser extension after SSR but before React hydrates. It is a browser-only warning, not an Agent Flow bug, and nothing is left unpatched at runtime. The `riverside-theme` patch already handles it - it renders `<body className="font-sans antialiased bg-[#151515]" suppressHydrationWarning>` (see the `layout.tsx` hunk in `assets/agent-flow-riverside-theme.patch`). If you still hit the error, your local `layout.tsx` has drifted and lost the `suppressHydrationWarning` attribute - most likely an upstream Next.js bump (16.1.6+) rewrote `layout.tsx` and a rebase kept the themed `bg-[#151515]` line but dropped the suppress attribute. Fix: re-add `suppressHydrationWarning` to the `<body>` tag in `web/app/layout.tsx` (Fast Refresh picks it up under `next dev`; no restart needed), or re-apply the theme patch per **Rebuilding the Theme**. If `layout.tsx` drifted, regenerate the patch afterward (per `assets/agent-flow-riverside-theme.patch.md`) so it keeps applying cleanly on the current Next.js.

## Pointers

- **Owned alternative:** `tools/session-flow.html` (see `systems/owned/session-flow.md`) - our repo-owned visualizer. No relay/hooks/install: it loads session files post-hoc from anywhere, live-tails a local Claude Code transcript via the File System Access API (Chromium), and also renders ChatGPT and Claude.ai exports, which Agent Flow cannot.
- **Investment:** Reference only. Optional local tool. We consume, we do not contribute.
- **Repo:** https://github.com/patoles/agent-flow (Apache 2.0)
- **Demo:** https://www.youtube.com/watch?v=Ud6eDrFN-TA
- **Local clone:** `~/agent-flow`
- **Settings backup created during setup:** `~/.claude/settings.json.bak-agentflow`
