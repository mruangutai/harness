# QA gate — BUG-2390 at review_sha 79db636b50aa6547edb2b16591f7c26c721f0b47 (run r-20261122-2-validate-validator)

**BLUF: PASS.** SC-03 holds with a green rerun and an exact baseline match. SC-02 holds with a static red that is real but weak. The code diff is behavior-preserving. No assertions were removed, skipped or weakened.

## Scope and checkout
- Managed pin: `.claude/worktrees/.pins/BUG-2390-policy-payload-type--r-20261122-2-validate-validator--harness-qa`. HEAD is 79db636b, clean, after `bun install --frozen-lockfile` (7 packages).
- Authored code is `git diff 9eb07b4f 369096a4` over the two files: 75 insertions and 51 deletions. 369096a4..79db636b touches neither file; it only adds records, a merge and a simplify note.
- Installed hook: none was changed. The candidate hook is tested only from the pin, and I make no claim about the installed hook.

## Phase 1 (from BRIEF/plan only)
Expected coverage:
1. Typecheck is green at the pin, and its red was a type-contract mismatch.
2. The hook suite count equals the main baseline (214).
3. The member-ops array-payload assertion survives.
4. No `as unknown as` remains.

Gap: no runtime test proves the new `Array.isArray` guard in `classifyPolicyRun`, or `opsList`'s refusal. That is acceptable for a behavior-preserving typing repair, because the existing suite exercises the narrow-gate path with object payloads. The array branch of `classifyPolicyRun` is reached only by member-ops, whose script is not a narrow gate. I did not verify that claim by reading the branch. See `coverage_gaps`.

## Matrix
- change_type is `bugfix`: `unit` if `touches_runtime_code`, and `integration` only if the fix is confined to tests and docs.
- The diff changes `.omp/extensions/harness-hooks.ts`, which is runtime code. So **unit is required** and integration is not.
- `typecheck` is active; its cmd is `bun run typecheck`.
- `unit` cmd is `run-unit-tests.py --kind unit`. It runs `tests/unit/test-omp-hooks.py`, which executes `bun test tests/unit/omp-hooks.test.ts` (confirmed in the output: "selected tests/unit/test-omp-hooks.py", then "PASS test-omp-hooks.py", 28.01s). The glob-versus-script-list check passes.
- Kinds recorded: unit `satisfied`, typecheck `satisfied`. Integration is not required and was not run. `matrix_ok: true`.

## Runs
1. **Plan T-01 verify, run verbatim** (`HARNESS_AGENT_TYPE` unset, `MAIN_BASELINE_PASS_COUNT=214`): exit 0. `tsc --noEmit` clean; `214 pass`, `0 fail`, `1553 expect() calls`; `rg 'as unknown as'` exits 1 (no match). Output is at `/tmp/q2390-verify.out` (ephemeral) and matches `notes/receipts/T-01-verify.txt` and `main-baseline-hooks.txt` byte for byte on counts.
2. **DEC-255 unit receipt:** `python3 <pin>/.claude/skills/harness/bin/run-unit-tests.py --kind unit --shard 1/1 --manifest <run>/qa/manifest-unit.json`. Exit 0, 65 files, tested_commit 79db636b. Receipt: `runs/r-20261122-2-validate-validator/qa/manifest-unit.json`. It is untouched by hand, and main commits it.

## Assertion integrity (SC-03)
I counted from the diff text, not the tool summary.
- Removed `expect(` lines: 24. Added `expect(` lines: 24, a one-to-one pairing by line. Each changed only in how the payload is read (`payload.x` to `payloadOf(call)?.x` or `objectPayload(call.payload).x`).
- Zero `.skip`, `.todo` or `it(`/`test(` lines were removed or added.
- Suite count is 214 at baseline and 214 at the pin.
- The member-ops assertion `toEqual([[ADD],[ADD]])` is preserved and now runs on the honest type (the `(call): unknown =>` annotation was dropped).
- The new `payloadOf` helper returns `undefined` for an absent call, matching the old `?.` reads.
- Production diff: `classifyPolicyRun` now reads `tool_input` only for object payloads. It uses `Array.isArray(payload) ? undefined : payload.tool_input`, so an array never reaches the narrow-gate command read. `opsList` refuses a non-list with the same `OPS_NOT_A_LIST` text `applyArgumentRefusal` returns, and it runs only after that refusal.

## Judgment: no relocated lie in the fixture
- `objectPayload` asserts with `Array.isArray` and throws loudly. It is a checked narrowing, not a cast, so the "array as object" claim is verified at runtime instead of hidden.
- Every typed read goes through it, and the rg gate finds no `as unknown as`.
- Six `(call.payload as any).tool_input…` reads remain at tests/unit/omp-hooks.test.ts:1014, 1028, 1030, 1278, 1279, 1292. They are pre-existing, outside the diff, and retained per the advisor and settled intake. They stay an unchecked object assumption, but an array there would throw a TypeError rather than pass silently, and they exist only on check-domain calls. This is an advisory residual, not a relocated lie.
- Narrowed casts such as `(objectPayload(payload).tool_input as Record<…>).task` are the old tool_input-field casts, preserved. They sit behind the asserted object, not around the payload.
- The `mergeGate` and `distillAuthority` option types keep `Record<string, unknown>` and receive `objectPayload(payload)`, so no object type was widened to cover an array.

## SC-02 static failure specificity
- `notes/receipts/T-01-red.txt` records head 9eb07b4f plus an uncommitted test-only working tree, and `TS2614: Module has no exported member 'PolicyPayload'`.
- The failure is a missing-export error from the test importing the new type. It is **signature-absent**: it proves the test depends on the new export. It does not show the brief's runner-contract mismatch (union versus Dict at the runner seam).
- There is no immutable test-only pin (no commit or SHA), so the red cannot be reproduced from a SHA. Typecheck is green at the pin (run 1).
- Verdict: a genuine non-zero typecheck before production changed, but weak. I record it as fail-first at the lowest tier, static signature-absent. I did not run a mutation proof. The check-domain hook denies source edits by QA even in a disposable pin, so discrimination beyond the static red is unshown, not disproven (O-05).
- This was reported to goalcheck (Validate2390.TightLemming) by IRC.

## Baseline equivalence
Mac Bun 1.3.14 reproduces 214 pass, 0 fail, 1553 expects. Baseline (main 9a818b46), T-01 verify and my pinned rerun are identical on all three counts.

## Open
- The `plan.yaml` verify at the pin is the apostrophe-repaired block (recorded deviation through the plan-merge amend ledger). I ran the repaired block verbatim.
- The `main-baseline-hooks.txt` head is main 9a818b46, while the pinned diff base is 9eb07b4f, a different commit. The counts agree, so I do not treat that as a defect.
