---
name: bayesian-stats
description: Convert frequentist statistical tests into their Bayesian equivalents. Provides mappings, code snippets, interpretation guides, and best practices.
user_invocable: true
---

When the user invokes `/bayesian-stats`, help them convert frequentist statistical tests into Bayesian equivalents.

If an argument is provided (e.g., `/bayesian-stats t-test`), look up that specific test. Otherwise, ask which frequentist test they want to convert.

## Mappings

| Frequentist Test | Bayesian Equivalent | Python Library |
|-----------------|--------------------|--------------| 
| Paired t-test | Bayesian paired t-test with JZS prior → BF₁₀ | `pingouin.bayesian_ttest(x, y, paired=True)` |
| Independent t-test | Bayesian independent t-test with JZS prior → BF₁₀ | `pingouin.bayesian_ttest(x, y, paired=False)` |
| Wilcoxon signed-rank | Bayesian paired t-test (robust alternative) or Bayesian sign test via PyMC | `pingouin` for approximate BF, `pymc` for full model |
| Fisher's exact / Chi-squared | Beta-Binomial model with Beta(1,1) priors on each group's success rate | Analytical or `pymc`: `pm.Beta("p", 1, 1)` per group |
| Mixed-effects logistic regression | Bayesian mixed-effects model | `bambi`: `bmb.Model("y ~ condition + (1|question)", data, family="bernoulli")` |
| ANOVA / F-test | Bayesian ANOVA | `pingouin.bayesian_anova(data, dv, between)` or `bambi` |
| Pearson correlation | Bayesian correlation | `pingouin.bayesian_corr(x, y)` |
| Bootstrap CI | Posterior credible interval from MCMC | `pymc` model → `arviz.summary()` for HDI |

## Code Snippets

### Bayesian Paired t-test (replaces Wilcoxon / paired t-test)
```python
import pingouin as pg
bf = pg.bayesian_ttest(x, y, paired=True, r=0.707)  # JZS prior, Cauchy scale r=√2/2
print(f"BF₁₀ = {bf:.3f}")
```

### Beta-Binomial (replaces Fisher's exact)
```python
import pymc as pm
import arviz as az

with pm.Model():
    p_a = pm.Beta("p_a", 1, 1)  # Condition A success rate
    p_b = pm.Beta("p_b", 1, 1)  # Condition B success rate
    pm.Binomial("obs_a", n=n_a, p=p_a, observed=k_a)
    pm.Binomial("obs_b", n=n_b, p=p_b, observed=k_b)
    delta = pm.Deterministic("delta", p_b - p_a)
    trace = pm.sample(4000)

az.summary(trace, var_names=["delta"], hdi_prob=0.95)
az.plot_posterior(trace, var_names=["delta"], ref_val=0)
```

### Bayesian Mixed-Effects (replaces frequentist mixed-effects)
```python
import bambi as bmb
import arviz as az

model = bmb.Model("correct ~ advice_source * question_category + (1|question_id)", data, family="bernoulli")
results = model.fit(draws=4000)
az.summary(results, var_names=["advice_source", "question_category", "advice_source:question_category"])
```

## Interpreting Bayes Factors (BF₁₀)

| BF₁₀ | Evidence |
|-------|----------|
| > 100 | Extreme evidence for H₁ |
| 30–100 | Very strong evidence for H₁ |
| 10–30 | Strong evidence for H₁ |
| 3–10 | Moderate evidence for H₁ |
| 1–3 | Anecdotal evidence for H₁ |
| 1/3–1 | Anecdotal evidence for H₀ |
| 1/10–1/3 | Moderate evidence for H₀ |
| 1/30–1/10 | Strong evidence for H₀ |
| < 1/30 | Very strong evidence for H₀ |

Key advantage: BF < 1/3 provides **evidence for the null**, not just "failure to reject." This is impossible with p-values.

## Best Practices

1. **Always report both** frequentist (p-values, CIs) and Bayesian (BF₁₀, posterior credible intervals) results. Reviewers expect p-values; Bayesian results add rigor.
2. **Sensitivity analysis**: Rerun Bayes factors with different prior scales (e.g., Cauchy r = 0.5, √2/2, 1.0). If conclusions are robust across priors, the result is more credible.
3. **Small samples**: Bayesian methods handle small n more gracefully — posteriors are properly wide when data is limited, rather than giving misleading p-values.
4. **Combining experiments**: Posteriors from one experiment become priors for the next. This is how evidence accumulates across studies.
5. **No multiple comparison correction needed**: Bayesian updating naturally handles multiplicity (though model comparison via Bayes factors still requires care).

## Required Packages
```
uv add pingouin pymc bambi arviz
```
