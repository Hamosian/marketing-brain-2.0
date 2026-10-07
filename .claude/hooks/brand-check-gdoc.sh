#!/usr/bin/env bash
# PreToolUse guardrail: enforce Riverside brand guidelines on Google Doc creation.
#
# Fires on the mcp__Google_Drive__create_file tool. If the payload is a Google Doc
# (native doc, or HTML/Markdown that Drive converts to a doc) but carries no brand
# markers, it returns permissionDecision:"ask" with a reminder to apply the
# /riverside-brand-guidelines skill first. Branded docs and non-doc files pass through
# silently. Deterministic (no LLM/API call), so it is safe on every create_file.
#
# Brand markers checked: Riverside Purple (#7C5CFF) or the Instrument Sans font,
# either of which only appears when the brand styling has been applied.
set -uo pipefail

input="$(cat)"

mt="$(printf '%s' "$input"  | jq -r '.tool_input.contentMimeType // .tool_input.mimeType // ""')"
title="$(printf '%s' "$input" | jq -r '.tool_input.title // ""')"
tc="$(printf '%s' "$input"  | jq -r '.tool_input.textContent // ""')"
b64="$(printf '%s' "$input" | jq -r '.tool_input.base64Content // .tool_input.content // ""')"
if [ -n "$b64" ]; then
  tc="$tc$(printf '%s' "$b64" | base64 -d 2>/dev/null || true)"
fi

# Is this a Google Doc creation? (native doc, or HTML/Markdown that converts to a doc)
is_doc=false
case "$mt" in
  *google-apps.document*|*text/html*|*text/markdown*) is_doc=true ;;
esac

# Brand markers: Riverside Purple or Instrument Sans.
branded=false
if printf '%s' "$tc" | grep -qiE '7C5CFF|Instrument Sans'; then branded=true; fi

if [ "$is_doc" = true ] && [ "$branded" = false ]; then
  reason="Riverside brand check: the Google Doc \"$title\" has no brand markers (Instrument Sans / #7C5CFF). Apply the /riverside-brand-guidelines skill BEFORE creating it: Instrument Sans font, logo + Riverside.com header, H1 near-black (#0F0F14) / H2 Riverside Purple (#7C5CFF) with 2px accent bars / H3 dark gray (#1C1C24), branded tables (near-black header row with white text, #EDE8FF alternating rows, #E6E6EB borders), and NO em-dash characters. Then re-create the doc."
  jq -cn --arg r "$reason" '{hookSpecificOutput:{hookEventName:"PreToolUse",permissionDecision:"ask",permissionDecisionReason:$r}}'
fi

exit 0
