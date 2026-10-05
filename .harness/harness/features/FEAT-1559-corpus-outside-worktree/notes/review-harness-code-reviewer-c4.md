# Code review c4 — PASS (grade_2)

Reviewed `e8d868f78a6ec43880598af5c5873f5daa8ba985..35587d8dfbf9178e21410c201601f7137fbfbbd6`; essential delta `6c11ab626ed568236978b1640928162b8cf0139f..35587d8dfbf9178e21410c201601f7137fbfbbd6`. Exact managed detached pin, not resident HEAD. Spec compliance preceded quality review. No blocking substance or spec violation found.

## Scope and evidence

Read BRIEF, complete signed plan, c3 fix receipt, previous reviewer dispositions, operator signature rulings and pinned feature record. Reviewed the complete executable/test/doc diff (artifact://2074, all 5814 lines), all 97 changed paths (artifact://2091), and essential delta (artifact://2065). No production UI path; OMP changes are tests. No other feature record modified. Required operator docs are present at the pin. Settled direct-session exemption, T-05 endpoint erratum, deferred T-06/#2101, budgets and Ruling B remain accepted; no reopening #2107/#2108 or prior B-1..B-9. Pinned feature.json still contains the prior review_sha; this dispatch explicitly supersedes it with 35587d8d and the audit used only that SHA.

Seven fixes independently traced through production and regression assertions:

| Fix | Owner | Closure |
| --- | --- | --- |
| factory_claim._record_path owner corpus | T-03 | Calls corpus_path; every record consumer shares it; missing own data remains local. |
| Raw hashing / type mismatch | T-01 | --no-filters --stdin-paths; mismatched symlink mode produces None/class C. In-memory independent probe confirmed argv and classification. |
| 120000 symlink hashing | T-01 | readlink bytes via fsencode, hash-object --stdin, never target contents. Independent mocked non-UTF8 target probe passed. |
| C-quoted cone decoding | T-01 | Git octals and escape map decoded before comparison. Independent Unicode, quote, backslash and newline decoder probes passed. |
| Detached operation identity | T-01 | symbolic-ref exit 1 reads rebase-merge, rebase-apply, BISECT_START; normal errors still raise. Independent mocked branch fallback passed. |
| Missing active directory | T-03 | Identity guard precedes owner fallback. Independent mocked missing-own/other-owner routing passed. |
| Quiet ordinary dirty work | T-04 | All three hooks pass --quiet-dirty; only all-DIRTY reports suppressed, exit retained; structural/error text remains. Independent mocked CLI probe observed exit 8 with empty stdout. |

QA's separate artifact `notes/review-harness-qa-c4.md` reports 52 unit files/767 tests and 80 integration files/2341 tests green in an ordinary exact-SHA clone, and seven regression tests red against prior production/green at this pin. These suite results are QA's evidence, not reviewer executions. QA notes unexercised real-filesystem mode mismatch/non-UTF8 link and post-merge mixed diagnostics; the independent reviewer mocks cover selected branches but are not an end-to-end substitute.

A disposable physical-fixture probe was refused before execution by bash-write-guard (reviewer read-only, Python writer). No bypass, source write, disposable clone or persistent fixture was made. The two subsequent authorized isolated probes were entirely in-memory mocks and passed; no suite/build/lint/formatter ran here.

## Mechanical medium findings (unchanged severity; nonblocking)

Grader ran against exact base/pin: artifact://2063, 352 passing records, 12 gated grade-2 records, no high. Each record below is a med substance finding (scope none). C/Cog/ABC are cyclomatic/cognitive/ABC; retaining these cohesive functions is justified, not grounds to re-gate already accepted design.

| Owner / function / line | C/Cog/ABC | Driver | Retention reason |
| --- | --- | --- | --- |
| T-02 check_state/corpus.py preflight:102 | 15/14/30.6 | C, ABC | Ordered refusal boundary must finish before Ctx population. |
| T-03 feature_corpus.py verify_report_findings:384 | 15/7/23.2 | C | Closed fail-closed report grammar belongs in one parser. |
| T-01 feature_corpus.py select:622 | 9/9/27.7 | ABC | Checkout classification and cone selection share one consistent result. |
| T-01 worktree-state.py divergent_paths:199 | 20/20/34.6 | all | Complete safety classification must precede every mutation. |
| T-01 worktree-state.py diagnose:241 | 13/12/36.8 | C, ABC | All diagnostic categories must be retained, not short-circuited. |
| T-01 worktree-state.py main:362 | 9/11/30.8 | ABC | Single CLI/report orchestration preserves mode and exit semantics. |
| T-01/T-05 f58_sparse_fixture.py snapshot:237 | 6/10/27.1 | ABC | One filesystem/index/config nonmutation witness. |
| T-03 test-feature-corpus-census.py Resolver.components:60 | 19/25/26.7 | all | Closed AST grammar; decomposition would obscure rejected syntax. |
| T-03 same statement_lines:116 | 7/18/9.4 | Cog | Statement association must preserve nested source ownership. |
| T-03 same detected_sites:139 | 12/18/26.9 | all | Alias resolution and enumeration classification are one census walk. |
| T-03 same findings:176 | 8/19/15.6 | Cog | One vocabulary checks every reader against the owner-root seam. |
| T-05 test-corpus-regression.py tree_digest:47 | 11/10/25.8 | C | Deterministic witness records filesystem types and contents together. |

## Open question / bounded advisory

Q1 (nonblocking): QA measured that a cone directory beginning with a literal double quote makes raw `sparse-checkout set --stdin` fail with exit 128. Read-side unquoting does not quote write-side stdin. The error is named and fail-closed, not destructive. Whether this exotic segment spelling belongs to the signed supported population is unclassified; recommend a separate explicit pathname-policy/backlog decision rather than silently widening this review or treating decoder probes as repair coverage.

No must-fix. Human-marker commits in range: 29b1a7dbb28b, 61326cff2a78, c4f5fa82ed19, 13b72d560cbe, 2f50604fa796, 9ae5c0627bfb.

Cleanup: managed pin removed with pinned-checkout.py remove using feature/run/persona key; exit 0. No reviewer disposable clones exist. Only this namespaced report was written; expertise unchanged.

## Same-run classification addendum — 2026-10-05 — FAIL (grade_2)

**Supersedes the PASS/no-must-fix/Q1 classification above, not its evidence or twelve grade-2 identities.** Leading-double-quote pathname failure is **substance, scope none, severity med, blocking must-fix**, owned by **T-01**. Its uncommon input and named fail-closed error justify med rather than a data-loss/high claim; blocking follows the unmet explicit convergence requirement, not a mechanical-grade downgrade.

- **Stage 1 authority:** BRIEF SC-01 explicitly requires newly tracked top-level directories to remain present without include-list edits; signed D-08 derives the cone from tracked metadata with no top-level allowlist. Neither authority excludes valid leading-quote names. T-01 owns `bin/worktree-state.py` and the pathname integration fixture. This is an existing-task mismatch with SC-01/D-08, not a scope expansion or an operator pathname-policy decision. Original Q1 is resolved; no missing authority remains.
- **Concrete failure:** a valid tracked top-level directory beginning with literal `"` enters the target cone; raw write-side stdin at pinned `.claude/skills/harness/bin/worktree-state.py:311` is interpreted by Git as an incomplete C-quoted string. QA's existing disposable Git probe measured exit 128, `unable to unquote C-style string` (`review-harness-qa-c4.md`, Extra probes). PM records SC-01 partial and the same source site (`research-FEAT-1559-corpus-outside-worktree-goalcheck-validate-c4.md`, SC outcomes/Q-C4-01). Required repair cannot converge for that valid input. A named refusal avoids an unsupported data-loss claim; it does not satisfy convergence.
- **Must-fix:** T-01 must serialize valid target directory names for Git's stdin grammar and retain a discriminating leading-quote integration case. Cheap local serialization is within current scope; do not add a name exemption, narrow SC-01, or treat read-side decoder probes as write-side repair evidence. Exact remedy is the implementer's choice. No implementation or new feature cycle was performed here.
- **Evidence limit:** the observed quote probe was NOT rerun. This addendum classifies QA's measurement against the signed authority; no new managed pin, clone, source/test/fixture write, grader, suite, build, lint or formatter execution occurred. Original seven independent fix assessments and source-only/mocked limits remain, as do DEC-174/INV-17, T-05 receipt/erratum, SC-10/#2101 deferral and #2107/#2108/B-1..B-9 exclusions. Original pin cleanup remains complete; no new disposable resource needs removal.

Open questions: none. Inspection evidence carried unchanged: SC-11 immutable T-05 receipt C=`69e3d81987b8a9d7676dbaf0f18674b8bf039579`, `non-regression-receipt.md:6-48,100-120`; SC-14 exact-pin guidance `AGENTS.md:10`, harness `SKILL.md:12-19`, verification `SKILL.md:66-75`, `.harness/README.md:51-139` (PM c4 inspection pointers). Mechanical code grade remains grade_2 from artifact://2063; the behavioral must-fix independently changes the verdict to FAIL.
