# Build — T-03 and T-04 (main-session-direct, DEC-174) — 2026-11-22

## T-03 — CI and Dependabot

- `checks`: after the existing `oven-sh/setup-bun@v2`, add `bun install --frozen-lockfile`, then `bun run typecheck`, both before the unit suite, with no `if`, `continue-on-error` or path filter. `integration-shards`: a frozen install after its Bun setup, for the compiler regression; the typecheck step is not duplicated per shard. `integration` is untouched (no `name`, `needs: [checks, integration-shards]`, `if: always()`).
- `.github/dependabot.yml`: version 2, `bun`, `/`, weekly. No entries existed before.
- Local structure verify rc 0 (`receipts/T-03-verify.txt`). Remote execution evidence (the PR run with frozen install and compiler logs) is collected at validation/PR time.

## T-04 — capability before activation

**Capability (precondition, landed in a716db69 BEFORE any status flip):**
- Red (`receipts/T-04-capability-red.txt`): with code_grade.py unchanged, the new synthetic assertions fail behaviorally, not on import (test-code-grade: 2 failures, flagged kinds still classify; test-suite-layout: 3 failures). A config COPY with typecheck active and no flag shows the live breakage: `offenders` = both `.omp/extensions/*.ts`, and `hygiene_uncertified` = `**/*.ts` and `**/*.tsx`. The probe script is preserved as `receipts/activation-probe.py.txt`.
- Implementation: a `_classifies_tests(kind)` predicate in code_grade.py (running status AND `classifies_tests` default true), used by `_is_test_path`; `offenders()`/`select_control_candidate()` inherit it; test-suite-layout's `_running_kinds` honors the same flag. `.agents/skills` is a symlink to `.claude/skills`, so both code_grade spellings are one file (the verify asserts byte parity). The predicate was extracted after the inline clause dropped `_is_test_path`'s self-grade below 4.
- `classifies_tests: false` on typecheck in `.harness/harness.json` and `templates/harness.json`; template `cmd` stays null. `_test_kinds_note` does not enumerate kind fields, so it is unchanged.
- Green (`receipts/T-04-capability-green.txt`): both unit scripts rc 0; the flagged config copy has no offenders and nothing uncertified, and the positive control is still detected.

**Compiler regression and activation:**
- `tests/integration/test-typescript-typecheck.py`: tracked-.ts discovery; the four settled sources; every tracked .ts in the real `tsc --listFilesOnly`; no `@ts-nocheck/@ts-ignore/@ts-expect-error`; `bun run typecheck` rc 0 on the real tree; a temporary out-of-checkout copy passes clean and fails with one appended `never` poison in `.omp/extensions/digest-schema.ts` (rc ≠ 0, `error TS`, file named); the activation guard. A 40 s shared deadline makes a timeout a failure, and a missing bun or tsc fails.
- Red against the unresolved config (`receipts/T-04-regression-red.txt`): 7 PASS, 1 FAIL (the activation guard only), rc 1.
- Real tree passed `bun run typecheck` BEFORE the cmd was filled (`receipts/T-04-real-typecheck-pre-activation.txt`, with source blob ids and toolchain versions).
- Activation: `cmd: "bun run typecheck"`, `status: active`, `_reason` deleted; detect/exclude unchanged; `test_matrix` and `_matrix_provenance` byte-identical to 0bdcabbf (asserted by the verify).
- D-01: DEC-213 rewritten in two bounded places: the `tests/manual` paragraph (a static source check may read a manual source, never run it) and the governing-semantics clause (detection vs. classification; two consumers; the superset obligation scoped to kinds that classify tests). DECISIONS-INDEX regenerated (line offsets only). SPEC §5.3's verification-gap paragraph is replaced.
- T-04 literal verify rc 0 (`receipts/T-04-verify.txt`). The unit kind via `run-unit-tests.py --kind unit` gives rc 0 (64 files). `check-plan-routes.py`: 0 violations. `check-state.py`: rc 0.

**Expected post-build `plan-merge.py check` anchor failures (not defects):** `create: true` entries now exist, and two `quote:` anchors (`digestCalls` signature, SPEC gap heading) were rewritten by this build. Those anchors are plan-time existence checks against the base.
