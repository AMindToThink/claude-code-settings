---
name: Paper prose edits — one at a time, verify before continuing
description: When editing paper prose (abstract, intro, body), make one atomic change, explain it, and wait for verification before the next; flag any wording that shifts claims even slightly
type: feedback
originSessionId: 53b7ce05-4c5a-4951-993d-81ca5410d748
---
For edits to `paper/*.tex` prose, default to one visible change per turn, with a short explanation of what changed and why. Even under auto mode, paper prose is different from routine refactoring: a wording shift can change what the paper claims.

**Why:** Matthew explicitly asked for this pattern during the 2026-04-24 checklist pass ("Make your changes one at a time so I can verify them") and later ("Be very careful as you go not to change the meaning or the claims made in the paper"). Bulk prose rewrites are hard to review and easy to regress. Splitting into atomic changes preserves his ability to say "revert that one" without undoing everything.

**How to apply:**
- After each prose edit, name the change in one sentence (what + why).
- Explicitly flag any wording that tightens or loosens a claim — even if it seems consistent with the paper's evidence, name the shift and let Matthew confirm. Example: splitting a sentence that was bare methodology ("we validate on X") into one that makes a result claim ("X verifies the curve's behavior") is a meaning shift worth flagging.
- When doing pure-formatting reflows (e.g., `latexindent` / `format_paper_sentences.py`), commit semantic changes first so the formatting commit has zero meaning diff.
- Auto mode accelerates checklist-marking, verification commands, and script fixes — not paper prose batch rewrites.
- **Exception — already-triaged batches:** When Matthew has reviewed a list of proposed edits and given approval signals for the batch (e.g., "1, 2, 3 would be improvements" or "make the edits, I'll revert what I don't like"), just apply them rather than presenting a second round for confirmation. Showing already-discussed edits a second time before applying is the wrong default; reverting is cheap, second-round-presentation is friction. Confirmed 2026-04-30: "make the edits, and if I don't like them I'll just not apply them. I prefer this over you showing me the edits at once like you did here."
