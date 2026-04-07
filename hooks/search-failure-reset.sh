#!/usr/bin/env bash
set -euo pipefail

# UserPromptSubmit hook: resets the search failure counter whenever the user
# sends a new message. This lets the user override the "stop guessing" advice
# by simply responding — their input implicitly says "I've given you new info,
# try again."

INPUT=$(cat)
SESSION_ID=$(echo "$INPUT" | jq -r '.session_id // empty')

if [[ -n "$SESSION_ID" ]]; then
    rm -f "/tmp/.claude-search-failures-${SESSION_ID}"
fi

exit 0
