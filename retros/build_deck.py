"""
Riverside-branded Q1 FY26 Marketing Ops Retro deck (v2).
Combined data from MOps Tasks (6257866754) and Website Development (18397093471) boards.

Brand rules:
- Background: Near Black #0F0F14
- Accent: Riverside Purple #7C5CFF (lines, labels, highlights only)
- Typography: Inter
- No em dashes anywhere
"""

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

# Brand colors
PURPLE     = RGBColor(0x7C, 0x5C, 0xFF)
NEAR_BLACK = RGBColor(0x0F, 0x0F, 0x14)
WHITE      = RGBColor(0xFF, 0xFF, 0xFF)
DARK_GRAY  = RGBColor(0x1C, 0x1C, 0x24)
MID_GRAY   = RGBColor(0x2A, 0x2A, 0x35)
LIGHT_GRAY = RGBColor(0xE6, 0xE6, 0xEB)
GREEN      = RGBColor(0x4A, 0xDE, 0x80)
AMBER      = RGBColor(0xFB, 0xBF, 0x24)
PINK       = RGBColor(0xF4, 0x72, 0xB6)
TEAL       = RGBColor(0x2D, 0xD4, 0xBF)

FONT = "Inter"
OUT  = "/Users/hananamos/Team context brain/retros/2026-Q1-marketing-ops.pptx"

prs = Presentation()
prs.slide_width = Inches(13.33)
prs.slide_height = Inches(7.5)
BLANK = prs.slide_layouts[6]


# ---------- helpers ----------
def add_slide():
    s = prs.slides.add_slide(BLANK)
    fill = s.background.fill
    fill.solid()
    fill.fore_color.rgb = NEAR_BLACK
    return s


def add_rect(slide, x, y, w, h, fill_color, line_color=None):
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, w, h)
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_color
    if line_color is None:
        shape.line.fill.background()
    else:
        shape.line.color.rgb = line_color
        shape.line.width = Pt(0.75)
    shape.shadow.inherit = False
    return shape


def add_text(slide, x, y, w, h, text, *, size=14, bold=False, color=WHITE,
             align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, font=FONT):
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0)
    tf.margin_right = Inches(0)
    tf.margin_top = Inches(0)
    tf.margin_bottom = Inches(0)
    tf.vertical_anchor = anchor
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.name = font
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    return tb


def add_paragraphs(slide, x, y, w, h, lines, *, size=14, bold=False, color=WHITE,
                   align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, line_spacing=1.25,
                   bullet=False, font=FONT):
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0)
    tf.margin_right = Inches(0)
    tf.margin_top = Inches(0)
    tf.margin_bottom = Inches(0)
    tf.vertical_anchor = anchor
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.line_spacing = line_spacing
        run = p.add_run()
        run.text = (("•  " if bullet else "") + line) if line else ""
        run.font.name = font
        run.font.size = Pt(size)
        run.font.bold = bold
        run.font.color.rgb = color
    return tb


def slide_title(slide, title, *, accent=True):
    if accent:
        add_rect(slide, Inches(0.5), Inches(0.55), Inches(0.045), Inches(0.55), PURPLE)
    add_text(slide, Inches(0.65), Inches(0.45), Inches(11.5), Inches(0.7),
             title, size=30, bold=True, color=WHITE)
    add_text(slide, Inches(0.65), Inches(1.05), Inches(11.5), Inches(0.3),
             "Marketing Ops · Q1 FY26 Retro", size=10, color=PURPLE)


def corner_dot(slide):
    d = slide.shapes.add_shape(MSO_SHAPE.OVAL,
                               Inches(12.85), Inches(0.4),
                               Inches(0.12), Inches(0.12))
    d.fill.solid()
    d.fill.fore_color.rgb = PURPLE
    d.line.fill.background()


def page_footer(slide, num, total):
    add_text(slide, Inches(0.5), Inches(7.05), Inches(6), Inches(0.3),
             "Riverside Growth · Marketing Operations", size=9, color=LIGHT_GRAY)
    add_text(slide, Inches(11.0), Inches(7.05), Inches(1.83), Inches(0.3),
             f"{num} / {total}", size=9, color=LIGHT_GRAY, align=PP_ALIGN.RIGHT)


# ---------- slides ----------
slides_built = []


# Slide 1: Cover
def slide_cover():
    s = add_slide()
    add_text(s, Inches(0.6), Inches(0.55), Inches(4), Inches(0.5),
             "RIVERSIDE", size=18, bold=True, color=PURPLE)
    add_rect(s, Inches(0.6), Inches(3.6), Inches(1.4), Inches(0.04), PURPLE)
    add_text(s, Inches(0.6), Inches(2.6), Inches(12), Inches(1.0),
             "Q1 FY26 Retro", size=56, bold=True, color=WHITE)
    add_text(s, Inches(0.6), Inches(3.85), Inches(12), Inches(0.6),
             "Marketing Operations", size=26, color=LIGHT_GRAY)
    add_text(s, Inches(0.6), Inches(4.55), Inches(12), Inches(0.4),
             "Feb 1, 2026  to  Apr 30, 2026", size=14, color=LIGHT_GRAY)
    add_text(s, Inches(0.6), Inches(6.85), Inches(8), Inches(0.3),
             "Hanan Amos · Head of Marketing Operations", size=11, color=LIGHT_GRAY)
    return s

slides_built.append(slide_cover)


# Slide 2: Team
def slide_team():
    s = add_slide()
    slide_title(s, "The Team")
    corner_dot(s)
    add_text(s, Inches(0.65), Inches(1.55), Inches(12), Inches(0.5),
             "Three direct reports, plus four contracted contributors who delivered alongside us in Q1.",
             size=14, color=LIGHT_GRAY)

    # Three core team cards
    members = [
        ("Hanan Amos", "Head of Marketing Operations",
         "MOps lead, attribution strategy, AI tooling rollout, HubSpot architecture.", PURPLE),
        ("Jonathan Galili", "Marketing Operations",
         "Engineering side of MOps. Data integrations, HubSpot infrastructure, attribution pipelines, reporting.", TEAL),
        ("Yuval Tsabar", "Marketing Website",
         "riverside.com pages, A/B tests, accessibility, localization. Owns the Website Development board and #website-dev.", AMBER),
    ]
    card_w = Inches(4.0)
    card_h = Inches(2.6)
    margins = Inches(0.65)
    gap = Inches(0.15)
    top = Inches(2.2)
    for i, (n, r, b, accent) in enumerate(members):
        x = margins + (card_w + gap) * i
        add_rect(s, x, top, card_w, card_h, DARK_GRAY, MID_GRAY)
        add_rect(s, x, top, card_w, Inches(0.07), accent)
        add_text(s, x + Inches(0.3), top + Inches(0.3), card_w - Inches(0.6), Inches(0.5),
                 n, size=18, bold=True, color=WHITE)
        add_text(s, x + Inches(0.3), top + Inches(0.85), card_w - Inches(0.6), Inches(0.4),
                 r, size=12, bold=True, color=accent)
        add_text(s, x + Inches(0.3), top + Inches(1.3), card_w - Inches(0.6), Inches(1.2),
                 b, size=11, color=LIGHT_GRAY)

    # Contractors strip
    add_text(s, Inches(0.65), Inches(5.1), Inches(12), Inches(0.4),
             "Contributing contractors:", size=11, bold=True, color=PURPLE)
    add_text(s, Inches(0.65), Inches(5.45), Inches(12), Inches(0.4),
             "Davor · Milutin · Raphael Landau · Igor Suprun (77 shipped together)",
             size=14, color=WHITE)
    return s

slides_built.append(slide_team)


# Slide 3: TL;DR
def slide_tldr():
    s = add_slide()
    slide_title(s, "TL;DR")
    corner_dot(s)
    body_lines = [
        "Marketing Ops shipped 245 of 339 planned items in Q1, a 72% completion rate across two monday boards.",
        "",
        "Output came from a 3-person core team (223 shipped) plus 4 contracted contributors (77).",
        "",
        "The headline insight: 85% of all Q1 items were unplanned. The team is operating in heavily reactive mode.",
        "Closing the gap between 43 planned and 339 actual is the single most important Q2 question.",
        "",
        "94 items carry over into Q2, including 7 P0 / Urgent items.",
    ]
    add_paragraphs(s, Inches(0.65), Inches(1.7), Inches(12), Inches(5),
                   body_lines, size=18, color=WHITE, line_spacing=1.35)
    return s

slides_built.append(slide_tldr)


# Slide 4: By the Numbers
def slide_numbers():
    s = add_slide()
    slide_title(s, "By the Numbers")
    corner_dot(s)

    stats = [
        ("339", "items planned in Q1\n(across both boards)", LIGHT_GRAY),
        ("245", "shipped (72%)", PURPLE),
        ("87", "carrying into Q2", AMBER),
    ]
    block_w = Inches(3.9)
    gap = Inches(0.25)
    start_x = Inches(0.65)
    y = Inches(1.85)
    for i, (num, label, color) in enumerate(stats):
        x = start_x + (block_w + gap) * i
        add_rect(s, x, y, block_w, Inches(2.2), DARK_GRAY, MID_GRAY)
        add_text(s, x, y + Inches(0.35), block_w, Inches(1.3),
                 num, size=72, bold=True, color=color, align=PP_ALIGN.CENTER)
        add_text(s, x, y + Inches(1.55), block_w, Inches(0.55),
                 label, size=12, color=LIGHT_GRAY, align=PP_ALIGN.CENTER)

    # Per-board split row
    y2 = Inches(4.4)
    secondary = [
        ("MOps Tasks board", "193 items · 128 shipped (66%)"),
        ("Website Dev board", "146 items · 117 shipped (80%)"),
        ("Volume peak", "Feb 130 · Mar 121 · Apr 54"),
    ]
    for i, (left, right) in enumerate(secondary):
        x = start_x + (block_w + gap) * i
        add_rect(s, x, y2, block_w, Inches(1.3), DARK_GRAY, MID_GRAY)
        add_text(s, x + Inches(0.25), y2 + Inches(0.22), block_w - Inches(0.5), Inches(0.4),
                 left, size=13, bold=True, color=WHITE)
        add_text(s, x + Inches(0.25), y2 + Inches(0.7), block_w - Inches(0.5), Inches(0.4),
                 right, size=13, color=LIGHT_GRAY)

    add_text(s, Inches(0.65), Inches(6.0), Inches(12), Inches(0.4),
             "Sources: monday.com Marketing Operations Tasks board (6257866754) and Website Development board (18397093471), items with Q1 due dates.",
             size=10, color=LIGHT_GRAY)
    return s

slides_built.append(slide_numbers)


# Slide 5: Output by group
def slide_output_by_member():
    s = add_slide()
    slide_title(s, "Output by Group")
    corner_dot(s)

    data = [
        ("Core team (3)",   223, PURPLE),
        ("Contracted (4)",   77, MID_GRAY),
    ]
    max_v = max(v for _, v, _ in data)
    label_x = Inches(0.65)
    label_w = Inches(2.6)
    bar_x = Inches(3.35)
    bar_max_w = Inches(7.8)
    val_x = Inches(11.25)
    row_h = Inches(0.55)
    top = Inches(1.65)

    for i, (lab, v, color) in enumerate(data):
        y = top + row_h * i
        add_text(s, label_x, y + Inches(0.05), label_w, Inches(0.45),
                 lab, size=13, bold=(color == PURPLE), color=WHITE)
        add_rect(s, bar_x, y + Inches(0.13), bar_max_w, Inches(0.22), MID_GRAY)
        bar_w = Emu(int(bar_max_w * (v / max_v)))
        add_rect(s, bar_x, y + Inches(0.13), bar_w, Inches(0.22), color)
        add_text(s, val_x, y + Inches(0.05), Inches(1.5), Inches(0.45),
                 str(v), size=13, bold=True, color=WHITE)

    # Legend
    add_rect(s, Inches(0.65), Inches(5.85), Inches(0.18), Inches(0.18), PURPLE)
    add_text(s, Inches(0.95), Inches(5.82), Inches(3), Inches(0.25),
             "Direct reports", size=11, color=LIGHT_GRAY)
    add_rect(s, Inches(2.85), Inches(5.85), Inches(0.18), Inches(0.18), MID_GRAY)
    add_text(s, Inches(3.15), Inches(5.82), Inches(4), Inches(0.25),
             "Contracted contributors", size=11, color=LIGHT_GRAY)

    add_text(s, Inches(0.65), Inches(6.3), Inches(12), Inches(0.7),
             "The function delivered through a 3-person core plus 4 contracted contributors.",
             size=14, color=LIGHT_GRAY)
    return s

slides_built.append(slide_output_by_member)


# Slide 6: PLANNED vs UNPLANNED (the headline insight)
def slide_planned_vs_unplanned():
    s = add_slide()
    slide_title(s, "Planned vs Unplanned (Headline Insight)")
    corner_dot(s)

    add_text(s, Inches(0.65), Inches(1.55), Inches(12), Inches(0.5),
             "85% of all Q1 work was unplanned. The team is operating in a heavily reactive mode.",
             size=15, color=LIGHT_GRAY)

    # Two big stat blocks
    blocks = [
        ("43",  "PLANNED",   "13% · on the books before Q1\nor tagged Planned on Web Dev board", TEAL),
        ("287", "UNPLANNED", "85% · added in-flight during Q1",                                  AMBER),
    ]
    block_w = Inches(5.95)
    gap = Inches(0.25)
    start_x = Inches(0.65)
    y = Inches(2.35)
    for i, (num, label, sub, color) in enumerate(blocks):
        x = start_x + (block_w + gap) * i
        add_rect(s, x, y, block_w, Inches(2.5), DARK_GRAY, MID_GRAY)
        add_rect(s, x, y, block_w, Inches(0.07), color)
        add_text(s, x, y + Inches(0.3), block_w, Inches(1.3),
                 num, size=84, bold=True, color=color, align=PP_ALIGN.CENTER)
        add_text(s, x, y + Inches(1.5), block_w, Inches(0.4),
                 label, size=14, bold=True, color=color, align=PP_ALIGN.CENTER)
        add_paragraphs(s, x + Inches(0.5), y + Inches(1.95), block_w - Inches(1.0), Inches(0.5),
                       sub.split("\n"), size=10, color=LIGHT_GRAY, align=PP_ALIGN.CENTER, line_spacing=1.2)

    # Per-board breakdown
    add_text(s, Inches(0.65), Inches(5.1), Inches(12), Inches(0.35),
             "Per board:", size=11, bold=True, color=PURPLE)

    rows = [
        ("MOps Tasks board",      "Proxy: created before Feb 1",      "24 planned",  "169 unplanned (88%)"),
        ("Website Dev board",     "Native field: Planned?",           "19 planned",  "118 unplanned (81%)"),
    ]
    row_h = Inches(0.45)
    top = Inches(5.5)
    for i, (b, src, p, u) in enumerate(rows):
        y = top + row_h * i
        add_text(s, Inches(0.65), y, Inches(3),    Inches(0.35), b,   size=12, bold=True, color=WHITE)
        add_text(s, Inches(3.7),  y, Inches(3),    Inches(0.35), src, size=11, color=LIGHT_GRAY)
        add_text(s, Inches(7.0),  y, Inches(2.5),  Inches(0.35), p,   size=12, color=TEAL)
        add_text(s, Inches(9.6),  y, Inches(3),    Inches(0.35), u,   size=12, color=AMBER)

    add_text(s, Inches(0.65), Inches(6.55), Inches(12), Inches(0.5),
             "Closing this gap is the single most important Q2 question. Aim to shift toward 30/70 by end of Q2.",
             size=13, bold=True, color=PURPLE)
    return s

slides_built.append(slide_planned_vs_unplanned)


# Slide 7: Shipped breakdown by type (MOps board only - Web Dev has no Type column)
def slide_shipped_breakdown():
    s = add_slide()
    slide_title(s, "MOps Output by Type")
    corner_dot(s)

    add_text(s, Inches(0.65), Inches(1.55), Inches(12), Inches(0.45),
             "Marketing Operations Tasks board only. Website Dev board does not categorize by type.",
             size=11, color=LIGHT_GRAY)

    data = [
        ("Reporting / Dashboard", 23),
        ("Biz Process",           22),
        ("HubSpot",               19),
        ("Data Integration",      18),
        ("Website Related",       16),
        ("Issue / Bugs",          11),
        ("Messaging",              9),
        ("Website A/B Test",       4),
        ("Email Blast",            2),
        ("Attribution",            1),
    ]
    max_v = max(v for _, v in data)
    label_x = Inches(0.65)
    label_w = Inches(2.6)
    bar_x = Inches(3.35)
    bar_max_w = Inches(7.8)
    val_x = Inches(11.25)
    row_h = Inches(0.4)
    top = Inches(2.05)

    for i, (lab, v) in enumerate(data):
        y = top + row_h * i
        add_text(s, label_x, y + Inches(0.04), label_w, Inches(0.35),
                 lab, size=12, color=WHITE)
        add_rect(s, bar_x, y + Inches(0.1), bar_max_w, Inches(0.18), MID_GRAY)
        bar_w = Emu(int(bar_max_w * (v / max_v)))
        add_rect(s, bar_x, y + Inches(0.1), bar_w, Inches(0.18), PURPLE)
        add_text(s, val_x, y + Inches(0.04), Inches(1.5), Inches(0.35),
                 str(v), size=12, bold=True, color=WHITE)

    add_text(s, Inches(0.65), Inches(6.4), Inches(12), Inches(0.7),
             "Reporting and HubSpot together accounted for a third of MOps Tasks output. Web Dev added 117 more shipped items on top: page launches, A/B tests, localization, accessibility, security fixes.",
             size=12, color=LIGHT_GRAY)
    return s

slides_built.append(slide_shipped_breakdown)


# Section divider helper
def section_divider(title):
    def fn():
        s = add_slide()
        add_rect(s, Inches(5.92), Inches(3.0), Inches(1.5), Inches(0.04), PURPLE)
        add_text(s, Inches(0.5), Inches(3.2), Inches(12.33), Inches(0.9),
                 title, size=44, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
        return s
    return fn

slides_built.append(section_divider("Wins"))


# Slide 9: 7 wins (now includes Yuval-attributed wins)
def slide_wins():
    s = add_slide()
    slide_title(s, "7 Wins Worth Celebrating")
    corner_dot(s)

    wins = [
        ("01", "Self-Attribution Channel infra + weekly Slack report",
         "New HubSpot property auto-tags every Enterprise form fill. Weekly digest in #growth-marketing-leaders. (Hanan)"),
        ("02", "AI tooling rollout for the team",
         "Mixpanel and Omni added to Claude as MCP connectors. Brand skill, deck-builder skill. (Hanan)"),
        ("03", "HubSpot lifecycle and PLG framework",
         "PLG Lifecycle, framework rebuild, French welcome drip, ChiliPiper fix, Win-back segmentation. (Hanan, Jonathan)"),
        ("04", "Reporting depth",
         "Mixpanel A/B revamp, PPC dashboard template, Subscription cancellations, Newsletter, Organic traffic. (Jonathan, Hanan)"),
        ("05", "Localization expansion",
         "French marketing pages launched, DE locale fixed, German pricing page recovered, Israel pages added. (Yuval, Raphael)"),
        ("06", "Accessibility audit implementation",
         "Header, footer, product pages remediated for AA. Dedicated #website-accessibility channel. (Yuval, Raphael)"),
        ("07", "Operational reliability across the website",
         "PPC 404 alerts, Cloudfront triage, /plans-/pricing redirect, /de cleanups, security fix, navbar bug crush. (Yuval, Jonathan)"),
    ]
    y_start = Inches(1.55)
    row_h = Inches(0.78)
    for i, (num, head, body) in enumerate(wins):
        ry = y_start + row_h * i
        circ = s.shapes.add_shape(MSO_SHAPE.OVAL, Inches(0.65), ry, Inches(0.5), Inches(0.5))
        circ.fill.solid()
        circ.fill.fore_color.rgb = DARK_GRAY
        circ.line.color.rgb = PURPLE
        circ.line.width = Pt(1.25)
        add_text(s, Inches(0.65), ry, Inches(0.5), Inches(0.5),
                 num, size=12, bold=True, color=PURPLE,
                 align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        add_text(s, Inches(1.35), ry - Inches(0.02), Inches(11.6), Inches(0.35),
                 head, size=13, bold=True, color=WHITE)
        add_text(s, Inches(1.35), ry + Inches(0.32), Inches(11.6), Inches(0.42),
                 body, size=10.5, color=LIGHT_GRAY)
    return s

slides_built.append(slide_wins)


# Section: Misses & Stuck
slides_built.append(section_divider("Misses and Stuck Work"))


# Slide 11: P0 / Urgent carryovers (now includes Web Dev Urgent items)
def slide_p0_carryovers():
    s = add_slide()
    slide_title(s, "P0 / Urgent Carryovers into Q2")
    corner_dot(s)

    add_text(s, Inches(0.65), Inches(1.55), Inches(12), Inches(0.45),
             "Seven items entering Q2 with top-priority. Five are infrastructure or data-flow, two are urgent website assets.",
             size=12, color=LIGHT_GRAY)

    rows = [
        ("Working on it", "Website",      "Jonathan", "Cloudfront caching causing intermittent 404s",          "MOps · P0"),
        ("Working on it", "Data Int.",    "Jonathan", "iOS revenue data not displaying in AppsFlyer Analytics", "MOps · P0"),
        ("Working on it", "Data Int.",    "Jonathan", "Multi-account feature and HubSpot data flow",            "MOps · P0"),
        ("Test is Open",  "A/B Test",     "Jonathan", "Home LP A/B test",                                       "MOps · P0"),
        ("New",           "Biz Process",  "Hanan",    "Budget report process with Erika",                       "MOps · P0"),
        ("New",           "Web Asset",    "Yuval",    "Static Assets - Love & Labor",                           "Web · Urgent"),
        ("New",           "Web Asset",    "Yuval",    "Love and Labor: Birth certificate LP",                   "Web · Urgent"),
    ]
    top = Inches(2.1)
    col_x = [Inches(0.65), Inches(2.55), Inches(4.05), Inches(5.55), Inches(11.0)]
    headers = ["Status", "Type", "Owner", "Item", "Source"]
    add_rect(s, Inches(0.65), top, Inches(12.05), Inches(0.4), DARK_GRAY)
    for hx, htxt in zip(col_x, headers):
        add_text(s, hx, top + Inches(0.07), Inches(2), Inches(0.3),
                 htxt, size=11, bold=True, color=PURPLE)

    row_h = Inches(0.5)
    for i, r in enumerate(rows):
        ry = top + Inches(0.4) + row_h * i
        if i % 2 == 0:
            add_rect(s, Inches(0.65), ry, Inches(12.05), row_h, DARK_GRAY)
        status, ttype, owner, item, src = r
        status_color = AMBER if status == "Working on it" else (PINK if status == "Test is Open" else PURPLE)
        pill = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                                  col_x[0], ry + Inches(0.1), Inches(1.7), Inches(0.3))
        pill.fill.solid()
        pill.fill.fore_color.rgb = NEAR_BLACK
        pill.line.color.rgb = status_color
        pill.line.width = Pt(1.0)
        pill.adjustments[0] = 0.5
        add_text(s, col_x[0], ry + Inches(0.1), Inches(1.7), Inches(0.3),
                 status, size=9, bold=True, color=status_color,
                 align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        add_text(s, col_x[1], ry + Inches(0.13), Inches(1.5), Inches(0.34),
                 ttype, size=11, color=WHITE)
        add_text(s, col_x[2], ry + Inches(0.13), Inches(1.5), Inches(0.34),
                 owner, size=11, color=WHITE)
        add_text(s, col_x[3], ry + Inches(0.13), Inches(5.4), Inches(0.34),
                 item, size=11, color=WHITE)
        add_text(s, col_x[4], ry + Inches(0.13), Inches(1.85), Inches(0.34),
                 src, size=10, color=LIGHT_GRAY)

    return s

slides_built.append(slide_p0_carryovers)


# Slide 12: P1 carryovers (themes)
def slide_p1_carryovers():
    s = add_slide()
    slide_title(s, "P1 Carryovers Worth Flagging")
    corner_dot(s)

    cards = [
        ("Attribution debt",
         "Fix UTM attribution (past UTMs always showing). Mobile app events for FB apps and separate funnel events. Daily event log to correlate activity with metric drops/increases.",
         PURPLE),
        ("HubSpot investigation pileup",
         "Multiple 'Investigate HubSpot contact...' tickets opened in April never moved past New. Pattern: investigation work gets logged but not scheduled.",
         AMBER),
        ("SEO debt",
         "'SEO debts: provide plan and ETA for no-index and robots.txt fixes' and 'Find independent solution for robo.txt management, remove dev dependency'. Both still New.",
         PINK),
        ("Website backlog",
         "Page URL cache (P1, no movement). Anomaly detection and on-call protocol for Website (P1, dropped). Replace internal links to parametrized URLs (Working on it).",
         GREEN),
    ]
    card_w = Inches(5.95)
    card_h = Inches(2.35)
    margins = Inches(0.65)
    gap = Inches(0.2)
    top = Inches(1.7)
    for i, (h, b, accent) in enumerate(cards):
        col = i % 2
        row = i // 2
        x = margins + (card_w + gap) * col
        y = top + (card_h + gap) * row
        add_rect(s, x, y, card_w, card_h, DARK_GRAY, MID_GRAY)
        add_rect(s, x, y, card_w, Inches(0.06), accent)
        add_text(s, x + Inches(0.3), y + Inches(0.25), card_w - Inches(0.6), Inches(0.5),
                 h, size=16, bold=True, color=WHITE)
        add_text(s, x + Inches(0.3), y + Inches(0.85), card_w - Inches(0.6), Inches(1.4),
                 b, size=12, color=LIGHT_GRAY)
    return s

slides_built.append(slide_p1_carryovers)


# Slide 13: Themes
def slide_themes():
    s = add_slide()
    slide_title(s, "Themes That Drove the Quarter")
    corner_dot(s)

    themes = [
        ("Performance pressure was the dominant context",
         "Feb closed at 78% of target. Signups down 14%, trials down 8%. Nir publicly called for new sources and CVR experiments. This shaped priority more than any planning doc."),
        ("AI adoption became a strategic Hanan-led project",
         "The team explicitly debated Claude vs GPT in early March. Hanan led the answer. Claude MCP rollouts for Mixpanel and Omni were felt across the team."),
        ("External event in early March slowed everyone down",
         "March 9 to 10 messages line up with the March creation peak (121) and explain April's drop to 54. Q1 was not a smooth quarter."),
        ("Website ops is its own throughput, not overflow",
         "The Web Dev board's 117 closes prove this. Should be planned for explicitly, not treated as background noise."),
    ]
    top = Inches(1.6)
    row_h = Inches(1.3)
    for i, (h, b) in enumerate(themes):
        y = top + row_h * i
        add_text(s, Inches(0.65), y + Inches(0.05), Inches(0.7), Inches(0.4),
                 f"0{i+1}", size=22, bold=True, color=PURPLE)
        add_text(s, Inches(1.4), y, Inches(11.5), Inches(0.4),
                 h, size=15, bold=True, color=WHITE)
        add_text(s, Inches(1.4), y + Inches(0.4), Inches(11.5), Inches(0.85),
                 b, size=11, color=LIGHT_GRAY)
    return s

slides_built.append(slide_themes)


# Slide 14: Process patterns
def slide_process_patterns():
    s = add_slide()
    slide_title(s, "Process Patterns to Fix")
    corner_dot(s)

    patterns = [
        ("85% reactive, 15% planned",
         "Of 339 Q1 items, only 43 were planned. This is a structural feature of the function. Q2 planning will not bend the curve unless intake changes."),
        ("MOps board fields are decorative",
         "173 of 193 items stuck in Stage = Requirements. 189 of 193 tagged 'Increase Engagement' as Primary Goal. Both fields add zero signal."),
        ("Priority inflation on MOps board",
         "72 P1s plus 17 P0s out of 193: ~46% of work is P1-or-higher. Nir flagged this in March. The label has lost its tradeoff power."),
        ("Web Dev does Planned? right",
         "Yuval is correctly tagging Planned vs Unplanned items. The data is reliable. Bring this practice to the MOps Tasks board."),
    ]
    card_w = Inches(5.95)
    card_h = Inches(2.35)
    margins = Inches(0.65)
    gap = Inches(0.2)
    top = Inches(1.7)
    for i, (h, b) in enumerate(patterns):
        col = i % 2
        row = i // 2
        x = margins + (card_w + gap) * col
        y = top + (card_h + gap) * row
        add_rect(s, x, y, card_w, card_h, DARK_GRAY, MID_GRAY)
        add_rect(s, x, y, Inches(0.06), card_h, PURPLE)
        add_text(s, x + Inches(0.3), y + Inches(0.3), card_w - Inches(0.6), Inches(0.5),
                 h, size=15, bold=True, color=WHITE)
        add_text(s, x + Inches(0.3), y + Inches(0.85), card_w - Inches(0.6), Inches(1.4),
                 b, size=12, color=LIGHT_GRAY)
    return s

slides_built.append(slide_process_patterns)


# Slide 15: Lessons for Q2
def slide_lessons_q2():
    s = add_slide()
    slide_title(s, "Lessons for Q2")
    corner_dot(s)

    lessons = [
        ("Treat planned/unplanned as a real metric.",
         "Track it weekly. Aim to shift from 13/87 toward 30/70 by end of Q2. Either more planned work entering, or fewer unplanned accepted."),
        ("Adopt Web Dev's Planned? field on MOps Tasks.",
         "Yuval already does this correctly. Bring the practice to the MOps board so future retros can use real data, not a created-date proxy."),
        ("Re-baseline priority on MOps board.",
         "No more than 5 active P0s at once. No more than 25% of open work tagged P1. Forces real tradeoffs."),
        ("Triage New items weekly.",
         "30 minutes Mondays for #mops-priority-room and the Tasks board. Catches the April investigation pileup pattern."),
        ("Budget for website ops explicitly.",
         "Website output is not overflow. Plan capacity for it the way we plan for HubSpot or attribution."),
        ("Capture the AI tooling work in this repo.",
         "Brand skill, MCP rollouts, deck-builder skill are load-bearing and not yet documented in this repo."),
    ]
    top = Inches(1.55)
    row_h = Inches(0.85)
    for i, (h, b) in enumerate(lessons):
        y = top + row_h * i
        add_text(s, Inches(0.65), y + Inches(0.05), Inches(0.55), Inches(0.4),
                 str(i+1), size=20, bold=True, color=PURPLE)
        add_text(s, Inches(1.25), y, Inches(11.7), Inches(0.4),
                 h, size=14, bold=True, color=WHITE)
        add_text(s, Inches(1.25), y + Inches(0.36), Inches(11.7), Inches(0.5),
                 b, size=11, color=LIGHT_GRAY)
    return s

slides_built.append(slide_lessons_q2)


# Slide 16: Q2 Implications - Carry / Kill / Scale
def slide_q2_implications():
    s = add_slide()
    slide_title(s, "Q2 Implications")
    corner_dot(s)

    cols = [
        ("CARRY", "Must finish", AMBER,
         [
             "5 MOps P0s (Cloudfront, iOS AppsFlyer, Multi-account HubSpot, Home LP test, Budget report)",
             "2 Web Dev Urgents (Love & Labor static assets, birth certificate LP)",
             "Open A/B tests (Descript vs CoCo, Home LP). Decide ship or kill in Week 1.",
         ]),
        ("KILL or DEFER", "Suggested", PINK,
         [
             "'Clarify Teamblind LP in Claude' (P1, March 17, no movement). Not a P1.",
             "April HubSpot investigation pileup. Triage Week 1: commit or close.",
             "Old Web Dev Stuck items from Feb (webinar image, /community code cleanup).",
         ]),
        ("SCALE", "Worked, do more", GREEN,
         [
             "Self-Attribution weekly report. Add SLG funnel UTM and paid attribution.",
             "AI tooling. HubSpot MCP playbook, 'campaign report in 60s', brand-asset workflows.",
             "Yuval's planning discipline. Bring Planned? field to MOps Tasks board.",
             "Localization. FR live, DE recovered. More locales likely in Q2.",
         ]),
    ]
    col_w = Inches(4.0)
    gap = Inches(0.15)
    start_x = Inches(0.65)
    top = Inches(1.65)
    h = Inches(5.0)
    for i, (label, sub, accent, items) in enumerate(cols):
        x = start_x + (col_w + gap) * i
        add_rect(s, x, top, col_w, h, DARK_GRAY, MID_GRAY)
        add_rect(s, x, top, col_w, Inches(0.07), accent)
        add_text(s, x + Inches(0.3), top + Inches(0.25), col_w - Inches(0.6), Inches(0.4),
                 label, size=13, bold=True, color=accent)
        add_text(s, x + Inches(0.3), top + Inches(0.6), col_w - Inches(0.6), Inches(0.4),
                 sub, size=10, color=LIGHT_GRAY)
        add_paragraphs(s, x + Inches(0.3), top + Inches(1.05), col_w - Inches(0.6), Inches(3.7),
                       items, size=10.5, color=WHITE, line_spacing=1.3, bullet=True)
    return s

slides_built.append(slide_q2_implications)


# Slide 17: Open Questions
def slide_open_questions():
    s = add_slide()
    slide_title(s, "Open Questions for the Q2 Plan")
    corner_dot(s)

    questions = [
        "Are we accepting the 85% reactive rate, or actively trying to bend it? With what mechanism?",
        "Who triages new requests entering both boards? Hanan as filter, or each owner filters their own?",
        "What capacity reservation for unplanned in Q2 (e.g. 50% of bandwidth) vs planned initiatives?",
        "Should we add a Type / Area-of-impact column on the Web Dev board so future retros can categorize its output?",
    ]
    y = Inches(1.65)
    row_h = Inches(1.15)
    for i, q in enumerate(questions):
        ry = y + row_h * i
        add_text(s, Inches(0.65), ry, Inches(0.7), Inches(0.7),
                 "?", size=42, bold=True, color=PURPLE)
        add_paragraphs(s, Inches(1.45), ry + Inches(0.18), Inches(11.4), Inches(0.85),
                       [q], size=14, color=WHITE, line_spacing=1.3)
    return s

slides_built.append(slide_open_questions)


# Slide 18: Closing
def slide_close():
    s = add_slide()
    add_rect(s, Inches(5.92), Inches(2.6), Inches(1.5), Inches(0.04), PURPLE)
    add_text(s, Inches(0.5), Inches(2.85), Inches(12.33), Inches(1.0),
             "Thank you.", size=56, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    add_text(s, Inches(0.5), Inches(3.95), Inches(12.33), Inches(0.5),
             "Onwards to Q2.", size=22, color=LIGHT_GRAY, align=PP_ALIGN.CENTER)
    add_text(s, Inches(0.5), Inches(5.5), Inches(12.33), Inches(0.4),
             "Hanan · Jonathan · Yuval", size=14, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    add_text(s, Inches(0.5), Inches(5.9), Inches(12.33), Inches(0.4),
             "Marketing Operations · Riverside Growth", size=12, color=PURPLE, align=PP_ALIGN.CENTER)
    return s

slides_built.append(slide_close)


# Build all slides
total = len(slides_built)
for i, fn in enumerate(slides_built, 1):
    s = fn()
    if i not in (1, total):
        page_footer(s, i, total)

prs.save(OUT)
print(f"Saved {OUT} ({total} slides)")
