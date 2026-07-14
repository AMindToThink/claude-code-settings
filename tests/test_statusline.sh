#!/bin/bash
# Tests for ~/.claude/statusline.sh
# Run: bash ~/.claude/tests/test_statusline.sh

STATUSLINE="$HOME/.claude/statusline.sh"
NOW=$(date +%s)
FAILURES=0

# Feed a JSON payload to the statusline, return its full output with ANSI
# escapes made visible as literal "ESC[..m" so we can assert on colors.
render() {
    printf '%s' "$1" | bash "$STATUSLINE" | sed 's/\x1b\[/ESC[/g'
}

# Just line N of the rendered output.
render_line() {
    render "$2" | sed -n "$1p"
}

# Number of lines the statusline printed.
render_nlines() {
    render "$1" | wc -l
}

expect_contains() {
    local desc="$1" haystack="$2" needle="$3"
    if [[ "$haystack" == *"$needle"* ]]; then
        echo "PASS: $desc"
    else
        echo "FAIL: $desc"
        echo "      expected to contain: $needle"
        echo "      got:                 $haystack"
        FAILURES=$((FAILURES + 1))
    fi
}

expect_not_contains() {
    local desc="$1" haystack="$2" needle="$3"
    if [[ "$haystack" != *"$needle"* ]]; then
        echo "PASS: $desc"
    else
        echo "FAIL: $desc"
        echo "      expected NOT to contain: $needle"
        echo "      got:                     $haystack"
        FAILURES=$((FAILURES + 1))
    fi
}

payload() {
    # $1 = extra JSON keys (may be empty)
    cat <<EOF
{
  "cwd": "$HOME/.claude",
  "model": {"display_name": "Opus 4.8"},
  "cost": {"total_cost_usd": 1.234, "total_lines_added": 10, "total_lines_removed": 2},
  "context_window": {"used_percentage": 45.0}
  ${1:+, $1}
}
EOF
}

# Countdowns truncate, and the script reads the clock a moment after this test
# does, so offsets carry ~30s of slack to stay off the minute boundary:
# 1h12m30s -> "1h12m", 3d4h30s -> "3d4h".
BOTH_LIMITS="\"rate_limits\": {
  \"five_hour\": {\"used_percentage\": 23.5, \"resets_at\": $((NOW + 4350))},
  \"seven_day\": {\"used_percentage\": 41.2, \"resets_at\": $((NOW + 273630))}
}"

VIM_INSERT="\"vim\": {\"mode\": \"INSERT\"}"

# 1. Layout: line 1 is identity + spend, line 2 is mode + the budgets.
#    Always exactly 2 lines.
FULL="$(payload "$BOTH_LIMITS, $VIM_INSERT")"
L1=$(render_line 1 "$FULL")
L2=$(render_line 2 "$FULL")
expect_contains "line 1 keeps model and cost" "$L1" "Opus 4.8"
expect_not_contains "line 1 carries no context usage" "$L1" "ctx:"
expect_not_contains "line 1 carries no plan usage" "$L1" "5h:"
expect_contains "line 2 leads with the vim mode" "$L2" "INSERT"
expect_contains "line 2 renders context usage" "$L2" "ctx:45%"
expect_contains "line 2 renders 5h percent and countdown" "$L2" "5h:24% (1h12m)"
expect_contains "line 2 renders 7d percent and countdown" "$L2" "7d:41% (3d4h)"
[[ "$L2" == *"INSERT"*"ctx:"*"5h:"*"7d:"* ]] \
    && echo "PASS: line 2 order is mode -> ctx -> 5h -> 7d" \
    || { echo "FAIL: line 2 order is mode -> ctx -> 5h -> 7d ($L2)"; FAILURES=$((FAILURES + 1)); }
N=$(render_nlines "$FULL")
[ "$N" -eq 2 ] \
    && echo "PASS: exactly 2 lines" \
    || { echo "FAIL: exactly 2 lines (got $N)"; FAILURES=$((FAILURES + 1)); }

# 2. rate_limits absent (API-key users, or before the first API response):
#    line 2 still exists for ctx, just without the plan segments.
OUT=$(render "$(payload)")
expect_contains "ctx still renders without rate_limits" "$OUT" "ctx:45%"
expect_not_contains "no 5h segment when rate_limits absent" "$OUT" "5h:"
expect_not_contains "no 7d segment when rate_limits absent" "$OUT" "7d:"
N=$(render_nlines "$(payload)")
[ "$N" -eq 2 ] \
    && echo "PASS: still 2 lines when rate_limits absent" \
    || { echo "FAIL: still 2 lines when rate_limits absent (got $N lines)"; FAILURES=$((FAILURES + 1)); }

# 3. Only one window present -- each may be independently absent.
ONLY_7D="\"rate_limits\": {\"seven_day\": {\"used_percentage\": 5, \"resets_at\": $((NOW + 630))}}"
L2=$(render_line 2 "$(payload "$ONLY_7D")")
expect_contains "7d alone still renders on line 2" "$L2" "7d:5% (10m)"
expect_not_contains "no 5h segment when only 7d present" "$L2" "5h:"

# 4. Vim mode: absent when vim mode is off; colored per mode when on.
L2=$(render_line 2 "$(payload)")
[[ "$L2" == ESC\[90mctx:* ]] \
    && echo "PASS: line 2 starts at ctx when vim mode is off" \
    || { echo "FAIL: line 2 starts at ctx when vim mode is off ($L2)"; FAILURES=$((FAILURES + 1)); }
L2=$(render_line 2 "$(payload "$VIM_INSERT")")
expect_contains "INSERT renders green" "$L2" "ESC[1;32mINSERTESC[0m"
L2=$(render_line 2 "$(payload "\"vim\": {\"mode\": \"NORMAL\"}")")
expect_contains "NORMAL renders blue" "$L2" "ESC[1;34mNORMALESC[0m"
L2=$(render_line 2 "$(payload "\"vim\": {\"mode\": \"VISUAL LINE\"}")")
expect_contains "VISUAL LINE renders yellow" "$L2" "ESC[1;33mVISUAL LINEESC[0m"

# 5. Effort level sits immediately after the model name.
OUT=$(render_line 1 "$(payload "\"effort\": {\"level\": \"xhigh\"}")")
expect_contains "effort follows the model name" "$OUT" "ESC[36mOpus 4.8ESC[0m ESC[90mxhighESC[0m"
# Absent when the model does not support the effort parameter.
OUT=$(render_line 1 "$(payload)")
expect_contains "model still renders without effort" "$OUT" "ESC[36mOpus 4.8ESC[0m"
expect_not_contains "no effort text when effort is absent" "$OUT" "xhigh"

# 6. resets_at already past -> "now" rather than a negative countdown.
OUT=$(render "$(payload "\"rate_limits\": {\"five_hour\": {\"used_percentage\": 0, \"resets_at\": $((NOW - 60))}}")")
expect_contains "past reset time shows 'now'" "$OUT" "5h:0% (now)"

# 7. Color thresholds: gray < 70 <= yellow < 90 <= red.
OUT=$(render "$(payload "\"rate_limits\": {\"five_hour\": {\"used_percentage\": 12, \"resets_at\": $((NOW + 3600))}}")")
expect_contains "low usage is gray (90)" "$OUT" "ESC[90m5h:12%"
OUT=$(render "$(payload "\"rate_limits\": {\"five_hour\": {\"used_percentage\": 75, \"resets_at\": $((NOW + 3600))}}")")
expect_contains "high usage is yellow (33)" "$OUT" "ESC[33m5h:75%"
OUT=$(render "$(payload "\"rate_limits\": {\"five_hour\": {\"used_percentage\": 96.4, \"resets_at\": $((NOW + 3600))}}")")
expect_contains "critical usage is red (31)" "$OUT" "ESC[31m5h:96%"

echo
if [ "$FAILURES" -eq 0 ]; then
    echo "All tests passed."
else
    echo "$FAILURES test(s) failed."
    exit 1
fi
