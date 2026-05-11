---
name: implement-math
description: Translate math (formulas, estimators, algorithms) into code so the implementation faithfully matches what the source actually specifies. Use when writing code from a formula, reviewing an LLM-generated implementation of a formula, debugging a numerical mismatch with a paper, designing a new metric/estimator, or refactoring an existing math-heavy computation. Especially load-bearing whenever aggregation operators (sums, means, expectations, products, geometric means) appear over indices that can be reordered, or whenever the same English label can refer to multiple non-equivalent estimators (e.g. ratio-of-means vs mean-of-ratios, micro-average vs macro-average, sample-weighted vs unweighted). Prevents the failure mode where a code path silently implements the wrong estimator under the same name as the intended one.
---

# Implement Math: Faithful Translation from Formulas to Code

**Core rule: Compact mathematical notation hides aggregation order. Your job is to make it visible — first in writing, then in code, then in tests.**

Mathematical formulas in papers and proposals are nearly always under-specified about *operator order*. The same expression can map to multiple inequivalent code paths depending on where each summation, mean, division, or expectation actually lives in the loop. The bugs this introduces are silent: numbers come out, plots look reasonable, only careful comparison against ground truth reveals the drift.

## Why This Skill Exists

A real, ~6-week-old bug from this codebase:

The paper's primary metric was specified as `D = C × a_n` (per-byte). The implementation computed `a_n_per_byte` two different ways inside one function:

- `mean_σ(bits_σ[k] / bytes_σ[k])` — mean-of-ratios (used internally for `E_rate`)
- `mean_σ(bits_σ[k]) / mean_σ(bytes_σ[k])` — ratio-of-means (used for the headline `a_n_per_byte` and the published `D`)

Both were stored under the same dict key `a_k_curve_per_byte`. Both are reasonable estimators. Only one is what the paper described. The bug was discovered, a separate diagnostic script (`scripts/analyze_per_byte.py`) was written to compute the correct estimator from per-permutation logs, and the canonical `core.py` was never patched. Six weeks later, every analysis script reading `metrics["a_k_curve_per_byte"]` got the wrong number, and the only flag was a docstring on a downstream helper.

This skill is the discipline that would have caught it on the day the formula was first translated into code.

## When to Use

Trigger this skill any time math meets code:

- Implementing a metric, estimator, loss, or algorithm from a paper
- Reviewing an LLM-generated implementation of a formula
- Debugging a numerical mismatch with a published result or analytic expectation
- Refactoring an existing math-heavy computation
- Designing a new statistical quantity for your own work
- Composing two existing math operations into a new one

**Especially** trigger it when:

- Aggregation operators appear (Σ, ∏, mean, E[·], geometric mean, log-sum-exp, softmax, Var, Cov)
- A quantity has indices that could be evaluated in different orders
- The same English label is in use for two distinct estimators in the codebase (a glaring sign — name them differently first, *then* implement)
- The formula uses any normalizing denominator that is itself an aggregate (per-byte, per-token, per-sample, per-class)

Do NOT skip this skill because "the formula is simple." Simple formulas hide order ambiguity especially well.

## The Discipline (in order, every time)

### 1. Restate the math with explicit indices and aggregation operators

Before writing code, expand the formula until aggregation order is visible. Compact notation is the enemy.

Bad (the source paper's notation):
```
D = C × a_n   (per-byte)
```

Good (what you actually have to implement):
```
a_n_pb := (1 / |Σ|) · Σ_{σ ∈ Σ} ( -log_2 P_θ(r_{σ(n)} | r_{σ(<n)}, p) / ‖r_{σ(n)}‖ )
                   ↑                ↑                                  ↑
                   outer mean       inner per-permutation              per-permutation byte denominator
                   over orderings   surprise (total bits)              (specific to this perm's slot-n response)

D_per_byte := C × a_n_pb
```

This is verbose. That's the point. The verbosity is what carries the information that compact notation discards.

If the source's notation is genuinely ambiguous about aggregation order — common in papers where the math is written compactly to fit a column — the *paper* has a bug, not just the code. Decide explicitly which order you are implementing, document it inline, and (if applicable) flag the ambiguity to the user.

### 2. Name the estimator, not just the quantity

When two estimators of the same quantity exist or could plausibly exist in the same codebase, give them distinct names that encode the aggregation choice. Never reuse one name for two non-equivalent estimators.

Bad: `a_n_per_byte` used for two different things.
Good: `a_n_pb_MoR` and `a_n_pb_RoM`, with the dispreferred one only ever appearing if explicitly requested.

This pattern recurs throughout statistics:

- `accuracy_micro` vs `accuracy_macro`
- `f1_micro` vs `f1_macro` vs `f1_weighted`
- `ppl_per_token` vs `ppl_per_byte` vs `ppl_per_word`
- `loss_sum` vs `loss_mean` vs `loss_per_example`
- `D_C_an` vs `D_C_E` (two different formulas for "diversity" in this codebase — see `CLAUDE.md`)

If you find a single name being used for two different aggregations, **rename before fixing**. The rename is the fix; the aggregation correction is downstream of having a name to attach the corrected behavior to.

### 3. Write a property test that distinguishes the candidates

Property tests must use cases where the candidate estimators give *numerically different* answers. Toy examples with equal-length / equal-weight inputs are useless — they pass for any reasonable aggregation order, so they don't certify which one you implemented.

Construct a case where the candidates **must** disagree:

```python
def test_mor_diverges_from_rom_when_uncorrelated():
    """Where bits and bytes vary inversely across perms, MoR ≠ RoM."""
    rec = {
        "a_k_curve": [55.0, 55.0],          # mean of [100, 10]
        "a_k_byte_counts": [55, 55],         # mean of [10, 100]
        "coherence_C": 1.0,
        "per_permutation_a_k_curves": [
            [100.0, 100.0],   # 100 bits paired with 10 bytes → 10/byte
            [10.0, 10.0],     # 10 bits paired with 100 bytes → 0.1/byte
        ],
        "per_permutation_byte_counts": [
            [10, 10],
            [100, 100],
        ],
    }
    v = compute_variants(rec)
    # MoR = mean([100/10, 10/100]) = mean([10.0, 0.1]) = 5.05
    assert v.a_n_pb_MoR == pytest.approx(5.05)
    # RoM = a_k_curve[-1] / a_k_byte_counts[-1] = 55/55 = 1.0
    assert v.a_n_pb_RoM == pytest.approx(1.0)
```

Generic version: for any aggregation, find an input where the two candidate orders give different answers, and assert the one you intended.

If the test passes for both candidates, the test is useless — strengthen it.

### 4. Embed the formula next to the implementation

Each function that implements a non-trivial math formula gets a docstring with two parts:

1. The formula in expanded form (with explicit aggregation operators)
2. A line-by-line correspondence to the code

```python
def compute_a_n_per_byte_MoR(perm_curves, perm_bytes):
    """Mean-of-ratios per-byte progressive surprise at the last position.

    Formula:
        a_n_pb_MoR = (1/|Σ|) · Σ_σ (a_{σ,n}^bits / ‖r_{σ(n)}‖)

    Code correspondence:
        - Σ_σ ... (sum over orderings):  ``sum(... for cur, b in zip(...))`` (line below)
        - 1/|Σ| (outer mean):            ``/ P``
        - per-permutation ratio:         ``cur[-1] / b[-1]`` inside the sum
    """
    P = len(perm_curves)
    return sum(cur[-1] / b[-1] for cur, b in zip(perm_curves, perm_bytes)) / P
```

The line-by-line correspondence is the part that catches reorderings. **If you can't write it cleanly, the implementation isn't faithful to the formula** — refactor until the correspondence is one-to-one.

This pattern is the math version of `import-content`'s "the document references the script's output by name" rule: the formula has one source of truth (the docstring), and the code's job is to be a transparent translation of it.

### 5. Faithfulness check on review

Before merging or claiming "done," ask explicitly — to yourself, to the LLM, or to a human reviewer:

> "For each summation / expectation / product / mean in the formula, point to the line of code that performs it, and confirm the order of operations matches the formula."

Do this in the diff. If the answer is "the order doesn't matter here" or "it does both at the same time," that's a smell — verify by constructing an input where order DOES matter and confirming the code's output agrees with your intended formula on that input.

When prompting an LLM to implement a formula, append: *"In your implementation, point to the line of code that performs each aggregation operator in the formula, in order. If you cannot, the implementation is not faithful — say so and ask for clarification before writing code."*

### 6. Fix the source, not just the consumer

When you find a discrepancy between a formula and a downstream computation, fix the canonical implementation, not just the analysis script that hit the bug.

If the canonical fix would invalidate saved data that's expensive to regenerate, at minimum:

- Add a tracked TODO at the top of the broken canonical code, naming what's wrong, the date, and the downstream script that does it correctly
- Add a comment in the canonical source that explicitly points at the correct downstream implementation
- Write a regression test that asserts the canonical and downstream implementations agree on a fresh input
- File the upstream fix as its own work item

A "skilled fix" that lives only in `analyze_per_byte.py` and not in `core.py` will be silently bypassed by the next code path that reads from `core.py`'s output — and there will always be a next code path. The fix has to be discoverable from either side.

### 7. Search the codebase before implementing

Before writing a new implementation of a formula, grep for existing implementations of the same quantity. There almost always is one. Two outcomes:

- **Reuse it**, even if it lives in a slightly inconvenient place — duplication is how naming drift starts.
- If you can't reuse it (different signature, different aggregation order, etc.), name your new implementation with the aggregation choice in the name, and add a comment in *both* implementations that names the other and explains the difference.

## Quick checklist (before claiming "implemented")

- [ ] Formula written in expanded form with all aggregation operators visible
- [ ] Each candidate aggregation order has a distinct name encoding the choice
- [ ] At least one test exists where candidate aggregations give numerically different answers, and asserts the correct one
- [ ] Function docstring contains the formula and a line-by-line correspondence to the code
- [ ] Searched the codebase for other implementations of the same formula; either reused them or noted the divergence in both places
- [ ] If this is fixing an existing bug: the fix is at the canonical source, not just the consumer
- [ ] If the canonical source can't be fixed yet: TODO + cross-reference comment + regression test asserting consumer-vs-source agreement

## When in doubt, ask

If you're translating math into code and you can't disambiguate aggregation order from the source material, **stop and ask the user before writing the code**.

> "What aggregation order do you intend for X — mean-of-ratios across permutations, or ratio-of-means? They differ when the per-permutation bits and byte counts are correlated."

The user can answer in five seconds. Debugging the resulting silent bug takes five weeks. The cost of one clarifying question is always less than the cost of one wrong implementation that ships.

## Recurring math-into-code traps to watch for

- **Ratio-of-means vs mean-of-ratios** (per-byte / per-token rates, weighted averages)
- **Micro vs macro vs weighted averaging** (multiclass metrics, fairness-aggregated metrics)
- **Sum-then-log vs log-then-sum** (likelihoods, log-partition functions)
- **Average-of-products vs product-of-averages** (variance / covariance / second moments)
- **Sample-weighted vs unweighted** (anything with importance weights, anything bootstrapped)
- **Population variance (`/n`) vs sample variance (`/(n-1)`)** (`np.std(ddof=0)` vs `ddof=1`)
- **Geometric vs arithmetic mean** (probabilities, multiplicative quantities, rates over time)
- **Inclusive vs exclusive endpoints** (sums over `range(n)` vs `range(n+1)`, off-by-one)
- **First-axis vs last-axis aggregation** in numpy/torch (`axis=0` vs `axis=-1` is a one-character difference with very different semantics)
- **Causal vs full attention masks** (autoregressive evaluation; off-by-one in shifted log-probs)
- **Logits vs log-probs vs probs** (which space the operation is meant to live in)

For any of these: name encodes the choice, test distinguishes the candidates, docstring documents the formula, line-by-line correspondence to the code.
