# QA gate — FEAT-65 validate c2

```yaml
VERDICT: PASS
DIGEST:
  headline: "QA-65-01 is closed: the cross_module unit/integration matrix is green, and measured final-pin provenance retains 15 RED→GREEN suites and 7 unchanged byte-identical suites."
  suite: pass
  failures: 0
  matrix_ok: true
  kinds:
    - { kind: unit, state: satisfied, cmd: "env -u HARNESS_AGENT_TYPE .agents/skills/harness/bin/run-unit-tests.py --kind unit", named_tests: 42 }
    - { kind: integration, state: satisfied, cmd: "env -u HARNESS_AGENT_TYPE .agents/skills/harness/bin/run-unit-tests.py --kind integration", named_tests: 69 }
  coverage_gaps: []
  sc_evidence:
    - { id: SC-01, test: "notes/byte-evidence-vs-baseline.md:10-414" }
    - { id: SC-02, test: "notes/red-first-receipts.md:11-84" }
    - { id: SC-03, test: "notes/red-first-receipts.md:11-194" }
    - { id: SC-04, test: "notes/red-first-receipts.md:148-203" }
    - { id: SC-05, test: "notes/red-first-receipts.md:86-116,148-184" }
    - { id: SC-06, test: "notes/research-FEAT-65-hook-site-classification.md" }
    - { id: SC-07, test: "notes/build-divergences.md:14-184" }
    - { id: SC-08, test: "notes/clean-pin-byte-receipts.md:3-70" }
    - { id: SC-09, test: "notes/red-first-receipts.md:128-135" }
    - { id: SC-10, test: "notes/red-first-receipts.md:137-146" }
  fail_first:
    - { sc: SC-01, evidence: "notes/byte-evidence-vs-baseline.md:3-8,389-414 — final-pin test copied into baseline production, 15 exit 1→0 rows, 7 0→0 byte-identical rows, 110 retained RED '-' lines." }
    - { sc: SC-02, evidence: "notes/red-first-receipts.md:11-25,37-84 — named baseline failures and pin GREENs." }
    - { sc: SC-03, evidence: "notes/red-first-receipts.md:11-25,27-35,37-50,52-84,86-146,186-194." }
    - { sc: SC-04, evidence: "notes/red-first-receipts.md:148-184,196-203." }
    - { sc: SC-05, evidence: "notes/red-first-receipts.md:86-116,148-184." }
    - { sc: SC-09, evidence: "notes/red-first-receipts.md:128-135." }
    - { sc: SC-10, evidence: "notes/red-first-receipts.md:137-146." }
  sc_status:
    - { id: SC-01, disposition: met, evidence: "Measured summary has 22 suites: 15 1→0 and 7 0→0; receipt methodology binds each test committed at the review pin to baseline and pin runs." }
    - { id: SC-02, disposition: met, evidence: "Retained RED/GREEN guarded-hook cases cover canonical open/closed diagnostics and verdicts." }
    - { id: SC-03, disposition: met, evidence: "Retained boundary, loud-defect, process-control, and direct-command RED/GREEN evidence is complete." }
    - { id: SC-04, disposition: met, evidence: "Census RED/GREEN receipts cover zero hooks, two boundary catches, increase and embedded-program mutants." }
    - { id: SC-05, disposition: met, evidence: "Retained prologue lock and each-copy mutation RED/GREEN evidence is complete." }
    - { id: SC-06, disposition: met, evidence: "Classification research and ledger retain the 77-site treatment record." }
    - { id: SC-07, disposition: met, evidence: "D-01 through D-15 record operator-visible divergences and owning cases." }
    - { id: SC-08, disposition: met, evidence: "Clean-pin receipt names 97d14f0b, later-commit status, streams, 0/2 census, and five-way identity." }
    - { id: SC-09, disposition: met, evidence: "feature-record direct-command RED 1→GREEN 0 is retained." }
    - { id: SC-10, disposition: met, evidence: "inflight_registry direct-command RED 1→GREEN 0 is retained." }
  provenance:
    review_sha: ffcc2dafa29fc56ae8a9634e9ed1508e1433661d
    baseline_sha: 4e8c73c07e5f1f102c392fe3800616fc94a1c53d
    measured: "git diff --quiet ffcc... -- .claude tests and -- run-unit-tests.py harness.json both exited 0; therefore the executed matrix's production, tests, runner, and matrix bytes equal the immutable review SHA."
    receipt: "byte-evidence-vs-baseline.md:3-8 names clean baseline production, pin test-copy method, raw/normalised streams, and verbatim zero-context differences."
    suite_counts: { total: 22, red_to_green: 15, unchanged_identical: 7, retained_red_lines: 110 }
    ledger: "build-divergences.md:178-184 records c1→c2 regeneration and no .claude/tests byte change from 7596434c; QA independently measured ffcc-to-receipt-head source diff exit 0."
  findings: []
  claim_gap_1898_occurrences: 0
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-65-broad-exception-hooks/.harness/harness/features/FEAT-65-broad-exception-hooks/notes/review-harness-qa-c2.md
```

## Measurements

`cross_module` requires active `unit` and `integration` (`.harness/harness.json:174-178`). The configured runners exited 0 with exact discovery totals **42 unit files** and **69 integration files**. They were executed in the designated feature worktree; comparison to `ffcc2dafa29fc56ae8a9634e9ed1508e1433661d` found no differences in `.claude`, `tests`, `run-unit-tests.py`, or `harness.json`, making the exercised relevant bytes pin-identical.

QA-65-01: the receipt summary at `notes/byte-evidence-vs-baseline.md:389-414` has 22 suite rows. Independent tally: 15 rows are `1→0`; seven are `0→0` with both normalised streams identical. Its per-suite zero-context diff blocks retain **110** `-` lines, including each of the 15 RED suites. The receipt's stated method is one test file as committed at the pin copied into clean `4e8c73c0` production for RED, restored, then run at the pin for GREEN (`:3-8`). This is provenance evidence, not merely a green suite.

The c1→c2 ledger row (`notes/build-divergences.md:178-184`) matches this result and the independent zero source/test-byte delta. #1898 lineage failures in this c2 QA run: **0**.

## Principles applied

- Build the Lever: used the configured kind runners and exact git-diff measurements rather than accepting narrated provenance counts.
