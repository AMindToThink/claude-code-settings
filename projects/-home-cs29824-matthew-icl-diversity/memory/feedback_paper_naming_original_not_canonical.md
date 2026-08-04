---
name: The workshop paper is THE paper; the original is archived
description: paper/main_icml_workshop.tex is the canonical paper; the original journal-track wrapper has been archived under paper/archive/ and should be treated as a historical relic
type: feedback
originSessionId: b3c18550-c986-4b53-8115-979d3cce8e71
---
There is one active paper in this repo: `paper/main_icml_workshop.tex` (rendered as `paper/main_icml_workshop.pdf`). Treat it as THE paper. The original journal-track wrapper (`paper/archive/in_context_diversity_metric.tex` as of 2026-04-30) is archived and should be treated as a historical relic, not a sibling.

**Why:** The user explicitly archived the original on 2026-04-30: "It has outlived its usefulness and is now a historical relic. If we want to reframe the paper, we'll do so by starting with the workshop paper and making changes from there." Earlier in the migration (also 2026-04-30) they had already flagged that calling the original "canonical" inverts the relationship, since the workshop has corrections the original lacks.

**How to apply:**
- Default to "the paper" when referring to the workshop paper. No need to qualify with "workshop" unless disambiguating.
- If you do need to refer to the archived wrapper, call it "the archived original" or "the original journal-track wrapper" and use the `paper/archive/` path.
- Do not propose changes to anything under `paper/archive/` (including its section files: `abstract`, `01_motivation`, `03_progressive_conditioning`, `04_coherence`, `05_reporting`, `07_5_tevet`, `07_6_rlhf`, `08_limitations`, `acknowledgements`) without the user explicitly asking.
- Section files in `paper/sections/` without the `_workshop` suffix that are still used by the workshop (e.g., `02_setup`, `06_practical`, `09_future_work`, `10_related`, `appB_excess_entropy`, `appC_mcdiv_confounds`, `appD_aggregation`, `appE_qwen3_comparison`, `appF_rlhf_cross_metric`, and the appendix-only `07_*` files) are shared with the archived wrapper but only the workshop uses them now. Edits there are workshop edits.
- The archive is preserved in git history regardless; if the user ever asks to revive it, restore by reversing commit `25c9131` (the archive commit) and updating the wrapper's relative paths.
