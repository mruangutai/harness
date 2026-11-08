# Simplify pass — FEAT-71 (code surface, before review_sha)

Four read-only readers (scout), one angle each, over `git diff 4a05030d 746a5056 -- .claude tests .harness/harness.json`,
excluding pure pruning and the two check-plan-routes files then under the code-grade fix.
Main session applies (DEC-174 main-session-direct; no eng-lead).

| Angle | Finding | Disposition |
|---|---|---|
| REUSE | module feature-id collector duplicated in five tests (test-gh-sync-build-entry, test-merge-gate, test-post-merge-sweep, test-validate-feature-json, test-feature-schema-build-entry) | **Applied for the three integration copies**: new `tests/integration/feature_id_probe_support.py` (`held_feature_ids`), following the existing `tests/integration/*_support.py` convention. **Skipped for the two unit copies**: no unit support module exists and no unit test imports integration support; creating a cross-kind import convention is outside this pass's scope. Assertions unchanged. |
| SIMPLIFICATION | dict branch + intermediate variable in the collector | **Applied** in both unit copies and the new helper (iterate collections directly; dicts iterate keys). |
| EFFICIENCY | none | — |
| ALTITUDE | none (reader could not run git diff; assessed sources and slice receipts) | — |

Suites re-run after the apply: test-merge-gate, test-post-merge-sweep, test-validate-feature-json,
test-feature-schema-build-entry, test-gh-sync-build-entry, test-code-grade (results in the commit's verify log).
