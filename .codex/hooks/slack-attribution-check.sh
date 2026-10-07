#!/usr/bin/env bash
# PreToolUse guardrail: enforce Marketing OS attribution on Slack messages.
#
# Fires on the mcp__Slack__slack_send_message tool. CLAUDE.md requires every Slack
# message the agent sends to carry the footer line `_Posted by the Marketing OS agent_`
# as its last line. This extracts the rendered message text (text / markdown_text /
# message and Block Kit block text) and passes silently only when that exact footer is
# the last non-empty line; otherwise it injects a non-gating reminder
# (hookSpecificOutput.additionalContext) to append the footer. Deterministic
# (no LLM/API call), so it is safe on every send.
#
# NON-GATING BY DESIGN. This must never return permissionDecision:"ask". The
# Marketing OS agent runs on Slack (Claude-in-Slack) and in cloud routines, both
# non-interactive: an "ask" has no human to answer it, so the send is aborted and the
# whole skill run dies as `exit 1` with no stderr. additionalContext nudges the model
# without blocking the tool, so a missing footer self-corrects on the next turn.
set -uo pipefail

input="$(cat)"

footer='_Posted by the Marketing OS agent_'

# Pull only the message-bearing text out of tool_input. Slack tool variants carry the
# body in text / markdown_text / message, and Block Kit nests the copy in block and
# attachment `.text` strings; collect them all (document order). Matching the exact
# footer as the final line - rather than the loose phrase anywhere in the serialized
# input - stops an unrelated field (a quoted body, thread context) from suppressing the
# reminder when the outgoing message actually has no footer.
msg="$(printf '%s' "$input" | jq -r '
  .tool_input as $t
  | [ $t.text?, $t.markdown_text?, $t.message?,
      ( ($t.blocks?      // empty) | .. | .text? | strings ),
      ( ($t.attachments? // empty) | .. | .text? | strings )
    ]
  | map(strings) | join("\n")
' 2>/dev/null || true)"

# Last non-empty line, trailing whitespace trimmed.
last_line="$(printf '%s\n' "$msg" | awk 'NF{l=$0} END{print l}' | sed 's/[[:space:]]*$//')"

if [ "$last_line" != "$footer" ]; then
  reason="Slack attribution check: this message does not end with the Marketing OS footer. CLAUDE.md requires every agent-sent Slack message to end with the line \`_Posted by the Marketing OS agent_\` as its final line. Append it before your next send. (If this is a thread reply, keep the footer and the thread_ts.)"
  jq -cn --arg r "$reason" '{hookSpecificOutput:{hookEventName:"PreToolUse",additionalContext:$r}}'
fi

exit 0
