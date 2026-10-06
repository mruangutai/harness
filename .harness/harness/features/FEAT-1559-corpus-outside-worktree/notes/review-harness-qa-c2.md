# QA gate — FEAT-1559 cycle 2 (run validate-c1-validator, pin 42856abb)

**BLUF: PASS.** Both required kinds are green at the exact pin in an ordinary full clone (unit exit 0,
52 files; integration exit 0, 80 files; 0 failing files). The three QA-relevant c1 must-fixes are closed
by tests that fail under reversion, and each was re-reddened here. G-1 and G-4 stay as
evidence-bound residual limits, not closed and not blocking. Nothing was edited in any tracked tree.

## Subject and identity
- Pin via `pinned-checkout.py add --feature FEAT-1559-corpus-outside-worktree --run-id validate-c1-validator --persona harness-qa --sha 42856abb91a3a87b9f27ebc933cc363a900afd3d` → HEAD `42856abb91a3a87b9f27ebc933cc363a900afd3d`, status clean. It was an **unconverted linked worktree** (120 `.harness/*/features` entries, owner hooks pre-1559), so it correctly cannot be the exact-pin suite subject: the plan (T-05) requires an ordinary full non-linked clone, and a layout-refusal there is the designed structural result. Helper was used first; only then a fallback.
- Fallback: `git clone --no-local --no-checkout <owner>` + `git update-ref --no-deref HEAD 42856abb…` + `git restore --source=HEAD --staged --worktree .` (no `git checkout`; guard refuses it) at `/tmp/f1559-qa-c2-c35x/clone`: HEAD `42856abb91a3a87b9f27ebc933cc363a900afd3d`, shallow false, `.git` a directory, 117 feature dirs, status clean. `worktree-state.py --verify --json` → exit 0, class `plain-clone`, findings `[]`. Runner invoked with `env -u HARNESS_AGENT_TYPE`.
- Base relation: full review range base `e8d868f7…` = `merge-base(pin, origin/main)` = `origin/main` (is ancestor; 20 commits). Fix delta 0e8301a5..42856abb = 2 commits (`33d10434` pin-note, `42856abb` fix). Whole-feature diff e8d868f7..42856abb touches 0 paths under any other feature directory (51 non-FEAT-1559 paths: production/tests/docs) — SC-11 independently re-derived.
- Cleanup: pin removed (`pinned-checkout.py remove`, 0 matching `git worktree list` entries and 0 dirs under `.pins`); sibling pins untouched; `/tmp/f1559-qa-c2-c35x` is disposable.

## Required kinds (harness.json) and results
All tasks T-01..T-05 `cross_module` → `unit` + `integration` both `always`; T-06 `docs` (abandoned) → none. component/ui/typecheck null/unresolved and no SC; functional/eval excluded (DEC-187); `locally_run` probes' `detect` untouched.

| Kind | Command (verbatim) | Exit | Discovery | Failing files | State |
|---|---|---|---|---|---|
| unit | `python3 .agents/skills/harness/bin/run-unit-tests.py --kind unit` | 0 | 52 files (`git ls-tree`: 52 `tests/unit/test-*.py`), 767 PASS lines | 0 | satisfied |
| integration | `python3 .agents/skills/harness/bin/run-unit-tests.py --kind integration` | 0 | 80 files (ls-tree 80), 2341 PASS | 0 | satisfied |

Non-failures: 4 `FAIL BUG-1290 5a/5b/5c` lines are `test-factory-claim-mutation.py`'s own mutation proof (repo G-09). Announced skips (not credited): live conversion-manifest validation (#2101), real-owner caller comparison in a plain clone. Clone status porcelain 0 after both runs.

Counts: 52/80 are the real discovery set. The original receipt's 54/86 were `^PASS test-` line counts; the appended erratum in `notes/non-regression-receipt.md` (original lines left) states exactly that and matches my count; I re-derived 52/80 from the tree and from the runner. It is a historical-count correction, not current failure evidence.

## c1 must-fix closures (independent, by mutation at the pin; clone restored `git status` 0 after each)
| # | Closure | Natural/mutant red here | Tier |
|---|---|---|---|
| 1 | SC-04 `check-plan-routes` missing landed dir (`require_landed`, :803) | (a) production files restored to 0e8301a5, tests at pin: `test_check_plan_routes_refuses_a_missing_landed_directory_by_name` and `…_in_a_full_clone` both `0 != 2`; (b) removing the `require_landed` call: same two reds | natural pre-fix RED against the c1 production + mutant |
| 2 | `board_lifecycle._feature_dirs` (:456-459) discovery incomplete / landed directory | local-glob mutant: `BoardStatus.test_a_landed_feature_absent_here_is_audited_against_its_cards` + `test_a_broken_layout_reports_the_corpus_unreadable` red; layout-refusal-dropped mutant: `test_a_broken_layout_reports_the_corpus_unreadable` red | mutation (production unchanged since c1, so no natural pre-fix red exists; tests are new) |
| 3 | `check-decision-anchors.py:141` owner routing + exit 2 | local `count_lines(candidate)` mutant: `DecisionAnchors.test_another_landed_features_file_is_counted_in_the_main_corpus` and `test_an_unreachable_main_corpus_exits_two` red | mutation |
| 4 | Nine grade failures | not QA-graded; behaviour preserved: both kinds green at pin (the pre-existing `test-worktree-state*`, `test-feature-corpus*`, `test-check-instruction-paths`, `test-corpus-non-regression` suites exercise the extracted helpers) | suite |
| 5 | L-1 count erratum | verified above | record |

`test-feature-corpus.py` = 24 tests, OK (clean clone). Decision-anchor and board mutants are the first time those two consumers are bound; mutants were applied by me, so only my evidence has examined them beyond the author's (second-reviewer independence not applied to the test design).

## Per-SC test and fail-first (every `verify: automated` SC)
Unchanged from c1 except the rows below; tiers are those stated in `review-harness-qa-c1.md` (bootstrap, assertion, mutant).
- SC-01 `test-worktree-state.py`, `-hooks.py`; SC-02 `test-feature-corpus.py` (reads, guards, Anchors added), `omp-hooks.test.ts`; SC-03 `test-check-state-corpus.py`; **SC-04** `test-check-state-corpus.py`, `test-feature-corpus.py` Discovery/Board (new), `test-feature-corpus-census.py`; SC-05 `test-feature-corpus-discovery.py`, `test-check-state-corpus.py`; SC-06 `test-corpus-non-regression.py` + plain-clone runs above (positive control, no fail-first possible); SC-07/08/09 hook/state suites; SC-12 `test-corpus-real-owner.py`; SC-13 six unit files.
- SC-10 deferred-by-ruling (#2101); SC-11 inspection (re-derived); SC-14 inspection.

## Residual limits (assessed, not closed, not blocking)
- **G-1 (SC-13/SC-01) — mutant survives at the pin.** `feature_corpus.py:504` `_maximal_outside_features` kept-ancestor clause replaced with `return set(under)`: unit `test-worktree-state-rules.py` (15 tests), integration `test-worktree-state.py` (23) and `-hooks.py` (8) all exit 0. `DIRS` (rules.py:23-31) has no kept `.harness` dir with a kept child. Per ruling it is an advisory negative-case gap (nested listing changes no materialised file, so no behaviour is wrong); stays in `coverage_gaps`.
- **G-4 (T-03) — inconclusive.** `check-domain.py:2706` `if False:` mutant: `tests/integration/test-check-domain-worktree.py` exit 0 in isolation, full unit pool exit 0 again (no red this time). The c1 single pool-only red was not reproduced; nothing here proves a defect or binds the skip. Assurance limit retained; not credited as covered.
- **SC-13 historical pre-production evidence (PM/IRC question).** No new pre-production capture exists. Bootstrap/import reds remain the only retained pre-change failure for most unit predicates; the discriminating evidence is my c1 present-state per-predicate mutants (unit files red at file:line, recorded in c1) plus the new natural RED in (1) above. This cycle did not retake the c1 SC-13 unit mutants (the unit files and their production predicates `derive_cone`, `identity`, `claiming_segments`, `reached_feature_dirs` were refactored by extraction in the fix: a refactor proof is the unchanged-green suites, not a new fail-first). Tier: constructed mutation, own reproduction; no natural predicate RED.
- Unit/integration passes are a plain-clone result; the real-owner non-skipped SC-12 run needs a converted caller (post-merge); a pre-merge pin refuses structurally by design (c1 N-1, unchanged).

## Gate fields
suite pass; failures 0; matrix_ok true; kinds unit/integration satisfied; coverage_gaps = G-1, G-4, SC-13 historical-evidence limit.

## Principles applied
- Verification is the product (rule 7): suites not credited as met SCs; each closure re-reddened by mutation.
- Never falsify the record (rule 15): survivor (G-1), inconclusive (G-4), tiers and the count erratum are recorded as found.
- No more specific than necessary (rule 6): G-1/G-4 stated as the weakest claim the evidence supports.

## Cleanup receipt
`/tmp/f1559-qa-c2-c35x` (clone and logs) was removed with `rm -rf` after the runs; verified absent (`ls` → no such file). The pin `FEAT-1559-corpus-outside-worktree--validate-c1-validator--harness-qa` was removed via `pinned-checkout.py remove`; 0 entries remain under `.pins` and in `git worktree list`.
