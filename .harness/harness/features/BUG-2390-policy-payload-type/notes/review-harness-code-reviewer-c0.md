# BUG-2390 code review — c0

FAIL: T-01 repairs the payload contract honestly, but SC-02's required contract-mismatch red and test-only pin are not evidenced.

Reviewed `51c2efebdd8ada060295c5b4adda68d93aabb27a..79db636b50aa6547edb2b16591f7c26c721f0b47`; authored code `9eb07b4f..369096a4`. Pinned source has no later two-file changes. No human-tagged commits; only feature metadata is dirty. No tests, builds, linters, formatters or mutations run by this reader.

## Stage 1 — specification

- SC-01 inspection passes: `.omp/extensions/harness-hooks.ts:49-56,410,431,525,971-974,1686` models object/array payloads, narrows arrays and forwards the actual ops list. `tests/unit/omp-hooks.test.ts:38-44,181-189,228,3590,3615` checks object access and widens both fixtures. Object-only callbacks receive checked objects (:380,397). No relocated array-as-object cast found; the six inherited payload `as any` reads remain, as authorized. The inherited runner-level `as any` (:3647) does not change the widened runner's payload declaration. The apology is replaced truthfully (:2161-2162).
- **F1 — substance, med, T-01; SC-02 mismatch:** pinned `notes/receipts/T-01-red.txt:1-6` reports only TS2614, missing `PolicyPayload` export, against baseline plus an unidentified test-only working tree. It contains neither the promised union-versus-object runner incompatibility nor a test-only commit pin. Missing an imported declaration proves declaration presence, not acceptance of arrays by the production runner contract. REASONED failure scenario: keeping the union export while restoring object-only production signatures and the old member-ops cast would not invalidate a fake that accepts the wider union; wider callback parameters remain assignable to a narrower callback contract. The recorded red therefore does not discriminate the repaired contract defect. Must fix: supply genuine, pinned contract-discriminating static evidence for T-01, preserving the historical failure honestly; any replacement of the signed historical requirement needs explicit approval, not a retrospective claim that TS2614 measured it.
- SC-03: pinned receipts report 214 pass / 0 fail / 1553 assertions for baseline and completed working tree. Diff preserves tests and assertion values; this is regression evidence, not runtime red. Its shared SC-02 discrimination remains unfulfilled.
- Verify-message apostrophe repair preserves acceptance. `opsList`/`refuseApply: never` shares the existing refusal text without a cast. Neither this departure nor the retained six `as any` reads weakens SC-01. No implementation scope creep found.

## Stage 2 — quality

No additional shipped-code defect found. Serialization and reporting wrappers are unchanged (:527,542-546); refusal precedence and broad-gate unavailability remain intact (:413-448). Member-ops is in neither narrow nor broad gate set (:372-385); the new array guard does not bypass an applicable member-ops gate. Malformed ops still refuse before core invocation (:1667-1668,973). Mechanical code grade: `n_a` (no changed Python paths).

## Principles applied

- Type System Discipline: checked both fixture declarations and narrowing bodies, not merely absence of the literal double cast.
- Migrate Callers, Then Delete Legacy APIs: checked both fixture runners, callback seams and recorded-call declarations; no replacement compatibility shim added.

## Open questions

None. QA owns subsequent gate execution; no rerun requested to reconfirm the recorded TS2614 failure.
