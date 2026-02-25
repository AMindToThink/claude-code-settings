#!/bin/bash
# Claude Code statusline script
# Receives JSON on stdin with session info

DATA=$(cat)

CWD=$(echo "$DATA" | jq -r '.cwd // ""')
MODEL=$(echo "$DATA" | jq -r '.model.display_name // ""')
COST=$(echo "$DATA" | jq -r '.cost.total_cost_usd // 0' | xargs printf "%.3f")
CTX=$(echo "$DATA" | jq -r '.context_window.used_percentage // 0' | xargs printf "%.0f")
ADDED=$(echo "$DATA" | jq -r '.cost.total_lines_added // 0')
REMOVED=$(echo "$DATA" | jq -r '.cost.total_lines_removed // 0')

# Shorten home directory to ~
CWD="${CWD/#$HOME/~}"

# Git branch (from the cwd)
BRANCH=$(git -C "$(echo "$DATA" | jq -r '.cwd // "."')" rev-parse --abbrev-ref HEAD 2>/dev/null)

# Build the line
LINE=""
[ -n "$MODEL" ] && LINE="${LINE}\033[36m${MODEL}\033[0m"
[ -n "$CWD" ] && LINE="${LINE}  \033[33m${CWD}\033[0m"
[ -n "$BRANCH" ] && LINE="${LINE}  \033[35m${BRANCH}\033[0m"
LINE="${LINE}  \033[32m\$${COST}\033[0m"
LINE="${LINE}  \033[32m+${ADDED}\033[0m \033[31m-${REMOVED}\033[0m"
LINE="${LINE}  \033[90mctx:${CTX}%\033[0m"

echo -e "$LINE"
