# Simplification apply receipt — BUG-285-canonical-reader

**Task:** T-02  
**Finding:** SIMP-01  
**Owner:** harness-backend-dev

## Result

Applied SIMP-01 by deleting only the obsolete two-line BUG-285 migration-history comment in `.claude/skills/harness/bin/factory_decompose.py` (former lines 115–116). The accessor call, executable bytes, tests, and assertions were not changed.

**Owner rationale:** T-02 names `harness-backend-dev` as its execution agent, and this finding is confined to the task's `factory_decompose.py#load_factory` surface.

## Signed verification

Command (run as one shell command):

```sh
python3 tests/unit/test-artifact-accessors.py && python3 tests/unit/test-feature-json-reader.py && python3 tests/integration/test-gh-sync-open.py && python3 tests/integration/test-factory-decompose.py && python3 tests/integration/test-harness-yaml.py && python3 tests/unit/test-factory-config.py && python3 tests/integration/test-sync-agent-adapters.py && python3 tests/integration/test-upgrade-config.py
```

**Exit/result evidence:** exit 0. The command completed all eight scripts successfully; reported terminal summaries include `Ran 19 tests ... OK`, `Ran 22 tests ... OK`, `ALL PASSED`, `179/179 checks passed.`, `116/116 checks passed.`, `18/18 cases passed`, and `12/12 cases passed.`

## Revert status

Not reverted: signed verification passed on the first run, so no repair was attempted.
