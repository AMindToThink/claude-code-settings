---
name: bibliography-from-ids
description: Set up script-generated bibliography entries so citation metadata is never hand-typed. Use when writing or editing a paper's bibliography / references / related-work, adding a citation, verifying an existing bibliography's correctness, or setting up a new paper project. Prevents fabricated author lists, titles, years, and venues by requiring every entry to be fetched from arXiv / Crossref / ACL Anthology via a build script.
---

# Bibliography from Identifiers: Script-Generated References

**Core rule: Never hand-type citation metadata.** You list identifiers; a script fetches canonical BibTeX. Author lists, titles, years, and venues are ALL derived from authoritative APIs — never typed from memory.

This is the citation analog of `import-content` (which does the same for tables and numbers).

## Why This Skill Exists

LLMs — including you — fabricate citation metadata at rates of 14 % to 95 % across domains (see CheckIfExist 2026, GhostCite 2026, BibTeX Citation Hallucinations 2026). The characteristic failure mode is: real paper title, real year, **completely wrong author list**. The author list is what gets rendered in every in-text citation, so this is a load-bearing error.

A real incident (Matthew's ICL-diversity paper, 2026-04-21): audit of 12 citations found 4 fabricated author lists, 1 unsupported claim, 1 wrong volume number, 4 wrong titles. Every fabricated entry pointed to a real paper — the identifier would have been correct if recorded. Identifier-first authoring would have prevented every single case.

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

## Step 1: Check Whether the Project Already Has the Pattern

Look for these files, in order:

- `refs_ids.toml` / `refs_ids.yaml` / `refs.bib` with a `% GENERATED FILE` banner
- `scripts/build_bib.py` or similar
- `CITATIONS.md` / `BIBLIOGRAPHY.md` workflow doc

If the pattern exists: add new entries to the TOML, run the build script, done.

If not: set it up (Step 2).

## Step 2: Set Up the Pattern for a New Project

Minimum four files. Below is a compact reference template. The icl-diversity project has the full reference implementation at `/home/cs29824/matthew/icl-diversity/` — check `scripts/build_bib.py`, `scripts/verify_cites.py`, `paper/refs_ids.toml`, `paper/CITATIONS.md`, `tests/test_bib_pipeline.py` for a complete working example.

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

Fail-loud philosophy — per Matthew's CLAUDE.md: never silently skip errors. `continue` on a missing field is forbidden.

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

## Reference Implementation

Complete worked example with all four files, unit tests, and reference bibliography:

- `/home/cs29824/matthew/icl-diversity/scripts/build_bib.py`
- `/home/cs29824/matthew/icl-diversity/scripts/verify_cites.py`
- `/home/cs29824/matthew/icl-diversity/paper/refs_ids.toml`
- `/home/cs29824/matthew/icl-diversity/paper/refs.bib`
- `/home/cs29824/matthew/icl-diversity/paper/CITATIONS.md`
- `/home/cs29824/matthew/icl-diversity/paper/citation_verification_report.md` (the audit that motivated it)
- `/home/cs29824/matthew/icl-diversity/tests/test_bib_pipeline.py`

Copy and adapt. Don't reimplement from scratch unless the project's stack (e.g. non-Python) requires it.

## Related Skills

- `import-content` — the table/numbers analog. Uses the same "identifier → script → generated artifact" pattern.
