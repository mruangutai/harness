# Fix c1 — BUG-2390 — 2026-11-22 (main-session-direct, rework round 1 of 1)

Validate c0 FAIL, finding T-01: the SC-02 red (`notes/receipts/T-01-red.txt`, TS2614 for a missing export) did not discriminate the runner contract. The code reviewer showed, and the advisor confirmed with a tsc probe, that a union-accepting test fake stays assignable to an object-only runner (parameter contravariance). Widening the fixture alone can never go red.

The disposition is from fable-advisor under the operator's delegated authority, and it is the explicit approval the digest asked for. SC-02's requirement is kept, and its evidence is reconstructed post hoc:
- **(a)** One assertion was added inside the existing FEAT-2225 member-ops test (`omp-hooks.test.ts:2163-2166`): `hooks.classifyPolicyRun("merge-gate.py", <recorded ops list>, <failed proc>)` is not blocked. It type-checks only if `classifyPolicyRun` accepts `PolicyPayload`, an argument-position (covariant) check, and at runtime it reaches the new `Array.isArray` guard on the narrow-gate failure path. Tests stay at 214 with 0 fail. Assertions go from 1553 to 1554, an addition with nothing removed or weakened.
- **(b)** Red commit `2a479efd`: production is main's object-only `harness-hooks.ts` plus only `export type PolicyPayload = Dict | unknown[]`, an alias no signature references (shown in the receipt). `bun run typecheck` fails with TS2345 at `omp-hooks.test.ts(2166,53)`: `PolicyPayload` is not assignable to `Dict`. Receipt: `notes/receipts/T-01-red-2.txt`.
- **(c)** Green commit: production restored to the widened contract, identical to `369096a4`. The plan verify passes: typecheck clean, 214 pass, 0 fail, 1554 expect() calls, no `as unknown as`. Receipt: `notes/receipts/T-01-verify-2.txt`.

`notes/receipts/T-01-red.txt` is kept unchanged as the original, non-discriminating record.
