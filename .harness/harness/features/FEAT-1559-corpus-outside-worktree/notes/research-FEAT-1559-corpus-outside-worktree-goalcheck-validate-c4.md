# Goal-check — FEAT-1559 cycle 4

**BLUF: grading complete; not an unqualified all-SC-met claim.** Seven requested fixes are present at the exact pin, with independently reproduced prior-production reds from QA. Operator, reader and maintainer perspectives remain **partial** for the specific limits below. No source fix, test run, build, lint or formatter was performed by PM. One new pathname counterexample needs an explicit scope/backlog decision; it retains QA/code-review's nonblocking advisory classification, without an invented severity.

## Subject and evidence boundaries

- Review SHA: `35587d8dfbf9178e21410c201601f7137fbfbbd6` only. Full range: `e8d868f78a6ec43880598af5c5873f5daa8ba985..35587d8dfbf9178e21410c201601f7137fbfbbd6`. Essential fix delta: `6c11ab626ed568236978b1640928162b8cf0139f..35587d8dfbf9178e21410c201601f7137fbfbbd6`.
- Source and documents were read from the managed PM pin, not resident HEAD. Reviewed full cumulative production/consumer/hook diff, changed legacy tests, added suites, pinned BRIEF/plan and guidance. Census: 97 changed paths; no other feature directory or CI workflow changed. No production UI; the only changed TypeScript file is `tests/unit/omp-hooks.test.ts`. Independent UI census agrees (`review-harness-ui-reviewer-c4.md`).
- `bin/` below means `.claude/skills/harness/bin/` at the review SHA; test/source line pointers refer to that SHA even after pin removal. Note pointers are relative to this feature's `notes/` directory.
- **Current executed evidence:** `review-harness-qa-c4.md:9-31`: ordinary full non-linked, non-shallow clone at the exact SHA; unit exit 0, 52 files; integration exit 0, 80 files. All seven new regression cases reproduced natural RED on `6c11ab62` production with pinned test bytes, then green at review SHA. Retargeted-symlink control is not falsely called red. PM read this evidence, did not rerun it.
- **Historical evidence:** `suite-baseline.md`, `receipt-T-02.md` through `receipt-T-05.md`, `non-regression-receipt.md`, and QA c1/c2/c3. Natural reds are credited where recorded; module/bootstrap failures and present-state mutants are not per-predicate historical-red proof. SC-13 retains that limit. Older suite/host receipts are not reported as executions at this SHA.
- Plan `traces:` cover all perspectives: T-01 state/cone, T-02 audit, T-03 corpus/gates, T-04 hooks, T-05 regression/docs. T-06 is abandoned by operator ruling; six tasks, sixteen decisions. No plan/approval/BRIEF/source edits.

## Independent seven-fix source assessment

| Fix | Exact-pin source and test evidence | Assessment and limits |
|---|---|---|
| Factory claim owner corpus | `bin/factory_claim.py:84-92,106-109,159-163`; `test-feature-corpus.py:360-371` | Both plan and issue-map lookup share `_record_path`/`corpus_path`; QA reproduced old `no_plan` failure. T-03. |
| Raw hashing and type mismatch | `bin/worktree-state.py:79-90,173-192,199-228,298-318`; `test-worktree-state.py:279-290` | File hashing uses `--no-filters`; index/file type mismatch is C before mutation. QA filter RED/green. Independent security probe replaced a tracked regular record with an invalid-byte-target symlink: exit 8, unrepaired, snapshot unchanged (`review-harness-security-reviewer-c4.md:18,25`); not a committed fixture or historical red. T-01. |
| Mode 120000 | Same hash/classification source; `test-worktree-state.py:292-309` | `readlink` text is hashed, not referent bytes. Unchanged-link RED/green; retarget-C positive control. Security independently checked invalid target bytes (`security-c4:19`). T-01. |
| C-quoted sparse listing | `bin/worktree-state.py:102-137`; `test-worktree-state.py:91-97` | Listing decoder handles C/octal escapes; non-ASCII RED/green. Read-side decoding does **not** prove write-side stdin encoding for every valid directory name; Q-C4-01 below. T-01. |
| Detached rebase/bisect identity | `bin/feature_corpus.py:97-128,359-370,622-672`; `test-worktree-state.py:111-124` | Rebase-merge fallback RED/green. Rebase-apply and BISECT_START fallback arms are source-inspected, not executed by QA; security's bisect probe was refused before setup, not a failed product test. Pins retain directory-only identity. T-01. |
| Missing active local record | `bin/feature_corpus.py:327-370`; `test-feature-corpus.py:120-131` | Checkout identity keeps a deleted active directory local-missing; other landed reads use owner. Directory- and branch-named RED/green. T-01/T-03. |
| Quiet ordinary work | `bin/worktree-state.py:362-394`; `hooks/post-checkout:38-48`, `post-merge:41-51`, `post-rewrite:26-35`; `test-worktree-state-hooks.py:184-195` | CLI retains dirty exit 8 but silences dirty-only output; all three hooks pass `--quiet-dirty` and print only nonempty failure output. Checkout/rewrite RED/green; post-merge quiet path and mixed dirty+structural output are source-only. Sweep/stdin/exit-0 behavior remains covered. T-01/T-04. |

## Perspective coverage

| Perspective | Verdict | SC coverage and remaining limit |
|---|---|---|
| operator | partial | SC-01/06/11 prove tested creation, plain-clone retention and unchanged historical records. SC-01 has Q-C4-01; standing-checkout conversion SC-10 is explicitly deferred, not delivered here. |
| reader | partial | SC-02/03/04/05/14 cover owner reads, exact subject/census, duplicates and instructions. SC-12 current owner half runs, but both active-worktree-caller checks skip at this SHA; historical T-05 caller evidence is not promoted to a fresh observation. |
| code maintainer | partial | SC-07/09 establish classification/nonmutation and verify-before-invariants. SC-08 exercises merge/rebase and class A separately, not its literal class-A merge repro; SC-13 lacks complete retained historical per-predicate red evidence. |

## SC outcomes

`met` below records the exercised behavioral outcomes, with the historical fail-first tier bounded above; it is not blanket certification that every historical predicate had a retained natural red. The explicit SC-13 assurance gap remains open, not retrospectively repaired.

| SC | Verdict | Method | Concrete evidence / traces |
|---|---|---|---|
| SC-01 | partial | automated integration + QA probe | `test-worktree-state.py:91,111`; `test-worktree-state-hooks.py` Creation and Operations, QA-c4:24-30 green. Q-C4-01 is a counterexample to unrestricted new tracked top-level-directory convergence. T-01/T-04. |
| SC-02 | met | automated integration | `test-feature-corpus.py` CrossCheckoutReads/WriteGuards; `omp-hooks.test.ts` absolute selector/quoted/multiple paths and relative control; QA-c4:17,29. Missing active record stays local; owner/sibling/write refusal controls. T-01/T-03/T-05. |
| SC-03 | met | automated integration | `test-check-state-corpus.py` selected-subject normalized equality, instrumented local opens and explicit missing selector; QA-c4:17. `bin/check_state/corpus.py` preflight before context/invariants. T-02. |
| SC-04 | met | automated integration | `test-check-state-corpus.py` name-set counts/extras/refusal; `test-feature-corpus-census.py` scratch unmarked and exactly-one-marker controls; `test-feature-corpus.py:360` factory owner lookup RED/green (QA-c4:24). T-01/T-02/T-03/T-05. |
| SC-05 | met | automated integration/unit | `test-feature-corpus.py` MergeGate/BranchCreateGate allow and deny payload controls, cross-segment claims; `test-feature-corpus-discovery.py` sentinels/era pair/third claimant/empty reason; QA-c4:17. Settled B-2 is not reopened or claimed fixed. T-01/T-02/T-03. |
| SC-06 | met | automated integration | `test-corpus-non-regression.py` Retention/plain-clone no-op and immutable planning-baseline finding retention; QA-c4:9-18 full clone, both registered kinds green. Full range leaves CI/depth/runner selection unchanged. T-01/T-02/T-05. |
| SC-07 | met | automated integration | `test-worktree-state.py` named exits, verify/repair snapshots, staged deletion, inside deletion, hidden untracked, mixed A/B/C and second repair; raw filter and link cases at :279/:292/:301. QA-c4:25-26; security-c4:18-19 independently exercises type/invalid-byte preservation. T-01/T-04. |
| SC-08 | partial | automated integration/unit | `test-worktree-state-hooks.py:134-195` merge/rebase, class-A read-tree→amend, dirty preservation, quiet checkout/rewrite; `test-worktree-state-hooks-rules.py` all-three delegates/exit/stdin/sweep. `receipt-T-04.md:40-117` explicitly says Git 2.54 does not reproduce merge-cleared skip bits. Thus literal hidden-feature class-A **merge** repro is unproven, though A repair and real merges separately pass. No new source defect claimed. T-04. |
| SC-09 | met | automated integration | `test-check-state-corpus.py` downstream-not-run, structural, dirty-only and mixed structural+dirty; `test-feature-corpus.py` gate refusal shapes/allow controls. `bin/check_state/corpus.py:80-119` inspects all structural findings; verify only. QA-c4:17. T-02/T-03/T-04. |
| SC-10 | deferred-by-ruling | operator ruling | Pinned BRIEF:37 and plan T-06 abandoned; operator rework answer; https://github.com/mruangutai/harness/issues/2101 and issuecomment-6001322957. Receipt belongs to post-merge #2101. HEAD must track `.claude/skills/harness/bin/feature_corpus.py`; older worktrees: merge main first; older pins: prune/recreate under that later authorized task, not this review. T-06. |
| SC-11 | met | inspection | `non-regression-receipt.md:6-48,100-120`: immutable receipt C=`69e3d81987b8a9d7676dbaf0f18674b8bf039579`, resolved main/pre=`e8d868f78a6ec43880598af5c5873f5daa8ba985`, 4635 other-feature files with unchanged manifest. PM exact full-range path/diff inspection additionally finds no other-feature path change through `35587d8d`; no extrapolated mutable-host or old-suite claim. The settled final-seam erratum stays intact. T-05. |
| SC-12 | partial | automated integration | `test-corpus-real-owner.py`; QA-c4:18,46: owner name==disk/>70 and missing/wrong-root mutants executed, 4/6 tests run; both active-worktree-caller checks announced host-prerequisite skips. `receipt-T-05.md` historical all-six caller/owner evidence and disposable owner-HEAD pin are carried context only, not exact-SHA fresh caller evidence. Prerequisite skip is not met. T-05. |
| SC-13 | partial | automated unit + historical inspection | `test-worktree-state-rules.py`, `test-feature-corpus-discovery.py`, `test-feature-corpus-gates.py`, census/rules suites all executed by QA-c4:17. Historical c1 G-5 and ship-review B-9: bootstrap/present-state mutant tiers do not establish every predicate's pre-production red. Settled G-1/G-4 limits remain advisory, not retaken or regraded. T-01/T-02/T-03/T-05. |
| SC-14 | met | inspection | Exact-pin `AGENTS.md:10`, harness `SKILL.md:12-19`, verification `SKILL.md:66-75`, `.harness/README.md:51-139`: active writes/absolute landed reads, no siblings/symlink/git provider, repair/verify/dirty skip and clone-local hooks configuration. Docs reviewed from pin, not resident guidance. T-05. |

## Findings, rulings and recommendations

- **Q-C4-01 — nonblocking scope/classification question, QA advisory unchanged.** A tracked top-level directory beginning with `"` makes `git sparse-checkout set --cone --stdin` exit 128 (`unable to unquote C-style string`). `bin/worktree-state.py:311` sends raw cone names; read-side `unquote` cannot fix write-side parsing. Repair fails closed with a named Git error; no destructive-loss claim. Concrete evidence: QA-c4:38 independent disposable probe; code reviewer confirmed as nonblocking Q1. Ownership: **T-01**, `bin/worktree-state.py` repair stdin encoding and `tests/integration/test-worktree-state.py` pathname fixture. Recommendation: explicitly decide supported pathname scope versus a filed follow-up; do not silently exempt this name from SC-01's existing wording. No existing ruling/backlog for it was found in the feature notes.
- **Retained assurance gap:** SC-13/c1 G-5, kind substance, severity **med** unchanged (ship-review B-9). Missing historical per-predicate red capture cannot be manufactured retrospectively. Ownership T-01/T-02/T-03/T-05 unit/evidence paths. Not a new must-fix production finding.
- SC-08's literal merge-repro and SC-12's skipped current caller are evidence limits, not newly invented code findings. Recommendation: retain their partial outcomes; collect a real converted-caller SC-12 run when #2101's HEAD-era prerequisite exists. Do not rerun suites simply to confirm already reported skips.
- Do not reopen DEC-174/INV-17 exemption, T-05 erratum, three-cycle/180-minute ruling, owner-root-only ruling B, deferred SC-10, #2107/#2108, or settled B-1..B-9. Nothing here claims those backlog items fixed.

## Cleanup

PM used only its managed pin key `FEAT-1559-corpus-outside-worktree / validate-c3-validator / harness-pm`; matching-key removal was requested from the feature tree (outside the pin). Removal completion is recorded below before return. No disposable clone was created by PM; no other reader's pin or live checkout was changed.

Matching-key managed removal completed successfully (0.42 s, no error/output). No PM pin or clone is retained.
