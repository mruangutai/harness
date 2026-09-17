# T-07 c1 receipt — zero-Python grading repair

## BLUF

`grading.distribution()` now invokes the genuine `code-grade.py` diff mode with identical existing `--base` and `--head` revisions when a requested project has no tracked Python paths, returning its real empty payload while retaining tracked-file `file_mix`.

## Fail-first evidence

Before the repair, the new real-subprocess `project-a` regression removes the fixture's only tracked `probe.py` and invokes `grading.distribution()`. It failed with:

```
usage: code-grade.py [-h] [--base BASE] [--head HEAD] [--json] [paths ...]
code-grade.py: error: provide PATH... or both --base REF and --head REF
```

The exact pre-fix verify ran 19 tests and failed only `test_grading_distribution_runs_real_cli_with_no_tracked_python_paths` with that error.

## Post-fix proof

The zero-Python regression executes the real CLI without mocked grading subprocesses, confirms the genuine empty grade payload, and independently counts tracked files for `file_mix`. The existing Python-path real-CLI regression remains green.

Exact T-07 verify:

```
...................
----------------------------------------------------------------------
Ran 19 tests in 3.227s

OK
```

- Commit: `eaf026d1` (`[harness:t-07] handle zero Python grading inputs`)
- Changed files: `.claude/skills/harness/bin/dashboard/grading.py`, `tests/unit/test-metrics-kpi.py`

## DEC-229 amendment

- task: `T-07`
- field: `intent`
- was: `python3 <harness bin>/code-grade.py --json <every tracked .py path in project_root> obtained from git -C project_root ls-files.`
- now: `python3 <harness bin>/code-grade.py --json <every tracked .py path in project_root> obtained from git -C project_root ls-files; when no tracked Python path exists, invoke code-grade.py through a valid real empty mode using both --base and --head at the same existing revision, never synthesize its payload.`
- reason: `The current CLI rejects an empty PATH list, and project-a legitimately tracks no Python files.`
- all success criteria, task set, decisions, files, and verify remain unchanged.
