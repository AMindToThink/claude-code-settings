---
name: read-entire
description: Read the entirety of one or more files without skipping or chunking. Use when the user wants you to read complete files and not summarize or truncate.
user_invocable: true
---

## Read Entire — Complete File Reading

The user has explicitly asked you to read one or more files **in their entirety**. This is a deliberate, conscious request. Do NOT:

- Read only parts of the file
- Use `head`, `tail`, or limited line ranges
- Say "the file is too large, let me read it in sections" and then only read some sections
- Summarize or skip sections
- Stop partway through and say "I have enough context"

### How to read the entire file

1. First attempt: use `Read` with no `offset` or `limit` parameters.
2. If the file is too large for a single Read call (>2000 lines), you MUST paginate through the ENTIRE file using `offset` and `limit`, reading sequential chunks until you reach the end. Do not stop after the first chunk.

Example for a 6000-line file:
```
Read file_path="..." offset=0 limit=2000
Read file_path="..." offset=2000 limit=2000
Read file_path="..." offset=4000 limit=2000
```

3. For `.md` files that fail due to embedded base64 images, use the `read-large-md` skill technique.

### Multiple files

If the user provides multiple file paths, read ALL of each file completely. Launch parallel Read calls when possible.

### After reading

Only after you have read the complete contents of every requested file should you proceed with whatever task the user has asked you to do. Do not start working on the task with partial file contents.

### Arguments

Pass the file paths as arguments. Example: `/read-entire path/to/file1.tex path/to/file2.md`

If no file paths are given, ask the user which files to read.
