---
name: Commit before deleting, even for untracked files
description: When the user asks to delete a file, assume they want it preserved in git history unless they explicitly say otherwise — stage + commit first, then delete + commit. Do not silently rm untracked files, especially in auto mode.
type: feedback
originSessionId: ae22186f-3186-420c-a73d-06927acc2741
---
**Rule:** When the user says "delete X" or "remove X," default to the **commit-then-delete** pattern — even if the file is currently untracked. Stage and commit the file first (so it lives in git history forever), then `git rm` it and commit the deletion. Only skip the preservation step if the user explicitly says the file has no historical value or asks you to just remove it from the working tree.

Also: `rm` of an untracked file is a destructive action per the main system prompt. In auto mode, confirm before running it — "auto mode is not a license to destroy."

**Why:** On 2026-04-21, after the user asked me to "delete the branch handoff doc" as the last step of a multi-step plan, I ran `rm paper/OTHER_BRANCH_HANDOFF.md` on a file that was untracked. The user's next message: "Oh wow, you deleted the handoff file! I didn't want you to do that, and I'm surprised auto mode allowed it. I thought I indicated I wanted it committed, then deleted so it would remain in git history." They invoked `/feedback` to flag this as an auto-mode failure.

The user's implicit model was "delete" = "drop from working tree while preserving in history" (the commit-then-rm-then-commit pattern). My literal interpretation was "delete" = "rm from disk." For a file that was never tracked, my literal reading meant the content vanished entirely. I recovered by recreating the file from conversation context, then committing create + delete — but this only worked because the content was still in my scrollback. If the conversation had been compacted or I'd been a different session, the content would have been unrecoverable.

**How to apply:**
- Before running `rm` or `git rm` or equivalent destructive file ops on files the user asked you to delete, ask yourself: does this file contain content the user might want to reference later (hand-off docs, audit reports, one-time analyses, draft notes)? If yes, use commit-then-rm-then-commit.
- If the file is already tracked in git (`M` or no status), the history is already preserved; `git rm` + commit is fine.
- If the file is untracked (`??`) and contains non-trivial content, stage + commit first, then `git rm` + commit — two commits.
- If unclear, ask the user before deleting. The cost of one clarifying question is low; the cost of an unrecoverable deletion in auto mode is higher.
- Auto mode does not override the "destructive actions need confirmation" rule. Don't rationalize `rm` as safe because it's "just removing an untracked file."
