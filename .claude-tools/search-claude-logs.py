#!/usr/bin/env python3
"""Search Claude Code conversation logs for tool outputs matching a pattern.

Searches JSONL conversation logs for bash/tool outputs containing the given
pattern. Useful for recovering results from past conversations where a script
computed values but never saved them to a file.

Usage:
    .claude-tools/search-claude-logs.py <pattern> [--project <project-path>] [--context <lines>]

Examples:
    .claude-tools/search-claude-logs.py "pass@1.*0.432"
    .claude-tools/search-claude-logs.py "power analysis" --context 20
    .claude-tools/search-claude-logs.py "0.432" --project ~/.claude/projects/-home-cs29824-matthew-other-project
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path


def find_project_log_dir() -> Path | None:
    """Find the Claude project log directory for the current working directory."""
    cwd = os.getcwd()
    claude_projects = Path.home() / ".claude" / "projects"
    if not claude_projects.exists():
        return None
    # Claude Code encodes project paths in a way that's not simply replacing
    # / with - (underscores may also become dashes). Match by checking if
    # the cwd path components appear in order in the directory name.
    cwd_parts = [p for p in cwd.split("/") if p]  # e.g. ['home','cs29824','matthew','steering_diversity']
    # Normalize cwd to the same format Claude uses: replace / and _ with -
    cwd_normalized = cwd.lstrip("/").replace("/", "-").replace("_", "-")
    best_match: Path | None = None
    best_len_diff = float("inf")
    for candidate in claude_projects.iterdir():
        if not candidate.is_dir():
            continue
        name = candidate.name.lstrip("-")
        # Check if the normalized cwd starts with or equals the dir name
        if cwd_normalized == name:
            return candidate  # exact match
        # Check if the dir name is a prefix of cwd (subproject)
        # or cwd is a prefix of the dir name — prefer shortest surplus
        if cwd_normalized.startswith(name):
            diff = len(cwd_normalized) - len(name)
            if diff < best_len_diff:
                best_len_diff = diff
                best_match = candidate
        elif name.startswith(cwd_normalized):
            diff = len(name) - len(cwd_normalized)
            if diff < best_len_diff:
                best_len_diff = diff
                best_match = candidate
    return best_match


def search_logs(
    log_dir: Path,
    pattern: str,
    context_lines: int,
) -> None:
    """Search JSONL conversation logs for tool outputs matching pattern."""
    regex = re.compile(pattern, re.IGNORECASE)
    jsonl_files = sorted(log_dir.glob("*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True)

    if not jsonl_files:
        print(f"No .jsonl files found in {log_dir}", file=sys.stderr)
        sys.exit(1)

    print(f"Searching {len(jsonl_files)} conversation logs in {log_dir}...\n", file=sys.stderr)

    matches_found = 0
    for jsonl_path in jsonl_files:
        with open(jsonl_path, errors="replace") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue

                # Extract stdout from tool results
                stdout = None
                if entry.get("type") == "tool_result":
                    tr = entry.get("toolUseResult", {})
                    stdout = tr.get("stdout", "")
                elif isinstance(entry.get("message"), dict):
                    content = entry["message"].get("content", [])
                    if isinstance(content, list):
                        for block in content:
                            if isinstance(block, dict) and block.get("type") == "tool_result":
                                text = block.get("content", "")
                                if isinstance(text, str):
                                    stdout = text

                if not stdout or not regex.search(stdout):
                    continue

                matches_found += 1
                conv_id = jsonl_path.stem[:12]
                print(f"=== Match #{matches_found} in {conv_id}... (line {line_num}) ===")

                # Show matching portion with context
                output_lines = stdout.splitlines()
                for i, ol in enumerate(output_lines):
                    if regex.search(ol):
                        start = max(0, i - context_lines)
                        end = min(len(output_lines), i + context_lines + 1)
                        for j in range(start, end):
                            marker = ">>>" if j == i else "   "
                            print(f"{marker} {output_lines[j]}")
                        print()

    if matches_found == 0:
        print(f"No matches for pattern: {pattern}", file=sys.stderr)
    else:
        print(f"Found {matches_found} matching tool output(s).", file=sys.stderr)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Search Claude Code conversation logs for tool outputs matching a pattern.",
    )
    parser.add_argument("pattern", help="Regex pattern to search for in tool outputs")
    parser.add_argument(
        "--project", type=str, default=None,
        help="Path to Claude project log directory (default: auto-detect from cwd)",
    )
    parser.add_argument(
        "--context", type=int, default=5,
        help="Number of context lines around each match (default: 5)",
    )
    args = parser.parse_args()

    if args.project:
        log_dir = Path(args.project).expanduser()
    else:
        log_dir = find_project_log_dir()

    if log_dir is None or not log_dir.exists():
        print("Error: could not find Claude project log directory.", file=sys.stderr)
        print("Specify with --project <path>", file=sys.stderr)
        sys.exit(1)

    search_logs(log_dir, args.pattern, args.context)


if __name__ == "__main__":
    main()
