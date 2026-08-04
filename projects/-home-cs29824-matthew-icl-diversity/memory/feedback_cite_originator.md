---
name: Cite the originator of an approach, not a downstream user
description: HIGH PRIORITY when citing "existing approaches" / "prior work" for a claim, cite the earliest / originator paper, not a recent follow-up - even if the follow-up is more convenient or already in the bib
type: feedback
originSessionId: 4fecf7aa-c30c-46ae-85ab-c42a19d9f42d
---
Cite the originator of an approach, not a downstream user.

**Why:** In the 2026-04-24 session on the ICL-diversity paper, I repeatedly reached for convenient-but-downstream citations when motivating "existing approaches measure diversity via embedding-based metrics." First I cited Diaz-Rodriguez 2025 (a k-LLMmeans *clustering-algorithm* paper, not a diversity-measurement paper). Then, after Matthew pushed back, I cited Lai 2020 (a niche geometric-mean-of-standard-deviations metric for *text collections*, not LLM outputs). Matthew pushed back a third time: **"It is best practice to cite the originator of an approach."** A literature-archaeology subagent (dispatched on request) confirmed Du and Black 2019 (ACL P19-1005, "Boosting Dialog Response Generation") is the earliest unambiguous instance of a scalar sentence-embedding-based diversity metric on generated text, and Tevet and Berant 2021 §2 treat them as the canonical originator. Recent and convenient papers are not substitutes for the origin.

**How to apply:**
- For broad claims about prior work ("existing approaches do X," "prior work has Y"), identify and cite the *originator*, even if a more-recent paper in the bib also does X.
- If uncertain about the originator, dispatch a literature-archaeology subagent: trace backward through the field's related-work lineage, rule out candidates per-paper-read (not hearsay), return a clear "X is the originator" or "no single originator, here are the earliest candidates." Don't guess.
- Cheap fallback: check what the canonical secondary source (survey / review / benchmark paper in the field) cites as the origin. Tevet and Berant 2021 §2 is the canonical secondary source for NLG-diversity-metric lineage; analogous survey papers exist in other subfields.
- Do NOT default to a recent-or-convenient paper just because it's already in the bib. That optimizes the wrong thing.
- Sign that you're about to make this mistake: the candidate citation is for a paper whose *main contribution* is not the approach you're citing it for (e.g., a clustering-algorithm paper cited as an example of diversity measurement, or a text-collection-characterization paper cited as an example of LLM-output diversity).

**Also:** This is symmetric with `feedback_citations_no_handtyping.md` (which prevents fabricated metadata). Together they cover the two orthogonal citation failure modes: (a) lying about *who* a paper is by (hand-typing wrong authors), and (b) lying about *what the paper did* by citing a downstream user when the prose describes the originator's contribution.
