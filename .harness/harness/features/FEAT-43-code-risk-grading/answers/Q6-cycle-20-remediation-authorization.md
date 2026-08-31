# Q6 — Remediation beyond the exhausted 13 cycles

**Decision:** Approved by the operator on 2026-08-29, answering Q2 of
`notes/ship-review-validate-final-panel-validator.md`.

Increase `max_total_cycles` from 13 to 20. Up to seven additional rework cycles are authorized.

**Option selected: option 1 — remediate.** The operator did NOT take option 2 (record a decision
accepting the six grade-3 production functions). There is no acceptance exemption for the feature's
self-grading failure: all four panel blockers are to be closed at their root, test-first.

- **CR-01** — the feature's own diff must pass the gate it ships. `code-grade.py` over the feature's
  own base..head range must exit 0; the six gated grade-3 production functions must reach their bar.
- **CR-02** — one canonical spelling for a gated, below-bar, non-grade-2 record shared by the tool,
  the shipped reviewer guidance and the digest schema (REQ-11).
- **SEC-01** — a reviewer's `code_grade` claim must be bound to `feature.json`'s `review_sha`; a
  self-named no-op range must not buy `n_a`.
- **UI-01** — a gated grade-3 record must carry a blocking signal in both the text and JSON report,
  and the guidance must name the state.

**Bounds that remain in force.** Cycles are a hard bound: at 20 the branch stops and returns
BLOCKED. After three failed repair attempts on any single blocker, stop and escalate rather than
thrash. Public contracts already established are preserved unless the signed requirements force a
change. No PR, merge, deploy, issue closure, worktree removal or ship action without a further
explicit operator ship decision; the run stops at the pre-ship briefing.
