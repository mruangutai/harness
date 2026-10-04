# QA gate — BUG-1898 c1

**BLUF: FAIL.** F-01 is closed by the pin's 81/81 exact-release checks. F-QA-01 remains open: the new wrapper is green at the pin but its claimed baseline-red proof did not mutate or release any sentinel, so it does not prove it would catch the suite-release regression. The required unit kind also fails one named grade assertion.

## Scope and matrix

Pinned review SHA: `81dbd81d21b04b6fdcba2435d2e73a12ec72fd2e`; canonical base: `a4d72e7fc91d0cf7a568d9e2a5225465a422170e`; focused c1 range: `84c3a6cbe74c7c27337d4372a68be60fca834118..81dbd81d21b04b6fdcba2435d2e73a12ec72fd2e` (three implementation/test files). Phase 1, from BRIEF/plan/matrix only, required unit and integration: T-01/T-02 are `cross_module`; T-03 is runtime `bugfix`; T-04 does not change config shape. SC-07 is the pending `locally_run` operator merge gate, not a panel failure.

| kind | command | result |
|---|---|---|
| unit | `env -u HARNESS_AGENT_TYPE .agents/skills/harness/bin/run-unit-tests.py --kind unit` | exit 1: `tests/unit/test-code-grade.py` fails `_registry_errand grade >= 4` (actual grade 3) |
| integration | `env -u HARNESS_AGENT_TYPE .agents/skills/harness/bin/run-unit-tests.py --kind integration` | pass; includes `test-validate-digest.py` |
| targeted T-03 | `python3 tests/integration/test-validate-digest.py` | exit 0; 81/81 BUG-1898 exact-release checks |
| targeted SC-01 | `python3 tests/integration/test-suite-claim-preservation.py` | exit 0; 16/16 distinct-persona sentinel rows preserved |
| inflight_claim_lifecycle_live | operator-only locally-run gate | pending; no fabricated receipt |

`matrix_ok: false`; `suite: fail`; one named assertion failure.

## Re-adjudication

### F-01 — closed

`tests/integration/test-validate-digest.py:5850-5877` executes the real hook against an invalid registry. The pin requires exit 2 for the dispatching parent's PASS, permits its BLOCKED return, permits a leaf, and compares the registry bytes to `{not json`. The T-03 run passed all five assertions, including the unchanged-byte check. This is a discriminating behavior test, not a source-text check.

### F-QA-01 — remains open

The wrapper at `tests/integration/test-suite-claim-preservation.py:43-74` seeds one claim for every governed persona in this checkout registry, each with `Suite.<persona>` runtime id; the measured set is **16 claims / 16 personas**. It invokes the real `test-validate-digest.py`, compares the complete selected rows (`kept == sentinels`), and finally calls `release(... feature=SENTINEL_FEATURE, claim_id=<each seeded id>)`; cleanup selectors are limited to its own 16 ids.

Pin result: wrapper exit 0, suite exit 0, all 16 rows byte-identical. Baseline discrimination result: in isolated checkouts, `VALIDATE_DIGEST_BIN=<0aa337f1 validate-digest.py> python3 <81db wrapper>` exited 1 because the current suite had 74 failures, **but the wrapper's selected sentinel rows were still byte-identical (0/16 released or mutated)**. The c1 suite adds `HOOK_IDENTITY` to generic hook fires (`tests/integration/test-validate-digest.py` focused diff), so it no longer recreates the old missing-identity precondition. `test-suite-claim-preservation.py` does not exist at `0aa337f1`; the requested opposite baseline-suite/pinned-validator overlay cannot be executed without copying a test into that isolated checkout, which the write guard refused because this QA role may not write tests. Thus the recorded red run proves only that old and new suite contracts diverge, not that the new wrapper detects the suite claim-release defect.

## Findings

- **F-QA-01** — kind: substance; severity: high; reader: harness-qa; owner: T-03/T-04. A baseline validator paired with the pin wrapper produced 0/16 sentinel mutation/release, while the suite itself failed 74 cases. If the hook again widens release by persona only for suite payloads, this wrapper can remain green because the pin suite supplies exact identity to its hook cases; SC-01's automated suite-preservation clause would regress undetected.
- **F-QA-02** — kind: substance; severity: high; reader: harness-qa; owner: T-03. `tests/unit/test-code-grade.py` rejects changed production function `validate-digest.py:_registry_errand` at grade 3 below its required grade 4 and it is not allowlisted. Any unit-matrix invocation fails, so a QA PASS would falsely claim the matrix passed.

`severity_max: high`.

## Fail-first and SC evidence

| SC | pin evidence | fail-first evidence |
|---|---|---|
| SC-01 | `test-validate-digest.py:5712-5760`; preservation wrapper | retained direct red: `notes/review-harness-qa-c0.md:23`, `artifact://365:243-391`; c1 wrapper baseline attempt above is non-discriminating |
| SC-02 | `tests/unit/omp-hooks.test.ts:1875-2001` | `notes/review-harness-qa-c0.md:25` (`artifact://362`) |
| SC-03 | `tests/integration/test-inflight-registry.py:1238-1410` | `notes/review-harness-qa-c0.md:25` |
| SC-04 | `tests/unit/omp-hooks.test.ts:2003-2113` | `notes/review-harness-qa-c0.md:26` (`artifact://362`) |
| SC-05 | `tests/integration/test-check-omp-port.py:194-214` | `notes/review-harness-qa-c0.md:27` |
| SC-06 | `test-validate-digest.py:5769-5844` | `notes/review-harness-qa-c0.md:28` (`artifact://365:378-391`) |

## Principles applied

- **Build the Lever** — used the configured runners plus isolated pin/baseline validator substitution, preserving the assigned worktree.
