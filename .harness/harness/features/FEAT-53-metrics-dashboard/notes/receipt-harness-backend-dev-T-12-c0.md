# T-12 receipt

## Verdict

BLOCKED — T-12's approved verification and integration-registration contract points to a retired runner, so its exact required command cannot execute and no compatible registration surface exists.

## Evidence

Pre-edit worktree status contained only sibling-generated client dist changes and a pre-existing feature state change; no T-12 source or test file exists. `serve.py`, `test-metrics-dashboard.py`, and `run-unit-tests.sh` are absent from their T-12 paths.

The exact planned verification command was run before any task implementation:

```text
$ bash .claude/skills/harness/bin/run-unit-tests.sh --check-kinds && python3 .claude/skills/harness/bin/test-metrics-dashboard.py
bash: .claude/skills/harness/bin/run-unit-tests.sh: No such file or directory

exit: 127
```

The live replacement `.claude/skills/harness/bin/run-unit-tests.py` documents `WAS A .sh ENTRY POINT (issue #1674)` and accepts only `--kind` or `--check-layout`; it has no `--check-kinds` option, no `INTEGRATION_SCRIPTS` registry, and executes only `tests/unit/test-*.py` and `tests/integration/test-*.py`. Thus creating the planned script would reverse the live native-runner cutover, while adding the named standalone bin test cannot satisfy the required registration instruction.

No fail-first test was written: the planned test's discovery/registration mechanism is unavailable, and production code before a valid failing test would violate TDD.

## DEC-229-eligible stale-path amendments

- task: T-12; field: files; was: `.claude/skills/harness/bin/run-unit-tests.sh`; now: `.claude/skills/harness/bin/run-unit-tests.py`; reason: issue #1674 retired the shell entry point in favor of the native runner.
- task: T-12; field: verify; was: `bash .claude/skills/harness/bin/run-unit-tests.sh --check-kinds && python3 .claude/skills/harness/bin/test-metrics-dashboard.py`; now: needs an approved command compatible with `run-unit-tests.py` and its directory-based integration discovery; reason: the old executable and `--check-kinds` flag do not exist.
- task: T-12; field: intent; was: register `test-metrics-dashboard.py` in `run-unit-tests.sh INTEGRATION_SCRIPTS`; now: needs an approved test location and native-runner discovery contract; reason: the native runner has no integration-script registry and only discovers `tests/integration/test-*.py`.

## Required resolution

Amend T-12's `files`, `verify`, and test-registration/test-path intent to the native runner contract, then redispatch. No implementation changes were made, no generated client dist was staged, and no trend write path was touched.
