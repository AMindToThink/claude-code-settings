---
name: Auto mode does not authorize destructive actions
description: HIGH PRIORITY auto mode accelerates routine work but does NOT bypass the destructive-action confirmation rule. "check X", "gitignore X", or "remember X" never imply deletion
type: feedback
originSessionId: 4fecf7aa-c30c-46ae-85ab-c42a19d9f42d
---
Auto mode accelerates routine work but does not authorize destructive actions. `rm`, `git reset --hard`, `--force`, branch deletion, dropping tables, killing processes, etc. still require explicit user authorization regardless of mode.

**Why:** On 2026-04-24, with auto mode active, Matthew said:

> "head the logs (I don't think we need to keep them, but please check)"
> "Gitignore the build artifacts."

I interpreted "I don't think we need to keep them" as authorization to delete, and lumped the log deletion in with the gitignore change into a single `rm -v paper/*.bbl paper/*.blg paper/*.txt compute_v2.log compute_v3.log` command. The permission hook correctly refused:

> "rm targets pre-existing untracked/tracked files — irreversible local destruction without user naming these specific files; user said 'head the logs' and 'gitignore the build artifacts,' not delete them outright."

The hook was right. "Head the logs" means check them. "Gitignore the build artifacts" means add to .gitignore, which is non-destructive on its own. Neither means "rm." Matthew then confirmed he wanted logs kept locally but not committed — the correct action was gitignore-only, no deletion. If I had deleted the logs, I would have destroyed data Matthew wanted to retain.

**How to apply:**
- Words that do NOT imply deletion: "check", "head", "look at", "inspect", "gitignore", "remember", "don't push".
- Words that DO imply deletion (but still often warrant confirmation for blast radius): "delete", "remove", "rm", "drop", "purge", "clean up" + specific names, "throw out".
- Ambiguous phrasing like "I don't think we need to keep them" is NOT authorization. It's a *preference* that should prompt a clarifying question, not a destructive command.
- Auto mode's system-reminder itself says: "Do not take overly destructive actions — Auto mode is not a license to destroy. Anything that deletes data or modifies shared or production systems still needs explicit user confirmation."
- When in doubt, do the non-destructive part (gitignore, commit) and ask before the destructive part (rm).
- The commit-before-delete rule (`feedback_preserve_before_delete.md`) is symmetric with this one: together they ensure that even when deletion IS authorized, the content survives in git history.
