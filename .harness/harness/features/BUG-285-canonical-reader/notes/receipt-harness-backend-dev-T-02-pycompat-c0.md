# T-02 receipt — system Python import compatibility

**Result: FAIL — implementation and all signed scripts pass, but a protected concurrent dirty-path hash changed after the pre-edit inventory.**

## System-Python regression proof

- Focused command (RED and GREEN):
  `python3 tests/unit/test-artifact-accessors.py SystemPythonCompatibilityContracts.test_macos_system_python_imports_typed_manifest_records`
- Actual interpreter: `/usr/bin/python3`, `Python 3.9.6`.
- RED: exit 1; 1 test ran, 1 failure. Exact pre-fix error:
  `TypeError: unsupported operand type(s) for |: 'types.GenericAlias' and 'NoneType'`
  from `ManifestDomainsView.main_session_writes` while importing the real accessor path.
- GREEN: exit 0; 1 test ran, `OK`.

## Correction and architecture

- Changed `.claude/skills/harness/bin/artifact_accessors.py` and `tests/unit/test-artifact-accessors.py` only (besides this receipt).
- `from __future__ import annotations` postpones evaluation of the existing signed typed record annotations. It retains the `tuple[str, ...] | None` typed API, frozen dataclasses, dependency-light/lazy imports, and all manifest behavior without a shim, dependency, or untyped substitute.

## Signed T-02 verification

- Exact command (worktree root):
  `python3 tests/unit/test-artifact-accessors.py && python3 tests/unit/test-feature-json-reader.py && python3 tests/integration/test-gh-sync-open.py && python3 tests/integration/test-factory-decompose.py && python3 tests/integration/test-harness-yaml.py && python3 tests/unit/test-factory-config.py && python3 tests/integration/test-sync-agent-adapters.py && python3 tests/integration/test-upgrade-config.py`
- Exit: 0; all 8 scripts passed. Reported totals: accessor 19 tests `OK`; feature reader 22 tests `OK`; gh-sync `ALL PASSED`; factory-decompose 179/179; harness-yaml listed all cases `ok`; factory-config 116/116; sync-agent-adapters 18/18; upgrade-config 12/12.

## Protected dirty-path inventory

- Before edits, SHA-256 inventory contained 29 dirty paths outside the two owned source/test files.
- Final comparison: 28 hashes matched; `tests/integration/test-merge-gate.py` changed concurrently (pre-edit SHA-256 `977ded2d3d9b7dee9247608e253339ce4315083e5f4ca9a941ef923a76521c8c`). This fails the requested all-protected-path match condition; no protected path was edited by this task.
