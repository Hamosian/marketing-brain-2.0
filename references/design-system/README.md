# Riverside Design System

A local extraction of the Riverside Design System from Figma, organized for use in code and documentation. Generated from the live Figma library (file wXQnl6mSANal8DCbMssQkO).

> **This is the product design system, not the marketing one.** These tokens describe the in-app product UI (dark product canvas, product component library). For marketing deliverables - decks, docs, landing pages, ads, dashboards, any artifact a person outside the product reads - use `/riverside-brand-guidelines` (colors, type, tone) and `/riverside-ux-patterns` (layout, interaction) instead. Only pull from this directory when the artifact is showing or mimicking an actual product screen (a UI mockup, a feature screenshot, an in-app component reference). The two systems intentionally differ on things like purple hex value; do not blend them.

## What is in here

```
riverside-design-system/
  README.md
  reference.html          Visual reference: color swatches and type scale
  tokens/
    colors.json           All color tokens, structured by group, with usage notes
    colors.css            CSS custom properties (--rs-*)
    colors.scss           SCSS variables ($rs-*)
    typography.json       Type styles (Instrument Sans scale)
    typography.css        CSS variables and ready-to-use type classes (.rs-*)
    tokens.js             JS export of colors and typography
  components/
    components.md         66 component families grouped by section, with variant axes
    components.json       Same inventory, structured
  icons/
    icons.json            1301 icons grouped into 21 categories
    icons.md              Readable icon index by category
  brand/
    brand.md              Logo variants, core brand colors, type, background textures
```

## Foundations at a glance

Color. The system is built for a dark product UI. Primary brand is primary.c600 (#9671ff), with primary.c800 (#7848ff) as the saturated step. Surfaces run on the secondary gray ramp (secondary.c1000 #151515 background up to secondary.c100 #fafafa text). Status colors cover error, warning, and success. An upgrade accent (upgrade.c700 #c9f273) marks paid or premium actions. A large transparent layer set supports overlays and glass effects.

Typography. One typeface, Instrument Sans, across the whole system. Weights: Regular 400, Medium 500, Semi Bold 600, Bold 700. (Instrument Sans tops out at 700; the former Extra Bold 800 headings now render at Bold 700.) The scale spans tiny-label (10px) through heading-xlarge (36px), with dedicated label, body, link, and heading families.

Components. 66 documented families across Buttons, Controls, Fields, Modals and Panels, Tooltips, Steps and Progress, Slider, Notifications and Banners, Menus, Video Player, Navigation, Logos and Avatars. Button Text (300 variants) and Mega Button (280 variants) are the largest matrices.

Icons. 1301 line-style icons in 21 categories, named category/icon-name.

## How to use the tokens

CSS:

```css
@import "tokens/colors.css";
@import "tokens/typography.css";

.card {
  background: var(--rs-secondary-c800);
  color: var(--rs-secondary-c100);
}
.card h2 { /* or just add class="rs-heading-small" */
  font: 700 var(--rs-font-heading-small-size)/var(--rs-font-heading-small-line) 'Instrument Sans';
}
```

JS / TS:

```js
import { colors, typography } from "./tokens/tokens.js";
const brand = colors.groups.primary.c600; // #9671ff
```

## Notes

Color hex values are exact, captured from the Figma paint styles. Variant counts reflect the full Figma matrix. Background textures and avatar images are raster image fills in Figma and are referenced by name in brand/brand.md rather than exported as binaries; pull those directly from Figma when you need the assets.
