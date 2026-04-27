---
name: latex-semantic-linebreaks
description: Use when editing LaTeX paper sources where prose paragraphs are written as long single lines, OR when starting a new LaTeX paper. Reflows .tex prose to one-sentence-per-line ("ventilated text" / "semantic linebreaks") so Edit() invocations are sentence-precise and git diffs review-friendly. Renders byte-identical PDF. Do NOT recommend latexindent or tex-fmt for this — both fail predictably on math-heavy LaTeX. Activates on phrases like "format the paper", "sentence-per-line", "semantic linebreaks", "ventilated text", "reflow latex", or any time you're editing a .tex file with multi-sentence single-line paragraphs.
---

# LaTeX semantic linebreaks (one-sentence-per-line)

LaTeX collapses single newlines in source to spaces in the rendered PDF, so reformatting prose to one-sentence-per-line is a **pure-source change with zero rendering impact**. The convention is variously called "semantic linebreaks", "ventilated text", or "one sentence per line".

## When to apply this skill

Apply when:

- A LaTeX paper source has multi-sentence paragraphs written as long single lines (which makes `Edit()` brittle and `git diff` paint whole paragraphs red).
- You're about to make many small prose edits across a paper.
- A user asks to "format" a paper, reflow .tex prose, or set up "sentence-per-line".

Do NOT apply mid-paragraph during a single small edit — it inflates that edit's diff. Run as a dedicated formatting commit, separate from semantic changes.

## Why an off-the-shelf tool will not work

Three off-the-shelf tools were evaluated and rejected. **Do not retry them.**

| Tool | Verdict |
|---|---|
| `latexindent --m oneSentencePerLine` (TeX Live) | Produces ~14 false breaks per math-heavy paper. Categories: tikz/factorial `!` mistaken for sentence end (`orange!70!black`, `1/n!`); quote-attached `?''` split off; `\texttt{.}` content broken; escaped-space `vs.\ ` broken; abbrev `etc.)` split before comma; footnote `.1` ambiguous. Tuning knobs (`betterFullStop`, `sentencesBeginWith`, `sentencesDoNotContain`) shift which categories fire but never eliminate them. Matches multiple closed-but-not-fully-fixed bugs in the latexindent.pl tracker. |
| `tex-fmt` (Rust) | Semantic-linebreaks support is an [open feature request (issue #80)](https://github.com/WGUNDERWOOD/tex-fmt/issues/80) as of early 2025. Not implemented. |
| `andykuszyk/texfmt` (Go) | Archived September 2024. Only does fixed-width reflow, not sentence-per-line. |

If you find yourself trying to install latexindent or tune its config, **stop**. Use the project-local Python script described below.

## Tool: state-aware Python formatter

A reference implementation lives in `references/format_sentences.py` of this skill. It is ~150 LoC and:

- Tracks math mode (`$...$`, `$$...$$`, `\(...\)`, `\[...\]`).
- Skips environments where breaks are wrong: `verbatim`, `lstlisting`, `tikzpicture`, `equation`, `equation*`, `align`, `align*`, `gather`, `gather*`, `eqnarray`, `eqnarray*`, `multline`, `multline*`, `array`, `matrix`, `pmatrix`, `bmatrix`, `vmatrix`, `cases`, `pgfplots`, `axis`, `tabular`, `tabular*`, `tabularx`.
- Skips opaque command arguments: `\texttt`, `\textcolor`, `\cite`, `\citep`, `\citet`, `\citeyear`, `\ref`, `\label`, `\url`, `\href`, `\verb`.
- Skips `%`-comments (with `\%` escaped form preserved).
- Recognizes abbreviations: `e.g.`, `i.e.`, `i.i.d.`, `cf.`, `vs.`, `et al.`, `etc.`, `Fig.`, `Eq.`, `Sec.`, `Tab.`, `Ref.`, `Refs.`, `Eqs.`, `Figs.`, `Tabs.`, `Secs.`, `App.`, `Apps.`, `Alg.`, `No.`. Add to `ABBREVS` if your paper uses others.
- **Handles escaped backslashes `\\`** before any single-char inspection, so `\\[1em]` (LaTeX linebreak + optional spacing) is not mistaken for `\[ display math` opener. *This was a real bug; see the regression test below.*
- Inserts `\n` only after `[.?!]`, optionally past attached `''` or `"`, then whitespace, then capital letter — provided no abbreviation matches the preceding ~12 chars.
- Idempotent: re-running on already-formatted source inserts nothing.

The companion test file `references/test_format_sentences.py` has 24 cases covering every edge case the script handles, including the runaway-skip-region regression. **Run the tests before trusting the script in a new project.**

## Workflow

```bash
# 1. Stage the script in the project (one-time setup).
mkdir -p scripts tests
cp ~/.claude/skills/latex-semantic-linebreaks/references/format_sentences.py \
   scripts/format_paper_sentences.py
cp ~/.claude/skills/latex-semantic-linebreaks/references/test_format_sentences.py \
   tests/test_format_paper_sentences.py
uv run pytest tests/test_format_paper_sentences.py -v   # expect 24 green

# 2. Commit any pending semantic .tex changes FIRST — keep formatting
#    in its own commit so reviewers can tell prose changes from reflow.
git add paper/your_paper.tex && git commit -m "..."

# 3. Run the formatter to a sibling file and review the diff.
python scripts/format_paper_sentences.py \
  paper/your_paper.tex /tmp/formatted.tex
diff paper/your_paper.tex /tmp/formatted.tex | less   # newlines only, no word changes

# 4. Apply, rebuild, and verify byte-identical rendered text.
cp /tmp/formatted.tex paper/your_paper.tex
cd paper && rm -f your_paper.{aux,bbl,blg,fdb_latexmk,fls,log,out} && \
  latexmk -pdf your_paper.tex

# 5. Verification — both byte counts MUST match exactly.
pdftotext -nopgbrk paper/your_paper.pdf -      | tr -s ' \n\t' ' ' | wc -c
# Compare against pre-format byte count (record this BEFORE step 4).

# 6. Commit format change separately.
git commit -am "format: sentence-per-line reflow (no semantic changes)"
```

## Verification rules

**Two checks, both required.**

### Rule 1: byte-identical rendered PDF text

```bash
pdftotext -nopgbrk before.pdf - | tr -s ' \n\t' ' ' | wc -c
pdftotext -nopgbrk after.pdf  - | tr -s ' \n\t' ' ' | wc -c
```

These two byte counts must match exactly. A `pdftotext -layout` line-by-line diff is **misleading** — column-position differences in extracted text produce tens of false-positive diff lines for purely cosmetic source reflow. The whitespace-collapsed `-nopgbrk` byte-count comparison is the right test.

### Rule 2: visually inspect the `.tex`

Byte-identical rendering does **not** guarantee the source got reflowed where you intended. A formatter bug (e.g., a runaway skip region from misparsing `\\[`) can leave whole paragraphs unformatted while still producing identical PDF output. After running, visually scan a few paragraphs in the `.tex` — every prose paragraph should have one sentence per line. If any paragraph is still a single long line, the skip-region detection is broken; debug it.

This is not theoretical: the original implementation of this script left ~25 lines unformatted (the abstract and §Motivation opening), and only Rule 1 verification missed it. The user's visual check caught it.

## Anti-patterns

- **Don't reformat in the same commit as semantic changes.** Reviewers can't tell a sentence reorder from a sentence move.
- **Don't reformat when the abstract has math at the wrong place.** If `\\[1em]` or similar shows up in `\title`, `\author`, or `\date`, ensure the formatter handles `\\` escapes — the reference script does.
- **Don't trust pdftotext-layout diffs.** They will spook you with hundreds of "differences" that are just column-position changes.
- **Don't recommend latexindent.** See above. It will not converge.

## Quick decision rule

```
Is the .tex source one-sentence-per-line in the paragraph you're editing?
├── Yes  → just edit; don't reformat.
└── No   → if you're making >2 prose edits, run the workflow above
          first as a separate commit. If you're making one quick edit,
          either skip reformatting (acceptable) or reformat just the
          paragraph by hand inside the Edit() call.
```
