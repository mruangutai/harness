# T-02 manifest view receipt

BLUF: `manifest_domains(path, agent=None, *, view=False)` now offers its immutable one-load typed view without adding another accessor seam; all signed scripts passed.

- Plan cross-check: T-02 verify command exactly matched `plan.yaml` lines 209-210.
- RED: `python3 tests/unit/test-artifact-accessors.py` exited 1; `Ran 16 tests in 0.036s`, with 3 expected errors: `TypeError: manifest_domains() got an unexpected keyword argument 'view'`.
- Focused GREEN: `python3 tests/unit/test-artifact-accessors.py` exited 0; `Ran 17 tests in 0.039s`, `OK`.
- One-load evidence: `test_view_returns_immutable_ordered_role_records_and_reads_once` wraps `harness_yaml.load_file` and asserts call count 1.
- Signed command (unchanged): `python3 tests/unit/test-artifact-accessors.py && python3 tests/unit/test-feature-json-reader.py && python3 tests/integration/test-gh-sync-open.py && python3 tests/integration/test-factory-decompose.py && python3 tests/integration/test-harness-yaml.py && python3 tests/unit/test-factory-config.py && python3 tests/integration/test-sync-agent-adapters.py && python3 tests/integration/test-upgrade-config.py`
- Aggregate signed exit: 0. Script results: artifact accessors PASS (17 tests); feature JSON PASS (22 tests); GH sync open PASS (`ALL PASSED`, no reported aggregate count); factory decompose PASS (179/179); harness YAML PASS (individual `ok` results, no reported aggregate count); factory config PASS (116/116); sync adapters PASS (18/18); upgrade config PASS (12/12).
- Protected dirty paths: SHA-256 inventory before edits and after all verification covered 27 non-owned dirty paths; every path and hash matched, including T-06 files and observations.
- Changed implementation/test files: `.claude/skills/harness/bin/artifact_accessors.py`; `tests/unit/test-artifact-accessors.py`.
- Architecture: the established `manifest_domains` accessor seam gained a keyword-only typed view depth; no second accessor, raw mapping, parser, model, callback, enum, exemption, or policy grammar was introduced.
