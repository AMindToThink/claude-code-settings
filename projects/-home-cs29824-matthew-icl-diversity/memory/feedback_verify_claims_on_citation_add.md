---
name: Run verify-citation-claims skill automatically on citation additions
description: HIGH PRIORITY after ANY new citation added to refs_ids.toml, run verify-citation-claims skill (not just verify_cites.py lint) to check the claim the paper attributes to it is actually in the cited paper
type: feedback
originSessionId: 4fecf7aa-c30c-46ae-85ab-c42a19d9f42d
---
After adding any new citation, run the `verify-citation-claims` skill as part of the addition — not as a separate user-triggered step.

**Why:** On 2026-04-24 I added `du2019boosting` and `lai2020diversity` to the ICL-diversity paper. The `verify_cites.py` lint passed (13 keys resolved), `build_bib.py` passed (metadata fetched from ACL / arXiv), and I reported the addition done. Matthew had to explicitly ask: "Please use our bibliography skills to make sure that our new citations are correct." The verify-citation-claims skill then caught a real mischaracterization — Lai's *diversity* metric was described as a "volume" in our prose, but Eq. 3 of the actual paper defines it as the geometric mean of per-axis standard deviations (a length scale, not a volume). The volume-like quantity appears in Lai's *density* metric, not diversity. This is exactly the miscitation failure mode the verify-citation-claims skill exists to catch — and it was latent in our paper for an hour because I treated `verify_cites.py` (metadata lint) as sufficient.

**How to apply:**
- `scripts/verify_cites.py` only checks that each `\cite{}` key resolves to a bib entry. It does NOT check that the entry supports the claim.
- `scripts/build_bib.py` only checks that the identifier resolves via arXiv / DOI / ACL. It does NOT check that the paper at that identifier makes the claim our prose attributes to it.
- After any citation addition, invoke the `verify-citation-claims` skill. For a single new citation, a single WebFetch of `ar5iv.labs.arxiv.org/html/<id>` or the ACL Anthology URL, asking the model to locate the specific section/equation supporting the claim, is enough. For 2+ citations, dispatch parallel subagents.
- Sign that this check is needed: the citation's prose makes a specific factual claim (a method name, a number, a framing) about what the cited paper does. If the prose only says "see [cite] for background," the claim is weaker and the check is optional. If the prose says "X introduced [method] [cite]," the check is mandatory.
- This is a stronger version of `feedback_citations_no_handtyping.md`: that memory prevents fabricated metadata (wrong authors, wrong year). This memory prevents fabricated claims (correct paper, wrong description of what it did). Both failure modes appeared in the 2026-04-21 audit of this paper.
