# QA gate — BUG-2110-lead-return-fail-fast — cycle 1

Pin: `63cac11a..a83198b1740c4d5f92905495695ec94ebe42779a` (detached pinned checkout, feature `BUG-2110-lead-return-fail-fast`, run c1, persona harness-qa; removed on return). Run with `env -u HARNESS_AGENT_TYPE`.

## BLUF

PASS. The configured `unit` and `integration` kinds are green at the pin. Every `verify: automated` SC (SC-01..SC-04) has a named test and a fail-first receipt. The receipt matches the current tests case-for-case. Both gate-loosening mutants redden exactly their own assertions. Two advisories: the T-01 `verify` procedure is no longer runnable, and the integration test file was refactored after the receipt was captured.

## Phase 1 — expected coverage, derived from BRIEF and plan only

- SC-01: three leads × zero, two, and irrelevant-only open runs are refused before any claim; the exactly-one run is a control; an unreadable or absent record refuses; a non-lead is unaffected.
- SC-02: a plan panel refuses for approved and absent approval before any claim; pending is accepted; the product drafting exception; the validator with no plan refuses; mission missing or conflicting refuses; the scope reader needs a declared plan; an approval flip during a lead run is caught.
- SC-03: unit diagnostics name the feature, lead, binding error, exactly-one-run remedy, and `feature-record.py run-start` (missing run), and the reconcile remedy (ambiguous run); the plan refusal names target, status, "before signature", and the pending-plan phase.
- SC-04: start, bind, and authorized append per lead; retained refusals (missing binding, wrong child, parent, feature, checkout, artifact); a pending scope review returns; a plan approved after start is refused at return; two gate-loosening mutants.
- Coverage gaps against Phase 1: none. The mutants are not committed tests (see below).

## Matrix resolution

Config: `.harness/harness.json`, read at the control plane. Task change types are T-01/T-02 `bugfix` and T-03 `docs`.

- bugfix `when unit if touches_runtime_code`: TRUE. The full diff touches `dispatch-guard.py`, so unit is required.
- bugfix `when integration if fix_confined_to_tests_and_contract_docs`: FALSE (runtime code changed). I add integration anyway: SC-02 and SC-04 declare `evidence: integration`, and I may add kinds.
- `__bug_class__` / `match_bug_class` is an unresolvable placeholder, so the floor stays at unit.
- docs `always: []`.
- `typecheck` is `cmd: null`, unresolved. It is not in the matrix, and no `.ts` file is in the diff, so it is not triggered. It is neither skipped nor represented as passed. BRIEF `Verification gaps` stands.

| kind | state | command | result |
|---|---|---|---|
| unit | satisfied | `run-unit-tests.py --kind unit` | exit 0; pool 8 workers, 56 files; `test-lead-start-preflight.py` 34 of 34; `test-omp-hooks.py` 138 pass 0 fail |
| integration | satisfied | `run-unit-tests.py --kind integration` | exit 0, run twice; pool 8 workers, 84 files; `test-lead-start-return.py` 57 of 57; `test-dispatch-guard.py` 113 of 113; `test-validate-digest.py` all sections pass |

The runner's own exit code is the grade (G-09). The unit and integration runs gave consistent discovery counts (56 and 84).

## Task verify strings

- T-01 `python3 /tmp/BUG-2110-fail-first-evidence.py --baseline 63cac11a`: **not re-run, and not re-runnable**. The script is absent (`/tmp/BUG-2110-fail-first-evidence.py` does not exist). The receipt says it was removed after use. Historical audit only, as instructed.
- T-02 `test-lead-start-preflight.py && test-lead-start-return.py`: 34 of 34 and 57 of 57 at the pin. The pipe through `tail` hid the exit codes, so the pass claim rests on the "N of N" lines. The runner-level exit 0 covers both files.
- T-03 `... --check-producers .`: 34 of 34 and 71 of 71. Seven producer files report "no competing blanket mission requirement".

## Fail-first (T-01 receipt `notes/evidence-T-01.md`, baseline `63cac11a3216aa8d…`)

- At baseline the unit file passed 4 of 34 and the integration file 40 of 57. Both exit 1.
- All 91 named cases are present in the receipt. I diffed the receipt's (case, kind) set against the (case, kind) set printed by the current tests: 91 vs 91, zero in either difference.
- Each `startup` case failed at baseline with `exit=0 claim=yes receipt=yes`, so the start went through to a claim. `control` cases passed.
- Per SC: SC-01 = 24 startup cases plus controls. SC-02 = 15 startup cases, including `scope/approved-while-lead-running`. SC-03 = 10 diagnostic cases that name `missing=[...]` pieces. SC-04 = `unregistered-witness` ×3 and `scope/approved-witness` startup-to-return reds, with `return_exit=2` as the witness gap.
- **Advisory A1.** Commit `40fa0c0e` ("split test helpers", +109/-82) rewrote `tests/integration/test-lead-start-return.py` after the receipt. The unit file is unchanged since `d870273d`. I did not re-capture the baseline red against the refactored file, per the instruction not to rerun known baseline errors. Evidence that the refactor was behavior-preserving: same 91 case IDs and kinds, the same 20 `check(` calls before and after, and a green current run. The assertion bodies are not diffed line by line, and the receipt's actual red outputs belong to the pre-refactor file.
- **Advisory A2.** The receipt records the external procedure's output only. The procedure was never committed (by design) and is now deleted, so this audit cannot independently reproduce the 4/34 and 40/57 figures.

## Mutation proofs (my own, at the pin; each restored, `git status --porcelain` clean afterwards)

| mutant | file | effect | newly failing |
|---|---|---|---|
| M1 missing-binding loosened | `digest_destination.py` `authorized_destination` | a missing binding falls through to the registered destination | exactly `SC-04/{eng,product,validator}/missing-binding` (54 of 57 passed) |
| M2 pending-only loosened | `validate-digest.py` return-side call at ~line 1022 | `_pending_plan_status_error` dropped from the return check | exactly `SC-04/scope/approved-after-start` (56 of 57 passed) |

M2 targets the return-side caller. Loosening the function itself would also redden the startup SC-02 cases, because `dispatch-guard.py` reuses that function, so the call site is the isolating mutation. Both mutants reproduce the receipt's mutant section (`evidence-T-01.md` lines 126-127).

## Mechanical code-grade (requested by Bug2110Validate.MisleadingMite)

`code-grade.py --base 63cac11a --head a83198b1 --json`: `passing: 96`, `ungraded: []`, and no record has a non-PASS result. Records at their bar (grade equal to bar, PASS, severity null):

- `dispatch-guard.py`: `_declared_mission` (L508, cyc 7, cog 4, abc 10.7), `_mission_scope` (L531), `_start_mission` (L540), `_plan_status_error` (L618), `_plan_preflight` (L633), `_lead_preflight` (L667), `_start_preflight` (L676, cog 7).
- Tests: `make_root`, `sc02_scope_reader`, `authorized_append` (integration); `make_root`, `sc03_plan_diagnostic` (unit).

Full records: `artifact://795`.

## Out of the change and unchanged as scoped

`validate-digest.py`, `digest_destination.py`, `.omp/extensions/harness-hooks.ts` carry no diff. `test-validate-digest.py` and `test-omp-hooks.py` are green.

## Open items

- Static TypeScript correctness is unproven (typecheck has no runner). It is not triggered by this diff.
- Pre-signature race: approval or run changes after a valid start are handled only by return-time validation. `SC-04/scope/approved-after-start` proves that path.
