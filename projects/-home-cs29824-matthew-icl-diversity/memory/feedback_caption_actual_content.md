---
name: Caption what exists, not what the argument needs
description: When creating an artifact (figure, table, plot, docstring, diagram) accompanied by descriptive text, the text must describe what is actually in the artifact, not what the surrounding argument wants it to show
type: feedback
originSessionId: 9471abbb-ddc3-4685-bb7a-3240a6d9a526
---
When creating any artifact that is accompanied by descriptive text — a figure with a caption, a table with a title, a function with a docstring, a diagram with a label, a commit with a message — write the text against the actual content of the artifact. If the honest description has to omit panels, skip columns, soften behavior, or hand-wave over what's really in the artifact to fit the surrounding argument, the artifact is wrong, not the text.

**Why:** Shipped a three-panel figure whose caption described only one panel, because the surrounding argument only needed that one panel's content. The figure stayed in the artifact for a long time with a misleading caption, looked overstuffed for its stated purpose, and was eventually cut wholesale. If the caption had been written honestly at creation time, the mismatch would have surfaced immediately — prompting either a simpler figure or a restructured argument — instead of being discovered much later by someone asking "does this figure match what the caption claims?"

**How to apply:** At artifact-creation time, before moving on, verify the descriptive text by actually inspecting the artifact (re-render the figure, look at the table, read the function signature and returns, read the diff). Read the description aloud against what's in front of you. If the honest description doesn't fit the argument, fix the artifact — drop panels, split tables, narrow function scope, refactor — rather than letting the text paper over the gap. Captions drift from figures the same way hand-typed numbers drift from their sources: silently, and only caught on audit.
