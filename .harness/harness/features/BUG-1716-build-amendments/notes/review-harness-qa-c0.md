# QA c0 — pinned matrix gate

## Verdict

FAIL — the required unit matrix failed at `c2bf2f3a2ffba5faf243867a915f082da17f387d`; the integration matrix and all four task-scoped behavioural commands passed.

## Matrix

| Kind | State | Command | Evidence |
|---|---|---|---|
| unit | failed | `env -u HARNESS_AGENT_TYPE .agents/skills/harness/bin/run-unit-tests.py --kind unit` | exit 1: `test-code-grade.py` reports `FAIL validate-digest.py:_amendment_entry_errors grade >= 4: expected True, got False` |
| integration | satisfied | `env -u HARNESS_AGENT_TYPE .agents/skills/harness/bin/run-unit-tests.py --kind integration` | exit 0; includes passing BUG-1716 `test-plan-merge.py` cases |

Matrix floor: unit is required by T-02/T-03 (`api`), T-04 (`cross_module`), and T-05's runtime-code `bugfix` predicate; integration is required by T-04. No locally-run or excluded kind detects the changed surfaces.

## Scoped evidence

- `python3 tests/integration/test-validate-digest.py`: pass; amendment contract cases cover SC-01 at `tests/integration/test-validate-digest.py:603-651`.
- `python3 tests/unit/test-feature-record.py && python3 tests/integration/test-validate-feature-json.py`: pass; selected overrule and schema behaviour cover SC-04 at `tests/unit/test-feature-record.py:242-288` and SC-03 schema form at `tests/integration/test-validate-feature-json.py:519-555`.
- `env -u HARNESS_AGENT_TYPE python3 tests/integration/test-plan-merge.py`: pass; signing and record-amendments cover SC-02/SC-03 at `tests/integration/test-plan-merge.py:3633-3835`.
- `python3 tests/integration/test-check-state-feat59.py`: pass; signed-text INV-40 trigger covers SC-03 at `tests/integration/test-check-state-feat59.py:415-480`.

All changed executable units are meaningfully bound by the cited tests: `validate-digest.py` (T-02), `feature-record.py`/schema (T-03), `plan-merge.py` (T-04), and `check-state.py` (T-05).

## Fail-first evidence

| SC | Evidence |
|---|---|
| SC-01 | `notes/receipt-main-session-T-02-fail-first.md:6-24` — new amendment acceptance and validation cases failed against pre-change `cb26ae9e`. |
| SC-02 | `notes/receipt-main-session-T-04-fail-first.md:10-37` — record-amendments, byte-preservation, refusal, and approval-survival cases failed against pre-change `1fbf8471`. |
| SC-03 | `notes/receipt-main-session-T-04-fail-first.md:6-9` and `notes/receipt-main-session-T-05-fail-first.md:7-18` — signing hashes and unrecorded-text detection cases failed before their respective changes. |
| SC-04 | `notes/receipt-main-session-T-03-fail-first.md:6-13` — amendment kind, exact overrule selection, and refusal-without-write tests failed against pre-change `07424285`. |

SC-05 through SC-07 are inspection criteria and are not reported as automated coverage.

## Finding

- `QA-c0-01` — **kind:** substance; **severity:** med; **owner:** T-02. **Scenario:** an implementation that satisfies the new digest cases still cannot clear the repository's required unit quality gate because the added `validate-digest.py:_amendment_entry_errors` is below the production grade-4 bar. **Evidence:** unit matrix command above; `tests/unit/test-code-grade.py:264-300` sets that bar and `validate-digest.py:402-440` is the failing changed function.

## Coverage gaps

None. Phase-1 required behaviours for SC-01 through SC-04 are each bound by a changed, scoped test and have credible fail-first receipts. The gate fails solely on the required unit matrix failure above.
