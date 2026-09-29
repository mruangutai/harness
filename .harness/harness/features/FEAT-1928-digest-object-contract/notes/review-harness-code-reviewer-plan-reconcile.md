# Plan reconciliation review — FEAT-1928

**BLUF:** PASS. The reconciliation incorporates every binding drift and FEAT-70 constraint without changing SC-01–SC-08, D-01–D-05, or the settled design; approval is correctly reset to pending.

## Reconciliation assessment

- **Dependency topology:** T-01 has no dependency, T-02 depends only on T-01 and explicitly remains runnable independently of FEAT-70, T-04 depends on T-01 and alone carries the FEAT-70 hard pre-start gate, and T-03 waits for both runtime work (T-02) and the plan-reader slice (T-04). This isolates the moving plan-reader surface without serializing unrelated enforcement work (`plan.yaml: T-01–T-04`).
- **FEAT-70 re-anchoring:** T-04 individually anchors `_lead_digest`, `_digest_mapping`, `_digest_findings`, `cmd_record_amendments`, and `cmd_record_panel`. Its intent requires FEAT-70 to be merged first, then requires all five symbols to be located in `bin/plan_merge`, updates every source entry through `plan-merge.py apply` or `amend`, and only then runs a fresh `plan-merge.py check` before implementation.
- **Drift locks:** T-01 records the zero broad-catch ceiling, normal package-boundary import requirement, canonical reader rows, `main-session-direct` classification, and `scanned_files` entries. T-02 records the moved `check_state` files, exact `_inv15_digest_verdict` owner, INV-15/46 read declarations, structure-lock coverage, and explicit #1960/#1969 string/fallback test deletion. The lane includes `check-state.py and check_state/**`; all enforcement edits remain DEC-174 `main-session-direct`.
- **History preservation:** the panel retains all five historical reader records (cycle-0 scope/should-not-exist/design and cycle-1 scope/goalcheck), all marked `ran`; all six prior findings preserve IDs, severities, kinds, proportionality scopes where applicable, resolutions, and `resolved` dispositions. T-04 additionally binds reader-status and finding-field preservation during the reader migration.
- **No reopened design:** the BRIEF diff changes only approval metadata. The plan diff leaves D-01–D-05 and SC-01–SC-08 untouched; reconciliation changes are limited to baseline/lane drift, task constraints, the isolated T-04 slice, and dependency ordering. The existing adapter/locality split remains intact: live schema loading, provider projection, durable-record loading, and plan consumption retain separate owners and interfaces.
- **Approval:** both BRIEF and plan are pending; `needs_approval: true` remains set. The prior approval is retained as history in `notes/approval-2026-09-28.md`, not represented as current authorization.

## Verification

`plan-merge.py check` completed against the reconciled worktree: T-01 22 anchors, T-02 36, T-03 6, T-04 7; **4 tasks, 71 anchors, 0 failures**. No project-wide checks were run.

## Inspection criteria

- **SC-05:** T-02 still requires the pinned real-provider live-probe receipt with Harness/OMP SHAs, invocation, null rejection, retry continuity, valid completion, exit status, and transcript hash.
- **SC-08:** T-02/T-03 still require the hard-cut census, current-instruction cleanup, decision supersession, and unchanged DEC-208 ruling.

```yaml
VERDICT: PASS
DIGEST:
  headline: "The reconciled plan isolates only T-04 behind FEAT-70, binds every drift correction, preserves panel history and settled scope, and is pending re-approval."
  severity_max: none
  findings: []
  must_fix: []
  spec_violations: []
  code_grade: n_a
  reviewed: "plan:/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1928-digest-object-contract/.harness/harness/features/FEAT-1928-digest-object-contract/plan.yaml"
  human_commits_in_scope: []
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1928-digest-object-contract/.harness/harness/features/FEAT-1928-digest-object-contract/notes/review-harness-code-reviewer-plan-reconcile.md
```
