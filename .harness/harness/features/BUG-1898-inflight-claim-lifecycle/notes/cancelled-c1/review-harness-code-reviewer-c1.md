# Code review c1 — BUG-1898-inflight-claim-lifecycle

## Conclusion

Stage 1 **PASS**: prior F-01 and F-QA-01 are closed at pin `81dbd81d21b04b6fdcba2435d2e73a12ec72fd2e`. Stage 2 **FAIL**: c1 worsens production `_registry_errand` to mechanical grade 3, below the required production bar of 4.

## Stage 1 — spec compliance

Canonical range: `a4d72e7fc91d0cf7a568d9e2a5225465a422170e..81dbd81d21b04b6fdcba2435d2e73a12ec72fd2e`; c1 delta: `84c3a6cbe74c7c27337d4372a68be60fca834118..81dbd81d21b04b6fdcba2435d2e73a12ec72fd2e` (3 executable/test paths, +145/-10). No `[harness:human]` commit is in scope. The only dirty tracked path was Harness-owned `feature.json`; pinned source was read from the review SHA.

- **F-01 dismissed / SC-06 and SC-08 met.** `_registry_errand` strict-reads the returning run by exact id and then exact children before its only release write (`.claude/skills/harness/bin/validate-digest.py:2306-2345`). An unreadable registry sends a lead/orchestrator non-BLOCKED return to exit 2, permits BLOCKED as the repair escape, performs no release, and leaves leaf returns unblocked (`validate-digest.py:2290-2304`). This matches DEC-204's exact-id held-child promise and DEC-100's separate guard-crash pass-through. The focused suite measured 81/81 BUG-1898 cases passing, including byte-identical corrupt registry preservation, parent refusal, BLOCKED escape, and leaf pass-through (`tests/integration/test-validate-digest.py:5865-5897`).
- **F-QA-01 dismissed / SC-01 met.** The preservation proof enumerates every shipped `harness-*.md` persona, creates a real runtime-bound claim for each, invokes the real `test-validate-digest.py` subprocess, compares every seeded row exactly, and releases only recorded claim ids in `finally` (`tests/integration/test-suite-claim-preservation.py:31-75`). Measured result: all three checks PASS, 0 failures; the invoked validator suite also ended `ALL PASSED`.
- No scope creep, omission, or decision mismatch found across the canonical range. SC-07 remains `pending_operator_gate` and was not graded as a panel failure.

## Stage 2 — code quality

The lifecycle branches fail closed and no new silent release path was found. However, the canonical mechanical grade run exited 1: `_registry_errand` is cyclomatic 9, cognitive 9, ABC 20.2, **GRADE 3 / BAR 4 / RESULT FAIL / SEVERITY high** (`validate-digest.py:2306`). The new strict-read and unreadable handling pushed the already central coordinator below the production readability bar; a future edit must simultaneously reason about identity refusal, root resolution, two ownership reads, held-child refusal, own-claim absence, exact release, and release errors. Concrete failure scenario: when the next lifecycle condition is added, a maintainer can place it after the release branch or return `None` on its error path, allowing a dispatch-capable parent to release or pass despite an unresolved ownership condition—the same fail-open defect class BUG-1898 closes. Split the strict ownership decision from the release errand while preserving read-before-write ordering.

## Verification

- `python3 tests/integration/test-validate-digest.py` — PASS; 81/81 BUG-1898 checks; `ALL PASSED`.
- `python3 tests/integration/test-suite-claim-preservation.py` — PASS; 3/3 checks, 0 failures.
- `code-grade.py --base a4d72e7f… --head 81dbd81d…` — exit 1; one production grade failure above.

## Principles applied

- **Model the Domain:** exact run ownership, dispatch capability, unreadable state, and release remain distinct lifecycle states; the grade failure reflects too many of them being coordinated in one function.
- **Delete First:** no compatibility release path, persona fallback, or bulk cleanup survives beside the exact-id path.
