# Goal-check — FEAT-2257 — validate c0

**PASS: all 13 SCs and both DEC-213 amendment rows are met.** Operator, code maintainer and reader perspectives pass. This is goal delivery, not a claim that unrelated panel gates or ship approval are complete.

## Evidence identity

Review pin: `45626d7964e732e8e21b594a78dcbed8fa0494a7`; implementation base: `bda50269`; immutable matrix base: `0bdcabbfc585a9357554817684d1b8a19d69038a`. Product guidance is pinned README Canonical surfaces and the canonical SPEC/DECISIONS it locates, not invented conventional docs. Decision consultation included DEC-183/188/205/213/254 through the control-plane index. All file anchors below refer to the review pin unless explicitly labelled receipts.

Actual PR [#2386](https://github.com/mruangutai/harness/pull/2386) run [45071766676](https://github.com/mruangutai/harness/actions/runs/45071766676): event `pull_request`, head SHA exactly the review pin, conclusion success. Checkout logs identify prospective merge `c42cb7a7205b6ef48a27f02ce9b10d22257800e0`, merging the pin into `df2f58ae7c7f9636a19134692d1e2be7f34a18c8`. Jobs: checks `137360070322`; shards 1/2/3/4 `137360070510/137360070447/137360070623/137360070524`; required integration `137360485393`; all success. This is merge-tree execution, not direct execution of the head tree. Earlier run 45071452185 at another SHA supplies no passing evidence here.

## SC outcomes and trace coverage

QA evidence: `notes/review-harness-qa-c0.md:14-32`; inspection evidence: `notes/review-harness-code-reviewer-c0.md:7-14`, corroborated by pinned object inspection. Receipt paths below are under `notes/receipts/`.

| SC | Verdict / method | Owning tasks; discriminating evidence |
|---|---|---|
| SC-01 | met / automated | T-01/02/04; integration `test-typescript-typecheck.py:51-108`, CI shard 2 exit 0: every tracked source in compiler list, suppression scan, real-tree pass, clean-copy pass and named poison diagnostic. Compiler RED `T-02-red.txt:1-33` precedes fixture edits; activation RED `T-04-regression-red.txt:1-12`. |
| SC-02 | met / inspection | T-01; `package.json:1-11`, `bun.lock:1-14`, `tsconfig.json:1-14`: only exact dev pins typescript 7.0.2 / @types/bun 1.4.5; strict/noEmit, local command; frozen install succeeds in pinned run. |
| SC-03 | met / inspection | T-03; workflow `:66-77,383-415`; actual checks and all four shards install frozen dependencies before compiler-dependent work. Ordinary shell failure propagation, no fallback/lock regeneration. |
| SC-04 | met / inspection | T-01; `.gitignore:1-4`; tracked manifest/lock/config and no node_modules entry in pinned tree; `T-01-verify.txt:1-6` records amended ignore/untrack proof; reviewer note :8. |
| SC-05 | met / inspection | T-03; `.github/dependabot.yml:1-8`: weekly root Bun updates; file new at implementation base, no prior entries lost. |
| SC-06 | met / inspection | T-03; workflow `:19-22,44-77,430-481`, unconditional checks/compiler and unchanged required context/dependency-result chain. Current run succeeds; aggregate receives CHECKS_RESULT/MATRIX_RESULT success and certifies 92 expected files exactly once across four shards at merge SHA. Same-command poison observed by shard 2; clean compiler observed by checks. |
| SC-07 | met / inspection | T-04; live config `:201-207`, template `:137-142`, DEC-213 `:6960-6964,6977`; `T-04-capability-green.txt:1-17` records unresolved live status before flip; `T-04-real-typecheck-pre-activation.txt:1-8` records command, versions, source blobs, output and exit 0 before activation. Final run executes active command successfully. Regression fails closed for missing compiler/config. |
| SC-08 | met / inspection | T-04; read-only JSON comparison of pinned live config against immutable 0bdcabbf finds test_matrix and _matrix_provenance unchanged; detect/exclude also unchanged. No typecheck matrix row added. |
| SC-09 | met / automated | T-02/04; QA :26, wrapper `tests/unit/test-omp-hooks.py`, pinned CI exit 0, 186 passes / 1465 expectations. Baseline/green receipts retain identical counts; fixture diff retains expectation values and no new any/suppression. Compiler RED is separate from runtime non-regression. |
| SC-10 | met / inspection | T-01/02/03/04; reviewer :12; pinned three-hunk fixture diff only, production extension diff empty, only two direct dev dependencies; no linter/formatter adoption. |
| SC-11 | met / inspection | T-01/04; `README.md:215-235`, `SPEC.md:1021-1026`: frozen install, exact command, coverage, any-boundary limitation, weekly and manual reviewed upgrades; executable host/boundary evidence remains required. |
| SC-12 | met / inspection | T-01..04; pinned plan routes and build notes `build-T-01-T-02.md:1-19`, `build-T-03-T-04.md:9-23` record direct worktree execution and capability-before-activation; `.agents/skills` is the committed symlink to authored `.claude/skills`, not a divergent implementation. |
| SC-13 | met / automated | T-04; QA :27, `tests/unit/test-code-grade.py:453-472`, `tests/unit/test-suite-layout.py:356-358,615-635`; both scripts exit 0 in pinned CI. `T-04-capability-red.txt:1-21` records behavioral RED and unflagged config-copy production offenders/broad-pattern failures; capability green retains positive control; existing live-layout cases pass after activation. |

Perspective discharge: **operator pass** (SC-03/06/08/12 → T-01..04); **code maintainer pass** (SC-01/02/04/05/09/11/13 → T-01..04); **reader pass** (SC-07/10 → T-01..04). Every SC has task traces and committed subjects; none requires UAT.

## Decision-disposition outcomes

Both entries are individual `amend` rows of pinned `plan.yaml.decisions_affected`, successor D-01, owner T-04; keep rows are intentionally not graded.

- **DEC-213 row 11 (1-based), clause “contains probes and review instruments that no normal runner may execute and no”: met.** At `45626d7964e732e8e21b594a78dcbed8fa0494a7:.harness/harness/docs/DECISIONS.md:6960-6964`, current text permits flagged static checking of manual source, retains the normal-runner execution ban and credentials/nondeterminism rationale.
- **DEC-213 row 12 (1-based), clause “the only mechanical consumer of”: met.** At `45626d7964e732e8e21b594a78dcbed8fa0494a7:.harness/harness/docs/DECISIONS.md:6977`, current text replaces exclusivity with default-true boolean classification and two consumers. `code_grade.py:458-486` honors it in the matcher, inherited by offenders/control selection; suite-layout `:356-358` shares the predicate for hygiene. The superset obligation covers test-classifying running kinds, without narrowing static source detection. This is an in-place current-text correction, not a new historical appendix or strike.

## Deviations and findings

- **T-02 unknown mapper: accepted behavioral deviation; kind execution, advisory, owner T-02.** `omp-hooks.test.ts:2148-2153` retains the identical payload equality and expected arrays; unknown is an honest comparison boundary, not an array-to-record cast, assertion deletion or changed runtime value. Generic filtering and literal narrowing repair the other errors. Recorder widening requested by intent did not land; this is not represented as literal plan compliance. It does not leave an SC unmet (reviewer :18; QA :35).
- **README --latest: accepted clarification; kind execution, advisory, owner T-01.** `README.md:233-235` uses `bun update --latest typescript @types/bun` to make an exact-pin upgrade effective, retaining review, verification and paired manifest/lock commit. The plain-update experiment is attributed to `build-T-01-T-02.md:9`, not claimed as a PM rerun or a separate captured receipt.
- **T-01 cache removal: authorized scope, not a finding.** Pinned feature.json judgements explicitly ledger advisor approval for both files and verify amendments; removal serves SC-04.
- **Kind form, advisory, owner T-04:** config labels understate classifier runtime logic; QA nevertheless imposed and observed both unit and integration floors. No missing goal evidence follows. QA's unshown independent mutants for coverage/suppression assertions remain advisory, not a false claim of demonstrated per-assertion discrimination.
- **Goal must-fix findings: none.** Code review's mechanical Python grade pending authorization is a separate panel gate, not an unmet product criterion or a PM execution request.

## Principles applied

- **Experience First:** accepted the effective exact-pin upgrade command for maintainers rather than enforcing ineffective literal wording.
- **Outcome-Oriented Execution:** required explicit capability and compiler boundaries before activation, and current-pin CI afterward; intermediate receipts alone do not establish the final outcome.

Open questions: none. Verification performed by PM: read-only Git object/diff/subtree inspection and GitHub run/log retrieval only; no builds, tests, lint, formatters, source changes or replanning.
