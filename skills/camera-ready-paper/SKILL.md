---
name: camera-ready-paper
description: Use when preparing a paper's camera-ready or arXiv release — de-anonymizing an accepted submission, packaging an arXiv tarball, checking dual-submission safety against a concurrent venue (e.g. a paper accepted at a workshop that's also under review at NeurIPS/ICML), or flagging reviewer-requested post-review additions. Encodes a byte-identity discipline (the public version changes ONLY author/venue metadata, never content), a numbers-from-scripts integrity gate, and the arXiv mechanics that actually bite.
---

# Camera-Ready / arXiv Release

A process for turning an **accepted** (often anonymized) paper into a public, de-anonymized camera-ready or arXiv post **without silently changing the reviewed content**, while staying safe with any concurrent submission at another venue.

This is a flexible skill: adapt the steps to the paper, but do NOT skip the **safety check** (§2), the **byte-identity gate** (§3), or the **integrity gate** (§5). Those are where mistakes become desk-rejections, retractions, or "we accidentally posted a different paper than the one that was reviewed."

## 0. Intake — gather before doing anything

Establish, in writing:
- **Venue + archival status.** Is the accepting venue *archival* (official proceedings, e.g. PMLR/ACL Anthology) or *non-archival* (workshop "reports", no proceedings)? This single fact drives the dual-submission analysis. If unstated, ask the organizers — don't infer from a tweet.
- **Concurrent submissions.** Is the same/related work under review elsewhere right now (another conference's main track)? Which venue, and what are its dates (decision date matters)?
- **What was actually submitted.** Which branch/commit/PDF is the accepted artifact? Repos accumulate divergent branches; the "obvious" branch is often *not* the one submitted. Verify (§3, step 1).
- **Deadlines & template.** Camera-ready deadline, page limit, the venue's LaTeX style.
- **Where numbers/citations come from.** Does the repo follow numbers-from-scripts / bib-from-IDs? Find the build scripts and tests.

## 1. Decide the target version with the author

If branches diverged, the authoritative content is **what was reviewed/accepted**, not the latest dev state. Surface every content difference between the candidate branches *in both directions* and let the author confirm which is authoritative. A distinctive, recent citation or a specific table is a fast oracle: "does your submitted PDF contain X?" pins down which branch was submitted. Get an explicit decision on any text that exists on one branch but not the accepted one (default: keep the accepted version exactly; re-adds are flagged content changes).

## 2. Dual-submission safety check (if anything is concurrently under review)

Fetch the *concurrent* venue's current policy (its handbook/CFP, not memory) and answer, with quotes:
- **Is a non-archival workshop a "dual submission" / "prior work"?** Most ML venues **exempt non-archival workshops** explicitly. Archival prior work is treated as prior work and can sink both papers if too incremental.
- **Are non-anonymous arXiv preprints allowed during review?** Usually yes ("the existence of non-anonymous preprints will not result in rejection"). Note any anonymity blackout window (NeurIPS historically has none; some CV venues do).
- **Desk-reject triggers** (style/page violations, de-anonymization of the *submission*, dual-submission non-compliance, missing checklist).

Then enforce these guardrails on every public artifact:
- **No concurrent-venue strings** anywhere in the public PDF *or source* — including LaTeX **comments** and PDF metadata. Grep for the venue name, "under review", and any anonymous-mirror IDs. A buried `% main_neurips.tex` comment is a leak.
- **The submitted (anonymous) PDF stays anonymized** — only the public copy is de-anonymized; they are separate artifacts.
- **No archival resubmission** of the same/longer work until the concurrent venue's decision date or withdrawal.
- **Don't aggressively advertise** the under-review paper; present/share it as the *accepted* venue's paper.

Produce an explicit **go / no-go** before proceeding.

## 3. Byte-identity gate — prove the merge/checkout preserved the accepted content

Goal: the public version's compiled paper is **byte-identical to the accepted version**, so the only later diffs are the de-anonymization edits (§4).

1. **Snapshot the reference.** sha256 the accepted PDF; record the accepted branch/commit.
2. **Bring content onto the target branch** (e.g. merge), then **pin every compiled-paper input to the accepted version's exact bytes** (`git checkout <accepted> -- <paths>`) for anything that diverged. Compiled inputs = the wrapper `.tex`, all `\input`'d sections, the style/`.bbl`/`.bib`, generated macro/table files, and figures.
3. **Gate (must pass):**
   - `git diff --diff-filter=MD <accepted> -- <compiled inputs>` is **empty** (no accepted file modified or missing).
   - A reproducible rebuild produces a PDF whose **sha256 equals the accepted PDF**. (If the repo pins `SOURCE_DATE_EPOCH`, this works; if bytes differ despite identical inputs, fall back to identical `pdftotext` output + identical inputs, and flag the toolchain difference rather than proceeding silently.)
4. Commit this as its own step so the byte-identical state is a checkpoint.

## 4. De-anonymize — change ONLY metadata, never content

Edit only the wrapper's author block, repo/URL, venue notice, and acknowledgements. Do **not** touch section/refs/macro files. Then prove it: `git diff <byte-identity-commit> -- <wrapper>` shows only those hunks, and a rendered diff vs the accepted PDF is limited to the author block, footer notice, URL, and the new acknowledgements heading (plus removal of reviewer line numbers, which is normal).

LaTeX-template gotchas:
- **ICML/PMLR styles:** without `[accepted]` the template **forces "Anonymous Authors"** regardless of `\icmlauthor`; `[accepted]` shows authors **but adds the PMLR "Appearing in Proceedings… Copyright" banner** — which is a *false* claim for a non-archival workshop. Look for a **`[preprint]`** option: it shows real authors with a neutral footer and no copyright banner. Override the preprint notice text if it injects `\today` (a pinned `SOURCE_DATE_EPOCH` will stamp a wrong date).
- **Acknowledgements:** if the author wants to write them, create an empty `\section*{Acknowledgements}` stub with a clear `% TODO` and **point them to the exact file path** — don't invent content.
- **De-anon completeness scan:** grep the built PDF + sources for leftover `Anonymous`, anon emails, and anonymous-mirror URLs. This verifies *your own edit*, not a venue requirement.

## 5. Integrity gate — citations + numbers-from-scripts

- Run the citation linter and the paper's macro/number tests.
- **When byte-identity matters, do NOT let regeneration scripts overwrite the pinned files.** Snapshot `paper_macros.tex` / `refs.bib`, run the tests, and if a regeneration drifts, **restore the accepted version** (byte-identity wins) and report the drift. (A clean run where regeneration reproduces identical bytes is the strong signal that the accepted numbers come from the committed data.)
- The rebuild tool should fail loudly on any undefined ref/cite.

## 6. arXiv packaging — use a tool, don't hand-roll a flattener

- **Use `arxiv-collector`** (`uvx --from arxiv-collector arxiv-collector --no-strip-comments <main.tex>`, run from the main `.tex`'s directory). It drives `latexmk`'s dependency tracking to gather exactly the used files and **bundles the `.bbl`** so arXiv needn't run BibTeX. Check latexmk isn't the broken 4.63b (`--get-latexmk` if so).
- **Parent-directory assets are the catch.** If the repo keeps figures/tables in directories *above* the paper folder, the main `.tex` uses `../figures`, `../results`, etc., and arxiv-collector stores them with `../` member paths that don't extract and aren't arXiv-valid (arXiv wants the main file at the top level, no parent-escaping paths). Fix with a **minimal deterministic normalization** — strip the leading `../` so assets sit under the bundle root, and `sed` the same `../` out of the bundled `.tex`. This is a path-normalization on the tool's output, *not* a from-scratch flattener.
- **Verify the bundle like arXiv:** unpack to a clean dir and compile with **pdflatex ×3 (no bibtex), using the bundled `.bbl`**. Assert: same page count as the de-anon PDF, 0 undefined refs/cites, 0 missing files, real authors render, and a sensitive-string scan (concurrent venue / anon mirror) comes back empty. Remove your test-compile artifacts (keep the `.bbl`) before tarring.
- **arXiv form settings** to hand the author: primary + cross-list categories; **license** (default the conservative **arXiv non-exclusive** — irrevocable per version — unless a funder mandates CC BY); a Comments field naming the accepted venue (no concurrent-venue string); endorsement note (established arXiv authors need none; first-timers since Jan 2026 need a personal endorser — institutional email alone no longer auto-endorses).

## 7. Reviewer-requested additions → a later arXiv version, clearly flagged

Adding reviewer-requested experiments to a camera-ready is standard in ML — but they weren't themselves peer-reviewed, so flag them:
- Post the accepted content as **v1** (frozen, citable, byte-identical). Add the new work as **v2** with a changelog in the arXiv **Comments** field and a footnote at each addition: *"Added after review in response to reviewer feedback; not itself peer-reviewed."*
- New numbers still go through the numbers-from-scripts pipeline (a changelog is prose — its numbers must be macro-sourced too).
- If the concurrent venue is still under review, v2 must stay concurrent-venue-string-free and must not become a separate archival submission.

## Guardrails (always)
- **Git identity** on shared machines: confirm `user.name` AND `user.email` match the right person before every commit.
- **Local commits only**; never push without asking.
- **Ask before squeezing** content to fit a hard page limit — don't thrash on margins/font tweaks.
- **Fail loud**, never silently skip — a regeneration drift, a missing figure, or a leaked venue string should stop the line, not get `continue`d past.

See `references/policy-quick-reference.md` for concrete NeurIPS-2026 / arXiv / ICML facts and source URLs gathered for this skill (verify against current pages — policies change yearly).
