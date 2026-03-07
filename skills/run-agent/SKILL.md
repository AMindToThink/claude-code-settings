---
name: run-agent
description: Run a custom agent by name
argument-hint: <agent-name> [task description]
disable-model-invocation: true
---

Delegate the following task to the **$ARGUMENTS[0]** agent. If additional arguments were provided, use them as the task description. If no task description was provided, ask the user what they'd like the agent to do.
