# Q7 — Preemptive raise to 25 total cycles

**Decision:** Issued by the operator on 2026-08-29, unprompted, superseding the ceiling set in
`Q6-cycle-20-remediation-authorization.md`.

Set `max_total_cycles` to **25**. This supersedes 20; it does not supersede anything else in Q6.

Everything else in Q6 stands unchanged:

- The remediate-all path continues. **No finding is waived** — CR-01, CR-02, SEC-01 and UI-01 are
  each still to be closed at their root, test-first. There is no acceptance exemption for the
  feature's self-grading failure.
- Cycles remain a hard bound: at 25 the branch stops and returns BLOCKED.
- Three failed repair attempts on one blocker still means stop and escalate, not thrash. A larger
  budget is not authorization to keep retrying a repair that is not converging.
- **No ship, merge, deploy, PR, issue closure or worktree removal is authorized.** The run still
  stops at the pre-ship briefing for a separate, explicit operator decision.

`cycles_used` stays truthful and is incremented only for actual rework: a FAIL routed back, an
unmet-SC re-dispatch, or a send-back a lead reports from inside a run.
