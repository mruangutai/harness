# fix-c1 FixD1_Wayfind: H2 and A1

Base: HEAD 15a240bc. Outputs are in `notes/fix-c1-FixD1_Wayfind/`. Run with HARNESS_AGENT_TYPE and CLAUDE_PROJECT_DIR unset.

## H2 (T-04, SC-03): wayfind.py
- **Change:** `gh_json_or_absent` now returns a module sentinel, `ABSENT`, for the pinned confirmed-404 classification. It no longer returns `None`, so a successful JSON `null` is no longer the same value as absence.
- **`blockers()`:** `ABSENT` maps to `[]`. Any other payload must be a list of objects; otherwise a typed `GhError` is raised through the new `unusable()`. The `or []` coercion is gone.
- **`parent_of()`:** `ABSENT` maps to `None`. Any other payload must be a dict whose `number` has `type(...) is int` and is ≥ 1, so bool, 0, negative, str, float, null, `{}` and list payloads raise `GhError`.
- **Fail-closed paths:** `cli()` already catches `GhError`. `frontier` therefore exits 1 before any eligibility decision (it never reads `issue view`), and `resolve` exits 1 after only the parent read, with no writes.
- **Imports:** added `import json`, used for `GhError.stdout`.
- **New tests in `tests/unit/test-wayfind.py`:**
  - `case_8b`: blockers null, `{}`, string, number, bool, non-object item and null item; parent null, `{}`, number false, true, 0, -2, "2", 2.0 and null, and a list.
  - `case_10b`: frontier with null and `{}` blockers prints no ticket and makes no `issue view` read.
  - `case_11b`: resolve with `{}`, number false, 0, "2" and null makes only the parent read, with no writes and no "no parent map".
- **Red:** `01-red-wayfind.txt` has 28 failures, all of them new cases. The pre-existing cases still pass.
- **Green:** `03-green-wayfind.txt` reports ALL PASS. The existing case_7 test, where a genuine 404 means absence, still passes.

## A1 (T-01): factory_gh.py
- **Change:** in `_ISSUE_URL`, the authority is now a hostname, `[A-Za-z0-9](?:[A-Za-z0-9.-]*[A-Za-z0-9])?`, with an optional `:port`. It used to be `[^/\s]+`.
- **New reject cases in `tests/unit/test-factory-gh.py`:** `https://?/…`, `https:///…`, `https://@/…`, `https://#/…` and `https://:443/…`.
- **New accept cases:** `ghe.example.co.uk` and `github.acme-corp.internal:8443` (GitHub Enterprise).
- **Red:** `02-red-factory-gh.txt` shows 4 of 324 failing. `https:///` was already rejected at HEAD, because `[^/\s]+` cannot match an empty string, so its case is a guard and not a red.
- **Green:** `04-green-factory-gh.txt` shows 324/324.

## Verifies
- **T-01:** `05-verify-T-01.txt` exits 0, all 4 files PASS.
- **T-04:** `06-verify-T-04.txt` exits 0, both files PASS.

Grades were not run in this cycle.
