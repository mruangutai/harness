# PASS — diagnostic monotonicity closes T-01 / SC-01

Reviewed `3dd8bb677bb2936361e3952030fc24f15bf9afc6..3aa17de30917ca7eee9d5edb6ebc944e6dc45236`, excluding later record-only `d21cf97f`. Current feature.json agrees with the dispatch pin. Measured census: 73 changed paths, two Python source/test paths and 71 feature records; no canonical-reader inventory change, producer-format change, human-tagged commit, or tracked working-tree modification. Source and receipts read through immutable `git show`/diff; no tests, probes, grading, builds or linters executed.

## Stage 1 — spec compliance passes

- **SC-01 inspection:** `validate-digest.py:2499–2520` accumulates header names permanently. Producer `run_pool.py:107–113` emits a header, verbatim captured output, then its close. Same-name PASS, echoed headers and closes cannot remove a name; every subsequent genuine FAIL qualifies. `partition(" ")` retains filename spaces. Index selection and final enumeration retain duplicates and original combined-stream order rather than deduplicating text.
- **SC-01 inspection:** mutation lines remain the contiguous run above the producer note (`validate-digest.py:2523–2531`; `run_pool.py:127–136`). The conditional heading precedes the unchanged last-20-line slice; no-match output has only the tail. Nonzero refusal remains 2; success and unavailable-run branches are unchanged (`:2475–2492,2534–2547`).
- **SC-02 inspection:** the six former timeout=3 calls use the shared 30-second constant; rationale names FIFO, dangling symlink, 10,000-deep JSON and load headroom (`test-validate-digest.py:1025–1031,3033,3066,3286–3288,3316–3318`). Prior SC-02 acceptance remains intact. Existing selector reuse serves the BRIEF; the intake digest contains no amendments list, and the recorded selector amendment weakens neither SC. No inspection-only SC exists; citations above record the requested source checks.
- Round-3 operator ruling explicitly accepts possible over-listing; this is not an SC violation. Absent PRODUCT docs/spec.md, docs/decisions.md and docs/architecture.md remain absent guidance, not invented requirements.

## Stage 2 — quality and discrimination pass

The old close-pairing state machine is gone, with no shim or stale caller. The monotone set makes the invariant local and the helper has one coherent job. No new in-scope correctness or maintainability defect found.

Pinned `receipts/discriminate-c4.txt/.stdout` uses final tests against cycle-2 gate `b228c3a2`: only the echoed-header/same-name-PASS case fails, listing MUTATED but losing both FAILs. The final regression executes the genuine QA refusal path through RUN_UNIT_TESTS_BIN and asserts both complete FAIL lines (`test-validate-digest.py:6435–6449`). This directly discriminates the prior blocker, rather than merely asserting parser internals.

Pinned `red-c4.*` records exact-base production plus final regressions with the six original calls restored: 14 failures, including observed `[3,3,3]` at all six sites and actual blocked-call failures after watchdog intervention. Those post-kill fixture exceptions are not independent defect evidence; observed old budgets and reached real calls establish the defect. `green-c4.*` records all 17 selected cases passing, exit 0 in 10.82s, and the full test file passing in 23.17s. Diff inspection confirms `3c6fb908..pin` changes only receipts/simplify record, so these executed subjects are code-equivalent to the pin. These are supplied receipts, not my execution. Main supplied grading at the same code-equivalent fix: exit 0, PASSING 29, no FAIL rows; `code_grade: pass`.

## Retained nonblocking findings / scope census

- **substance / med, outside patch:** required unit-kind coverage remains absent, operator-disposed to #2281; matrix stays false. Selected/full-file integration evidence is not complete integration-kind coverage.
- **substance / low, accepted:** captured `FAIL name` after any header for that name can be over-listed, including within a passing block. This is the explicitly accepted diagnostic-accuracy cost, not a blocker.
- **substance / info, outside patch:** existing runner-launch/timeout fail-open remains unchanged; unavailable independent execution can leave a claim unverified. BRIEF excludes changing that policy.

## Principles applied

- **Delete First:** removing header/close pairing removes the state whose destructive updates caused the diagnostic loss; no replacement compatibility layer is retained.

Must-fix: none. Open questions: none. Authorized final literal verification belongs to QA: `python3 tests/integration/test-validate-digest.py --only run_bug2253_cases`.
