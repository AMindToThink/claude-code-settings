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
COST=$(echo "$DATA" | "$JQ" -r '.cost.total_cost_usd // 0' | xargs printf "%.3f")
CTX=$(echo "$DATA" | "$JQ" -r '.context_window.used_percentage // 0' | xargs printf "%.0f")
ADDED=$(echo "$DATA" | "$JQ" -r '.cost.total_lines_added // 0')
REMOVED=$(echo "$DATA" | "$JQ" -r '.cost.total_lines_removed // 0')

# Shorten home directory to ~
CWD="${CWD/#$HOME/~}"

# Git branch (from the cwd)
BRANCH=$(git -C "$(echo "$DATA" | "$JQ" -r '.cwd // "."')" rev-parse --abbrev-ref HEAD 2>/dev/null)

# Build the line
LINE=""
[ -n "$MODEL" ] && LINE="${LINE}\033[36m${MODEL}\033[0m"
[ -n "$CWD" ] && LINE="${LINE}  \033[33m${CWD}\033[0m"
[ -n "$BRANCH" ] && LINE="${LINE}  \033[35m${BRANCH}\033[0m"
LINE="${LINE}  \033[32m\$${COST}\033[0m"
LINE="${LINE}  \033[32m+${ADDED}\033[0m \033[31m-${REMOVED}\033[0m"
LINE="${LINE}  \033[90mctx:${CTX}%\033[0m"

echo -e "$LINE"
