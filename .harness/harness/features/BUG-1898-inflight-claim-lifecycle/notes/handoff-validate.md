# Handoff — BUG-1898-inflight-claim-lifecycle, validate → operator gate — written at 6bfc21e3ccdf78eb86cdd0eb250067348d887096, seq-3

## Next

The automated panel is clean. Before merge, the operator runs the credentialled live OMP probe from the feature worktree and records its PASS for SC-07. Do not merge or claim ship readiness until that receipt exists.

## Trust

- The c3 validator panel closed F-QA-01 with the exact two-label mutant oracle and both singleton/substitution negative controls — .harness/harness/features/BUG-1898-inflight-claim-lifecycle/runs/validate-c3-validator/digest.md — verified-at 6bfc21e3ccdf78eb86cdd0eb250067348d887096
- Unit and integration gates passed 42/42 and 70/70; the focused suite-preservation wrapper exited 0 — .harness/harness/features/BUG-1898-inflight-claim-lifecycle/notes/review-harness-qa-c3.md — verified-at 6bfc21e3ccdf78eb86cdd0eb250067348d887096
- SC-01 through SC-06 and SC-08 are met; SC-07 is pending_operator_gate — .harness/harness/features/BUG-1898-inflight-claim-lifecycle/notes/research-BUG-1898-inflight-claim-lifecycle-goalcheck-validate-c3.md — verified-at 6bfc21e3ccdf78eb86cdd0eb250067348d887096

## Dead ends

- Do not substitute dry-run output, unit evidence, or a fabricated note for the credentialled live OMP receipt — .harness/harness/features/BUG-1898-inflight-claim-lifecycle/BRIEF.md — verified-at 6bfc21e3ccdf78eb86cdd0eb250067348d887096
- Do not rerun the read-only panel at the same SHA; F-01, F-02, and F-QA-01 are closed — .harness/harness/features/BUG-1898-inflight-claim-lifecycle/runs/validate-c3-validator/digest.md — verified-at 6bfc21e3ccdf78eb86cdd0eb250067348d887096
- Do not remove the pre-existing scratch worktrees named by the assignment; the c3 panel removed every scratch artifact it created — .harness/harness/features/BUG-1898-inflight-claim-lifecycle/runs/validate-c3-validator/digest.md — verified-at 6bfc21e3ccdf78eb86cdd0eb250067348d887096

## Working set

- .harness/harness/features/BUG-1898-inflight-claim-lifecycle/BRIEF.md
- .harness/harness/features/BUG-1898-inflight-claim-lifecycle/feature.json
- .harness/harness/features/BUG-1898-inflight-claim-lifecycle/runs/validate-c3-validator/digest.md
- .harness/harness/features/BUG-1898-inflight-claim-lifecycle/notes/live-omp-probe.md

## Done when

Scope: operator executes SC-07 and records a real PASS before merge
Authority: brief-perspective:.harness/harness/features/BUG-1898-inflight-claim-lifecycle/BRIEF.md#operator
