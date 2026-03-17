---
name: read-large-md
description: Read markdown files that are too large for the Read tool due to embedded base64 images. Use when Read fails with "exceeds maximum allowed size" on a .md file.
user-invocable: false
---

## Reading Large Markdown Files with Embedded Images

Markdown files exported from Google Docs or similar tools often contain base64-encoded inline images (`![alt](data:image/png;base64,...)`) on single very long lines. These make the file hundreds of KB or millions of tokens, causing the Read tool to fail with "exceeds maximum allowed size" or "exceeds maximum allowed tokens."

### Technique

Use **Grep** to extract only the text lines, filtering out image data:

```
Grep pattern="^[^!]" path="<file>" output_mode="content" head_limit=200
```

This matches all lines that do NOT start with `!` (markdown image syntax), skipping the `![...](data:image/png;base64,...)` lines.

### Paginating through results

Use `offset` and `head_limit` to read in chunks:

```
Grep pattern="^[^!]" path="<file>" output_mode="content" offset=0 head_limit=200
Grep pattern="^[^!]" path="<file>" output_mode="content" offset=200 head_limit=200
```

### Finding specific sections

Search directly for section headers or keywords:

```
Grep pattern="## Theory of Change" path="<file>" output_mode="content" -A=30
```

### When to use this

- Read tool fails on a `.md` file due to size
- The file is known to contain embedded images (e.g., Google Docs export)
- You need the text content but not the images
