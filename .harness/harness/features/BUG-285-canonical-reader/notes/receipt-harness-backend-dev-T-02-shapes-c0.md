# PASS — strict value and source contracts are complete

Changed `.claude/skills/harness/bin/artifact_accessors.py`, `.claude/skills/harness/bin/feature_json_write.py`, `tests/unit/test-artifact-accessors.py`, and `tests/unit/test-feature-json-reader.py`. `parse_gh_json` now returns any strict JSON value; feature JSON supports exactly one path or keyword-only text source through one strict parsing and validation path.

Fail-first proof: before production edits, `python3 tests/unit/test-artifact-accessors.py && python3 tests/unit/test-feature-json-reader.py` failed in `test_github_json_accepts_any_strict_json_value` because list/scalar values raised `ArtifactAccessError: ... JSON document is not a mapping`; the focused feature reader run then failed because `load_feature_json()` required `path` and rejected keyword `text`.

Exact signed T-02 verify command passed: `python3 tests/unit/test-artifact-accessors.py && python3 tests/unit/test-feature-json-reader.py && python3 tests/integration/test-gh-sync-open.py && python3 tests/integration/test-factory-decompose.py && python3 tests/integration/test-harness-yaml.py && python3 tests/unit/test-factory-config.py && python3 tests/integration/test-sync-agent-adapters.py && python3 tests/integration/test-upgrade-config.py` (all component suites passed; reported 12, 22, 179/179, 115/115, 18/18, and 12/12 checks where counts are emitted). `task_verify: pass`.

Scope boundary: no GitHub consumer or T-03 path was modified; no temporary bridge, accessor, alias, or reader file was added; no commit was made.
