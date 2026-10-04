# Handoff — BUG-1898-inflight-claim-lifecycle, build → validate — written at 84c3a6cbe74c7c27337d4372a68be60fca834118, seq-2

## Next

Dispatch the validate team to harness-validator-lead over review SHA `84c3a6cbe74c7c27337d4372a68be60fca834118`: QA gates the configured matrix and red baseline `0aa337f1`, code reviews spec before quality, security audits claim selection and release, UI self-scopes out, and goalcheck grades the four BRIEF perspectives. The lead must consolidate actionable findings with concrete failure scenarios and weigh the three unapplied simplify findings named in the build digest.

## Trust

- The build run is closed PASS over T-01 through T-05 and names the implementation pin — .harness/harness/features/BUG-1898-inflight-claim-lifecycle/runs/build-main-direct/digest.md — verified-at 84c3a6cbe74c7c27337d4372a68be60fca834118
- The feature ledger pins the same review SHA and records one build cycle — .harness/harness/features/BUG-1898-inflight-claim-lifecycle/feature.json — verified-at 84c3a6cbe74c7c27337d4372a68be60fca834118
- The canonical review base is merge-base origin/main at a4d72e7fc91d0cf7a568d9e2a5225465a422170e — .git — verified-at 84c3a6cbe74c7c27337d4372a68be60fca834118

## Dead ends

- Do not run or grade the live OMP probe in the panel; it is the operator-run merge gate and has no receipt — .harness/harness/features/BUG-1898-inflight-claim-lifecycle/notes/live-omp-probe.md — verified-at 84c3a6cbe74c7c27337d4372a68be60fca834118
- Do not apply simplify suggestions during read-only validation; assess the three unapplied items, especially `_held_children` role filtering — .harness/harness/features/BUG-1898-inflight-claim-lifecycle/runs/build-main-direct/digest.md — verified-at 84c3a6cbe74c7c27337d4372a68be60fca834118
- Do not invent automated stale-claim cleanup or release any live or ambiguous row — .harness/harness/features/BUG-1898-inflight-claim-lifecycle/notes/ship-checklist.md — verified-at 84c3a6cbe74c7c27337d4372a68be60fca834118

## Working set

- .harness/harness/features/BUG-1898-inflight-claim-lifecycle/BRIEF.md
- .harness/harness/features/BUG-1898-inflight-claim-lifecycle/plan.yaml
- .harness/harness/features/BUG-1898-inflight-claim-lifecycle/feature.json
- .harness/harness/features/BUG-1898-inflight-claim-lifecycle/runs/build-main-direct/digest.md
- .harness/harness/features/BUG-1898-inflight-claim-lifecycle/notes/live-omp-probe.md

## Done when

Scope: one consolidated read-only validation panel at the pinned implementation SHA
Authority: brief-perspective:.harness/harness/features/BUG-1898-inflight-claim-lifecycle/BRIEF.md#code maintainer
Authority: plan-task:T-01.verify
Authority: plan-task:T-03.verify
Authority: plan-task:T-05.verify
