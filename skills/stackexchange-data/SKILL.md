---
name: stackexchange-data
description: Use when fetching or analyzing StackOverflow / Stack Exchange content (questions, answers, comments, vote scores) for a dataset, audit, or research pipeline. Direct page access is blocked from Matthew's machines (WebFetch refuses the domain; curl gets Cloudflare 403) — this skill gives the working Stack Exchange API path and its empirically-discovered quirks. Triggers - "scrape/fetch/download StackOverflow", "SO answers/comments", "api.stackexchange.com", building datasets from SE sites.
---

# Getting Stack Exchange data

## Do not try to fetch the pages

- `WebFetch` on stackoverflow.com fails with "Claude Code is unable to fetch from stackoverflow.com" (tool-level domain block). Subagents hit the same wall — do not fan out agents to "visit" SE pages.
- `curl` with a browser User-Agent gets a Cloudflare 403.
- The official API (`https://api.stackexchange.com/2.3`) is the working path, and it's *richer* than the rendered page: exact net scores, canonical permalinks, and ALL comments (the page hides comments past the first five behind AJAX).

## API essentials

- Anonymous quota: **300 requests/day/IP** (`quota_remaining` is in every response). No key needed at moderate scale.
- Batch up to **100 ids per request**: `/questions/{id1;id2;...}`, `/comments/{id1;...}`, `/posts/{ids}/comments`.
- Custom filters: `GET /filters/create?include=...&base=none&unsafe=false`. Wrapper fields take a leading dot (`.items;.backoff;.quota_remaining;.has_more`); typed fields are `question.body_markdown`, `answer.score`, `comment.link`, `shallow_user.reputation`, etc. Filter strings are permanent — create once, reuse. Decode an existing filter with `/filters/{filter}`.
- Every question/answer/comment object has a `link` field with its canonical permalink — use these verbatim for citations; never hand-construct SO URLs (comment URLs embed the answer id and are easy to get wrong).

## Quirks that cost hours (all verified empirically, 2026-08)

1. **Nested comments never include body fields.** A filter can request `comment.body_markdown` and `/filters/{id}` will confirm it's included — but comments nested inside `/questions` or `/answers` responses still arrive bodyless. Fetch bodies separately via `/comments/{id1;...;id100}` (bodies DO appear when comment is the top-level type) and merge back by `comment_id`.
2. **`comment.body_markdown` is silently dropped unless `comment.body` is also in the filter.** Include both.
3. **Backoff is strict.** Sleeping exactly `backoff` seconds still yields HTTP 400 `{"error_id":502,"error_name":"throttle_violation"}` — sleep `backoff + 3s` and keep ~2s between requests. Parse the JSON error body instead of `raise_for_status()` (the body says what went wrong); on `throttle_violation`, sleep ~35s and retry once.
4. **Deleted posts vanish silently** — the response just omits those ids. Detect by set-difference against what you asked for; record and fail loudly rather than pressing on.

## Design the fetch to be resumable

Write each batch to disk as it arrives (one JSON per item, or an append-only JSONL) and skip ids already on disk at startup. A throttle kill mid-run then costs nothing.

## Reference implementation

Working, tested scripts (PEP 723, `uv run`):
`/home/matthew/interrogation-protocols/bashbench2_confusions/fetch_question_data.py` (batched questions+answers with filter creation, backoff handling, resume) and `fetch_comments.py` (comment-body fetch + merge-by-id, hard-fails if any nested comment ends up bodyless). Copy these rather than rederiving.
