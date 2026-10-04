# QA c6 exact-pin gate — BUG-1898

**BLUF: PASS.** At `47b345fe65e992e07386de717f43b9f8dd495dc8`, the corrected S3 oracle rejects every named nested-row mutant and retains valid direct/top-level cases; its final empty-row selector includes the nested id. Required runnable matrix evidence is green and retained automated-SC red-first evidence remains present.

## Scope and matrix

- Exact pin exists; `merge-base(origin/main, pin)` is `a4d72e7fc91d0cf7a568d9e2a5225465a422170e`. Canonical range has 71 paths. Focused range `7893fe7a23e493dcd1554e439f28e3c9832b4de4..47b345fe65e992e07386de717f43b9f8dd495dc8` has 10 paths; its sole executable delta is `tests/manual/probe-inflight-claim-lifecycle.py` (+15/-6).
- Phase 1 (BRIEF/plan only): cross-module T-01/T-02 require unit+integration; runtime bugfix T-03 adds unit; config-shape T-04 adds integration. The union is unit+integration. `inflight_claim_lifecycle_live` is locally_run outside the automated matrix.
- `bun test tests/unit/omp-hooks.test.ts` in an exact-pin archive: 99 pass, 0 fail, 273 expectations. `python3 tests/integration/test-run-unit-tests-kinds.py`: 8 PASS. Probe `py_compile` passed.
- Kinds: unit **satisfied**; integration **satisfied**; inflight_claim_lifecycle_live **locally_run** (final operator receipt recorded); component/ui/typecheck not matrix requirements. Coverage gap retained: BRIEF.md:42-45 declares no typecheck runner for the TypeScript hook.

## Independent c6 S3 oracle

- Synthetic import-and-call against the archive invoked `_governing_root`, `nested_ids`, `crossed_rows`, and `check_batch_ids`. It confirmed any-depth governance (`Nest.Probe.Deep` → `Nest`), gathered nested ids at any depth, and accepted only `Nest.Probe` with `harness-eng-lead` and parent `Nest`.
- The c5 `Nest.Probe.Deep` case, deeper otherwise-well-formed `Nest.Probe.Deep.More`, wrong persona, wrong parent, and mixed valid `Nest.Probe` plus deeper row each produced a crossed row and therefore fail S3 (the mixed case also violates the exactly-one nested-id check). Valid `Nest.Probe` and top-level `Nest`/`Plain` orchestrators pass.
- The synthetic call captured `governed_rows(['Nest', 'Plain', 'Nest.Probe'])`; `check_batch_ids` passes `governed + nested` at `tests/manual/probe-inflight-claim-lifecycle.py:474-475`. A complete selector-callsite search found no remaining singleton/crossed-row escape.

## SC evidence and residuals

- Automated SC-01..SC-06 retain current-test and pre-fix failing evidence at `notes/review-harness-qa-c0.md:23-28` (SC-01, 02, 03, 04, 05, 06 respectively). The c6 probe-only correction adds no automated SC.
- SC-07 is graded only from the final authorized entry: `notes/live-omp-probe.md:1105-1296` reports PASS 29/29, observed `Nest.Probe` as `harness-eng-lead` (`1249-1266`), and empty registry before/after (`1294-1295`). No live mode ran here.
- No must-fix finding. Historical `handoff-validate.md` seq-3 late succession (INV-43) remains a non-blocking residual.

## Execution hygiene

- Archive scratch created with `git archive 47b345fe65e992e07386de717f43b9f8dd495dc8 | tar -x`; it contained the temporary oracle only. No checkout source, test, config, plan, or receipt was changed; no formatter, linter, project-wide suite/build, or credentialled live probe ran. Scratch and generated cache were removed after evidence capture.

## Principles applied

- **Build the Lever** — the deterministic archive-local synthetic oracle exercised all adversarial and passing S3 selector shapes instead of accepting a manual trace.
