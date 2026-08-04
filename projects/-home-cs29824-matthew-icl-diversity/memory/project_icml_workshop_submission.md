---
name: ICML workshop submission lives on main; worktree removed
description: As of 2026-04-30, the workshop branch was merged into main and the worktree was removed; edit paper/sections/ on main
type: project
originSessionId: 9d6c158e-13d9-4837-8b45-38cca1a59479
---
Matthew is preparing the ICML workshop submission. The workshop paper compiles from `paper/main_icml_workshop.tex` and pulls section sources from `paper/sections/*.tex`. As of 2026-04-30, the `workshop-icml2026` branch has been merged into `main` (merge commit `c5e6d68`), and the `.worktrees/workshop-icml2026/` worktree has been removed. All workshop content now lives on `main` in the primary working tree at `/home/cs29824/matthew/icl-diversity/paper/`.

**Why:** Earlier in the workshop adaptation (Phase 2/3), edits were isolated in the worktree. That work has since landed on main. After confirming nothing of value remained in the worktree (the only uncommitted modification was a superseded version of `03_method_workshop.tex`), the worktree was force-removed on 2026-04-30.

**How to apply:** When the user asks to edit "the paper", a section, or rebuild the PDF, default to `paper/sections/` on main. The workshop variant (`paper/main_icml_workshop.tex`) is the **active** paper and is more up-to-date than the **original** (`paper/in_context_diversity_metric.tex`). Refer to the non-workshop wrapper as the "original" paper, not "canonical" (see `feedback_paper_naming_original_not_canonical.md`). Only touch `in_context_diversity_metric.tex` when the user explicitly names it.
