---
name: Don't inherit explanations from old docs — verify against current evidence
description: Explanations written before a bug was found are probably wrong about the cause of observed behavior
type: feedback
---

When old documentation explains an observed behavior, don't repeat the explanation — verify it. If the doc was written before a bug was discovered, the explanation is probably wrong.

**Why:** In the steering_diversity project, an old PR doc said divergence between eager and CUDA graph modes was "expected from float16 accumulation reordering." I repeated this in new docs. It was actually caused by a cache collision bug. The old explanation was a plausible-sounding guess that became incorrect once the real cause was found.

**How to apply:** When referencing prior explanations: (1) check if any bugs were found after the explanation was written, (2) test the claim yourself rather than trusting it, (3) if you can't verify, flag it as unverified rather than stating it as fact.
