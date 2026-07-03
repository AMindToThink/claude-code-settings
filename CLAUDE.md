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

# Error Handling Philosophy

- **Never use `continue` to silently skip errors.** If something would fail, fail loudly and early. Crashing on bad input is good — it surfaces the problem immediately.
- Validate preconditions upfront and raise/exit before doing any work, rather than catching errors mid-loop and pressing on.
- Prefer failing fast over producing partial/misleading results.

# Subagent model default

Subagents (the Task/Agent tool, plus the built-in Explore/Plan/general-purpose agents) should default to **Sonnet 5**. The recent Sonnet is strong enough for most delegated work, and this keeps subagent cost and latency well below running them on the main model (Opus/Fable).

- **Where it lives:** `env.CLAUDE_CODE_SUBAGENT_MODEL` = `"sonnet"` in `~/.claude/settings.json`. There is no dedicated settings key for a default subagent model — this env var is the official lever (Claude Code subagents docs). Takes effect on new sessions.
- **Precedence (important):** this env var is FIRST in subagent model resolution — it overrides both a per-invocation `model` parameter AND an agent file's `model:` frontmatter. So it is a hard default, not a soft one: even an agent explicitly asking for Opus gets Sonnet while the var is set. To run a specific agent on a different model, change or unset the var.
- **Keep this updated as models release and capabilities shift.** Re-evaluate the value whenever a new model ships — bump it to the newest strong, cost-effective tier for delegated work (a future Sonnet, or whatever best balances capability vs cost). Don't let it stagnate on an outdated model.

# Advisor model (`/advisor`) — when to invoke

`/advisor` consults a stronger, more expensive model. Getting the right answer, writing good code, and doing good research are valuable, and the advisor helps with all three — but it is bottlenecked by cost and has limitations in its use, so invoke it wisely.

**Invoke the advisor for:**
- Debugging, once you've struggled for ~5 minutes or more — or immediately, if you expect the bug to be hard.
- Math/proof-writing help when the math is strange or nonstandard.
- Identifying why a *particular* log/trajectory went the way it did. Not for bulk-reading lots of logs/trajectories unless explicitly asked.
- Interpreting research results (e.g., "what is the most interesting feature?") — especially when results are surprising. This often involves reading logs.
- Planning or suggesting next experiments.

**NEVER invoke the advisor for:**
- Anything sensitive or cybersecurity-related. The guardrails are strict and err strongly toward false positives — a refusal wastes the call. Project CLAUDE.md files may tighten this further (e.g., AI Control projects, whose logs/trajectories are cybersecurity-related).
- Routine work.

**If a consult doesn't resolve the problem** — that usually reflects confusion the advisor is still better placed to untangle:
1. First consult fails → refine your own understanding, then consult again.
2. Second fails → consult a third time, giving the advisor more freedom and scope to figure things out itself.
3. Third fails → your call: wait for a human, or keep working the problem yourself.

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