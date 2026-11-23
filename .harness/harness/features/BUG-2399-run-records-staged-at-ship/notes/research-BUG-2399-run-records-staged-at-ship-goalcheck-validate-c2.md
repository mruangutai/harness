# BUG-2399 — goalcheck, validate c2

**PASS: both perspectives, SC-01–03 and the DEC-238 amendment are met. C1 MF-1 and MF-2 are resolved, not regressed.** This is a bounded delivery assessment, not a fresh QA gate receipt or ship authorization. No tests, historical failures, builds, linters or formatters were rerun; no source, tests, plan or approval changed.

Pin: `74e6896c6113f916efd9c5ceb24a7d60e7c5c0cd`; base: `9eb07b4f3cd235c234a10edddbfe5542c1e85fba`; c1: `9db1ba98209df49017e73fae13da56f3e240086c`. Code/document pointers below name pinned PRODUCT paths; notes are feature-local. All product inspection used `git show <pin>:<path>` or explicit base-to-pin/c1-to-pin diffs, never mutable HEAD. The pinned plan owns all five delivery files in T-01 and traces all three SCs. Current plan differs only in station status; its tasks, decisions, dispositions and approval match the pin.

## Perspective outcomes

- **PASS — operator:** SC-01 and SC-02 discharge automatic complete non-UI staging, explicit missing-evidence reporting and nonmutating previews. Traversal failure now blocks before pruning/staging rather than silently omitting records (pruner:178–200,228–243; test:194–224,239–296).
- **PASS — code maintainer:** SC-03 discharges instruction alignment and unchanged pruning/safety behavior; SC-01/02 supply genuine failing-then-passing regressions. The historical removal clause is vacuously satisfied by explicit operator ruling, not by an invented removal (notes/answers-2026-11-23-c1-ruling.md:5–8).

## Criterion evidence

| Criterion | Verdict / method | Evidence |
|---|---|---|
| SC-01 | met / automated | Pinned tests/unit/test-prune-run-evidence.py:194–224 compares the complete recorded-run non-UI path-to-index-blob map, including kept/pruned runs, nested qa manifests, panels and acceptance files; excludes UI/unrecorded content and checks preview index/file immutability and repeat execution. Symlink staging assertions:348–367. C1 QA note:9–18 records 36 passing checks and audits original base failures; notes/red-first-T-01.md:15–24,53–84 records genuine staging assertion failures. Its c1-fix section:139–182 binds the exact current pruner/test hashes to 40 PASS, zero FAIL/SKIP, including unreadable-subtree failures before mutation. |
| SC-02 | met / automated | Pinned test evidence_refused:239–245 asserts exit 2, both missing paths and unchanged files/index in prune and preview; evidence_complete:248–268 restores paths and asserts successful digest staging. Pruner:165–169,217–237 checks absence before mutation. C1 QA note:15–18 and red-first note:20–24,73–84 audit base rc=0 assertion failures, not setup failures; the exact-subject c1-fix green receipt includes these unchanged tests. |
| SC-03 | met / inspection | Operator ruling:5–8 resolves only the removal clause. Pinned .omp/commands/harness-ship.md:43–59 retains both invocations and the existing human ship-commit message, explicitly including automatically staged records. C1 reviewer note:11–13 covers preserved selection/refusal/symlink semantics; direct base-to-pin inspection and AST comparison confirm unchanged _passing_validate_runs, keep_set, _ui_targets, _prune, _has_review_pin and _load_record. Pruner:207–208 prevents preview Git writes; test:194–201 protects every fixture file and index byte. DECISIONS.md changes only the ship bullet; index changes only seven subsequent +4 line anchors. |

## Decision-disposition outcome

**DEC-238 amend — met / inspection / T-01:** plan decisions_affected[0], clause “Ship keeps the record and drops the rest”, successor D-01. At `74e6896c6113f916efd9c5ceb24a7d60e7c5c0cd:.harness/harness/docs/DECISIONS.md:8058–8070`, the rewritten bullet states all non-UI retention, automatic force-staging and exit-2 refusal naming all absent cycle_evidence paths. Abandon and other bullets are unchanged. Keep rows DEC-174/179/225/254/187 are skipped; no strike rows exist. This grades the actual replacement, not merely a DEC mention (DEC-188/205/254).

## C1 must-fix reconciliation

- **MF-1 — resolved; substance; owner T-01; SC-01.** Pruner:186–188 supplies os.walk onerror; :196–200 collects all traversal errors; :238–243 reports them and exits 1 before either mutation, including dry-run. Pinned test unreadable_cases:282–296 uses chmod 000 on recorded qa/; unreadable_checks:271–279 asserts exit/message and unchanged index/UI. The pinned red-first c1-fix receipt reports three genuine failures on c1 and four new passing assertions on the fix without a SKIP. Resolution is an inspected implementation repair plus hash-bound execution evidence, not reliance on the ruling's assertion that it was fixed.
- **MF-2 — resolved by operator ruling; form; owner T-01; SC-03.** The pinned ruling expressly accepts the nonexistent historical removal target as vacuously satisfied and directs grading remaining clauses without amendment/reapproval. Those clauses pass above. This is an authority disposition, not a production repair. No old must-fix remains open or regressed; no new finding or scope question.

## Assurance boundaries

- No c2 QA assessment was available when evidence was collected. The c1 QA receipt proves execution at c1, not this pin. Current green evidence is the committed c1-fix execution receipt; PM independently measured SHA-256 matches: pinned pruner 55df0581…1a93ef, pinned test 5431b502…baa05d. C1 pruner/test and original base-pruner hashes also match their receipts. AST comparison shows every prior test function unchanged except main adding unreadable_cases; this is evidence transfer and receipt audit, not fresh execution or a current runner manifest claim. Permission coverage is the recorded uid-501 run, not root execution.
- C1 goalcheck:25 records a successful index-generation comparison at 3fa183eb6e4efa39dab012280bd42cfbf541d536. PM measured identical decision document, index and generator blobs between that commit and this pin. This supports regenerated-index inspection by input equivalence, not a claimed command run at this pin.
- C1 QA's advisory gaps remain unexecuted here: Git-add failure, unsafe ids, nested ui inclusion, linked-file exclusion, hash mismatch and escaped evidence paths. Shared implementation inspection is not dedicated behavioral coverage. None introduces a demonstrated unmet criterion.
- PRODUCT docs/spec.md, docs/decisions.md and docs/architecture.md are absent at the pin, as disclosed at signature; no substitute product guidance was invented. Open questions: none. Main/QA retain ownership of current-pin gate verification.
