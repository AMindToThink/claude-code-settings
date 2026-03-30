---
name: Check for uncommitted changes before submodule operations
description: Always check git status before running git submodule update to avoid overwriting work
type: feedback
---

Before running `git submodule update --init` or similar submodule operations, always check `git status` and `git diff` first to make sure there aren't uncommitted changes that could be overwritten.

**Why:** Matthew caught me about to run a submodule update without checking for existing changes first. Submodule operations can overwrite local state.

**How to apply:** Any time you need to init/update submodules (especially in worktrees), run `git status` and `git diff` first, verify nothing would be lost, and only then proceed.
