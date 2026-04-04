---
name: Never override framework defaults without cause
description: Do not override default settings (max_tokens, temperature, etc.) unless there is a diagnosed reason. Ask before adding non-default settings.
type: feedback
---

Never override a framework's default settings unless there is a specific, diagnosed reason. Ask before adding any non-default parameter.

**Why:** A speculative `--max-tokens` override was added early in a project and carried forward through multiple iterations. It caused failures on reasoning models (truncated before writing answers) and silently degraded non-reasoning model scores (provider capped at 4096 regardless of the override). The framework default ("model specific") would have used the correct values automatically. This wasted significant time, tokens, and experiment runs.

**How to apply:** When using a tool/framework, start with all defaults. If something fails, diagnose the root cause before changing settings. If you want to add a non-default setting, explain why and ask first.
