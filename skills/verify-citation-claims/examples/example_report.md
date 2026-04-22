# Example Citation Verification Report (fictional)

This is a sanitized, fictional example of the output produced by the
`verify-citation-claims` skill. Use it as a template for the real report
your skill invocation should write to `paper/citation_verification_report.md`
(or similar location).

Real reports made on this template during the 2026-04-21 audit of a
12-citation paper discovered: 4 fabricated author lists, 1 unsupported
claim, 1 wrong journal volume, 4 title typos. Every one of these was
catchable by a parallel subagent dispatched with the prompt template in
SKILL.md Step 3.

---

# Citation Verification Report

Date: YYYY-MM-DD
Paper: `paper/your_paper.tex`
Method: Each citation was verified by a parallel subagent that located
the cited paper via arXiv / Crossref / ACL Anthology and cross-checked
the specific claim in our paper against the cited source.

## Summary Table

| Bibkey | Status | Severity | Issue |
|---|---|---|---|
| `smith2020foo` | **Verified** | — | Numbers match Table 3 exactly |
| `jones2021bar` | Minor | LOW | Paper year in our bib is 2021; arXiv submission year is 2020 |
| `patel2023baz` | **Wrong number** | MEDIUM | Parameter count in our prose (1.5B) is 1.7B in the actual paper, §2 |
| `chen2024quux` | **FABRICATED authors** | HIGH | Our bib lists "Chen et al."; actual first author is Liu |
| `kim2024xyz` | **Unsupported claim** | HIGH | Our prose says X uses method Y; paper actually uses method Z |
| `author2019report` | **Verified** | — | Manual entry cross-checked against PDF at cited URL |

**High-severity issues: 2 (fabricated author list + unsupported claim).**

---

## Detailed Findings

### 1. `smith2020foo` — Section 3.2

**Our paper claims:** Smith et al. achieved 85.3% accuracy on SomeBench.

**Actual paper (Smith et al. 2020, arXiv:2004.XXXXX):** Reported 85.3% on
SomeBench (Table 3, main result column).

**Verdict:** Fully verified. Recommended more precise citation:
"Smith et al. (2020), Table 3, main result."

### 2. `jones2021bar` — Section 4.1

**Our paper claims:** Jones et al. (2021) introduced the Fooify algorithm.

**Actual paper:** arXiv:2011.XXXXX, submitted November 2020. Presented at
SomeConference 2021.

**Resolution:** Our 2021 year reflects the venue publication; arXiv
submission year is 2020. Either is defensible. If citing the venue,
prefer the `acl:` or `doi:` identifier over `arxiv:` in refs_ids.toml
so the year field resolves to the venue year automatically.

### 3. `patel2023baz` — Section 5, intro paragraph

**Our paper claims:** Patel et al.'s model has 1.5B parameters.

**Actual paper (Patel et al. 2023, arXiv:2305.XXXXX, §2):** The model has
1.7B parameters.

**Recommended fix:** Change "1.5B" → "1.7B" in the .tex. This is a prose
error next to a (correctly resolved) citation. The bib is fine; the
claim description is wrong.

### 4. `chen2024quux` — Related Work

**Our paper cites:** "Chen, Wang, Li (2024), Foo: A Survey."

**Actual paper (arXiv:2406.XXXXX):** Authors are Yuting Liu, Wei Zhang,
and Michael Rodriguez. Title is "Foo: A Comprehensive Survey." **No
author named Chen on the paper.**

**Recommended fix:** Our bib entry has a fabricated author list.
Set the identifier in `refs_ids.toml` and rerun `build_bib.py`; do not
attempt to hand-correct the author list. Consider renaming the bib key
to `liu2024quux` for readability, but this is optional — natbib renders
from the author field, not the key.

### 5. `kim2024xyz` — Section 6.2

**Our paper claims:** "Kim et al. use method Y to achieve Z."

**Actual paper (Kim et al. 2024, arXiv:2402.XXXXX, §3):** The paper
actually uses method Z', not Y. Method Y is referenced only in the
related-work section.

**Recommended fix:** This is the citation-doesn't-support-the-claim
failure mode. Two options:
- Swap to a different reference that actually introduces method Y
  (search for the canonical paper for method Y).
- Weaken our prose to match what Kim et al. actually do (method Z').

### 6. `author2019report` — Section 2

**Manual entry.** Cross-checked against the PDF at the cited URL.
Parameter count, architecture details, and training data description
all match. No issues.

---

## Items Needing Manual Review

1. `chen2024quux` fabricated author list — fix via `bibliography-from-ids`.
2. `kim2024xyz` unsupported claim — decide swap vs. weaken; both require prose edit.
3. `patel2023baz` parameter count — prose-side edit, straightforward.

## Items That Are Fully Fine

- `smith2020foo`, `author2019report`, `jones2021bar` (modulo preprint-year pedantry).

## Papers Unable to Access

None. All 6 citations located. (If any had been paywalled or unresolvable,
they would appear here with "UNABLE TO VERIFY — needs manual review"
rather than being guessed.)
