# FEAT-53 pinned code review — cycle 0

BLUF: **FAIL.** Stage 1 passes, including the operator-ratified T-25 lane and the explicit deferral of T-17/METRICS.md. Stage 2 finds two fail-open source omissions and seven mandatory high code-grade failures.

- review_sha: `9b34c65246136666bc69f220824bb262965e75c0`
- merge_base: `a18d6a9f1f832084df84be22097a409d73bf4f61`
- reviewed range: `a18d6a9f1f832084df84be22097a409d73bf4f61...9b34c65246136666bc69f220824bb262965e75c0`
- cycles_used: 0

## Stage 1 — spec compliance: PASS

The pinned BRIEF, DESIGN and plan decisions/tasks trace the implementation surfaces in the 279-path diff. The three product routes, per-project KPI source, fleet work collector, null-aware measurements, lifecycle migration, token pipeline and tests all have owning tasks. No spec violation was found. SC-15 and SC-20 are assigned to the independent UI inspection reader, not re-judged here. T-17/METRICS.md is known deferred completion work by operator instruction and is not a finding. T-25 is operator-ratified and was not relitigated.

Human commits newly in scope: `91bfa049`, `c83feaa6`, `1745ca83`, `ab0c1501`, `ca4ac5bc`, `d9b6354b`, `60a2c900`; their changed paths were included in the same pinned range.

## Stage 2 — code quality: FAIL

### Ranked findings

1. **high · substance · T-23 · harness-code-reviewer** — `.claude/skills/harness/bin/dashboard/work.py:183-186` silently falls back to the main-checkout feature directory when a registered worktree feature directory exists but is unreadable. **Failure scenario:** remove read/execute access from a live worktree's feature directory while its main copy is stale; collection displays the stale main state with `error: null`, rather than the specific source error required by REQ-19/REQ-20, so an operator can act on the wrong station/status.
2. **high · substance · T-23 · harness-code-reviewer** — `.claude/skills/harness/bin/dashboard/work.py:72-75` catches every fleet-load exception and converts it to `fleet = None`. **Failure scenario:** malformed or unreadable `.harness/factory/fleet.yaml` makes every fleet repository and registered worktree disappear while `/api/work` still returns a successful root-only payload with no source error, making an incomplete inventory look complete (REQ-16/REQ-20).
3. **high · substance · T-25 · harness-code-reviewer** — mechanical gate: `backfill-grilling-status.py:31 citations` grades 3 (cyclomatic 6, cognitive 13, ABC 14.4; driver cognitive; production bar 4). A citation-format extension must be reasoned through nested parsing branches, increasing the realistic risk that one manifest form is missed during the one-shot migration.
4. **high · substance · T-25 · harness-code-reviewer** — mechanical gate: `backfill-grilling-status.py:84 check` grades 3 (cyclomatic 10, cognitive 13, ABC 22.7; driver cyclomatic+cognitive+abc; production bar 4). A new manifest validation branch can incorrectly accept or reject an entry because validation, aggregation and reporting paths are interleaved.
5. **high · substance · T-06 · harness-code-reviewer** — mechanical gate: `dashboard/kpi.py:28 compute` grades 3 (cyclomatic 7, cognitive 1, ABC 25.9; driver ABC; production bar 4). Adding or changing one KPI source requires editing a wide orchestration function, creating a realistic omission risk between feature enrichment and aggregate output.
6. **high · substance · T-31 · harness-code-reviewer** — mechanical gate: `dashboard/work.py:325 _tokens` grades 3 (cyclomatic 9, cognitive 4, ABC 19.4; driver cyclomatic; production bar 4). Extending phase/token classification can update total accounting but miss one phase branch, yielding internally inconsistent totals.
7. **high · substance · T-27 · harness-code-reviewer** — mechanical gate: `tests/integration/test-metrics-dashboard.py:108 test_work_api_filters_live_disk_payload_and_preserves_static_routes` grades 1 (cyclomatic 6, cognitive 0, ABC 72.2; driver ABC; test bar 3). A route regression can be obscured in an oversized multi-contract test, making its failing assertion hard to localize and safely maintain.
8. **high · substance · T-26 · harness-code-reviewer** — mechanical gate: `tests/integration/test-work-dashboard.py:196 worktree_case` grades 1 (cyclomatic 23, cognitive 11, ABC 63.2; driver cyclomatic+abc; test bar 3). Changing one worktree case risks weakening another because fixture construction, collection and many assertions share one function.
9. **high · substance · T-24 · harness-code-reviewer** — mechanical gate: `tests/integration/test-work-dashboard.py:284 attention_case` grades 1 (cyclomatic 18, cognitive 19, ABC 65.6; driver ABC; test bar 3). Adding an attention boundary can accidentally bypass or overwrite an existing case within the same large function.

### Grade-2 records (medium, non-blocking on their own)

All required reasons were assessed: `backfill-grilling-status.py:103 main` (T-25) is cohesive CLI dispatch; `attention.py:76 _feature_attention` (T-24) centralizes ordered state precedence; `trend.py:_records` (T-10) performs one record-normalization pass; `grilling_status.py:parse` (T-25) keeps one front-matter grammar; `test-grilling-status.py:74 tool_cases` (T-25), `test-metrics-trend.py:248 test_cmd_ship_records_trend_before_board_writes_and_handles_failure` (T-19), `test-work-dashboard.py:149 metrics_case` (T-31), and `test-metrics-kpi.py:42 test_hand_labelled_feature_and_aggregate_values` (T-06) each keep a single end-to-end scenario together. These are accepted grade-2 reasons, not additional must-fix items.

### Mechanical grade evidence

`python3 /Users/molchairuangutai/GitHub/harness/.claude/skills/harness/bin/code-grade.py --base a18d6a9f1f832084df84be22097a409d73bf4f61 --head 9b34c65246136666bc69f220824bb262965e75c0`

Result: exit 1, `code_grade: fail`; 294 passing functions, the seven high records above, and eight reason-required grade-2 records.

### Assessed and dismissed

- The extra `return available` after `dashboard/kpi.py:_branch_names` is dead code, but it is unreachable rather than a shipped behavior defect; no separate finding.
- `/api/work` filtering uses `item.segment`; registered fleet worktree rows set segment from the repository name, so the apparent repository/segment mismatch does not reproduce for those rows.
- Missing T-17 documentation is operator-deferred and intentionally excluded.
- T-25 routing/direct execution was ratified and is not reopened.
