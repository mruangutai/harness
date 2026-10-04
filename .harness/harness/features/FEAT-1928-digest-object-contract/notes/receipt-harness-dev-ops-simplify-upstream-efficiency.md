# Receipt — simplify-upstream-eng · EFFICIENCY (merge integration)

BLUF: PASS, no efficiency findings attributable to the merge resolution.

- `.omp/extensions/harness-hooks.ts:996-997` run start resets `digestBinding` and `featureRootCache` (two assignments). `:1460` agent_end resets the cache. Both are O(1) and run once per run boundary.
- Cache reset on agent_end is the intended cost bound: `featureRoot` (`:945-965`) memoizes per `[agent, feature, cwd]` key, so the per-call lookup is not repeated within a run. The merge keeps this and adds no per-call work.
- No retained `legacySubagentStop` or `lastAssistantText` fallback was found in the grep over the file, so there is no extra transcript scan on the hot path.
- `tests/unit/omp-hooks.test.ts`: BUG1016 cases live inside the `OMP task lifecycle adapter` describe (`:122-1698`), and the schema describe starts at `:1701`. No duplicated fixtures or added suite runs came from the merge.
- DECISIONS-INDEX: documentation only, with no runtime cost.
- Not checked: I did not run measurements, in line with the read-only, no-execution brief. The full-suite run belongs to the parent.
