---
name: into-trustable-bash
description: Convert a command that needed permission approval into a standalone bash script with hardcoded operations and parameterized inputs, then add it to the allowlist so future invocations run without prompting.
user_invocable: true
---

## Into Trustable Bash

Convert a command that required (or would require) permission approval into a **standalone bash script** with fixed behavior and parameterized inputs, saved to `.claude-tools/` in the project root and added to the Claude Code permission allowlist.

### When to Use

- The user just approved a command and wants to avoid re-approving it
- The user runs `/into-trustable-bash` after a command that needed permission
- You notice a repeated pattern of approved commands and suggest this skill

### Procedure

#### Step 1: Identify the Command

Look at the most recent command that needed approval (or the command the user points to). Identify:
- **The fixed operation**: what it does (the logic, pipeline, analysis)
- **The variable inputs**: what changes between invocations (file paths, column names, thresholds, flags)

#### Step 2: Write the Script

Create a script at `.claude-tools/<descriptive-name>.sh` in the project root. The name should describe the operation, not the inputs (e.g., `csv-summary.sh`, `json-structure.sh`, `count-lines-by-type.sh`).

Every script MUST follow this template:

```bash
#!/usr/bin/env bash
set -euo pipefail

# <One-line description of what this script does>
# Usage: .claude-tools/<name>.sh <arg1> <arg2> ...

# --- Input validation ---
if [[ $# -lt <N> ]]; then
  echo "Usage: $0 <arg1-description> <arg2-description> ..." >&2
  exit 1
fi

ARG1="$1"
ARG2="$2"
# ... assign all args to named variables upfront

# --- Validate inputs exist / are sane ---
# e.g., check files exist, values are in expected range
[[ -f "$ARG1" ]] || { echo "Error: file not found: $ARG1" >&2; exit 1; }

# --- Precondition checks ---
# Verify the environment can support this operation before starting.
# See "Precondition Checks" section below for examples.

# --- Do the work ---
# Hardcoded operation using the validated inputs
# If Python is needed, use a heredoc:
python3 << 'PYTHON_END' "$ARG1"
import sys
filepath = sys.argv[1]
# ... fixed logic here ...
PYTHON_END
```

#### Step 3: Script Invariants (MANDATORY)

Every generated script MUST satisfy ALL of these:

1. **Starts with** `#!/usr/bin/env bash` and `set -euo pipefail`
2. **No filesystem writes** — output goes to stdout/stderr only. No creating, modifying, or deleting files.
3. **No network access** — no `curl`, `wget`, `requests`, `urllib`, etc.
4. **No package installation** — no `pip install`, `uv add`, `apt-get`, etc.
5. **No code execution from arguments** — no `eval`, no `python3 -c "$1"`, no `bash -c "$1"`. Arguments are DATA, never CODE.
6. **Input validation** — check argument count, file existence, and value sanity before doing any work.
7. **Precondition checks** — verify the environment can support the operation before starting (see below).
8. **Python via heredoc** — when embedding Python, use `<< 'PYTHON_END'` (single-quoted delimiter prevents shell interpolation). Pass inputs via `sys.argv` or environment variables, not shell variable substitution inside the heredoc.

If the desired operation cannot satisfy these invariants (e.g., it needs to write files or access the network), **do not create the script**. Explain why and suggest the user keep using the regular command with permission prompts.

#### Precondition Checks

Scripts should fail fast with a clear error if the environment isn't ready. Think about what resources the operation needs and verify them before doing work. Common examples:

- **GPU availability**: Check that a GPU is free (or has enough free VRAM) before launching a CUDA job. A script that silently falls back to CPU or OOMs mid-run wastes time.
  ```bash
  # Check that at least one GPU has >20GB free VRAM
  python3 << 'CHECK_GPU'
  import subprocess, sys, json
  result = subprocess.run(
      ["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
      capture_output=True, text=True
  )
  if result.returncode != 0:
      print("Error: nvidia-smi not available", file=sys.stderr); sys.exit(1)
  free_mb = [int(x.strip()) for x in result.stdout.strip().split("\n")]
  if not any(m > 20000 for m in free_mb):
      print(f"Error: no GPU with >20GB free VRAM (available: {free_mb} MB)", file=sys.stderr)
      sys.exit(1)
  CHECK_GPU
  ```

- **Required tools**: Check that commands the script depends on are installed.
  ```bash
  command -v jq >/dev/null 2>&1 || { echo "Error: jq is required but not installed" >&2; exit 1; }
  ```

- **Required Python packages**: Check imports before running the main logic.
  ```bash
  python3 -c "import pandas, torch" 2>/dev/null || {
      echo "Error: required Python packages not installed (pandas, torch)" >&2; exit 1;
  }
  ```

- **File size / memory**: If the operation loads a large file into memory, check that the file isn't unreasonably large.
  ```bash
  FILE_SIZE=$(stat -c%s "$INPUT_FILE" 2>/dev/null || stat -f%z "$INPUT_FILE")
  MAX_SIZE=$((2 * 1024 * 1024 * 1024))  # 2GB
  if (( FILE_SIZE > MAX_SIZE )); then
      echo "Error: file is $(( FILE_SIZE / 1024 / 1024 ))MB, exceeds 2GB limit" >&2; exit 1
  fi
  ```

The goal: **never let a trustable script fail silently or waste resources on a doomed operation.** If it can't succeed, it should say why immediately.

#### Step 4: Make Executable

```bash
chmod +x .claude-tools/<name>.sh
```

#### Step 5: Add to Allowlist

Read the project's `.claude/settings.json` (or create the permissions section if needed). Add:

```json
"Bash(.claude-tools/<name>.sh *)"
```

to the `permissions.allow` array. This allows Claude Code to run the script with any arguments without prompting.

If `.claude/settings.json` doesn't exist for the project, check whether the user wants this in project settings or user settings (`~/.claude/settings.json`).

#### Step 6: Confirm

Tell the user:
- What script was created and what it does
- What arguments it takes
- That future invocations will run without permission prompts
- Remind them they can inspect the script at any time: `.claude-tools/<name>.sh`

### Example

**Original command** (needed approval):
```bash
python3 -c "import pandas as pd; df = pd.read_csv('$FILE'); print(df.describe())"
```

**Resulting script** (`.claude-tools/csv-summary.sh`):
```bash
#!/usr/bin/env bash
set -euo pipefail

# Print summary statistics for a CSV file
# Usage: .claude-tools/csv-summary.sh <csv-file>

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <csv-file>" >&2
  exit 1
fi

CSV_FILE="$1"
[[ -f "$CSV_FILE" ]] || { echo "Error: file not found: $CSV_FILE" >&2; exit 1; }

python3 -c "import pandas" 2>/dev/null || {
    echo "Error: pandas is required but not installed" >&2; exit 1;
}

python3 << 'PYTHON_END' "$CSV_FILE"
import pandas as pd
import sys

filepath = sys.argv[1]
df = pd.read_csv(filepath)
print(df.describe())
PYTHON_END
```

**Allowlist entry**: `Bash(.claude-tools/csv-summary.sh *)`
