#!/usr/bin/env bash
set -euo pipefail

# PostToolUse hook: tracks consecutive empty search results (Glob, Grep, Bash).
# After THRESHOLD consecutive failures, injects feedback telling Claude to
# ask the user for help instead of continuing to guess.
#
# State is tracked in a temp file per session. Resets on any successful search.

THRESHOLD=3
STATE_FILE="/tmp/.claude-search-failures-$$"

INPUT=$(cat)

TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name // empty')
SESSION_ID=$(echo "$INPUT" | jq -r '.session_id // empty')

# Use session-specific state file if available
if [[ -n "$SESSION_ID" ]]; then
    STATE_FILE="/tmp/.claude-search-failures-${SESSION_ID}"
fi

# Determine if this was an empty/failed search
is_failure=false

case "$TOOL_NAME" in
    Glob)
        # Glob: check if matches array is empty
        match_count=$(echo "$INPUT" | jq '.tool_response.matches // [] | length')
        if [[ "$match_count" -eq 0 ]]; then
            is_failure=true
        fi
        ;;
    Grep)
        # Grep: check for "No files found" or "No matches found" in output
        response=$(echo "$INPUT" | jq -r '.tool_response // empty')
        if echo "$response" | grep -qiE 'No (files|matches) found|^$'; then
            is_failure=true
        fi
        ;;
    Bash)
        # Bash: check for common "not found" patterns in find/ls/grep commands
        command=$(echo "$INPUT" | jq -r '.tool_input.command // empty')
        stderr=$(echo "$INPUT" | jq -r '.tool_response.stderr // empty')
        stdout=$(echo "$INPUT" | jq -r '.tool_response.stdout // empty')
        exit_code=$(echo "$INPUT" | jq -r '.tool_response.exitCode // 0')

        # Only track search-like commands
        if echo "$command" | grep -qE '^(find |ls |grep |rg )'; then
            if [[ "$exit_code" -ne 0 ]] || [[ -z "$stdout" ]]; then
                is_failure=true
            fi
        fi
        ;;
    *)
        # Not a search tool — ignore
        exit 0
        ;;
esac

if [[ "$is_failure" == "true" ]]; then
    # Increment counter
    count=0
    if [[ -f "$STATE_FILE" ]]; then
        count=$(cat "$STATE_FILE")
    fi
    count=$((count + 1))
    echo "$count" > "$STATE_FILE"

    if [[ "$count" -ge "$THRESHOLD" ]]; then
        jq -n \
            --arg count "$count" \
            --arg threshold "$THRESHOLD" \
            '{
                "hookSpecificOutput": {
                    "hookEventName": "PostToolUse",
                    "additionalContext": ("You have had " + $count + " consecutive empty search results. You are probably looking in the wrong place or using the wrong name. Ask the user where to find what you are looking for. (If the user has already told you to keep searching, continue — but try a substantially different approach, not minor variations of the same query.)")
                }
            }'
    fi
else
    # Success — reset counter
    rm -f "$STATE_FILE"
fi

exit 0
