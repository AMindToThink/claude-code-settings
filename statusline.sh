#!/bin/bash
# Claude Code statusline script
# Receives JSON on stdin with session info

# Find jq: prefer system jq, fall back to ~/.local/bin
JQ=$(command -v jq 2>/dev/null || echo "$HOME/.local/bin/jq")
if [ ! -x "$JQ" ]; then
    echo "jq not found"
    exit 0
fi

DATA=$(cat)

CWD=$(echo "$DATA" | "$JQ" -r '.cwd // ""')
MODEL=$(echo "$DATA" | "$JQ" -r '.model.display_name // ""')
# Absent when the current model does not support the effort parameter
EFFORT=$(echo "$DATA" | "$JQ" -r '.effort.level // empty')
# Present only while vim mode is enabled. We render it ourselves, so settings.json
# sets statusLine.hideVimModeIndicator to suppress the built-in "-- INSERT --" row.
VIM=$(echo "$DATA" | "$JQ" -r '.vim.mode // empty')
COST=$(echo "$DATA" | "$JQ" -r '.cost.total_cost_usd // 0' | xargs printf "%.3f")
CTX=$(echo "$DATA" | "$JQ" -r '.context_window.used_percentage // 0' | xargs printf "%.0f")
ADDED=$(echo "$DATA" | "$JQ" -r '.cost.total_lines_added // 0')
REMOVED=$(echo "$DATA" | "$JQ" -r '.cost.total_lines_removed // 0')

# Plan (subscription) rate limits. Only present for Pro/Max, and only after the
# first API response of a session -- "// empty" leaves these blank otherwise.
RL5_PCT=$(echo "$DATA" | "$JQ" -r '.rate_limits.five_hour.used_percentage // empty')
RL5_AT=$(echo "$DATA" | "$JQ" -r '.rate_limits.five_hour.resets_at // empty')
RL7_PCT=$(echo "$DATA" | "$JQ" -r '.rate_limits.seven_day.used_percentage // empty')
RL7_AT=$(echo "$DATA" | "$JQ" -r '.rate_limits.seven_day.resets_at // empty')
NOW=$(date +%s)

# resets_at is Unix epoch seconds -> compact "2h14m" / "3d4h" / "12m"
fmt_until() {
    local target="${1%%.*}"
    case "$target" in
        ''|*[!0-9]*) return ;;
    esac
    local secs=$(( target - NOW ))
    if [ "$secs" -le 0 ]; then echo "now"; return; fi
    local d=$(( secs / 86400 )) h=$(( secs % 86400 / 3600 )) m=$(( secs % 3600 / 60 ))
    if [ "$d" -gt 0 ]; then echo "${d}d${h}h"
    elif [ "$h" -gt 0 ]; then echo "${h}h${m}m"
    else echo "${m}m"; fi
}

pct_color() {
    local p="${1%%.*}"
    case "$p" in
        ''|*[!0-9]*) p=0 ;;
    esac
    if [ "$p" -ge 90 ]; then echo 31        # red
    elif [ "$p" -ge 70 ]; then echo 33      # yellow
    else echo 90; fi                        # gray
}

# "5h:24% (1h12m)" -- percentage, and how long until that window refreshes
fmt_limit() {
    local label="$1" pct="$2" at="$3"
    [ -z "$pct" ] && return
    local until
    until=$(fmt_until "$at")
    printf '\033[%sm%s:%.0f%%%s\033[0m' "$(pct_color "$pct")" "$label" "$pct" "${until:+ ($until)}"
}

# This replaces the built-in indicator, so each mode gets its own color to stay
# glanceable: INSERT green, NORMAL blue, VISUAL yellow.
vim_color() {
    case "$1" in
        INSERT) echo '1;32' ;;
        NORMAL) echo '1;34' ;;
        VISUAL*) echo '1;33' ;;
        *) echo '1' ;;
    esac
}

# Shorten home directory to ~
CWD="${CWD/#$HOME/~}"

# Git branch (from the cwd)
BRANCH=$(git -C "$(echo "$DATA" | "$JQ" -r '.cwd // "."')" rev-parse --abbrev-ref HEAD 2>/dev/null)

# First line: model, effort, where we are, and what this session has spent
LINE=""
[ -n "$MODEL" ] && LINE="${LINE}\033[36m${MODEL}\033[0m"
[ -n "$EFFORT" ] && LINE="${LINE} \033[90m${EFFORT}\033[0m"
[ -n "$CWD" ] && LINE="${LINE}  \033[33m${CWD}\033[0m"
[ -n "$BRANCH" ] && LINE="${LINE}  \033[35m${BRANCH}\033[0m"
LINE="${LINE}  \033[32m\$${COST}\033[0m"
LINE="${LINE}  \033[32m+${ADDED}\033[0m \033[31m-${REMOVED}\033[0m"

# Second line: vim mode, then the budgets -- context, then plan usage.
LINE2=""
[ -n "$VIM" ] && LINE2="\033[$(vim_color "$VIM")m${VIM}\033[0m  "
LINE2="${LINE2}\033[90mctx:${CTX}%\033[0m"
SEG=$(fmt_limit 5h "$RL5_PCT" "$RL5_AT") && [ -n "$SEG" ] && LINE2="${LINE2}  ${SEG}"
SEG=$(fmt_limit 7d "$RL7_PCT" "$RL7_AT") && [ -n "$SEG" ] && LINE2="${LINE2}  ${SEG}"

echo -e "$LINE"
echo -e "$LINE2"
exit 0
