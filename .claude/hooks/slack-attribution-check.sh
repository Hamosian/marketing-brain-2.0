#!/usr/bin/env bash
# PreToolUse guardrail: the Marketing OS footer on agent-sent Slack messages.
#
# Fires on any Slack send or schedule tool (matcher mcp__.*__slack_(send|schedule)_message).
# Until 2026-10-04 the matcher named mcp__Slack__slack_send_message, a server name this
# workspace's Slack connector does not use, so the check never ran once.
#
# Two rules from CLAUDE.md:
#   - an agent-sent message ends with `_Posted by the Marketing OS agent_`;
#   - a message Nir approved word for word goes out WITHOUT it (per Nir, 2026-09-30).
# "Approved word for word" is read from the content-gate ledger: a text recorded with
# `scripts/content_gate_record.py --nir-approved`. The ledger normalisation ignores the
# footer, so the same approved text matches with or without it.
#
# NON-GATING BY DESIGN: it only injects additionalContext, never blocks or asks, so it is
# safe in Claude-in-Slack and cloud routines. The content gate does the blocking.
set -uo pipefail

input="$(cat)"
footer='_Posted by the Marketing OS agent_'

msg="$(printf '%s' "$input" | jq -r '
  .tool_input as $t
  | [ $t.text?, $t.markdown_text?, $t.message?,
      ( ($t.blocks?      // empty) | .. | .text? | strings ),
      ( ($t.attachments? // empty) | .. | .text? | strings )
    ]
  | map(strings) | join("\n")
' 2>/dev/null || true)"
[ -z "$msg" ] && exit 0

last_line="$(printf '%s\n' "$msg" | awk 'NF{l=$0} END{print l}' | sed 's/[[:space:]]*$//')"

approved="$(MSG="$msg" python3 - <<'PY' 2>/dev/null
import os, sys
sys.path.insert(0, os.path.join(os.environ.get("CLAUDE_PROJECT_DIR", "."), ".claude", "hooks"))
from content_gate_lib import digest, nir_approved_hashes
print("yes" if digest(os.environ["MSG"]) in nir_approved_hashes() else "no")
PY
)"

if [ "$approved" = "yes" ]; then
  if [ "$last_line" = "$footer" ]; then
    reason="Slack attribution check: Nir approved this message word for word, so it goes out WITHOUT the Marketing OS footer (CLAUDE.md, 2026-09-30). Remove the footer line and send the approved text as is."
    jq -cn --arg r "$reason" '{hookSpecificOutput:{hookEventName:"PreToolUse",additionalContext:$r}}'
  fi
  exit 0
fi

if [ "$last_line" != "$footer" ]; then
  reason="Slack attribution check: this message does not end with the Marketing OS footer. CLAUDE.md requires every agent-sent Slack message to end with the line \`_Posted by the Marketing OS agent_\`. Append it before you send. If Nir approved this exact text word for word, it goes out without the footer: record it with \`scripts/content_gate_record.py --nir-approved\` instead."
  jq -cn --arg r "$reason" '{hookSpecificOutput:{hookEventName:"PreToolUse",additionalContext:$r}}'
fi
exit 0
