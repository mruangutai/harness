# Handoff — FEAT-36-merge-gitignore-coverage, plan → build — written at 0fa8f336e55dc57bca09a9f7df0524a35195ee7e, seq-3

## Next

Present `BRIEF.md` and `plan.yaml` for explicit user approval. Only after the main session records
both signatures and transitions the feature to Ready may a build orchestrator dispatch T-01 through
harness-eng-lead to harness-dev-ops (`plan.yaml#tasks/T-01`).

## Trust

- The brief states five requirements and six verification-bound success criteria, with approval pending — .harness/harness/features/FEAT-36-merge-gitignore-coverage/BRIEF.md — UNVERIFIED
- The plan contains one pending team task tracing REQ-01 through REQ-05 to harness-dev-ops, with approval pending — .harness/harness/features/FEAT-36-merge-gitignore-coverage/plan.yaml — UNVERIFIED
- The route checker reports zero violations for T-01 at the recorded `resolved_at` revision — .harness/harness/features/FEAT-36-merge-gitignore-coverage/plan.yaml#lanes — UNVERIFIED
- REUSE returned an explicit empty outcome; disposition: no PM application and no advisory carry-forward — .harness/harness/features/FEAT-36-merge-gitignore-coverage/notes/receipt-harness-dev-ops-plan-simplify-reuse.md — UNVERIFIED
- SIMPLIFICATION returned an explicit empty outcome; disposition: no PM application and no advisory carry-forward — .harness/harness/features/FEAT-36-merge-gitignore-coverage/notes/receipt-harness-dev-ops-plan-simplify-simplification.md — UNVERIFIED
- EFFICIENCY returned an explicit empty outcome; disposition: retain both the direct baseline run and all-kinds boundary verification — .harness/harness/features/FEAT-36-merge-gitignore-coverage/notes/receipt-harness-dev-ops-plan-simplify-efficiency.md — UNVERIFIED
- ALTITUDE returned an explicit empty outcome; disposition: retain D-01, D-02, and T-01 at their current authority levels — .harness/harness/features/FEAT-36-merge-gitignore-coverage/notes/receipt-harness-dev-ops-plan-simplify-altitude.md — UNVERIFIED
- The four-angle simplify segment completed PASS with zero substantive or advisory findings, so no product-lead/PM application run was warranted — .harness/harness/features/FEAT-36-merge-gitignore-coverage/runs/plan-simplify-eng/digest.md — UNVERIFIED

## Dead ends

- Do not start T-01 or any build action while either approval remains pending — .harness/harness/features/FEAT-36-merge-gitignore-coverage/BRIEF.md#approval and .harness/harness/features/FEAT-36-merge-gitignore-coverage/plan.yaml#approval — UNVERIFIED
- Do not edit merge-gitignore.sh unless the new behavioral test first proves a documented contract violation — .harness/harness/features/FEAT-36-merge-gitignore-coverage/plan.yaml#D-02 — UNVERIFIED
- Do not reopen empty simplify outcomes as invented work; route only new substantive evidence through product-lead and PM — .harness/harness/features/FEAT-36-merge-gitignore-coverage/runs/plan-simplify-eng/digest.md — UNVERIFIED
- Do not expand coverage to unrelated utilities or merge the eventual pull request — .harness/harness/features/FEAT-36-merge-gitignore-coverage/BRIEF.md#constraints — UNVERIFIED

## Working set

- .harness/harness/features/FEAT-36-merge-gitignore-coverage/BRIEF.md
- .harness/harness/features/FEAT-36-merge-gitignore-coverage/plan.yaml
- .harness/harness/features/FEAT-36-merge-gitignore-coverage/STATE.md
- .harness/harness/features/FEAT-36-merge-gitignore-coverage/feature.json
- .harness/harness/features/FEAT-36-merge-gitignore-coverage/runs/plan-simplify-eng/digest.md
