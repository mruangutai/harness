# FEAT-2081 — Brief intake

BRIEF.md is ready for signature discussion, not implementation approval. Its pending draft passes the feature-scoped INV-38, INV-41, and INV-49 check (exit 0, “all state invariants hold”). No plan.yaml or production files were written.

## Promises and evidence

- Operator: faster complete CI without fail-open aggregation, lost gates, or a pending check after shard dependencies finish.
- Code maintainer: complete discoverable partitions, unchanged unsharded behavior, and less audit work with identical findings.
- Ten SCs: integration automation SC-01/02/03/06/08; unit automation SC-07; pinned workflow inspection SC-04/05; user-run UAT SC-09/10.
- The user must run the throwaway-PR broken-test, shard-cancellation, and omitted-file cases, plus the restored green control (SC-09), and judge the live CI and controlled audit timing comparisons (SC-10).
- No applicable null runner gap. Actual Actions cancellation, context identity, and timing remain live verification gaps; local tests cannot discharge them.

## Open questions — signature recommendations

- OQ-01: Approve or amend four initial shards, below-100-second integration critical path in three consecutive passing runs, and lower median audit wall time across three same-host/corpus runs for each test/check-state path. These are recommendations, not settled thresholds; 45–70 seconds remains inference.
- OQ-02: Confirm shard-only cancellation is the required conclusion guarantee; keep whole-workflow cancellation/supersession separate. `always()` must not be presented as a guarantee after cancellation of its entire workflow.

## Binding references

DEC-174's enforcement-layer carve-out requires main-session-direct execution; DEC-183 preserves the required integration context and rejects claims that a workflow protects its own deletion; DEC-211 supplies complete selection, attribution, and isolation. Source issue: https://github.com/mruangutai/harness/issues/2081. The settled conversation supplied the measured baseline; it was not remeasured here.

## Principles applied

- Experience First — speed remains subordinate to the operator's trustworthy, concluding required check; no rejected suite-selection or paid-runner alternative was added.
