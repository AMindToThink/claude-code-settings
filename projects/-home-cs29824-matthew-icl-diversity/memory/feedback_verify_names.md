---
name: Verify file and folder names
description: Always ls/glob to check actual names when user underspecifies — never guess punctuation like dash vs underscore
type: feedback
---

Always verify file/folder names with `ls` or `Glob` when the user gives an approximate name (e.g., "steering diversity"). Never guess punctuation (dash vs underscore, camelCase vs snake_case, etc.).

**Why:** Guessed `steering-diversity` instead of `steering_diversity`, which caused a script bug and a wasted round-trip. User explicitly said: "Please actually check folder and file names when I underspecify them."

**How to apply:** Any time a user references a file or folder without exact punctuation, run a quick `ls` or glob to confirm the actual name before using it in code, scripts, or commands.
