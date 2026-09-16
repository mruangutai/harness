# STATE

## Current

- feature: BUG-1725-task-file-overlap
- run: .harness/harness/features/BUG-1725-task-file-overlap/runs/validate-validator/digest.md
- squad: validator
- status: awaiting-user
- verdict: FAIL
- review_sha: b317f9a54f7f5f6570e0d36b1a46601357a02ec9
- severity_max: high
- cycles_used: 0 (cycle attribution is blocked by Q5)

## Open Questions

- Q1 (blocking, Main session direct): T-01 / SC-02 — resolve the approved criterion's unavailable fail-first proof; the exit-0 assertion passes both before and after the overlap implementation, so reframe with operator approval or supply genuinely discriminating evidence before revalidation.
- Q2 (blocking, Main session direct): T-01 / SC-03 / SC-04 — align the approved inspection paths with canonical `.claude` Git objects, or ship real objects at the declared `.agents` paths, then re-pin; exact `git show` at the current pin exits 128.
- Q3 (blocking, Main session direct): T-01 matrix — resolve the required unit gate failure in `test-check-state-inv35.py` (unquoted notes value reports INV-35 naming #217) before revalidation.
- Q4 (non-blocking harness defect): Why was the BUG-1725 UI reader later bound to other feature claims, preventing its artifact-form repair? Its measured UI scope-out remains usable.
- Q5 (blocking ledger defect): `check-state.py` requires one cycle for this FAIL run, but the required `feature-record.py run-end --cycles-used 1` route is rejected because the active feature schema forbids `runs[].cycles_used`; Main must reconcile the ledger mechanism before the next run.
