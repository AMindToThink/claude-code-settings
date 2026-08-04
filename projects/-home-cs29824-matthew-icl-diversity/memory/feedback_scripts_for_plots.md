---
name: Always write plotting code to files
description: Never use inline python -c for plots; always write to a script file for reproducibility
type: feedback
---

Always write plotting/analysis code to files (not inline `python -c`). Matthew wants scripts to be repeatable.

**Why:** Reproducibility. If a plot needs to be regenerated, the command to produce it should be a script file that can be re-run, not an inline command lost in conversation history.

**How to apply:** When generating plots or analysis output, always create a `.py` script file first, then run it.
