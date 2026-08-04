---
name: decTest is boring; focus on crowdsourced Tevet tasks
description: HIGH PRIORITY. Matthew has said many times that decTest (temperature/sampling sweep) is not a measurement of true diversity — do not use decTest underperformance or sign-flips as counter-evidence against $C \times a_n$
type: feedback
originSessionId: 53b7ce05-4c5a-4951-993d-81ca5410d748
---
decTest varies sampling parameters (temperature, top-p); this changes surface token-level diversity without changing what the policy could semantically express. Matthew does not consider this a measurement of real diversity and has stated this repeatedly across sessions. decTest is included in the paper only for consistency with Tevet and Berant's original benchmark.

**Why:** Matthew considers the crowdsourced McDiv / McDiv_nuggets / ConTest tasks (which use human diversity labels) the real external validation of $C \times a_n$. A sign flip on decTest is a known, expected, and uninteresting artifact of temperature scaling and should not restructure narrative or claims.

**How to apply:**
- Scope ablation / comparison claims to "the nine binary tasks" (ConTest, McDiv_nuggets, McDiv × {prompt_gen, resp_gen, story_gen}) or "the crowdsourced benchmarks."
- Do not flag decTest results as a problem for headline claims unless specifically asked.
- When reporting ablation tables that include decTest rows, note the sign flip only if it is load-bearing for a specific argument — otherwise pass over.
- If tempted to suggest a prose edit that makes a narrative "fully transparent about decTest," don't — it's not a transparency gap, it's intentional scoping.
