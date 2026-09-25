# QA gate c1 — BUG-1898 inflight claim lifecycle

**BLUF: FAIL.** F-01 is closed: the real validator suite passes all 81 BUG-1898 exact-release checks, including `_b1898_unreadable_registry_holds_the_parent`. F-QA-01 remains open: the new serial preservation run is green, but it has no faithful red proof and its sentinel setup races, leaks on a second invocation, and does not bind its root sentinels to the suite's throwaway-registry hook executions. SC-07 remains `pending_operator_gate`, not a panel failure.

## Reviewed scope and matrix

Canonical range: `a4d72e7fc91d0cf7a568d9e2a5225465a422170e..81dbd81d21b04b6fdcba2435d2e73a12ec72fd2e`; c1 delta: `84c3a6cbe74c7c27337d4372a68be60fca834118..81dbd81d21b04b6fdcba2435d2e73a12ec72fd2e` (11 paths, 483 insertions, 18 deletions; executable/test paths: validator plus the two integration tests). Phase 1, derived before source: T-01/T-02 `cross_module` require unit+integration; T-03 `bugfix` touches runtime code and requires unit; T-04 config shape requires integration; T-05 docs requires none. Union: **unit, integration**.

| kind | state | measured command / result | coverage |
|---|---|---|---|
| unit | satisfied | `bun test tests/unit/omp-hooks.test.ts` → exit 0; **98 pass, 0 fail, 272 expectations, 1 file** | SC-02/04 run-start, reclaim, identity and settlement |
| integration | satisfied | `python3 tests/integration/test-validate-digest.py` → exit 0; **81/81 BUG-1898 exact-release checks**, `ALL PASSED` | SC-01/03/06 digest and F-01 unreadable registry |
| integration (F-QA-01 target) | fail | `python3 tests/integration/test-suite-claim-preservation.py` serialized → exit 0; **3 PASS, 0 failures**, after one failed concurrent attempt → exit 1 | green preservation is not discriminating; see finding |
| inflight_claim_lifecycle_live | locally_run | not run by constraint | SC-07 operator gate; no live receipt |
| typecheck / component / ui | not_applicable | no configured applicable command; excluded from this lifecycle matrix | BRIEF records typecheck gap; no UI surface |

`matrix_ok: false`: required unit/integration behavior is green, but the required SC-01 suite-preservation integration proof is defective, so the matrix cannot prove the full change.

## Measured preservation and F-01

`test-suite-claim-preservation.py:38-53` enumerates **16** governed `harness-*.md` personas, including the four specifically requested unrelated personas `harness-backend-dev`, `harness-documentor`, `harness-eng-lead`, and `harness-pm`; it assigns each `Suite.<persona>` runtime id. The serialized green run seeded 16, invoked the real `test-validate-digest.py` subprocess, asserted all seeded rows byte-identical, and released recorded ids in its `finally` (`:57-75`).

That is not sufficient red/green discrimination. The suite's BUG-1898 hook cases explicitly use a fresh `_t09_root()` and pass it as `HARNESS_PROJECT_DIR` (`test-validate-digest.py:5664-5668, 5705-5729; 1733-1753`). Thus none of those hook calls resolves or releases the preservation test's checkout-root sentinel rows. No baseline-`0aa337f1`/pin-overlay or isolated equivalent red receipt exists for this new proof. The retained c0 SC-01 direct-validator red (`review-harness-qa-c0.md:23`, 7/76 exact-release checks) predates and does not discriminate the new suite-preservation wrapper.

The proof is also not reentrant: its fixed `SENTINEL_FEATURE` and static `Suite.<persona>` identities are seeded before the `try`/`finally` (`test-suite-claim-preservation.py:22-24, 43-58`). Two independently issued c1 commands both exited 1 at `entry["claim_id"]` because `claim_with_receipt()` returned `None` while a same-feature PM sentinel was live; the failing invocation never enters cleanup. After serialized cleanup, one rerun passed as above. This is measured failure, not a theoretical race.

F-01 passes: `_registry_errand` strict-reads before release and routes unreadability to `_unreadable_registry` (`validate-digest.py:2306-2342`). `_b1898_unreadable_registry_holds_the_parent` verifies parent PASS refusal (exit 2), recovery guidance/BLOCKED escape, leaf behavior, and exact corrupt-parent bytes preservation (`test-validate-digest.py:5850-5877`); all are included in the measured 81/81.

## Fail-first and SC evidence

| SC | current evidence | fail-first evidence |
|---|---|---|
| SC-01 | direct preservation `test-validate-digest.py:5712-5760`; serial wrapper green above | direct red retained at `notes/review-harness-qa-c0.md:23`; **no qualifying red for the new suite wrapper** |
| SC-02 | unit command above | `notes/review-harness-qa-c0.md:24` |
| SC-03 | validator command above | `notes/review-harness-qa-c0.md:25` |
| SC-04 | unit command above | `notes/review-harness-qa-c0.md:26` |
| SC-05 | retained port mutant evidence | `notes/review-harness-qa-c0.md:27` |
| SC-06 | validator 81/81, including F-01 | `notes/review-harness-qa-c0.md:28` |

## Finding

- **F-QA-01** — `kind: substance`; `scope: task`; `severity: high`; `reader: harness-qa`; `owner: T-03/T-04`. Scenario: two validator-panel or CI workers invoke `python3 tests/integration/test-suite-claim-preservation.py` while a first worker has seeded `BUG-1898-suite-sentinel`; the second hits the PM one-flight refusal, dereferences `None`, exits 1 before `finally`, and leaves its already-created non-PM sentinels. Independently, a validator regression that releases claims in its actual hook-root can remain unproven because the invoked suite directs its hook subprocesses to fresh `HARNESS_PROJECT_DIR` roots rather than the sentinels' registry. Make the proof isolated/reentrant and establish a retained baseline/mutant red that exercises the same sentinel registry before closing SC-01.

## Principles applied

- **Build the Lever:** reran the shipped preservation harness and its real validator subprocess rather than hand-simulating row preservation; its measured race and disconnected hook roots are reproducible from the cited commands.
