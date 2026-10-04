# Receipt — harness-ai-dev — simplify-upstream-eng ALTITUDE (merge conflict files)

BLUF: PASS, no findings. The three conflict files integrate at the right depth; nothing new is attributable to the merge.

Evidence (read-only, no checks run):
- `.omp/extensions/harness-hooks.ts`: run-start reset keeps `digestBinding = undefined` and `featureRootCache = undefined` (lines 996-997). `featureRootCache` has a single home (944-966), with one resolver `featureRoot`. `agent_end` (1456-1461) resets only `runGate` and `featureRootCache`. No `legacySubagentStop` or `lastAssistantText` remains (grep empty). One authority per rule, with no duplicate statement to drift.
- `tests/unit/omp-hooks.test.ts`: BUG-1016 tests sit inside `describe("OMP task lifecycle adapter")` (opens 122; BUG-1016 block 1232-~1560). The feature hook tests follow, and the `loadDigestSchemaBundle` describe starts at 1701, after the hook describe closes. Order matches the contract. I did not diff assertion counts, so "none weakened" rests on structure only.
- `DECISIONS-INDEX.md`: DEC-156/DEC-237 (object contract) and DEC-250/DEC-251 (manual ruling) are both present with `@offset` anchors. No duplicate or competing statement of the same rule.

Findings: none (no fold-in, briefing-row or leave items).
