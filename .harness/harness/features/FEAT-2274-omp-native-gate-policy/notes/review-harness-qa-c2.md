# QA gate, cycle 2 — FEAT-2274

Pin `242f9714d426415611bea796dd30a807f14c4193`; baseline `1e0b014917125bc9aae1f30a2f6fd53ed239f3bc`; prior-cycle pin `649612d8`. Gate run in a managed pinned checkout (`pinned-checkout.py`, persona `harness-qa`, HEAD = pin, clean). Red reproductions in two more managed checkouts (`harness-qa-base` = baseline source + pin `tests/`; `harness-qa-pre` = `649612d8` source + pin `tests/`, then `649612d8` tests). All three removed on return. `HARNESS_AGENT_TYPE` unset for runners (G-07); no project-root env inherited (only CLAUDECODE/OMPCODE). Logs in `/tmp/qa2274c2/` are not durable; the commands and counts below are the record.

## VERDICT: PASS — matrix_ok true, both active kinds green at the pin, every automated SC has a retained pre-fix red

c1 F-1/F-2/F-3 (V4/V5/V6) are closed. V1/V2/V3 each have their own new red-then-green assertion, reproduced here, not read from the receipt.

## Gate state at the pin

| Kind | Command (from `.harness/harness.json`) | Exit | Discovery | Result |
|---|---|---|---|---|
| unit (active) | `.agents/skills/harness/bin/run-unit-tests.py --kind unit` | 0 | 63 files, 1187 PASS lines (one PASS per script, G-04) | pass |
| integration (active) | `.agents/skills/harness/bin/run-unit-tests.py --kind integration` | 0 | 91 files, 3077 PASS lines | pass |
| functional, eval | `excluded`, DEC-187 | n/a | not_applicable | no SC rests on them |
| component, ui, typecheck | `unresolved`, cmd null | n/a | not required (change types are cross_module/config/docs); #2257 accepted | none claimed |
| omp_session_accessor, handoff_comprehension, issue_types_live | `locally_run` | n/a | diff touches none of their detect surfaces | none needed |

Discovery contains every new/changed owner file by name: `test-omp-native-gate-runtime.py`, `test-harness-constraints.py`, `test-gen-decisions-index.py`, the seven gate suites, `test-omp-hooks.py` (runs `omp-hooks.test.ts`), `test-harness-boundary.py`, `test-code-grade.py`, `test-lead-start-preflight.py`. The `FAIL BUG-1290` and `ERROR could not resolve scan root` lines in the logs are those suites' own mutation-proof output (G-09); the runner exit decides. The two known baseline canonical-reader failures were not rerun.

Matrix: T-01 `cross_module` requires unit and integration (both satisfied); T-02 `config` requires integration only when `touches_config_shape` (integration is green regardless); T-03 `docs` requires nothing. `matrix_ok: true`.

Task verify clauses run at the pin: T-01 runtime 445 passed / 0 failed; omp-hooks 179 pass / 0 fail; boundary ALL PASS. T-02 constraints 14 passed / 0 failed. T-03 `gen-decisions-index.py --stdout | diff` clean, plus the above.

## c1 must-fix closures in this lens

- **V4 (F-1) closed.** `test-lead-start-preflight.py` `[control] BUG-2141/lead-eng` now asserts pass-through to native authority (exit 0, one claim, no `spawns: list`, no DEC-174 text); 61/61 at the pin. Red: the `649612d8` file against the same source gives `60 of 61`, `FAIL [control] BUG-2141/lead-eng: ... keeps its existing spawns allowlist refusal ... exit=0 claim=yes`. Receipt `fix-c1-v4-v5.md`.
- **V5 (F-2) closed for the two self-graded cases.** `test-code-grade.py` PASS at the pin (in the unit run). Red: the `649612d8` tests give `FAIL test-validate-digest.py:run_feat65_guard_cases grade >= 3` and `...run_feat2274_unavailable_cases grade >= 3` (rc 1). The risk grader over the full diff (`code-grade.py --base 1e0b0149 --head 242f9714 --json`) reports 108 records, `passing` 104, no grade-1, four grade-2 `med` records (listed in findings).
- **V6 (F-3) closed.** `test-gen-decisions-index.py` passes at the pin; index regeneration diff is clean. Red: pin tests over `649612d8` docs give `FAIL test_committed_index_is_complete_and_within_budget: 5 row(s)` (the same five rows as c1).
- **V1 (high) has real discrimination.** Pin tests over `649612d8` source: gh-close-gate `8 FAILED` (no/unparseable/non-mapping harness.json, duplicate keys, github block list/empty list/null each exit 0 instead of the named exit 2); branch-create-gate `86/93`, 7 config-fault FAILs. Both 156-ok / 93/93 at the pin. Unrelated commands exit 0 untouched in the paired controls.
- **V2 has real discrimination.** test-dispatch-guard `172 of 174` at `649612d8` with the two new cases red (failed run-dir vocabulary; unreadable tool grants: exit 0, stdout only the claim, no unavailable line); `174 of 174` at the pin, and the three controls (readable shell-less grant, declared-empty manifest, non-governed target) emit nothing. The fixture now carries the persona it dispatches, so each case injects one fault; the exactly-one assertion is unchanged.
- **V3 has real discrimination.** At `649612d8` source, `omp-hooks.test.ts` fails 1 (`an explicit deny stays a refusal and a normal pass stays silent beside an unavailable gate`; reason lacks the sibling notice); 179/179 at the pin. Provenance limit: the claim that omp 19.1.0 drops `additionalContext` on a blocked call rests on the receipt's Bun-binary `strings` evidence and 18.14.1 type source (`fix-c1-v3-red-green.md`), outside the pin; the extension contract is what the test checks (SC-05-style gap, accepted).

## Fail-first per automated SC (tier: natural RED at the immutable baseline `1e0b0149` with pin tests, reproduced here; Main's receipts are the durable copies)

Baseline results here: runtime suite `3 passed, 442 failed`; omp-hooks `159 pass, 20 fail`; boundary 7 FAIL; constraints `3 passed, 11 failed`; check-domain 4; bash-write-guard 4; dispatch-guard `164 of 174` (10 FAIL); validate-digest 7; gh-close-gate 58; branch-create-gate `49/93` (44); plan-sign-gate 67. All assertion failures, none import/collection errors.

| SC | Test at the pin | Red evidence |
|---|---|---|
| SC-01 | `test-omp-native-gate-runtime.py` (guarded crash, startup, missing gate, missing interpreter, spawn error, SIGKILL; each broad gate); `test-harness-boundary.py` feat2274_*; `test-dispatch-guard.py:515 case_f2274_unavailable_outcome`, `:588`, `:603`; `test-validate-digest.py:5540`; `test-check-domain.py`/`test-bash-write-guard.py` f2274 cases | baseline red above; `notes/t01-red-runtime.md`, `t01-red-py-broad.md`; V2 at `649612d8` |
| SC-02 | `test-omp-native-gate-runtime.py` narrow cases; gh-close/branch-create (`run_corpus_agreement:319`, `run_issue_2107:383`, `run_config_faults:467`)/plan-sign corpora; `omp-hooks.test.ts` narrowGateApplies, classifyPolicyRun | baseline 58/44/67 FAIL; V1 at `649612d8` 8/7 FAIL; `notes/t01-red-py-narrow.md`, `t01-red-ts.md`, `fix-c1-v1-red-green.md` |
| SC-03 | `omp-hooks.test.ts:2309` before_subagent_spawn refuses a harness target outside task, Main and governed parents | baseline `(fail)` for exactly this test; `notes/t01-red-ts.md` |
| SC-05 | `test-harness-constraints.py:54-114` (exact agents, alwaysApply, five groups, two exclusions, three lead guidance cases) | baseline `3 passed, 11 failed`: the rule file, glob, alwaysApply, groups 1-5 and 3 leads FAIL; the 3 passes are the RULES.md control and two exclusions (vacuous by design, paired with the positive content checks); `notes/t02-red-green.md` |
| SC-06 | `test-dispatch-guard.py:1259 case_27_spawn_targets_are_native_authority` (27a, 27c, 27e) | baseline `FAIL case 27a/27c/27e` (formerly refused, now passes the guard) |
| SC-07 | `omp-hooks.test.ts:2172, 2184, 2196, 2221, 2229, 2246, 2259, 2287` (notice multiplicity, input/env, schema, content composition) | baseline: 10 of the 20 `(fail)` lines are the FEAT-2274 composition tests; V3 test red at `649612d8` |
| SC-09 | runtime suite controls; `omp-hooks.test.ts:2111` merge-gate fail-closed (green at baseline, an unchanged control); validate-digest `[f2274]` unavailable cases and `absent/null/blank/non-object digest_object stays a contract refusal` (`test-validate-digest.py:5534`) | unavailable-visibility red at baseline (validate-digest 7 FAIL incl. no-schema, no-identity, stop_hook_active, missing registry); denial controls cited green at baseline in `t01-red-runtime.md` section B |

Tier caveat (O-03): the runtime suite's baseline red of 442 is mostly signature-absent (`runPolicy` not exported at baseline); the semantic red is Main's `t01-red-runtime.md` section B (export shim, controls `ok`, unavailable assertions `FAIL`), consistent with the python and TS suites' semantic reds above.

## Findings

All non-blocking; none reopens a settled gap.

1. **advisory, low, kind `maintainability`, owner T-01 (`tests/integration/test-check-domain.py:_feat2274_cases`, `test-dispatch-guard.py:case_f2274_unavailable_outcome`, `test-bash-write-guard.py:run_feat65_guard_cases`, `run_feat2274_unavailable_cases`).** The code-risk grader still reports four grade-2 `med` records (bar 3) in test files outside `test-code-grade.py`'s `SELF_GRADED_FILES`, so no gate fails. Scenario: a later edit to one of these cases is graded below the bar. c1 accepted the locality reasons; I rederive only that the grader output matches the stated count and no grade-1 remains. Route: code reviewer's call.
2. **advisory, low, kind `contract-wording`, owner T-03 (SPEC.md §4.2 line ~752).** SC-01/SC-07 say passive additionalContext; at the pin, a blocked pre-call can carry a sibling gate's notice only in the refusal `reason` (the V3 consequence). Intent (notice not lost) is met and SPEC records it; the literal "additionalContext" wording is met for non-blocked calls only. Left to pm/operator; no action needed unless the operator wants the BRIEF reworded.
3. **limit, SC-06 sub-claim.** The retention of the other dispatch-guard checks rests on the unchanged green suite (174 cases) and the 27x passthrough cases; I ran no per-check mutation proof. Discrimination of the retained checks is unshown, not disproven (O-05).

## Principles applied

- Build the Lever: the red reproductions are one rerunnable loop (`git checkout <pin> -- tests` over a managed pre-fix checkout, then the named test files) rather than a hand reading of receipts; Main's `t0*-red-*.md` receipts are the committed copies.
- Verification is the product: no suite green was taken as SC evidence without a retained red for the same named test.

## Coverage gaps

None from Phase 1. SC-04, SC-08 are inspection. Typecheck (#2257) and live native rule delivery are accepted gaps.
