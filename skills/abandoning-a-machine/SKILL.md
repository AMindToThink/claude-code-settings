---
name: abandoning-a-machine
description: Use when someone is about to lose access to a machine (shared server, lab box, cloud/VM instance, expiring rental) and needs to preserve all their work before it's gone. Systematically finds everything that exists ONLY on that machine — unpushed commits, stashes, untracked/uncommitted files, dirty submodules, non-git dirs, loose files, and large gitignored artifacts — and backs it up to GitHub / HuggingFace / an off-machine archive, non-destructively. Triggers on "losing access to this machine", "back up everything before I lose the server", "migrating off this box", "decommission", "my instance expires".
---

# Abandoning a machine

Goal: nothing the user cares about dies with the machine. Work the problem as **"what exists only here?"** — anything already on a remote (GitHub/HF) can be finished from any other machine later. Prioritize the few things that are genuinely local-only.

## 0. Preconditions (shared-machine safety FIRST)
- **Verify git identity before EVERY commit.** On shared OS accounts, `user.name`/`user.email` may default to a *different person*. Check `git config user.name && git config user.email` inside each repo; abort if either is wrong. Committing with a colleague's email is a real, recurring failure.
- **Never read or touch other users' home folders.** Their backup is their problem.
- **Find the working credential.** The token in a stored `.git-credentials` may be **stale**; the one git actually uses can come from elsewhere in the helper chain. Resolve it with `git credential fill` and test it against the API (`GET /user` → 200) before relying on it. No `gh` CLI? Use the REST API via `curl`.

## 1. Audit — enumerate everything not on a remote
For **every** git repo (find them: `find . -name .git -prune -o -name .git -print`, plus submodules):
- **Unpushed commits on ALL branches**, not just the current one: `git for-each-ref --format='%(refname:short)' refs/heads` then `git rev-list --count <b> --not --remotes`. Non-current branches hide work.
- **Stashes** (`git stash list`) — these do **not** get pushed and are lost silently.
- **Uncommitted + untracked** files (`git status --porcelain`), including inside **submodules** (each has its own remote; a superproject backup only records the pointer).
- **Worktrees** (`git worktree list`) — separate branches/commits.
Then the **non-git surface**: the home root usually isn't a repo, so loose scripts/notebooks/configs and whole non-git directories are unversioned. And **large gitignored artifacts** (weights, datasets, wandb) that no push will ever capture.

## 2. Back up to git — non-destructively
- Push recovered work to **uniquely-named `backup/migration-*` branches**. Never `--force`; never push onto a shared branch that would diverge (it'll reject → land it on a `backup/*` branch instead).
- **Stashes → branches:** `git branch backup/migration-stash-N stash@{N}` then push. (Count them all — don't `head` the list.)
- **WIP without disturbing the working tree:** build a commit via a temp index so you never touch HEAD/index/worktree:
  `GIT_INDEX_FILE=$tmp git read-tree HEAD; GIT_INDEX_FILE=$tmp git add -A; tree=$(… write-tree); commit=$(git commit-tree $tree -p HEAD -m "migration backup"); git push origin $commit:refs/heads/backup/migration-wip`
  Stage **only** intended paths — never blind `git add -A` into a real commit when unrelated WIP is present.
- **Broken/SSH/embedded-token submodule remotes:** push via `GIT_ASKPASS` with the working token to the clean HTTPS URL, bypassing the repo's broken credential config.
- **Loose files + non-git dirs:** collect into ONE new **private** repo (init *outside* the home root so you don't turn `$HOME` into a repo; set identity explicitly since `includeIf` won't apply). **Exclude secrets** (`.git-credentials`, `.gitconfig`, keys) and caches.
- **Someone else's repo** (you have local commits but no push rights): back up to a branch on your *own* new private repo; don't push to their default branch without asking.

## 3. Big data — GitHub can't hold it
- **> 100 MB files / multi-GB trees don't belong on GitHub.** Split by fate:
  - **Fine-tuned model weights** → HuggingFace (public repo is free; user's call on visibility). Note bare `state_dict`s need the base-model config/tokenizer documented.
  - **Other irreplaceable outputs** (your own compute: results, computed stats) → `tar` and **move off-machine** (scp / external / cloud). This is the user's action; give exact commands.
  - **Reproducible** (HF caches, public datasets, `.venv`, compiled artifacts) → skip; document how to regenerate.
- Produce a manifest of what was left behind and why.

## 4. Reproducibility docs (so the backup is usable, not just present)
Each repo should document, **verified against the actual code** (never fabricate dataset IDs / commands — grep `load_dataset`/`from_pretrained`/config): environment recreation (from real lockfiles), data acquisition, run commands, external deps (models, wandb, env vars, sibling forks), hardware. Leave explicit `TODO (owner):` where truly undeterminable.

## 5. Verify — don't trust exit codes
Confirm each backup landed **on the remote by SHA** (`git ls-remote` / API), not by a local "exit 0". A filtered log once hid a failed push. Re-list new repos' contents.

## 6. Hazards seen in the wild
- **Disk full mid-backup?** Clear caches first (`~/.cache/huggingface`, pip/uv) — usually frees plenty without deleting any real work.
- **Forking the conversation to parallelize** can spawn an autonomous agent that *also* executes the same instruction and collides with subagents you launch (duplicate files, push races). If you fan out with subagents, make sure only one executor owns each repo, and reconcile duplicates afterward (keep the verified doc, drop the fabricated one).
- **Fresh PAT is for the NEXT machine**, not this one — the current machine's credentials won't travel and stored tokens may already be expired.
