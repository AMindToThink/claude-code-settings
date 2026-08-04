---
name: project_camera_ready_olmo_deferred
description: Camera-ready shipped style-only (2026-06-15); OLMo self-scoring + grader-invariance MERGED to main 2026-08-03 (arXiv v2 material)
metadata: 
  node_type: memory
  type: project
  originSessionId: 201966a3-e855-4c89-9641-e92157cb6bc4
  modified: 2026-08-03T22:00:16.407Z
---

The ICML'26 Human-AI Co-Creativity camera-ready (due 2026-06-15) was shipped **style-only**: commit `2cd07db` on main swaps the wrapper to `\usepackage[accepted]{icml2026_GenAICreativity}`. The PDF submitted to OpenReview on that date reflects that state; anything merged afterward is arXiv-v2 material, not what the workshop has.

**2026-08-03: the deferred OLMo self-scoring matrix is now MERGED into main** (merge commit `c663670`), extended well beyond the original deferral:
- Appendix `paper/sections/appG_olmo_self_scoring.tex` ("Grader Robustness"): pre-registered 5-grader matrix + exploratory cross-family tier (Llama-3.1-8B base, GPT-2 124M) + grader-vs-stage variance decomposition (stage ≈87-90%, grader ≈8-12%) + Tevet conTest grader-invariance analysis (4 graders, ρ vs human labels stable, item share 90-95% of z-scored variance).
- All numbers script-generated: `scripts/rlhf_experiment/7_matrix_paper_outputs.py`, `scripts/analyze_tevet_grader_invariance.py`; FINDINGS at `results/rlhf_experiment/matrix/FINDINGS.md` and `results/tevet/grader_invariance/FINDINGS.md`.
- Standalone preview: `paper/olmo_matrix_preview.tex`.
- GPT-2 caveat: 1024-token context excludes 13 AlpacaEval prompts (`--skip-over-context` sidecar, verified pair-exact by the analysis).
- Not pushed as of the merge; the `olmo-self-scoring` branch/worktree still exists (fully merged). Gitignored full Tevet per-permutation sidecars for the new tags were copied into main's `results/tevet/<tag>/conTest/`.

Remaining for an actual arXiv v2 release: the items in [[project_arxiv_conclusion_single_forward_pass]] (conclusion wording, DPO/RLVR arrow, title), plus flagging appG as a post-review addition. See [[project_icml_workshop_submission]].
