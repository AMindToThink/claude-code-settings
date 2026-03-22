# GPU Task Spooler

GPU Task Spooler (`ts`) is installed at `~/bin/ts` for scheduling GPU jobs across multiple Claude Code instances. Ensure `~/bin` is in PATH before using.

## Setup

```bash
export PATH="$HOME/bin:$PATH"
ts -S 2  # Allow max 2 concurrent GPU jobs (one per GPU)
```

## Submitting Jobs

```bash
# 1-GPU job (e.g., GPT-2)
ts -G 1 uv run python scripts/my_script.py --device cuda:0

# 2-GPU job (e.g., Qwen 2.5-32B with device_map=auto)
ts -G 2 uv run python scripts/my_script.py --device auto --torch-dtype float16

# CPU-only job (no GPU reservation)
ts uv run python scripts/my_script.py --device cpu
```

## Monitoring

```bash
ts -l            # List all jobs (queued, running, finished)
ts -c <id>       # View stdout/stderr of job <id>
ts -t <id>       # Tail (follow) output of running job
ts -w <id>       # Block until job <id> finishes
ts -i <id>       # Show job info (command, slots, etc.)
```

## Queue Management

```bash
ts -S <n>        # Set max concurrent jobs to n
ts -K            # Kill the task spooler server (resets queue)
ts -k <id>       # Kill a specific job
ts -r <id>       # Remove a finished job from the list
ts -u <id>       # Make a job urgent (move to front of queue)
```

## Environment Notes

- The machine has 2x Quadro RTX 8000 (48GB each)
- `ts -S 2` allows two 1-GPU jobs or one 2-GPU job at a time
- `ts` automatically sets `CUDA_VISIBLE_DEVICES` for each job
- Jobs from any Claude Code instance share the same queue (coordinated via `/tmp`)
- Working directory is inherited from where `ts` is called

## Common Patterns

```bash
# Submit experiment, then tail it
JOB_ID=$(ts -G 1 uv run python scripts/run_experiment.py --device cuda:0)
ts -t $JOB_ID

# Chain: run experiment then plot results
ts -G 1 uv run python scripts/run_experiment.py --output results/out.json
ts uv run python scripts/plot_results.py --input results/out.json

# Check if all jobs are done
ts -l | grep -c running
```
