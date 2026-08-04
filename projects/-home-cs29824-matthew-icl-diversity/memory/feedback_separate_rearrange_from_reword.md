---
name: separate-rearrange-from-reword
description: Standing rule — never mix rearranging text with adding/removing/rewording it in one action
metadata: 
  node_type: memory
  type: feedback
  originSessionId: e9d514d3-7dbc-48fa-a20c-6b2424dd6317
  modified: 2026-08-04T04:02:33.191Z
---

Standing rule from Matthew (2026-08-03, paper-rebuttal session): ALWAYS perform rearranging (moving/reordering existing text) and content changes (adding, removing, rewording) as separate actions.

**Why:** Mixed diffs are hard to review. A pure move shows as relocation; a pure reword shows as a small delta. Combined, every change must be re-read word-by-word to find what actually changed. Matthew reviews edits manually, especially on prose he authored ([[paper-prose-one-at-a-time]] is the paper-prose version of this rule).

**How to apply:** First action: rearrange verbatim (typos and all — flag them, don't fix them). Later actions: propose wording changes one at a time with a one-line rationale each. If dropping obviously discarded scratch text during a rearrangement, list every dropped piece explicitly so it can be vetoed.
