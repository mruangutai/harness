# Send-back criteria — FEAT-2516 plan run 2026-11-27-01 (cycle 2; written before any return)

Operator rulings 2026-11-27: scope B-9 (#2524) only; retarget T-03 to feature_record/ after the
rebase onto 3e979ae3; one scope re-read of T-03 for PF-d0e16ad5 and PF-3a8e31e4.

## draft/revise (pm) is sent back if any of:
- tasks are not exactly T-03 and T-05; source_issues not [2524]; approval not pending; `approval:` written.
- any SC, perspective, decision (D-01, D-03), lane row or decisions_affected row survives that served only T-01/T-02/T-04; any trace to a removed SC.
- T-05 depends_on still names a removed task, or T-05 verify still runs suites only removed tasks needed without saying why they stay as regression.
- T-03 files/intent/verify still name `feature-record.py#_run_end_digest`, `feature_schema.py`, or line numbers; the `code_repository` home and `_bound_mirror_binding` reuse not re-derived against feature_record/; validate-digest.py step not re-checked against its current text.
- `plan-merge.py check` exit != 0 or output not reported.
- BRIEF still describes B-1..B-8 problems/SCs or carries the operator / code-maintainer perspectives only those tasks served.

## scope (code-reviewer) is sent back (once) if:
- it does not state, per PF-d0e16ad5 and PF-3a8e31e4, closed or open against the revised T-03 text AND the worktree code; or ranges beyond T-03 (T-05 only where T-03 reaches it).

## apply (pm) is sent back if:
- record-panel / set-panel / check not exit 0 or output not reported; a removed-task finding marked `resolved` as if fixed (must be disposed as moot, honestly); digest lacks the per-finding status of all ten cycle-1 findings.

## goalcheck (pm): sent back if any surviving perspective lacks a grade, or graded against BRIEF instead of the grilling's B-9 rows.

## Never re-panel: what the re-read leaves open goes to signature (DEC-176).
