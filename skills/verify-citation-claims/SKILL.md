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

- arXiv: **`https://ar5iv.labs.arxiv.org/html/<id>`** (first choice — version-agnostic, readable HTML). Fall back to `https://arxiv.org/abs/<id>` only if ar5iv is down.
- DOI: `https://doi.org/<id>`
- ACL Anthology: `https://aclanthology.org/<id>/` (and `.pdf`)
- OpenReview: `https://openreview.net/forum?id=<id>`

**arXiv URL guidance — lessons from the 2026-04-22 first-invocation test:**

- `https://ar5iv.labs.arxiv.org/html/<id>` — **Use this first.** It does not require a version suffix (no `v1` / `v2`) and returns readable HTML that WebFetch can parse section-by-section.
- `https://arxiv.org/html/<id>v<N>` — Avoid. Agents routinely guess the wrong version number and get 404s.
- `https://arxiv.org/abs/<id>` — Returns the abstract only. Too thin to verify section-level claims; use only as a last-resort fallback if ar5iv is unreachable.
- `https://arxiv.org/pdf/<id>` — Avoid via WebFetch. Comes back as unreadable binary.

### Step 3: Dispatch one subagent per citation, in parallel

This is the heavy-lifting step. Use the `dispatching-parallel-agents` pattern. A dozen citations verified sequentially takes hours; in parallel, minutes.

**Task-tool fallback:** If the `Task` / parallel-agent tool is not
available in your harness (as was the case during the 2026-04-22
first-invocation test), substitute **parallel `WebFetch` calls issued
in a single message** from the main conversation. The work still
parallelizes at the HTTP level; you lose the isolated-context benefit
(the main agent now carries every paper's content in its window), but
the verification itself still works. Pass the same prompt-template
content as inline instructions, and synthesize the findings yourself.

Per-citation subagent prompt template (also usable as inline guidance
for the `WebFetch` fallback):

```
Task: Verify a citation in a research paper by reading the actual cited
paper and checking that its claims match what our paper says.

**Our paper cites:**
<author(s)> (<year>), "<title>" — <venue>. <identifier>.

**Our paper claims this reference supports:**
1. In <section/paragraph>: "<exact quoted sentence from our paper>"
2. <additional claims if any>

**Your task:**
1. Find the paper via <URL>.
   - For **arXiv** papers, use `https://ar5iv.labs.arxiv.org/html/<id>` as
     the first-try URL. It is version-agnostic (no `v1` / `v2` suffix)
     and returns readable HTML. Do NOT try `arxiv.org/html/<id>v<N>`
     (agents routinely guess the wrong version and get 404s), and do NOT
     WebFetch `arxiv.org/pdf/<id>` (comes back as unreadable binary).
     Fall back to `arxiv.org/abs/<id>` only if ar5iv is down — the
     abstract alone is too thin to verify section-level claims.
   - For DOIs, OpenReview, and ACL Anthology, use the canonical URLs.
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

**If direct fetch fails** (paywall, 404, unreadable PDF), try a
**WebSearch for the specific claim phrase** — a numerical figure, a
section title, or a distinctive quote. It often surfaces the fact on a
cache or citing secondary source (Semantic Scholar, OpenReview
discussion, NASA ADS for physics, DBLP for CS venues, EleutherAI
leaderboards for LM benchmarks). This is particularly useful for
published-venue metadata (journal volumes, page counts) that appears in
indices like ADS, DBLP, or Semantic Scholar.

**If you still cannot access the paper** after trying ar5iv, the
fallback URL, and a WebSearch for the claim phrase, flag clearly:
"UNABLE TO VERIFY — needs manual review." Do NOT guess.

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

## Troubleshooting: When Direct Fetch Fails

Citation verification routinely hits dead ends — a PDF is paywalled,
the HTML link is stale, arXiv times out. Before giving up and marking
"UNABLE TO VERIFY," try in this order:

1. **Wrong arXiv URL shape.** If a subagent reports 404, check whether
   it used `arxiv.org/html/<id>v<N>` (prone to version mismatch) or
   `arxiv.org/pdf/<id>` (unreadable binary). Redirect it to
   `ar5iv.labs.arxiv.org/html/<id>`, which is version-agnostic.
2. **WebSearch for the specific claim phrase.** A numerical figure, a
   section title, or a distinctive quote from the paper often surfaces
   the fact on a cache or citing secondary source: Semantic Scholar,
   OpenReview discussion threads, NASA ADS (physics), DBLP (CS
   venues), or scorecard-style indices like the EleutherAI LM
   leaderboard. This was how the 2026-04-22 test run confirmed a GPT-3
   bits-per-byte number (EleutherAI leaderboard) and a Crutchfield
   journal volume (ADS) when direct fetch didn't work.
3. **Author's homepage / lab page.** Some authors host a free PDF or an
   extended-abstract HTML that evades the venue paywall.
4. **Only after all three fail**, mark "UNABLE TO VERIFY — needs
   manual review." Do NOT guess; guessing reintroduces the
   fabrication failure mode this skill exists to prevent.

## What This Skill Does NOT Handle

- **Numbers inside tables or figures** → that is `import-content`.
- **Typographical and grammar issues** → out of scope; use an editor / linter.
- **Novelty claims** ("we are the first to…") — subagents can sometimes catch these if the cited paper predates the claim and does the same thing, but the skill isn't specifically designed for prior-art search. For serious novelty checks, run a separate literature-search pass.
- **Paywalled papers** — try the Troubleshooting steps above first (WebSearch for the claim phrase often surfaces the fact on a cache or citing secondary source). If all routes fail, report "UNABLE TO VERIFY" and ask the user to check manually or provide a copy.

## Related Skills

- `bibliography-from-ids` — the write-time companion. Prevents fabricated metadata.
- `import-content` — the table-and-numbers analog. Same "script-generated, never hand-typed" principle.
- `dispatching-parallel-agents` — the underlying mechanism for Step 3. Use its conventions for the subagent prompts.
