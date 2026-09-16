# T-02 cycle-1 receipt — public accessor boundary

## Conclusion

`artifact_accessors.load_feature_json` is the sole public feature.json read seam for both real consumers. Its inward implementation now rejects malformed present `github`/`factory` recorded parent and issues values before either consumer can create objects; absent blocks and numeric-string coercion remain valid.

## Debug evidence

Hypothesis: malformed recorded parent/issues values reached `load_feature_json` because validation existed only in consumer-specific conversion code. Falsifier: a public-seam regression would raise before either consumer was called.

RED, before the production repair:

```text
$ python3 tests/unit/test-artifact-accessors.py
.FFFF.....
FAILED (failures=4)
AssertionError: Exception not raised
```

The four failing public-seam subtests were `github.parent: true`, `github.issues: []`, `factory.parent: "not-a-number"`, and `factory.issues: []`.

GREEN after the repair:

```text
$ python3 tests/unit/test-artifact-accessors.py
.......
Ran 7 tests
OK
```

## Signed verification

Command run from the worktree root:

```sh
python3 tests/unit/test-artifact-accessors.py && python3 tests/unit/test-feature-json-reader.py && python3 tests/integration/test-gh-sync-open.py && python3 tests/integration/test-factory-decompose.py && python3 tests/integration/test-harness-yaml.py && python3 tests/unit/test-factory-config.py && python3 tests/integration/test-sync-agent-adapters.py && python3 tests/integration/test-upgrade-config.py
```

Exit status: `0`.

Verbatim suite summaries:

```text
.......
Ran 7 tests in 0.034s
OK
....................
Ran 20 tests in 0.004s
OK
ALL PASSED
179/179 checks passed.
114/114 checks passed.
18/18 cases passed
12/12 cases passed.
```

The gh-sync and factory-decompose integration output each includes passing `BUG-285 wrong parent refuses before parent or task issue creation` and `BUG-285 wrong issues refuses before parent or task issue creation` checks.

## Files touched

- `.claude/skills/harness/bin/feature_json_write.py`
- `.claude/skills/harness/bin/gh-sync.py`
- `.claude/skills/harness/bin/factory_decompose.py`
- `tests/unit/test-artifact-accessors.py`
- `tests/unit/test-feature-json-reader.py`
- `.harness/harness/features/BUG-285-canonical-reader/notes/receipt-harness-backend-dev-T-02-c1.md`
