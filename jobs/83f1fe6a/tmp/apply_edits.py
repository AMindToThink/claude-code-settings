"""One-off literal-replacement edits to paper/writeup.tex.

Operates on the real on-disk file (not the harness Read/Edit cache, which has
been serving a stale pre-dac2 copy). Each replacement asserts exactly one match
(fail-fast per repo policy) so a stale/unexpected file surfaces loudly.
"""
from pathlib import Path

PATH = Path("paper/writeup.tex")
text = PATH.read_text()

edits: list[tuple[str, str]] = [
    # 1) Abstract: drop the "All numbers are script-generated" sentence
    #    (matches the user's uncommitted edit on main).
    (
        "self-neutralizes and is left open. All numbers are script-generated and cited by\nname.",
        "self-neutralizes and is left open.",
    ),
    # 2) Caveats footnote: the pre-registered validation table was removed by dac2,
    #    so "pre-registered claim" now dangles -> "empirical claim".
    (
        "the fast filter (Section~\\ref{sec:filter}) is an empirical, pre-registered claim.}",
        "the fast filter (Section~\\ref{sec:filter}) is an empirical claim.}",
    ),
    # 3) Section 4 generation paragraph: compress the speculative mechanism down to
    #    the honest observation (correction self-neutralizes -> effectively T=1) plus
    #    the one believed factor (model is a sub-optimal predictor of its own temp).
    (
        "Even\nthe modest closed-loop version, feeding $\\hat\\beta_t$ back into the sampler as it\n"
        "generates, self-neutralizes: correcting toward $\\hat\\beta$ drives the effective\n"
        "decoding temperature back to $\\beta_{\\mathrm{dec}}\\to 1$, cancelling the very\n"
        "signal it reads off. We confirmed this across exact-grid filters, so it is not an\n"
        "approximation artifact (Appendix~\\ref{app:controls}). Turning the read-out into\n"
        "better generation is the honest open problem.",
        "Even\nthe modest closed-loop version, feeding $\\hat\\beta_t$ back into the sampler as it\n"
        "generates, did not help: the corrected stream comes out at effectively\n"
        "temperature~$1$, so the correction neutralizes itself (confirmed across\n"
        "exact-grid filters, so it is not an approximation artifact;\n"
        "Appendix~\\ref{app:controls}). We did not pin down why; one factor we believe\n"
        "contributes is that the model is not an optimal predictor of its own\n"
        "temperature. Turning the read-out into better generation is the honest open\n"
        "problem.",
    ),
    # 4) Appendix corrector: cut the "boredom"/"confusion" regime speculation and the
    #    garbage-in/garbage-out aside; keep the corrector definition, the observation,
    #    and the two empirical controls.
    (
        "A corrector $\\beta^{\\mathrm{dec}}_t = \\beta^{\\mathrm{target}}/\\hat\\beta_t^{\\,p}$\n"
        "divides a user's target by the estimate. An empirical sweep shows it pins the\n"
        "effective temperature in the ``boredom'' regime ($\\beta^{\\mathrm{target}}>1$) but\n"
        "overshoots in the ``confusion'' regime ($\\beta^{\\mathrm{target}}<1$), where\n"
        "low-$\\beta$ self-generation degrades into incoherent text within $\\sim$20 tokens\n"
        "(a garbage-in/garbage-out confound that limits what the confusion-regime numbers\n"
        "can claim). Two further controls in the longer draft\n"
        "(\\texttt{paper/decoding\\_paper.tex}) support only ``do not correct at\n"
        "$\\beta^{\\mathrm{target}}=1$, because Qwen is already calibrated there'': a\n"
        "sampler-switch experiment (the belief is not a fast per-token entropy read-out, a\n"
        "null on one mechanism) and a closed-loop-vs-invariance comparison. The\n"
        "natural-text survey behind the wild-text claim of Section~\\ref{sec:filter} (all\n"
        "$\\scSurvNDatasets$ types) is tabulated there as well.",
        "A corrector $\\beta^{\\mathrm{dec}}_t = \\beta^{\\mathrm{target}}/\\hat\\beta_t^{\\,p}$\n"
        "divides a user's target by the estimate. In an empirical sweep it did not\n"
        "deliver better generation: the closed loop neutralizes itself and the output\n"
        "lands at effectively temperature~$1$. We did not establish the mechanism. Two\n"
        "controls in the longer draft (\\texttt{paper/decoding\\_paper.tex}) each rule out\n"
        "one candidate: a sampler-switch experiment shows the belief is not a fast\n"
        "per-token entropy read-out, and a closed-loop-vs-invariance comparison\n"
        "constrains it further. The natural-text survey behind the wild-text claim of\n"
        "Section~\\ref{sec:filter} (all $\\scSurvNDatasets$ types) is tabulated there as\n"
        "well.",
    ),
]

for old, new in edits:
    n = text.count(old)
    if n != 1:
        raise SystemExit(
            f"Expected exactly 1 match, found {n} for snippet:\n---\n{old[:90]}...\n---"
        )
    text = text.replace(old, new)

PATH.write_text(text)
print("All 4 edits applied.")
