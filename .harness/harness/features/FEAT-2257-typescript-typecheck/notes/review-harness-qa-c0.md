# QA gate audit — FEAT-2257, pin 45626d79 (cycle 0)

**BLUF: PASS.** matrix_ok true; every automated SC (01/09/13) has a natural-RED receipt plus a green run bound to the pin. Nothing was executed locally (DEC-174, gate-only assignment). Execution evidence is the main-session receipts plus the remote PR #2386 run on the pinned SHA. Two advisory findings (below), none blocking.

## Phase 1 (from BRIEF/plan only)
SC-01: compiler red on the eight errors, then green; tracked-.ts vs compiler file-list parity; no suppression comments; one poison fails the command. SC-09: hook suite unchanged in assertions and counts. SC-13: synthetic unit asserts, red before the filter; config-copy offenders/hygiene reproduction before activation. No Phase 1 expectation lacks a test (see advisory A-2 on discrimination).

## Matrix (floor)
- Tasks T-01..T-04 are all `change_type: config` → `always: []`, `when: integration if touches_config_shape`. The diff changes the `typecheck` kind's shape in a config a gate reads (cmd/status/_reason removed, new `classifies_tests` key): **integration required** → satisfied.
- Added by QA (permitted): T-04 changes runtime logic (`code_grade._classifies_tests`, suite-layout filter) → **unit** also required → satisfied. Advisory A-1: T-04 is labelled config; it is logic/cross_module in substance.
- test_matrix and _matrix_provenance byte-equal to immutable base 0bdcabbf (checked by `git show` + json compare, read-only). Only `test_kinds.typecheck` differs.
- `typecheck` kind (active, `bun run typecheck`) is not in the matrix; it is compiler static coverage, reported separately from unit/integration discovery.

## Kinds
|kind|state|evidence|
|---|---|---|
|unit|satisfied|CI run 45071766676 `checks`/Unit suite at pin: test-code-grade.py exit 0, test-suite-layout.py exit 0, test-omp-hooks.py exit 0 (186 tests locally pre/post, 1465 expect()). Local pre-simplify receipt T-04-verify.txt: unit kind rc 0, 64 files (build note).|
|integration|satisfied|shard 2/4 selected `tests/integration/test-typescript-typecheck.py` by directory discovery, exit 0, 2.36s; shards 1–4 and aggregate `integration` pass.|
|typecheck (not matrix)|satisfied as compiler coverage|CI `Typecheck` step success after frozen install (typescript@7.0.2, @types/bun@1.4.5, Bun 1.4.5) on merge ref c42cb7a (pin merged into df2f58ae). Compiler file-list parity is asserted by the integration test, not by discovery counts.|

## Remote PR #2386 current pin
`gh pr view`: headRefOid = 45626d79 (OPEN, MERGEABLE). Run 45071766676 (event pull_request, headSha 45626d79) conclusion success: checks, integration-shards 1–4, integration all pass. Superseded run 45071452185 (SHA 4cc44d64, failure at repo-state) is NOT used. Step order in `checks`: Install Bun → frozen install → Typecheck → unit. Merge-tree checkout confirmed in log ("Merge 45626d79 into df2f58ae"). Each shard has the frozen-install step. SC-03/06 inspection is PM's (ItchyYak); this is the raw pointer.

## fail_first (all natural RED, receipts under notes/receipts/)
- **SC-01** — `T-02-red.txt`: `bun run typecheck` at 0eb5d06e before any edit, rc 1, exactly the eight settled TS diagnostics (semantic red). Regression `T-04-regression-red.txt` (HEAD a716db69, unresolved config): 7 PASS / 1 FAIL (activation guard) rc 1 — red only for the activation shape; its compiler checks were already green after T-02.
- **SC-09** — compiler red = `T-02-red.txt` (kept separate, per BRIEF); runtime non-regression = `T-02-hooks-baseline.txt` (186/0/1465 before) vs `T-02-verify-green.txt` (186/0/1465 after) and CI exit 0 at pin. Diff of omp-hooks.test.ts is 3 hunks (generic `digestCalls`, `as const`, `unknown` map): no assertion removed/changed, no suppression, no `any`.
- **SC-13** — `T-04-capability-red.txt` (HEAD a9bcb3f9, code_grade.py unchanged): test-code-grade 2 behavioral failures, test-suite-layout 3 behavioral failures (not import errors) rc 1; config copy with flag absent shows offenders = both .omp extensions and uncertified `**/*.ts`,`**/*.tsx`. Green: `T-04-capability-green.txt` rc 0, flagged copy empty, positive control still detected; the pre-capability receipt precedes the activation commit 4cc44d64. The "absent/true keeps True" assertions pass both before and after (baseline guard, discrimination not claimed).

## sc_evidence pointers
- SC-01: tests/integration/test-typescript-typecheck.py (coverage `check_coverage` :73, suppression `check_no_suppression` :82, poison `check_poison_fails` :95; CI shard 2 exit 0).
- SC-09: tests/unit/omp-hooks.test.ts via tests/unit/test-omp-hooks.py (CI exit 0 at pin).
- SC-13: tests/unit/test-code-grade.py and tests/unit/test-suite-layout.py (classifies_tests cases; CI exit 0 at pin).

## Deviations judged
1. **T-02 `unknown` payload comparison (omp-hooks.test.ts:~2150): accepted.** Runtime identical, same `toEqual` and values, recorder untouched; widening to `Dict | unknown[]` would touch 29 reads plus an out-of-scope production cast. It departs from plan intent ("fixture record should represent member-ops arrays truthfully"); the departure is recorded in build-T-01-T-02.md. Weakest sufficient, no finding beyond advisory A-3.
2. **README `bun update --latest typescript @types/bun`: accepted.** Satisfies SC-11 ("bun update … commit … rerun"); the stated reason (plain update keeps exact pins) is true of Bun semantics. Evidence is a scratch-project run recorded only in the build note, no receipt file (A-3).
3. T-01 `files`/verify amendment (untrack stray node_modules vitest cache, assert `git ls-files node_modules` empty) is ledgered in feature.json judgements; receipt T-01-verify.txt rc 0; `git ls-files` shows only the four .ts sources and node_modules ignored.

## Findings (advisory; owner = main-session-direct build, T-04/T-02)
- **A-1 (T-04, low):** change_type `config` understates a logic change (code_grade.py, suite-layout filter). The unit floor was met anyway. Not a gate failure.
- **A-2 (T-04, low):** integration coverage and suppression assertions were never shown red (they passed on creation); only poison discrimination and the activation guard have behavior. Discrimination is unshown, not disproved (e.g. no recorded run dropping a source from tsconfig `include`). `.omp/**/*.ts` in tsconfig include is what makes the dot-directory sources covered.
- **A-3 (T-02/T-01, info):** the README bun-update claim and the pre-pin local rerun after the simplify commit 45626d79 (test-suite-layout.py change) are in notes only, no receipt file. The pin's own CI exit 0 for test-suite-layout.py/test-code-grade.py covers the latter.
- **A-4 (info):** local Bun 1.3.14 vs CI Bun 1.4.5 (setup-bun@v2 unpinned); the compiler is exact-pinned and passed on both, so no finding.
- Compiler static coverage is bounded: the typed surface excludes `pi`/`ctx: any` live-host API (accepted, SC-10/BRIEF gap); `.tsx/.mts/.cts` are not in tsconfig include but none are tracked.

## Not executed
No test, compiler, build or lint was run by QA (DEC-174 gate-only). Remote CI at the pin is the only pinned execution evidence.

## Principles applied
None cited from craft leaves; verification-rules protocol applied.
