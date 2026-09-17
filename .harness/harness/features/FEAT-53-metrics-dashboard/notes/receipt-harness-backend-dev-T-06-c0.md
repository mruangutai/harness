# T-06 receipt

KPI core now resolves only the supplied project root, routes all approval gaps through `brief_approval.approval_date`, and returns measured throughput/rework plus explicit unavailable placeholders.

## Red proof

Before production modules existed, `python3 tests/unit/test-metrics-kpi.py` exited 1 at `import kpi` with `ModuleNotFoundError: No module named 'kpi'`. The test already contained the named hand-labelled contract assertions for shipped values, four distinct approval-gap reasons, missing ship record, generated-at-relative window bounds, and parse-error unavailability.

## Amended task verify

```sh
python3 .claude/skills/harness/bin/run-unit-tests.py --check-layout && python3 tests/unit/test-metrics-kpi.py
```

Exit: 0

```text
.....
----------------------------------------------------------------------
Ran 5 tests in 0.296s

OK
```

## Targeted code-grade proof

```sh
python3 /Users/molchairuangutai/GitHub/harness/.claude/skills/harness/bin/code-grade.py .claude/skills/harness/bin/dashboard/kpi.py .claude/skills/harness/bin/brief_approval.py tests/unit/test-metrics-kpi.py
```

Exit: 0. All 29 graded functions passed their bar; production functions are grade 4 or higher and test functions grade 3 or higher.

## Files and commit

Touched: `.claude/skills/harness/bin/dashboard/kpi.py`, `.claude/skills/harness/bin/brief_approval.py`, `tests/unit/test-metrics-kpi.py`, and `.claude/skills/harness/bin/dashboard/fixtures/project-a/`.

Commit: `63cb3485d883522e86a83ab68d2616c07352d727` (`[harness:t-06] Build KPI core`).
