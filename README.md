# Claude Code Settings

Personal Claude Code configuration for syncing setup across machines.

## What's Included

| File | Purpose |
|---|---|
| `settings.json` | Hooks, status line, permissions, effort level |
| `statusline.sh` | Script that renders the status bar (model, cost, context %, lines changed) |
| `CLAUDE.md` | Global instructions applied to every project |
| `skills/` | Custom slash commands (e.g., `/archive-logs`) |
| `agents/` | Custom subagent definitions |

## Setup on a New Machine

### Prerequisites

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) installed
- [terminal-notifier](https://github.com/julienXX/terminal-notifier) for notification hooks: `brew install terminal-notifier`
- `jq` for the status line script: `brew install jq`

### Install

```bash
# Back up existing config if needed
[ -d ~/.claude ] && mv ~/.claude ~/.claude.backup

# Clone
git clone https://github.com/AMindToThink/claude-code-settings.git ~/.claude

# Make the status line script executable
chmod +x ~/.claude/statusline.sh
```

Claude Code will auto-create the missing runtime directories (`todos/`, `statsig/`, `projects/`, etc.) on first launch.

### Verify

Launch `claude` — you should see the status bar at the bottom:
```
Opus 4.6  ~/current/dir  $0.000  +0 -0  ctx:0%
```

## Maintenance

After changing settings on any machine:

```bash
cd ~/.claude
git add -u
git commit -m "Update settings"
git push
```

On other machines: `cd ~/.claude && git pull`

## Notes

- The `.gitignore` excludes all runtime state (history, caches, session data, todos, etc.)
- MCP server OAuth tokens are not portable — re-authenticate on each machine
- The `CLAUDE.md` contains personalized instructions (name, workflow preferences)
