# QA gate — BUG-2141 T-01 @ 423049fe49c122ee2ec790c53cdc6ce19f1ec791 (run c0)

**BLUF: FAIL.** Every command is green and the fail-first is independently reproduced, but SC-04's literal integration scope is under-delivered (finding F-1, T-01). The prohibited dispatch is covered in integration. The product/validator dispatches and most shared-policy nonqualifying shapes are not.

Base: origin/main = merge-base = `0b17e9bbf7ef4baafa0eb0844ec0edbb753dd86f`. The pin was read through `pinned-checkout.py` (`--persona harness-qa`) and removed on return.

## Phase 1 — expected coverage, from BRIEF and plan only

- SC-03 unit: Main to eng-lead on a single-task and a multi-task all-direct plan exits 2 before a claim, names DEC-174 and the build-directly remedy, and leaves the registry unchanged. Controls: orchestrator-origin, lead-origin, and nonqualifying plans (mixed, team, missing mode, empty, invalid, absent).
- SC-04 integration: the prohibited dispatch, plus Main to product-lead and validator-lead valid dispatches, plus mixed/team and shared-policy nonqualifying shapes, plus unrelated outcomes retained.
- Helper reuse, SC-04: `dispatch-guard.py` calls `handoff_policy.exempt_reason` and does not duplicate its predicate.
- Configured-feature case: Main to eng-lead with a missing feature or run still reaches the BUG-2110 preflight refusal.

## Matrix (`.harness/harness.json`)

change_type `bugfix` resolves to:
- unit: required, because `dispatch-guard.py` is runtime code (`touches_runtime_code`).
- integration: not triggered by the matrix, because the fix is not confined to tests and docs. BRIEF SC-04 still names integration, so I ran and graded it.
- `__bug_class__`: unresolvable placeholder (repo G-08).

`matrix_ok: false`. The matrix floor (unit) is satisfied. The BRIEF-named SC-04 integration scope is not: the `integration` kind is reported `missing` for the product/validator-control and nonqualifying-shape cases (F-1). The integration suite is green, but it does not cover those cases.

## Gate results at the pin (HEAD verified 423049fe; `HARNESS_AGENT_TYPE` unset, repo G-07)

| Command | Result |
|---|---|
| T-01 verify, part 1: `python3 tests/unit/test-lead-start-preflight.py` | exit 0, 50 of 50 cases passed, 0 `^FAIL` |
| T-01 verify, part 2: `python3 tests/integration/test-dispatch-guard.py` | exit 0, 117 of 117 cases passed, 0 `^FAIL` |
| T-01 verify, part 3: `gen-decisions-index.py --stdout \| diff - DECISIONS-INDEX.md` | exit 0, empty diff |
| `run-unit-tests.py --kind unit` | exit 0, discovered 140, pool 56 files, 58 `PASS test-` lines, 0 `FAIL test-`, includes `test-lead-start-preflight.py` |
| `run-unit-tests.py --kind integration` | exit 0, pool 84 files, 90 `PASS test-` lines, 0 `FAIL test-`, includes `test-dispatch-guard.py` |

The unit log contains an `ERROR could not resolve scan root` line. It comes from a negative case in another script, and that script's PASS line and the runner's exit 0 stand.

The 58 vs 56 and 90 vs 84 differences between PASS-line counts and pool file counts are not reconciled. They come from the runner's own tally (repo G-04, G-11) and do not change the exits. Raw logs: `/tmp/qa-c0-run-unit.txt` and `/tmp/qa-c0-run-integration.txt`. The bash-write-guard denied copying them into `runs/c0/`, so the key lines are in this note.

Kinds:
- `unit`: satisfied.
- `integration`: satisfied, run beyond the matrix floor.
- `functional`, `eval`: excluded (DEC-187).
- `component`, `ui`: unresolved and not triggered.
- The `locally_run` probes: their `detect` surfaces are untouched by this diff.

## Fail-first (audit of notes/evidence-T-01.md, own reproduction)

The evidence note is narrative about a deleted runner. I reproduced it myself. I checked out immutable baseline `0b17e9bb` as a second pin (persona `harness-qa-base`) and overlaid only the two pinned test files with `git checkout 423049fe -- <tests>`. `dispatch-guard.py` and every sibling module are the baseline's.

Tier: own reproduction at the baseline pin, which ranks as constructed baseline RED, not a natural pre-fix RED. The author's historical run was never retained.

- Unit, exit 1, 46 of 50 passed. The four failures are `BUG-2141/main-eng/{single,multi}-direct` and their `/diagnostic` cases. Each reads `exit=0 claim=yes receipt=yes stderr=''`.
- Integration, exit 1, 114 of 117 passed. The three failures are the three `case 15c` assertions on the all-direct plan: exit 2, DEC-174 plus "directly" in stderr, and registry unchanged. The registry shows a `harness-eng-lead` claim with dispatcher `Main`.
- The control `case 15c: ... mixed plan still claims` passed at baseline.

These are assertion failures (the baseline accepts the detour), not import, mission, registration or fixture failures. Logs: `/tmp/qa-c0-base-unit.txt` and `/tmp/qa-c0-base-int.txt`.

- SC-03 `fail_first`: satisfied.
- SC-04 `fail_first`: satisfied, for the prohibited-dispatch assertion only.

## Findings

**F-1 [T-01, SC-04, major, spec-gap]: integration omits required cases.**
- BRIEF SC-04 requires integration assertions for "valid main-session product/validator dispatches, mixed/team plans, and shared-policy nonqualifying shapes".
- Pinned `case_15c_omp_main_eng_lead_on_all_direct_plan_refused` (`tests/integration/test-dispatch-guard.py:~681`) covers only two shapes: all-direct with 2 tasks, and mixed.
- No integration case has Main dispatching product-lead or validator-lead. The only other Main-origin integration case is the orchestrator claim in 15b.
- Integration also has no team-only, missing-mode, empty, invalid or absent plan.
- The intent is met at unit level (`dec174_controls` and `dec174_nonqualifying_unchanged` in `tests/unit/test-lead-start-preflight.py:~345-385`).
- The SC text says integration, so this is two findings in the O-04 sense: intent met, literal text unmet.
- Peer `Bug2141Validate.GrubbyStoat` raised the same gap. I verified it against the pinned file.
- Route: owning builder to extend the integration test (add the controls and shapes), then re-gate. QA does not author the tests.

**F-2 [T-01, advisory, coverage-gap]: Main-origin BUG-2110 retention is not directly tested.**
- Read of `dispatch-guard.py:690-714`: `_direct_orchestration_refusal` returns silently on `AuthorizationError` (a `ValueError`, caught via the `errors` tuple) or on a missing plan, and the unchanged `_start_preflight()` follows.
- I found no test where the Main origin dispatches eng-lead with no registered feature or no open lead run and the BUG-2110 refusal is asserted. This is inferred from the code, not measured.
- The nonqualifying unit shapes all register the lead run and hit the claim path.

**F-3 [advisory, inspection]: `.omp/commands/harness.md` opening.**
- "You never dispatch a lead or a member... never do the feature's work yourself — except as below" is one sentence with a trailing exception, and the exception follows immediately.
- The "never dispatch a lead" clause is conditional only through that trailing phrase. SC-02 inspection belongs to the reviewers.

## Origin detection (read of the pinned code)

- The guard reuses the existing `omp_main` predicate: `agent == "Main"`, `runtime == "omp"`, `harness_agent_id == "Main"`, and no parent agent id. No second identity spelling was introduced.
- The gate keys exactly on `dispatched == "harness-eng-lead"`. A claude-runtime or child-parented "Main" does not match. Orchestrator and lead origins are unaffected: the unit controls show orchestrator to eng-lead unchanged, and lead to eng-lead keeps the spawns refusal.
- The qualifying answer is `handoff_policy.exempt_reason(feature_dir)[0]`, which is fail-closed and plan.yaml-only.
- Not mutated: I did not run a mutant on the guard line, because that is outside this gate-only assignment.

DEC-174 amendment, DEC-120 cross-reference, `AGENTS.md` and `harness.md` are consistent in content: same duties, same permitted leads, same prohibition on eng-lead, and the same ledger pointer. The index is regenerated and the diff is empty.

## Principles applied
None cited (no leaf read this run).
