# Code review — FEAT-53 backend fix c5

**BLUF:** PASS. V-07 is resolved at the actual fixed tip `ae5970d92c5142ccc2530d8b4519afda8b184000`; the one-commit repair is spec-compliant, the four canonical grade records pass, and no new fail-open or silent path was found.

## Stage 1 — spec compliance

- **V-07 — resolved (original kind `substance`, severity `high`, reader `code-reviewer`, owner `T-12`).** `tests/integration/test-metrics-dashboard.py:128-147` loads the oracle from fixture `expected.json`, obtains fixture and Harness responses independently, checks the fixture through `_assert_fixture_kpis`, checks the Harness project root separately through `_assert_harness_route`, and runs a systemic mutant that makes `kpi.compute` ignore its requested root and compute from the Harness root. `_bound_fixture_kpis` at `tests/integration/test-metrics-dashboard.py:356-367` independently binds feature IDs, every selected shipped-feature KPI field, throughput, rework, feature touchpoints, and nested aggregate touchpoint values. The fixture assertion rejects the mutant at `tests/integration/test-metrics-dashboard.py:144-145`; the focused test passed. This closes the c4 failure scenario: a shared project-root/data leak no longer remains green behind a self-referential `kpi.compute(ROOT)` oracle.
- The repair changes only `trend.py` and four backend test files, all serving the assigned V-07 proof or the named grade repairs. No scope creep, omission, decision mismatch, or human commit appears in `d1d9a44e..ae5970d9`. Parent-owned attention/grilling repairs and every excluded surface are untouched.

## Stage 2 — code quality

- `trend.py:152-205` preserves the reader pipeline: JSON parse, schema/identity/timestamp rejection, nested whole-value unavailability, then newest-duplicate selection. `read()` still applies window selection before `_series` and `_weekly`; `_segments` remains the shared null-gap splitter. The 16-test trend file passed, including schema rejection, duplicate resolution, per-field unavailable reasons, weekly/series segmentation, append/commit success and failure, and ship-before-board ordering.
- The three grade-driven test refactors retain their prior subjects and discriminators: `TrendTest.test_cmd_ship_records_trend_before_board_writes_and_handles_failure` still finds the real `cmd_ship`, asserts one trend call precedes board calls, and requires a handler (`test-metrics-trend.py:281-312`); `metrics_case` still constructs all five elapsed/token fixtures and executes all seven assertions (`test-work-dashboard.py:149-210`); `KpiCoreTest.test_hand_labelled_feature_and_aggregate_values` still uses the committed fixture and asserts headers, labelled KPIs, unavailable branches, and the exact diff call (`test-metrics-kpi.py:42-47,585-634`). Their targeted runs passed: 16 trend tests, 7 metrics assertions, and 21 KPI tests.
- Complete-feature grading (`a18d6a9f1f832084df84be22097a409d73bf4f61..ae5970d9`) reports 396 passing records; exact-repair grading reports 27 passing changed/new records, with no severity or reason-required record. The four canonical current records pass: `trend.py:_records` grade 5 (3/3/7.1, production bar 4), `test-work-dashboard.py:metrics_case` grade 5 (1/0/6.7), `TrendTest.test_cmd_ship_records_trend_before_board_writes_and_handles_failure` grade 4 (1/0/9.5), and `KpiCoreTest.test_hand_labelled_feature_and_aggregate_values` grade 5 (1/0/4.5), all test bar 3.
- Fail-open review found no new defect: malformed/schema/timestamp records are discarded with reasons; nested grade/attribution absence is surfaced; duplicate selection is deterministic; response failures raise before payload use; and the project-leak mutant is required to fail.

```yaml
VERDICT: PASS
DIGEST:
  headline: "V-07 resolves at ae5970d9: independent fixture bindings, separate fixture/Harness checks, and a systemic project-leak mutant now discriminate the former shared-oracle failure."
  severity_max: none
  findings: []
  must_fix: []
  spec_violations: []
  code_grade: pass
  reviewed: "d1d9a44eef283949b9465c97358c6741f4b337b0..ae5970d92c5142ccc2530d8b4519afda8b184000"
  human_commits_in_scope: []
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-53/.harness/harness/features/FEAT-53-metrics-dashboard/notes/review-harness-code-reviewer-c5.md
```
