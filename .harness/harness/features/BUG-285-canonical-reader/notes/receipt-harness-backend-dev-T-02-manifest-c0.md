# T-02 manifest domains receipt

BLUF: `manifest_domains(path, agent=None)` now aggregates dynamically discovered named-role write domains while retaining explicit-agent delegation; focused coverage passes, but the signed T-02 verification is blocked by pre-existing partial T-03 work in `gh_issue_types.py`.

## TDD evidence

- Fail-first command: `python3 tests/unit/test-artifact-accessors.py`
- Observed failure: `TypeError: manifest_domains() missing 1 required positional argument: 'agent'` from `test_omitted_agent_aggregates_named_role_writes_only`; 13 tests ran, exit 1.
- Focused green command: `python3 tests/unit/test-artifact-accessors.py`
- Result: 13 tests ran, `OK`, exit 0.

## Signed verification

Exact command (unchanged):

```sh
python3 tests/unit/test-artifact-accessors.py && python3 tests/unit/test-feature-json-reader.py && python3 tests/integration/test-gh-sync-open.py && python3 tests/integration/test-factory-decompose.py && python3 tests/integration/test-harness-yaml.py && python3 tests/unit/test-factory-config.py && python3 tests/integration/test-sync-agent-adapters.py && python3 tests/integration/test-upgrade-config.py
```

Exit: 1. Executed scripts: `test-artifact-accessors.py` (13 tests, OK), `test-feature-json-reader.py` (22 tests, OK), and `test-gh-sync-open.py` (no aggregate discovery/execution count reported before abort). The third script failed because `gh-sync.py` calls missing `gh_issue_types.classify_capability`, producing `AttributeError` at `gh-sync.py:963`; remaining `&&` scripts did not execute.

## Scope and protected work

Implementation files changed: `.claude/skills/harness/bin/artifact_accessors.py`, `tests/unit/test-artifact-accessors.py`.

Architecture: the existing public `manifest_domains` accessor seam gained the omitted/`None` aggregation mode directly; no new public seam, parser, exemption, role list, alias, or re-export was introduced. Explicit agents still delegate unchanged to `harness_yaml.manifest_domains`.

Protected-path SHA-256 comparison: all 23 pre-existing modified paths outside the two permitted implementation/test paths matched their pre-edit hashes byte-for-byte after every command. This includes the partial T-03 files, notably `.claude/skills/harness/bin/gh-sync.py` (`d97c31ccf3d3b8f304294a9770c7e9dbf9342a5dc7c6134c3ffc09bf66eacf3b`) and `.claude/skills/harness/bin/gh_issue_types.py` (`c6d50580a5a58dff8b240cb5aeb601ba1b1adc63c427c2925fe498b3813b8c7b`).
