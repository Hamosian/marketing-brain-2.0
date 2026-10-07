const pptxgen = require("pptxgenjs");

const PURPLE = "7C5CFF";
const NEAR_BLACK = "0F0F14";
const WHITE = "FFFFFF";
const DARK_GRAY = "1C1C24";
const MID_GRAY = "2A2A35";
const LIGHT_GRAY = "E6E6EB";
const DIM = "9B9BA8";
const STROKE = "4A4A58";
const FONT = "Instrument Sans";

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.33 x 7.5
pres.author = "Riverside Marketing";
pres.title = "Marketing OS, how the system works";

const W = 13.33;

function darkSlide(title, subtitle) {
  const s = pres.addSlide();
  s.background = { color: NEAR_BLACK };
  // corner dot motif
  s.addShape(pres.shapes.OVAL, { x: 12.86, y: 0.42, w: 0.13, h: 0.13, fill: { color: PURPLE } });
  if (title) {
    s.addText(title, { x: 0.5, y: 0.3, w: 11.8, h: 0.55, fontSize: 26, bold: true, color: WHITE, fontFace: FONT, margin: 0 });
  }
  if (subtitle) {
    s.addText(subtitle, { x: 0.5, y: 0.88, w: 12.3, h: 0.38, fontSize: 12.5, color: LIGHT_GRAY, fontFace: FONT, margin: 0 });
  }
  return s;
}

function panel(s, x, y, w, h) {
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x, y, w, h, rectRadius: 0.08,
    fill: { color: DARK_GRAY }, line: { color: MID_GRAY, width: 1 },
  });
}

function chip(s, x, y, w, h, text, opts = {}) {
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x, y, w, h, rectRadius: 0.06,
    fill: { color: opts.hot ? "2A2347" : MID_GRAY },
    line: { color: opts.hot ? PURPLE : STROKE, width: opts.hot ? 1.25 : 0.75 },
  });
  if (Array.isArray(text)) {
    s.addText(text, { x, y, w, h, align: "center", valign: "middle", fontFace: FONT, margin: 0 });
  } else {
    s.addText(text, { x, y, w, h, align: "center", valign: "middle", fontSize: opts.fontSize || 12, color: opts.color || WHITE, fontFace: FONT, margin: 0 });
  }
}

function arrowRight(s, x, y, w, opts = {}) {
  s.addShape(pres.shapes.LINE, { x, y, w, h: 0, line: { color: opts.color || STROKE, width: 1.75, endArrowType: "triangle" } });
}
function arrowLeft(s, x, y, w, opts = {}) {
  s.addShape(pres.shapes.LINE, { x, y, w, h: 0, line: { color: opts.color || STROKE, width: 1.75, beginArrowType: "triangle" } });
}
function arrowDown(s, x, y, h, opts = {}) {
  s.addShape(pres.shapes.LINE, { x, y, w: 0, h, line: { color: opts.color || STROKE, width: 1.75, endArrowType: "triangle" } });
}
function arrowUp(s, x, y, h, opts = {}) {
  s.addShape(pres.shapes.LINE, { x, y, w: 0, h, line: { color: opts.color || STROKE, width: 1.75, beginArrowType: "triangle" } });
}
function plainLine(s, x, y, w, h, opts = {}) {
  s.addShape(pres.shapes.LINE, { x, y, w, h, line: { color: opts.color || STROKE, width: 1.75 } });
}

function numCircle(s, x, y, n) {
  s.addShape(pres.shapes.OVAL, { x, y, w: 0.36, h: 0.36, fill: { color: NEAR_BLACK }, line: { color: PURPLE, width: 1.5 } });
  s.addText(String(n), { x, y: y - 0.01, w: 0.36, h: 0.36, align: "center", valign: "middle", fontSize: 13, bold: true, color: PURPLE, fontFace: FONT, margin: 0 });
}

// ---------------------------------------------------------------- slide 1: cover
{
  const s = pres.addSlide();
  s.background = { color: NEAR_BLACK };
  s.addImage({ path: "riverside-logo-white.png", x: 0.5, y: 0.45, w: 2.1, h: 0.5 });
  s.addText("The Marketing OS", { x: 0.5, y: 2.75, w: 11.5, h: 0.95, fontSize: 46, bold: true, color: WHITE, fontFace: FONT, charSpacing: -0.5, margin: 0 });
  s.addText("How the marketing brain works: architecture, data flow, and the learning loop", {
    x: 0.5, y: 3.78, w: 10.5, h: 0.45, fontSize: 19, color: LIGHT_GRAY, fontFace: FONT, margin: 0,
  });
  s.addText([
    { text: "Riverside Marketing", options: { color: PURPLE, bold: true } },
    { text: "   Jul 2026   Source of truth: the marketing-brain repo", options: { color: DIM } },
  ], { x: 0.5, y: 6.65, w: 11, h: 0.35, fontSize: 12, fontFace: FONT, margin: 0 });
  s.addShape(pres.shapes.OVAL, { x: 12.86, y: 0.42, w: 0.13, h: 0.13, fill: { color: PURPLE } });
}

// ---------------------------------------------------------------- slide 2: at a glance
{
  const s = darkSlide(
    "The platform at a glance",
    "Four stages, one direction of flow, one loop back: the team talks to Claude, Claude loads the brain, the agents act on live systems"
  );

  const py = 1.45, ph = 4.6;

  // Team panel
  panel(s, 0.5, py, 2.7, ph);
  s.addText("Marketing team", { x: 0.5, y: py + 0.12, w: 2.7, h: 0.3, align: "center", fontSize: 14.5, bold: true, color: WHITE, fontFace: FONT, margin: 0 });
  chip(s, 0.65, 2.85, 2.4, 0.42, "Claude Code");
  chip(s, 0.65, 3.43, 2.4, 0.42, "claude.ai and Cowork");
  chip(s, 0.65, 4.01, 2.4, 0.42, "Claude in Chrome");

  // Brain panel
  panel(s, 3.7, py, 2.7, ph);
  s.addText("The brain (this repo)", { x: 3.7, y: py + 0.12, w: 2.7, h: 0.3, align: "center", fontSize: 14.5, bold: true, color: WHITE, fontFace: FONT, margin: 0 });
  chip(s, 3.85, 2.0, 2.4, 0.6, [
    { text: "CLAUDE.md", options: { fontSize: 12, bold: true, color: WHITE, breakLine: true } },
    { text: "the map, always loaded", options: { fontSize: 9.5, color: LIGHT_GRAY } },
  ], { hot: true });
  chip(s, 3.85, 2.76, 2.4, 0.42, "references/  (IDs, contacts)");
  chip(s, 3.85, 3.34, 2.4, 0.42, "systems/  (architecture)");
  chip(s, 3.85, 3.92, 2.4, 0.42, "skill knowledge/  (deep refs)");
  chip(s, 3.85, 4.5, 2.4, 0.42, "graphify knowledge graph");

  // Agents panel
  panel(s, 6.9, py, 2.7, ph);
  s.addText("The agents", { x: 6.9, y: py + 0.12, w: 2.7, h: 0.3, align: "center", fontSize: 14.5, bold: true, color: WHITE, fontFace: FONT, margin: 0 });
  s.addText("ROUTING LAYER", { x: 6.9, y: 1.95, w: 2.7, h: 0.25, align: "center", fontSize: 9.5, bold: true, color: PURPLE, charSpacing: 2, fontFace: FONT, margin: 0 });
  chip(s, 7.05, 2.22, 2.4, 0.4, "/marketing-brain router", { hot: true });
  chip(s, 7.05, 2.74, 2.4, 0.58, [
    { text: "12 skill agents", options: { fontSize: 12, color: WHITE, breakLine: true } },
    { text: "own live system access", options: { fontSize: 9.5, color: LIGHT_GRAY } },
  ]);
  arrowDown(s, 8.25, 3.4, 0.24);
  s.addText("SPECIALIST LAYER", { x: 6.9, y: 3.7, w: 2.7, h: 0.25, align: "center", fontSize: 9.5, bold: true, color: PURPLE, charSpacing: 2, fontFace: FONT, margin: 0 });
  chip(s, 7.05, 3.97, 2.4, 0.78, [
    { text: "29 deep-dive subagents", options: { fontSize: 12, color: WHITE, breakLine: true } },
    { text: "paid, SEO, content, email, podcast, PR, growth", options: { fontSize: 9.5, color: LIGHT_GRAY, breakLine: true } },
    { text: "no live access", options: { fontSize: 9.5, italic: true, color: DIM } },
  ]);

  // Live systems panel
  panel(s, 10.1, py, 2.7, ph);
  s.addText("Live systems", { x: 10.1, y: py + 0.12, w: 2.7, h: 0.3, align: "center", fontSize: 14.5, bold: true, color: WHITE, fontFace: FONT, margin: 0 });
  const liveItems = ["HubSpot", "Omni BI + Snowflake", "monday.com", "Slack", "Ad platforms", "Webflow site"];
  liveItems.forEach((t, i) => chip(s, 10.25, 2.0 + i * 0.56, 2.4, 0.42, t));

  // forward arrows + labels
  const midY = 3.75;
  s.addText("uses", { x: 3.2, y: 3.4, w: 0.5, h: 0.26, align: "center", fontSize: 9, color: DIM, fontFace: FONT, margin: 0 });
  arrowRight(s, 3.22, midY, 0.46);
  s.addText("routes", { x: 6.4, y: 3.4, w: 0.5, h: 0.26, align: "center", fontSize: 9, color: DIM, fontFace: FONT, margin: 0 });
  arrowRight(s, 6.42, midY, 0.46);
  s.addText("acts on", { x: 9.6, y: 3.4, w: 0.5, h: 0.26, align: "center", fontSize: 9, color: DIM, fontFace: FONT, margin: 0 });
  arrowRight(s, 9.62, midY, 0.46);

  // learning loop back (agents -> brain)
  plainLine(s, 8.25, 6.05, 0, 0.4, { color: PURPLE });
  plainLine(s, 5.05, 6.45, 3.2, 0, { color: PURPLE });
  arrowUp(s, 5.05, 6.09, 0.36, { color: PURPLE });
  s.addText("/retro opens PRs, knowledge compounds", { x: 3.5, y: 6.52, w: 6.3, h: 0.3, align: "center", fontSize: 11, bold: true, color: PURPLE, fontFace: FONT, margin: 0 });

  s.addText("Around this flow: CI lint on every PR, doc-agent wiki and graph sync on every merge, scheduled cloud routines with no human at the keyboard.", {
    x: 0.5, y: 7.02, w: 12.3, h: 0.32, fontSize: 10.5, color: DIM, fontFace: FONT, margin: 0,
  });
}

// ---------------------------------------------------------------- slide 3: request end to end
{
  const s = darkSlide(
    "A request, end to end",
    "What happens when someone asks the Marketing OS a broad question"
  );

  const steps = [
    ["Classify", "/marketing-brain reads the request and picks the path"],
    ["Load scoped context", "the CLAUDE.md map plus only the relevant docs"],
    ["Delegate", "to the skill agent that owns the domain, e.g. /data-agent"],
    ["Pull live data", "MCP into HubSpot, Omni, monday, Slack, ad platforms"],
    ["Specialist deep pass", "domain analysis on the data, no live access needed"],
    ["Synthesize and close", "decision, owner, evidence, next action"],
  ];
  const cw = 3.7, ch = 1.5;
  const xs = [0.5, 4.82, 9.13];
  const rowY = [1.6, 3.65];

  // row 1: steps 1-3 left to right
  for (let i = 0; i < 3; i++) {
    const x = xs[i], y = rowY[0];
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w: cw, h: ch, rectRadius: 0.08, fill: { color: DARK_GRAY }, line: { color: MID_GRAY, width: 1 } });
    numCircle(s, x + 0.2, y + 0.2, i + 1);
    s.addText(steps[i][0], { x: x + 0.7, y: y + 0.17, w: cw - 0.9, h: 0.35, fontSize: 14.5, bold: true, color: WHITE, fontFace: FONT, margin: 0 });
    s.addText(steps[i][1], { x: x + 0.7, y: y + 0.56, w: cw - 0.9, h: 0.8, fontSize: 11.5, color: LIGHT_GRAY, fontFace: FONT, margin: 0 });
  }
  arrowRight(s, 4.28, rowY[0] + ch / 2, 0.46);
  arrowRight(s, 8.59, rowY[0] + ch / 2, 0.46);
  // down from step 3 to step 4
  arrowDown(s, xs[2] + cw / 2, rowY[0] + ch, rowY[1] - rowY[0] - ch);

  // row 2: steps 4-6, positions right to left
  const order2 = [
    { idx: 3, x: xs[2] },
    { idx: 4, x: xs[1] },
    { idx: 5, x: xs[0] },
  ];
  for (const { idx, x } of order2) {
    const y = rowY[1];
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w: cw, h: ch, rectRadius: 0.08, fill: { color: DARK_GRAY }, line: { color: MID_GRAY, width: 1 } });
    numCircle(s, x + 0.2, y + 0.2, idx + 1);
    s.addText(steps[idx][0], { x: x + 0.7, y: y + 0.17, w: cw - 0.9, h: 0.35, fontSize: 14.5, bold: true, color: WHITE, fontFace: FONT, margin: 0 });
    s.addText(steps[idx][1], { x: x + 0.7, y: y + 0.56, w: cw - 0.9, h: 0.8, fontSize: 11.5, color: LIGHT_GRAY, fontFace: FONT, margin: 0 });
  }
  arrowLeft(s, 8.59, rowY[1] + ch / 2, 0.46);
  arrowLeft(s, 4.28, rowY[1] + ch / 2, 0.46);

  // rules callout
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.5, y: 5.6, w: 12.33, h: 1.3, rectRadius: 0.08, fill: { color: "2A2347" }, line: { color: PURPLE, width: 1 } });
  s.addText([
    { text: "Safety rule:  ", options: { bold: true, color: PURPLE } },
    { text: "any mutating write along the way (HubSpot changes, monday updates, Slack sends) pauses for human approval first, unless a specific automation skill was invoked.", options: { color: WHITE, breakLine: true } },
    { text: "Data rule:  ", options: { bold: true, color: PURPLE } },
    { text: "data questions go to Rivermind first; the skill agent only falls back to direct Omni or Snowflake when Rivermind lacks coverage.", options: { color: WHITE } },
  ], { x: 0.8, y: 5.75, w: 11.73, h: 1.0, fontSize: 12.5, fontFace: FONT, valign: "top", paraSpaceAfter: 6, margin: 0 });
}

// ---------------------------------------------------------------- slide 4: progressive disclosure
{
  const s = darkSlide(
    "Progressive disclosure, what loads when",
    "The brain is a map, not a library: a session starts with one file and pulls depth only when the task needs it"
  );

  const tiers = [
    ["ALWAYS LOADED", "CLAUDE.md", "Team identity, task routing tables, directives, pointers to everything else."],
    ["ON DEMAND", "references/  (team, boards, Slack, messaging)   systems/owned/   systems/reference/", "Loaded when a task mentions the system, without being asked."],
    ["ON TRIGGER", ".claude/skills/  (61 skills)   .claude/agents/  (specialist subagents)", "A skill's SKILL.md loads only when its trigger fires or the router delegates to it."],
    ["DEEP, IN A SKILL", "skills/*/knowledge/*.md", "Heavy reference content a skill pulls mid-run: queries, field dictionaries, configs."],
  ];
  tiers.forEach((t, i) => {
    const y = 1.55 + i * 1.32;
    const hot = i === 0;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.5, y, w: 12.33, h: 1.12, rectRadius: 0.08, fill: { color: hot ? "2A2347" : DARK_GRAY }, line: { color: hot ? PURPLE : MID_GRAY, width: 1 } });
    s.addText(t[0], { x: 0.8, y: y + 0.14, w: 2.2, h: 0.85, fontSize: 10.5, bold: true, color: PURPLE, charSpacing: 1.5, valign: "middle", fontFace: FONT, margin: 0 });
    s.addText(t[1], { x: 3.2, y: y + 0.16, w: 9.4, h: 0.42, fontSize: 13.5, bold: true, color: WHITE, fontFace: FONT, margin: 0 });
    s.addText(t[2], { x: 3.2, y: y + 0.6, w: 9.4, h: 0.4, fontSize: 11.5, color: LIGHT_GRAY, fontFace: FONT, margin: 0 });
  });

  s.addText("Result: sessions start instant, context stays scoped, and 61 skills can coexist without drowning the router.", {
    x: 0.5, y: 6.95, w: 12.3, h: 0.35, fontSize: 11, color: DIM, fontFace: FONT, margin: 0,
  });
}

// ---------------------------------------------------------------- slide 5: flywheel
{
  const s = darkSlide(
    "The learning flywheel",
    "What turns a context repo into a compounding brain: every learning is a reviewed pull request, never tribal memory"
  );

  const boxes = [
    ["1", "Run a task with the brain", "any skill, any session"],
    ["2", "A non-obvious learning surfaces", "platform quirk, missing step, gotcha"],
    ["3", "/retro captures and routes it", "to the right file: system, skill, reference"],
    ["4", "PR review, the human gate", "CI lint checks structure on every PR"],
    ["5", "Merge to main", "doc-agent syncs the wiki and the graph"],
    ["6", "Next session loads a smarter brain", "for the whole team, not one person"],
  ];
  const bw = 3.6, bh = 1.25;
  const xs = [0.6, 4.87, 9.13];
  const yTop = 1.85, yBot = 4.1;

  const drawBox = (b, x, y, hot) => {
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w: bw, h: bh, rectRadius: 0.08, fill: { color: hot ? "2A2347" : DARK_GRAY }, line: { color: hot ? PURPLE : MID_GRAY, width: 1 } });
    numCircle(s, x + 0.18, y + 0.18, b[0]);
    s.addText(b[1], { x: x + 0.66, y: y + 0.15, w: bw - 0.85, h: 0.62, fontSize: 13, bold: true, color: WHITE, fontFace: FONT, margin: 0 });
    s.addText(b[2], { x: x + 0.66, y: y + 0.78, w: bw - 0.85, h: 0.4, fontSize: 10.5, color: LIGHT_GRAY, fontFace: FONT, margin: 0 });
  };

  drawBox(boxes[0], xs[0], yTop, false);
  drawBox(boxes[1], xs[1], yTop, false);
  drawBox(boxes[2], xs[2], yTop, true);
  drawBox(boxes[3], xs[2], yBot, false);
  drawBox(boxes[4], xs[1], yBot, false);
  drawBox(boxes[5], xs[0], yBot, true);

  arrowRight(s, xs[0] + bw, yTop + bh / 2, xs[1] - xs[0] - bw);
  arrowRight(s, xs[1] + bw, yTop + bh / 2, xs[2] - xs[1] - bw);
  arrowDown(s, xs[2] + bw / 2, yTop + bh, yBot - yTop - bh);
  arrowLeft(s, xs[1] + bw, yBot + bh / 2, xs[2] - xs[1] - bw);
  arrowLeft(s, xs[0] + bw, yBot + bh / 2, xs[1] - xs[0] - bw);
  arrowUp(s, xs[0] + bw / 2, yTop + bh, yBot - yTop - bh, { color: PURPLE });

  s.addText([
    { text: "The rule that keeps it honest:  ", options: { bold: true, color: PURPLE } },
    { text: "team and system knowledge goes to the repo via PR. Personal memory holds only individual preferences. If it would help a teammate, it never stays in one head.", options: { color: LIGHT_GRAY } },
  ], { x: 0.6, y: 5.85, w: 12.1, h: 0.75, fontSize: 12.5, fontFace: FONT, margin: 0 });
}

// ---------------------------------------------------------------- slide 6: operating state
{
  const s = darkSlide(
    "Operating state, how work moves",
    "Every piece of work the OS touches moves through one state loop, from intake to a captured learning"
  );

  const states = [
    ["intake", 1.1],
    ["triaged", 1.2],
    ["planned", 1.25],
    ["executing", 1.3],
    ["ready for review", 1.8],
    ["shipped", 1.2],
    ["measured", 1.3],
    ["learned", 1.2],
  ];
  const gap = 0.26;
  const totalW = states.reduce((a, [, w]) => a + w, 0) + gap * (states.length - 1);
  let x = (W - totalW) / 2;
  const py = 3.35, ph = 0.52;
  const centers = [];
  states.forEach(([label, w], i) => {
    const hot = label === "learned";
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: py, w, h: ph, rectRadius: 0.26, fill: { color: hot ? "2A2347" : MID_GRAY }, line: { color: hot ? PURPLE : STROKE, width: hot ? 1.25 : 0.75 } });
    s.addText(label, { x, y: py, w, h: ph, align: "center", valign: "middle", fontSize: 12, color: WHITE, fontFace: FONT, margin: 0 });
    centers.push(x + w / 2);
    if (i < states.length - 1) arrowRight(s, x + w, py + ph / 2, gap);
    x += w + gap;
  });

  // investigating branch above, between triaged and planned
  const invW = 1.6, invX = (centers[1] + centers[2]) / 2 - invW / 2, invY = 2.25;
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: invX, y: invY, w: invW, h: 0.5, rectRadius: 0.25, fill: { color: MID_GRAY }, line: { color: STROKE, width: 0.75 } });
  s.addText("investigating", { x: invX, y: invY, w: invW, h: 0.5, align: "center", valign: "middle", fontSize: 12, color: WHITE, fontFace: FONT, margin: 0 });
  // triaged -> investigating (vertical, head at investigating)
  arrowUp(s, centers[1] + 0.18, invY + 0.5, py - invY - 0.5);
  // investigating -> planned (vertical, head at planned)
  arrowDown(s, centers[2] - 0.14, invY + 0.5, py - invY - 0.5);
  s.addText("evidence needed", { x: invX - 1.9, y: invY + 0.05, w: 1.8, h: 0.3, align: "right", fontSize: 9.5, color: DIM, fontFace: FONT, margin: 0 });

  // blocked branch below executing
  const blkW = 1.3, blkX = centers[3] - blkW / 2, blkY = 4.55;
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: blkX, y: blkY, w: blkW, h: 0.5, rectRadius: 0.25, fill: { color: MID_GRAY }, line: { color: STROKE, width: 0.75 } });
  s.addText("blocked", { x: blkX, y: blkY, w: blkW, h: 0.5, align: "center", valign: "middle", fontSize: 12, color: WHITE, fontFace: FONT, margin: 0 });
  arrowDown(s, centers[3] - 0.18, py + ph, blkY - py - ph);
  arrowUp(s, centers[3] + 0.18, py + ph, blkY - py - ph);
  s.addText("dependency or decision needed", { x: blkX + blkW + 0.15, y: blkY + 0.1, w: 3.0, h: 0.3, fontSize: 9.5, color: DIM, fontFace: FONT, margin: 0 });

  // loop back learned -> intake
  const loopY = 1.7;
  plainLine(s, centers[7], loopY, 0, py - loopY, { color: PURPLE });
  plainLine(s, centers[0], loopY, centers[7] - centers[0], 0, { color: PURPLE });
  arrowDown(s, centers[0], loopY, py - loopY - 0.04, { color: PURPLE });
  s.addText("learnings feed the next intake", { x: 3.5, y: 1.32, w: 6.3, h: 0.3, align: "center", fontSize: 11, bold: true, color: PURPLE, fontFace: FONT, margin: 0 });

  s.addText("Triaged work goes straight to planned when scope is clear, or through investigating when evidence is needed. Executing can bounce through blocked and back. Nothing is done until the learning is captured.", {
    x: 0.6, y: 5.85, w: 12.1, h: 0.7, fontSize: 12, color: LIGHT_GRAY, fontFace: FONT, margin: 0,
  });
}

// ---------------------------------------------------------------- slide 7: autonomy today
{
  const s = darkSlide(
    "Autonomy today",
    "Prove a workflow with a human at the keyboard, then graduate it to a schedule"
  );

  const header = [
    { text: "Mode", options: { bold: true, color: WHITE, fill: { color: MID_GRAY } } },
    { text: "What runs", options: { bold: true, color: WHITE, fill: { color: MID_GRAY } } },
    { text: "Examples", options: { bold: true, color: WHITE, fill: { color: MID_GRAY } } },
  ];
  const cell = (t, opts = {}) => ({ text: t, options: { color: LIGHT_GRAY, fill: { color: DARK_GRAY }, ...opts } });
  const rows = [
    header,
    [
      cell("Assistive\nhuman at the keyboard", { bold: true, color: WHITE }),
      cell("Skills invoked in Claude Code, claude.ai, or Chrome. Mutating writes ask for approval."),
      cell("/marketing-brain, /good-morning, /pm-story, /page-cro, /nir-monthly-report"),
    ],
    [
      cell("Autonomous\nscheduled cloud routines", { bold: true, color: WHITE }),
      cell("Proven skills running on a schedule with no human in the loop."),
      cell("/nir-mql-live-report daily, /invoice-inbox-to-monday weekly, /access-welcome daily"),
    ],
    [
      cell("Autonomous\non repo events", { bold: true, color: WHITE }),
      cell("Automation that keeps the brain itself healthy."),
      cell("CI lint on every PR, doc-agent wiki and graph sync on every merge"),
    ],
  ];
  s.addTable(rows, {
    x: 0.5, y: 1.7, w: 12.33, colW: [3.1, 4.9, 4.33],
    border: { pt: 1, color: MID_GRAY },
    fontFace: FONT, fontSize: 12.5,
    valign: "middle",
    rowH: [0.5, 1.15, 1.15, 1.15],
    margin: 0.12,
  });

  s.addText("This is the same arc R&D's ATA platform formalizes as assistive to autonomous: the Marketing OS runs it on managed Claude infrastructure instead of an owned runtime.", {
    x: 0.5, y: 6.5, w: 12.3, h: 0.6, fontSize: 11.5, color: DIM, fontFace: FONT, margin: 0,
  });
}

// ---------------------------------------------------------------- slide 8: what each team leader gets
{
  const s = darkSlide(
    "What each team leader gets",
    "The system is shared, the payoff is personal. Live use cases, not a roadmap: every skill named here exists in the repo today"
  );

  const leaders = [
    ["VP MARKETING", "Abel Grünfeld",
      ["One operating brief: /marketing-brain", "Attribution via /rivermind:ask"],
      "Memory that survives turnover"],
    ["GROWTH MARKETING", "Nir Taranto",
      ["Monthly report + daily MQL DM run themselves", "Paid audits, /page-cro, SEO agent"],
      "Reporting without the data pulls"],
    ["BRAND", "Raz Messing",
      ["Every deck and page on brand by default", "Design tokens in every build task"],
      "Executable guidelines, zero policing"],
    ["MARKETING: PMM + CONTENT", "Sivan Mazuz",
      ["Messaging + VoC in every copy task", "Customer language from Gong on tap"],
      "One source of truth for positioning"],
    ["PAID ACQUISITION", "Raz Navon",
      ["Live channel access, 250+ check audits", "Brand DNA, copy, and ad-image skills"],
      "Full-account audits in hours"],
    ["GROWTH CHANNELS", "Dor Druker",
      ["/campaign-agent runs cross-channel tests", "/rivermind:ask answers channel questions"],
      "New channels tested at solo speed"],
    ["CREATOR MARKETING", "Savion Ron Shemesh",
      ["Podcast, video, and social specialists on tap", "Creator briefs on brand by default"],
      "Creator content shipped and measured"],
    ["MARKETING OPERATIONS", "Hanan Amos",
      ["/mops-standup, /hubspot-workflow-qa", "Invoice filing runs as a weekly routine"],
      "Ops chores automated, QA guardrails"],
  ];

  const cw = 2.89, ch = 2.55, gapX = 0.25;
  const ys = [1.5, 4.3];
  leaders.forEach((L, i) => {
    const x = 0.5 + (i % 4) * (cw + gapX), y = ys[Math.floor(i / 4)];
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w: cw, h: ch, rectRadius: 0.08, fill: { color: DARK_GRAY }, line: { color: MID_GRAY, width: 1 } });
    s.addText(L[0], { x: x + 0.2, y: y + 0.16, w: cw - 0.4, h: 0.22, fontSize: 8, bold: true, color: PURPLE, charSpacing: 1.2, fontFace: FONT, margin: 0 });
    s.addText(L[1], { x: x + 0.2, y: y + 0.4, w: cw - 0.4, h: 0.3, fontSize: 13, bold: true, color: WHITE, fontFace: FONT, margin: 0 });
    s.addText([
      { text: L[2][0], options: { bullet: true, breakLine: true } },
      { text: L[2][1], options: { bullet: true } },
    ], { x: x + 0.2, y: y + 0.76, w: cw - 0.36, h: 1.05, fontSize: 9.5, color: LIGHT_GRAY, fontFace: FONT, paraSpaceAfter: 4, margin: 0 });
    s.addShape(pres.shapes.LINE, { x: x + 0.2, y: y + 1.9, w: cw - 0.4, h: 0, line: { color: MID_GRAY, width: 0.75 } });
    s.addText([
      { text: "Payoff:  ", options: { bold: true, color: PURPLE } },
      { text: L[3], options: { color: LIGHT_GRAY } },
    ], { x: x + 0.2, y: y + 1.98, w: cw - 0.4, h: 0.52, fontSize: 9, fontFace: FONT, margin: 0 });
  });
}

// ---------------------------------------------------------------- slide 9: why teams pick it
{
  const s = darkSlide(
    "Why teams pick it",
    "The four properties that make the brain worth adopting, whatever your sub-org runs"
  );

  const benefits = [
    ["It compounds", "Every task makes the next one faster. Learnings land as reviewed PRs, so knowledge belongs to the team, not one person's memory."],
    ["Guardrails built in", "Writes to HubSpot, monday, and Slack ask a human first. Data answers come from the analytics team's validated Rivermind layer."],
    ["Day-one onboarding", "A new teammate opens Claude in the repo and it already knows the boards, channels, systems, and conventions."],
    ["Nothing to host", "Plain markdown on managed Claude infrastructure. No runtime to operate, no vendor lock beyond the docs themselves."],
  ];
  const bw = 2.93, bh = 2.6, gap = 0.2;
  benefits.forEach((B, i) => {
    const x = 0.5 + i * (bw + gap), y = 2.1;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w: bw, h: bh, rectRadius: 0.08, fill: { color: DARK_GRAY }, line: { color: MID_GRAY, width: 1 } });
    s.addText(String(i + 1), { x: x + 0.25, y: y + 0.22, w: 1.0, h: 0.55, fontSize: 30, bold: true, color: PURPLE, fontFace: FONT, margin: 0 });
    s.addText(B[0], { x: x + 0.25, y: y + 0.85, w: bw - 0.5, h: 0.35, fontSize: 15, bold: true, color: WHITE, fontFace: FONT, margin: 0 });
    s.addText(B[1], { x: x + 0.25, y: y + 1.26, w: bw - 0.5, h: 1.2, fontSize: 10.5, color: LIGHT_GRAY, fontFace: FONT, margin: 0 });
  });

  s.addText([
    { text: "The pitch in one line:  ", options: { bold: true, color: PURPLE } },
    { text: "your team's best day becomes its default day, because everything learned is still there tomorrow.", options: { color: LIGHT_GRAY } },
  ], { x: 0.5, y: 5.3, w: 12.3, h: 0.4, fontSize: 13, fontFace: FONT, margin: 0 });
}

// ---------------------------------------------------------------- slide 10: where it lives
{
  const s = darkSlide("Where this lives", "Every version of these diagrams, and which one to trust");

  const items = [
    ["marketing-brain repo, README", "The architecture section renders these diagrams natively on GitHub. The repo is the source of truth."],
    ["docs/marketing-os-data-flow.html", "The Riverside-branded visual version, in the repo. Open locally in a browser."],
    ["GitHub wiki", "Generated mirror, auto-synced by the doc-agent on every merge. Never edited by hand."],
    ["Notion: The Marketing OS, how the system works", "Sibling of the Marketing Brain stakeholder quick start, formatted after R&D's ATA platform page."],
    ["docs/platform-integration.md", "Every MCP connector, skill, and ID wired end to end. The engineering-register version is docs/marketing-os-technical-architecture.md."],
  ];
  items.forEach((it, i) => {
    const y = 1.55 + i * 1.0;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.5, y, w: 12.33, h: 0.78, rectRadius: 0.08, fill: { color: DARK_GRAY }, line: { color: MID_GRAY, width: 1 } });
    s.addShape(pres.shapes.OVAL, { x: 0.78, y: y + 0.34, w: 0.14, h: 0.14, fill: { color: PURPLE } });
    s.addText(it[0], { x: 1.1, y: y + 0.1, w: 5.6, h: 0.62, fontSize: 13, bold: true, color: WHITE, valign: "middle", fontFace: FONT, margin: 0 });
    s.addText(it[1], { x: 6.8, y: y + 0.1, w: 5.85, h: 0.62, fontSize: 11, color: LIGHT_GRAY, valign: "middle", fontFace: FONT, margin: 0 });
  });

  s.addText([
    { text: "If a copy disagrees with the repo, ", options: { color: LIGHT_GRAY } },
    { text: "trust the repo and open a PR.", options: { bold: true, color: PURPLE } },
  ], { x: 0.5, y: 6.75, w: 12.3, h: 0.4, fontSize: 13, fontFace: FONT, margin: 0 });
}

pres.writeFile({ fileName: "marketing-os-how-it-works.pptx" }).then(() => console.log("written"));
