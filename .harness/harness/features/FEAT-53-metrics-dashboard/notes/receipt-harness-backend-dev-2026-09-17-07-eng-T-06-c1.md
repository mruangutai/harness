# T-06 binary-numstat verification correction (c1)

## BLUF

The DEC-229 scoped T-06 verification amendment is closed: the committed binary-numstat repair at `ad475c5a7486c9af46d13336bdb2ab2cfe7ca24b` is directly proven by the amended KPI suite.

## Prior fail-first evidence and committed repair

The c0 receipt (`notes/receipt-harness-backend-dev-2026-09-17-07-eng-T-06-c0.md`) records the pre-fix direct `_change_size` reproduction using `3\t2\ttext.py\n-\t-\timage.png`, which raised `ValueError: invalid literal for int() with base 10: '-'`, and the permanent regression's pre-fix 17-test run with one error.

Commit `ad475c5a7486c9af46d13336bdb2ab2cfe7ca24b` contains both the permanent regression, `test_change_size_counts_binary_file_without_inventing_lines`, and the source fix in `.claude/skills/harness/bin/dashboard/kpi.py`: it excludes the `-` binary sentinel from numeric line totals while still adding the binary path to the changed-file set. The regression proves insertions `3`, deletions `2`, and `files_changed` `2` for numeric plus binary numstat rows.

## DEC-229 closed amendment

T-06 `verify` was:

```sh
python3 .claude/skills/harness/bin/run-unit-tests.py --check-layout && python3 tests/unit/test-metrics-kpi.py
```

It is now:

```sh
python3 tests/unit/test-metrics-kpi.py
```

Reason: `The shared layout preflight rejects tracked frontend-owned colocated tests unrelated to T-06; the scoped KPI suite directly proves this task.`

No BRIEF success criterion, task set, decision, intent, or file scope changes. No source or test path was changed in this c1 verification cycle.

## Amended verify proof

Ran verbatim:

```sh
python3 tests/unit/test-metrics-kpi.py
```

Output:

```text
.................
----------------------------------------------------------------------
Ran 17 tests in 2.861s

OK
```
