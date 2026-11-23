# Operator signature — BUG-2390 — 2026-11-22

Signed by **fable-advisor** under the operator's delegated authority. Rework: 1 round / 45 min. Overrules: none.

> The plan matches the grilling ruling point for point:
> - `Dict | unknown[]` (Approach A);
> - an `Array.isArray` guard in `classifyPolicyRun`, vacuously safe because `expertise-merge.py` is in neither NARROW_GATES nor BROAD_GATES;
> - test-first red via test-only widening;
> - honest fixture narrowing with no relocated cast: one asserted helper that fails loudly on arrays, plus pinned-diff inspection for single casts that rg cannot see.
>
> The sole `as unknown as` across both files is harness-hooks.ts:1673. The baseline binding is sound: 9eb07b4f is the direct parent of main 9a818b46, and the diff between them touches neither owned file, so `MAIN_BASELINE_PASS_COUNT=214` applies unchanged and the ESCALATE condition is resolved. Exact pass-count equality is intended: the array path is already exercised, and SC-02's static red is the discrimination evidence.
