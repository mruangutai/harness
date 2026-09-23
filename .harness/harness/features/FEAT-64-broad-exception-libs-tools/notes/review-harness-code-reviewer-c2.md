# FEAT-64 code review — validate c2

## Disposition

**PASS.** Reviewed immutable `a4a3d7f8e9b91181fb6cc3ae058df8e02275d983..721b690e3578fbaba2b88d93774667d94ac4d8a3`. The only dirty tracked path was Harness-owned `feature.json`; production, test, and evidence claims below use the pinned objects. No `[harness:human]` commit is in scope.

## Stage 1 — spec compliance: PASS

The full 67-path union is accounted for: 18 production tools/libraries implement T-01..T-03; 20 tests cover typed failures, defect propagation, catch ceilings/mutants, and one-parse invariants; 29 feature/evidence objects carry the signed specification, receipts, prior reviews, and validation state. Every change serves SC-01..SC-08 or D-01..D-04; no scope creep, omission, or mismatch remains. Pinned inspection for SC-04 finds no change to `.claude/hooks/**` or `.omp/extensions/harness-hooks.ts`, and `board_lifecycle.py` remains baseline-identical. SC-05's moved rationales remain with their handlers, the copied bootstrap remains unchanged, and new explanatory prose is marked FEAT-64.

Prior-item regrade:

- **GC-64-04 — CLOSED.** `git diff --name-status a4a3d7f8..220feabb -- '.harness/**/*.yaml' '.harness/**/*.yml'` independently returns exactly three additions: `plan.yaml`, `runs/validate-validator/state.yaml`, and `runs/validate-c1-validator/state.yaml`. Running `test-harness-yaml-corpus.py` from an isolated archive of `220feabb` with `HARNESS_PROJECT_DIR` pinned to that archive reproduces `104 files`, `.harness=100`, teams `=4`. `notes/build-divergences.md` §A4 and `notes/byte-evidence.md` now agree on those bytes and contributors.
- **QA-64-01 — CLOSED.** `git cat-file -e 721b690e:.harness/harness/features/FEAT-64-broad-exception-libs-tools/runs/build-main-direct/digest.md` succeeds; the build digest is tracked at the review pin and was inspected as pinned evidence.

## Stage 2 — code quality: PASS

Started only after Stage 1 passed. The narrowed catches sit at the owning parser, subprocess, filesystem, fleet, or repository-module seams. Expected environmental failures retain their documented quiet/fail-open behavior, while unrelated programming defects escape. The two remaining broad catches are the specified shared `RepoModuleError` wrapper and unwired `hook_guard`; `BaseException` is used only to restore `sys.modules` before re-raising process-control signals. The route and handoff caches are cleared at their public execution boundaries, cache parse failures as failures rather than defaults, and eliminate duplicate reparses without a second loader or diagnostic. No compatibility shim, duplicated exception policy, dead branch, or new silent-failure path was found.

The changed tests bind real subjects and discriminating mutants: RuntimeError escape cases fail against the baseline broad handlers; catch-increase mutants name the changed file/count; the reduction mutant stays clean; route and handoff call-count cases distinguish one parse from two. The build digest makes no `## Principles applied` claim requiring separate falsification. `code-grade.py --base a4a3d7f8 --head 721b690e` reports 48 passing changed functions, no failure, and no grade-2 waiver.

## Verification

All three signed T-01, T-02, and T-03 command chains passed at the reviewed tree. The isolated `220feabb` corpus reproduction passed 16/16 with the exact `104/100/4` line. No formatter, linter, or unrelated project-wide suite was run.

## Findings

None.

## Principles applied

No craft leaf changed the disposition; the review is grounded in the signed criteria, pinned diff, direct evidence reproduction, behavioral tests, and mechanical grade.
