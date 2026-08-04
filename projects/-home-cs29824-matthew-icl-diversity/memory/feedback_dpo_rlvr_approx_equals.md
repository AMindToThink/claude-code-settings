---
name: feedback-dpo-rlvr-approx-equals
description: "Between OLMo DPO and RLVR Decan values, ALWAYS use approximately-equals (≈), never an arrow/trend"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 250ba3c1-57a5-43a3-a154-cea69fbc6846
---

In any presentation of the OLMo-2-7B post-training stage sequence (base → SFT → DPO → RLVR Decan values, e.g. `0.481 → 0.329 → 0.286 ≈ 0.281`), the connector **between DPO and RLVR must be approximately-equals (≈ / `&asymp;` in HTML, `~=` in plain text), never an arrow `→`**.

**Why:** The paper pre-registers only three contrasts: H1a base>SFT, H1b SFT>DPO, H1c base>RLVR. DPO-vs-RLVR is the **exploratory H1′ two-sided contrast with NO directional prediction** ("we have no directional prediction for which post-training stage loses more diversity", `paper/sections/07_6_rlhf_workshop.tex`). An arrow between DPO (0.286) and RLVR (0.281) falsely implies a trend / ordered drop we have no theoretical or empirical basis to claim. Matthew flagged this hard ("ALWAYS use approximately equals for those two") on 2026-06-23. Related: [[feedback_dectest_boring]] (don't over-read post-training stage noise), [[feedback_caption_actual_content]].

**How to apply:** base→SFT→DPO use `→` (those drops are claimed/significant); DPO↔RLVR uses `≈`. "Decreases/drops monotonically across the stages" prose is fine and stays (0.286 ≥ 0.281 is non-increasing; the poster and paper both keep it). The poster (`paper/poster/icl_diversity_poster.html`) already uses `&asymp;`; the slide and narration script were fixed to match. Apply the same to any new figure, slide, arXiv v2 edit, or talk.
