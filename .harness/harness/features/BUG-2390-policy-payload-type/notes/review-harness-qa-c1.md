# QA gate c1 — BUG-2390 at 780f9138dc3423c45368aa5334f06bd2532e0e8f (run r-20261122-3-validate-validator)

**BLUF: PASS.** The c0 non-discriminating red is closed by a reconstructed red that I reproduced independently. The green pin holds: typecheck clean, 214 pass, 0 fail, 1554 expects, and no `as unknown as`. Production at the pin is byte-identical to 369096a4 (`git diff --quiet 369096a4 780f9138 -- .omp/extensions/harness-hooks.ts` exits 0).

## Phase 1 (BRIEF/plan only)
Expected coverage: (1) a static red that fails specifically on the runner contract, with the test-only pin immutable; (2) typecheck green at the pin; (3) hook suite count equals the main baseline (214), with no removed, skipped or weakened assertions; (4) no payload-path double cast; (5) the member-ops array assertion survives. Every item has coverage. The one gap is the runtime guard (see Gaps).

## Matrix
change_type `bugfix` → unit when `touches_runtime_code`. The diff changes `.omp/extensions/harness-hooks.ts`, so **unit is required**. Integration requires `fix_confined_to_tests_and_contract_docs`, which is false here, so it is not required and not run. Typecheck is active (`bun run typecheck`). `matrix_ok: true`.

## Runner scope (actual)
- Pin: `.claude/worktrees/.pins/BUG-2390-policy-payload-type--r-20261122-3-validate-validator--harness-qa`, HEAD 780f9138, clean, `bun install --frozen-lockfile` (7 packages).
- **unit** receipt: `run-unit-tests.py --kind unit --shard 1/1 --manifest <run>/qa/manifest-unit.json` → exit 0, 65 files, 8 workers, 24.01s. `tests/unit/test-omp-hooks.py` ran inside it (exit 0, 19.02s); it executes `bun test tests/unit/omp-hooks.test.ts`, so the glob and script-list check holds. tested_commit is 780f9138. I did not hand-edit the receipt.
- **typecheck**: run through the plan T-01 verify, not as a separate receipt. DEC-255 receipts cover only unit and integration.
- **integration**: not required, not run. No receipt was written for it.
- Plan T-01 verify, run verbatim with `MAIN_BASELINE_PASS_COUNT=214` (main baseline receipt line 3 reads ` 214 pass`): exit 0. `tsc --noEmit` clean; `214 pass`, `0 fail`, `1554 expect() calls`; `rg 'as unknown as'` exits 1.
- Environment: `HARNESS_AGENT_TYPE` unset for runs. The installed hook was not changed and I make no claim about it.

## SC-02 red recheck (independent)
- Detached pin at red 2a479efd: `bun run typecheck` exit 1 with `tests/unit/omp-hooks.test.ts(2166,53): error TS2345: Argument of type 'PolicyPayload' is not assignable to parameter of type 'Dict'` and `Type 'unknown[]' is not assignable to type 'Dict'`. This reproduces `notes/receipts/T-01-red-2.txt` exactly.
- Red production is `git diff 9eb07b4f 2a479efd -- .omp/extensions/harness-hooks.ts`: one insertion, `export type PolicyPayload = Dict | unknown[];`. Nothing references the alias there (`grep PolicyPayload` at red returns line 44 only), so the contract is object-only.
- The red test file is byte-identical to the pin's (`git diff --quiet 2a479efd 780f9138 -- tests/unit/omp-hooks.test.ts` exits 0). The only difference between red and green is therefore the production widening.
- At the pin the alias is used at three signatures (PolicyRunner payload, classifyPolicyRun, runPolicy; lines 56, 410, 525) and the red goes green.
- The c0 flaw (a union-accepting fake stays assignable to an object-only runner by parameter contravariance) does not apply: the new assertion passes a union-typed value to the production function in argument position, which is covariant and so can fail.
- Tier and class: reconstructed (post-hoc) red on immutable SHAs, approved by fable-advisor. It is a static, semantic type-contract red. It is not a natural pre-fix run and I label it as such.
- Scope of the red: it reddens on `classifyPolicyRun`'s parameter. Reverting only `PolicyRunner` or `runPolicy` is not separately probed, so those two seams are covered by the same alias and compile path, not by their own red. I ran no per-site mutation (O-06); that is a limit on this evidence.
- **SC-03** is a regression criterion and shares SC-02's static proof. No runtime red is claimed.
- **Runtime reach**: the new assertion at test line 2166 reaches the `Array.isArray` guard (hook line 429). Removing the guard would make `payload.tool_input` read `undefined` on an array and the result is unchanged, so the runtime assertion does not discriminate the guard. The discrimination is the type error only. I report it as unshown at runtime (O-05), not as useless.

## Assertion integrity
- Diff 9eb07b4f..780f9138 on the two files: 79 insertions, 51 deletions.
- `expect(` lines: 24 removed, 25 added: a one-to-one change in how payloads are read, plus the single new assertion. Zero `.skip`, `.todo` or `it(`/`test(` lines added or removed. Test count 214 equals the baseline; expects go from 1553 to 1554.
- Production diff has no `as any`, `as Dict` or `as unknown` cast added. The two removals are the array-as-Dict casts (`payload as Dict | undefined`, `params.ops as unknown as Dict`).
- The six pre-existing `(call.payload as any).tool_input` reads from c0 remain; they are outside the diff and are an advisory residual.

## Gaps
- Runtime test for the `Array.isArray` guard does not discriminate (above); the guard is type-proven only.
- Per-seam reds for PolicyRunner and runPolicy are unshown.
- The red is reconstructed rather than natural; the original `T-01-red.txt` (TS2614, signature-absent) is retained unchanged and is not counted as discriminating.

## Principles applied
- Type System Discipline (read this run? No). Not cited, as I did not read the leaf.

## Cleanup
Pins `...--harness-qa-red` removed after the reproduction; `...--harness-qa` removed on return.
