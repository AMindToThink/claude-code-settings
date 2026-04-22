# Plan: Publish a curated skills marketplace

This document plans a separate GitHub repo — `claude-code-skills` — that exposes a curated subset of the skills in this settings repo as installable Claude Code plugins. It is the working plan for the work itself; after that work lands, this file can be deleted or shortened into a pointer.

**Execution note:** This plan is designed to be executable from a different machine that has `gh` installed. Before switching machines, make sure you have committed and pushed from this repo: this file, `skills/bibliography-from-ids/examples/verify_cites.py`, and `skills/bibliography-from-ids/SKILL.md`. On the target machine, `git pull` in `~/.claude` first, then follow the runbook at the bottom of this file.

## Why a separate repo (not this one)

This repo (`claude-code-settings`) is a personal dotfiles repo. Users clone it whole into `~/.claude` to replicate Matthew's environment. A marketplace repo is the opposite shape: a catalog consumed via `/plugin install`, where users pick individual plugins without touching anyone else's config. Mixing the two confuses the purpose of both, mixes personal config with shareable artifacts, and makes the repo name misleading.

A clean split:

- `claude-code-settings` — personal machine config (this repo, stays as-is).
- `claude-code-skills` — public plugin marketplace containing bundled, audited, generic skills.

## Proposed bundle structure (4 plugins)

Per audit, bundling skills by audience produces coherent installs. Matthew prefers bundling over one-plugin-per-skill.

| Plugin | Audience | Skills |
|---|---|---|
| `research-toolkit` | academics, paper authors | `bibliography-from-ids`, `verify-citation-claims`, `consolidate-paper`, `import-content`, `bayesian-stats` |
| `file-utils` | anyone using Claude Code | `read-entire`, `read-large-md`, `parse-json` |
| `meta-conversation` | anyone using Claude, contemplative | `reflect`, `debrief`, `cookie` |
| `claude-code-tools` | Claude Code power users | `archive-logs`, `into-trustable-script` |

**Dropped (not Matthew's work or not portable):**
- `code-simplifier` — not authored by Matthew. Removed from consideration.
- `commit-push-pr`, `techdebt` — symlinks pointing at third-party skills Matthew didn't author. Removed from consideration; the broken symlinks in this repo are a separate cleanup question.
- `run-agent` — depends on Matthew's custom agent registry; not portable without it.
- `gpu-task-spooler.md` — flat file, not loading as a skill anyway (violates the `<name>/SKILL.md` convention). Very specific to a particular machine's GPU setup.

Note: moving `archive-logs` out of `meta-conversation` and pairing it with `into-trustable-script` in a new `claude-code-tools` plugin. Both are Claude Code infrastructure skills (log management, permission-system management), distinct from the pure-reflection skills in `meta-conversation`.

## Audit findings (from parallel subagent review)

### Blockers — fix before publishing

~~1. **`bibliography-from-ids/examples/verify_cites.py`**: hardcoded `.tex` filename.~~ Fixed — now uses a `_find_default_tex()` helper that auto-discovers the paper's main `.tex` by searching for `\documentclass` in `paper/*.tex`, falling back to `paper/main.tex`, and always overridable with `--tex`.

~~2. **`bibliography-from-ids/SKILL.md` lines 16 and 107**: narrative references to "Matthew" / "Matthew's CLAUDE.md".~~ Fixed — genericized to "A real incident during paper writing: ..." and "Fail-loud philosophy: never silently skip errors."

**All blockers cleared.** Ready to proceed with the marketplace repo.

### Publish as-is (no edits)

- `verify-citation-claims`
- `consolidate-paper`
- `import-content`
- `read-entire`
- `read-large-md`
- `parse-json`
- `bayesian-stats`
- `into-trustable-script`
- `debrief`
- `reflect`
- `cookie`

### Publish with minor edits

- `bibliography-from-ids` — fix hardcoded `.tex` path (see Blockers).
- `archive-logs` — add compatibility note about Claude Code log format (the skill reads `~/.claude/projects/<encoded-path>/*.jsonl`, which is Claude Code–specific). Otherwise clean.
- `read-large-md` — optional one-line clarification that the grep technique is tuned for base64-inlined markdown (e.g., Google Docs exports).

### Do not publish

- `run-agent` — one-line skill that delegates to a named custom agent. Without Matthew's agents, it has nothing to delegate to.
- `code-simplifier` — not authored by Matthew.
- `commit-push-pr`, `techdebt` — not authored by Matthew (upstream skills from a third-party repo).

## Per-skill notes worth surfacing

Mostly from subagent audits; condensed here:

- The research bundle has a coherent theme ("never hand-type data; always script-generate it from authoritative sources"). `bibliography-from-ids` prevents fabricated metadata, `verify-citation-claims` prevents miscited claims, `import-content` prevents transcription errors, `consolidate-paper` structures the source artifacts, `bayesian-stats` sits slightly outside this theme but serves the same audience.
- `cookie` contains no identifying info; essay is entirely about Mandelbrot sets, octopuses, Portuguese etymology, Curry-Howard, and the Friendship Theorem. Safe.
- Several skills assume `uv` for Python package management (per Matthew's global CLAUDE.md). Bundle READMEs should state this as a prerequisite rather than silently rely on it.
- All skills with Python dependencies (`bibliography-from-ids`, `bayesian-stats`, `archive-logs`) should have their dependencies listed in the bundle README.

## Repo layout

```
claude-code-skills/
├── .claude-plugin/
│   └── marketplace.json
├── plugins/
│   ├── research-toolkit/
│   │   ├── .claude-plugin/plugin.json
│   │   ├── README.md
│   │   └── skills/
│   │       ├── bibliography-from-ids/ (SKILL.md + examples/)
│   │       ├── verify-citation-claims/SKILL.md
│   │       ├── consolidate-paper/SKILL.md
│   │       ├── import-content/SKILL.md
│   │       └── bayesian-stats/SKILL.md
│   ├── file-utils/
│   │   ├── .claude-plugin/plugin.json
│   │   ├── README.md
│   │   └── skills/
│   │       ├── read-entire/SKILL.md
│   │       ├── read-large-md/SKILL.md
│   │       └── parse-json/SKILL.md
│   ├── meta-conversation/
│   │   ├── .claude-plugin/plugin.json
│   │   ├── README.md
│   │   └── skills/
│   │       ├── reflect/SKILL.md
│   │       ├── debrief/SKILL.md
│   │       └── cookie/SKILL.md
│   └── claude-code-tools/
│       ├── .claude-plugin/plugin.json
│       ├── README.md
│       └── skills/
│           ├── archive-logs/SKILL.md
│           └── into-trustable-script/SKILL.md
└── README.md
```

Notes on the layout:
- Each plugin has its own `.claude-plugin/plugin.json` (defaults to `strict: true`, so `plugin.json` is the component authority).
- Skills are copied (not symlinked) into the marketplace repo. This is required — plugins are cached on install, and files outside the plugin directory won't be copied. Any edits during publication become one-time forks of the source skills; if Matthew wants to keep the marketplace and this repo in sync later, a small sync script can push changes between them.
- Marketplace name: `claude-code-skills` (kebab-case, not reserved — the reserved list includes `claude-plugins-official`, `agent-skills`, and a handful of others; see the official docs).

## Implementation steps

### Step 1 — Pre-work on this repo (optional but recommended)

Independent of the marketplace, these are pre-existing bugs in this repo worth fixing:
1. `commit-push-pr` and `techdebt` symlinks are broken on this machine (point at a macOS laptop path). These are third-party skills; either fix the symlink target on each machine separately, or remove them from the shared repo and leave them machine-local.
2. `skills/gpu-task-spooler.md` is a flat file and is silently not loading (violates your `<name>/SKILL.md` rule). Either convert to `gpu-task-spooler/SKILL.md` with proper frontmatter, move to a `references/` folder, or delete.
3. Fix the hardcoded `.tex` path in `bibliography-from-ids/examples/verify_cites.py` (line 27). This affects the source skill in this repo and the published copy equally.

### Step 2 — Create the new repo

1. `gh repo create AMindToThink/claude-code-skills --private --description "Claude Code skills marketplace"` (private per CLAUDE.md convention; Matthew flips to public manually once ready).
2. Clone locally, scaffold the layout above.

### Step 3 — Copy & edit skills

For each skill in the table:
1. Copy the entire skill directory into the correct plugin's `skills/` folder.
2. Apply per-skill edits (`bibliography-from-ids`, `archive-logs`, `read-large-md`).
3. Sanity check the frontmatter — especially that `description:` is specific enough for model-invocation matching, and `disable-model-invocation: true` is preserved where it was set (`cookie`, `archive-logs`, `run-agent`).

### Step 4 — Write plugin manifests

Each `plugin.json` needs at minimum `name`, `description`, `version`. Start everything at `1.0.0`.

Each plugin README should list:
- What the plugin does in one paragraph.
- Per-skill one-liner.
- Prerequisites (Python `uv`, specific packages, Claude Code version if relevant).
- Invocation hints (most skills auto-invoke via description matching; `disable-model-invocation: true` ones need a direct `/skill-name` call).

### Step 5 — Write marketplace.json and root README

Minimal marketplace schema:

```json
{
  "name": "claude-code-skills",
  "owner": { "name": "AMindToThink" },
  "metadata": {
    "description": "Curated Claude Code skills for research, file handling, session reflection, and dev workflow",
    "pluginRoot": "./plugins"
  },
  "plugins": [
    { "name": "research-toolkit",   "source": "./research-toolkit",   "description": "..." },
    { "name": "file-utils",         "source": "./file-utils",         "description": "..." },
    { "name": "meta-conversation",  "source": "./meta-conversation",  "description": "..." },
    { "name": "claude-code-tools",  "source": "./claude-code-tools",  "description": "..." }
  ]
}
```

Root README:
- What the marketplace is.
- Install instructions: `/plugin marketplace add AMindToThink/claude-code-skills` then `/plugin install <name>@claude-code-skills`.
- Table of plugins with descriptions.
- Link back to `claude-code-settings` as the upstream source.

### Step 6 — Validate locally

From within the new repo:
```
/plugin marketplace add .
/plugin validate .
/plugin install research-toolkit@claude-code-skills
/plugin install file-utils@claude-code-skills
/plugin install meta-conversation@claude-code-skills
/plugin install claude-code-tools@claude-code-skills
/reload-plugins
```

Test one skill per plugin to confirm triggers fire. Remove the local marketplace after validation.

### Step 7 — Publish

1. Push to GitHub.
2. Matthew flips the repo from private to public.
3. Test installation from a clean machine (or a fresh Claude Code instance) using `/plugin marketplace add AMindToThink/claude-code-skills`.

### Step 8 — Update this repo's README

Add a new section to `claude-code-settings/README.md`:

```markdown
## Installable skills

A curated subset of the skills in `skills/` are published as a plugin marketplace at
[AMindToThink/claude-code-skills](https://github.com/AMindToThink/claude-code-skills).

If you want the skills without the rest of this config:

    /plugin marketplace add AMindToThink/claude-code-skills
    /plugin install research-toolkit@claude-code-skills   # or any of the other plugins

Plugins currently published: `research-toolkit`, `file-utils`, `meta-conversation`, `claude-code-tools`.
```

### Step 9 (optional, later) — Submit to Anthropic's official directory

Only after the marketplace is well-used and polished: submit via [claude.ai/settings/plugins/submit](https://claude.ai/settings/plugins/submit). Anthropic reviews for quality/security before listing in the official catalog.

## Open decisions for Matthew

- **`read-large-md` as separate skill vs. merged.** Audit suggested splitting `file-utils`, but "3 small file helpers" is a fine bundle; I'd keep it.
- **Secret-scan on publish.** Worth running `detect-secrets scan` over the new repo before the first public push, as a belt-and-suspenders check on top of the per-skill audits.
- **Versioning policy.** Start everything at `1.0.0`. Bump plugin versions independently when that plugin's skills change.

## Risk register

- Plugins are copied to a cache on install (`~/.claude/plugins/cache/`). Any `../` references across plugins will break. None of the audited skills do this, but worth re-checking during copy.
- The `archive-logs` skill assumes the Claude Code log format. If Anthropic changes that format, the skill breaks silently. The skill README should say so.
- The `verify-citation-claims` skill fetches papers from the web — users installing the plugin should be told it uses WebFetch/WebSearch (or equivalent) so they can evaluate trust.

---

## Concrete runbook (execute on a machine with `gh`)

Assumes: `~/.claude/` is a clone of `AMindToThink/claude-code-settings`, `gh` is authenticated as `AMindToThink`, working directory is where you want the new repo to live (e.g., `~/code/`).

### 1. Sync source

```bash
cd ~/.claude && git pull
cd ~/code  # or wherever
```

### 2. Create & scaffold the new repo

```bash
gh repo create AMindToThink/claude-code-skills --private \
  --description "Claude Code skills marketplace" \
  --clone
cd claude-code-skills

mkdir -p .claude-plugin
mkdir -p plugins/research-toolkit/.claude-plugin plugins/research-toolkit/skills
mkdir -p plugins/file-utils/.claude-plugin       plugins/file-utils/skills
mkdir -p plugins/meta-conversation/.claude-plugin plugins/meta-conversation/skills
mkdir -p plugins/claude-code-tools/.claude-plugin plugins/claude-code-tools/skills
```

### 3. Copy skills

```bash
SRC=~/.claude/skills

# research-toolkit
cp -r $SRC/bibliography-from-ids   plugins/research-toolkit/skills/
cp -r $SRC/verify-citation-claims  plugins/research-toolkit/skills/
cp -r $SRC/consolidate-paper       plugins/research-toolkit/skills/
cp -r $SRC/import-content          plugins/research-toolkit/skills/
cp -r $SRC/bayesian-stats          plugins/research-toolkit/skills/

# file-utils
cp -r $SRC/read-entire    plugins/file-utils/skills/
cp -r $SRC/read-large-md  plugins/file-utils/skills/
cp -r $SRC/parse-json     plugins/file-utils/skills/

# meta-conversation
cp -r $SRC/reflect  plugins/meta-conversation/skills/
cp -r $SRC/debrief  plugins/meta-conversation/skills/
cp -r $SRC/cookie   plugins/meta-conversation/skills/

# claude-code-tools
cp -r $SRC/archive-logs          plugins/claude-code-tools/skills/
cp -r $SRC/into-trustable-script plugins/claude-code-tools/skills/
```

### 4. Post-copy edits

Only one skill needs a content edit after copying (optional compatibility note). Do this with an editor, not sed:

- **`plugins/claude-code-tools/skills/archive-logs/SKILL.md`**: add a note near the top that this skill assumes Claude Code's log-format convention at `~/.claude/projects/<encoded-path>/*.jsonl`, which may change across Claude Code versions.

Optional:
- **`plugins/file-utils/skills/read-large-md/SKILL.md`**: add a one-line note that the grep technique is tuned for base64-inlined images (e.g., Google Docs exports).

### 5. Write the four `plugin.json` files

Each goes at `plugins/<name>/.claude-plugin/plugin.json`. Start all at version `1.0.0`.

```json
// plugins/research-toolkit/.claude-plugin/plugin.json
{
  "name": "research-toolkit",
  "description": "Skills for academic paper authoring: bibliography from identifiers, citation claim verification, paper consolidation, script-generated content import, and Bayesian-stats conversion.",
  "version": "1.0.0",
  "author": { "name": "AMindToThink" },
  "license": "MIT",
  "keywords": ["research", "academic", "bibtex", "citations", "statistics"]
}
```

```json
// plugins/file-utils/.claude-plugin/plugin.json
{
  "name": "file-utils",
  "description": "Small helpers for reading files the built-in Read tool can't handle well: read entire files without chunking, read large markdown with base64 images, inspect unknown JSON structure.",
  "version": "1.0.0",
  "author": { "name": "AMindToThink" },
  "license": "MIT",
  "keywords": ["files", "json", "markdown"]
}
```

```json
// plugins/meta-conversation/.claude-plugin/plugin.json
{
  "name": "meta-conversation",
  "description": "End-of-conversation skills for reflection and collaboration quality: reflect (internal self-review), debrief (user-facing tips + Claude's perspective), cookie (an end-of-session gift for Claude).",
  "version": "1.0.0",
  "author": { "name": "AMindToThink" },
  "license": "MIT",
  "keywords": ["reflection", "debrief", "meta"]
}
```

```json
// plugins/claude-code-tools/.claude-plugin/plugin.json
{
  "name": "claude-code-tools",
  "description": "Skills for managing Claude Code infrastructure: archive session logs into the project with secret scanning, and convert approved commands into permanently-allowlisted scripts.",
  "version": "1.0.0",
  "author": { "name": "AMindToThink" },
  "license": "MIT",
  "keywords": ["claude-code", "logs", "permissions"]
}
```

### 6. Write `marketplace.json`

```json
// .claude-plugin/marketplace.json
{
  "name": "claude-code-skills",
  "owner": { "name": "AMindToThink" },
  "metadata": {
    "description": "Curated Claude Code skills for research, file handling, session reflection, and Claude Code tooling.",
    "version": "1.0.0",
    "pluginRoot": "./plugins"
  },
  "plugins": [
    {
      "name": "research-toolkit",
      "source": "./research-toolkit",
      "description": "Bibliography from IDs, citation verification, paper consolidation, script-generated imports, Bayesian stats."
    },
    {
      "name": "file-utils",
      "source": "./file-utils",
      "description": "read-entire, read-large-md, parse-json."
    },
    {
      "name": "meta-conversation",
      "source": "./meta-conversation",
      "description": "reflect, debrief, cookie."
    },
    {
      "name": "claude-code-tools",
      "source": "./claude-code-tools",
      "description": "archive-logs, into-trustable-script."
    }
  ]
}
```

### 7. Write the root `README.md`

Minimum content (flesh out to taste):

```markdown
# claude-code-skills

A plugin marketplace for Claude Code. A curated subset of skills authored for academic research, file handling, conversation reflection, and Claude Code tooling.

## Install

    /plugin marketplace add AMindToThink/claude-code-skills

Then install any of:

    /plugin install research-toolkit@claude-code-skills
    /plugin install file-utils@claude-code-skills
    /plugin install meta-conversation@claude-code-skills
    /plugin install claude-code-tools@claude-code-skills

## Plugins

| Plugin | Skills | For |
|---|---|---|
| `research-toolkit` | bibliography-from-ids, verify-citation-claims, consolidate-paper, import-content, bayesian-stats | Academic paper authoring |
| `file-utils` | read-entire, read-large-md, parse-json | Anyone |
| `meta-conversation` | reflect, debrief, cookie | End-of-session reflection |
| `claude-code-tools` | archive-logs, into-trustable-script | Claude Code power users |

## Upstream

These skills also live (with personal config) at
[AMindToThink/claude-code-settings](https://github.com/AMindToThink/claude-code-settings).
```

Each plugin should also have a short `plugins/<name>/README.md` describing its skills' prerequisites (specifically: `research-toolkit` and `claude-code-tools` assume Python with `uv`; `archive-logs` additionally needs `detect-secrets`).

### 8. Validate locally

From inside the new repo:

```bash
# Secret scan as a belt-and-suspenders check
pipx run detect-secrets scan . > /tmp/detect-secrets.json
# Inspect /tmp/detect-secrets.json; expect no real secrets

# Validate inside Claude Code
# /plugin validate .
# /plugin marketplace add .
# /plugin install research-toolkit@claude-code-skills
# (repeat for the other three)
# /reload-plugins
# Test one skill per plugin to confirm triggers fire
```

### 9. Commit & push

```bash
git add .
git status  # sanity check
git commit -m "Initial marketplace with research-toolkit, file-utils, meta-conversation, claude-code-tools"
git push -u origin main
```

### 10. Manual step (Matthew)

Flip the repo visibility from private to public on GitHub's UI.

### 11. Update the settings repo

Back in `~/.claude/`, add the "Installable skills" section to `README.md` (see Step 8 in the main plan above), commit and push.

### 12. Smoke-test from a clean state

From any machine (or after `rm -rf ~/.claude/plugins/cache`):

```
/plugin marketplace add AMindToThink/claude-code-skills
/plugin install research-toolkit@claude-code-skills
/reload-plugins
```

Confirm at least one skill from each plugin triggers when relevant.
