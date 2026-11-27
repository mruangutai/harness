# T-01 red/green evidence: one typed transport

Built main-session-direct (DEC-174) by `BuildD_T01` in this worktree, from HEAD `42b7f0d3`
against baseline `b5a4a7f2`. Every run had `HARNESS_AGENT_TYPE` and `CLAUDE_PROJECT_DIR` unset.
The raw outputs are in `t01-red-green/`, each ending with its own `exit=` line.

| Step | File | Result |
|---|---|---|
| Baseline verify (before any edit) | `00-baseline-verify.txt` | exit 0. All 4 scripts PASS. |
| Red: tests written, production untouched | `01-red-test-factory-gh.txt` | exit 1. 15 of 278 FAILING, all of them T-01 cases. |
| Red | `01-red-test-gh-cost-log.txt` | exit 1. 5 of 49 FAILING, all of them T-01 cases. |
| Green: after the production edits | `02-green-test-factory-gh.txt` | exit 0. 319/319. |
| Green | `02-green-test-gh-cost-log.txt` | exit 0. 59/59. |
| Code grades | `03-code-grade-full.json` | Every changed production function grades 4 or higher, and every changed test function 3 or higher (table below). |
| Literal T-01 verify | `04-verify.txt` | exit 0. 4 PASS, the two check-state INV-26 scripts included. |
| Adjacent suites (beyond the verify) | `05-adjacent-suites.txt` | exit 0. 27 files: every unit and integration test naming factory_gh, gh_cost_log or FACTORY_GH, plus the broad-catch census. |

## Red failures and what each proved missing

**test-factory-gh.py.** The failures were the T-01 cases:
- GhResult shape;
- try_gh success, JSON and JSON null, nonzero exit, launch failures, call-time FACTORY_GH and rate-limit diagnosis;
- strict JSON (malformed, duplicate key, nonfinite);
- escape of unexpected exceptions;
- input forwarding;
- the launch_gh contract;
- issue_number_from_url, accept and reject.

On the old code, each of these stopped at the missing names (`GhResult`, `try_gh`, `launch_gh`, `issue_number_from_url`).

Two failures were behavioural rather than missing names. Both were create_issue:
- a non-ASCII-digit URL tail returned a number, because `str.isdigit` accepts fullwidth digits;
- an oversized tail raised a raw `ValueError` (#1542).

**test-gh-cost-log.py.**
- `_read_counter` launched `subprocess.run` itself instead of going through `factory_gh.launch_gh`. This showed up in the "counter uses launch_gh", "counter failures read None" and "import orders" cases.
- `try_gh` and `launch_gh` were absent, so the telemetry cases (one fake binary, launch_gh not measured) could not run.

Two cases passed on the old code. Both are guards that must keep holding through the change:
- the existing ON/OFF wrap sites;
- run_gh measuring once.

## Grades for the changed functions (code-grade.py; production bar 4, test bar 3)

**Production:**

| Function | Grade |
|---|---|
| `GhResult.ok` | 5 |
| `launch_gh` | 4 |
| `_decode_gh_json` | 5 |
| `_exit_error` | 4 |
| `try_gh` | 4 |
| `run_gh` | 5 |
| `issue_number_from_url` | 4 |
| `create_issue` | 5 |
| `gh_cost_log._read_counter` | 5 |

**Tests:** every new or changed test function grades 3, 4 or 5. The full list is in the JSON.

The code-grade command itself exits 1. The failing functions are all unchanged ones in factory_gh.py:
- `_value_from_argv`, graded 3;
- `project_item_stations`, graded 1;
- `issue_stations`, graded 1;
- `_project_field_resolve`, graded 2;
- `project_resolve`, graded 2;
- `project_link_repository`, graded 3;
- `issue_board_item_id`, graded 1;
- `create_ref`, graded 3.

None of them is touched by T-01.
