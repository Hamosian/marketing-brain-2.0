const pptxgen = require("pptxgenjs");

// ---- Riverside brand palette ----
const PURPLE     = "7C5CFF";
const PURPLE_DK  = "5B3FD6";
const NEAR_BLACK = "0F0F14";
const WHITE      = "FFFFFF";
const DARK_GRAY  = "1C1C24";
const MID_GRAY   = "2A2A35";
const LIGHT_GRAY = "E6E6EB";
const MUTED      = "9A9AA8";
const FONT       = "Inter";

const LOGO = "riverside-logo-white.png";

const pres = new pptxgen();
pres.defineLayout({ name: "RIVERSIDE", width: 13.33, height: 7.5 });
pres.layout = "RIVERSIDE";
pres.author = "Riverside Growth";
pres.title  = "The Marketing OS";

const W = 13.33, H = 7.5;
const ML = 0.7;            // left margin
const CW = W - ML * 2;     // content width

const card = () => ({ type: "outer", color: "000000", blur: 9, offset: 3, angle: 135, opacity: 0.30 });

// ---- shared slide furniture ----
function bg(slide) { slide.background = { color: NEAR_BLACK }; }

function cornerDot(slide) {
  slide.addShape(pres.shapes.OVAL, { x: 12.95, y: 0.5, w: 0.14, h: 0.14, fill: { color: PURPLE } });
}

function header(slide, eyebrow, title) {
  // purple left accent bar
  slide.addShape(pres.shapes.RECTANGLE, { x: ML, y: 0.62, w: 0.07, h: 0.74, fill: { color: PURPLE } });
  if (eyebrow) {
    slide.addText(eyebrow.toUpperCase(), {
      x: ML + 0.22, y: 0.5, w: 11, h: 0.3, margin: 0,
      fontSize: 11, bold: true, color: PURPLE, fontFace: FONT, charSpacing: 2, align: "left", valign: "top"
    });
    slide.addText(title, {
      x: ML + 0.22, y: 0.78, w: 11.5, h: 0.62, margin: 0,
      fontSize: 29, bold: true, color: WHITE, fontFace: FONT, align: "left", valign: "top"
    });
  } else {
    slide.addText(title, {
      x: ML + 0.22, y: 0.6, w: 11.5, h: 0.78, margin: 0,
      fontSize: 30, bold: true, color: WHITE, fontFace: FONT, align: "left", valign: "middle"
    });
  }
  cornerDot(slide);
}

function pill(slide, text, x, y, w, color = PURPLE) {
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h: 0.34, fill: { color }, rectRadius: 0.17 });
  slide.addText(text.toUpperCase(), {
    x, y, w, h: 0.34, margin: 0, align: "center", valign: "middle",
    fontSize: 10.5, bold: true, color: WHITE, fontFace: FONT, charSpacing: 1.5
  });
}

// rounded card
function box(slide, x, y, w, h, opts = {}) {
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x, y, w, h, rectRadius: 0.1,
    fill: { color: opts.fill || DARK_GRAY },
    line: { color: opts.border || MID_GRAY, width: 1 },
    shadow: opts.shadow ? card() : undefined
  });
}

// =========================================================
// 1. COVER
// =========================================================
let s = pres.addSlide(); bg(s);
s.addImage({ path: LOGO, x: ML, y: 0.6, w: 2.5, h: 0.594 });
// faint large purple accent block (thin bar, accent only)
s.addShape(pres.shapes.RECTANGLE, { x: ML, y: 3.42, w: 1.7, h: 0.05, fill: { color: PURPLE } });
pill(s, "Riverside Growth  ·  internal", ML, 2.7, 3.3);
s.addText("The Marketing OS", {
  x: ML, y: 3.6, w: 11.5, h: 1.0, margin: 0,
  fontSize: 50, bold: true, color: WHITE, fontFace: FONT
});
s.addText("Our team context brain: turning Claude from an isolated tool into an operating partner that understands our systems, our work, and our priorities.", {
  x: ML, y: 4.7, w: 9.6, h: 1.0, margin: 0,
  fontSize: 18, color: LIGHT_GRAY, fontFace: FONT, lineSpacingMultiple: 1.15
});
s.addText("Goal and capability roadmap  ·  June 2026", {
  x: ML, y: 6.7, w: 9, h: 0.4, margin: 0, fontSize: 13, color: MUTED, fontFace: FONT
});

// =========================================================
// 2. THE PROBLEM
// =========================================================
s = pres.addSlide(); bg(s);
header(s, "Why we built it", "The knowledge was trapped");
const probs = [
  ["Tribal knowledge", "How we run paid, how our pipeline really works, what breaks and why. It lived in people's heads, not anywhere the team could reuse."],
  ["Siloed tools", "HubSpot, Omni, monday, Slack, Windsor, the ad platforms. Context never crossed from one system to the next."],
  ["AI started cold", "Every chat began from zero. We re-explained our systems, boards, and conventions, every single time."]
];
{
  const n = probs.length, gap = 0.4, cw = (CW - gap * (n - 1)) / n, y = 1.75, ch = 3.5;
  probs.forEach((p, i) => {
    const x = ML + i * (cw + gap);
    box(s, x, y, cw, ch, { shadow: true });
    s.addText(String(i + 1).padStart(2, "0"), { x: x + 0.35, y: y + 0.35, w: 1.2, h: 0.6, margin: 0, fontSize: 30, bold: true, color: PURPLE, fontFace: FONT });
    s.addText(p[0], { x: x + 0.35, y: y + 1.15, w: cw - 0.7, h: 0.5, margin: 0, fontSize: 19, bold: true, color: WHITE, fontFace: FONT });
    s.addText(p[1], { x: x + 0.35, y: y + 1.75, w: cw - 0.7, h: ch - 2.0, margin: 0, fontSize: 13.5, color: LIGHT_GRAY, fontFace: FONT, lineSpacingMultiple: 1.18, valign: "top" });
  });
}
box(s, ML, 5.6, CW, 0.95, { fill: MID_GRAY, border: PURPLE });
s.addText([
  { text: "The cost:  ", options: { bold: true, color: PURPLE } },
  { text: "repeated context, inconsistent answers, and slow onboarding. Every gain was reset the moment a person or a chat moved on.", options: { color: WHITE } }
], { x: ML + 0.35, y: 5.6, w: CW - 0.7, h: 0.95, margin: 0, fontSize: 15, fontFace: FONT, valign: "middle", lineSpacingMultiple: 1.12 });

// =========================================================
// 3. THE GOAL (statement)
// =========================================================
s = pres.addSlide(); bg(s);
header(s, "The goal", "Claude as an operating partner");
s.addText("“", { x: ML - 0.05, y: 1.5, w: 1.5, h: 1.2, margin: 0, fontSize: 110, bold: true, color: PURPLE, fontFace: "Georgia" });
s.addText([
  { text: "Turn Claude from an isolated tool into an ", options: { color: WHITE } },
  { text: "operating partner", options: { color: PURPLE, bold: true } },
  { text: " that understands our systems, workflows, conventions, tribal knowledge, priorities, and how we route work.", options: { color: WHITE } }
], { x: ML + 0.05, y: 2.45, w: 11.4, h: 2.1, margin: 0, fontSize: 30, bold: true, fontFace: FONT, lineSpacingMultiple: 1.12, valign: "top" });

const goals = [
  ["Version-controlled", "Lives in git. Every change is reviewed and shipped as a PR."],
  ["AI-first", "Structured for Claude to consume, not for humans to skim."],
  ["Shared by the team", "One brain the whole department reads from and writes to."]
];
{
  const n = goals.length, gap = 0.4, cw = (CW - gap * (n - 1)) / n, y = 5.25, ch = 1.55;
  goals.forEach((g, i) => {
    const x = ML + i * (cw + gap);
    box(s, x, y, cw, ch);
    s.addShape(pres.shapes.RECTANGLE, { x, y: y + 0.22, w: 0.06, h: ch - 0.44, fill: { color: PURPLE } });
    s.addText(g[0], { x: x + 0.3, y: y + 0.25, w: cw - 0.5, h: 0.4, margin: 0, fontSize: 16, bold: true, color: WHITE, fontFace: FONT });
    s.addText(g[1], { x: x + 0.3, y: y + 0.7, w: cw - 0.55, h: 0.75, margin: 0, fontSize: 12.5, color: LIGHT_GRAY, fontFace: FONT, lineSpacingMultiple: 1.12, valign: "top" });
  });
}

// =========================================================
// 4. WHAT IT IS (two column: text + structure)
// =========================================================
s = pres.addSlide(); bg(s);
header(s, "The what", "A context brain, built as a repo");
// left text
s.addText([
  { text: "It is a single, version-controlled knowledge base, structured for AI and maintained by the team.\n\n", options: { fontSize: 16, color: WHITE, bold: true, breakLine: true } },
  { text: "CLAUDE.md", options: { fontSize: 14, color: PURPLE, bold: true } },
  { text: " is the always-loaded map. Everything else loads only when the task needs it.\n\n", options: { fontSize: 14, color: LIGHT_GRAY } },
  { text: "Pointers, not copies.", options: { fontSize: 14, color: PURPLE, bold: true } },
  { text: " We link to the live source, never duplicate it, so the brain never goes stale when a platform changes.", options: { fontSize: 14, color: LIGHT_GRAY } }
], { x: ML, y: 1.85, w: 5.5, h: 4.6, margin: 0, fontFace: FONT, lineSpacingMultiple: 1.2, valign: "top" });

// right: structure diagram
const sx = 6.9, sw = 5.7;
box(s, sx, 1.8, sw, 0.85, { fill: MID_GRAY, border: PURPLE, shadow: true });
s.addText([
  { text: "CLAUDE.md", options: { bold: true, color: WHITE, fontSize: 16 } },
  { text: "    always loaded", options: { color: PURPLE, fontSize: 12, bold: true } }
], { x: sx + 0.35, y: 1.8, w: sw - 0.7, h: 0.85, margin: 0, valign: "middle", fontFace: FONT });

const children = [
  ["references/", "IDs, contacts, boards, channels"],
  ["systems/", "how each system we own works"],
  [".claude/skills/", "workflows and specialist sub-agents"],
  ["systems/reference/", "platforms we depend on"]
];
children.forEach((c, i) => {
  const y = 3.0 + i * 0.92;
  // connector
  s.addShape(pres.shapes.LINE, { x: sx + 0.4, y: 2.65, w: 0, h: y + 0.35 - 2.65, line: { color: MID_GRAY, width: 1.5 } });
  s.addShape(pres.shapes.LINE, { x: sx + 0.4, y: y + 0.35, w: 0.35, h: 0, line: { color: MID_GRAY, width: 1.5 } });
  box(s, sx + 0.85, y, sw - 0.85, 0.74);
  s.addText([
    { text: c[0] + "   ", options: { bold: true, color: PURPLE, fontSize: 13 } },
    { text: c[1], options: { color: LIGHT_GRAY, fontSize: 12 } }
  ], { x: sx + 1.15, y, w: sw - 1.35, h: 0.74, margin: 0, valign: "middle", fontFace: FONT });
});
s.addText("Loaded on demand", { x: sx + 0.85, y: 6.75, w: sw, h: 0.3, margin: 0, fontSize: 11, italic: true, color: MUTED, fontFace: FONT });

// =========================================================
// 5. BY THE NUMBERS
// =========================================================
s = pres.addSlide(); bg(s);
header(s, "Today", "What is already in the brain");
const stats = [
  ["27", "skills and workflows", "ready to trigger by name"],
  ["12", "specialist sub-agents", "data, paid, web, lifecycle, more"],
  ["5", "owned systems documented", "and a growing reference layer"],
  ["15+", "connected systems", "from HubSpot to the ad platforms"]
];
{
  const n = stats.length, gap = 0.4, cw = (CW - gap * (n - 1)) / n, y = 2.2, ch = 3.1;
  stats.forEach((st, i) => {
    const x = ML + i * (cw + gap);
    box(s, x, y, cw, ch, { shadow: true });
    s.addText(st[0], { x: x, y: y + 0.45, w: cw, h: 1.3, margin: 0, fontSize: 64, bold: true, color: PURPLE, fontFace: FONT, align: "center" });
    s.addShape(pres.shapes.RECTANGLE, { x: x + cw / 2 - 0.4, y: y + 1.85, w: 0.8, h: 0.035, fill: { color: MID_GRAY } });
    s.addText(st[1], { x: x + 0.2, y: y + 2.05, w: cw - 0.4, h: 0.5, margin: 0, fontSize: 14.5, bold: true, color: WHITE, fontFace: FONT, align: "center" });
    s.addText(st[2], { x: x + 0.2, y: y + 2.55, w: cw - 0.4, h: 0.45, margin: 0, fontSize: 11.5, color: MUTED, fontFace: FONT, align: "center", lineSpacingMultiple: 1.05 });
  });
}
s.addText("Numbers grow every week the team uses it. That is the point.", { x: ML, y: 5.7, w: CW, h: 0.4, margin: 0, fontSize: 13.5, italic: true, color: LIGHT_GRAY, fontFace: FONT, align: "center" });

// =========================================================
// 6. PROGRESSIVE DISCLOSURE
// =========================================================
s = pres.addSlide(); bg(s);
header(s, "How it works", "A map, not a library");
s.addText("Claude never loads the whole knowledge base. It gets exactly the context the task needs, nothing more, so the context window stays sharp and answers stay accurate.", {
  x: ML, y: 1.7, w: 11.6, h: 0.7, margin: 0, fontSize: 15, color: LIGHT_GRAY, fontFace: FONT, lineSpacingMultiple: 1.15
});
const layers = [
  ["1", "Always loaded", "CLAUDE.md", "The map. What this repo is, where knowledge lives, team conventions."],
  ["2", "Loaded on demand", "systems/ · references/", "“Check the paid account” pulls in just the paid acquisition doc."],
  ["3", "Deep, inside skills", "knowledge/ files", "A skill opens heavy reference only at the exact step it is needed."]
];
{
  const y0 = 2.65, lh = 1.15, gap = 0.22;
  layers.forEach((l, i) => {
    const y = y0 + i * (lh + gap);
    const w = CW;
    box(s, ML, y, w, lh, { shadow: true });
    s.addShape(pres.shapes.OVAL, { x: ML + 0.3, y: y + lh / 2 - 0.3, w: 0.6, h: 0.6, fill: { color: NEAR_BLACK }, line: { color: PURPLE, width: 1.5 } });
    s.addText(l[0], { x: ML + 0.3, y: y + lh / 2 - 0.3, w: 0.6, h: 0.6, margin: 0, fontSize: 20, bold: true, color: PURPLE, fontFace: FONT, align: "center", valign: "middle" });
    s.addText([
      { text: l[1] + "    ", options: { bold: true, color: WHITE, fontSize: 16 } },
      { text: l[2], options: { color: PURPLE, fontSize: 12.5, bold: true } }
    ], { x: ML + 1.15, y: y + 0.2, w: w - 1.4, h: 0.45, margin: 0, fontFace: FONT });
    s.addText(l[3], { x: ML + 1.15, y: y + 0.62, w: w - 1.4, h: 0.45, margin: 0, fontSize: 12.5, color: LIGHT_GRAY, fontFace: FONT });
  });
}

// =========================================================
// 7. MARKETING OS - ONE FRONT DOOR
// =========================================================
s = pres.addSlide(); bg(s);
header(s, "The front door", "One agent for the whole department");
s.addText([
  { text: "/marketing-brain", options: { bold: true, color: PURPLE, fontSize: 15 } },
  { text: " takes any broad or cross-system request and runs the operating loop, then delegates to the right specialist.", options: { color: LIGHT_GRAY, fontSize: 14 } }
], { x: ML, y: 1.7, w: 11.6, h: 0.55, margin: 0, fontFace: FONT, lineSpacingMultiple: 1.12 });

const steps = ["Classify\nthe request", "Load\nthe context", "Delegate to\nsub-agents", "Synthesize a\nrecommendation", "Close\nthe loop"];
{
  const n = steps.length, gap = 0.35, cw = (CW - gap * (n - 1)) / n, y = 2.45, ch = 1.1;
  steps.forEach((st, i) => {
    const x = ML + i * (cw + gap);
    box(s, x, y, cw, ch, { fill: MID_GRAY });
    s.addText(st, { x: x + 0.1, y, w: cw - 0.2, h: ch, margin: 0, fontSize: 13, bold: true, color: WHITE, fontFace: FONT, align: "center", valign: "middle", lineSpacingMultiple: 1.0 });
    if (i < n - 1) s.addText("›", { x: x + cw + 0.02, y, w: gap, h: ch, margin: 0, fontSize: 22, bold: true, color: PURPLE, fontFace: FONT, align: "center", valign: "middle" });
  });
}
s.addText("Twelve specialist sub-agents", { x: ML, y: 3.95, w: CW, h: 0.35, margin: 0, fontSize: 13, bold: true, color: PURPLE, fontFace: FONT, charSpacing: 1 });
const agents = ["Data", "Measurement", "HubSpot", "Lifecycle", "monday", "Slack", "Content", "Paid acquisition", "Website", "SEO and AI search", "Ops automation", "Campaign"];
{
  const cols = 6, gap = 0.25, cw = (CW - gap * (cols - 1)) / cols, ch = 0.62, y0 = 4.4;
  agents.forEach((a, i) => {
    const r = Math.floor(i / cols), c = i % cols;
    const x = ML + c * (cw + gap), y = y0 + r * (ch + 0.22);
    box(s, x, y, cw, ch);
    s.addShape(pres.shapes.OVAL, { x: x + 0.22, y: y + ch / 2 - 0.05, w: 0.1, h: 0.1, fill: { color: PURPLE } });
    s.addText(a, { x: x + 0.42, y, w: cw - 0.5, h: ch, margin: 0, fontSize: 12, color: WHITE, fontFace: FONT, valign: "middle" });
  });
}
s.addText("Closing the loop: tracks operating state, asks before any mutating action, updates monday and Slack, captures the learning.", { x: ML, y: 6.55, w: CW, h: 0.5, margin: 0, fontSize: 12.5, italic: true, color: MUTED, fontFace: FONT });

// =========================================================
// 8. THE REACH - CONNECTED SYSTEMS
// =========================================================
s = pres.addSlide(); bg(s);
header(s, "The reach", "It works where we already work");
const groups = [
  ["Data and BI", ["Omni BI", "Snowflake", "Mixpanel", "Windsor.ai"]],
  ["CRM and lifecycle", ["HubSpot", "Pre-Op data", "Gong calls"]],
  ["Work and comms", ["monday.com", "Slack"]],
  ["Paid acquisition", ["Google Ads", "Meta", "LinkedIn", "Microsoft"]],
  ["Web and SEO", ["riverside.com", "Search Console", "Ahrefs"]],
  ["Content and brand", ["Decks", "Docs", "Brand guidelines"]]
];
{
  const cols = 3, gap = 0.4, cw = (CW - gap * (cols - 1)) / cols, ch = 1.95, y0 = 1.9, rgap = 0.35;
  groups.forEach((g, i) => {
    const r = Math.floor(i / cols), c = i % cols;
    const x = ML + c * (cw + gap), y = y0 + r * (ch + rgap);
    box(s, x, y, cw, ch, { shadow: true });
    s.addShape(pres.shapes.RECTANGLE, { x, y: y + 0.28, w: 0.06, h: 0.4, fill: { color: PURPLE } });
    s.addText(g[0], { x: x + 0.32, y: y + 0.25, w: cw - 0.5, h: 0.45, margin: 0, fontSize: 15, bold: true, color: WHITE, fontFace: FONT });
    // chips
    let cx = x + 0.32, cy = y + 0.85;
    g[1].forEach((chip) => {
      const chw = 0.22 + chip.length * 0.085;
      if (cx + chw > x + cw - 0.25) { cx = x + 0.32; cy += 0.5; }
      slideChip(s, chip, cx, cy, chw);
      cx += chw + 0.18;
    });
  });
}
function slideChip(slide, text, x, y, w) {
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h: 0.38, rectRadius: 0.19, fill: { color: MID_GRAY } });
  slide.addText(text, { x, y, w, h: 0.38, margin: 0, fontSize: 11, color: LIGHT_GRAY, fontFace: FONT, align: "center", valign: "middle" });
}

// =========================================================
// 9. THE FLYWHEEL
// =========================================================
s = pres.addSlide(); bg(s);
header(s, "Why it compounds", "It gets smarter every time we use it");
const fly = [
  ["Do the work", "Run a real workflow with Claude: a campaign, an audit, an investigation."],
  ["Capture it", "Say /retro. Claude writes up the non-obvious learning."],
  ["Open a PR", "The learning is reviewed and merged into the repo, not lost in a chat."],
  ["Brain improves", "The doc or skill is now sharper for everyone."],
  ["Next run is better", "The whole team starts the next task further ahead."]
];
{
  const n = fly.length, gap = 0.3, cw = (CW - gap * (n - 1)) / n, y = 2.0, ch = 2.7;
  fly.forEach((f, i) => {
    const x = ML + i * (cw + gap);
    box(s, x, y, cw, ch, { shadow: true });
    s.addShape(pres.shapes.OVAL, { x: x + cw / 2 - 0.32, y: y + 0.35, w: 0.64, h: 0.64, fill: { color: NEAR_BLACK }, line: { color: PURPLE, width: 1.5 } });
    s.addText(String(i + 1), { x: x + cw / 2 - 0.32, y: y + 0.35, w: 0.64, h: 0.64, margin: 0, fontSize: 22, bold: true, color: PURPLE, fontFace: FONT, align: "center", valign: "middle" });
    s.addText(f[0], { x: x + 0.18, y: y + 1.15, w: cw - 0.36, h: 0.55, margin: 0, fontSize: 14, bold: true, color: WHITE, fontFace: FONT, align: "center", lineSpacingMultiple: 1.0 });
    s.addText(f[1], { x: x + 0.18, y: y + 1.7, w: cw - 0.36, h: 0.9, margin: 0, fontSize: 11.5, color: LIGHT_GRAY, fontFace: FONT, align: "center", lineSpacingMultiple: 1.12, valign: "top" });
    if (i < n - 1) s.addText("›", { x: x + cw + 0.01, y, w: gap, h: ch, margin: 0, fontSize: 20, bold: true, color: PURPLE, fontFace: FONT, align: "center", valign: "middle" });
  });
}
box(s, ML, 5.05, CW, 0.95, { fill: MID_GRAY, border: PURPLE });
s.addText([
  { text: "The result:  ", options: { bold: true, color: PURPLE } },
  { text: "knowledge stops being tribal. What one person learns once, the whole team reuses forever, and the advantage compounds week over week.", options: { color: WHITE } }
], { x: ML + 0.35, y: 5.05, w: CW - 0.7, h: 0.95, margin: 0, fontSize: 15, fontFace: FONT, valign: "middle", lineSpacingMultiple: 1.12 });

// =========================================================
// 10. DIVIDER - CAPABILITY ROADMAP
// =========================================================
s = pres.addSlide(); bg(s);
s.addImage({ path: LOGO, x: ML, y: 0.6, w: 1.8, h: 0.428 });
s.addShape(pres.shapes.RECTANGLE, { x: W / 2 - 1.0, y: 2.95, w: 2.0, h: 0.05, fill: { color: PURPLE } });
s.addText("The capability roadmap", { x: 1, y: 3.15, w: W - 2, h: 0.9, margin: 0, fontSize: 40, bold: true, color: WHITE, fontFace: FONT, align: "center" });
s.addText("What the marketing department unlocks as the brain grows.", { x: 1, y: 4.15, w: W - 2, h: 0.5, margin: 0, fontSize: 17, color: LIGHT_GRAY, fontFace: FONT, align: "center" });

// =========================================================
// 11. FOUR HORIZONS (timeline)
// =========================================================
s = pres.addSlide(); bg(s);
header(s, "The trajectory", "Four horizons");
const horizons = [
  ["Now", "Foundation live", "Daily brief, structured tasks, ad audits, self-serve data, sub-agent routing.", true],
  ["Next quarter", "The operating loop", "Campaign orchestration, automated readouts, lifecycle flows, spend pacing.", false],
  ["6 months", "Runs the rhythm", "Cross-system investigations, proactive anomaly flags, self-serve data for all.", false],
  ["12 months", "A compounding moat", "Institutional memory, day-one onboarding, the model replicated across teams.", false]
];
{
  const n = horizons.length, gap = 0.4, cw = (CW - gap * (n - 1)) / n;
  const lineY = 2.35;
  s.addShape(pres.shapes.LINE, { x: ML + cw / 2, y: lineY, w: CW - cw, h: 0, line: { color: MID_GRAY, width: 2 } });
  horizons.forEach((hz, i) => {
    const x = ML + i * (cw + gap);
    const cx = x + cw / 2;
    const active = hz[3];
    s.addShape(pres.shapes.OVAL, { x: cx - 0.13, y: lineY - 0.13, w: 0.26, h: 0.26, fill: { color: active ? PURPLE : NEAR_BLACK }, line: { color: PURPLE, width: 2 } });
    s.addText(hz[0].toUpperCase(), { x: x, y: lineY - 0.75, w: cw, h: 0.4, margin: 0, fontSize: 13, bold: true, color: active ? PURPLE : LIGHT_GRAY, fontFace: FONT, align: "center", charSpacing: 1 });
    const cardY = 2.9, ch = 3.4;
    box(s, x, cardY, cw, ch, { shadow: true, border: active ? PURPLE : MID_GRAY });
    s.addText(hz[1], { x: x + 0.3, y: cardY + 0.35, w: cw - 0.6, h: 0.9, margin: 0, fontSize: 18, bold: true, color: WHITE, fontFace: FONT, lineSpacingMultiple: 1.0, valign: "top" });
    s.addShape(pres.shapes.RECTANGLE, { x: x + 0.3, y: cardY + 1.45, w: 0.7, h: 0.04, fill: { color: PURPLE } });
    s.addText(hz[2], { x: x + 0.3, y: cardY + 1.7, w: cw - 0.6, h: ch - 1.9, margin: 0, fontSize: 13, color: LIGHT_GRAY, fontFace: FONT, lineSpacingMultiple: 1.2, valign: "top" });
  });
}
s.addText("We are here", { x: ML, y: 6.55, w: 2.5, h: 0.35, margin: 0, fontSize: 12, italic: true, bold: true, color: PURPLE, fontFace: FONT, align: "center" });

// =========================================================
// 12. NOW & NEXT (detail)
// =========================================================
s = pres.addSlide(); bg(s);
header(s, "Horizons 1 and 2", "Now, and next quarter");
function phaseCol(slide, x, w, tag, tagColor, title, items) {
  const y = 1.85, ch = 4.95;
  box(slide, x, y, w, ch, { shadow: true });
  pill(slide, tag, x + 0.35, y + 0.35, 1.7, tagColor);
  slide.addText(title, { x: x + 0.35, y: y + 0.85, w: w - 0.7, h: 0.5, margin: 0, fontSize: 18, bold: true, color: WHITE, fontFace: FONT });
  slide.addText(items.map((it, idx) => ({
    text: it, options: { bullet: { code: "2022", indent: 14 }, color: LIGHT_GRAY, fontSize: 13, breakLine: true, paraSpaceAfter: 8 }
  })), { x: x + 0.45, y: y + 1.5, w: w - 0.85, h: ch - 1.75, margin: 0, fontFace: FONT, lineSpacingMultiple: 1.1, valign: "top" });
}
{
  const gap = 0.5, w = (CW - gap) / 2;
  phaseCol(s, ML, w, "Live now", PURPLE, "The foundation", [
    "Daily operating brief: tasks, Slack, risks, and actions",
    "One front door for any marketing request",
    "Structured tasks with Why, What, and Done When",
    "Multi-platform paid ad audits, 250+ checks",
    "Self-serve data Q&A across Omni and Snowflake",
    "Living system docs: paid, HubSpot, Omni, website, ops",
    "Funnel and Pre-Op intelligence, Gong call exploration"
  ]);
  phaseCol(s, ML + w + gap, w, "Next quarter", PURPLE_DK, "The operating loop", [
    "Campaign orchestration: brief, launch, tracking, readout",
    "Automated weekly measurement and performance readouts",
    "Lifecycle journeys: MQL to SQL, nurture, win-back",
    "Paid spend pacing and wasted-spend alerts",
    "The flywheel running: every retro adds to the brain",
    "More sub-agents wired to more of our real workflows"
  ]);
}

// =========================================================
// 13. SCALING & COMPOUNDING (detail)
// =========================================================
s = pres.addSlide(); bg(s);
header(s, "Horizons 3 and 4", "Scaling, and a compounding moat");
{
  const gap = 0.5, w = (CW - gap) / 2;
  phaseCol(s, ML, w, "6 months", PURPLE, "Runs the rhythm", [
    "Cross-system investigations without hand-holding",
    "Proactive anomaly detection in the morning brief",
    "Self-serve data for every marketer, not just analysts",
    "Brand-consistent content and decks on demand",
    "The OS drives our weekly operating cadence"
  ]);
  phaseCol(s, ML + w + gap, w, "12 months", PURPLE_DK, "A compounding moat", [
    "Institutional memory that survives turnover",
    "New hires productive on day one",
    "Decisions grounded in one consistent source of truth",
    "The model replicated across other teams at Riverside",
    "A measurable speed advantage that keeps widening"
  ]);
}

// =========================================================
// 14. WHAT THIS MEANS FOR YOU
// =========================================================
s = pres.addSlide(); bg(s);
header(s, "For the team", "What this means for you");
const wins = [
  ["Stop re-explaining", "The AI already knows our systems, boards, and conventions. No more setting the scene every time."],
  ["Consistent answers", "Same logic every run, grounded in our real, live sources. Less second-guessing."],
  ["Less clicking", "Workflows replace manual trips through dashboards, boards, and admin panels."],
  ["Your knowledge compounds", "What you teach it once, the whole team reuses forever. Your best thinking outlives any single project."]
];
{
  const cols = 2, gap = 0.5, cw = (CW - gap) / cols, ch = 2.15, rgap = 0.35, y0 = 1.9;
  wins.forEach((win, i) => {
    const r = Math.floor(i / cols), c = i % cols;
    const x = ML + c * (cw + gap), y = y0 + r * (ch + rgap);
    box(s, x, y, cw, ch, { shadow: true });
    s.addShape(pres.shapes.OVAL, { x: x + 0.35, y: y + 0.35, w: 0.5, h: 0.5, fill: { color: PURPLE } });
    s.addText(String(i + 1), { x: x + 0.35, y: y + 0.35, w: 0.5, h: 0.5, margin: 0, fontSize: 18, bold: true, color: WHITE, fontFace: FONT, align: "center", valign: "middle" });
    s.addText(win[0], { x: x + 1.05, y: y + 0.4, w: cw - 1.3, h: 0.45, margin: 0, fontSize: 18, bold: true, color: WHITE, fontFace: FONT, valign: "middle" });
    s.addText(win[1], { x: x + 0.35, y: y + 1.05, w: cw - 0.7, h: 0.95, margin: 0, fontSize: 13.5, color: LIGHT_GRAY, fontFace: FONT, lineSpacingMultiple: 1.18, valign: "top" });
  });
}

// =========================================================
// 15. KEEPING IT HEALTHY
// =========================================================
s = pres.addSlide(); bg(s);
header(s, "The discipline", "A clean brain, or none at all");
box(s, ML, 1.75, CW, 0.85, { fill: MID_GRAY, border: PURPLE });
s.addText([
  { text: "A messy brain is worse than no brain:  ", options: { bold: true, color: PURPLE } },
  { text: "it produces wrong answers with high confidence. Four habits keep it trustworthy.", options: { color: WHITE } }
], { x: ML + 0.35, y: 1.75, w: CW - 0.7, h: 0.85, margin: 0, fontSize: 14.5, fontFace: FONT, valign: "middle" });
const rules = [
  ["Pointers, not copies", "Never duplicate live data. Link to the source so nothing drifts."],
  ["The RALPH loop", "Review, audit, learn, prune, handoff. A quarterly cleanup."],
  ["/health-check monthly", "Surfaces stale docs, empty stubs, and template drift."],
  ["/retro after novel work", "Non-negotiable. Capture the learning before it evaporates."]
];
{
  const cols = 2, gap = 0.5, cw = (CW - gap) / cols, ch = 1.5, rgap = 0.3, y0 = 2.95;
  rules.forEach((rl, i) => {
    const r = Math.floor(i / cols), c = i % cols;
    const x = ML + c * (cw + gap), y = y0 + r * (ch + rgap);
    box(s, x, y, cw, ch);
    s.addShape(pres.shapes.RECTANGLE, { x, y: y + 0.25, w: 0.06, h: ch - 0.5, fill: { color: PURPLE } });
    s.addText(rl[0], { x: x + 0.32, y: y + 0.28, w: cw - 0.55, h: 0.45, margin: 0, fontSize: 16, bold: true, color: WHITE, fontFace: FONT });
    s.addText(rl[1], { x: x + 0.32, y: y + 0.75, w: cw - 0.55, h: 0.6, margin: 0, fontSize: 13, color: LIGHT_GRAY, fontFace: FONT, lineSpacingMultiple: 1.12, valign: "top" });
  });
}

// =========================================================
// 16. START TODAY (CTA + close)
// =========================================================
s = pres.addSlide(); bg(s);
header(s, "Get started", "Start today");
const cmds = [
  ["“good morning”", "Your daily brief: active work, Slack, risks, next actions"],
  ["“run the marketing OS”", "An operating brief with priorities, owners, and evidence"],
  ["“create a task”", "A structured monday story, written for you"],
  ["“interview me”", "The AI extracts your knowledge straight into the repo"],
  ["“let's retro”", "Capture what we learned so the next run is better"]
];
{
  const y0 = 1.85, rh = 0.66, gap = 0.16;
  cmds.forEach((cm, i) => {
    const y = y0 + i * (rh + gap);
    box(s, ML, y, 7.4, rh, { fill: i === 0 ? MID_GRAY : DARK_GRAY });
    s.addText(cm[0], { x: ML + 0.3, y, w: 3.1, h: rh, margin: 0, fontSize: 15, bold: true, color: PURPLE, fontFace: FONT, valign: "middle" });
    s.addText(cm[1], { x: ML + 3.4, y, w: 3.85, h: rh, margin: 0, fontSize: 12, color: LIGHT_GRAY, fontFace: FONT, valign: "middle", lineSpacingMultiple: 1.0 });
  });
}
// right: the ask
box(s, 8.7, 1.85, 3.93, 4.0, { fill: MID_GRAY, border: PURPLE, shadow: true });
pill(s, "The one ask", 9.0, 2.15, 1.9);
s.addText("Each of us writes or improves one system doc this month.", { x: 9.0, y: 2.7, w: 3.4, h: 1.0, margin: 0, fontSize: 19, bold: true, color: WHITE, fontFace: FONT, lineSpacingMultiple: 1.08, valign: "top" });
s.addText("That is the whole flywheel. Use it for real work, then teach it what you learned. The brain grows from there.", { x: 9.0, y: 4.1, w: 3.4, h: 1.5, margin: 0, fontSize: 13.5, color: LIGHT_GRAY, fontFace: FONT, lineSpacingMultiple: 1.2, valign: "top" });
s.addShape(pres.shapes.RECTANGLE, { x: ML, y: 6.35, w: 1.5, h: 0.045, fill: { color: PURPLE } });
s.addText("One team. One brain. Compounding every week.", { x: ML, y: 6.55, w: CW, h: 0.5, margin: 0, fontSize: 18, bold: true, color: WHITE, fontFace: FONT });

// ---- write ----
const out = "Riverside-Marketing-OS.pptx";
pres.writeFile({ fileName: out }).then(() => console.log("WROTE " + out)).catch(e => { console.error(e); process.exit(1); });
