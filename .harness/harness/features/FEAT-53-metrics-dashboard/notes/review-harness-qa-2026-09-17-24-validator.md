# QA gate — T-27 U-01 repair

## BLUF

**FAIL:** the focused fixtures and server import pass, and the absent-clone degradation is exercised non-vacuously, but T-27 has no fixture proving its required **all-unreadable** 500 behaviour. This is a substantive coverage gap, not a command failure.

## Scope and pin

- Reviewed delta: `93785232ac32ae4fecc0a456d286e772ad15eb82..cee11b46240e9b80f97cfb6d3aaa601b6514abe0` (T-27 literal verify at `plan.yaml:1773-1775`).
- The supplied checkout currently has excluded `f637728e` checked out; `cee11b46..f637728e` changes only `feature.json`, not the four T-27 source/fixture files. The executed focused fixtures therefore exercised the exact pinned T-27 code and test files; no claim is made about the excluded commit.
- Phase 1 expected: collector and endpoint fixtures must non-vacuously cover absent-clone readable-row/error degradation, `repo=all` 200, selected absent repository 500, all-unreadable 500, invalid config 500, plus Python 3.11+ import.

## Executed evidence now

- `python3 --version` → `Python 3.14.5`.
- `python3 tests/integration/test-work-dashboard.py --case collector` → PASS; discovered/executed **10/10** assertions. The absent-clone assertion executed and printed readable rows plus exactly one `{repo, path, reason}` error (`test-work-dashboard.py:123-152`).
- `python3 tests/integration/test-metrics-dashboard.py` → PASS; discovered/executed **9/9** unittest cases in 15.596s. `test_absent_fleet_clone_degrades_work_payload` asserts `repo=all` 200 with `FEAT-101-harness` readable, exactly one error with `repo`, `path`, and `reason`, and selected absent `alpha` 500 (`test-metrics-dashboard.py:119-140`). Invalid config is 500 (`:301-305`).
- Required import command → `serve import OK`.

## Fail-first provenance (receipts, not re-executed now)

- c0 receipt `receipt-harness-backend-dev-2026-09-17-23-eng-T-27-c0.md:14-17`: endpoint case failed before the production edit, `AssertionError: 200 != 500`, one test.
- c1 receipt `receipt-harness-backend-dev-2026-09-17-23-eng-T-27-c1.md:17-21`: collector fixture failed before correction with missing `collect_fleet`; then passed 10 assertions. These are credible fail-first records for the two changed fixture paths.

## Finding

- **T-27 — severity: high; kind: substance.** No focused fixture establishes a state where **all sources are unreadable** and `/api/work?repo=all` returns 500. The only absent-clone default request deliberately asserts 200 because the harness control rows remain readable (`test-metrics-dashboard.py:307-311`); selected-absent and invalid-config 500 cases are distinct (`:312-314`, `:301-305`). Failure scenario: a future change can degrade every configured source or suppress the last readable control source while returning an empty/successful `repo=all` payload; both current fixtures remain green because neither creates nor asserts the all-unreadable condition. Add a named all-unreadable endpoint fixture asserting 500 before this gate can pass.

## Matrix

- T-27 literal amended verify was cross-checked and its two commands were executed exactly.
- `must_fix`: the all-unreadable endpoint coverage above.

## Gate handoff

```yaml
VERDICT: FAIL
findings:
  - task: T-27
    severity: high
    kind: substance
    failure_scenario: A repo=all request can return a successful empty payload when every source is unreadable; no current fixture creates or rejects that state.
must_fix:
  - Add a named all-unreadable endpoint fixture asserting /api/work?repo=all returns 500.
fail_first:
  - sc: SC-25
    evidence: notes/receipt-harness-backend-dev-2026-09-17-23-eng-T-27-c0.md:14-17
  - sc: SC-25
    evidence: notes/receipt-harness-backend-dev-2026-09-17-23-eng-T-27-c1.md:17-21
```
