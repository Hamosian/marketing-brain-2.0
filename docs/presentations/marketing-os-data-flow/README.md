# Marketing OS, how the system works (deck)

Riverside-branded 10-slide deck of the Marketing OS architecture and data-flow diagrams: the platform at a glance, a request end to end, progressive disclosure, the learning flywheel, the operating state loop, and autonomy today. Slide-deck version of [`docs/marketing-os-data-flow.html`](../../marketing-os-data-flow.html) and the README architecture section.

- **Deck:** [`marketing-os-how-it-works.pptx`](marketing-os-how-it-works.pptx)
- **Google Slides:** in a presentation choose File > Import slides and upload the .pptx (or upload to Drive and "Open with Google Slides"). If a fallback font appears, select all and re-apply Instrument Sans.
- **Rebuild:** `npm install pptxgenjs && node build.js` in this directory (regenerates the .pptx from `build.js`; the logos are the only assets).

The repo is the source of truth for the diagrams. `build.js` hard-codes the slide content, so rebuilding alone reproduces the same slides. If the deck drifts from `CLAUDE.md` or `systems/owned/marketing-brain.md`, first update the content in `build.js` against those files, then rebuild and commit the regenerated .pptx.
