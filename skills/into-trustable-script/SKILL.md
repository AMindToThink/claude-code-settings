---
name: into-trustable-script
description: Convert a command that needed permission approval into a standalone script (Python or Bash) with hardcoded operations and parameterized inputs, then add it to the allowlist so future invocations run without prompting.
user_invocable: true
---

## Into Trustable Script

Convert a command that required (or would require) permission approval into a **standalone script** with fixed behavior and parameterized inputs, saved to `.claude-tools/` in the project root and added to the Claude Code permission allowlist.

### When to Use

- The user just approved a command and wants to avoid re-approving it
- The user runs `/into-trustable-script` after a command that needed permission
- You notice a repeated pattern of approved commands and suggest this skill

### When NOT to Use

**Long-running or resource-intensive commands are poor candidates.** The point of a trustable script is that it runs without prompting — but that also means it runs without a gut-check. A script that ties up a GPU for 30 minutes or saturates memory for an hour can silently block other work.

Before converting a command that you expect to be long-running or resource-heavy (GPU training, large-scale data processing, batch inference, etc.), **estimate the runtime and resource cost, tell the user, and ask whether they still want it auto-approved.** A command that takes 5 seconds to run 100 times is fine; a command that takes 20 minutes and locks a GPU is something the user probably wants to approve each time.

### Choosing Python vs Bash

**Prefer Python** (`.py`) — it's simpler, easier to read, and avoids heredoc awkwardness. Use Python unless you have a reason not to.

**Use Bash** (`.sh`) only when the script primarily orchestrates shell commands — e.g., combining `pgrep`, `nvidia-smi`, `curl`, `tail` in a status checker. If the bash script would just be a wrapper around a single Python heredoc, skip the wrapper and write Python directly.

### Procedure

#### Step 1: Identify the Command

Look at the most recent command that needed approval (or the command the user points to). Identify:
- **The fixed operation**: what it does (the logic, pipeline, analysis)
- **The variable inputs**: what changes between invocations (file paths, column names, thresholds, flags)

#### Step 2: Write the Script

Create a script at `.claude-tools/<descriptive-name>.py` (or `.sh`). The name should describe the operation, not the inputs (e.g., `csv-summary.py`, `json-structure.py`, `vllm-status.sh`).

##### Python Template

```python
#!/usr/bin/env python3
"""One-line description of what this script does.

Usage: .claude-tools/<name>.py <arg1> <arg2> ...
"""
import sys

def main() -> None:
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <arg1-description> <arg2-description> ...", file=sys.stderr)
        sys.exit(1)

    arg1 = sys.argv[1]

    # --- Validate inputs ---
    # e.g., check files exist, values are in expected range
    import os
    if not os.path.isfile(arg1):
        print(f"Error: file not found: {arg1}", file=sys.stderr)
        sys.exit(1)

    # --- Precondition checks ---
    # Verify the environment can support this operation.
    # See "Precondition Checks" section below.

    # --- Do the work ---
    # Fixed logic using validated inputs
    ...

if __name__ == "__main__":
    main()
```

##### Bash Template

Use this only for shell-heavy scripts that orchestrate multiple CLI tools.

```bash
#!/usr/bin/env bash
set -euo pipefail

# <One-line description>
# Usage: .claude-tools/<name>.sh <arg1> <arg2> ...

if [[ $# -lt <N> ]]; then
  echo "Usage: $0 <arg1-description> ..." >&2
  exit 1
fi

ARG1="$1"
[[ -f "$ARG1" ]] || { echo "Error: file not found: $ARG1" >&2; exit 1; }

# --- Precondition checks ---

# --- Do the work ---
# When embedding Python in bash, use heredocs with single-quoted delimiters:
python3 << 'PYTHON_END' "$ARG1"
import sys
filepath = sys.argv[1]
# ...
PYTHON_END
```

#### Step 3: Script Invariants (MANDATORY)

Every generated script MUST satisfy ALL of these:

1. **No project filesystem writes** — output goes to stdout/stderr only. No creating, modifying, or deleting files in the project or home directory. Temporary files in `/tmp` are acceptable for intermediate data, but clean up after yourself.
2. **No external network access** — no reaching out to the internet. Localhost connections are allowed for checking local services (e.g., health-checking a local API server). No requests to external hosts.
3. **No package installation** — no `pip install`, `uv add`, `apt-get`, etc.
4. **No code execution from arguments** — no `eval()`, no `exec()`, no `subprocess.run(user_string, shell=True)`. In bash: no `eval`, no `python3 -c "$1"`, no `bash -c "$1"`. Arguments are DATA, never CODE.
5. **Input validation** — check argument count, file existence, and value sanity before doing any work.
6. **Precondition checks** — verify the environment can support the operation before starting (see below).
7. **Bash-specific**: starts with `#!/usr/bin/env bash` and `set -euo pipefail`. When embedding Python, use `<< 'PYTHON_END'` (single-quoted delimiter prevents shell interpolation).
8. **Python-specific**: starts with `#!/usr/bin/env python3`. Use `argparse` or `sys.argv` for inputs. Use type hints.

If the desired operation cannot satisfy these invariants (e.g., it needs to write to the project directory or access external services), **do not create the script**. Explain why and suggest the user keep using the regular command with permission prompts.

#### Precondition Checks

Scripts should fail fast with a clear error if the environment isn't ready. Think about what resources the operation needs and verify them before doing work. Common examples:

- **GPU availability**: Check that a GPU is free or has enough VRAM before launching a CUDA job.
  ```python
  import subprocess, sys
  result = subprocess.run(
      ["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
      capture_output=True, text=True,
  )
  if result.returncode != 0:
      print("Error: nvidia-smi not available", file=sys.stderr); sys.exit(1)
  free_mb = [int(x.strip()) for x in result.stdout.strip().split("\n")]
  if not any(m > 20000 for m in free_mb):
      print(f"Error: no GPU with >20GB free VRAM (available: {free_mb} MB)", file=sys.stderr)
      sys.exit(1)
  ```

- **Required Python packages**: Try importing before running main logic.
  ```python
  try:
      import pandas, torch
  except ImportError as e:
      print(f"Error: missing required package: {e.name}", file=sys.stderr)
      sys.exit(1)
  ```

- **Required CLI tools** (bash):
  ```bash
  command -v jq >/dev/null 2>&1 || { echo "Error: jq is required but not installed" >&2; exit 1; }
  ```

- **File size / memory**: Check before loading large files.
  ```python
  import os, sys
  size = os.path.getsize(filepath)
  if size > 2 * 1024**3:
      print(f"Error: file is {size // 1024**2}MB, exceeds 2GB limit", file=sys.stderr)
      sys.exit(1)
  ```

The goal: **never let a trustable script fail silently or waste resources on a doomed operation.** If it can't succeed, it should say why immediately.

#### Step 4: Make Executable

```bash
chmod +x .claude-tools/<name>.py  # or .sh
```

#### Step 5: Add to Allowlist

Read the project's `.claude/settings.json` (or create the permissions section if needed). Add:

```json
"Bash(.claude-tools/<name>.py *)"
```

to the `permissions.allow` array. This allows Claude Code to run the script with any arguments without prompting.

If `.claude/settings.json` doesn't exist for the project, check whether the user wants this in project settings or user settings (`~/.claude/settings.json`).

#### Step 6: Confirm

Tell the user:
- What script was created and what it does
- What arguments it takes
- That future invocations will run without permission prompts
- Remind them they can inspect the script at any time

### Examples

#### Python Example

**Original command** (needed approval):
```bash
python3 -c "import pandas as pd; df = pd.read_csv('data.csv'); print(df.describe())"
```

**Resulting script** (`.claude-tools/csv-summary.py`):
```python
#!/usr/bin/env python3
"""Print summary statistics for a CSV file.

Usage: .claude-tools/csv-summary.py <csv-file>
"""
import os
import sys

def main() -> None:
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <csv-file>", file=sys.stderr)
        sys.exit(1)

    csv_file = sys.argv[1]
    if not os.path.isfile(csv_file):
        print(f"Error: file not found: {csv_file}", file=sys.stderr)
        sys.exit(1)

    try:
        import pandas as pd
    except ImportError:
        print("Error: pandas is required but not installed", file=sys.stderr)
        sys.exit(1)

    df = pd.read_csv(csv_file)
    print(df.describe())

if __name__ == "__main__":
    main()
```

**Allowlist entry**: `Bash(.claude-tools/csv-summary.py *)`

#### Bash Example (shell-heavy)

**Use case**: Check vLLM server status across process, GPU, API, and logs.

**Resulting script** (`.claude-tools/vllm-status.sh`): Bash is appropriate here because it orchestrates `pgrep`, `nvidia-smi`, `curl`, and `tail` — tools that are natural in shell but awkward in Python.

**Allowlist entry**: `Bash(.claude-tools/vllm-status.sh *)`
