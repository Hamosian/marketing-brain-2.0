# Marketing OS deck

A Riverside-branded slide deck (`Riverside-Marketing-OS.pptx`) explaining the Team Context Brain / Marketing OS: the goal, and what the marketing department unlocks over time, framed as a capability roadmap. Built for the marketing team.

The `.pptx` is committed so you can present it directly. The generator is committed too so the deck stays reproducible and editable in version control, in keeping with the repo's "AI-first, version-controlled" philosophy.

## Contents

| File | What it is |
|------|------------|
| `Riverside-Marketing-OS.pptx` | The deck. Open in PowerPoint, Keynote, or Google Slides. |
| `build.js` | pptxgenjs generator. Edit this, not the `.pptx`, then rebuild. |
| `riverside-logo-white.png` | White Riverside logo for dark slides (used by `build.js`). |
| `riverside-logo.png` | Source logo (near-black on transparent). Used to regenerate the white version. |
| `package.json` / `package-lock.json` | Pins `pptxgenjs`. |

## Rebuild the deck

```bash
cd docs/presentations/marketing-os
npm install
node build.js          # writes Riverside-Marketing-OS.pptx
```

### Font requirement

The deck was generated with **Inter** before the brand switched to **Instrument Sans** (#57). Rebuild with `build.js` updated to Instrument Sans before presenting, and present from a machine that has the font installed, or PowerPoint will substitute a generic sans.

```bash
brew install --cask font-instrument-sans   # macOS, if the font is missing
```

If the brand font is absent, some renderers substitute a trial font that stamps a "DEMO" glyph onto characters like `+` and `-`. That is a missing-font symptom, not a defect in the file. Install the font and re-render.

## Visual QA (render to images)

Requires LibreOffice and Poppler:

```bash
brew install --cask libreoffice
brew install poppler

soffice --headless --convert-to pdf Riverside-Marketing-OS.pptx
pdftoppm -jpeg -r 130 Riverside-Marketing-OS.pdf slide   # writes slide-NN.jpg
```

`*.pdf`, `slide-*.jpg`, and `node_modules/` are git-ignored.

## Regenerate the white logo

If you swap the source logo, recolor its opaque pixels to white for dark backgrounds:

```bash
python3 -c "from PIL import Image; im=Image.open('riverside-logo.png').convert('RGBA'); px=im.load(); w,h=im.size; [px.__setitem__((x,y),(255,255,255,px[x,y][3])) for y in range(h) for x in range(w) if px[x,y][3]>5]; im.save('riverside-logo-white.png')"
```
