# T-06 binary numstat repair

## BLUF

`kpi.compute()` now counts a binary numstat row as one changed file while retaining only numeric insertion/deletion totals. Commit: `ad475c5a7486c9af46d13336bdb2ab2cfe7ca24b`.

## Fail-first and post-fix proof

Before production editing, a direct `_change_size` reproduction with `3\t2\ttext.py\n-\t-\timage.png` raised `ValueError: invalid literal for int() with base 10: '-'`. The permanent interface-level regression then failed pre-fix: `test_change_size_counts_binary_file_without_inventing_lines` raised the same exception; the suite ran 17 tests with 1 error.

After the local change, `python3 tests/unit/test-metrics-kpi.py` passed: `Ran 17 tests in 2.861s`, `OK`. The regression verifies each computed feature reports insertions `3`, deletions `2`, and files_changed `2` for one numeric and one binary numstat row.

## Required verify

Ran verbatim:

```sh
python3 .claude/skills/harness/bin/run-unit-tests.py --check-layout && python3 tests/unit/test-metrics-kpi.py
```

It exited 2 before the KPI suite because `--check-layout` reports tracked, out-of-layout frontend tests: `dashboard/client/src/gapstates.test.tsx`, `kpi-content.test.tsx`, and `routes.test.tsx`. No owned source/test was modified to suppress this unrelated layout failure.

## DEC-229 amendment report

Proposed stale-verify amendment: T-06 `verify` must be split so its KPI proof remains `python3 tests/unit/test-metrics-kpi.py`, while the shared layout gate is repaired or rehomed by the owner of the three client test paths. The signed combined command cannot pass in the current approved T-06 file scope. No T-06 interface, intent, or files amendment is needed for the binary-numstat repair.

## Changed implementation

Committed paths: `.claude/skills/harness/bin/dashboard/kpi.py`, `tests/unit/test-metrics-kpi.py`. The source ignores the `-` sentinel only for line totals and always adds its path to the changed-file set. No caller fallback or invented line count was added.
