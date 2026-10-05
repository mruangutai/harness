# Receipt — REUSE angle, final merge (FEAT-1928)

**BLUF:** Prune canonical loading and classification rows reuse the existing seams; no finding. One low advisory: cold identity adoption re-spells the four-marker adoption block already in `before_agent_start`. Not executed; read-only.

## Findings

1. `.omp/extensions/harness-hooks.ts:1085-1095` vs `:1014-1023` — LOW / advisory
   - Summary: `adoptPersistedRun` repeats the sequence detectHarnessAgent + detectMarker(REVIEW_PIN/MISSION/FEATURE) + `runtimeLineage` + `sessionCwd` + set-if-present + `setFeature`, which `before_agent_start` already performs.
   - Cost: a fifth marker added to the first path must be edited in lockstep in the cold path, and the less-visited cold path goes stale silently (cold revived runs would lose that marker).
   - Alternative: one local `adoptMarkers(systemPrompt, ctx)` called from both sites. Dispatch capture is correctly reused (`captureDispatchFromMessage` at :1096), `detectHarnessAgent`/`detectMarker` are reused, and `digestBinding`/`featureRootCache` stay separate and reset only in `openRun` (:996-997) and :1488. Do not merge those two. Optional; flag-only, apply=0 (mark for Main's discretion).

## Clean (reuse verified)
- `prune-run-evidence.py:110-112` loads feature.json through `artifact_accessors.load_feature_json` with `FeatureJsonError` refusal; same call shape as validate-digest.py:823-825, gh-sync.py:562-564, merge-gate.py:200-202. No local parser. The sole `json.load` (`:53`, `_served_commit`) reads the UI results envelope, not a canonical artifact; classified exempt `module_internal_format` (classification json:2038-2051).
- Classification rows for prune (json:2038-2065): one exempt row for `_served_commit`, one canonical row `_load_record::load_feature_json#1` carrying feature-owning task T-01/plan; file listed in the reader roster (json:2187). 158 `"id"` lines, 0 duplicate ids (bash count, a read-only shell tally).

## Reads
angle-reuse.md; artifact-paths.md; prune-run-evidence.py greps (:52-55,:101-135); harness-hooks.ts:870,944-966,993-1011,1013-1052,1060-1108; bin-wide `load_feature_json` grep; canonical-reader-classification.json:2036-2078,2186-2190.
Not read/verified: tests/unit contents, DECISIONS, tests.yml, feature-record.py (outside reuse concern per task).

## Principles applied
None cited (no leaf read; skill: harness-simplify angle-reuse only).
