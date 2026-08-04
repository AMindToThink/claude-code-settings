---
name: project-arxiv-conclusion-single-forward-pass
description: "Next arXiv build of ICL-diversity paper — tighten conclusion's \"single forward pass\" to add \"per permutation\""
metadata: 
  node_type: memory
  type: project
  originSessionId: 250ba3c1-57a5-43a3-a154-cea69fbc6846
---

**Canonical, version-controlled copy of this list lives in the repo at `paper/arxiv_v2_todo.md`** (committed 2026-06-23 at Matthew's request so it travels with the repo and is visible to collaborators). Keep that file as the source of truth; this memory mirrors it for cross-session recall. `scripts/build_arxiv.sh` header points to it.

For the **next arXiv build** of the ICL-diversity paper, tighten the conclusion's phrase "in a single forward pass" to "in a single forward pass **per permutation**" to match the abstract.

**Why:** The bare "single forward pass" is loose. The metric runs **one forward pass per permutation** and averages over n_σ random permutations (variance reduction over orderings), so the full metric is n_σ passes, not one. The genuine claim is per-ordering: one pass over the concatenated responses scores all n responses' conditional surprises at once (causal LM, no need for n growing-prefix passes). The **abstract already states it correctly** ("a single forward pass per permutation", `paper/sections/abstract_workshop.tex`); only the conclusion (`paper/sections/conclusion_workshop.tex`, "in a single forward pass") dropped the qualifier. Matthew flagged this 2026-06-23.

**How to apply:** Do NOT edit the reviewed/camera-ready conclusion now. At the next arXiv build, change conclusion_workshop.tex "in a single forward pass" → "in a single forward pass per permutation". The poster (`paper/poster/`) already uses the precise "single forward pass per permutation" in its Takeaways bullet.

**Third arXiv-v2 fix (paper title is out of date on arXiv).** The arXiv v1 metadata title (verified 2026-06-23 on https://arxiv.org/abs/2606.01811) is the OLD SHORT title: "``I've Seen How This Goes'': Characterizing Diversity via Progressive Conditional Surprise". The camera-ready paper PDF, slide, and poster all use the CURRENT LONG title: "``I've Seen How This Goes'': Characterizing the Diversity of LLM Generations and Human Writing via Progressive Conditional Surprise". At the next arXiv version (replace/new version), update the title field to the long camera-ready title so arXiv matches the paper. (OpenReview's listing also still shows the short title; updating that is separate and optional.) Matthew asked to note this 2026-06-23.

**Second arXiv-v2 fix (DPO→RLVR arrow in the abstract).** `paper/sections/abstract_workshop.tex` line 6 reads "$D_{Ca_n}$ drops monotonically across the base $\to$ SFT $\to$ DPO $\to$ RLVR stages". The DPO$\to$RLVR arrow asserts a trend the paper does not claim (DPO-vs-RLVR is the exploratory H1' two-sided contrast, no directional prediction; see [[feedback_dpo_rlvr_approx_equals]]). At the next arXiv build, change the arrow chain to a plain comma list: "drops monotonically across the base, SFT, DPO, and RLVR stages" (a list does not assert pairwise direction; keeps "monotonically", which holds since 0.286 ≥ 0.281). This matches the poster's already-approved prose. Do NOT touch the camera-ready now. Flagged 2026-06-23 after Matthew confirmed submission #21 was accepted. Also check the body (07_6_rlhf_workshop.tex line 62 uses "base $\to$ SFT $\to$ DPO $\to$ Instruct (RLVR)") for the same arrow.
