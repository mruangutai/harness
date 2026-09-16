# ALTITUDE inspection — BUG-1699 lifecycle cards

**Conclusion: PASS.** The committed product diff `60b8d4d99f50edab6a63352ea43ebbc4ffc09750..212ad9ca` puts lifecycle projection behind one deep module and keeps phase-boundary authority with explicit callers; no ALTITUDE finding is warranted.

## Findings

[]

## Inspection coverage

- **One authority and locality:** `gh_board.project` is the sole card-placement policy (`.claude/skills/harness/bin/gh_board.py:126-150`); both write and audit/reconcile callers consume it (`gh-sync.py:1494-1529`, `board_lifecycle.py:488-529`, `check-state.py` INV-26 projection call).
- **Seams and depth:** the new projection module absorbs task, parent, and source-card placement while exposing one plan/record interface. Deleting it would recreate policy at its multiple callers; no speculative adapter was added.
- **Interface test surface:** active-phase projection, terminal placement, vocabulary refusal, and no-I/O/column invariants are exercised at the `gh_board.project` interface (`tests/unit/test-gh-board.py:415-471`); lifecycle command tests exercise the outer caller seam.
- **Ownership reassessment:** active-phase ownership is intentionally explicit at lifecycle callers and is documented once in the mirror contract (`.claude/skills/harness/references/github-mirror.md:32-68,99-130`), with the orchestrator playbook pointing to the transition boundaries (`.claude/skills/harness/SKILL.md:164-181`). This is appropriate caller authority, not duplicate policy.
- **Lifetime and residuals:** no new persistent adapter/client is introduced. Accepted residuals remain bounded by explicit controls: best-effort board writes, ship-time audit, and the narrow identity-guard caveat (`gh-sync.py:1483-1529,2290-2304`; `plan-merge.py:2063-2135`).

No source, test, plan, BRIEF, ledger, STATE, prior receipt, or run-record file was changed.
