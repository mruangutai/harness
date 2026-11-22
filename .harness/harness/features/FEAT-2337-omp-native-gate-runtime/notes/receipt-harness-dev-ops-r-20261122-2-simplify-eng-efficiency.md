# Receipt — simplify · efficiency · FEAT-2337 plan surface (pending, unsigned)

BLUF: one low advisory finding, no blocking waste. Read-only; nothing executed or measured.

## Findings

1. **low** — plan.yaml T-02 intent (lines ~369-375): lineage check "ancestry plus NUL-safe changed paths for each intervening commit including merge parents".
   - Cost: a literal reading spawns one git process per intervening commit and repeats ls-tree/ancestry per claimed kind (unit + integration). This runs once per QA PASS return, not on the per-write hot path. Each git spawn is on the order of 10 ms [INFERENCE, unmeasured], so ledger-only chains of a few commits cost tens of ms. Advisory only.
   - Alternative: state "resolve lineage once per validate call, shared across kinds" and let the builder use one `git log -m --name-status -z -M review_sha..tested_commit` pass. That keeps per-commit change-then-revert and merge-parent semantics without N spawns. The builder can choose the mechanism either way; the plan need not pin it.

2. **info** — T-01/T-02/T-03 intents each re-read the BRIEF, research note and the DEC-100/174/187/234 sections sequentially. All three tasks are main-session-direct, so the same context is reused. Not worth a plan edit.

## Judged not waste (stated, not flagged)

- Final QA's full unit/integration receipts, full Bun wrapper, runtime and validate-digest suites after all commits are the boundary evidence.
- Focused verifies are already targeted: `--test-name-pattern FEAT-2337`, `--feat2337`, `--only run_feat2337_*`, each bounded under 55 s.
- `--benchmark` (3 warmups + 15 pairs × 5 gates ≈ a few seconds [INFERENCE]) is deliberately serialized outside pooled suites for idle-host validity.
- The `--feat2337` grading kept out of the default suite avoids a permanently growing diff re-grade (panel finding already resolved).
- Deleting the 1800 s per-kind rerun in validate-digest is the feature's efficiency gain.
- Settled constraints (async callers, 30 s constant, five parallel gates, receipt-only PASS) were not relitigated.
