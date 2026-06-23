# Policy quick-reference (gathered 2026-05/06)

**These are point-in-time facts. Conference policies change every year — re-fetch the current pages before relying on them.** Sources are linked so you can re-verify fast.

## NeurIPS 2026 (main track) — for a paper concurrently under review there

Source of record: **NeurIPS 2026 Main Track Handbook** — https://neurips.cc/Conferences/2026/MainTrackHandbook

- **Non-archival workshop exemption (verbatim):** "The reviewing process will treat any other archival submission by an overlapping set of authors as prior work (**dual submissions to nonarchival workshops are permitted**)." → A non-archival workshop paper is *not* a dual submission. The whole exemption hinges on the workshop staying non-archival — confirm that with organizers.
- **Archival prohibition (verbatim):** "we explicitly prohibit submitting work to NeurIPS and then later submitting the same work to another **archival** venue while it is still under review at NeurIPS." Non-compliance "is grounds for **desk rejection** … at any point."
- **Preprints (verbatim):** "The existence of non-anonymous preprints (on arXiv …) **will not result in rejection**." "Authors may submit anonymized work … that is already available as a preprint … without citing it." Public versions "should not say 'Under review at NeurIPS' or similar."
- **Double-blind:** a non-anonymous preprint alone does not violate it; "**aggressive advertising** of papers under submission may be deemed a violation." Self-citations in the *submitted* PDF must be anonymized.
- **Desk-reject triggers:** style/margin/page-limit violations; de-anonymization of the submission; dual-submission non-compliance; failing submission requirements (e.g. missing checklist).
- **Page limit:** 9 content pages; references/appendix/checklist excluded.
- **Contemporaneous-work cutoff:** work online after **2026-03-01** is "contemporaneous" — your own later preprint can't be used to reject your submission.
- **2026 dates:** abstract 2026-05-04, full paper 2026-05-06, author discussion Jul 27–Aug 3, **decisions 2026-09-24**, conference Dec 6–12 (Sydney). (https://neurips.cc/Conferences/2026/Dates)

## arXiv (as of early 2026)

- **Endorsement (changed 2026-01-21):** institutional email alone **no longer auto-endorses**. Auto-endorsement now needs an academic email **and** prior authorship in the target domain; otherwise get a personal endorser (advisor). (https://blog.arxiv.org/2026/01/21/attention-authors-updated-endorsement-policy/) Established authors are unaffected.
- **Source / `.bbl`:** arXiv does not run BibTeX — **ship the precompiled `.bbl`** (always works; the Nov-2025 `.bib` support has edge cases, esp. biblatex/Biber). https://info.arxiv.org/help/submit_tex.html
- **Flat layout:** main `.tex` at top level; **no `../`-escaping paths**; figures must be `.pdf/.png/.jpg` for pdfLaTeX; add `\pdfoutput=1` if the engine is misdetected. No hard MB cap (just a 34-megapixel image warning since Feb 2026).
- **License:** options are arXiv non-exclusive, CC BY 4.0, CC BY-SA, CC BY-NC-SA, CC BY-NC-ND, CC0. **License is irrevocable per version.** Conservative default when future publication is possible: **arXiv non-exclusive** (CC0 conflicts with many publishers; CC BY only if mandated). https://info.arxiv.org/help/license/
- **Versioning:** v1, v2, … are permanent and public; the per-version **Comments** field is the canonical changelog spot. https://info.arxiv.org/help/versions.html
- **Tooling:** `arxiv-collector` (https://github.com/djsutherland/arxiv-collector) bundles deps + `.bbl` via latexmk; latexmk **4.63b** has broken dep-tracking (`--get-latexmk` to fetch a good one).

## ICML 2026 style / workshops

- **`icml2026.sty` author display:** default = "Anonymous Authors"; `[accepted]` = real authors **+ PMLR "Proceedings … Copyright" banner** (a false claim for non-archival); **`[preprint]`** = real authors + neutral "Preprint." footer, **no banner** (right for non-archival/arXiv). The default submission mode also renders reviewer **line numbers**, which `[preprint]`/`[accepted]` remove.
- **Main-conf camera-ready** allows one extra page (9 pp) to address reviewers; the originally-submitted version + full review record are published for accepted papers. https://icml.cc/Conferences/2026/AuthorInstructions , https://icml.cc/Conferences/2026/CallForPapers
- **Workshops are usually non-archival** ("made available as non-archival reports") and inherit/loosen the main-conf rules — but **arXiv permission, exact camera-ready format/banner, and the deadline are workshop-specific; ask the organizers** if not posted.

## Norms for post-review additions

Adding reviewer-requested results to a camera-ready is standard in ML/NLP (it's what the extra page is for); some fields (e.g. MICCAI) forbid new experiments — check the venue. Best practice for transparency: a footnote at the addition ("added after review … not itself peer-reviewed"), an arXiv v1(as-reviewed)/v2(extended) split with a Comments-field changelog, and (where the venue does it) the published review record makes the delta auditable.
