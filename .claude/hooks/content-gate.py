#!/usr/bin/env python3
"""PreToolUse gate: no outward message leaves unless its exact text passed the
content pipeline (nik-voice -> de-ai -> critique SHIP) and was recorded with
scripts/content_gate_record.py. Exit 2 blocks the tool call and tells the model
what to do; it never asks a human, so it is safe in scheduled and cloud runs.
Added 2026-10-04 after repeated sends that skipped de-ai and critique (Nir: "we had
many instances where you didn't run it")."""
import json, re, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from content_gate_lib import approved_hashes, digest, normalise

data = json.load(sys.stdin)
tool = data.get("tool_name", "")
inp = data.get("tool_input", {}) or {}

# Only outward channels: Slack and Gmail. Session-to-session messages are not outward.
if "ccd_" in tool or not re.search(r"__(slack_send_message|slack_schedule_message|slack_send_message_draft|create_draft|update_draft|reply|send_message|forward)$", tool):
    sys.exit(0)
if tool.endswith("__send_message") and "slack" not in tool and inp.get("draftId") and not (inp.get("body") or inp.get("htmlBody")):
    sys.exit(0)  # sending an existing Gmail draft: its text was gated when the draft was created

texts = [inp.get(k) for k in ("message", "body", "htmlBody", "forwardText") if inp.get(k)]
if not texts:
    sys.exit(0)  # nothing written by us (e.g. a bare forward)

# Gmail link guard (2026-10-06). The Gmail connector rewrites every link and bare domain
# into a visible google.com/url?q=...&ust=... redirect, on send_message, reply and
# create_draft alike, plain body or HTML anchor. Two partner emails went out that way after
# passing critique, because the gate checks the text we send, not the text that lands.
# Email addresses are left alone (the lookbehind skips anything after "@").
is_gmail = "slack" not in tool
LINK = re.compile(r"https?://|www\.|(?<![@\w.-])[a-z0-9-]+(\.[a-z0-9-]+)*\.(com|fm|io|net|org|co|ai|app|so|me|tv)\b", re.I)
if is_gmail and any(LINK.search(t) for t in texts):
    hit = next(LINK.search(t).group(0) for t in texts if LINK.search(t))
    sys.stderr.write(
        f"CONTENT GATE: blocked a Gmail send with a link or domain in it (\"{hit}\").\n"
        "The Gmail connector rewrites every link and bare domain into a google.com/url redirect "
        "the reader sees, including in drafts and HTML anchors. Name the page in words instead "
        "(\"your webinar software list\", \"our homepage\"), or give Nir the link to paste in Gmail "
        "himself. See references/integration-debugging.md, 'The Gmail connector rewrites links'.\n")
    sys.exit(2)
# Prefer the plain body when both plain and HTML are given; either matching passes.
ok = approved_hashes()
if any(digest(t) in ok for t in texts):
    sys.exit(0)

preview = normalise(texts[0])[:120]
sys.stderr.write(
    "CONTENT GATE: blocked. This text has not passed the content pipeline.\n"
    f"Text starts: \"{preview}\"\n"
    "Before any outward message: run nik-voice (pick the register) -> de-ai -> critique. "
    "On a SHIP verdict, record the EXACT final text:\n"
    "  python3 scripts/content_gate_record.py --verdict SHIP --register <register> <<'EOF'\n  <final text>\n  EOF\n"
    "then retry this call with that same text. Changing a word after critique means re-running critique.\n")
sys.exit(2)
