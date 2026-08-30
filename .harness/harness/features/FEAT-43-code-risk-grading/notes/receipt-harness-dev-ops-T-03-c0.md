# T-03 receipt — FAIL

The CLI contract tests pass, but T-03's required integration command fails in this checkout because its pre-existing hook tests invoke `python3 -P`, which this machine's Python 3.9 rejects. The implementation and its direct subprocess contract test are complete; this receipt does not claim broader validation.

## Test-first RED

Command:

```sh
python3 .claude/skills/harness/bin/test-code-grade-cli.py
```

Exit status: `1`

Output:

```text
FAIL path bar exit: expected 1, got 2
FAIL text field PATH: src/risk.py: expected True, got False
FAIL text field LINE: 1: expected True, got False
FAIL text field QUALNAME: grade_two: expected True, got False
FAIL text field CYCLOMATIC: 11: expected True, got False
FAIL text field COGNITIVE: 1: expected True, got False
FAIL text field ABC: 10.0: expected True, got False
FAIL text field GRADE: 2: expected True, got False
FAIL text field DRIVER: cyclomatic: expected True, got False
FAIL text field SEVERITY: med: expected True, got False
FAIL text field REASON REQUIRED: grade_two: expected True, got False
FAIL text field SEVERITY: high: expected True, got False
FAIL text field PASSING: 1: expected True, got False
FAIL json bar exit: expected 1, got 2
Traceback (most recent call last):
  ... json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)
```

## Scoped contract test after implementation

Command:

```sh
python3 .claude/skills/harness/bin/test-code-grade-cli.py
```

Exit status: `0`

Output:

```text
PASS test-code-grade-cli
```

## Required verification

Command (verbatim from `plan.yaml`):

```sh
.claude/skills/harness/bin/run-unit-tests.sh --kind integration
```

Exit status: `2`

Output: the runner executed `test-code-grade-cli.py` successfully (`PASS test-code-grade-cli`), then exited nonzero after existing integration tests failed. The failures repeatedly report `Unknown option: -P` from `/Library/Developer/CommandLineTools/.../python3`; the final runner error was `syntax error near unexpected token 'done'`. Full captured output is available at `artifact://59` in this run transcript.

## Scope

- Added CLI adapter and subprocess contract test.
- Registered `test-code-grade-cli.py` in `INTEGRATION_SCRIPTS` and `test_kinds.integration.detect`.
- Retained existing registrations; also added the already-listed `test-merge-gitignore.py` literal to `integration.detect` so the runner's mandatory kind cross-check advances past its pre-existing mismatch.
