---
name: handle-machine-shared-memory
description: Use when a shared multi-user Linux box keeps freezing or going unresponsive from out-of-memory (OOM) events, when one user's process is eating all the RAM, or when someone needs to cap memory so the machine stays usable without starving legitimate work. Covers cgroup-v2 / systemd memory guard rails (MemoryMax / MemoryMin), giving Docker its own capped slice, a preflight that refuses over-budget eval runs, and the reasoning that makes the caps safe. Triggers on "the server keeps freezing", "OOM killed my process / dbus / the session", "someone is hogging all the memory", "put a memory limit on docker/users so the machine never dies", "cgroup memory caps", "MemoryMax", "the box becomes unusable under load". Assumes you have root but NOT hardware control (can't add RAM).
---

# Handling shared-machine memory (stop the OOM freezes)

**Goal:** the machine never becomes globally unusable, *and* each user (and Docker)
can still use a lot of memory. The failure you're fixing is not "a process died" —
it's "a process died and took `dbus`/`sshd` with it, freezing the whole box." One
process OOMing is fine and even desirable (fail fast); the session going down is not.

The whole approach is one idea: **make a machine-wide OOM structurally impossible
(the rail), and make the split between users and Docker cheap to change (the dial)**
— so you never have to forecast the "right" numbers.

**Boundary rule:** these commands change a shared machine's global state and need
root. Produce them, explain exactly how to run them, and let the human run them —
do NOT execute `systemctl` / `set-property` / `docker restart` / swap changes
yourself unless the user has explicitly told you to. If they say "I'll run those,"
believe them and just hand over precise, copy-pasteable commands.

---

## 0. Diagnose first (read-only) — and don't trust an empty grep

Before changing anything, prove what actually happened.

- **Find the OOM victims and the collateral.** `journalctl -k` / `dmesg` for
  `Out of memory`, `oom-kill`, `Killed process`. Identify the hog (PID, UID, RSS,
  runtime) *and* whether the kernel killed anything load-bearing (`dbus-daemon`,
  `sshd`, `systemd`) — that collateral is *why the machine froze*, not the hog itself.
- **Empty grep output on a shared box often means permission-denied, not absence.**
  If you can't read `/var/log` or another user's `journalctl`, you'll get nothing
  back and wrongly conclude "no OOMs." Confirm you can actually read the source
  (try with `sudo`, check exit codes) before reporting "none found." This is a
  recurring self-inflicted false conclusion.
- **`memory.current` includes reclaimable page cache.** A slice showing 39 GiB
  "used" may be mostly cache from reading large files; a cap it hits triggers
  *reclaim*, not an OOM. Don't size caps off a cache-inflated number, and don't
  size them off an *idle-moment snapshot* taken after the hog was already killed —
  that measures a coffee break, not the workload.

Record physical RAM, cgroup version, whether `systemd-oomd` is installed, and the
current caps:

```bash
grep MemTotal /proc/meminfo
systemctl show user.slice   -p MemoryMax -p MemoryMin -p MemoryCurrent
systemctl show system.slice -p MemoryMax -p MemoryMin -p MemoryCurrent
cat /sys/fs/cgroup/user.slice/memory.max 2>/dev/null
```

---

## 1. The rail — the one invariant that never moves

**Caps are permissions, not reservations.** `MemoryMax=80G` means "you may never
exceed 80", NOT "80 is set aside for you." So two caps that each look safe can
still over-commit the machine:

```
user.slice = 80G  +  docker.slice = 20G  =  100G on a 94 GiB box
```

Both slices sit "within limits" right until physical RAM is exhausted → global OOM
→ dbus dies → freeze returns.

**The rail: `user.slice + docker.slice ≤ MemTotal − RESERVE`.** That sum, under
physical RAM, is the only thing that makes a machine-wide OOM impossible. Everything
else is a dial; this is the rail.

**Derive RESERVE** (everything charged to *neither* user nor docker slice):
- `system.slice` — sshd, dbus, dockerd, containerd, journald, plus `containerd-shim`
  processes (~15 MB each × containers). Budget a few GiB.
- Kernel memory charged to no cgroup — slab, page tables, network buffers: ~2–3 GiB.
- A responsiveness cushion so `ssh`/`htop`/`ls` always work: ~1–2 GiB.

A reserve of ~8 GiB is a reasonable starting default on a ~90 GiB box. **Compute the
rail as `floor(MemTotal_GiB − RESERVE_GIB)`; never hardcode the result** — flooring
rounds toward a larger reserve (conservative), and on a new machine the number
follows automatically.

---

## 2. `MemoryMax` vs `MemoryMin` — use both, for different jobs

- **`MemoryMax` = ceiling** ("you may never exceed this"). A *permission*. Summing
  these is the rail; it makes a global OOM impossible.
- **`MemoryMin` = floor** ("this much is yours unconditionally; never reclaimed").
  A *grant*. This keeps the machine *responsive* — sshd/dbus can't be reclaimed out
  from under you.

**`MemoryMin` alone is NOT enough, and this is the subtle part:** it protects against
*reclaim*, not against the *OOM killer*. Per the kernel cgroup-v2 docs, if no
unprotected reclaimable memory remains, the OOM killer still fires — and victim
selection never consults `memory.min`. So you need both: summing caps make a global
OOM impossible; `MemoryMin` grants keep the survivors resident. Neither substitutes
for the other.

**Trap: "uncapped" is not "protected."** A slice with `MemoryMax=infinity`,
`MemoryMin=0` (the usual default for `system.slice`) can grow *and* be fully
reclaimed under pressure — it looks protective and reserves nothing. Give the
must-survive slice a real `MemoryMin`.

---

## 3. Docker needs its own slice (containers escape `user.slice`)

`docker run` is **not a fork — it's an RPC to `dockerd`.** The CLI asks the daemon
(root, in `system.slice`) to create the container; a process inherits its cgroup from
its *parent*, and the parent is the daemon, not your shell. Under the default
`cgroupfs` driver the container lands at top-level `/sys/fs/cgroup/docker/<id>`,
**outside `user.slice` entirely**. So a per-user cap does nothing to containers, and
Docker needs its own top-level `docker.slice`, capped directly.

**One-time plumbing** (the only disruptive/irreversible step — do it while zero
containers exist, when it's free):

```bash
sudo mkdir -p /etc/docker
sudo tee /etc/docker/daemon.json >/dev/null <<'EOF'
{
  "exec-opts": ["native.cgroupdriver=systemd"],
  "cgroup-parent": "docker.slice"
}
EOF
sudo systemctl restart docker
```

If `daemon.json` already exists with other settings, MERGE these two keys in — don't
overwrite (a second write silently drops the old content). Verify it's valid,
non-empty JSON before restarting (`python3 -c "import json; json.load(open('/etc/docker/daemon.json'))"`).

**Trap: capping `docker.service` caps nothing.** `set-property docker.service
MemoryMax=…` limits only the ~36 MB *daemon* — containers aren't its cgroup children.
It looks like a working Docker limit and enforces nothing. Cap `docker.slice`.

---

## 4. Apply the caps

```bash
# Rail: docker + user must sum under MemTotal - RESERVE. Example on a 94 GiB box
# (rail = 86): pick a starting split, e.g. docker 36 / user 50.
sudo systemctl set-property docker.slice     MemoryMax=36G
sudo systemctl set-property user.slice       MemoryMax=50G   # rail - docker
sudo systemctl set-property user-1000.slice  MemoryMax=40G   # per-user, under the parent
sudo systemctl set-property user-1001.slice  MemoryMax=40G

# Reservations — the "simple commands always work" part (often ZERO by default).
sudo systemctl set-property system.slice     MemoryMin=4G
sudo systemctl set-property user-0.slice     MemoryMin=1G    # root's shell lives in user.slice
```

- Per-user caps that sum ABOVE the parent (40+40 > 50) are intentional: either user
  can burst to most of the user budget, neither can take it all. They're inert until
  the parent `user.slice` cap is set (a child can't exceed its parent).
- `set-property` persists to `/etc/systemd/system.control/<unit>.d/` and takes effect
  **live, no restart**. Undo one with `sudo systemctl revert <unit>`.
- The starting split is a *starting position, not a prediction*. Don't justify it with
  a measured "real need" — today's heaviness may be a bug, and tomorrow's Docker need
  is larger. Make it cheap to change instead (next section).

---

## 5. The dial + a preflight (so you never forecast)

Turning the dial is `user.slice = rail − docker.slice`, two `set-property` calls. Do
NOT build a "rebalance script" that prints commands for a human to run — **a script
that emits commands enforces nothing** (same shape as the `docker.service` trap:
looks like a guard rail, isn't). Put the reasoning in a short doc, and put
enforcement where it can actually enforce:

1. **The kernel** — `MemoryMax` is the rail.
2. **A launch-path preflight** — refuse over-budget runs before they spend anything.

**Make container cost arithmetic, not a guess.** Container memory is bounded: each
sample's compose file declares `mem_limit`s (e.g. BashArena ≈ 2.25 GiB/sample across
~5 containers). So `docker.slice ÷ per_sample = concurrent samples`, and any desired
concurrency names its own budget. A preflight that (a) sums `mem_limit`s from the
compose file, (b) reads `/sys/fs/cgroup/docker.slice/memory.max`, (c) refuses if
`max_samples × per_sample > budget` — and whose refusal **prints the exact
`set-property` commands to widen the budget** (derived from `MemTotal − RESERVE`, not
a magic constant) — *is* the dial. No separate calculator; it already computed the
number.

**The preflight must:**
- **Never auto-rebalance.** Silently shrinking the other user's budget so your run
  fits is exactly the quiet action to avoid. Refuse, print, let a human decide.
- **Fail loudly on unreadable inputs** (missing/uncapped `docker.slice`, unreadable
  compose) rather than assuming a default and pressing on — a check computed from a
  guessed number is worse than no check, because it looks like it passed.

**Why over-budget is worse than a freeze once capped:** with `docker.slice` capped,
an over-committed run no longer freezes the box — the kernel just OOM-kills containers
mid-eval, producing trajectories where *infrastructure* failures wear *agent-failure*
clothing. Bad data type-compatible with good data. The preflight exists to stop that
silent corruption, not just the freeze.

---

## 6. Deliberately skipped / deferred

- **Swap: skip it** (for a box where big memory is usually a bug). At `MemoryMax` the
  kernel reclaims first and OOM-kills only if reclaim fails; a big Python heap is
  nearly all *anonymous* memory, so with no swap there's nothing to reclaim and the
  kill is immediate and clean. Adding swap turns that clean kill into disk thrash that
  saturates the shared disk — reintroducing "unusable" via the I/O path.
- **`MemoryHigh` (soft throttle): defer** until you have a *measured* profile of
  legitimate large runs, and add it *with* swap (it can't throttle anon-heavy Python
  with nowhere to reclaim to). Size it just below `MemoryMax`, as a brake — set it to
  "worst bug so far" and a legitimate large run sits permanently throttled into
  uselessness.
- **`systemd-oomd`: optional** — PSI-based proactive killing with better victim
  selection than the kernel's, if installed.

---

## 7. Verify (don't infer from config)

1. **Containers really land in the slice.** After the restart + a fresh login, start a
   container and confirm it's under `/sys/fs/cgroup/docker.slice/…`, NOT top-level
   `/sys/fs/cgroup/docker/`. If top-level, `cgroup-parent` didn't take and the cap
   enforces nothing.
2. **The rail holds.** As one user: `python3 -c "x=bytearray(60*2**30)"`. Confirm it's
   killed at the per-user cap, the **other user is unaffected**, **dbus survives**,
   `ssh` still connects, and the machine never freezes.
3. **The dial works.** Run the preflight over-budget → it refuses and prints the
   commands; apply them; re-run → passes. That loop is what replaces forecasting.

**Docker-socket gotcha before any of this is testable:** `docker ps` can fail with
`permission denied … /var/run/docker.sock` even when `getent group docker` lists your
user — a login session predating the group-add carries stale supplementary groups.
`newgrp docker` or a fresh login clears it. (Corollary: the `docker` group is
root-equivalent — `-v /:/host` — so per-container `--memory` is unenforceable by
anyone but the requester, but an aggregate *slice* cap is enforced by the kernel
regardless.)

---

## 8. Communicating the commands (recurring pain points)

When you hand root commands to a human, be explicit enough that they never have to
guess — this genuinely tripped the user up more than once:

- **State who and where.** "Run as your normal user (`sudo` elevates per-command);
  directory doesn't matter for these." Don't make them wonder if they must `su` to root.
- **`sudo` = root privileges, NOT root's folders.** A plain `sudo <cmd>` keeps your
  current working directory; only `sudo -i` moves you to `/root`. Since these commands
  use absolute paths (`/etc/docker/…`) or no path (`systemctl`), cwd is irrelevant —
  say so, so they don't second-guess.
- **Relative-path commands are the exception.** The preflight uses `scripts/…`, so it
  *must* run from the repo root, as the normal user, no sudo. Call this out separately.
- **"Create a file with content" ≠ `touch`.** `touch` makes an empty file; an empty
  `daemon.json` is invalid JSON and breaks dockerd. Give the full `sudo tee <<'EOF'`
  heredoc, and a `cat` + JSON-validate step before the restart.
- **Flag when a command isn't available yet.** If the preflight lives on an unmerged
  branch, it won't be on disk on `main` — say that, so they don't run it into a
  "file not found."
