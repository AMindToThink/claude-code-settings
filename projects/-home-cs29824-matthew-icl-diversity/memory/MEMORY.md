# Memory

## User Preferences
- [Verifiable numeric citations](user_cite_sources.md) — HIGH PRIORITY: all numbers in files must cite a deterministic, re-runnable source
- [Always write plotting/analysis code to files](feedback_scripts_for_plots.md) — never use inline `python -c` for plots; scripts must be repeatable
- [Matthew's mentor is Shi Feng](user_mentor_shi_feng.md) — Shi Feng, GWU, Google Scholar d0npq2oAAAAJ

## Project
- [ICML workshop submission lives on main](project_icml_workshop_submission.md) — workshop branch merged into main (2026-04-30); edit `paper/sections/` on main, not the worktree
- [Camera-ready style-only; OLMo self-scoring now on main](project_camera_ready_olmo_deferred.md) — 2026-06-15 camera-ready = `[accepted]` sty swap only; OLMo matrix + cross-family grader invariance merged to main 2026-08-03 (appG, arXiv-v2 material, not pushed at merge time)
- [Tevet McDiv dedup deactivated](project_tevet_dedup.md) — conflicting-label rows are Tevet's pair structure (same prompt, disjoint responses), NOT duplicates; --dedup hard-fails
- [arXiv v2 fixes (don't touch camera-ready)](project_arxiv_conclusion_single_forward_pass.md) — (1) conclusion "in a single forward pass" → "...per permutation"; (2) abstract+body DPO→RLVR arrow → comma list (no false trend); (3) update arXiv title (short) → camera-ready long title

## Reference
- [How to read paper tables](reference_table_sources.md) — read results/tables/*.tex or summary_table.txt, never PDF or memory
- [LaTeX paper formatting (sentence-per-line)](reference_latex_formatter.md) — use scripts/format_paper_sentences.py; do NOT retry latexindent or tex-fmt

## Feedback
- [Deliverables go in the repo, not the scratchpad](feedback_deliverables_in_repo_not_scratchpad.md) — files Matthew opens (PDFs, previews) belong at gitignored repo paths like paper/build/; VSCode can't see /tmp scratchpad
- [Always cite numeric sources](feedback_cite_sources.md) — every number in captions/papers/reports must reference the script+output that produced it
- [Never hand-type citation metadata](feedback_citations_no_handtyping.md) — HIGH PRIORITY: all bib entries fetched from arXiv/DOI/ACL via scripts/build_bib.py; use the `bibliography-from-ids` skill
- [Cite the originator of an approach](feedback_cite_originator.md) — HIGH PRIORITY: for "prior work" / "existing approaches" claims, cite the earliest paper, not a downstream user; dispatch literature-archaeology subagent if unsure
- [Verify claims on citation add](feedback_verify_claims_on_citation_add.md) — HIGH PRIORITY: run verify-citation-claims skill after any new citation; verify_cites.py only checks key resolution, not claim support
- [Auto mode ≠ destructive-action authorization](feedback_auto_mode_not_destructive_authorization.md) — HIGH PRIORITY: "check X" or "gitignore X" never imply deletion; auto mode accelerates routine work only
- [Verify file/folder names](feedback_verify_names.md) — always ls/glob to confirm actual names; never guess dash vs underscore
- [Investigate before widening tolerances](feedback_investigate_before_tolerances.md) — never relax test tolerances as first response; find root cause first
- [Commit before deleting, even for untracked files](feedback_preserve_before_delete.md) — when user says "delete X," default to commit-then-delete to preserve in git history; never silently `rm` untracked files in auto mode
- [Caption what exists, not what the argument needs](feedback_caption_actual_content.md) — figure captions, table titles, docstrings must describe actual content; if honest description doesn't fit the argument, fix the artifact, not the text
- [Check git status before overwriting IDE-open files](feedback_check_ide_open_file_before_overwriting.md) — when system-reminder says file is open in IDE, run `git diff` and ask before any `cp`/`mv` that writes to that path
- [Paper prose edits — one at a time, verify before continuing](feedback_paper_prose_one_at_a_time.md) — for paper prose, make one atomic change, explain it, and flag any wording shift that could alter a claim; auto mode does not override this
- [decTest is boring; focus on crowdsourced Tevet tasks](feedback_dectest_boring.md) — HIGH PRIORITY: decTest sign flips are known artifacts of temperature scaling; do not raise as counter-evidence against $C \times a_n$
- [DPO ≈ RLVR, never an arrow](feedback_dpo_rlvr_approx_equals.md) — OLMo stage sequence: DPO↔RLVR connector is approximately-equals (exploratory H1' contrast, no directional claim); base→SFT→DPO keep arrows
- [Separate rearranging from rewording](feedback_separate_rearrange_from_reword.md) — never mix moves and wording changes in one action; rearrange verbatim first, then propose rewords one at a time
- [Small faithful framing edits by default](feedback_small_faithful_framing_edits.md) — for framing feedback, default to smallest directional edit; reserve big reframings for moments the user explicitly signals one ("E is uninteresting in its uninterestingness", "do a real overhaul")
- [No unsupported elaboration of cited work](feedback_no_unsupported_elaboration_of_cited_work.md) — when describing cited papers/datasets, stick to what the source supports; no strengthening adjectives or implied claims
- [No em-dashes in public-facing writing](feedback_no_em_dashes_in_public_writing.md) — HIGH PRIORITY: avoid `—` and LaTeX `---` in papers, READMEs, blog posts; use commas/colons/parens/sentence breaks; en-dashes `--` are fine
- [The workshop paper is THE paper; original is archived](feedback_paper_naming_original_not_canonical.md) — `paper/main_icml_workshop.tex` is canonical; original wrapper archived at `paper/archive/` on 2026-04-30
