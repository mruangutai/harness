# BUG-2390 code review — c1

PASS: T-01's c0 SC-02 finding is closed by the explicitly approved reconstructed contract red; no remaining findings or must-fix items.

Reviewed `51c2efebdd8ada060295c5b4adda68d93aabb27a..780f9138dc3423c45368aa5334f06bd2532e0e8f`, plus c0 `79db636b50aa6547edb2b16591f7c26c721f0b47` to this pin. Active feature.json agrees with the dispatched pin; only feature metadata is tracked-dirty. No human-tagged commits. Inspected complete range paths and commit list; implementation changes remain the two T-01 files, with feature records alongside them.

## Stage 1 — specification

- SC-01 inspection PASS: `.omp/extensions/harness-hooks.ts:49-56,410,431-432,525,971-974,1686` honestly accepts/narrows object-or-array payloads and forwards the actual ops array. `tests/unit/omp-hooks.test.ts:38-46,181-189,228,3594,3619` widens fixtures and checked object reads; no relocated array-as-object assertion appears in the full diff. Fixture apology is truthful (:2161-2162). Serialization and forwarding wrappers remain unchanged.
- SC-02 / T-01 c0 finding CLOSED: independently diffed `9eb07b4f..2a479efd` production: its sole change is the exported `PolicyPayload` alias; signatures remain object-only. Red and final tests are identical. At red `tests/unit/omp-hooks.test.ts:2166`, the recorded payload union is passed directly into object-only `classifyPolicyRun`; `notes/receipts/T-01-red-2.txt:14-19` records TS2345 there, specifically `unknown[]` not assignable to `Dict`, exit 1. This addresses the c0 failure scenario (a widened fake alone remains assignable through contravariance). Reconstruction is post hoc, explicitly authorized by the dispatch/advisor, not represented as original chronological test-first evidence. Original TS2614 receipt is unchanged across c0-to-pin.
- SC-03: full baseline-to-pin diff retains test cases and assertions; c0-to-pin adds exactly one assertion and no production change. Pinned baseline receipt reports 214 pass / 1553 expectations; green receipt reports 214 pass / 1554 expectations, zero failures and typecheck exit 0 at `a6129082`. Independently diffed production `369096a4..780f9138`: empty. Green production therefore matches the original implementation; red-to-final tests also have an empty diff. QA owns execution at the new review pin; these are inspected historical receipts, not reader-executed results.
- No criterion omission, mismatch or implementation scope creep remains under the approved reconstructive disposition. The verify-message amendment does not weaken a success criterion; no build-lead amendment list or dev principle claim adds another obligation.

## Stage 2 — quality

No additional shipped-code defect found. `.omp/extensions/harness-hooks.ts:414-448` preserves refusal precedence and broad-gate unavailability; member-ops is absent from both gate sets (:372-385). Array narrowing does not skip an applicable member-ops refusal. Invalid ops still refuse before forwarding (:1667-1668). The added assertion calls the real classifier with a recorded array and failed narrow-gate process, then checks literal `blocked: false`; returning undefined would fail. Its static mutant is the pinned object-only reconstruction, which the receipt shows reddens. It is not independent runtime proof against removing only the array guard, nor is runtime red required by SC-03.

Mechanical grader explicitly bound to NEW pin: `code-grade.py --base 51c2efebdd8ada060295c5b4adda68d93aabb27a --head 780f9138dc3423c45368aa5334f06bd2532e0e8f` returned `PASSING: 0`. No changed Python paths: `code_grade: n_a`. No tests, builds, linters, formatters or mutations executed by this reader.

## Principles applied

- Type System Discipline: judged checked narrowing and all affected runner declarations, rather than treating a missing-export red or cast-absence grep as contract proof.

## Open questions

None. Findings: none. Remaining verification belongs to QA's required pinned run.
