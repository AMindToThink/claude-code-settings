#!/usr/bin/env python3
"""Find Claude Code chat transcripts that were active on a given local-time day.

Why this script exists: a naive `timestamp.startswith("YYYY-MM-DD")` filter
silently drops sessions a user clearly considers part of "yesterday" because
the JSONL timestamps are UTC and a session started at 23:30 local can have
first_ts=2026-05-02T04:30Z. We scan a UTC window wide enough to cover any
reasonable local timezone, then report each chat's actual UTC bounds so the
caller can decide.

Usage:
  scan_chats.py --date YYYY-MM-DD                  # local-day, system tz
  scan_chats.py --date YYYY-MM-DD --tz America/Chicago
  scan_chats.py --date YYYY-MM-DD --buffer-hours 6 # widen the UTC window
  scan_chats.py --date YYYY-MM-DD --project /path  # different project
  scan_chats.py --date YYYY-MM-DD --full-msgs      # show first user + tail
  scan_chats.py --date YYYY-MM-DD --unfinished-only

Output one line per matching chat (sorted by first timestamp), then optional
detail blocks. UTC timestamps are tagged with Z; --full-msgs adds a heuristic
[UNFINISHED?] flag for sessions whose final assistant turn looks like a
question with no user reply.
"""
import argparse
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

try:
    import zoneinfo
except ImportError:
    zoneinfo = None


def project_dir_from_path(cwd: Path) -> Path:
    """Map /home/foo/proj → ~/.claude/projects/-home-foo-proj."""
    name = "-" + str(cwd).strip("/").replace("/", "-")
    return Path.home() / ".claude" / "projects" / name


def get_text(msg) -> str:
    if not isinstance(msg, dict):
        return ""
    content = msg.get("content", "")
    if isinstance(content, str):
        return content
    if not isinstance(content, list):
        return str(content)
    parts = []
    for c in content:
        if not isinstance(c, dict):
            continue
        t = c.get("type")
        if t == "text":
            parts.append(c.get("text", ""))
        elif t == "tool_use":
            parts.append(f"[tool_use:{c.get('name', '?')}]")
        elif t == "tool_result":
            tr = c.get("content", "")
            if isinstance(tr, list):
                tr = " ".join(
                    x.get("text", "") if isinstance(x, dict) else str(x) for x in tr
                )
            parts.append(f"[tool_result:{str(tr)[:200]}]")
    return "\n".join(parts)


def parse_iso(ts: str):
    if not ts:
        return None
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except ValueError:
        return None


def is_real_user_msg(txt: str) -> bool:
    """A 'real' user message is one the user actually typed.
    Excludes tool_result echoes, system reminders, slash-command markers,
    bash-input/output echoes, and local-command-caveat markers.
    """
    if not txt:
        return False
    head = txt.lstrip()[:120]
    if head.startswith("[tool_result"):
        return False
    for marker in (
        "<system-reminder>",
        "<command-name>",
        "<command-message>",
        "<bash-input>",
        "<bash-stdout>",
        "<bash-stderr>",
        "<local-command-caveat>",
    ):
        if marker in head:
            return False
    return True


def scan_file(path: Path, start_utc: datetime, end_utc: datetime):
    """Return None if the chat had no message in [start_utc, end_utc); else a dict."""
    timestamps = []
    msgs = []  # (type, ts_dt, text)
    try:
        with path.open() as fh:
            for line in fh:
                try:
                    d = json.loads(line)
                except json.JSONDecodeError:
                    continue
                ts = parse_iso(d.get("timestamp", ""))
                if ts is None:
                    continue
                timestamps.append(ts)
                t = d.get("type")
                if t in ("user", "assistant"):
                    msgs.append((t, ts, get_text(d.get("message", {}))))
    except OSError as e:
        print(f"[skip] {path.name}: {e}", file=sys.stderr)
        return None
    if not timestamps:
        return None
    first, last = min(timestamps), max(timestamps)
    # Interval-overlap test
    if last < start_utc or first >= end_utc:
        return None
    return {"path": path, "first": first, "last": last, "msgs": msgs}


def first_user_text(msgs) -> str:
    for t, _, txt in msgs:
        if t == "user" and is_real_user_msg(txt):
            return txt
    return ""


def looks_unfinished(msgs) -> bool:
    """Heuristic: last assistant message asks a question and has no real user reply."""
    if not msgs:
        return False
    last_assistant_idx = None
    last_real_user_idx = None
    for i, (t, _, txt) in enumerate(msgs):
        if t == "assistant":
            last_assistant_idx = i
        elif t == "user" and is_real_user_msg(txt):
            last_real_user_idx = i
    if last_assistant_idx is None:
        return False
    if last_real_user_idx is not None and last_real_user_idx > last_assistant_idx:
        return False
    last_txt = msgs[last_assistant_idx][2].rstrip()
    if not last_txt:
        return False
    if last_txt.endswith("]"):  # cut off mid tool_use
        return True
    tail = last_txt[-500:]
    return "?" in tail


def fmt_utc(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%MZ")


def fmt_local(dt: datetime, tz) -> str:
    return dt.astimezone(tz).strftime("%Y-%m-%d %H:%M")


def resolve_tz(tz_name: str | None):
    if tz_name:
        if zoneinfo is None:
            raise RuntimeError("zoneinfo not available; install Python 3.9+")
        return zoneinfo.ZoneInfo(tz_name)
    return datetime.now().astimezone().tzinfo


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Find Claude Code chats active on a given local-time day."
    )
    ap.add_argument("--date", required=True, help="Local date as YYYY-MM-DD")
    ap.add_argument(
        "--tz",
        default=None,
        help="IANA timezone name (default: system; use this if system is UTC).",
    )
    ap.add_argument(
        "--buffer-hours",
        type=float,
        default=0.0,
        help="Extra slack (hours) on each side of the UTC window. "
        "Useful when you're unsure of timezone.",
    )
    ap.add_argument(
        "--project",
        default=None,
        help="Project path (default: current working directory).",
    )
    ap.add_argument(
        "--full-msgs",
        action="store_true",
        help="Print first user message and last 3 messages per chat.",
    )
    ap.add_argument(
        "--unfinished-only",
        action="store_true",
        help="Only show chats whose last assistant turn looks like an unanswered question.",
    )
    args = ap.parse_args()

    tz = resolve_tz(args.tz)

    try:
        y, m, d = (int(x) for x in args.date.split("-"))
        start_local = datetime(y, m, d, 0, 0, 0, tzinfo=tz)
    except (ValueError, TypeError):
        print(f"Invalid --date: {args.date!r}; want YYYY-MM-DD", file=sys.stderr)
        return 2
    end_local = start_local + timedelta(days=1)
    buf = timedelta(hours=args.buffer_hours)
    start_utc = start_local.astimezone(timezone.utc) - buf
    end_utc = end_local.astimezone(timezone.utc) + buf

    proj_path = Path(args.project).resolve() if args.project else Path.cwd()
    pd = project_dir_from_path(proj_path)
    if not pd.is_dir():
        print(f"No project dir at {pd}", file=sys.stderr)
        return 1

    print(f"Project dir : {pd}", file=sys.stderr)
    print(
        f"Local window: {start_local.isoformat()} → {end_local.isoformat()}",
        file=sys.stderr,
    )
    print(
        f"UTC window  : {fmt_utc(start_utc)} → {fmt_utc(end_utc)} "
        f"(buffer ±{args.buffer_hours:g}h)",
        file=sys.stderr,
    )

    hits = []
    for path in sorted(pd.glob("*.jsonl")):
        info = scan_file(path, start_utc, end_utc)
        if info is None:
            continue
        info["unfinished"] = looks_unfinished(info["msgs"])
        info["first_user"] = first_user_text(info["msgs"])
        if args.unfinished_only and not info["unfinished"]:
            continue
        hits.append(info)

    hits.sort(key=lambda h: h["first"])
    print(f"\n{len(hits)} chat(s):\n")
    for h in hits:
        flag = " [UNFINISHED?]" if h["unfinished"] else ""
        print(
            f"{h['path'].name}  "
            f"{fmt_utc(h['first'])} → {fmt_utc(h['last'])}  "
            f"({len(h['msgs'])} msgs){flag}"
        )
        if args.full_msgs:
            fu = h["first_user"][:300].replace("\n", " ")
            print(f"   first: {fu}")
            for t, ts, txt in h["msgs"][-3:]:
                truncated = txt[:300].replace("\n", " ")
                print(f"   [{t}] {fmt_utc(ts)}: {truncated}")
            print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
