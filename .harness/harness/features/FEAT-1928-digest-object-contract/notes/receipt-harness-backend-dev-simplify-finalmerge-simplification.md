# Receipt: FEAT-1928 final-merge SIMPLIFICATION reader (harness-backend-dev)

**BLUF:** One finding (low): duplicate `import artifact_accessors` in `prune-run-evidence.py`. Everything else in the read scope is load-bearing and passes the deletion test. No execution; reads only. task:none, files_touched:[].

## Findings

### S1 — duplicate import (low, merge-introduced)
1. File: `.claude/skills/harness/bin/prune-run-evidence.py`
2. Line: 28 and 31 (`import artifact_accessors  # noqa: E402`, twice; 29-30 are harness_boundary, harness_yaml)
3. Summary: the same module is imported twice in one block; the merge left the upstream import and Main's canonical-reader import side by side.
4. Cost: reader sees two identical lines and must work out whether they differ. The sorted import block is also broken. The only uses are `artifact_accessors.load_feature_json` / `.FeatureJsonError` (110-111).
5. Alternative: delete line 31 and keep 28, which preserves the alphabetical order. No behaviour change; the deletion test shows nothing reappears. Apply only under Main (DEC174).

## Checked and kept (no finding)
- **digestBinding vs featureRootCache** (`.omp/extensions/harness-hooks.ts:870, 944-966, 996-997, 1487-1488`): different lifetimes. The binding is set from `digest_destination.py` at lead run-start (1000-1009). The cache is keyed by `[runtimeAgentId, currentFeature, cwd]` and is also cleared at session end (1488). Both are reset in `openRun`. Merging them would add coupling, so I recommend no collapse.
- **adoptPersistedRun** (1079-1098): reads only `session_init.systemPrompt` and `.task`, then calls `captureDispatchFromMessage` on the task. There is no assistant-text or YAML live fallback. Its single caller is `agent_start` (1105), guarded by `runtimeAgentId ? "" : …`. Deleting it would reopen #1908, so it is not a pass-through.
- **Schema refusal ordering** (1215-1228): `schemaControlRefusal` → `taskModelOverride` → `withDigestSchemas` run before `dispatch-guard.py` (1231). The `DigestSchemaBundleError` catch rethrows anything else, so it is not redundant.
- **Tests, describe closure** (`tests/unit/omp-hooks.test.ts`): `describe("OMP task lifecycle adapter")` opens at 122 and closes at 1698 after the last FEAT-1928 case at 1690-1697. `describe("loadDigestSchemaBundle")` opens at 1701 as a sibling, with no stray closure. The schema-refusal "no claim" case (1638-1656) asserts `guardCalls(calls)` is empty. Cold-revival cases sit in the BUG-1898 describe (2659-2711+), with `revivedCtx` feeding `session_init` only.
- **Duplicate-key test retention** (`tests/unit/test-prune-run-evidence.py:95-102`): a single duplicate-key case, through the canonical reader, asserting rc==2, "feature.json" in stderr, and runs not pruned. No redundant second case remains. Assertions are strong, not weakened.
- **CI gate** (`.github/workflows/tests.yml:200-226`): the summary regex is coupled to check-plan-routes.py and rejects both an absent summary and 0 files scanned. This is intentional anchoring, not trimmable.
- **Not read:** feature-record.py elapsed accounting, DECISIONS/INDEX, distillation.md, classification JSON. They were outside what I could verify for simplification in this pass, so I make no claim about them.

## Principles applied
- Delete First (`delete-first.md`, read): S1 is a pure removal with no addition. I did not suggest merging the seams or adding new interface.
- harness-codebase-design deletion test, applied to adoptPersistedRun, the two caches and the schema-refusal block.
