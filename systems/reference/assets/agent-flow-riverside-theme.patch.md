<!-- last-reviewed: 2026-07-14 -->
# Agent Flow - Riverside theme patch

`agent-flow-riverside-theme.patch` is a checked-in backup of the local-only `riverside-theme`
branch of the [Agent Flow](../agent-flow.md) clone. That branch lives only on Hanan's machine and
was never pushed (the upstream `patoles/agent-flow` is a public third-party repo, so internal
branding must not go there). This patch is the recovery and sharing path instead.

## What it contains

The complete Riverside cosmetic re-skin - all three theme commits (initial re-skin,
text-legibility refinements, and the 2026-07-11 alignment to exact Riverside Design System tokens
from `references/design-system/`). Scoped to the five theme files only:

- `web/lib/colors.ts` - core palette (design-system tokens: primary.c600 `#9671ff` accent,
  secondary gray surfaces/text, status ramps for the functional state colors)
- `web/app/globals.css` - Instrument Sans font, brand `.dark` vars, glass-card. On-primary
  foreground tokens (`--primary-foreground`, `--sidebar-primary-foreground`) are dark `#151515`
  (secondary.c1000), not white, so control labels clear WCAG AA (~5.4:1) on the `#9671ff` purple
- `web/app/layout.tsx` - background (`#151515`, secondary.c1000) + "Riverside Agent Flow" title, plus
  `suppressHydrationWarning` on `<body>` to silence the React hydration mismatch that browser
  extensions (e.g. Grammarly) trigger by injecting `data-gr-*` attributes onto the body before
  React hydrates
- `web/components/agent-visualizer/index.tsx` and `.../file-attention-panel.tsx` - two stray cyan
  literals; the empty-state heading/subtitle use opaque primary tints (`#c3afff` c400 / `#b196ff`
  c500) rather than low-alpha purple, for legible contrast on the `#151515` canvas

It deliberately **excludes** the local `pnpm-workspace.yaml` `allowBuilds` change - that is
machine setup, not theme, and is documented separately in the Setup section of `systems/reference/agent-flow.md`.

## Apply it (fresh clone, branch not present)

```bash
# point this at your local marketing-brain checkout (this patch lives in that repo, not in ~/agent-flow)
BRAIN=~/marketing-brain
cd ~/agent-flow
git checkout main
git checkout -b riverside-theme
git apply "$BRAIN/systems/reference/assets/agent-flow-riverside-theme.patch"
git commit -am "Apply Riverside brand theme to Agent Flow visualizer"
```

Then run the dev server as usual. Verified to apply cleanly against upstream `main` on 2026-07-11.

## Refreshing this patch

If the theme changes again on Hanan's clone, regenerate from `~/agent-flow` (the explicit
`main riverside-theme` range means the command works from any checked-out branch):

```bash
git diff main riverside-theme -- web/lib/colors.ts web/app/globals.css web/app/layout.tsx \
  web/components/agent-visualizer/index.tsx \
  web/components/agent-visualizer/file-attention-panel.tsx \
  > systems/reference/assets/agent-flow-riverside-theme.patch
```
