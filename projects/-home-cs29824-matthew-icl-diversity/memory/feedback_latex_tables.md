---
name: Generate LaTeX tables from scripts, never copy numbers by hand
description: Analysis scripts must output .tex table files that the paper \inputs directly — no manual transcription of numbers into the paper
type: feedback
---

Analysis scripts must output LaTeX table files (e.g., `results/tables/contest.tex`) that the paper `\input{}`s directly. Never manually copy numbers from script output into the paper.

**Why:** Manual transcription of numbers is error-prone. Matthew caught discrepancies between script output and paper tables caused by using the wrong data subset. Machine-generated tables eliminate this class of error entirely.

**How to apply:**
- Scripts that compute results for the paper should write `.tex` files containing complete `\begin{table}...\end{table}` environments (or just the tabular body if the caption needs manual editing).
- The paper uses `\input{../results/tables/filename.tex}` to include them.
- The `.tex` files should include a comment citing the script and run-tag that generated them.
- When updating results, re-run the script — don't edit the `.tex` file by hand.
