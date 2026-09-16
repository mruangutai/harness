# T-02 receipt — harness-backend-dev

## Result
PASS — `artifact_accessors.py` supplies the dependency-light public seam; malformed-present GitHub and factory receipt fields now refuse before issue creation.

## Fail-first evidence
Before production edits:
- `python3 tests/unit/test-artifact-accessors.py` exited 1: `ModuleNotFoundError: No module named 'artifact_accessors'`.
- `python3 tests/unit/test-feature-json-reader.py` exited 1: `test_nonfinite_constants_raise` failed for `NaN`, `Infinity`, and `-Infinity`.
- `python3 tests/integration/test-gh-sync-open.py` exited 1: wrong parent and wrong issues both created GitHub issues.
- `python3 tests/integration/test-factory-decompose.py` exited 1: wrong parent and wrong issues both created factory task issues.

## Verification
Exact command (worktree root):
```sh
python3 tests/unit/test-artifact-accessors.py && python3 tests/unit/test-feature-json-reader.py && python3 tests/integration/test-gh-sync-open.py && python3 tests/integration/test-factory-decompose.py && python3 tests/integration/test-harness-yaml.py && python3 tests/unit/test-factory-config.py && python3 tests/integration/test-sync-agent-adapters.py && python3 tests/integration/test-upgrade-config.py
```
Exit result: `0`.

Observable #1682 consumer proof: both real consumers' regressions report `BUG-285 wrong parent refuses before parent or task issue creation` and `BUG-285 wrong issues refuses before parent or task issue creation`; no create call is reached.

## Files touched
- `.claude/skills/harness/bin/artifact_accessors.py`
- `.claude/skills/harness/bin/feature_json_write.py`
- `.claude/skills/harness/bin/gh-sync.py`
- `.claude/skills/harness/bin/factory_decompose.py`
- `.claude/skills/harness/bin/upgrade-config.py`
- `tests/unit/test-artifact-accessors.py`
- `tests/unit/test-feature-json-reader.py`
- `tests/integration/test-gh-sync-open.py`
- `tests/integration/test-factory-decompose.py`

## Scope exclusions
No T-03/T-04 callers, enforcement-layer source/tests, canonical classification artifact, T-05–T-07 paths, formatters, linters, builds, project-wide suites, or commits.

Artifact: this receipt.
