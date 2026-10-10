# Code review — BUG-2141 — c1

**PASS: T-01 / SC-04's cycle-0 must-fix is closed by inspection; no new regression identified.** This reader executed no checks. QA owns execution and the pinned mechanical grading receipt.

Reviewed `0b17e9bbf7ef4baafa0eb0844ec0edbb753dd86f..cc0c16bd31035152857c07036fce6094715e596e`; remediation delta starts at `423049fe49c122ee2ec790c53cdc6ce19f1ec791`. Git merge-base confirms the immutable baseline. Full commit history has no human-attributed commits; initial working tree is clean. The delta is executable-tests-only, not literally one-path-only: it also commits feature metadata and five cycle-0 reader receipts. No production, documentation, shared-policy or existing assertion changes occur.

## Stage 1 — specification
- SC-01 inspection stands: unchanged `.harness/harness/docs/DECISIONS.md:4509-4520,2359-2361` and generated index retain the accepted lifecycle/permissions/cross-reference result.
- SC-02 inspection stands: unchanged `AGENTS.md:39` and `.omp/commands/harness.md:8-15` retain the accepted short qualified pointers. SC-03 and prior fail-first evidence also stand; no new baseline-red claim is made.
- SC-04 closure: pinned `tests/integration/test-dispatch-guard.py:756-776` adds Main→product (plan/patch) and Main→validator (validate/fix) on a nonempty all-direct pending plan, plus Main→engineering on team-only, missing-mode, empty, malformed and absent plans. Existing `:679-712` retains all-direct refusal and mixed acceptance. Shared-helper consumption remains unchanged at `.claude/skills/harness/bin/dispatch-guard.py:705`.
- All additions serve SC-04; feature records preserve validation history. No build-lead amendments or developer receipts exist for this main-direct build.

## Stage 2 — quality and assertion discrimination
`_main_start` (`:728-749`) creates an isolated root, registers the appropriate open lead run, supplies the actual OMP Main identity and mission/root headers, then executes the real guard through `fire` (`:54-69`). Its return reads the resulting registry, filtered to the literal lead and feature, before finally removing the fixture. The absent-plan case starts without a plan; missing-mode omits one task's key; malformed YAML is not a second policy implementation.

`_starts_and_claims` (`:752-754`) binds real exit 0, exactly one matching registry claim and a claim receipt; the DEC-174 absence assertion has those positive observations alongside it. Returning without claiming, crashing, or rejecting a valid dispatch cannot satisfy it. [INFERENCE] Broadening the refusal to product/validator reddens their controls; treating any nonempty plan, an empty plan, or unreadable/missing plans as all-direct reddens the corresponding engineering control. These are reasoned discriminators, not executed mutants. Existing unrelated assertions are untouched and the new case is invoked by `main` (`:1296`). No vacuous or fixture-only assertion identified.

Python risk skill and grader rules read before quality assessment. [INFERENCE] The four added functions meet the test-code bar and the earlier accepted Python remains unchanged; `code_grade: pass` is the inspection assessment, not an independently executed grader result. Requested exact baseline→pin grading from QA/validator lead for final fan-in; mechanical confirmation remains their evidence obligation under the no-check dispatch constraint.

No new findings, spec violations or must-fix. The prior nonblocking Main-origin BUG-2110 fallback coverage advisory is unchanged, not re-gated. Open evidence question: include QA's exact-pin mechanical grading result in final validation; no implementation question.
