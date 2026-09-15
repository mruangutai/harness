# T-02 pycompat rebaseline receipt — cycle 1

**Result: PASS — focused proof and all signed scripts passed; every protected cycle-start hash remained stable.**

## Inputs cross-checked

- Assessment: `runs/2026-09-15-t02-pycompat-eng/assessment-c0.md`.
- Cycle-0 TDD evidence: `notes/receipt-harness-backend-dev-T-02-pycompat-c0.md` (its recorded RED then GREEN system-Python proof).
- `plan.yaml` T-02 `verify:` exactly matches the signed command below.

## Focused system-Python proof

- Command: `python3 tests/unit/test-artifact-accessors.py SystemPythonCompatibilityContracts.test_macos_system_python_imports_typed_manifest_records`
- Actual `/usr/bin/python3`: `Python 3.9.6`.
- Focused command interpreter: `python3` reported `Python 3.14.5`.
- Exit: 0; reported count: `Ran 1 test`; `OK`.

## Signed T-02 verification

- Exact command:
  `python3 tests/unit/test-artifact-accessors.py && python3 tests/unit/test-feature-json-reader.py && python3 tests/integration/test-gh-sync-open.py && python3 tests/integration/test-factory-decompose.py && python3 tests/integration/test-harness-yaml.py && python3 tests/unit/test-factory-config.py && python3 tests/integration/test-sync-agent-adapters.py && python3 tests/integration/test-upgrade-config.py`
- Exit: 0.
- Reported script results: artifact-accessors `19 tests OK`; feature-json-reader `22 tests OK`; gh-sync-open `ALL PASSED` (no aggregate count reported); factory-decompose `179/179`; harness-yaml all named cases `ok` (no aggregate count reported); factory-config `116/116`; sync-agent-adapters `18/18`; upgrade-config `12/12`.

## Protected dirty-path rebaseline

- Cycle-start inventory: 31 dirty paths, excluding this c1 receipt.
- Post-gate comparison: 31/31 SHA-256 hashes identical.
- `tests/integration/test-merge-gate.py` was included as authorized concurrent T-06 baseline and remained stable: `977ded2d3d9b7dee9247608e253339ce4315083e5f4ca9a941ef923a76521c8c`.
- Source/test edits by this verification cycle: zero.
