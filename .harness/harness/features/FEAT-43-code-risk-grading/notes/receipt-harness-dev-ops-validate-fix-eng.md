# CLI grading validation — FEAT-43

CLI grading now reads NUL-delimited, status-aware diffs, excludes deleted Python paths, emits deterministic path order, labels cognitive complexity as a Sonar-style approximation in text and JSON, and reports each record's bar and result.

## Changed files

- `.claude/skills/harness/bin/code-grade.py`
- `.claude/skills/harness/bin/test-code-grade-cli.py`

## Test-first evidence

RED command:

```sh
/opt/homebrew/bin/python3 .claude/skills/harness/bin/test-code-grade-cli.py
```

Result: exit 1. Missing cognitive qualification, `BAR`, and `RESULT` text fields; JSON lacked `cognitive_method`.

GREEN command:

```sh
/opt/homebrew/bin/python3 .claude/skills/harness/bin/test-code-grade-cli.py
```

Exact result: `PASS test-code-grade-cli` (exit 0).

The subprocess tests exercise real CLI path grading, grade-2 actionability (`REASON REQUIRED`), deletion omission, a tab-to-newline rename, and equivalent output/exit codes after reversed file-creation enumeration.

## Owned-function grade audit

```sh
/opt/homebrew/bin/python3 .claude/skills/harness/bin/code-grade.py .claude/skills/harness/bin/code-grade.py .claude/skills/harness/bin/test-code-grade-cli.py
```

Result: 19 passing records; exit 1 because two grade-2 records require actionability. No grade-1 record remains.

- `code-grade.py:main` — grade 2, ABC 27.3: existing CLI argument parsing/dispatch/reporting orchestration.
- `test-code-grade-cli.py:test_diff_and_determinism` — grade 2, ABC 29.2: explicit fixture setup for deletion, tab/newline rename, and reverse-enumeration smoke cases.

The new `_diff_paths` function is grade 3 (cognitive 11), not grade 1. The broad plan verification command was intentionally not run per assignment constraint.
