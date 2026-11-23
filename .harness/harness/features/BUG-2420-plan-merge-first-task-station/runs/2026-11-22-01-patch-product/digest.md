# BUG-2420 patch product

## Acceptance contract
Return pending BRIEF.md (at most 120 lines) and plan.yaml with exactly T-01, main-session-direct, explicit status ready seeded through plan-merge apply, source issue 2420, and top-level status plan. Scope is stations.py and its tests only. Require test-first receipts for the three-row unit regression, one drafting-path integration regression, and signed approval-byte survival; do not duplicate BUG-2349 union coverage. Record the actual Python grade bars and applicable CI checks, including the canonical-reader audit, in the task verification contract. Require plan-merge check exit 0 with zero failures and its exact output in the PM artifact. No implementation or test execution in this run.

DEC-225: no readers, panel, or goal-check. No prototype is needed: this changes existing CLI behavior, not an end-user interaction design; the operator may override that assessment.

## Assessment
Pending PM return. A missing binding requirement or invalid draft is inadequate; preserve the pending signature gate and report any blocker rather than weaken scope.

## Final assessment — PASS, signature required
Pending BRIEF.md and plan.yaml satisfy the bounded patch intake. T-01 on disk explicitly carries status: ready and execution_mode: main-session-direct; approval.status is pending, top-level status is plan, source_issues is [2420]. Three traced SCs require test-first unit/integration and signed-approval preservation. Verification names the canonical-reader audit and actual grade bars (production 4, tests 3). No implementation or tests ran, and SC delivery remains future work.

### Member
- draft / harness-pm / PASS: Pending patch artifacts ready; on-disk T-01 is status ready and main-session-direct.
- Member artifact: ../../notes/research-BUG-2420-patch-product.md
- Changed deliverables: ../../BRIEF.md and ../../plan.yaml.
- One step, zero send-backs. No readers, panel or goal-check ran under DEC-225.

### Plan-check receipt (member-observed, not rerun by lead)
Exact output:

```text
OK T-01 3 anchor(s) resolved
CHECK /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2420-plan-merge-first-task-station/.harness/harness/features/BUG-2420-plan-merge-first-task-station/plan.yaml against /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2420-plan-merge-first-task-station: 1 task(s), 3 anchor(s) resolved, 0 failure(s)
EXIT STATUS: 0
```

### Open questions
None. Obtain the operator's signature before executing T-01. Product docs/spec.md, docs/decisions.md and docs/architecture.md are absent in the assigned checkout; this limitation is disclosed in the BRIEF and member receipt. No prototype needed for this bounded existing-CLI correction; operator may override.

```yaml
VERDICT: PASS
DIGEST:
  headline: BUG-2420 pending BRIEF and single-task plan ready for signature; plan
    check passes with zero failures.
  open_questions: []
  files_touched:
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2420-plan-merge-first-task-station/.harness/harness/features/BUG-2420-plan-merge-first-task-station/BRIEF.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2420-plan-merge-first-task-station/.harness/harness/features/BUG-2420-plan-merge-first-task-station/plan.yaml
  expertise_update: []
  team: patch-product
  steps_run: 1
  cycles_used: 0
  members:
  - step: draft
    persona: harness-pm
    verdict: PASS
    headline: Pending patch artifacts ready; on-disk T-01 is status ready and main-session-direct.
    files_touched:
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2420-plan-merge-first-task-station/.harness/harness/features/BUG-2420-plan-merge-first-task-station/BRIEF.md
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2420-plan-merge-first-task-station/.harness/harness/features/BUG-2420-plan-merge-first-task-station/plan.yaml
  must_fix: []
  branch: feat/BUG-2420-plan-merge-first-task-station
  escalations: []
  adequacy_notes:
  - 'Member-observed plan check exact output:

    OK T-01 3 anchor(s) resolved

    CHECK /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2420-plan-merge-first-task-station/.harness/harness/features/BUG-2420-plan-merge-first-task-station/plan.yaml
    against /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2420-plan-merge-first-task-station:
    1 task(s), 3 anchor(s) resolved, 0 failure(s)

    EXIT STATUS: 0'
  - 'Confirmed on-disk T-01 explicitly carries status: ready and execution_mode: main-session-direct.
    BRIEF Approval and plan approval.status remain pending; top-level status is plan;
    source_issues is [2420].'
  - No readers, panel or goal-check ran under DEC-225. No implementation or test execution
    occurred; SC implementation remains future work.
  - 'Actual grade bars encoded: changed production Python functions >=4; new/changed
    test functions >=3. Verification includes python3 .agents/skills/harness/bin/check-plan-routes.py
    --canonical-reader-audit.'
  - Assigned product docs/spec.md, docs/decisions.md and docs/architecture.md are
    absent; disclosed without invented substitute guidance.
  - No prototype required for this bounded correction to existing CLI behavior; operator
    may override that assessment.
  sc_status: []
  needs_approval: true
  severity_max: none
  matrix_ok: none
  coverage_gaps: []
  findings: []
  readers: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2420-plan-merge-first-task-station/.harness/harness/features/BUG-2420-plan-merge-first-task-station/runs/2026-11-22-01-patch-product/digest.md
```
