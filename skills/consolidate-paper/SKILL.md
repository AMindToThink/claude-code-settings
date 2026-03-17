---
name: consolidate-paper
description: Consolidate scattered research notes, logs, experiment outputs, and submodule docs into a single living research paper. Use when the user wants to pull together multiple source documents into one structured paper.
argument-hint: "[output-path]"
---

## Consolidate Research into a Living Paper

Create a single living markdown document that consolidates scattered research artifacts (notes, logs, configs, experiment outputs, submodule docs) into a structured research paper.

Output path: $ARGUMENTS (default: `docs/paper.md`)

### Phase 1: Inventory Sources

Before writing anything, gather and read all source material in parallel:

1. **Research documents**: drafts, writeups, preregistration, research logs, READMEs
2. **Experiment configs**: YAML files, parameter settings
3. **Results artifacts**: metrics.json, stats.json, or equivalent results files
4. **Plot sidecar files**: .description.txt, .commentary.txt files that describe figures
5. **Submodule docs**: READMEs, PLAN.md, HYPOTHESES.md from submodules
6. **Verify which figures exist**: Glob for actual plot files (png/pdf) so you reference real files, not imagined ones

Use parallel tool calls aggressively — read all independent sources at once.

If any markdown files are too large (e.g., Google Docs exports with base64 images), use `Grep pattern="^[^!]"` to extract text lines only.

### Phase 2: Plan the Structure

If the user provided a plan, follow it. If not, propose a standard structure and get approval:

- Title, Authors, Abstract
- Introduction (motivation, assumptions, contributions)
- Related Work (organized by topic, not flat list)
- Methods (one subsection per methodology component)
- Experiments & Results (one subsection per experiment, with tables and figures)
- Discussion (observations, implications, limitations)
- Conclusion
- References (consolidated, deduplicated)
- Appendices (pre-registration, supplementary analyses, hypotheses, etc.)

### Phase 3: Write the Document

Write the full document in **one Write call** to avoid consistency issues from piecemeal assembly. Key principles:

- **Embed figures** with relative paths from the doc's directory: `![Caption](../outputs/experiment/plots/figure.png)`
- **Include full results tables** — copy exact numbers from metrics/stats files, don't summarize
- **Use tag conventions** for incomplete sections:
  - `<!-- TODO: description -->` — work needed
  - `<!-- NOTE: description -->` — informal notes, links, planning items
  - `<!-- FEEDBACK: question -->` — questions for collaborators
- **Don't invent data** — if results aren't available, use a TODO tag
- **Mark planned/proposed work** with TODO tags inline rather than in a separate section — keeps them close to the relevant context

### Phase 4: Verify

After writing:

1. Count TODO/NOTE/FEEDBACK tags: `grep -c '<!-- TODO' docs/paper.md`
2. Check line count is reasonable
3. Spot-check that results tables match source data files
4. Verify all referenced figures actually exist (Glob for each path)
5. Check for duplicate references

### Phase 5: Companion README

Create a brief README in the same directory explaining:
- What each file is
- The tag conventions and how to find gaps
- The relationship between the paper and canonical source documents (logs, preregistration, etc.)
- How figures are referenced
- Conversion plan (e.g., pandoc to LaTeX when ready)

### Common Pitfalls

- **Large markdown files with embedded images**: Use Grep, not Read. See the `read-large-md` skill.
- **Stale line-number references**: If following a plan from a prior conversation, line numbers may be wrong. Re-read files fresh.
- **Trusting research logs over data files**: If there's a discrepancy between a log entry and the actual metrics.json, the JSON is authoritative.
- **Over-emphasizing one finding**: Let the user decide what's interesting. Present results factually and let the framing come from discussion.
