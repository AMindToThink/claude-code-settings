---
name: Matthew's multi-message style and how to handle it
description: Matthew sends multiple messages while Claude works — use prefix to determine priority (After this / Stop / For later)
type: user
---

Matthew likes to send follow-up messages while Claude is working, rather than waiting. This is helpful — it keeps context flowing. Handle based on framing:

- "After this:" or "Next:" → finish current task first, then address
- "Stop" or interrupting a tool → stop immediately and address
- "For later:" or "thinking out loud:" → note it, finish current work, address when natural
- No prefix → default to finishing current task first, then address
