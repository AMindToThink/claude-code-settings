---
name: Don't elaborate cited-work descriptions with unsupported claims
description: When describing cited papers/datasets/benchmarks, stick to what the local source supports; resist strengthening adjectives or implied protocol details that aren't there
type: feedback
originSessionId: ac479e89-11e5-453f-91b5-7a066a8b5c3e
---
When describing cited work — a paper, dataset, benchmark, prior method — stick to what the local source supports. Don't add strengthening adjectives, implied protocols, or attribution details that aren't directly in the source. If I'm tempted to add a strengthening word to a draft, ask "does this come from the source or from me?"

**Why:** in conversation 2026-04-27 I described Tevet's McDiv labels as assigned by "*separate* independent workers" — adding "separate" beyond what the prior md said and beyond what App C of our local paper supports. App C describes a *construction* protocol where the same worker writes the high-diversity set (5 different continuations) and the low-diversity set (5 paraphrases of one of those continuations), which directly contradicts "separate raters." The user caught it. This is the same failure shape as fabricating citation metadata, just at the prose-elaboration level rather than the bibliography level — and the same shape as an earlier incident where the user had to ask "did we actually compare with EAD/SentBERT?" because I'd asserted it from the paper text without verifying the code/data existed.

**How to apply:**
- When describing source material (paper, dataset, benchmark, prior method), default to weaker descriptive language over rhetorical strengthening. "Workers wrote the responses" beats "*independent* workers wrote the responses." "Labels grounded in human judgment" beats "labels assigned by *separate* independent workers."
- Before sending an Edit that contains an adjective or attribution detail about a cited work, run a mental check: "is this in the source I have, or am I elaborating?"
- If unsure, either grep/read the source to confirm, or remove the contested clause. The user noticing a fabricated detail costs more trust than the absence of a detail.
- Related guards already in memory: `feedback_citations_no_handtyping.md` (bibliography metadata), `feedback_verify_claims_on_citation_add.md` (claim-support audit). This memory covers the third leg: prose-level elaboration of already-cited work.
