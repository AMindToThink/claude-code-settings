"""Demote section 4 ("Generating better, and limitations") into the appendix by
moving the single \\appendix declaration to just before that section. Line-based
and fail-fast so any unexpected structure surfaces loudly.
"""
from pathlib import Path

PATH = Path("paper/writeup.tex")
lines = PATH.read_text().splitlines(keepends=True)

GEN = r"\section{Generating better, and limitations}\label{sec:gen}"
gen_idx = [i for i, l in enumerate(lines) if l.strip() == GEN]
if len(gen_idx) != 1:
    raise SystemExit(f"expected 1 Generating section, found {len(gen_idx)}")
gi = gen_idx[0]
if not lines[gi - 1].startswith("% ==="):
    raise SystemExit(f"line before Generating section is not a comment rule: {lines[gi-1]!r}")

app_idx = [i for i, l in enumerate(lines) if l.strip() == r"\appendix"]
if len(app_idx) != 1:
    raise SystemExit(f"expected exactly 1 \\appendix, found {len(app_idx)}")
ai = app_idx[0]
if ai <= gi:
    raise SystemExit("existing \\appendix is not after the Generating section as expected")

# Remove the existing \appendix (higher index first so gi stays valid),
# then insert it on its own line just before the Generating section's comment rule.
del lines[ai]
lines.insert(gi - 1, "\\appendix\n")

PATH.write_text("".join(lines))
print("Moved \\appendix before the Generating-better section.")
