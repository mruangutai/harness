# FEAT-65 QA matrix gate — cycle 0

## Verdict

**FAIL.** The pinned matrix is green and both required kinds are present, but no retained, SC-bound pre-fix failing run proves fail-first for any automated criterion. Green current tests do not earn the red-first gate.

## Phase 1 expectations (source-blind)

From `BRIEF.md` and `plan.yaml` alone, the gate requires: integration proof of preserved hook output/exit bytes (SC-01), canonical guarded diagnostics and existing verdicts (SC-02), typed boundaries plus unexpected-defect and process-control escape behavior (SC-03), unit census and named increase mutants (SC-04), unit five-copy prologue lock and per-copy mutants (SC-05), unit loud/nonzero direct `feature-record.py` failure (SC-09), and integration loud/nonzero direct `inflight_registry.py` failure (SC-10). SC-06–SC-08 are inspection-owned.

## Pinned matrix execution

Review SHA: `75a36628079ab1b37f7bd53f3100bde7305a8133`.

| Required kind | Command run in pinned checkout | Discovery | Result |
|---|---|---:|---|
| unit | `.agents/skills/harness/bin/run-unit-tests.py --kind unit` | 42 files | pass (exit 0) |
| integration | `.agents/skills/harness/bin/run-unit-tests.py --kind integration` | 69 files | pass (exit 0) |

All T-01–T-04 tasks declare `change_type: cross_module`; `.harness/harness.json:174-178` therefore requires **unit and integration**. Both active commands are configured at `.harness/harness.json:285-289,320-324` and both exercised the change-specific suites. `matrix_ok: true`.

## Literal verify reconciliation

- **T-01:** its eight named `test-check-domain*.py` integration suites are discovered and green; the clean-pin receipt records each at `notes/clean-pin-byte-receipts.md:11-18`.
- **T-02:** `test-validate-digest.py` (integration) and `test-code-grade.py` (unit) are discovered and green; receipt lines 19-20.
- **T-03:** its eight named integration suites plus `test-feature-record.py` (unit) are discovered and green; receipt lines 21-29.
- **T-04:** `test-broad-catch-census.py` and `test-harness-boundary.py` are discovered and green; receipt lines 30-31.

## SC evidence and fail-first audit

| SC | Current covering test(s) | Fail-first evidence | Gate |
|---|---|---|---|
| SC-01 | `tests/integration/test-check-domain.py:50-88`, `test-validate-digest.py:5562-5593`, `test-bash-write-guard.py:1120-1160`, `test-dispatch-guard.py:366-395`, `test-merge-gate.py:294-307`; byte receipt `notes/byte-evidence-vs-baseline.md:12-275` | **Missing.** No retained pre-fix failing command/output bound to these tests. | fail |
| SC-02 | Same guarded-hook suites; e.g. `tests/integration/test-check-domain.py:74-88`, `test-merge-gate.py:294-307` | **Missing.** | fail |
| SC-03 | `tests/integration/test-check-domain.py:50-88`, `test-validate-digest.py:5562-5593`, `test-dispatch-guard.py:366-395`, `test-bash-write-guard.py:1120-1160`, `test-merge-gate.py:294-307` | **Missing.** | fail |
| SC-04 | `tests/unit/test-broad-catch-census.py:106-121` | **Missing.** The live mutation checks are green, but no retained pre-fix red run exists. | fail |
| SC-05 | `tests/unit/test-broad-catch-census.py:140-156` | **Missing.** | fail |
| SC-09 | `tests/unit/test-feature-record.py` (current unit runner); named current behavior in `notes/build-divergences.md:161-162` | **Missing.** | fail |
| SC-10 | `tests/integration/test-inflight-registry.py:1262-1280` | **Missing.** | fail |
| SC-06–SC-08 | inspection-owned | not automated | n/a |

`runs/build-main-direct/digest.md:48-51` says T-03/T-04 had a “red” phase and that all task chains later passed, but names neither the failing test nor the command/output. It is not concrete fail-first evidence for any SC; neither are the green receipts at `notes/clean-pin-byte-receipts.md:9-31`.

## Finding

- **QA-65-01 — fail-first gate is unearned.**
  - **SC:** SC-01, SC-02, SC-03, SC-04, SC-05, SC-09, SC-10
  - **Location:** `runs/build-main-direct/digest.md:48-51`; absent from all five shared evidence artifacts.
  - **Defect/failure scenario:** A newly added assertion can pass at the review pin even if it never failed against the targeted old behavior; a green runner then proves only present compatibility, not that the asserted mutation/regression is detectable.
  - **Remedy:** Retain one pre-fix failing execution per automated SC, naming the exact covering test and failing assertion (or an equivalent receipt line), then retain the corresponding green post-fix result.
  - **Kind:** substance
  - **Severity:** high
  - **Owned tasks:** T-01/T-02/T-03/T-04

## Coverage gaps

No Phase-1 behavior is untested at the review pin. The sole gap is the mandatory fail-first receipt for every automated SC.

## Principles applied

- **Build the Lever:** executed the configured per-kind runner rather than sampling individual test files; its actual discovery sets establish the matrix result.
