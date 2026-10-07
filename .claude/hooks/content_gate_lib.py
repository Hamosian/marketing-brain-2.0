"""Shared helpers for the content-pipeline gate (hook + recorder).

The gate's one rule: text that leaves the building (a Slack message, a Gmail draft,
reply, send or forward) must match, after normalisation, a text that was recorded
as SHIP by the critique stage. Normalisation is deliberately forgiving about
formatting (whitespace, case, markdown/HTML markup, Slack <url|label> link syntax,
the agent footer) and strict about words: change one word after critique and the
gate blocks until the new text is re-judged and re-recorded.
"""
import hashlib, html, json, os, re, time

ROOT = os.environ.get("CLAUDE_PROJECT_DIR") or os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LEDGER = os.path.join(ROOT, ".claude", "content-gate", "approved.jsonl")
FOOTER_RE = re.compile(r"_?posted by the marketing os agent_?", re.I)

def normalise(text: str) -> str:
    t = html.unescape(text or "")
    t = re.sub(r"<br\s*/?>|</p>|</div>", "\n", t, flags=re.I)
    t = re.sub(r"<(https?://[^|>]+)\|([^>]+)>", r"\2 \1", t)   # slack <url|label>
    t = re.sub(r"<(https?://[^>]+)>", r"\1", t)
    t = re.sub(r"<[^>]+>", " ", t)                               # html tags
    t = re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)", r"\1 \2", t)  # markdown links
    t = FOOTER_RE.sub(" ", t)
    t = re.sub(r"\*sent using\*.*$", " ", t, flags=re.I | re.M)
    t = re.sub(r"[*_`~>#]", " ", t)                             # markdown marks
    t = re.sub(r"\s+", " ", t).strip().lower()
    return t

def digest(text: str) -> str:
    return hashlib.sha256(normalise(text).encode()).hexdigest()

def approved_hashes():
    out = set()
    if os.path.exists(LEDGER):
        for line in open(LEDGER):
            try: out.add(json.loads(line)["sha256"])
            except Exception: pass
    return out

def nir_approved_hashes():
    out = set()
    if os.path.exists(LEDGER):
        for line in open(LEDGER):
            try:
                r = json.loads(line)
                if r.get("nir_approved"): out.add(r["sha256"])
            except Exception: pass
    return out

def record(text, verdict, register, note="", nir_approved=False):
    os.makedirs(os.path.dirname(LEDGER), exist_ok=True)
    row = {"sha256": digest(text), "at": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "verdict": verdict,
           "register": register, "preview": normalise(text)[:90], "note": note, "nir_approved": bool(nir_approved)}
    with open(LEDGER, "a") as f: f.write(json.dumps(row, ensure_ascii=False) + "\n")
    return row
