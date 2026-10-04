# Receipt: simplify-upstream-eng, SIMPLIFICATION angle (harness-backend-dev)

BLUF: PASS with zero findings. The three conflict files add no complexity beyond what each side already carried.

## Scope read (read-only, no checks run)
- `.omp/extensions/harness-hooks.ts`: `openRun` (996-997), `featureRootCache` (944-966), `rootCall`, post-write gate (1425-1431), `agent_end` (1456-1461).
- `tests/unit/omp-hooks.test.ts`: `describe` boundaries and test order (122-1698).
- `.harness/harness/docs/DECISIONS-INDEX.md`: DEC-156, DEC-237 and DEC-251 lines (159, 231, 234).

## Deletion test on the merge
- `openRun` resets `digestBinding` and `featureRootCache` side by side. These are two independent run-scoped states; neither could be derived from the other. No pass-through.
- `agent_end` resets `runGate` and `featureRootCache` only. The legacy `legacySubagentStop` / `lastAssistantText` fallback is absent (grep: no match), as DEC-237 requires.
- The cache reset appears at both run open and `agent_end`. Each side already carried one of them. The key is `[runtimeAgentId, currentFeature, cwd]`, so the second reset is a boundary guard, not a merge duplicate.
- Tests: BUG-1016 cases (1232-1567) sit inside the hook `describe`, before the FEAT-1928 schema/yield cases (1569+). `describe("OMP task lifecycle adapter")` closes at 1698 before `describe("loadDigestSchemaBundle")` at 1701. The `agent_end validates nothing` test (1690) is the last test before that close.
- Index: DEC-251 (line 234) and DEC-237 (line 231) are both present with `@` anchors and the generator line format. DEC-156 carries the DEC-237 ref.

## Findings
none. Candidates considered and dropped:
- Double `featureRootCache` reset: a boundary guard keyed per run. Not a merge duplicate.
- Comment at test line 123 ("so no other case is rewritten") mildly narrates the change. It is upstream text, not a conflict-resolution artifact.

## Principles applied
- Build the Lever: nothing to build. This is a read-only review with no script, codemod or generator in the diff, so no lever is claimed.

## Open
None. The integrated full suite is the parent's to run.
