# QA c1 — BUG-2141 T-01 (pin cc0c16bd31035152857c07036fce6094715e596e)

**PASS.** The c0 must_fix is closed: `case_15d` runs the real guard (`fire()` subprocess) and asserts exit, claim count and receipt for every control SC-04 named. All commands exit 0.

## Delta and pin
- Pin..worktree HEAD differs only in `feature.json`. The tree was clean at HEAD, so the suites ran in the feature worktree and need no pinned checkout.
- `423049fe..cc0c16bd` touches `tests/integration/test-dispatch-guard.py` (+64, tests only), plus feature notes and `feature.json`. No source, unit-test or doc change, so SC-01..03 stand.
- Full diff `0b17e9bb..cc0c16bd`: 18 files. Production code is `dispatch-guard.py` (+25). Docs are DECISIONS, INDEX, AGENTS, harness.md.
- Matrix (bugfix, resolved over the FULL diff per P-13):
  - unit `when touches_runtime_code`: true, required and satisfied.
  - integration `when fix_confined_to_tests_and_contract_docs`: false (runtime code changed). It is run anyway because SC-04 is signed as integration.
  - `__bug_class__` is a placeholder (repo G-08): no fire.

## Phase 1 expectations (from BRIEF/plan, source-blind)
Main→product-lead (plan, patch) and Main→validator-lead (validate, fix) on an all-direct plan start and claim. Main→eng-lead on team-only, missing-mode, empty, invalid and absent plans still starts and claims. The all-direct eng-lead refusal exits 2 before a claim and names DEC-174. All are covered; `coverage_gaps` is empty.

## Commands (exit codes, not just PASS counts)
| Command | Exit | Result |
|---|---|---|
| `tests/unit/test-lead-start-preflight.py` | 0 | 50 of 50, 0 FAIL |
| `tests/integration/test-dispatch-guard.py` | 0 | 126 of 126 (c0: 117; +9 `case 15d`), 0 FAIL |
| `gen-decisions-index.py --stdout \| diff - DECISIONS-INDEX.md` | 0 | empty diff |
| `run-unit-tests.py --kind unit` | 0 | 56 files discovered, 56 `-----` blocks, all `(exit 0`; includes `test-lead-start-preflight.py` |
| `run-unit-tests.py --kind integration` | 0 | 84 files discovered, 84 blocks, all `(exit 0`; includes `test-dispatch-guard.py` (7.99s) |

- The runner's raw `^PASS test-` count (58/90) exceeds the file counts because some scripts print nested `PASS test-...` lines. The `-----` blocks and the pool lines are the discovery counts (G-04).
- The single `ERROR could not resolve scan root` line sits inside passing `test-suite-independence.py`. It is a self-test line (`ok self-test unresolved root refuses`), not a failure.
- Env: `HARNESS_AGENT_TYPE` unset for the runs (repo G-07).

## SC-04 control quality (read at `tests/integration/test-dispatch-guard.py:717-777`)
- `_main_start` builds a disposable registered checkout, registers one open lead run, writes the plan (or none) and fires the real guard as OMP Main. It reads the registry back via `_claims_for`.
- `_starts_and_claims` asserts exit 0, exactly one claim, `harness_claim` in stdout and `DEC-174` absent from stderr. It is not stdout-substring-only (P-02), and the claim count is read from the registry.
- Positives: product-lead plan/patch and validator-lead validate/fix, on an all-direct plan. Each has its own mission header.
- Negatives (still claim): team-only, missing execution_mode (direct+absent), empty tasks, invalid YAML, absent plan. Missing-mode is a genuine mixed-with-unset shape. Each leg is a separate case (P-06).
- The refusal controls are in `case 15c` (single/multi direct in unit, multi-direct in integration), unchanged from c0.
- The guard consumes `handoff_policy.exempt_reason` (`dispatch-guard.py:704`). It reproduces no predicate and `handoff_policy.py` is untouched.
- No uncovered declared case.

## fail_first (automated SCs)
- SC-03: retained `notes/evidence-T-01.md`. Baseline `0b17e9bb` unit failed 4 of 50: `BUG-2141/main-eng/{single,multi}-direct` and their diagnostics. Independently reproduced in c0 (`review-harness-qa-c0.md`) and not rerun.
- SC-04: retained `notes/evidence-T-01.md`. Baseline integration failed 3 of 117 at `case 15c` (exit 0 instead of 2, no DEC-174, claim recorded). Positives and controls passed at baseline by design, so no red history is invented for the 15d positives.

## Advisories retained (nonblocking)
1. The new 15d controls are not mutation-proven. I could not perturb a pinned guard because check-domain bars QA writes outside tests and notes.
2. BUG-2110 fallback: the absent- and invalid-plan legs now exercise Main origin plus plan-unresolvable fallback. An unresolvable or unregistered declared feature with Main origin still has no dedicated regression (low).
3. The unit and integration scripts pass, but nothing asserts the PRODUCT-lead/validator-lead positives would fail if the guard were widened to refuse them. They are guarded by assertion shape only.

## Principles applied
None cited beyond harness-verification-rules (matrix resolved over the full diff; fail-first reuse, not reconstruction).

Pinned checkout created for the mutation attempt was removed on return.
