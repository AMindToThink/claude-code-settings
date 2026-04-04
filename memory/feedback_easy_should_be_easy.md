---
name: Easy things should be easy
description: When a standard task is unexpectedly hard, diagnose the root cause (usually misconfiguration) before writing custom workarounds. Ask before going custom.
type: feedback
---

When something *should be easy* but is actually hard, stop and figure out why before building workarounds. The root cause is almost always a misconfiguration, not a missing feature.

Before writing custom code (wrappers, scorers, parsers, etc.), ask Matthew. Standard tools exist for standard tasks — hundreds of practitioners use them daily.

**Why:** In a prior project, a 43% failure rate on a standard eval was misdiagnosed as a scorer bug needing a custom wrapper. The actual cause was a `max_tokens` setting too low for the model's reasoning chain. The fix was changing one CLI flag, not writing code.

**How to apply:**
1. Web search for how others solved the same problem
2. Check configuration (flags, env vars, model settings)
3. Ask Matthew before writing anything custom
