---
name: verify-citation-claims
description: Audit whether a paper's prose actually matches the content of its cited references. Use before submitting / publishing a paper, after substantial prose revisions, when adding a new citation, when reviewing someone else's paper, or any time a user asks to "check the citations" / "verify claims" / "make sure X is supported." Dispatches parallel subagents that fetch each cited paper and verify the specific claim against specific sections. Complements `bibliography-from-ids`, which prevents fabricated metadata; this skill prevents miscited claims and factual drift in surrounding prose.
---

# Verify Citation Claims: Does the Cited Paper Actually Say That?

**Core rule: every `\cite{…}` in a paper must be backed by a claim that the cited paper actually makes.** This skill is how you check.

It is the companion to `bibliography-from-ids`:

| Problem | Skill | When |
|---|---|---|
| Fabricated author lists / titles / years | `bibliography-from-ids` | write time |
| Miscited claims: citation exists, but paper doesn't support the claim | `verify-citation-claims` | review time |
| Factual errors in prose near a citation (wrong context length, wrong volume) | `verify-citation-claims` | review time |

Use both. The first prevents the bib from lying about who wrote what. The second prevents the body text from lying about what they said.

## When to Use

Fire this skill whenever any of these apply:

- A paper is nearing submission / publication
- A user asks to "verify citations," "check the claims," "audit the references," "make sure this is supported," "is this really what they found?"
- A user adds a single new citation and asks whether it supports the claim they're attaching it to
- A user is reviewing someone else's paper
- Substantial prose was added near existing citations (claims may now overclaim what the cited work says)
- After `bibliography-from-ids` has fixed the metadata, but before a final PR / merge

Do NOT fire for:
- Informal writing, blog posts, talk slides
- Verifying numbers in tables (that is `import-content`)
- Fixing BibTeX entries themselves (that is `bibliography-from-ids`)

## The Rule

A citation is supported iff:

1. The cited paper exists and the identifier resolves.
2. The claim in the surrounding sentence can be located in a specific section / equation / table of the cited paper.
3. Any numeric value, method name, or quoted finding mentioned near the citation matches the cited source to within rounding.

If any of (1)–(3) fails, there is a problem that must be reported.

## Process

### Step 1: Inventory every citation and its claim

Parse the paper for all `\cite{…}`, `\citep{…}`, `\citet{…}` etc. For each, record:

- The citation key
- The exact surrounding sentence or sentences making the claim
- Section / paragraph location in the paper
- Any nearby numeric values, method names, or paper-specific jargon

If `paper/refs_ids.toml` exists (from `bibliography-from-ids`), the `claim = "..."` field is a useful starting point but must not be trusted alone — it can be stale, and the surrounding prose may have drifted.

### Step 2: Look up each paper's canonical source

For each citation, record the authoritative URL:

- arXiv: `https://arxiv.org/abs/<id>` (or `.../pdf/<id>` for the PDF)
- DOI: `https://doi.org/<id>`
- ACL Anthology: `https://aclanthology.org/<id>/` (and `.pdf`)
- OpenReview: `https://openreview.net/forum?id=<id>`

Prefer HTML versions for arXiv when available (`https://arxiv.org/html/<id>v<N>`) — they're much easier for WebFetch to parse than PDFs.

### Step 3: Dispatch one subagent per citation, in parallel

This is the heavy-lifting step. Use the `dispatching-parallel-agents` pattern. A dozen citations verified sequentially takes hours; in parallel, minutes.

Per-citation subagent prompt template:

```
Task: Verify a citation in a research paper by reading the actual cited
paper and checking that its claims match what our paper says.

**Our paper cites:**
<author(s)> (<year>), "<title>" — <venue>. <identifier>.

**Our paper claims this reference supports:**
1. In <section/paragraph>: "<exact quoted sentence from our paper>"
2. <additional claims if any>

**Your task:**
1. Find the paper via <URL>. Use WebFetch on the abstract page and the
   full-text HTML / PDF.
2. Read the abstract, introduction, and methods. Then locate the
   specific section(s) relevant to each claim above.
3. Verify:
   - Does the paper actually make this claim?
   - If a specific number is mentioned (e.g., "0.72 bits/byte"), does it
     match what the paper reports? Within rounding?
   - If a specific method is mentioned (e.g., "self-BLEU"), does the
     paper actually use that method?
4. Identify a specific section / equation / table reference that most
   directly supports each claim. Recommend a citation more precise than
   "[cite]" (e.g., "Smith et al. 2024, §3.2" or "Smith et al. 2024,
   Theorem 1").

**If you cannot access the paper** (web search fails, paywall, 404),
flag clearly: "UNABLE TO VERIFY — needs manual review." Do NOT guess.

**Return a short report (~300 words) with:**
- arxiv / DOI / canonical URL
- Whether each claim is supported, partially supported, or unsupported
- Specific section / page / equation reference for each claim
- Any concerns (e.g., paper doesn't make the claim we attribute to it,
  numbers off by more than rounding, wrong method name)
- Any additional relevant information worth flagging (while reading,
  did you notice OTHER nearby claims in our paper that this paper could
  support or contradict?)
```

Critical prompt details:

- **"UNABLE TO VERIFY" escape hatch**: Without this, subagents will guess and return plausible-sounding fabrications. Always include.
- **Ask for specific section / equation / table references**: Produces more rigorous verification. A subagent that has to cite Section 3.2 can't handwave.
- **"Any additional relevant information worth flagging"**: Catches the bonus errors. In the 2026-04-21 incident, this prompt caught the Crutchfield volume-13-vs-15 error — which was in no subagent's explicit task.
- **Real paper title, authors, venue in the prompt**: Sometimes the .bib is wrong (see `bibliography-from-ids`). Include both the user-supplied fields AND ask the subagent to verify the author list against the actual paper.

### Step 4: Synthesize into a report

For each citation, report: **Verified** / **Discrepancy** / **Unable to Verify**. Group by severity:

- **HIGH**: Fabricated author lists, unsupported claims, numbers off by > rounding
- **MEDIUM**: Wrong numbers / titles / venues in prose near citation, wrong framing of the paper
- **LOW**: Wording nuances, preprint-vs-venue year ambiguities, minor typos

Save the report to `paper/citation_verification_report.md` (or `reports/…`) so it's a diffable artifact. Include a summary table at the top, detailed findings per citation below, and explicitly flag items needing manual review.

### Step 5: Act on the findings

For each flagged item, the fix belongs in one of three places — be clear about which:

- **The bib entry** is wrong → `bibliography-from-ids` territory. Add / fix / swap the identifier in `refs_ids.toml`. Don't hand-edit the `.bib`.
- **The `\cite{}` targets the wrong paper** → swap the citation. If replacing a preprint with a conference version, usually keep the key and just change the identifier in the TOML. If swapping to a different paper entirely, add a new TOML entry and change the `\cite{}` site.
- **The prose is wrong** → edit the prose. Factual drift like "Qwen2.5-32B, 32K context" (actually 128K) is purely prose-side.

When in doubt, ask the user which of the three to apply. Some disagreements are judgment calls (e.g., whether a paper's Shannon-entropy diversity measure "typically operates at the surface level" — arguably yes in spirit, arguably no in letter).

## Worked Example

A sanitized example audit report ships with this skill at
`examples/example_report.md`. It shows the expected output format:
summary table, per-citation detailed findings, items-needing-review,
items-that-are-fine, and papers-unable-to-access sections.

The real 2026-04-21 audit that motivated this skill (12 citations,
2 minutes wall-clock via parallel subagents, 4 fabricated author lists
found) followed the same template. Findings were routed per Step 5:
bib-side fixes via `bibliography-from-ids`, prose-side factual errors
(e.g. a wrong context-window number) via hand-edit of the .tex, and one
cite-side fix (citation didn't support its claim) via a paper-swap that
touched both the bib and the `\cite{}` site.

## Interaction with `bibliography-from-ids`

If the user sets up the bibliography with `bibliography-from-ids` from the start, this skill becomes cheaper and more targeted:

- The `claim = "..."` TOML field is pre-written, so Step 1 is mostly done.
- The identifier is already canonical, so Step 2 is done.
- Verification is then purely claim-side.

If the project doesn't use `bibliography-from-ids` yet, you can do Step 1 yourself by reading the `.tex` and grep'ing for `\cite{}` sites. Consider recommending `bibliography-from-ids` to the user as part of the findings.

## What This Skill Does NOT Handle

- **Numbers inside tables or figures** → that is `import-content`.
- **Typographical and grammar issues** → out of scope; use an editor / linter.
- **Novelty claims** ("we are the first to…") — subagents can sometimes catch these if the cited paper predates the claim and does the same thing, but the skill isn't specifically designed for prior-art search. For serious novelty checks, run a separate literature-search pass.
- **Paywalled papers** — report "UNABLE TO VERIFY" and ask the user to check manually or provide a copy.

## Related Skills

- `bibliography-from-ids` — the write-time companion. Prevents fabricated metadata.
- `import-content` — the table-and-numbers analog. Same "script-generated, never hand-typed" principle.
- `dispatching-parallel-agents` — the underlying mechanism for Step 3. Use its conventions for the subagent prompts.
