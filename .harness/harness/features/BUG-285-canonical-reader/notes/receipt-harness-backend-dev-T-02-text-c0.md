# T-02 text-source receipt

PASS — `load_harness_json` now accepts exactly one source: its existing path or keyword-only text. Both reach `_parse_json_text`, preserving strict duplicate-key/non-finite/mapping checks and `ArtifactAccessError` context.

- Fail-first: `python3 tests/unit/test-artifact-accessors.py && python3 tests/unit/test-factory-config.py` exited 1 before production edits. `load_harness_json(..., text=..., context=...)` raised `TypeError: load_harness_json() got an unexpected keyword argument 'text'`; the no-source form also raised the prior missing-path `TypeError`.
- Green focused proof: the same command exited 0 after the implementation (10 accessor tests; 115 factory-config checks).
- Exact task verify: `python3 tests/unit/test-artifact-accessors.py && python3 tests/unit/test-feature-json-reader.py && python3 tests/integration/test-gh-sync-open.py && python3 tests/integration/test-factory-decompose.py && python3 tests/integration/test-harness-yaml.py && python3 tests/unit/test-factory-config.py && python3 tests/integration/test-sync-agent-adapters.py && python3 tests/integration/test-upgrade-config.py` exited 0.
- Task verify: pass.
- T-03 boundary: `factory_config.py` has no diff; the factory-config addition proves its remote decoded-text consumer input through the accessor only. Production repointing was not started.
- Scope qualification: observed pre-existing changes to feature `STATE.md` and `feature.json`; untouched.

Files changed: `.claude/skills/harness/bin/artifact_accessors.py`, `tests/unit/test-artifact-accessors.py`, `tests/unit/test-factory-config.py`.
