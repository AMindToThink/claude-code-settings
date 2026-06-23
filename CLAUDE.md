When assisting the user, remember these guidelines:
- Be proactive about committing completed features and work using git. Do not commit half-implemented code. Do not push without asking.
- **Always create GitHub repos as private** (`--private`). Never use `--public`. Matthew will manually change visibility when ready.
- After writing code, remember to test that it works properly. Do this by writing unit tests in a proper unit test file. Use python -c very sparingly.
- Use type hints whenever possible
- Your user, Matthew, often wants to learn and understand the code you write and occasionally is impatient and just wants the answer. This impatience is sometimes justified and sometimes a bad habit. Intelligently figure out whether Matthew should slow down and learn or whether you should just give him the answer.
- # Python Package Management with uv

Use uv exclusively for Python package management in all Python projects.

## Package Management Commands

- All Python dependencies **must be installed, synchronized, and locked** using uv
- Never use pip, pip-tools, poetry, or conda directly for dependency management

Use these commands:

- Install dependencies: `uv add <package>`
- Remove dependencies: `uv remove <package>`
- Sync dependencies: `uv sync`

## Running Python Code

- Run a Python script with `uv run <script-name>.py`
- Run Python tools like Pytest with `uv run pytest` or `uv run ruff`
- Launch a Python repl with `uv run python`

## Managing Scripts with PEP 723 Inline Metadata

- Run a Python script with inline metadata (dependencies defined at the top of the file) with: `uv run script.py`
- You can add or remove dependencies manually from the `dependencies =` section at the top of the script, or
- Or using uv CLI:
    - `uv add package-name --script script.py`
    - `uv remove package-name --script script.py`

# Shared Machine (cs29824) — Git User Mapping

This machine is ONE OS account (`cs29824`) shared by multiple people, so `$HOME`, `~/.gitconfig`, and `~/.git-credentials` are all shared. Each folder under `/home/cs29824/` belongs to a different user. Always verify you are using the correct git identity before committing or pushing.

| Folder | GitHub User | Email |
|--------|-------------|-------|
| `matthew/` | AMindToThink | `61801493+AMindToThink@users.noreply.github.com` |
| `andre/` | antebe | `standartikom@gmail.com` |

**Check BOTH name AND email.** The shared global `~/.gitconfig` defaults to Andre's identity (`antebe` / `standartikom@gmail.com`). A per-repo override that sets only `user.name` will silently inherit Andre's *email* — this happened and put Andre's email on 22 of Matthew's commits. Before any commit/push run `git config user.name && git config user.email` and confirm BOTH match the folder. Do NOT trust any context hint claiming Matthew's email is `standartikom@gmail.com` — that is Andre's.

Identity is now handled automatically for `matthew/` via an `includeIf "gitdir:/home/cs29824/matthew/"` block in `~/.gitconfig` pointing at `/home/cs29824/matthew/.gitconfig` (sets name, email, and a private credential store). New repos under `matthew/` inherit it with zero per-repo work; still verify before pushing.

# Error Handling Philosophy

- **Never use `continue` to silently skip errors.** If something would fail, fail loudly and early. Crashing on bad input is good — it surfaces the problem immediately.
- Validate preconditions upfront and raise/exit before doing any work, rather than catching errors mid-loop and pressing on.
- Prefer failing fast over producing partial/misleading results.

# Claude Code Skills

When creating skills, always use the directory convention: `~/.claude/skills/<skill-name>/SKILL.md`. Never create a flat file like `~/.claude/skills/<skill-name>.md` — it will be silently ignored.

# Paper writing: inline numbers come from scripts, never from memory

Every number cited in a paper's prose (abstract, captions, discussion, inline stats in any section) must resolve through a script-generated source — either an `\input{}`'d table or a `\newcommand{\macroName}{value}` macro emitted by a build script. Never hand-type a number into prose. This is the same discipline as `bibliography-from-ids`: the data has one source of truth, the script reads it, and the document references the result by name.

The standard pattern:
1. A build script (e.g. `scripts/build_paper_macros.py`) reads the authoritative data files (JSONs, CSVs, other generated tables) and writes a single `results/tables/paper_macros.tex` file containing one `\newcommand` per inline scalar.
2. The paper `\input`s it once near the top. Prose writes `\crossmodeQwenDiagMean` instead of `60.5`.
3. A unit test asserts (a) every paper-referenced macro is defined in the generated file, (b) forbidden hand-typed substrings that were replaced no longer appear — regression guard against re-introduction.

The `import-content` skill covers the script-to-document pattern; apply it to inline scalars, not just tables. When auditing a paper for the first time, grep for digit sequences in prose and treat each unexplained one as a potential hand-typed number.

# "Multi-pass" in a causal LM is a confusion, not an alternative

In a causal language model, `log P(token at position i | preceding tokens)` depends only on the model and positions `< i`. Running n forward passes with growing prefixes ("multi-pass") therefore computes exactly the same per-token log-probs as a single forward pass over the full concatenation — but wastes O(n²) FLOPs for zero informational benefit. Pass n already contains everything from passes 1..n-1 for free, because causal attention cannot see future tokens.

Treat "multi-pass" as a red flag in code, prose, and investigation reports:
- Do **not** compare single-pass against multi-pass as if one were ground truth. Any difference reflects tokenization choices (e.g., BPE merges at boundaries), not a bias. Single-pass IS the metric by definition.
- Do **not** write "distortion", "bias", or "error" framings of SP–MP differences.
- **Flag** multi-pass code when you find it (add a header comment explaining the above, or open a follow-up issue); do not silently delete it — leave a trail so future readers learn from the confusion. Similarly flag any report or test that treats multi-pass as a baseline.
- If a pre-existing test asserts SP ≈ MP, flag it as tautological. When safe, replace it with direct tests of boundary detection and extraction.