# BUG-1016 goalcheck — validate c3

**PASS by pinned inspection: both delivered perspectives satisfy the approved contract; R2's misplaced insertion is repaired, not waived.** This is a product/contract assessment, not a fresh automated gate measurement. QA's independent c3 execution remains required for consolidated validation.

Pin: `ef9cbce243444628d4ca74931be94a576e493dd5`; observed canonical range: `af2a958ab06c0d6fc026b363b59fc3147e3982f1..ef9cbce243444628d4ca74931be94a576e493dd5`. All implementation/test/document pointers below refer to `git show` at that pin, not moving HEAD. `H` = `.omp/extensions/harness-hooks.ts`; `U` = `tests/unit/omp-hooks.test.ts`; `R` = this feature's `notes/t01-receipts-main-session.md` at the pin. Pinned plan: T-01 traces SC-01..07; T-02 traces SC-07, with the four production/test/document files owned by those tasks. Task status is not evidence.

## Delivered perspectives
- **operator: pass** — SC-01..06 / T-01: effective relative inputs and omitted searches select the assigned worktree; multi-file edits use those same effective targets for guards; explicit destinations, refusal, silence and main-session/Bash boundaries are preserved. Assurance is the adapter boundary and inspected carrying tests, not live host/filesystem execution.
- **code maintainer: pass** — SC-07 / T-01,T-02: DEC-251 and its index row document all seven tools, the actual ast_edit paths array, one resolver, amended predicate, defaults, guards and host boundaries; implementation and regression assertions agree.

## Predicate and R2 closure
Re-read approved BRIEF Constraints, Relative filesystem predicate, and pinned DEC-251:8029-8041: trim surrounding whitespace, remove **one** outer double-quote pair, then classify nonblank / nonabsolute / not leading ~ / not leading scheme://; preserve original wrapper and excluded bytes. R1 remains resolved by operator amendment, not a new repair. H rootTarget:354-368 now computes insertion as leading-whitespace length plus one when quoted, instead of raw.indexOf(target). For raw three quotes, target is one quote and insertion is at 1; for four quotes, target is two quotes and insertion is also at 1. Thus the opening wrapper stays before root/, and the original target and closing wrapper stay after it [inspection-derived, not executed]. H rootedInput:377-403 shares this helper with edit section/MV rewriting, so the same repair reaches those callers. U:1347's named R2 regression asserts both exact quote-only outputs, quoted space/padded paths and quoted tilde/absolute/scheme exclusions. The c2→pin source/test/docs diff contains only this helper repair and regression; DEC-251 and the approved predicate are unchanged. This explicitly supersedes c2's overbroad completion claim rather than treating c2's green suite as R2 evidence.

## SC outcomes
Methods retain the BRIEF's declarations. “met” below is this reader's delivered-behavior assessment from pinned code/tests and retained discriminating receipts; it does **not** assert a c3 automated execution result.

| SC | Verdict | Method | Task-bound evidence at pin |
|---|---|---|---|
| SC-01 | met | automated/unit | T-01; H rootTarget/rootPathList/rootedInput:354-403; U:1320,1338,1347,1364 exercise six interfaces, list entries, R2, selectors and non-path/input preservation; R:8-10 records original named failures. |
| SC-02 | met | automated/unit | T-01; shared EDIT_TARGET/extractEditPaths H:77-88 and rootedInput:377-383, effective pre/post H:1177-1188,1457-1461; U:1417,1522 assert multiple sections/MV, quoted spaces, untouched hashes/body/line endings and original/revised guard destinations; R:13,20. R2 edit closure is shared-helper inspection, not a dedicated quote-only edit execution. |
| SC-03 | met | automated/unit | T-01; H:372,384-403 limits defaults to undefined/null on grep/glob/ast_grep and preserves blanks; U:1374,1386 exercises each search default, absent required arguments and verbatim blanks/separators; R:11-12. |
| SC-04 | met | automated/unit | T-01; H featureRoot/rootCall:987-1017 uses currentFeature and the pinned PolicyRunner, validates one absolute answer, preserves no-match input and refuses errors; readiness/authorization precede rooting H:1148-1184, cache clears H:1038,1490. U:1449-1520 plus retained authorization control U:646; R:14-19. No new resolver or dispatch/environment/input-selected root in the diff. |
| SC-05 | met | automated/unit | T-01; H rootTarget preserves explicit exclusions and unchanged domainTarget/fileDomain:269-313 gates each write/edit target downstream. U:1338,1347,1399,1522,1546 plus retained URI matrix U:1018-1159 cover permitted/refused schemes, pre/post and mixed-file/MV refusal; R:20-21,26. |
| SC-06 | met | automated/unit | T-01; H:1157,1332 preserves non-governed early returns; path-tool sets exclude Bash; no new success advisory/notification branch. U:1399,1562 and retained main write/edit U:1161 / Bash env U:764 controls; shared governed rewrite failures R:8-21, controls correctly labeled at R:26. Settled c1 F1/F2 are not reopened. |
| SC-07 | met | inspection | T-01,T-02; pinned DECISIONS.md DEC-251:8013-8089 and DECISIONS-INDEX.md DEC-251 @8013; H registerHarnessHooks/rooting helpers and U OMP task lifecycle adapter cases above agree on all named clauses. Canonical diff changes no resolver, OMP implementation or Claude host. |

## Assurance bounds and open questions
No tests/build/lint/formatter ran here. Retained red-first receipt R is historical main-session evidence, not reproduced by PM; `notes/review-harness-qa-c2.md:31-40` independently binds its named cases, but c2's 123/0 is **not** claimed for c3. New R2 pass/red measurements and both literal plan commands belong to QA: `python3 tests/unit/test-omp-hooks.py`; `python3 .claude/skills/harness/bin/gen-decisions-index.py --stdout | diff - .harness/harness/docs/DECISIONS-INDEX.md`. Orchestrator's 124/0 and 123/1 claims are unmeasured by this reader. Regression tables do not exhaust every predicate × tool combination; shared-helper inspection supplies that generalization. G1's previously absent quoted-tilde/scheme path-field examples now exist at U:1347, without claiming exhaustive coverage. No TypeScript typecheck, UAT or live end-to-end host assurance is established. Pre-existing ast_edit mutation-set omission, fixture-reuse backlog and prior host/guard URI refusal Q1 remain out-of-range advisories, not attributed defects. New findings: none. Open questions: none. No source/test/docs/feature record changed; reviewed diff authorship is not mine.

```yaml
VERDICT: PASS
DIGEST:
  headline: Both perspectives pass pinned contract inspection; R2 is repaired, with fresh automated measurements owned by QA.
  feasibility: clear
  surface: M
  flags: [enforcement, inspection-only]
  recommend: proceed
  tasks: 2
  decisions: 1
  needs_approval: true
  risk: med
  sc_status:
    - {id: SC-01, verdict: met, method: automated, evidence: "ef9cbce2: U1320/1338/1347/1364, HrootTarget/rootedInput; R8-10; inspection assurance, QA c3 gate separate"}
    - {id: SC-02, verdict: met, method: automated, evidence: "ef9cbce2: U1417/1522, HEDIT_TARGET/effective pre-post; R13/20; R2 edit closure by shared-helper inspection"}
    - {id: SC-03, verdict: met, method: automated, evidence: "ef9cbce2: U1374/1386, HROOT_DEFAULT_TOOLS/rootedInput; R11-12"}
    - {id: SC-04, verdict: met, method: automated, evidence: "ef9cbce2: U1449-1520/646, HfeatureRoot/rootCall/authorization; R14-19"}
    - {id: SC-05, verdict: met, method: automated, evidence: "ef9cbce2: U1347/1522/1546 and retained URI matrix, HdomainTarget/fileDomain; R20-21/26"}
    - {id: SC-06, verdict: met, method: automated, evidence: "ef9cbce2: U1399/1562/1161/764, Hmain/non-governed/Bash boundaries; R8-21/26"}
    - {id: SC-07, verdict: met, method: inspection, evidence: "ef9cbce2: DEC-251/index row, HregisterHarnessHooks/rooting helpers, U OMP task lifecycle adapter; named SC table above"}
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1016-worktree-relative-paths/.harness/harness/features/BUG-1016-worktree-relative-paths/notes/research-BUG-1016-worktree-relative-paths-goalcheck-validate-c3.md
```
