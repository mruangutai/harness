# FEAT-1928 current verification

Main-session-direct execution (DEC-174), 2026-10-04. Final code-only candidate: `4379809b1ce7e37e89407b2ade7912abc898fed9`. Subsequent evidence/record commits must not change the seven live under-test file hashes recorded in the receipt.

## Executed commands and observed outcomes

From this feature worktree:

```sh
python3 .agents/skills/harness/bin/run-unit-tests.py --kind all
bun test tests/unit/omp-hooks.test.ts
python3 tests/manual/probe-digest-object-contract.py --provider openai --timeout 900
python3 tests/manual/probe-digest-object-contract.py --verify --verify-receipt .harness/harness/features/FEAT-1928-digest-object-contract/notes/live-digest-object-probe-current.md
```

- Complete Python pool at `4379809b`: all 120 files passed; eight workers; 112.95 seconds wall. Host output `artifact://209`. Includes the exact-release sentinel preservation and intentional persona-wide-release mutation check, both passing. The preceding pool at `27ea2206` also passed all 120 files.
- Hook suite after the shared-reference simplification at `27ea2206`: 105 passed, zero failed, 427 assertions. No hook/adapter/schema source changes occurred between that run and `4379809b`; later changes were probe/test refactors and captured evidence.
- Actual clean-tree live probe at `4379809b`: 18/18 checks, followed by 33/33 receipt-verification checks. Run interval: `2026-10-04T04:48:07+00:00` through `2026-10-04T04:48:34+00:00`; 43 transcript records. Main/child identities, strict injected bundle, explicit null, refusal component, same-job retry, accepted object, completion, and exit zero are re-derived from the transcript, not hand-authored.
- Installed OMP: `omp/18.6.0`, launcher `~/.bun/bin/omp`, launcher SHA-256 `3fdbf0d27eb43682b26a4bb487c34516b74d1dc12e373177ae3ecc37053cfd72`. Source SHA `89d2610993af69427574bde17791df63906ec4e5` is release-tag metadata, not binary identity.
- Plan anchor check: 76 resolved, zero failures. Instruction-path check: 61 files, zero violations. Canonical state checks passed before the two main-session commits.

Canonical provider suites ran once from `/Users/molchairuangutai/GitHub/oh-my-pi`, actual checkout HEAD `d0d1f81054a82d0e76d3f0bce42d8a706fe8cb10`:

```sh
bun test packages/ai/test/schema-normalization.test.ts packages/ai/test/schema-compatibility.test.ts packages/ai/test/anthropic-tool-schema.test.ts packages/coding-agent/test/tools/provider-schema-compatibility.test.ts
```

Result: 111 passed, zero failed, 221 assertions across four files. This checkout SHA is the suite-source identity, not the installed bundled-runtime identity. Initial missing workspace dependencies were resolved with `bun install --frozen-lockfile --ignore-scripts`; tracked upstream source was not changed.

## Grading and preservation

After refreshing `origin/main`, the repository-derived review base is `b8e9f9c8f451cfe4b4e211eb97093525b7872c1b`. Changed-function grading against both that base and reconciled local main `e0bb9814` gives 203 passing functions, eight grade-2 reason requirements, and no high findings. Explicit per-function reasons are in `code-risk-current.md`; the CLI still exits one for reason requirements, not a blanket PASS.

Throwaway behavior comparisons preserved the complete derived live evidence and all 18 predicate details on the original actual transcript, and all 36 original schema-validation inputs and accept/reject outcomes after splitting the test by schema family. Historical parity retains 291 fixtures, 14 planned accept/reject deltas, and zero unplanned mismatches; its removed throwaway generators remain available at the documented historical commit. The September 30 live receipt and transcript were not overwritten.

Independent validation and goal-check are still required. These main-session observations are evidence, not an independent panel verdict or a waiver of fail-first requirements.
