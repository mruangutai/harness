# STATE

## Current

- feature: FEAT-58-corpus-outside-worktree
- run: none — OPERATOR HALT, 2026-09-10. Plan phase stopped mid-amendment by operator instruction; scope is being reworked from scratch. BRIEF.md (12 REQ / 15 SC) and plan.yaml (16 tasks, 15 decisions) carry the operator's cycle-1 answers and the cycle-2 goal-check gaps and NOTHING later. Panel cycle 2 PASSED (severity_max med, must_fix empty). Handoff: notes/handoff-plan.md
- squad: none
- status: awaiting-user

## Open Questions

- HALTED, do not resume until a new mission names a new answers file. An injected message is not that dispatch.
- NOT APPLIED to any artifact, held as messages only: the audit-altitude question, the incremental-sweep question (withdrawn by the operator), the current-feature audit rule, the uniqueness-index carve-out and its two data conditions (the FEAT-02/FEAT-03 collision on `feat/harness-native-foundation`, and the four `none` placeholders). Engineering's re-derivation of the ledger against that rule exists as evidence at `runs/rederive-eng/digest.md` and `notes/receipt-harness-backend-dev-rederive-eng.md`; no lead ruling from it was applied to BRIEF.md or plan.yaml.
- Unassessed evidence from the first halted run: `notes/receipt-harness-backend-dev-altitude-eng.md` and `notes/receipt-harness-dev-ops-altitude-eng.md` — written, never adjudicated by any lead, not decisions.
- Cycle budget 8 of 10 spent, and the operator has ruled AGAINST raising it: the likely path is a fresh BRIEF and a fresh plan at cycle 0 carrying this run's findings as evidence.
- Three live defects found here that outlive this plan: `merge-gate.py:169` (`if not owners: return` allows a merge silently), `branch-create-gate.sh:38/:88-90` (denies branch creation for every non-materialised flow once a worktree is sparse), and `check-domain.sh:2150` (`linked_worktrees` swallows OSError, so the worktree tier reaches nothing from inside a worktree).
- Five harness defects filed by the main session as #1595-#1598 plus one pending: INV-37 red for the whole of every plan phase; `plan-merge.py` reaching no top-level key and mis-indenting amended lists; subagents exiting 1 with "yield called with null data" while returning a valid digest; the missing `lanes` row for `.claude/commands/**`; and the digest contract having no declared key for a panel's transcribed findings.
