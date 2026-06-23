---
name: supervising-training-runs
description: Use when launching a multi-hour neural-network training, fine-tune, or other long GPU job autonomously from Claude Code and you need to catch failures (NaN, stuck-at-chance, dead process, throughput collapse, OOM) early instead of waking up to a wasted GPU window.
---

# Supervising training runs

## Overview

**Core idea: don't tail logs, parse structured telemetry; don't poll, get notified.**

A long training run is supervised well when (a) the run itself emits a single JSONL file with one fact per line, and (b) a separate watchdog process exits-with-anomaly the *moment* something looks wrong, re-invoking you. You check in via cheap `tail` reads, not by dumping full logs into context.

This is different from how a human watches W&B trend curves — your strengths are parsing structured data and reacting on notification, not staring at plots.

## When to use

- About to launch a multi-hour training / fine-tune / long GPU job that must run autonomously.
- The user is away or sleeping and the GPU window is fixed.
- Asked to "babysit" / "monitor" / "manage" a training run.

Do not use for runs < ~15 min — the preflight + watchdog ceremony isn't worth it.

## The pattern (in order — skip none)

1. **Bench the GPU.** Run ~15 train steps of the *real* architecture at the *real* seq-len/precision/batch on the target GPU to measure samples/sec. Compute `time = N_samples × N_epochs / sps`. Budget separately for preprocessing and eval. If projection blows your window, subsample BEFORE writing more code — not after.
2. **Audit the data before training, not after.** Scraped code corpora routinely contain ~5–10% rows that aren't valid in the claimed language (broken syntax, wrong language, truncated). Training on them is noise — the model learns surface signatures of broken syntax. Run a parallel `ast.parse` (or equivalent) check on every row and **drop or flag the unparseable rows in BOTH the raw and any normalized variant** so the kept set stays aligned. If a normalizer (`black`, AST round-trip, formatter) is part of the experiment, filter to rows where **both** the validity check **and** the normalizer succeed — otherwise the "normalized" variant secretly contains verbatim-fallback rows that aren't normalized at all, and the treatment is impure. Cost: ~1 min on 14 cores for ~150k rows.
3. **Smoke preflight (mandatory).** ~2k samples, 1 epoch, eval every ~20 steps. Confirm: loss falls below chance, val AUROC moves *up* from ~0.5 (label polarity correct, not inverted), `metrics.jsonl` written, checkpoint saves+reloads. Most "wasted 4 hours" come from skipping this.
4. **Launch as `run_in_background=true` Bash, on a single physical line.** Use `python -u`, set `PYTHONUNBUFFERED=1 HF_HUB_DISABLE_PROGRESS_BARS=1 TRANSFORMERS_VERBOSITY=error TOKENIZERS_PARALLELISM=false`. The background completion notification is your "it finished" signal.
5. **Telemetry contract.** The training script appends to `metrics.jsonl` with `flush()`:
   - per-step (every ~10): `{"step","t","loss","lr","grad_norm","sps"}`
   - per-eval (every ~250): `{"step","eval_auroc","eval_acc"}`
   - Built-in fail-loud: assert label polarity at startup; **raise on non-finite loss** (don't write a NaN and continue).
   - Also enable `report_to=["tensorboard"]` for the *human's* dashboard (zero auth; SSH-tunnel `tensorboard --logdir <out> --port 6006`). W&B if the user has an account/key. A small `matplotlib` PNG render of `metrics.jsonl` makes a phone-friendly snapshot you can `SendUserFile`.
6. **Launch a watchdog** as a separate background job. Polls metrics file every ~30s. Exits **7 (anomaly)** on any of: NaN/inf loss, metrics file mtime stale > MAX_STALL (~360s = dead/hung), val AUROC < 0.70 after the warmup-ish step threshold (stuck at chance on an easy task), hard timeout. Exits **0** when the completion sentinel (e.g. `final_val_metrics.json`) appears. Either exit re-invokes you — early on failure, late on success.
6. **Don't poll-block.** Background-job completion + watchdog cover both outcomes. Each check-in: `tail -k metrics.jsonl` + one `nvidia-smi` + one `pgrep`. Cheap context.

## Healthy trajectory (alarm thresholds)

For a typical fine-tune binary classifier:

| Signal | Healthy | Alarm |
|---|---|---|
| Loss (binary CE) | < 0.5 after ~200 steps (chance ≈ 0.69) | flat at ~0.69 after ~400 steps |
| Val AUROC | > 0.85 by end of epoch 1, > 0.9 within first few hundred steps on an "easy" task | pinned ~0.5 → label/data bug; trending toward 0 → inverted labels (just flip) |
| Pre-clip grad-norm | 0.1 – 10 | sustained > 50 (exploding) or < 1e-3 (collapse) |
| Throughput | stable | sustained > 25% drop vs first-200-step median |
| NaN / inf loss | never | abort on the FIRST step, don't wait |

## Operational gotchas (caught the hard way)

| Symptom | Cause | Fix |
|---|---|---|
| Background bash runs, GPU stays at 0% | newlines in a multi-line `run_in_background` command got collapsed into spaces, so `cd … mkdir … python` ran as one broken command | one physical line, `&&` between steps |
| Balanced subset silently drops the `label` column | pandas 2.x `groupby().apply()` drops the grouping column | sample per group explicitly: `pd.concat([g.sample(per, random_state=SEED) for _, g in df.groupby("label")])` |
| `TypeError: ... overwrite_output_dir` | removed in transformers v5 | drop it (the dir is fresh anyway); also `evaluation_strategy` → `eval_strategy` |
| 18k-line log dominated by progress bars, real error buried | HF default progress bars | env: `HF_HUB_DISABLE_PROGRESS_BARS=1 TRANSFORMERS_VERBOSITY=error`; on read, `grep -avE "it/s\|Materializing\|Loading weights"` |
| In-process `black` on 100k+ files times out | serial single-process | `multiprocessing.Pool(N)` with a **module-level** worker (must be picklable); 14 procs cuts ~15 min to ~1 min |
| GPU shows 0% util right after launch | still in `.map()` tokenization or `from_pretrained` weight load | wait 1–2 min before alarming; the watchdog's MAX_STALL handles real stalls |
| Credentials in `~/.git-credentials` look fine but `git push` 401s | stored token has been revoked/expired | tell the user; don't try other credential paths — the harness will block credential scanning, correctly |

## Common mistakes

- **Skipping the smoke run** because "it's a standard recipe." It's the cheapest insurance you'll buy: ~3 min vs ~3 hours wasted.
- **Hand-tailing the full log** on each check-in. Wastes context. Tail the *JSONL*, last few lines only.
- **Polling for completion.** Background jobs *notify*. Use the notification; reserve `ScheduleWakeup` for genuinely external state (external API, queue) the harness can't track.
- **Treating "no telemetry yet" as a stall** in the first 2 minutes. `.map()` on large datasets takes time before GPU activity.
- **Writing a NaN, continuing, hoping it recovers.** Raise. Fail loud.
- **Hardcoding the recipe's published `N_samples` × `epochs`** without checking it fits the GPU window. Bench first, subsample if needed, then write code.

## Checkpointing

`load_best_model_at_end=True`, `metric_for_best_model="auroc"`, `save_total_limit=2`. A late crash costs at most one eval interval.

## Reference — a minimal Trainer callback that implements this

```python
import json, time, numpy as np
from pathlib import Path
from transformers import TrainerCallback

class JsonlMonitor(TrainerCallback):
    """One JSONL line per train log + per eval. Aborts loudly on non-finite loss."""
    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text("")
        self._t = self._lt = time.time(); self._last_step = 0
    def _w(self, d):
        with self.path.open("a") as f:
            f.write(json.dumps(d) + "\n"); f.flush()
    def on_log(self, args, state, control, logs=None, **kw):
        logs = logs or {}
        rec = {"step": state.global_step, "t": round(time.time() - self._t, 1)}
        if "loss" in logs:
            if not np.isfinite(logs["loss"]):
                self._w({**rec, "FATAL": "non-finite loss"})
                raise RuntimeError(f"non-finite loss at step {state.global_step}")
            now = time.time()
            sps = ((state.global_step - self._last_step) * args.per_device_train_batch_size
                   / max(now - self._lt, 1e-6))
            self._lt = now; self._last_step = state.global_step
            rec.update(loss=round(logs["loss"], 4), lr=logs.get("learning_rate"),
                       grad_norm=round(logs.get("grad_norm", float("nan")), 3),
                       sps=round(sps, 1))
        if "eval_auroc" in logs:
            rec.update(eval_auroc=round(logs["eval_auroc"], 4),
                       eval_acc=round(logs.get("eval_accuracy", float("nan")), 4))
        self._w(rec)
```

## Reference — a minimal watchdog

```python
# Exit 7 (ANOMALY) on stall/NaN/stuck; exit 0 on completion sentinel.
import json, time, sys
from pathlib import Path
DIR = Path(sys.argv[1])
metrics, done = DIR/"metrics.jsonl", DIR/"final_val_metrics.json"
POLL, MAX_STALL, MIN_AUROC, MIN_AUROC_STEP, HARD = 30, 360, 0.70, 500, 3*3600
t0 = time.time()
while True:
    time.sleep(POLL)
    if done.exists(): print("OK done"); sys.exit(0)
    if time.time() - t0 > HARD: print("ANOMALY hard timeout"); sys.exit(7)
    if not metrics.exists(): continue
    if time.time() - metrics.stat().st_mtime > MAX_STALL:
        print("ANOMALY stall"); sys.exit(7)
    rows = [json.loads(l) for l in metrics.read_text().splitlines()[-50:] if l.strip()]
    if rows and "loss" in rows[-1]:
        l = rows[-1]["loss"]
        if not isinstance(l, (int, float)) or l != l: print("ANOMALY NaN"); sys.exit(7)
    for e in [r for r in rows if "eval_auroc" in r]:
        if e.get("step", 0) >= MIN_AUROC_STEP and e["eval_auroc"] < MIN_AUROC:
            print(f"ANOMALY stuck val_auroc={e['eval_auroc']}"); sys.exit(7)
```

## Red flags — STOP and reassess

- About to launch a multi-hour run without having benched samples/sec on the target GPU.
- About to launch without a smoke run.
- Smoke val AUROC didn't move above ~0.5 → don't launch; you'd be burning hours on a broken pipeline.
- About to use `evaluation_strategy=` or `overwrite_output_dir=` on transformers v5 — they'll error out.
- About to tail a multi-MB stdout log to "check progress." Tail `metrics.jsonl` instead.
- About to read credentials the user hasn't pointed you to — the harness will (correctly) block this.
