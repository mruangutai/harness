# Code review — FEAT-53 backend fix c4

**BLUF:** FAIL. Eight assigned blockers are resolved and no production/API regression was found, but V-07 remains open: the replacement isolation test does not compare each fixture KPI with the Harness value and can pass when both calls share the same project-leaking KPI implementation.

## Assigned-item classification

- **V-04 — resolved.** `serve.py:71-75,119-125` blocks untrusted Host values before routing and accepts only the six loopback forms exercised at `test-metrics-dashboard.py:118-126`; the targeted test passed.
- **F-QA-02 — resolved.** Three full-repository requests completed in 5.074s, 5.100s, and 5.233s, each below 8s with >1s headroom (`test-metrics-dashboard.py:148-163`).
- **V-07 — open.** `test-metrics-dashboard.py:128-146` compares the repository route with `kpi.compute(ROOT, ...)`, the same implementation used by that route, while the only fixture-vs-repository inequality is `project.root`. `_assert_kpi_shape` checks keys only. If `kpi.compute` leaks Harness-derived aggregate/trend/feature values into every project, both sides reproduce the leak and the test remains green; SC-03's per-KPI fixture-vs-Harness isolation is therefore still unbound. Owner: **T-12**.
- **V-08 — resolved.** Separate worktrees append distinct records and undergo two merges; both parsed records and raw JSONL order are asserted at `test-metrics-trend.py:68-87`. The 16-test trend file passed.
- **V-19 — resolved.** Every trend field is asserted `None`, non-zero, and reasoned at `test-metrics-trend.py:151-162`; the recorded field mutant is discriminating.
- **V-12 — resolved.** `kpi.compute` delegates selection and payload assembly without changing the `kpi/1` shape (`kpi.py:29-58`); exact-range grading reports no failure and its new helpers grade 4/5.
- **V-13 — resolved.** Token extraction and phase aggregation preserve null-aware totals; targeted metrics assertions passed and replacement helpers grade 5.
- **V-14 — resolved.** The dashboard integration decomposition preserves selection, refresh, disk-only, error, static-route, payload-shape, and asset assertions; exact-range grading passes all decomposed functions.
- **V-15 — resolved.** Worktree path, kind, precedence, and identity branches remain asserted at `test-work-dashboard.py:196-285`; all four targeted worktree assertions passed and replacements grade 4/5.

## Review evidence

- Immutable range: one commit, six intended paths only; no `[harness:human]` commit.
- Canonical exact-range grade: 38 passing records, no `SEVERITY` or `REASON REQUIRED`; `code_grade: pass`.
- Targeted dashboard tests: 3 passed. Trend integration: 16 passed. Metrics/worktree cases: 7 and 4 assertions passed.
- Production refactors preserve `kpi/1` payload assembly and token null semantics. Host rejection is fail-closed before every route. No new silent failure or payload/API change was found.
- Excluded, not reopened: retained `/assets/index-hkwR5g06.js` 404 (F-QA-01/V-01/T-16), F-QA-03, V-02/V-03/V-09/V-10/V-11/V-16/V-17/V-18/V-20, and fixed-dark.

```yaml
VERDICT: FAIL
DIGEST:
  headline: "Eight backend blockers resolve, but V-07 remains open because the isolation test is self-referential and does not compare every fixture KPI against Harness."
  severity_max: high
  findings:
    - { kind: substance, scope: task, severity: high, reader: code-reviewer, task: T-12, summary: "V-07 remains open: the SC-03 isolation test can reproduce project leakage on both sides.", why: "If kpi.compute leaks Harness-derived feature, aggregate, or trend values for fixture projects, the route and its expected value call the same leaking implementation; only project.root is compared across projects, so the test passes with wrong KPI data." }
  must_fix:
    - "V-07 · T-12: compare every fixture KPI against an independently obtained Harness-repository value (and bind fixture expected values), rather than using kpi.compute as the route oracle."
  spec_violations:
    - { kind: omission, path: tests/integration/test-metrics-dashboard.py, ref: SC-03 }
  code_grade: pass
  reviewed: "ffd9fb0204701cdae968ef0febc86943fb4829bd..3b78eb833f12e82e711c6e1b82bf712821ab0a1b"
  human_commits_in_scope: []
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-53/.harness/harness/features/FEAT-53-metrics-dashboard/notes/review-harness-code-reviewer-c4.md
```
