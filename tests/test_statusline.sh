#!/bin/bash
# Tests for ~/.claude/statusline.sh
# Run: bash ~/.claude/tests/test_statusline.sh

STATUSLINE="$HOME/.claude/statusline.sh"
NOW=$(date +%s)
FAILURES=0

# Feed a JSON payload to the statusline, return its rendered line with ANSI
# escapes made visible as literal "ESC[..m" so we can assert on colors.
render() {
    printf '%s' "$1" | bash "$STATUSLINE" | sed 's/\x1b\[/ESC[/g'
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

# 1. Both windows present: percentage + time until refresh, 5h before 7d.
OUT=$(render "$(payload "\"rate_limits\": {
  \"five_hour\": {\"used_percentage\": 23.5, \"resets_at\": $((NOW + 4320))},
  \"seven_day\": {\"used_percentage\": 41.2, \"resets_at\": $((NOW + 273600))}
}")")
expect_contains "5h window renders percent and countdown" "$OUT" "5h:24% (1h12m)"
expect_contains "7d window renders percent and countdown" "$OUT" "7d:41% (3d4h)"
expect_contains "limits come after context usage" "$OUT" "ctx:45%"
[[ "$OUT" == *"ctx:45%"*"5h:"*"7d:"* ]] \
    && echo "PASS: ordering is ctx -> 5h -> 7d" \
    || { echo "FAIL: ordering is ctx -> 5h -> 7d ($OUT)"; FAILURES=$((FAILURES + 1)); }

# 2. rate_limits absent (API-key users, or before the first API response).
OUT=$(render "$(payload)")
expect_contains "renders normally without rate_limits" "$OUT" "ctx:45%"
expect_not_contains "no 5h segment when rate_limits absent" "$OUT" "5h:"
expect_not_contains "no 7d segment when rate_limits absent" "$OUT" "7d:"

# 3. Only one window present -- each may be independently absent.
OUT=$(render "$(payload "\"rate_limits\": {\"seven_day\": {\"used_percentage\": 5, \"resets_at\": $((NOW + 600))}}")")
expect_contains "7d alone still renders" "$OUT" "7d:5% (10m)"
expect_not_contains "no 5h segment when only 7d present" "$OUT" "5h:"

# 4. resets_at already past -> "now" rather than a negative countdown.
OUT=$(render "$(payload "\"rate_limits\": {\"five_hour\": {\"used_percentage\": 0, \"resets_at\": $((NOW - 60))}}")")
expect_contains "past reset time shows 'now'" "$OUT" "5h:0% (now)"

# 5. Color thresholds: gray < 70 <= yellow < 90 <= red.
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
