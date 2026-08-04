---
name: Investigate discrepancies before widening tolerances
description: Never propose relaxing test tolerances as a first response to unexpected results
type: feedback
---

Never propose widening test tolerances as a first response to unexpected discrepancies. Investigate the root cause first.

**Why:** Matthew cares about understanding *why* things differ, not just making tests green. "The test would pass if we relaxed the tolerance" is not an answer — it's avoiding the question.

**How to apply:** When a test fails with values close but not matching, systematically investigate: check inputs, check conversion logic, try different configurations, search for known issues. Only after the root cause is understood should tolerances be discussed, and they should be justified by the investigation.
