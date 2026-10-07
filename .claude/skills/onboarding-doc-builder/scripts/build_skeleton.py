"""Build a new hire's onboarding doc from one SPEC, with the Riverside .docx builder.

Copy this file to the scratchpad, fill SPEC from the repo (see knowledge/playbook.md for what
each part holds and where it comes from), then run:

    python3 build_skeleton.py --out "<Name> - <Team> onboarding.docx"           # final
    python3 build_skeleton.py --out draft.docx --draft                          # while filling

Without --draft the build refuses to write while any "[Replace: ...]" marker is left, so a
half-filled doc cannot ship by accident. Text parts use the builder's parts syntax: a plain
string, or ("b", text) bold, ("pb", text) purple label, ("c", text) channel or skill name,
("link", text, url). Keep em and en dashes out of every string (CLAUDE.md).
"""
import argparse
import os
import re
import sys
import tempfile


def _repo_root():
    d = os.path.dirname(os.path.abspath(__file__))
    while d != "/" and not os.path.exists(os.path.join(d, "scripts", "riverside_docx.py")):
        d = os.path.dirname(d)
    return d


REPO = os.environ.get("MARKETING_BRAIN_REPO", _repo_root())
sys.path.insert(0, os.path.join(REPO, "scripts"))
import riverside_docx as rd  # noqa: E402

R = "[Replace: {}]".format  # marker for anything still to fill

SPEC = {
    "header": "Marketing Operations onboarding, internal",
    "cover_image": None,      # scripts/web_screenshot.sh https://riverside.com/ cover.jpg
    "org_chart_image": None,  # knowledge/orgchart_template.html, rendered at scale 2 and cropped
    "hire_first_name": R("first name"),
    "team": R("team name, e.g. Marketing Operations"),
    "letter_opening": R("one bold line, e.g. We're so excited to have you join us."),
    "letter": [R("what the team does, in two or three sentences"), R("why this role matters")],
    "responsibilities": [(R("area: "), R("what the team owns there"))],
    "letter_goal": R("the main goal, concrete"),
    "letter_closer": R("a two-word closer, e.g. Go team."),
    "signer_first_name": R("signer first name"),
    "who_we_are": [
        ("What is Riverside", [R("the few things our pages have to explain")]),
        ("Marketing department goal", [R("named by what it is measured on")]),
    ],
    "org_chart_caption": R("Marketing, <month year>. HiBob has the full, live org chart."),
    "team_paragraphs": [(R("The <team> team"), [R("who is on it, and ... you.")])],
    "prereq_intro": R("Everything below should be ready in your first days."),
    "access": [(R("tool"), R("why you need it"), R("who grants it (references/other_teams.md)"))],
    "channels": [(R("group: "), [R("#channel")])],
    "channels_caption": R("which channels are private"),
    "people_intro": R("who they will meet; intros are 30 min at most; the topic convention"),
    "people": [(R("who"), R("team"), R("title, checked in HiBob"), R("30 min, 1st week"))],
    "people_caption": R("holidays or absences in week 1"),
    "phases": [  # Phase 2 onward. "sections" are optional h3 blocks before the To do list.
        {"title": "Phase 2: Know Riverside", "intro": [R("intro")], "sections": [],
         "todo": [R("to do")]},
    ],
    "weeks": [(R("Week 1\n<dates>"), R("focus"), R("by the end of the week"))],
    "days_31_90_callout": R("This part is a draft on purpose ... we agree in our 1:1."),
    "days_31_90": [(R("Days 31 to 60, <theme>. "), R("outcomes")),
                   (R("Days 61 to 90, <theme>. "), R("outcomes"))],
    "culture": [  # (heading, bullets, numbered)
        ("How we work", [R("principle")], True),
        ("Meetings", [R("meeting")], False),
    ],
    "documents": [[R("document"), " (", R("what it is"), ")"]],
    "closing": R("Thanks and good luck. We're so excited to have you."),
    "signer_name": R("signer full name"),
    "signer_title": R("signer title"),
}


def build(spec):
    doc = rd.new_doc()
    rd.brand_header(doc, spec["header"])
    rd.page_numbers(doc)

    if spec["cover_image"]:
        rd.picture(doc, spec["cover_image"], space_after=18)
    for text, bold in ((spec["hire_first_name"] + ",", True), ("Welcome to the", False),
                       (spec["team"] + " team at Riverside.", True)):
        rd._styled_para(doc, text, 26, rd.NEAR_BLACK, bold=bold, space_after=0, keep_with_next=True)
    rd._spacer(doc, 10)
    rd.accent_bar(doc, space_after=10)
    rd.rich(doc, [("b", spec["letter_opening"])], size=11)
    for para in spec["letter"]:
        rd.rich(doc, para)
    rd.rich(doc, "Our responsibilities include:", space_after=4)
    rd.bullets(doc, [[("b", label), text] for label, text in spec["responsibilities"]])
    rd.rich(doc, spec["letter_goal"])
    rd.rich(doc, [("b", spec["letter_closer"])], space_after=12)
    rd.rich(doc, "Good luck,", space_after=0)
    rd.rich(doc, [("b", spec["signer_first_name"])])

    rd.page_break(doc)
    rd.h1(doc, "Who we are")
    for heading, paras in spec["who_we_are"]:
        rd.h2(doc, heading)
        for para in paras:
            rd.rich(doc, para)
    if spec["org_chart_image"]:
        rd.h2(doc, "The Marketing department")
        rd.picture(doc, spec["org_chart_image"], space_after=2)
        rd.caption(doc, spec["org_chart_caption"])
    for heading, paras in spec["team_paragraphs"]:
        rd.h2(doc, heading)
        for para in paras:
            rd.rich(doc, para)

    rd.page_break(doc)
    rd.h1(doc, "Prerequisites")
    rd.rich(doc, [("b", "100% motivation.")], size=11)
    rd.rich(doc, spec["prereq_intro"])
    rd.table(doc, ["", "What", "Why you need it", "Who sets it up"],
             [["☐", w, y, o] for w, y, o in spec["access"]], widths=[0.4, 1.9, 2.6, 1.6], check_col=True)
    rd.rich(doc, [("b", "Get added to these Slack channels:")], space_after=4).paragraph_format.keep_with_next = True
    rd.bullets(doc, [[("pb", label)] + [p for c in chans for p in (("c", c), ", ")][:-1]
                     for label, chans in spec["channels"]])
    rd.caption(doc, spec["channels_caption"])

    rd.page_break(doc)
    rd.h1(doc, "Phase 1: Know the people")
    rd.rich(doc, spec["people_intro"])
    rd.table(doc, ["Who", "Team", "Title", "Duration and week"], [list(r) for r in spec["people"]],
             widths=[1.75, 1.3, 1.6, 1.85])
    rd.caption(doc, spec["people_caption"])

    for phase in spec["phases"]:
        rd.h1(doc, phase["title"])
        for para in phase["intro"]:
            rd.rich(doc, para)
        for heading, items in phase.get("sections", []):
            rd.h3(doc, heading)
            rd.bullets(doc, items)
        rd.h3(doc, "To do")
        rd.bullets(doc, phase["todo"])

    rd.page_break(doc)
    rd.h1(doc, "Your first 90 days")
    rd.h2(doc, "First month, week by week")
    rd.table(doc, ["Week", "Focus", "By the end of the week"], [list(w) for w in spec["weeks"]],
             widths=[1.3, 1.4, 3.8])
    rd.h2(doc, "Days 31 to 90")
    rd.callout(doc, spec["days_31_90_callout"], size=11)
    for label, text in spec["days_31_90"]:
        rd.label_para(doc, label, text)

    rd.h1(doc, "Culture and ways of working")
    for heading, items, numbered in spec["culture"]:
        rd.h2(doc, heading)
        rd.bullets(doc, items, numbered=numbered, keep_together=True)

    rd.h1(doc, "Documents")
    rd.bullets(doc, spec["documents"])
    rd._spacer(doc, 10)
    rd.rich(doc, [("b", spec["closing"])], size=11, space_after=12)
    rd.rich(doc, [("b", spec["signer_name"])], space_after=0)
    rd.rich(doc, spec["signer_title"])
    rd.diligence(doc, "document", "drafting and formatting")
    return doc


def _all_text(doc):
    parts = [p.text for p in doc.paragraphs]
    parts += [c.text for t in doc.tables for row in t.rows for c in row.cells]
    return "\n".join(parts)


def main():
    ap = argparse.ArgumentParser(description="Build an onboarding doc from SPEC.")
    ap.add_argument("--out", required=True, help="output .docx path")
    ap.add_argument("--draft", action="store_true", help="allow [Replace: ...] markers")
    args = ap.parse_args()

    doc = build(SPEC)
    text = _all_text(doc)
    left = sorted(set(re.findall(r"\[Replace: [^\]]*\]", text)))
    dashes = len(re.findall("[\u2014\u2013]", text))
    if (left or dashes) and not args.draft:
        print(f"refusing to build: {len(left)} unfilled markers, {dashes} em/en dashes")
        for m in left[:20]:
            print("  ", m)
        return 1
    raw = os.path.join(tempfile.mkdtemp(), "raw.docx")
    doc.save(raw)
    before, after = rd.slim(raw, args.out)
    print(f"built {args.out} ({before} -> {after} bytes); markers left: {len(left)}, dashes: {dashes}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
