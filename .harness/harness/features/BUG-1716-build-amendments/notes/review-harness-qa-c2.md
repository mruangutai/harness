# QA c2 — pinned matrix gate

**BLUF: PASS.** Pinned SHA `e348b40d5bba915a6131be37de728947da990deb` passes both required matrix kinds. The V-01 ordinary-ledger-I/O regression executes its `PermissionError` arm and proves the command reports the error and restore with no traceback while both `plan.yaml` and `feature.json` stay byte-identical.

## Scope and matrix

Phase 1 (before source review) required automated coverage for closed lead-digest amendments (SC-01), all-or-nothing task transcription and signed-hash/INV-40 behavior (SC-02/SC-03), and exact amendment-overrule/refusal behavior (SC-04). The complete feature plan includes API T-02/T-03, cross-module T-04, runtime-code bugfix T-05, and documentation tasks. Matrix requirements are therefore `unit` and `integration`; no changed detect surface requires a locally-run kind.

| Kind | State | Exact command | Result |
|---|---|---|---|
| unit | satisfied | `python3 .claude/skills/harness/bin/run-unit-tests.py --kind unit` | exit 0; 40 files; 5.79s wall |
| integration | satisfied | `python3 .claude/skills/harness/bin/run-unit-tests.py --kind integration` | exit 0; 72 files; 92.66s wall |

`matrix_ok: true`. The commands ran from a detached QA worktree resolving exactly to the reviewed SHA, not the ambient feature checkout.

## V-01 remeasurement

`tests/integration/test-plan-merge.py:3933-3958` installs a mode-000 `feature.json.lock` after recording original bytes, causing the ledger lock acquire to raise `PermissionError` after the plan splice. Its executed integration output reports all three assertions passing: nonzero exit naming `PermissionError` with no traceback, restore message, and equality of both plan and ledger bytes. The case is included in `CASES` at `tests/integration/test-plan-merge.py:4062-4063`. The implementation catches the ordinary exception and restores under the plan lock at `.claude/skills/harness/bin/plan-merge.py:2256-2271`. V-01 is closed.

## SC evidence and fail-first

| SC | Current evidence | Retained fail-first evidence |
|---|---|---|
| SC-01 | `tests/integration/test-validate-digest.py:603-651` | `notes/receipt-main-session-T-02-fail-first.md:6-24` |
| SC-02 | `tests/integration/test-plan-merge.py:3711-3840,3909-3958` | `notes/receipt-main-session-T-04-fail-first.md:6-37` |
| SC-03 | `tests/integration/test-plan-merge.py:3647-3695`; `tests/integration/test-check-state-feat59.py:440-496` | `notes/receipt-main-session-T-04-fail-first.md:6-9`; `notes/receipt-main-session-T-05-fail-first.md:7-18` |
| SC-04 | `tests/unit/test-feature-record.py:245-288` | `notes/receipt-main-session-T-03-fail-first.md:6-21` |

SC-05 through SC-07 are inspection criteria. Phase-1 expectations are covered; `coverage_gaps: []`. `findings: []`; `must_fix: []`.

The known `validate-digest.py` #919 re-verification defect (issue #1756) was not used to re-run or invalidate these direct Python matrix results.

QA removed its temporary pinned worktree after the runs. A final `git worktree list --porcelain` contains no `.claude/worktrees/qa-*-pin` entry.
