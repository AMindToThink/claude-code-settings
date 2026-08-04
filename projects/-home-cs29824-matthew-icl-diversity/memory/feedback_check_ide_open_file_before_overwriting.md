---
name: Check git status before overwriting a file the user has open in their IDE
description: When the system reminder says a file is open in the user's IDE, run `git diff` (and ask if needed) before any `cp`/`mv` that overwrites that path. IDE buffers may hold unsaved user edits.
type: feedback
originSessionId: ed2cb122-3a59-44e7-9762-901f8d3dcde5
---
When a system reminder says "the user opened the file X in the IDE", treat that as a signal to be careful with mutations to X — not to ignore. Before any `cp`, `mv`, redirect, or other destructive operation that overwrites X:

1. Run `git diff -- X` to see whether the user has uncommitted edits already on disk.
2. If the path-on-disk differs from `HEAD` in a way you didn't author, **stop and ask** before overwriting.
3. If on-disk matches `HEAD` but the IDE-open reminder is recent, ask whether they have unsaved edits in the IDE buffer.

**Why**: During the LaTeX formatter work (2026-04-24), the user was editing figure 1 in their IDE while I was running `cp /tmp/backup.tex paper/X.tex` repeatedly during a build-state debugging cycle. I overwrote a state that may have included their unsaved edits. They confirmed afterward "my changes weren't that important" — a near-miss, not a hit, but the failure mode is real and irreversible (an IDE may not auto-save, and `git` cannot recover an unsaved buffer).

**How to apply**: Whenever the conversation includes a `<system-reminder>` of the form "user opened file X in IDE", that file becomes "yellow-flagged" for the rest of the session: check `git diff` before any operation that writes to X, regardless of how routine. Auto-mode does not change this — auto-mode accelerates routine work, not destructive overwrites of paths the user is actively touching.
