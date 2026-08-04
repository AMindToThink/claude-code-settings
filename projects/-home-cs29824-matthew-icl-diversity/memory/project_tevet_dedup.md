---
name: Tevet McDiv "dedup" flag is deactivated; conflicts are pair structure, not contamination
description: Do not pass --dedup to compute_icl_metrics_for_tevet; do not reintroduce a "Label Contamination" claim in the paper
type: project
originSessionId: fb65e212-c891-4c3a-a565-d831dc204ffb
---
McDiv_nuggets has rows that share a context but have fully disjoint five-response sets. These are the surviving fragment of Tevet's ConTest pair structure (high-div / low-div response sets for the same prompt) preserved into the McDiv_nuggets HDS-labeled subset, NOT contamination. An earlier session mistook them for duplicates and added a `--dedup` flag plus a "Label Contamination" appendix subsection; both have been removed.

**How to apply:**
- Do NOT pass `--dedup` to `scripts/compute_icl_metrics_for_tevet.py` (the flag now hard-fails).
- Do NOT re-introduce a "Label Contamination" claim in the paper.
- If a future agent sees the conflicting-label pairs and wants to "fix" them, point them at `investigations/tevet_overlap_followup.md` first.
