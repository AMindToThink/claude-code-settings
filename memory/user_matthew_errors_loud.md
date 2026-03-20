---
name: Matthew wants errors loud — never suppress warnings or soften failures
description: Matthew strongly prefers loud errors over clean output — don't suppress warnings, don't soften error messages, don't auto-fix problems silently
type: user
---

Matthew wants errors and warnings to be as loud as possible. When something goes wrong or looks wrong, it should crash or warn prominently — never be silently fixed or suppressed.

Specific patterns to avoid:
- Don't suppress upstream warnings to make output cleaner
- Don't auto-downgrade errors to warnings
- Don't use `continue` to skip errors in loops
- Don't catch exceptions and log them at a lower level
- Don't add fallback behavior that masks the real problem

When in doubt, fail loudly. Matthew would rather investigate a false alarm than miss a real bug.
