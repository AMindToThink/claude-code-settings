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