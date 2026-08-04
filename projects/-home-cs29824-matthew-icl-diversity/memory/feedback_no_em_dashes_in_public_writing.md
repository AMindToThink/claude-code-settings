---
name: No em-dashes in public-facing writing
description: Avoid em-dashes (— or LaTeX originSessionId: 73781dba-5759-498c-a9c7-7c527e51ac97
---
) in any prose Matthew will publish — papers, README, blog posts, public docs. Use commas, colons, parens, semicolons, or sentence breaks instead.
type: feedback
---

Do not use em-dashes (Unicode `—` or LaTeX `---`) in any prose that Matthew will publish externally: paper sections, README files, blog posts, public documentation, conference submissions.

**Why:** Em-dashes are a stylistic tell of LLM-generated prose; Matthew prefers human-flavored punctuation in anything that goes out under his name. He has stated this preference; treat it as a hard rule for public writing, not a stylistic suggestion.

**How to apply:**
- Sweep on every public-prose edit: when adding or rewriting prose in `paper/`, `README*.md`, blog posts, or any file the user publishes, ensure no `---` or `—` remains in the new text.
- Replacement choice depends on what the em-dash is doing:
  - Parenthetical insertion → comma pair, or parentheses for weaker asides.
  - Cap before a clarification, list, or definition → colon.
  - Strong break / change of direction → period (new sentence) or semicolon.
  - Range (numerical) → en-dash `--` or `\textendash` — these are NOT em-dashes and stay.
- Internal artefacts are out of scope: code comments, CLAUDE.md, internal markdown notes, commit messages, and todos can keep em-dashes if they were already there. The rule is about what reaches a public audience.
- LaTeX gotcha: `--` is en-dash (ranges), `---` is em-dash (the thing to avoid). Don't mass-replace `--` and break number ranges like `pages 5--7`.
- When in doubt about a specific replacement that could shift emphasis or alter a claim, flag it rather than choosing silently — the paper-prose-one-at-a-time rule still applies.
