---
name: bibliography-from-ids
description: Set up script-generated bibliography entries so citation metadata is never hand-typed. Use when writing or editing a paper's bibliography / references / related-work, adding a citation, verifying an existing bibliography's correctness, or setting up a new paper project. Prevents fabricated author lists, titles, years, and venues by requiring every entry to be fetched from arXiv / Crossref / ACL Anthology via a build script.
---

# Bibliography from Identifiers: Script-Generated References

**Core rule: Never hand-type citation metadata.** You list identifiers; a script fetches canonical BibTeX. Author lists, titles, years, and venues are ALL derived from authoritative APIs — never typed from memory.

This is the citation analog of `import-content` (which does the same for tables and numbers).

## Why This Skill Exists

LLMs — including you — fabricate citation metadata at rates of 14 % to 95 % across domains (see CheckIfExist 2026, GhostCite 2026, BibTeX Citation Hallucinations 2026). The characteristic failure mode is: real paper title, real year, **completely wrong author list**. The author list is what gets rendered in every in-text citation, so this is a load-bearing error.

A real incident during paper writing: an audit of 12 citations found 4 fabricated author lists, 1 unsupported claim, 1 wrong volume number, and 4 wrong titles. Every fabricated entry pointed to a real paper — the identifier would have been correct if recorded. Identifier-first authoring would have prevented every single case.

## When to Use

Use this skill **before** writing any `@article{...}`, `@inproceedings{...}`, `\bibitem{...}`, or similar BibTeX entry. Triggers include:

- "Add a reference to X paper"
- "Write a related-work section"
- "Fix the bibliography"
- "Verify my citations"
- Setting up a new LaTeX paper
- Writing a literature review document (even Markdown / Google Doc)

If the user types `\cite{foo}` and `foo` isn't in the bib yet, this skill applies.

**Do not use** for:
- Fixing prose that describes what a cited paper does (that's a span-level claim check, separate problem)
- Blog posts or non-formal writing where a URL is sufficient

## The Rule

1. You list identifiers. The script fetches metadata. The .bib file is generated.
2. You never type author names, titles, years, or venues into a BibTeX entry.
3. "Manual" entries (for papers without arXiv/DOI/ACL ID) are allowed but flagged — they reintroduce the failure mode.
4. **Citation keys must match the first author the metadata resolves to.** Keys are not opaque IDs — they show up in `.tex` source, in grep, in reviewers' mental models. A key like `lam2025noveltybench` on a paper whose first author is Yiming Zhang is a hallucinated attribution preserved in amber, even if the rendered PDF says "Zhang et al." correctly. Hallucinations must be eliminated wherever they occur, including keys. If a canonical community key exists (ACL Anthology format, DBLP style, conference-preferred), prefer that; otherwise construct `<firstauthor><year><shorttitleword>` from real metadata. **If you find a key that encodes a wrong attribution, rename it** (both in `refs_ids.toml` and every `\cite{}` site) — don't leave the lie in the source.

## Step 1: Check Whether the Project Already Has the Pattern

Look for these files, in order:

- `refs_ids.toml` / `refs_ids.yaml` / `refs.bib` with a `% GENERATED FILE` banner
- `scripts/build_bib.py` or similar
- `CITATIONS.md` / `BIBLIOGRAPHY.md` workflow doc

If the pattern exists: add new entries to the TOML, run the build script, done.

If not: set it up (Step 2).

## Step 2: Set Up the Pattern for a New Project

Minimum four files. Below is a compact reference template. Full working copies of the scripts ship with this skill in `examples/` (see the Reference Implementation section below); copy them into the target project to get started faster.

### `paper/refs_ids.toml` — the only human-editable file

```toml
# Source of truth. Each [[cite]] = citation key + ONE identifier + claim.
# Run: uv run python scripts/build_bib.py

[[cite]]
key   = "vaswani2017attention"
arxiv = "1706.03762"
claim = "Transformer architecture; §3.2 scaled dot-product attention."

[[cite]]
key   = "devlin2019bert"
acl   = "N19-1423"           # ACL Anthology ID if published there
claim = "Pretraining via masked LM."

[[cite]]
key   = "someauthor2024doi"
doi   = "10.1234/xyz.5678"
claim = "Specific claim in §X."

[[cite]]
key   = "radford2019language"    # OpenAI tech report (no arXiv / DOI)
manual = true
entry = """
@techreport{radford2019language,
  author = {Radford, Alec and Wu, Jeffrey and ...},
  ...
}
"""
claim = "GPT-2 architecture / training."
```

**Precedence when multiple identifiers are given:** `acl > doi > arxiv > manual`. The script picks the first that applies, preferring published metadata over preprint.

### `scripts/build_bib.py` — fetches canonical BibTeX

Core responsibilities:

1. Parse `refs_ids.toml` (Python 3.12 `tomllib` is stdlib — no dep).
2. For each entry, dispatch by identifier type:
   - `acl:<id>` → `GET https://aclanthology.org/<id>.bib` (returns BibTeX directly)
   - `doi:<id>` → `GET https://doi.org/<id>` with `Accept: application/x-bibtex` (Crossref content negotiation)
   - `arxiv:<id>` → `GET https://export.arxiv.org/api/query?id_list=<id>` (returns Atom XML — parse manually)
   - `manual` → emit the `entry = """..."""` body verbatim
3. Rewrite the `@type{KEY,...}` key to match the TOML `key=` field (ACL/Crossref emit their own keys).
4. Prepend each entry with `% source:` and `% claim:` comment lines.
5. Write `paper/refs.bib` **atomically** (temp-file + `os.replace`) so a failed run leaves the previous `refs.bib` intact.
6. Fail loudly on: missing field, non-200 HTTP, zero authors, zero title, unresolved identifier.

Fail-loud philosophy: never silently skip errors. `continue` on a missing field is forbidden.

### arXiv API — watch for these gotchas

- Author names with no spaces (e.g. "Qwen") are "corporate authors" and must be braced (`{Qwen}`) in BibTeX so name-parsing doesn't split them. **Also**, if a corporate author appears first, natbib will render "Qwen et al. (2024)" instead of the conventional "Yang et al. (2024)" — provide a `skip_authors = ["Qwen"]` override in the TOML to filter them.
- arXiv emits stray `:` as an "author" between corporate and individual authors — filter out any name with no alphabetic characters.
- arXiv `published` is in ISO 8601; extract year with `[:4]`.
- arXiv `title` may contain multi-line whitespace — collapse with `" ".join(title.split())`.
- arXiv submission year may differ from publication year (e.g. Holtzman "Curious Case" — submitted 2019, ICLR 2020). If the venue year matters, either use `acl:` or `doi:` instead, or add a `year_override` field.

### `scripts/verify_cites.py` — offline linter

Pure stdlib, no network:

1. Parse the `.tex` for all `\cite`, `\citep`, `\citet`, `\citealp`, `\citeauthor`, etc. variants. Strip comments before matching so `% \cite{dead}` is ignored.
2. Parse `refs.bib` entry keys with `@\w+\s*\{\s*([^,\s}]+)`.
3. Exit 2 if any `\cite{}` key is missing from the bib; exit 3 if any bib entry is unused (waivable with `--ignore-unused`).

Regex for `\cite` (handles optional bracket arguments and comma-separated keys):
```python
CITE_RE = re.compile(r"\\cite[a-zA-Z]*\*?(?:\[[^\]]*\])?(?:\[[^\]]*\])?\{([^}]+)\}")
```

### `paper/CITATIONS.md` — workflow sidecar

Every project that uses the pattern needs this. It explains:
- the 4-step workflow (edit TOML → build → verify → latexmk)
- the precedence rule
- what the system prevents vs. doesn't prevent
- references to the APIs used

Users should be able to pick up the pattern from CITATIONS.md alone.

### `tests/test_bib_pipeline.py` — unit tests

- `--offline-manual-only` flag for CI / smoke-testing without network.
- Test: rejects duplicate keys.
- Test: rejects entries with no identifier.
- Test: rewrites the inner `@type{KEY,...}` when manual entry's key differs from TOML's `key`.
- Test: `verify_cites.py` happy path, missing key, unused key, `\cite` variant handling, commented-out cites.

## Step 3: Wire the .tex File

Replace any `\begin{thebibliography}...\end{thebibliography}` block with `\bibliography{refs}`:

```latex
\bibliographystyle{plainnat}
\bibliography{refs}
```

Then run `latexmk -pdf` — bibtex picks up `refs.bib` automatically.

## Step 4: What the System Does NOT Prevent

Be explicit with the user about the system's limits:

1. **Miscited claims.** If the prose says "X showed Y" and X's paper does not show Y, fetching X's BibTeX does nothing. The `claim = "..."` TOML field is the hook for the sister skill `verify-citation-claims`, which dispatches parallel subagents to check each claim against the actual cited paper.
2. **Factual errors in prose next to a citation.** E.g. a misquoted parameter count. Also handled by `verify-citation-claims` as part of span-level review.
3. **Picking the wrong paper to cite.** If the right paper isn't in `refs_ids.toml`, the tool cannot suggest one.

## Common Failure Modes and Fixes

| Symptom | Cause | Fix |
|---|---|---|
| `author = {{Qwen}} and ...` literal braces showing in PDF | over-bracing corporate author | single braces `{Qwen}` inside field delimiter |
| First in-text citation rendering as "Team et al." instead of first human author | corporate author recorded by arXiv | `skip_authors = ["Team"]` in TOML |
| `\cite{key}` rendering as `[?]` | key missing from bib | re-run `build_bib.py`; if still missing, add to TOML |
| Two different "Smith et al. 2025" papers cited | genuine year+author collision | natbib adds `a`/`b` suffixes automatically — no action needed |
| arXiv submission year differs from venue year | paper published at later conference | prefer `acl:` / `doi:` over `arxiv:`, or accept the submission year |
| Crossref returns volume 13 for a paper you thought was volume 15 | the `arxiv:` preprint had wrong metadata | trust the DOI — the published volume is canonical |
| `\cite{lam2025X}` renders as "Zhang et al. 2025" (key and rendered author don't match) | key was hand-typed against a hallucinated first author and never corrected | rename the key to match the real first author; update `refs_ids.toml` and every `\cite{}` site; rebuild `refs.bib` and re-run `verify_cites.py` |

## Reference Implementation

Portable reference implementation ships with this skill in `examples/`:

- `examples/build_bib.py` — the resolver (arXiv / Crossref / ACL Anthology → `paper/refs.bib`, atomic writes, fail-loud).
- `examples/verify_cites.py` — the offline linter. `\cite{}` ↔ `refs.bib` correspondence.
- `examples/test_bib_pipeline.py` — unit tests (10 tests; uses `--offline-manual-only` so CI doesn't need network).
- `examples/refs_ids.toml.example` — sanitized demo TOML with all four identifier types (arxiv / doi / acl / manual) and the `skip_authors` override.

**To use:** copy `examples/build_bib.py`, `examples/verify_cites.py`, `examples/test_bib_pipeline.py` into the target project's `scripts/` and `tests/`. Rename `examples/refs_ids.toml.example` to `paper/refs_ids.toml` and populate with the project's own citations. Add `paper/CITATIONS.md` with the project-specific workflow (this SKILL.md is a template for its content).

The absolute paths in these files assume `scripts/` and `paper/` live at the project root (matching the project layout described in this skill). Tweak the paths at the top of each script if your project uses a different layout.

Don't reimplement from scratch unless the project's stack (e.g. non-Python) requires it.

## Related Skills

- `import-content` — the table/numbers analog. Uses the same "identifier → script → generated artifact" pattern.
