"""Restructure section 4:
  - move the generation paragraph into the appendix (section retitled
    "Generating better"),
  - keep the Limitations paragraph in the body, as the closing note of section 3.
Line-based and fail-fast.
"""
from pathlib import Path

PATH = Path("paper/writeup.tex")
lines = PATH.read_text().splitlines(keepends=True)


def find_one(pred, desc):
    idx = [i for i, l in enumerate(lines) if pred(l)]
    if len(idx) != 1:
        raise SystemExit(f"{desc}: expected 1, found {len(idx)}")
    return idx[0]


gen_sec = find_one(
    lambda l: l.strip() == r"\section{Generating better, and limitations}\label{sec:gen}",
    "generating section",
)
lim_start = find_one(lambda l: l.strip() == r"\paragraph{Limitations.}", "limitations start")
lim_end = find_one(
    lambda l: l.strip() == r"\texttt{scripts/e1\_synthetic\_pilot.py}).", "limitations end"
)
app = find_one(lambda l: l.strip() == r"\appendix", "appendix")
corrector = find_one(
    lambda l: l.strip()
    == r"\section{Corrector and supporting control experiments}\label{app:controls}",
    "corrector section",
)

if not (gen_sec < lim_start <= lim_end < app < corrector):
    raise SystemExit("unexpected ordering of landmarks")
if not lines[gen_sec - 1].startswith("% ==="):
    raise SystemExit("no comment rule above the generating section")
if not lines[gen_sec + 1].startswith("% ==="):
    raise SystemExit("no comment rule below the generating section header")
if lines[lim_start - 1].strip() != "":
    raise SystemExit("expected blank line before Limitations paragraph")

rule = lines[gen_sec - 1]                       # the "% ===...===\n" decoration
gen_para = lines[gen_sec + 2 : lim_start - 1]    # generation paragraph (no trailing blank)
lim_block = lines[lim_start : lim_end + 1]       # Limitations paragraph (no surrounding blanks)
if gen_para[-1].strip() != "problem.":
    raise SystemExit(f"generation paragraph does not end as expected: {gen_para[-1]!r}")

new_region: list[str] = []
new_region += lim_block                          # Limitations now closes section 3 (body)
new_region += ["\n", "\\appendix\n", rule]
new_region += ["\\section{Generating better}\\label{sec:gen}\n", rule]
new_region += gen_para                           # generation paragraph -> appendix
new_region += ["\n"]                             # blank before the Corrector section

# Replace the rule-above-Generating ... through the old \appendix line.
lines[gen_sec - 1 : app + 1] = new_region
PATH.write_text("".join(lines))
print("Restructured: generation -> appendix; Limitations kept in body (closing section 3).")
