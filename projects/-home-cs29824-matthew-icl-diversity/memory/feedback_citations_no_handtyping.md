---
name: Never hand-type citation metadata
description: HIGH PRIORITY — use identifier-first workflow (arXiv ID / DOI / ACL ID → script → refs.bib) for every citation; never type author lists, titles, years, or venues from memory
type: feedback
originSessionId: ae22186f-3186-420c-a73d-06927acc2741
---
**Rule:** Every BibTeX entry in a paper must be generated from a stable identifier (arXiv ID, DOI, or ACL Anthology ID) via a build script. Author lists, titles, years, and venues are never typed from memory — not even "just this one small change."

**Why:** Audit on 2026-04-21 of Matthew's ICL-diversity paper found **5 of 12 citations with high-severity errors**:
- 4 completely fabricated author lists (Lai et al. → actually sole-author Diaz-Rodriguez; Chen et al. → actually Guo et al.; He et al. → actually Zhang, Peng, Bollegala; Lam, Do → actually Zhang, Diddee, et al.)
- 1 unsupported claim (Zhang 2024 allegedly using self-BLEU but actually uses Shannon entropy)
- Plus 4 wrong titles, 1 wrong year, 1 wrong journal volume (Crutchfield Chaos 15 → actually vol 13)

Every fabricated entry pointed to a real paper — the identifier would have been correct if recorded. The failure mode is LLM-typical: real title + real year + fabricated authors. Literature (CheckIfExist 2026, GhostCite 2026) reports fabrication rates of 14 %–95 % across LLMs. This is not a rare bug; it is the default behaviour of untooled citation authoring.

**How to apply:**
- Two complementary skills cover the problem:
  - `bibliography-from-ids` — write-time. Ensures every BibTeX entry is fetched from arXiv / Crossref / ACL Anthology rather than hand-typed. Fire this whenever adding / editing the bibliography or a single new `\cite{}`.
  - `verify-citation-claims` — review-time. Dispatches parallel subagents to check each `\cite{}`'s surrounding claim against the actual cited paper (catches miscited claims and factual drift in prose that the write-time tool cannot). Fire this before submission, after substantial prose revisions, or when a user asks to "check the citations."
- Reference implementation at `/home/cs29824/matthew/icl-diversity/`: `scripts/build_bib.py`, `scripts/verify_cites.py`, `paper/refs_ids.toml`, `paper/CITATIONS.md`, `paper/citation_verification_report.md` (the one-time audit that motivated the tooling). Copy and adapt for any new paper project.
- For this specific paper: `refs_ids.toml` is the only file to edit; `uv run python scripts/build_bib.py` regenerates `refs.bib`; `uv run python scripts/verify_cites.py` lints `\cite{}` ↔ `refs.bib` correspondence.
- If a user asks to "add a citation" without mentioning the tooling, still use the tooling. Don't let the convenient shortcut of hand-typing an entry win.
- Manual entries (OpenAI tech reports, etc.) are permitted but must be rare — each one is a reintroduced failure mode.

**Also**: this pattern is symmetric with `user_cite_sources.md` / `feedback_cite_sources.md` (which require script-sourced NUMBERS) — together, no load-bearing content (tables, numbers, or citations) is ever hand-typed.
