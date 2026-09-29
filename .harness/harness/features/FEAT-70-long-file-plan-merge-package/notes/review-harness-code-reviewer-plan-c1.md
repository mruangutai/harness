# FEAT-70 helper-contract recheck

## BLUF

PASS with one medium, non-gating specification mismatch. The proposed local `copy_plan_merge(dst_bin)` can copy the same *shape* of tree, but it is not contract-equivalent to extending and reusing the settled helper: it creates a second implementation of executable-plus-package copying.

## Evidence and finding

The binding note requires the test suite to gain a tree-copy helper “as `check_state_support.copy_check_state`” so `PLAN_MERGE_BIN` mutation proofs copy the package, not one file (`.harness/notes/grilling-long-file-plan-merge-package-2026-09-28.md:60-65`). The existing helper is a concrete implementation of that operation: it copies the entry, restores executable mode, recursively copies the sibling package, and excludes `__pycache__` (`tests/integration/check_state_support.py:31-34,70-76`). Its two callers use it to build isolated executable-plus-package trees (`tests/integration/test-check-state-worktrees.py:148-150,291-303`).

The helper is presently hard-coded to `SCRIPT`, `PACKAGE_DIR`, `check-state.py`, and `check_state`, so T-01 cannot call it for `PLAN_MERGE_BIN` unchanged. That does not make a parallel local implementation equivalent to reuse: the draft explicitly directs T-01 to add `copy_plan_merge(dst_bin)` with the same copy/mode/cache responsibilities (`plan.yaml:64`; mirrored in `BRIEF.md:38`). Under that wording, the shared operation remains duplicated rather than the existing helper being generalized and reused.

**Finding (substance, medium; SC-01 mismatch):** If a later package-copy correction changes mode preservation, cache exclusion, symlink handling, or tree replacement in only one helper, check-state isolation and plan-merge mutation proofs construct different source trees; one proof family can then pass while no longer exercising the same complete-package contract. Amend T-01 to extract/generalize the existing executable-plus-sibling-package copy operation into one reusable integration-support helper, keep `copy_check_state` as its check-state-specific caller only if that name remains useful, and have `copy_plan_merge` (or its call sites) delegate to that same operation using paths resolved from `PLAN_MERGE_BIN`. Do not maintain two independent `shutil.copy`/`copytree` implementations.

This does not change the cycle-0 mission-proportionality judgment. The package split, twelve grade repairs, behavior fix, package-aware mutation proofs, classification migration, and immutable byte receipts still justify a plan mission; the finding only corrects how one required test-support operation is shared inside T-01.

## Review record

```yaml
VERDICT: PASS
DIGEST:
  headline: The local helper matches today’s copy behavior but duplicates rather than extends the settled reusable tree-copy operation.
  severity_max: med
  findings:
    - kind: substance
      scope: task
      severity: med
      reader: code-reviewer
      summary: "T-01 specifies a second executable-plus-package copy implementation instead of one reusable integration-support operation."
      why: "When copy semantics change in only one implementation, one mutation-proof family can pass against an incomplete or differently constructed source tree."
  must_fix: []
  spec_violations:
    - kind: mismatch
      path: plan.yaml
      ref: SC-01
  code_grade: n_a
  reviewed: "plan:/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-70-long-file-plan-merge-package/.harness/harness/features/FEAT-70-long-file-plan-merge-package/plan.yaml"
  human_commits_in_scope: []
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-70-long-file-plan-merge-package/.harness/harness/features/FEAT-70-long-file-plan-merge-package/notes/review-harness-code-reviewer-plan-c1.md
```
