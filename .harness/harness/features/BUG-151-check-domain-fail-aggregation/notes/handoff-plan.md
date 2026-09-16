# Handoff — BUG-151-check-domain-fail-aggregation, plan → build — written at 6d969ed3, seq-1

## Next

Once the main session signs `approval` in both BRIEF.md and plan.yaml, dispatch the `build` team to
`harness-eng-lead` with T-01 first (`depends_on: []`), then T-02 (`depends_on: [T-01]`). Both are
`execution_agent: harness-backend-dev`, both `change_type: bugfix`, both touch only
`tests/integration/test-check-domain.py`. Carry each task's `verify:` verbatim from plan.yaml.

## Trust

- The defect is real and unchanged at the base: 20 `fails += run_x()` statements plus a
  `+ run_bug1305_cases()` return term aggregate 24 `run_` names, and the comment above them claims
  an assertion that does not exist — tests/integration/test-check-domain.py:5182-5235 —
  verified-at 6d969ed3
- The suite is green at the base: exit 0, 398 column-0 `ok` lines, 0 column-0 `FAIL` lines, 38s
  wall — orchestrator ran it on this worktree — verified-at 6d969ed3
- importlib-loading the module costs 0.03s and executes no cases, so T-01's `verify:` is cheap and
  discriminating (it fails pre-change on the absent `_aggregation_verdict`) —
  .harness/harness/features/BUG-151-check-domain-fail-aggregation/plan.yaml T-01.verify —
  verified-at 6d969ed3
- The panel graded a PLAN and no code, so no `review_sha` exists yet and none is required until the
  Building → Review seam —
  .harness/harness/features/BUG-151-check-domain-fail-aggregation/runs/plan-validator/digest.md —
  verified-at 6d969ed3
- Two sibling suites carry the identical shape and are OUT of scope by the operator's own scoping:
  tests/integration/test-validate-digest.py (13 sites) and tests/integration/test-bash-write-guard.py
  (8 sites) — BRIEF.md `## Constraints` — UNVERIFIED (counts reported by the product lead, not
  re-measured by the orchestrator)

## Dead ends

- Strict equality of printed FAIL lines against the returned total: rejected, not deferred. The two
  candidate invariants are exit-code-equivalent, so nothing can be gained on any run's verdict, and
  strict equality risks a false alarm on a helper that prints two FAIL lines for one counted
  failure — plan.yaml D-01 — verified-at 6d969ed3
- A hand-written registry list of block names (the issue's option 1 as written): rejected, because
  an enumeration cannot notice a block nobody enumerated — plan.yaml D-02 — verified-at 6d969ed3
- A pre-edit working-tree baseline for SC-03: removed from the plan. The baseline is recovered from
  the pinned commit inside T-02 instead — plan.yaml T-02.intent step 8(a) — verified-at 6d969ed3

## Working set

- .harness/harness/features/BUG-151-check-domain-fail-aggregation/plan.yaml
- .harness/harness/features/BUG-151-check-domain-fail-aggregation/BRIEF.md
- tests/integration/test-check-domain.py
- .harness/harness/features/BUG-151-check-domain-fail-aggregation/runs/plan-validator/digest.md

## Done when

Scope: dispatch the build team for T-01 once the plan carries the operator's signature
Authority: approval:.claude/worktrees/harness/BUG-151-check-domain-fail-aggregation/.harness/harness/features/BUG-151-check-domain-fail-aggregation/BRIEF.md#Approval
