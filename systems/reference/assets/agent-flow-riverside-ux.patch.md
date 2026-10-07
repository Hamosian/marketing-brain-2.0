<!-- last-reviewed: 2026-07-13 -->
# Agent Flow - Riverside UX patch

`agent-flow-riverside-ux.patch` is a checked-in backup of the local-only `riverside-ux` branch of
the [Agent Flow](../agent-flow.md) clone. Like `riverside-theme`, this branch lives only on Hanan's
machine and was never pushed (upstream `patoles/agent-flow` is a public third-party repo; our local
customizations do not go there). This patch is the recovery and sharing path instead.

Unlike the theme patch, this one is **functional, not cosmetic** - it adds UI/UX behavior on top of
the brand re-skin. It is layered: `riverside-ux` is branched off `riverside-theme`, so apply the
theme patch first, then this one.

## What it contains

Thirty-three local commits of UX and branding work. Originally chrome-only; the layer now also
touches canvas rendering (brand watermark, per-agent model line, camera director, event pings,
history trails, calm-at-rest gating, agent-node shape). Across the changed files:

- **Keyboard-shortcuts overlay** (`web/components/agent-visualizer/shortcuts-overlay.tsx`, new) - a
  centered glass-card modal listing every shortcut (Playback / Panels / View / Selection) with
  kbd-style chips. Toggled with `?` or a new top-bar help button; closes on `?`, `Esc`, backdrop
  click, or the close button. The app previously surfaced none of its 12+ shortcuts. While the
  overlay is open it behaves as a modal: `use-keyboard-shortcuts.ts` gates every key except `Esc`
  and `?`, so background shortcuts can't mutate playback, panels, or selection behind it.
- **Top-bar discoverability** (`web/components/agent-visualizer/top-bar.tsx`) - `title` tooltips with
  key hints on every control, a new `?` help button, and affordance polish (cursor, hover, wider hit
  area).
- **Top-bar segmented groups** (`top-bar.tsx`) - the bar reorganized into four segmented groups
  sharing one container and one 22px button style: read-only stats (connection, agents menu,
  tokens ~cost), panels (Files, Chat, $ Cost, Timeline), view modes (Director, Fleet), and meta
  icons (mute, ?). The session-tab strip gets the same container and shrinks with internal scroll,
  so a crowded tab strip can no longer push the right-side controls off screen.
- **Bottom-bar icon menu** (`web/components/agent-visualizer/control-bar.tsx`) - a `⋮` button at the
  right end of the control bar opens a glass-card popover above it with three view controls: Grid
  (G), Stats (S), and Zoom fit (Shift+F). Each item shows its SVG icon, label, and keyboard hint chip.
  Active state is reflected in the menu. Available in both live and review modes.
- **Riverside brand mark** (`web/components/agent-visualizer/background-layer.ts`) - the full
  Riverside logo + wordmark drawn as `Path2D` at 7% white opacity, centered in the canvas viewport
  and painted immediately after the void fill, so it sits behind the graph nodes, particles, and
  hex grid. Originally a bottom-left DOM overlay in `index.tsx`; moved into the canvas background
  on 2026-07-07 because the canvas repaints an opaque background every frame, so a DOM element can
  never render behind the graph.
- **Riverside favicon** (`web/public/icon.svg`) - replaces Agent Flow's default favicon with the
  Riverside logo mark (white mark on Riverside-purple background).
- **Disable Next.js dev indicator** (`web/next.config.mjs`) - `devIndicators: false` removes the
  floating "N" build-status button from the dev server.
- **View-preference persistence** (`web/hooks/use-persistent-toggle.ts`, new) - the six view
  toggles (grid, stats, cost, timeline, files, transcript) persist to localStorage under
  `agent-flow.view.*` and sync across open tabs via storage events. The stored value is read after
  mount so SSR markup and the first client render agree.
- **Scrubber event tooltips** (`web/components/agent-visualizer/control-bar.tsx`) - each event dot
  on the bottom scrubber gets a 10x20px invisible hit area and a glass-card hover tooltip showing
  the event's state color, label, and timestamp. Mousedown still bubbles to the scrubber, so
  seeking over a dot keeps working. Applies to both live and review modes.
- **Session tab tooltips** (`web/components/agent-visualizer/session-tabs.tsx`) - hovering a tab
  shows the session label plus status (Active/Completed) and start time. Note the relay truncates
  labels to 14 chars before broadcast (`SESSION_LABEL_MAX` in the relay), so the full prompt is
  not recoverable in the web app.
- **Keyboard agent cycling** (`web/hooks/use-keyboard-shortcuts.ts`,
  `web/components/agent-visualizer/index.tsx`) - Left/Right arrow keys cycle selection through the
  agents, opening the detail card and chat panel for each. Listed in the shortcuts overlay.
- **Relay-disconnect banner** (`web/components/agent-visualizer/reconnect-banner.tsx`, new) - a
  top-center "RELAY DISCONNECTED" banner when the SSE connection drops for 3s+ in web live mode.
  The web app previously had no disconnect signal at all (the top-bar connection indicator renders
  only inside VS Code).
- **Interactive cost panel** (`web/components/agent-visualizer/cost-panel.tsx`, new;
  `web/components/agent-visualizer/canvas.tsx`) - the cost toggle now opens a sortable per-agent
  DOM table with share bars and a by-tool breakdown, replacing the old canvas-drawn summary HUD
  (`drawCostSummaryPanel`). The floating per-node cost pills remain canvas-drawn.
- **Export actions** (`web/components/agent-visualizer/control-bar.tsx`) - the `⋮` icon menu gains
  two export items: copy a markdown session summary to the clipboard, and save a canvas snapshot
  as PNG.
- **Wiring** (`web/hooks/use-keyboard-shortcuts.ts`, `web/components/agent-visualizer/index.tsx`) -
  `?` / `Esc` handling and overlay state; `showStats`, `showHexGrid`, `onToggleStats`,
  `onToggleGrid`, `onZoomToFit` props wired from `index.tsx` into the control bar.
- **Design-system literal sweep** (`web/public/icon.svg`, `cost-panel.tsx`, `control-bar.tsx`,
  `web/lib/canvas-constants.ts`) - the UX layer's few hardcoded colors aligned to the same
  Riverside Design System tokens as the theme (2026-07-11): favicon background primary.c600,
  cost-panel row surface secondary.c800, live-dot glow and FPS warning status_error.c700.
- **Demo-coexistence fix** (`web/next.config.mjs`, `web/tsconfig.json`, `.gitignore`) - demo mode
  builds into `.next-demo` instead of `.next`, so a `dev:demo` server can run alongside a live
  `dev:web` without fighting over `.next/dev/lock`. This is a dev-workflow convenience, not UI.
- **Fleet view** (`web/components/agent-visualizer/fleet-view.tsx`, new;
  `web/hooks/use-fleet-stats.ts`, new; `index.tsx`, `top-bar.tsx`, `shortcuts-overlay.tsx`,
  `use-keyboard-shortcuts.ts`, `use-vscode-bridge.ts`) - a mission-control overlay (toggle `V` or
  the top-bar Fleet button) showing every session as a card: status badge (NEEDS INPUT / ERROR /
  STALLED / RUNNING / DONE), schematic mini graph of agents colored by live state, tool/error/
  token/cost stats, model chip, last-activity age. Cards sort by attention priority; the order
  freezes while the overlay is open so the `1`-`9` jump hotkeys always match the screen, while
  badges and stats update live at 1Hz. Stats come from an incremental reduction over the bridge's
  per-session event buffers (new `getSessionEvents` accessor) - no extra simulations. Stall
  threshold: 2 minutes of silence on an active session; the initial consumption of a session's
  historical buffer keeps the session's `lastActivityTime` seed rather than counting as fresh
  activity, so an already-idle session reads STALLED immediately after page load. The overlay is
  modal (digits jump, `V`/`Esc` close, other shortcuts gated); the top-bar button shows a pulsing
  needs-attention count. Known limitation: fleet stats are built from events received since the
  page loaded - after a browser reload, background sessions show sparse cards (label/status only)
  until they emit again, because the relay does not replay event history. Web-only, no relay or
  parser changes.
- **Per-agent model visibility** (`extension/src/transcript-parser.ts`, `extension/src/protocol.ts`,
  `extension/src/session-watcher.ts`, `scripts/relay.ts`, `web/lib/agent-types.ts`,
  `web/lib/utils.ts`, `web/lib/canvas-constants.ts`, `web/lib/mock-scenario.ts`,
  `web/hooks/simulation/handle-agent-events.ts`, `web/components/agent-visualizer/canvas/draw-agents.ts`,
  `agent-detail-card.tsx`, `cost-panel.tsx`) - every agent node shows which model it runs on:
  a model line under the node name on canvas, a model chip in the agent detail card, and a model
  label per row in the cost panel. On the parser side, `model_detected` used to fire once per
  session; it is now tracked per agent and re-emitted on change, so subagents report their own
  model and mid-session `/model` switches update live. `formatModelName` compacts raw IDs
  ("claude-opus-4-8-20260115" → "Opus 4.8"). This is the first change that touches the parser and
  relay, so after applying the patch, rebuild the relay artifact (`node scripts/build-relay.js`)
  and restart the relay for the parser side to take effect.

- **Agent roster menu** (`web/components/agent-visualizer/top-bar.tsx`, `index.tsx`) - the top-bar
  "N agents" label opens a live roster (state dot, name, MAIN badge, current tool or state, model,
  tokens); clicking a row selects that agent.
- **Timeline drill-down Gantt** (`web/components/agent-visualizer/timeline-panel.tsx`,
  `web/hooks/simulation/types.ts`) - the timeline panel redesigned as an interactive Gantt: fat
  lanes with tool icons and a time-split bar, click-to-drill into per-tool run groups led by an
  Outcomes digest, with level-of-detail rendering for long sessions.
- **Director follow mode** (`web/components/agent-visualizer/canvas/camera-director.ts`, new;
  `web/hooks/use-canvas-camera.ts`, `canvas.tsx`, `index.tsx`, `top-bar.tsx`, `control-bar.tsx`,
  `shortcuts-overlay.tsx`, `use-keyboard-shortcuts.ts`, `web/lib/canvas-constants.ts`) - toggled
  with `D`, a top-bar Director chip, or the `⋮` menu: the camera flies to the highest-priority
  live event (needs-input > error > fresh spawn > running tool > thinking) with dwell hysteresis,
  clamped focus zoom, and a slower cinematic lerp. Manual navigation suspends it; re-toggling or
  Zoom fit re-engages. Falls back to auto-fit when nothing qualifies.
- **Event pings** (`web/components/agent-visualizer/canvas/detect-state-changes.ts`,
  `draw-effects.ts`) - a short expanding ring on each tool start (amber) and tool error (red,
  larger, echoed on the owning agent).
- **History trails** (`canvas.tsx`, `canvas/draw-edges.ts`, `canvas/draw-agents.ts`) - recently
  trafficked edges stay warm and recently active nodes keep a residual glow, decaying over 30s.
  Render-side maps only; no simulation changes.
- **Calm at rest** (`canvas.tsx`, `canvas/draw-agents.ts`) - depth-particle drift slows to 30%
  when no agent is active; idle/complete nodes drop their scanline.
- **Agent-node shape** (`canvas/draw-misc.ts`, `canvas/draw-agents.ts`, `canvas/draw-effects.ts`,
  `background-layer.ts`) - the agent nodes change from a sharp hexagon to a soft-cornered
  (rounded) hexagon, and the faint background honeycomb grid becomes a rounded-square grid. All
  node layers route through one `drawNodeShape` helper (replacing `drawHexagon`), so the shadow,
  glow, fill, scanline clip, state ring, and spawn ripple restyle together; node sizing is
  unchanged. The background tiler is renamed `drawSquareGrid` and draws rounded squares.
- **Fleet attention reasons** (`web/hooks/use-fleet-stats.ts`, `fleet-view.tsx`) - NEEDS INPUT
  cards show what the session is blocked on (permission notification text); ERROR cards carry the
  failing tool and message.
- **Demo permission beat** (`web/lib/mock-scenario.ts`) - a 3s permission gate before the final
  Bash type-check so the waiting state is demoable end-to-end.
- **Demo showcase loop** (`web/hooks/use-agent-simulation.ts`, `web/hooks/simulation/types.ts`,
  `index.tsx`, `control-bar.tsx`, `use-keyboard-shortcuts.ts`, `shortcuts-overlay.tsx`,
  `canvas.tsx`) - in demo
  mode the mock scenario replays continuously: when it plays out (last event + the 8s
  `MOCK_END_BUFFER_S`), the simulation restarts from a clean slate instead of stopping playback,
  so the demo playground runs hands-off on a showcase/kiosk screen. Toggled with `L` or the `⋮`
  menu → Loop demo (loop icon, active state, `L` hint); on by default and persisted like the
  other view prefs (`agent-flow.view.demoLoop`). The toggle is only surfaced (and the `L` key only
  acts) in demo mode; live mode is untouched, and switching the loop off restores upstream's
  play-once-then-stop behavior. Because the scenario reuses agent/edge IDs across runs, a
  simulation-clock rewind (loop restart, manual restart, backward seek) also clears the
  canvas-local history caches in `canvas.tsx` (edge warmth, agent heat, prev-state maps, pending
  effects) so each replay starts visually clean - no stale trails, and the opening spawn ripple
  fires every loop.
- **Auto-highlight video export** (`web/hooks/use-highlight-export.ts`, new; `index.tsx`,
  `control-bar.tsx`, `shortcuts-overlay.tsx`, `use-keyboard-shortcuts.ts`,
  `web/lib/canvas-constants.ts`) - `R` or the `⋮` menu scores the session's timeline events,
  picks the most eventful 12s window, replays it in review mode with the director driving while
  recording the canvas via MediaRecorder + `captureStream`, downloads a `.webm` (`.mp4` on Safari,
  which cannot record WebM), and restores the prior playback state. The menu entry hides when
  MediaRecorder is unsupported. The recording banner is DOM, so it stays out of the captured frames.
- **Session poster export** (`web/components/agent-visualizer/poster-export.ts`, new;
  `background-layer.ts` exports the brand paths; `index.tsx`, `control-bar.tsx`) - `⋮` menu →
  Save poster renders a 3200x1800 PNG share card: Riverside-styled stats column (duration, agents,
  tool calls, errors, tokens, est. cost, model chips, logo mark) beside a cover-fit snapshot of
  the live canvas.

It deliberately **excludes** the local `pnpm-workspace.yaml` `allowBuilds` change (machine setup,
documented in the Setup section of `systems/reference/agent-flow.md`). The `colors.ts` legibility refinements that
were once uncommitted are now commits on `riverside-theme` and live in the theme patch.

## Apply it (fresh clone, branch not present)

```bash
# point this at your local marketing-brain checkout (this patch lives in that repo, not in ~/agent-flow)
BRAIN=~/marketing-brain
cd ~/agent-flow
# pin to upstream v0.9.1 - the 2026-07-11 upstream commits collide with this layer (see note below)
git checkout -b riverside-theme 2959fa9
git apply "$BRAIN/systems/reference/assets/agent-flow-riverside-theme.patch"
git commit -am "Apply Riverside brand theme to Agent Flow visualizer"
git checkout -b riverside-ux
git apply "$BRAIN/systems/reference/assets/agent-flow-riverside-ux.patch"
git commit -am "Add Riverside UX layer (shortcuts overlay, control discoverability, demo distDir)"
```

Then rebuild the relay artifact (`node scripts/build-relay.js`), restart any running relay (via
`launchctl kickstart -k` if the launchd keep-alive is installed - see the system doc), and run the
dev server as usual. A relay that keeps running the old artifact will not emit the per-agent
`model_detected` events.

> **Pin the base to upstream v0.9.1 (`2959fa9`).** Upstream merged five commits on 2026-07-11
> (#58-#64), including its own per-agent model-name work that collides with this layer's parser
> and web hunks - the patch no longer applies on the moved `main`. On a fresh clone, check out the
> pinned commit before branching: `git checkout -b riverside-theme 2959fa9`. Rebasing the layer
> onto the new upstream `main` is a deliberate future task (the model-visibility feature partially
> overlaps upstream's), not something to do casually while recovering the branch.

Verified on 2026-07-14 to apply cleanly on top of `riverside-theme` at the pinned base, typecheck
clean (`tsc --noEmit`), and play correctly in demo mode (loop wrap and loop-off stop both
exercised in a browser). The 2026-07-14 regeneration added the demo showcase loop and was rebuilt
from a reconstruction of the branch pinned at `2959fa9` (not from Hanan's clone - two cosmetic
hunks in `agent-types.ts` and `handle-agent-events.ts` resolved against that exact base), so
Hanan's local `riverside-ux` needs the demo-loop commit cherry-picked or re-applied from this
patch to stay in sync. The 2026-07-13 regeneration covered the agent-node shape change (rounded
hexagon nodes and a rounded-square background grid) and folded in the previously unregenerated
top-bar segmented-groups, glass-groups, and review-playback commits. The 2026-07-11 regeneration
covered the highlight-export and session-poster work, and before that director mode, event pings,
history trails, fleet reasons, and the timeline-Gantt and agent-roster commits.

## Refreshing this patch

If the UX layer changes again on Hanan's clone, regenerate from `~/agent-flow` by diffing the
**whole** `riverside-theme`→`riverside-ux` range - no explicit file list. The earlier curated-list
form silently dropped new files (`web/public/icon.svg`) and the brand-mark / dev-indicator commits;
the full-range diff captures every changed file automatically:

```bash
git diff riverside-theme riverside-ux \
  > systems/reference/assets/agent-flow-riverside-ux.patch
```

The range diff is naturally scoped: it excludes everything already in `riverside-theme` (the whole
theme), and it excludes `pnpm-workspace.yaml` because that is a working-tree change, not a commit
on `riverside-ux`.
