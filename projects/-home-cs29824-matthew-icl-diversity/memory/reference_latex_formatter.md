---
name: LaTeX paper formatting (sentence-per-line)
description: For paper/in_context_diversity_metric.tex, use scripts/format_paper_sentences.py — a custom state-aware formatter. Off-the-shelf tools (latexindent, tex-fmt) fail on math-heavy LaTeX in predictable ways; do not retry them.
type: reference
originSessionId: ed2cb122-3a59-44e7-9762-901f8d3dcde5
---
The paper source under `paper/` uses **one-sentence-per-line** ("ventilated text" / "semantic linebreaks"). LaTeX collapses single newlines to spaces, so this is a pure-source convention; the rendered PDF is unchanged.

**Why it matters:** sentence-precise `Edit()` calls (no multi-line `old_string` needed for uniqueness), sentence-precise git diffs, line numbers stable for the lifetime of a sentence rather than a paragraph.

## Tool: `scripts/format_paper_sentences.py`

Custom state-aware Python formatter in this repo. Walks the `.tex` tracking math mode (`$...$`, `\(...\)`, `\[...\]`, `$$...$$`), skip-environments (`verbatim`, `tikzpicture`, `equation`, `align`, `tabular`, …), opaque command arguments (`\texttt`, `\textcolor`, `\cite`, `\ref`, `\label`, `\url`, `\href`, `\verb`), and `%` comments. Inserts `\n` after `[.?!]` only when outside any skip region, optionally past attached `''`/`"`, followed by whitespace + capital, and not preceded by an abbreviation in the `ABBREVS` list.

**Tested by `tests/test_format_paper_sentences.py`** (23 cases, all green). Idempotent. Run:

```bash
uv run python scripts/format_paper_sentences.py \
  paper/in_context_diversity_metric.tex /tmp/formatted.tex
diff paper/in_context_diversity_metric.tex /tmp/formatted.tex
cp /tmp/formatted.tex paper/in_context_diversity_metric.tex
cd paper && latexmk -pdf in_context_diversity_metric.tex
```

**Verification rule:** rendered text must be byte-identical. Use `pdftotext -nopgbrk file.pdf - | tr -s ' \n\t' ' ' | wc -c` before and after; bytes must match exactly.

## Why not the off-the-shelf tools

**`latexindent --m oneSentencePerLine` (TeX Live, v4.0):** tried first. Produced ~14 false breaks that changed rendered output. Categories: tikz/factorial `!` mistaken for sentence end (`orange!70!black`, `1/n!`); quote-attached `?''` split apart; `\texttt{.}` content broken; escaped-space `vs.\ ` broken; `etc.)` split before a comma; footnote `.1` ambiguous. Tuning knobs (`betterFullStop`, `sentencesBeginWith.A-Z`, `sentencesDoNotContain` with regex for abbreviations and protected commands) shifted which categories fired but did not eliminate them. Matches multiple closed-but-not-fully-fixed issues on the `latexindent.pl` tracker. **Do not retry; it does not converge.**

Install footnote (in case a future agent needs it for a non-format reason): `tlmgr install latexindent` then `cpan -T install YAML::Tiny File::HomeDir Unicode::GCString Log::Log4perl Log::Dispatch::File`. Modules go to `/home/cs29824/perl5/lib/perl5/`; set `PERL5LIB=/home/cs29824/perl5/lib/perl5:/home/cs29824/perl5/lib/perl5/x86_64-linux-gnu-thread-multi`. Binary at `/home/cs29824/.TinyTeX/bin/x86_64-linux/latexindent`.

**`tex-fmt` (Rust):** semantic-linebreaks support is an open feature request (tex-fmt issue #80) as of early 2025. Not yet implemented.

**`andykuszyk/texfmt`:** archived September 2024. Only does fixed-width reflow, not sentence-per-line.

## Lesson logged for future me

When asked to "find a different tool" for LaTeX semantic linebreaks, the answer is *the custom script we already have*. The tool selection problem has been resolved. Do not spend time researching alternatives or tuning latexindent further.
