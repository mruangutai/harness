# Operator signature — BUG-2399 — 2026-11-22

Signed by **fable-advisor** under the operator's delegated authority. The operator said: "follow my previous instructions regarding clean and green merge and deferring to advisor", and the previous instruction was "defer to the advisor to sign the plan when it comes back … defer any questions to the advisor".

Rework ruling: rounds=2, minutes=90. Overrules: none.

## Decision note (advisor's words)

> Plan verified against the 2026-11-22 grilling rulings and the repo, not just the digest. Every settled point survives intact: exact narrow rule `.harness/*/features/*/runs/*/ui/**` with no negations (T-02); ABORTED-run removal refusal as intended behavior with evidence preserved (T-01 exit-4/WOULD-DISCARD regression, T-03 doc); distill records committed before merge-distill with "no merge call may precede" (T-01 distill half, T-03 distillation.md); no Harness backfill, enforced by a build-time read-only zero-inventory recheck that stops on nonzero (T-02) — I re-verified zero ignored-untracked non-UI run files and 299 tracked non-UI/0 UI files at main today. The three SPEC passages T-03 targets (2.5 commit policy :252-253, QA force-add :1624, retention :2311-2312) are exactly the obsolete ones, and the retention edit aligns SPEC to DEC-238's existing station-based rule rather than changing it; DEC-238 is preserved byte-for-byte. Verify scripts are proportionate: red-gated on BUG-2399-labeled FAIL lines so missing setup can't fake red, receipts byte-preserved, no live GitHub/fleet mutation. Both panel findings resolved on the merits; no overrule needed.

## Execution observations (non-blocking)

1. The stale comment at `feature-worktree.py:341-343` ("`.gitignore:7` ignores `.harness/*/features/*/runs/**` … untracked BY CONSTRUCTION") becomes false after T-02. Fold the one-line correction into T-02 (GATE 3's `ls-files` conclusion stays true).
2. Do not "correct" the `prune-run-evidence.py` docstring about the UI lane under T-03's "direct repetitions" clause. Retention behavior is protected.
