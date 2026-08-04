---
name: deliverables-in-repo-not-scratchpad
description: "Files Matthew will open (PDFs, previews, reports) go in the repo, never the Claude scratchpad"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 9b55321d-037a-4a3f-802e-2a49bcd02f03
  modified: 2026-08-03T19:30:12.473Z
---

Do not place files Matthew will want to open (compiled PDFs, previews, generated reports) in the Claude scratchpad under /tmp.

**Why:** Matthew browses files through VSCode, which is rooted at the repo; the session scratchpad is invisible there and vanishes with the session.

**How to apply:** Put human-facing artifacts inside the repo at a gitignored location. For paper preview PDFs use `paper/build/` (gitignored via the `build/` rule; precedent: `paper/rlhf_experiment_preview.pdf` had its own gitignore entry). Reserve the scratchpad for genuinely temporary intermediates (logs, temp scripts, page renders) that only Claude reads. Sending a file with SendUserFile does not replace putting it somewhere findable on disk.
