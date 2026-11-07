# QA gate — BUG-2180 T-01 fix c1 @ 909798ec572ffe6ec484e89fd36f0f58ef113c45 (base 4a05030d)

**Verdict: PASS.** R2 RESOLVED (change-specific unit kind exists, discovered, green, discriminating); R1 is a code-reviewer item, not QA-graded (see below). matrix_ok true; literal T-01 verify green. No source/test edits. Pin checkout `.pins/BUG-2180-inv26-fleet-routing--fix-c1-qa--harness-qa` HEAD == pin (verified `git rev-parse`), removed on return. Commit `1e55b30c` is an ancestor of the pin (`merge-base --is-ancestor` exit 0). `check_state/board.py` has no commits in `554f219e..pin` (empty `git log`) — unchanged since 554f219e. Pin-vs-checkout-HEAD delta (b02796ec) is `feature.json` only.

## Phase 1 (source-blind, from BRIEF/plan)
SC-01 bound-only routing, misplaced twin, shared numbers across repos, owner-sync-off bound; SC-02 mixed owner/bound with retained controls; SC-03 GhError -> CANNOT VERIFY naming feature+error, others compared; SC-04 unresolvable binding -> CANNOT VERIFY, no owner fallback, healthy compared; DEC-217 unit floor: a unit test exercising changed INV-26 logic. All map to tests below; no Phase 1 gap.

## Matrix (PRODUCT `.harness/harness.json`)
T-01 `bugfix`: `unit if touches_runtime_code` -> TRUE (board.py) -> unit REQUIRED; `integration if fix_confined_to_tests_and_contract_docs` FALSE (informational; run anyway); `__bug_class__` unresolvable placeholder, no fire (repo G-08).
- **unit: satisfied.** `env -u HARNESS_AGENT_TYPE run-unit-tests.py --kind unit` -> exit 0, `Ran 118 tests OK`, `pool: 8 workers, 58 files, 33.85s` (c0 was 57: +1 = the new file). Change-specific file discovered and run: `----- test-check-state-inv26-routing.py (exit 0, 0.16s) -----` / `PASS test-check-state-inv26-routing.py` (unit-run output lines 45, 55). Named tests: 9 assertions u.1..u.6 in 6 cases.
- **integration: satisfied.** `--kind integration` -> exit 0, `84 files, 137.62s`; `test-check-state-inv26.py (exit 0, 23.80s)` under load (output line 1316/1354). (84 unchanged vs c0.)
- locally_run kinds: none touched (board.py/INV-26 only). functional/eval excluded, component/ui unresolved but not in the bugfix row.
- Runner caveat: counts are files, one PASS per script (repo G-04); the 4 deliberate `FAIL BUG-1290` lines belong to test-factory-claim-mutation.py (repo G-09) — graded on exit code. Test run with `HARNESS_AGENT_TYPE` unset (repo G-07).

## Commands and exits (all at the pin)
| cmd | exit | result |
|---|---|---|
| `python3 tests/integration/test-check-state-inv26.py` (literal T-01 verify) | 0 | 37 `ok`, 0 `FAIL`, 7.7 s wall (<60 s); x.1-x.6 ok |
| `python3 tests/unit/test-check-state-inv26-routing.py` | 0 | 9 PASS (u.1-u.6) |
| `run-unit-tests.py --kind unit` | 0 | 58 files, 33.85 s |
| `run-unit-tests.py --kind integration` | 0 | 84 files, 137.62 s |
| integration file vs BASE bin (`CHECK_STATE_BIN=<git archive 4a05030d>`; board.py `cmp` = base blob) | 1 | 31 ok, 6 FAIL x.1-x.6, 0 Import/ModuleNotFound/Syntax errors |

## Discrimination
**Unit (R2).** Saved base run `notes/evidence-fix-c1-unit-base.txt`: exit 1, 7 FAIL + 2 PASS controls; after run `evidence-fix-c1-unit-after.txt`: exit 0, 9 PASS. I did NOT re-run the base unit failures. Failure kind is semantic, not setup: reads `('org/repo',3,[16,17,40,41])` (bound numbers unioned into owner read), `reads=[]` with sync off, bound feature judged as "not on the board" on the owner board, GhError path not converted, probe count 1 vs 0. Control cases u.3-healthy and u.5-offline pass at base (correct: unchanged behavior). Read the test (`tests/unit/test-check-state-inv26-routing.py:76-187`): real `inv_26(ctx)` entrypoint, real `gh_board` projection with only `board_stations_for` replaced by a recording fake that raises the real `factory_gh.GhError`; resolver raises real `artifact_accessors.FleetError`. Fake asserts the argument tuple (repo, board number, sorted numbers) at each call (P-12 satisfied). u.1 shares issue 41 across two repos; u.2/u.4 negatives are scoped to the structured read log, not stdout (P-02 satisfied). Provenance caveat (advisory): the base evidence file lacks its own command/SHA header; command/SHA are only in `receipt-main-session-fix-c1.md` (scratch bin from 4a05030d, same test file). Tier: natural RED, main's own capture, not independently reproduced by me per assignment.
**Integration (G-06, test file was refactored: case_x split into `_x1_.._x6_`).** I retook the red at base with the refactored file: exit 1, 31 ok, exactly x.1-x.6 FAIL (excerpts: x.1 `asked={'org/repo': {16,17,14}}` + `GhError ... number of 14`; x.3 `asked={}`; x.4 `asked={'org/repo': {16,17,40,41}}`; x.5 `exit=1 traceback=True lines=[]`; x.6 `asked={'org/repo': {16,17,40,41}}`). Semantic, 0 setup errors. Refactor preserved discrimination.
Mutant naming: owner-union routing (x.1/x.4/u.1), owner-sync-gates-bound (x.3/u.2), uncaught GhError (x.5/u.3), owner fallback on FleetError (x.6/u.4) — each reddens at base.

## SC status
- SC-01 PASS — `tests/integration/test-check-state-inv26.py:747` (_x1), `:755` (_x2), `:762` (_x3), `:774` (_x4); unit u.1/u.2 `tests/unit/test-check-state-inv26-routing.py:128-148`.
- SC-02 PASS — x.4 `:774` (mixed, shared number 41) + 31 retained v/w controls green at base and final; unit u.1 owner clean.
- SC-03 PASS — x.5 `:792`; unit u.3 `:151-161`.
- SC-04 PASS — x.6 `:807`; unit u.4 `:164-172`.

## Prior items
- R1 (T-01 high substance, case_x grade 1): **QA cannot grade complexity** (code-grade is the reviewer's; main reports case_x split to `_x1_.._x6_`, helpers `_x_run/_x_has/_x_asked`). Observed: the split exists at pin (`:747-822`) and all assertions still pass and still redden at base. Status: **resolved-pending code-reviewer grade**; no QA regression.
- R2 (T-01 high substance, unit floor lacked discriminating unit coverage): **RESOLVED** — change-specific unit file now in the unit bucket (58 vs 57 files), run, green; 7 saved semantic base reds.
- Regressions: none. Q1 scope ruling honored (file is amended into T-01 `files`; plan.yaml lines 29-32).

## Findings / gaps
No new gate defect. Advisory (T-01, severity low... recorded as nonblocking, not a gate failure):
1. [form, low, T-01] base-unit evidence file has no embedded cmd/SHA header (provenance only in receipt).
2. [adequacy, low, T-01] u.6 ("nothing in flight -> gh not probed") reddens at base on a probe-count behavior outside SC-01..04 text; harmless extra control, noted so it is not read as SC evidence.
3. [coverage, low, T-01] BoardError branch has no dedicated case; shared handler exercised via GhError — settled nonblocking in assignment, not re-raised as requirement.
Cleanup: base-run raw outputs live only in `/tmp/c1qa-*.txt` (non-durable; write guard allows only qa-*.md); durable excerpts are inline above.

## Principles applied
- Verification is the product (rule 7): green kind accepted only with the new file shown discovered and a saved semantic red.
- Never falsify the record (rule 15): provenance gap in base evidence reported, not smoothed.
