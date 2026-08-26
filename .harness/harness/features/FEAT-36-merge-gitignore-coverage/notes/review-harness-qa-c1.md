# QA gate — PASS

**Review SHA:** `df23bdaa7113700977ec43e617e293c854c0854e`
**Range:** `0fa8f336e55dc57bca09a9f7df0524a35195ee7e..df23bdaa7113700977ec43e617e293c854c0854e`

## Result

T-01 is `change_type: feature` with `test_kinds: [unit, integration]` (`plan.yaml:41-57`). The pinned matrix requires both kinds (`.harness/harness.json:40-50`); no interaction-flow predicate fires and `eval` is not applicable. Both configured commands are active: unit `.agents/skills/harness/bin/run-unit-tests.sh --kind unit`, integration `.agents/skills/harness/bin/run-unit-tests.sh --kind integration` (`.harness/harness.json:103-122`). Discovery is non-zero: `run-unit-tests.sh:17-18` lists 23 unit and 24 integration scripts, including the changed `test-merge-gitignore.py` only in integration.

The prescribed command was run verbatim in a detached worktree at the review SHA:

```sh
python3 .agents/skills/harness/bin/test-merge-gitignore.py &&
.agents/skills/harness/bin/run-unit-tests.sh --kind all
```

It exited **0** in 155.16s. Direct evidence: all seven named merge cases passed (SC-01..SC-05: `test-merge-gitignore.py:36-123`), then the all-kinds run exited 0 and emitted `PASS test-merge-gitignore.py`. Thus all 23 unit and all 24 integration registrations executed without a failed script. The all-kinds invocation also ran the registration drift detector and kind cross-check before tests (`run-unit-tests.sh:42-127`); no `MISCONFIGURED` or `KIND-DRIFT` finding was emitted. The changed test is explicitly registered in `INTEGRATION_SCRIPTS` (`:18`) and exact-path integration detection (`harness.json:118-122`), so there is no kind drift.

## C0 continuity and limits

- **F-01 / MF-01 (mandatory matrix failure): closed.** The review SHA includes the isolated-hook `PYTHONDONTWRITEBYTECODE=1` repair (`test-bash-write-guard.py:469-471`) while retaining the one-implementation assertion requiring `after == (2, 2)` (`:503-506`). Its successful all-kinds execution establishes the repaired path under the prescribed gate.
- **F-02 (diagnostic exactness): advisory continuity only.** The incomplete-check test still uses substring matching (`test-merge-gitignore.py:69-73`), so fabricated supersets are not rejected. This is a cross-panel non-blocking advisory, not a new QA-gate failure.
- Adequacy limit: this gate measured required unit/integration execution and behavioral SC-01..SC-05. SC-06 is inspection-only; no UI or AI eval applies.

## Findings and disposition

- New findings: none. `must_fix: []`.
- Open questions: none.
- Files touched: `.harness/harness/features/FEAT-36-merge-gitignore-coverage/notes/review-harness-qa-c1.md`.
