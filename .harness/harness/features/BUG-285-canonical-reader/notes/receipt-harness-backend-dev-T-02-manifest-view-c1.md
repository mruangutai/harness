# T-02 manifest view c1 receipt

BLUF: The typed manifest view now emits every first-seen named role, including roles without a usable domain, while preserving duplicate aggregation and strict YAML error types.

- Plan cross-check: T-02 and its `verify:` command exactly matched `plan.yaml` lines 187-232 and 209-210.
- Fail-first command: `python3 tests/unit/test-artifact-accessors.py` exited 1. `Ran 18 tests in 0.041s`; `test_view_keeps_named_roles_with_missing_or_invalid_domains` failed because the view returned only `aggregate`, omitting `missing` and `invalid` records.
- Focused green: `python3 tests/unit/test-artifact-accessors.py` exited 0; `Ran 18 tests in 0.039s`, `OK`.
- Strict YAML assertions: duplicate YAML raises `harness_yaml.DuplicateKeyError`; malformed, unreadable, non-UTF-8, and non-mapping inputs each raise `harness_yaml.YamlParseError`; no production wrapping was added.
- Signed command (unchanged): `python3 tests/unit/test-artifact-accessors.py && python3 tests/unit/test-feature-json-reader.py && python3 tests/integration/test-gh-sync-open.py && python3 tests/integration/test-factory-decompose.py && python3 tests/integration/test-harness-yaml.py && python3 tests/unit/test-factory-config.py && python3 tests/integration/test-sync-agent-adapters.py && python3 tests/integration/test-upgrade-config.py`
- Signed result: exit 0. Script results: artifact accessors PASS (18 tests); feature JSON PASS (22 tests); GH sync open PASS (`ALL PASSED`, no aggregate count); factory decompose PASS (179/179); harness YAML PASS (individual `ok` results, no aggregate count); factory config PASS (116/116); sync adapters PASS (18/18); upgrade config PASS (12/12).
- Protected dirty paths: SHA-256 inventory before edits and after verification covered 27 non-owned dirty paths; all 27 paths and hashes matched exactly.
- Files changed: `.claude/skills/harness/bin/artifact_accessors.py`; `tests/unit/test-artifact-accessors.py`.
- Architecture: the existing `manifest_domains(view=True)` traversal now initializes a named role before considering its domain; no accessor, model, parser, callback, exemption, enum, or policy grammar was added. The typed records, one-load behavior, legacy `view=False` paths, and public `TypeError` remain unchanged.
