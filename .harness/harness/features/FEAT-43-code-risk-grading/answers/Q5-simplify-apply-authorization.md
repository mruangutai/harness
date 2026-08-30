# Q5 — Does the max-13 authorization cover SIMPLIFY's R-01 apply?

**Decision:** Answered by the operator on 2026-08-28. Supersedes the reading recorded in
`notes/handoff-validate.md` and in `Q3-cycle-13-overrun.md`.

Q3 authorized the sequence "configured QA, then SIMPLIFY, commit source, set a new immutable review
pin, synchronize Review, and run the full validator panel" while permitting "no additional
source-fix cycle". The blocked SIMPLIFY run read those two clauses as contradictory and stopped.

The operator resolves it as follows. **SIMPLIFY is authorized as a standard four-angle pass, and a
standard pass includes its single warranted apply under the one-fix ceiling.** R-01 is therefore
inside the already-authorized SIMPLIFY step, not an additional source-fix cycle. It does not
increment `cycles_used`, which stays at 13 of 13.

Scope of the apply is exactly R-01 from `runs/validate-fix-c13-simplify-eng/digest.md`: consolidate
commit resolution onto the grading module's resolver, preserving commit-only resolution,
`--end-of-options`, option-like revision rejection, and both callers' observable error behavior.
Nothing else in the working tree is reopened.

**No source fix is authorized after the next validator panel.** A panel FAIL is terminal BLOCKED.
A panel PASS continues to product goal-check, documentation, UAT handling, and the human ship
briefing. The ship decision remains the user's; merge and deploy remain prohibited.
