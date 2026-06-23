"""Move the Limitations paragraph out of the body into its own appendix section
(placed first in the appendix, before "Generating better"). Line-based, fail-fast.
"""
from pathlib import Path

PATH = Path("paper/writeup.tex")
lines = PATH.read_text().splitlines(keepends=True)


def find_one(pred, desc):
    idx = [i for i, l in enumerate(lines) if pred(l)]
    if len(idx) != 1:
        raise SystemExit(f"{desc}: expected 1, found {len(idx)}")
    return idx[0]


lim_start = find_one(lambda l: l.strip() == r"\paragraph{Limitations.}", "limitations start")
lim_end = find_one(
    lambda l: l.strip() == r"\texttt{scripts/e1\_synthetic\_pilot.py}).", "limitations end"
)
app = find_one(lambda l: l.strip() == r"\appendix", "appendix")
gen = find_one(lambda l: l.strip() == r"\section{Generating better}\label{sec:gen}", "generating")

if not (lim_start < lim_end < app < gen):
    raise SystemExit("unexpected ordering")
if lines[lim_start - 1].strip() != "":
    raise SystemExit("expected blank line before Limitations")
if not lines[app + 1].startswith("% ==="):
    raise SystemExit("expected comment rule directly after \\appendix")
if app + 2 != gen:
    raise SystemExit("\\appendix block is not immediately followed by the Generating section")

rule = lines[app + 1]                       # "% ===...===\n"
lim_body = lines[lim_start + 1 : lim_end + 1]  # paragraph text (drop the \paragraph lead-in)

new_region = (
    ["\\appendix\n", rule, "\\section{Limitations}\\label{sec:limits}\n", rule]
    + lim_body
    + ["\n", rule]
)

# Replace from the Limitations paragraph through the rule above the Generating section.
lines[lim_start : app + 2] = new_region
PATH.write_text("".join(lines))
print("Moved Limitations into its own appendix section (before Generating better).")
