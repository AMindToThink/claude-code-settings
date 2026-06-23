---
name: critique
description: Spin up one or more fresh-context subagents to critically evaluate a proposed theory, hypothesis, interpretation, or experimental design before committing to it. Use when the user says "have an agent critique this" / "get a second opinion on" / "is this design sound" / invokes /critique, or proactively before running any experiment or committing to a non-trivial theoretical claim.
user_invocable: true
---

# Critique

Dispatch fresh-context subagents to attack an idea before you act on it. Subagents without conversation history catch confirmation-biased designs that someone close to the problem will rationalize past.

## When to use

**User-invoked:**
- `/critique <thing to attack>` — user wants this run on their input.
- "have an agent critique this", "get a second opinion on", "is this design sound", "what's wrong with my plan."

**Proactively (per `feedback_subagent_critique_default` memory):**
- Before running an experiment.
- Before committing to an interpretation of empirical data.
- Before writing up a theoretical claim.
- When you (Claude) propose anything in the categories: theory, hypothesis, interpretation, experimental design.

If the user has not granted standing authorization, ask first. If they have (check memory), just do it.

## What makes a subagent critique valuable vs. useless

The critique's quality is bounded by the prompt's quality. Bad prompts get bland answers; the agent has no context and will fill the void with generic advice. Good prompts produce specific, technical attacks. Follow this pattern:

### 1. Background paragraph

The agent has zero conversation history. Tell it:
- What the project is (one paragraph).
- Where the key files are (paths).
- What's already known / what experiments have run.
- Any existing memos or write-ups it should read (with full paths).

### 2. The thing to critique

State it concretely. Quote the load-bearing claim or paste the design specification verbatim. Cite file:line where relevant. Call out which assumptions you think are doing the most work.

### 3. Specific attack questions

Don't ask "is this good?" Ask things like:
- Does this experiment actually distinguish hypothesis A from hypothesis B? What does outcome X prove vs. outcome Y?
- Is there a simpler explanation that fits the same data?
- Are two distinct concepts being conflated? (If you suspect they are, name them.)
- What's the strongest argument *against* this interpretation?
- What confounders does the design fail to control?
- Does the noise / power analysis hold under more pessimistic assumptions?

The two question framings that have historically been most load-bearing:
1. **"Does this experiment actually measure what we want it to measure?"**
2. **"Is there a simpler explanation or approach?"**

Include either or both if applicable.

### 4. Guard against scope creep

Add a "what not to do" instruction so the agent doesn't sprawl. Typical:

> "Don't recommend running a completely different experiment unless you can argue the current one is fundamentally broken. The question is whether this design delivers what's claimed, not what other experiments could exist."

### 5. Output constraint

Cap response length. Force a one-line verdict at the top.

> "Under 500 words. Lead with: 'run as designed' / 'run with these specific changes' / 'design is broken, here's why'. Be specific (file:line citations where relevant). Don't be diplomatic."

## Implementation

Use the `Agent` tool with `subagent_type: general-purpose`. Set `run_in_background: true` when you'd otherwise sit waiting — you can read code or do other prep while the agent works, and the system will notify you on completion.

**For multiple independent angles**, dispatch multiple agents in parallel in a single tool-call block. Common patterns:
- One agent attacks "does this measure X?"; another attacks "is there a simpler explanation?".
- One agent reads the design as a methods reviewer; another reads it as a statistician focused on power and confounders.

## After receiving the critique

Treat it as a peer review, not an oracle. Some points will be wrong, others load-bearing. The pattern that has worked:

1. **Read the full critique** end-to-end before responding.
2. **For each point, decide**: is this load-bearing? Can I refute it cleanly? Or is it pointing at a real issue I missed?
3. **If the critique changes the design materially**, do NOT proceed to running anything. Surface the changes to the user with your assessment and pause for direction. Critiques that change "run experiment X" to "run experiment Y" or "measure Z first" are decisions the user owns.
4. **If the critique is wrong on a point that matters**, write down *why* in your response to the user and proceed.
5. **If you and the critic agree the design is fine with minor tweaks**, apply them and proceed (still surface the changes in your next message so the user sees what was adjusted).

## Anti-patterns

- **Empty briefs.** "Critique this experiment design: ..." → bland feedback. Always include background and specific attack questions.
- **Asking the agent to decide.** The critique informs *your* decision; don't outsource the call to the subagent.
- **Skipping the critique because "I'm pretty sure."** That's exactly the bias the critique exists to catch.
- **Running multiple critique passes on minor tweaks.** Once a design is endorsed with changes, apply and move on — don't keep asking for blessing.
