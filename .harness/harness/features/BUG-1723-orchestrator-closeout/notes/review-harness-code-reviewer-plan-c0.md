# Scope and architecture review — BUG-1723-orchestrator-closeout

## BLUF

The draft covers the live close-run, fail-closed phase-seam, playbook, and post-shipment measurement requirements, and its composition order matches the settled intent. Two specification defects should be corrected before signature: the settled `validate-digest.py` main-session-direct surface is absent from the lane table, and T-03's verify block does not bind the per-file documentation contract it claims to verify.

## Findings

1. **[med · substance · reader: scope] The lane table drops a settled main-session-direct source surface.** `plan.yaml` T-01 names `.claude/skills/harness/bin/validate-digest.py#validate`, and the grilling record's “Build execution” ruling explicitly places `validate-digest.py` in `main-session-direct`, but `lanes.rows` has no row for it. If implementing the composed validator requires changing that named surface, the plan has no declared execution route for the change despite DEC-179; the signed plan would contradict its own T-01 file set and the settled lane. Add the `validate-digest.py` lane row, or remove it from T-01's change surface while explicitly recording that it is invoked unchanged.

2. **[med · substance · reader: scope] T-03's verify can pass while SC-04 is false.** The command checks `close-run` in each file but searches `STATE.md`, `handoff`, `commit`, and `quarantine` only in the three-file concatenation. For example, removing the separate-commit instruction from `harness/SKILL.md` still passes if `ledger.md` happens to contain “commit”; similarly it does not bind quarantine to wake time. That allows a task declared verified even though one required playbook surface omits or contradicts the settled close-out boundary. Make the checks file-specific and semantic enough to distinguish separate writes and wake-time quarantine, or rely explicitly on SC-04's inspection gate rather than claiming this token probe verifies the contract.

## Trace and architecture assessment

- No orphan task or nonexistent SC trace found: T-01 serves SC-01/02, T-02 serves SC-03, and T-03 serves SC-04 plus the documented SC-05 measurement procedure.
- T-03's dependency on T-01 and T-02 is valid: its prose must describe both the shipped command and INV-42. T-01 and T-02 are independent and may proceed in parallel.
- D-01/T-01 preserve the settled composition order: digest validation → run-end → optional plan-station → optional judgement → spend, stopping at the first refusal while retaining earlier durable writes.
- Architecture is proportionate: `feature-record.py close-run` is a deep orchestration interface over existing authoritative writers rather than duplicated mutation logic; existing seams and adapters retain their validation, locking, and diagnostics. The phase invariant remains local to `check-state.py`. No speculative seam, pass-through module, or needless new adapter is planned.
- The fallback phase-seam contract matches the settled issue-1708 constraint: no new feature field and no `run_uid` dependency; unusable chronology fails closed.
- No mission- or task-level proportionality finding: all three tasks serve live requirements and no task plans work outside the grilling scope.

## Open questions

None.
