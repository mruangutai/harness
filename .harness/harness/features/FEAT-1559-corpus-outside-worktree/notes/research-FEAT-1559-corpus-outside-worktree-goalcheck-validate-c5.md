# Goal-check — FEAT-1559 validate cycle 5

**BLUF: c4 remediation is independently red/green verified at f8a67546bcb42b6a5fd4327398615a4cfc07ae4d; 11 SCs met, SC-08/13 remain settled partial, SC-10 deferred by ruling.** Terminal c5 QA is incorporated below. PM ran no tests, builds, linters or formatters. Source pointers are pinned; bin means .claude/skills/harness/bin, notes are this feature's notes.

## Independent delta and evidence boundaries

Inspected 35587d8dfbf9178e21410c201601f7137fbfbbd6..f8a67546: only production change is bin/worktree-state.py; only test change is tests/integration/test-worktree-state.py. Both belong to T-01 (plan files:581,585); no plan/approval or goal amendment occurs. quote:143-154 encodes os.fsencode bytes with C escapes or three-digit octal; stdin_lines:157-159 emits one quoted name per line. BOTH repair:333 (sparse-checkout set) and present_blobs:210-211 (hash-object --no-filters --stdin-paths) use it. Link hashing:213 supplies content, not names. Regression test_names_git_would_unquote_on_stdin_converge:99-109 asserts leading-literal-quote directory retention, hidden newline-file removal and verify convergence. This independently establishes implementation repair, not an authority/scope exemption; receipt-main-session-fix-c4.md is not execution evidence credited by PM.

Cumulative e8d868f78a6ec43880598af5c5873f5daa8ba985..review pin path census: 104 paths; no other feature directory or CI workflow changed. C4 evidence transfers only where production, tests, fixtures and relevant configuration are unchanged in the inspected delta. C4 QA is execution at 35587d8d, not re-execution at this pin. Mutable real-owner observations require fresh QA evidence. Prior unit predicate natural-red gaps and literal class-A merge repro remain limits, not reopened findings.

## Perspectives

- operator — **partial**: SC-01/06/11 cover creation, plain-clone behavior and historical-record retention; SC-10 remains deferred to post-merge #2101, not delivered here.
- reader — **met**: SC-02/03/04/05/12/14 cover landed reads, declared audit subject, exact discovery, duplicates, fresh real-owner observations and guidance.
- code maintainer — **partial**: SC-07/09 cover classification and preflight; SC-08 literal merge repro and SC-13 historical per-predicate red assurance remain partial.

## Every SC

| SC | Grade | Evidence and task trace |
|---|---|---|
| SC-01 | met | C4 QA:24-30 RecordBearingClasses plus c5 QA:19-28 independent old-production red/current green for leading literal quote and hidden newline; each stdin writer independently mutated red. Current integration test-worktree-state.py 29/29. T-01/T-04. |
| SC-02 | met | C4 QA:17,29,86; test-feature-corpus.py CrossCheckoutReads/WriteGuards and missing-active test; omp-hooks.test.ts absolute selectors and relative control. Subjects unchanged by delta. T-01/T-03/T-05. |
| SC-03 | met | C4 QA:17,87; test-check-state-corpus.py:84,99,105,123,143 normalized selected-subject equality, local-open instrumentation, missing selection; bin/check_state/corpus.py preflight. Subjects unchanged. T-02. |
| SC-04 | met | C4 QA:17,24,88; test-check-state-corpus.py:149,158; test-feature-corpus-census.py:182-235 scratch census; test-feature-corpus.py:244,360 owner consumers. Subjects unchanged. T-01/T-02/T-03/T-05. |
| SC-05 | met | C4 QA:17,89; test-feature-corpus-discovery.py:29-60 sentinels/era pair/third claimant/empty reason; test-feature-corpus.py MergeGate/BranchCreateGate payload allow/deny. Subjects unchanged. T-01/T-02/T-03. |
| SC-06 | met | test-corpus-non-regression.py:98,105,118; c5 QA:8-17 full non-linked, non-shallow clone at exact pin: unit 52 files/767 PASS, integration 80 files/2341 PASS, both exit 0. CI/depth/runner selection unchanged by cumulative census. Positive controls are not natural-red proof. T-01/T-02/T-05. |
| SC-07 | met | C4 QA:25-26,91 classification/nonmutation/idempotence cases plus c5 QA:17,19-28 current 29/29 state tests, natural old red and independent repair/hash-input mutants. Byte-probe boundaries below are not universal filename assurance. T-01/T-04. |
| SC-08 | partial | C4 QA:92,100; test-worktree-state-hooks.py and hooks-rules cover creators/delegates/stdin/merge/rebase; receipt-T-04.md:73-83 cannot reproduce literal merge-cleared skip bits on Git 2.54. A repair and merges separately do not prove that conjunct. Settled evidence limit, no new finding. T-04. |
| SC-09 | met | C4 QA:17,93; test-check-state-corpus.py:165,175,183,193 downstream-not-run/structural/dirty/mixed; bin/check_state/corpus.py:76-119 calls verify, examines every structural finding, returns before invariants. Subjects unchanged. T-02/T-03/T-04. |
| SC-10 | deferred-by-ruling | Pinned BRIEF:37, T-06 abandoned. #2101 owns receipt after merge; HEAD must contain feature_corpus.py before conversion. Older worktrees merge main first; older pins need that later authorized recreation, never conversion under old tools here. T-06. |
| SC-11 | met | non-regression-receipt.md:6-48,105-120 immutable C=69e3d81987b8a9d7676dbaf0f18674b8bf039579, main/pre=e8d868f78a6ec43880598af5c5873f5daa8ba985, equal 4635-entry manifests; settled erratum preserved. Independent cumulative pinned path census extends no-other-feature-change through current pin, not a claim of a new mutable-host manifest measurement. T-05. |
| SC-12 | met | c5 QA:38-39 fresh managed caller at current review pin: unrepaired caller structural refusal with downstream-not-run, repair/verify 0 and status 0, then test-corpus-real-owner.py 6/6 OK without SKIP. Mutable owner observed now, not inferred from c4; carried test assertions :106,118,138,144,189 cover equality, host floor, mutants and dirty/structural cases. Full-clone suite's owner-is-caller skips are not this evidence. T-05. |
| SC-13 | partial | C4 QA:81-100 six unit suites executed; constructed/bootstrap tiers do not establish every predicate's pre-production natural red. Retained c1 G-5 substance/med unchanged, dismissed by c4 ruling; no new evidence and not reopened. T-01/T-02/T-03/T-05. |
| SC-14 | met | Pinned AGENTS.md:10; harness/SKILL.md:12-19; verification-rules/SKILL.md:66-75; .harness/README.md:58-65,77-130 distinguish active writes, absolute landed-owner reads, no sibling/symlink/git provider, repair/verify/dirty recovery and clone-local hooksPath. Unchanged by delta. T-05. |

## Findings and rulings

No NEW classified finding or scope change. Prior c4 medium substance must-fix belongs to T-01/SC-01 and is behaviorally closed by c5 QA:19-28, not merely by its implementation receipt. DEC-174/INV-17, T-05 receipt erratum, ruling B, SC-10/#2101, four-round/240-minute allowance and cycles_used=6 are settled. #2107/#2108/#2109, B1..B9 and dismissed twelve grade-2 c4 findings are not reopened. No UAT criteria.

Q-C5-EVIDENCE resolved by terminal QA: unit 52 files/767 PASS and integration 80 files/2341 PASS, both exit 0; old production 35587d8d fails, current pin converges, and each changed stdin arm discriminates independently. Q-C5-HOST resolved by fresh repaired active-caller 6/6 without skips (QA:38-39). These were handoff dependencies, not product defects.

## Byte assurance limits and advisories

C5 QA:30-36 measures, not a claim that all bytes converge: directory probes 762 names, 753 ok/9 not ok; 370 on-disk checks and 384 lone-high-byte list-only checks. Nine whitespace-edge/LF cases fail identically through direct Git argv and old production; current repair names cone/skip-bits refusal exit 3, not a crash. Valid UTF-8 directory probes: 333 e2e plus 12 list-only, zero bad. Hidden filenames: 378 creatable byte-position cases plus 333 UTF-8 cases hash correctly; lone high bytes are untested end-to-end there because APFS rejects them. NUL and component slash are excluded by construction. These probes do not prove untested bytes or universal legal-name support.

Non-blocking QA advisories (QA:44-47): no committed unit assertion directly pins quote/stdin_lines or discriminates the backslash branch; Git cone whitespace/LF limits remain pre-existing. Preserve SC-08 literal class-A merge reproduction and SC-13 historical predicate-red limits unchanged, without reopening rulings.

## Cleanup

Managed PM pin key FEAT-1559-corpus-outside-worktree / validate-c5 / harness-pm was already removed successfully via pinned-checkout.py remove from outside the pin (exit 0); no pin created for this finalization. QA confirms its own pin and clones removed (QA:54-55). PM changed only this owned goalcheck artifact, not source, tests, fixtures, brief or plan. All 14 grades are final for this evidence handoff; partial and deferred grades remain explicit.
