#!/usr/bin/env python3
"""Record a text that passed the content pipeline so the content gate lets it out.

  python3 scripts/content_gate_record.py --verdict SHIP --register internal-ask <<'EOF'
  <exact final text>
  EOF

Add --nir-approved when Nir approved the exact wording in chat; the footer check then expects NO footer.
Only SHIP is accepted: a REVISE text goes back to nik-voice, it does not get recorded.
"""
import argparse, json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".claude", "hooks"))
from content_gate_lib import record

ap = argparse.ArgumentParser()
ap.add_argument("--verdict", required=True)
ap.add_argument("--register", required=True)
ap.add_argument("--note", default="")
ap.add_argument("--nir-approved", action="store_true", help="Nir approved this exact text word for word: it goes out WITHOUT the agent footer")
a = ap.parse_args()
if a.verdict.upper() != "SHIP":
    sys.exit("Only a SHIP verdict can be recorded. Revise and re-run critique.")
text = sys.stdin.read()
if not text.strip():
    sys.exit("No text on stdin.")
print(json.dumps(record(text, "SHIP", a.register, a.note, a.nir_approved), ensure_ascii=False))
