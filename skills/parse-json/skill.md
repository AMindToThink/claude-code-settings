---
name: parse-json
description: Inspect and extract data from unknown JSON files without fumbling
user_invocable: true
---

## Parse JSON Skill

When the user asks you to parse, inspect, or extract data from a JSON file (or when you encounter an unknown JSON file during work), follow this two-phase approach. **Never guess the structure — always inspect first.**

### Phase 1: Structure Discovery (single call)

Run a single Python snippet that reveals the full structure:

```python
python3 -c "
import json, sys

with open('FILE_PATH') as f:
    data = json.load(f)

def describe(obj, path='root', depth=0, max_depth=3):
    indent = '  ' * depth
    if isinstance(obj, dict):
        print(f'{indent}{path}: dict with {len(obj)} keys: {list(obj.keys())[:15]}')
        if depth < max_depth:
            for k in list(obj.keys())[:5]:
                describe(obj[k], f'{path}[\"{k}\"]', depth+1, max_depth)
    elif isinstance(obj, list):
        print(f'{indent}{path}: list of {len(obj)} items')
        if len(obj) > 0 and depth < max_depth:
            describe(obj[0], f'{path}[0]', depth+1, max_depth)
    else:
        val = repr(obj)
        if len(val) > 80: val = val[:80] + '...'
        print(f'{indent}{path}: {type(obj).__name__} = {val}')

describe(data)
"
```

### Phase 2: Targeted Extraction

Only after structure is known, write extraction code using the actual keys and nesting. Use `statistics.mean/stdev` for aggregation. Print results in a clean tabular format.

### Rules

1. **Never assume keys exist** — use the discovered structure from Phase 1
2. **One inspection call, then one extraction call** — no trial-and-error loops
3. **For large files** (>256KB), use the Python approach rather than the Read tool
4. **Print scalar summaries**, not raw arrays — the user wants insight, not data dumps
5. If the file has nested groups (e.g., scenarios with per-prompt results), aggregate with mean +/- std across the group
