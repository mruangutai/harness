# QA gate — PASS

Both configured suites passed from the assigned worktree. Each invocation set `PATH=/opt/homebrew/bin:$PATH`, selecting Homebrew Python for the runner; the runner invokes `python3` to resolve its root and execute every registered script (`.claude/skills/harness/bin/run-unit-tests.sh:11,150`).

## Executed commands

- `PATH=/opt/homebrew/bin:$PATH .agents/skills/harness/bin/run-unit-tests.sh --kind unit` — exit 0; 29 registered scripts discovered (`run-unit-tests.sh:30`), including `test-code-grade.py`; its contract completed as `PASS test-code-grade`.
- `PATH=/opt/homebrew/bin:$PATH .agents/skills/harness/bin/run-unit-tests.sh --kind integration` — exit 0; 28 registered scripts discovered (`run-unit-tests.sh:31-32`), including `test-code-grade-cli.py`, `test-validate-digest.py`, and `test-check-plan-routes.py`; each completed PASS.

## Changed-surface coverage

- `code_grade.py` is covered by 12 hand-derived grade fixtures and all-band set equality, direction pairs, change-set resolution, worked examples, and delivery assertions (`test-code-grade.py:24-54,374-407`).
- `code-grade.py` is covered through subprocess tests of fields, bars, exits, parse failure, determinism, and configured test classification (`test-code-grade-cli.py:64-105,108-116,187-282`).
- `validate-digest.py` is covered by the reviewer-grade state probe: PASS-compatible `code_grade: grade_2` with `[one auditable reason]`, rejection without `grade_2_reasons`, and rejection of `code_grade: fail` with PASS (`test-validate-digest.py:1767-1777`); the validator enforces those conditions (`validate-digest.py:774-782`).
- `check-plan-routes.py` is covered by owner-manifest/deviation refusal, prior-revision false-OK discrimination, and unreadable-owner refusal (`test-check-plan-routes.py:1411-1460`), exercising owner resolution (`check-plan-routes.py:91-112,775-818`).

The grade-2 digest requirement is non-vacuous: `grade_2` needs a non-empty list of non-blank reasons (`validate-digest.py:774-779`), while `fail` remains incompatible with `VERDICT: PASS` (`validate-digest.py:780-782`). The CLI independently proves grade 2 exits 0 while still emits `REASON REQUIRED`, and grade 1 remains blocking (`test-code-grade-cli.py:96-104`).

No changed test or source surface lacks a named, executed contract. Matrix adequacy: T-01/T-02/T-06/T-07 are `logic` (unit required); T-03/T-08/T-09 include integration, with T-08 `cross_module` requiring both. Both active required kinds ran and their explicit registrations are guarded by runner drift/cross-kind checks (`run-unit-tests.sh:56-141`).
