# CODE goalcheck — FEAT-2081 — validate-c0

SC-01..08 are met on the carrying implementation and recorded discriminating evidence; SC-09/10 remain not_met pending user UAT. No product-code blocker found. The draft UAT needs one authority-wording correction before readiness; final QA/reviewer receipts and the review pin must also be entered. This is CODE validation, not a signed-plan return or ship approval.

## Assurance

Inspected git objects at fc942ec4ebb0783f61e9809e3fc329b7f53be3e6; canonical range e8d868f7..fc942ec4. Read pinned BRIEF, plan (all three amendments), feature.json, evidence-T-01..04, equivalence ledger and uat.md. feature.json's review_sha=none is superseded for this inspection by the explicit dispatch pin, not inferred from HEAD. No tests/build/lint/formatters run by this reader. Earlier execution receipts are evidence, not a claim of re-execution. QA independently reports the checker hash at this pin equals 608c6446013d6862 from the equivalence proof; git diff d89f9b23..fc942ec4 is empty for checker, locks test and single-pass test. Final QA matrix receipt is still being collected by the QA seat.

## Criteria (paths relative to feature or repository as indicated)

| SC | verdict | method / carrying evidence |
|---|---|---|
| SC-01 | met | automated: notes/evidence-T-01.md red-first completeness, weighting, ties, unknown-file, argument and actual-completion witnesses; pinned tests/integration/test-run-unit-tests-shards.py:101,116,123,129 and malformed-argument cases |
| SC-02 | met | automated: notes/evidence-T-02.md independent C-failure/skipped/cancelled/missing mutations and positive control; pinned tests/integration/test-integration-shard-aggregation.py:133,198; gate conclusion_defects requires exact success |
| SC-03 | met | automated: same ledger S/R/V/X mutation rows; pinned aggregation test:145–198 and gate discover_expected/coverage_defects independently use supplied commit git tree, not manifests/HEAD/worktree |
| SC-04 | met | inspection: pinned .github/workflows/tests.yml:19–29 triggers/concurrency; :359–368 ubuntu matrix and fail-fast false; :417–424 unique unnamed integration job, needs both, job-level always; :447–464 literal needs results and fail-closed validator/download outcome |
| SC-05 | met | inspection: each gate individually remains in checks: Unit :106, feature-state :115, plan-route :165, canonical-reader :227, instruction-path :245, layout :271, repository-state :337; all flow through needs :419 and CHECKS_RESULT :450 into validator. Summary/nonempty and exit propagation bodies preserved in pinned baseline diff; no optional/advisory gate |
| SC-06 | met | automated: notes/qa-structure-audit-equivalence.md 53-input old/new ordered findings + CLI exit/stdout/stderr equivalence, independent feat62/consolidation/broad-catch witnesses, 9 red-first traversal failures and exact once-per-node green counts; pinned single-pass test:160 and locks CASES:618; unchanged checker hash binds proof to pin |
| SC-07 | met | automated: notes/evidence-T-01.md M1/M2/M3 unit discovery/attribution/failure mutations; pinned tests/unit/test-runner-unsharded.py:62 and subsequent failure cases |
| SC-08 | met | automated: evidence-T-01 M1/M3 integration omissions/masked failures plus existing kinds/layout/pool passes; evidence-T-03 existing structure-lock regressions and SC-06 differential proof |
| SC-09 | not_met | uat: user has not executed/signed U-01/U-02/U-04/U-05 with tested SHAs and URLs; real accidental failure is not the required deliberate omission case |
| SC-10 | not_met | uat: two reported passes (95s/88s) do not establish three consecutive runs; earlier different-checkout timing does not prove fixed-corpus comparison; L-01 and P1/P2/P3 remain user outcomes |

## Perspective coverage

- operator — partial: SC-02..05 pass (T-02/T-04, pinned workflow and evidence-T-02); SC-09/10 await user UAT, solely explaining partial perspective coverage.
- code maintainer — pass: SC-01/06/07/08 pass (T-01/T-03, evidence-T-01/T-03 and equivalence ledger); every carrying SC has approved task traces.

## UAT readiness

The script provides concrete throwaway-PR setup, positive/failing/omission/restored cases, independent expected-file proof, manifests, required-check conclusions, timestamps, tested merge SHA vs head SHA, three consecutive performance runs, baseline limitations, fixed-corpus interleaved timing commands and user-only signoff. Pending execution blanks are expected, not CODE blockers. Do not require completion of SC-10 timing before ready: it is part of user UAT, not an automated prerequisite.

Finding GC-01 — kind substance; severity medium; owner T-06; preparation blocker, not product-code blocker. Scenario: notes/uat.md L-01 is labelled “fill or waive by Main's decision,” preceding prose makes its necessity Main's call, and signoff says “L-01 if required.” Main could waive the fixed-corpus lower-median proof despite signed SC-10/T-06, leading to acceptance on different corpora. Remedy: remove all waiver/discretion language and make L-01 a mandatory user-executed SC-10 outcome; only a new explicit user amendment may relax it. No re-planning or execution rerun is requested.

Before status becomes ready, fill review_sha with the final panel pin, replace stale inspection hints with current locations above, and record green QA/reviewer/final-matrix prerequisites (all automated/inspection SCs). Blank readiness receipt fields are ordinary preparation bookkeeping; no status change or UAT pass was authored here. Estimated user effort remains the draft's ~45 minutes wall / ~20 minutes attention.

Open questions: none. Settled cancellation, test-only cache, one-time differential proof, no check-state wiring and DEC-174 routing are accepted without re-litigation.
