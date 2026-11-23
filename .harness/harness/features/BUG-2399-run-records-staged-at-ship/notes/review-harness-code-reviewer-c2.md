# Code review c2 — PASS

T-01 satisfies the inspected criteria; both c1 must-fix items are resolved. No new findings, spec violations or open questions.

Reviewed `9eb07b4f3cd235c234a10edddbfe5542c1e85fba..74e6896c6113f916efd9c5ceb24a7d60e7c5c0cd`, including fix delta from `9db1ba98209df49017e73fae13da56f3e240086c`. Source/test conclusions use pinned Git bytes, not mutable HEAD. Working-tree changes were confined to feature STATE.md/feature.json; active review pin matches dispatch. Human commit in scope: `6ad54d0f [harness:human] BUG-2399-run-records-staged-at-ship: operator signature (rework 1 round / 45 min, main-session-direct T-01)`.

## Stage 1 — specification

- **SC-01 / T-01:** pruner `_recorded_run_ids`, `_run_files`, `_stage_paths` and `_stage` (172–214) enumerate recorded runs recursively, exclude root UI and symlinks, and force-add literal NUL-delimited paths after pruning (242–243). Tests: 194–224 assert exact staged path/blob maps, UI/unrecorded exclusion, preview immutability and repetition.
- **SC-02 / T-01:** pruner:165–169 collects all missing evidence paths; 217–237 preserves unmatched-keep precedence and refuses missing evidence with exit 2 before mutation. Tests:239–268 cover multiple missing paths, unchanged files/index and complete evidence.
- **SC-03 inspection / T-01:** `.omp/commands/harness-ship.md:38–59` retains invocation placement, both commands and existing human commit, documenting automatic staging. Pruner:81–162 keep selection, pin refusal and UI/symlink deletion logic are unchanged in the base-to-pin diff; 207–208, 238–243 preserve mutation-free dry-run. `.harness/harness/docs/DECISIONS.md:8058–8072` changes only DEC-238's ship bullet; index changes are corresponding +4 line offsets. Operator ruling accepts the historical removal clause as vacuously satisfied without amendment/reapproval.
- All production changes serve SC-01/02/03 or D-01; remaining changed paths are feature records. No build amendments were supplied. Product `docs/spec.md`, `docs/decisions.md`, `docs/architecture.md` are absent at pin; no replacement guidance invented.

## Stage 2 — quality and old must-fix disposition

- **MF-1 resolved (substance, prior med, T-01):** pruner:186–188 passes `onerror=note`; `_stage_paths` aggregates errors across recorded runs (196–200). Main checks the complete error list and returns 1 at 238–241 **before** `_prune` or `_stage`, including dry-run. No partial staging manifest reaches mutation after a reported traversal error. Existing keep/missing-evidence refusals remain earlier.
- Regression binds the real CLI: tests:271–296 chmods a populated recorded qa subtree unreadable, checks exit/message in both modes and unchanged index plus a prunable UI sentinel. Removing the callback or delaying refusal until after mutation defeats these assertions. Historical c1 red/green receipt is audited, not rerun: `notes/red-first-T-01.md`, c1 fix section; pinned production/test SHA-256 match its green identities (`55df0581…a93ef`, `5431b502…a05d`). Receipt records uid 501, 3 assertion failures on c1 and 40 PASS/0 SKIP on fix. Root-mode permission skipping is explicitly disclosed, not treated as measured coverage.
- **MF-2 resolved (form, T-01):** `notes/answers-2026-11-23-c1-ruling.md` explicitly disposes of SC-03's absent historical removal target; remaining clauses inspected above. Neither item is open or regressed.
- Fail-open review found no additional concrete defect in traversal aggregation, refusal ordering, literal staging or link exclusions. Assertions cross the real CLI/index seam, with presence checks beside exclusions.
- Required pinned `code-grade.py --base 9eb07b4f… --head 74e6896c…`: **23 PASS**, no severity/reason-required records; `code_grade: pass`. No tests, builds, lint, formatters or historical failures executed. Runtime gate verification belongs to QA.

## Principles applied

- **Delete First:** accepted the local enumeration/preflight split without new modules or CLI surfaces; unchanged retention logic is reused rather than duplicated.
