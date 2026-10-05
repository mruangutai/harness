# Receipt — SIMPLIFY altitude, FEAT-1928 (harness-ai-dev, read-only)

Graded SHA: 14f04a75410acf26d0f1a9179fe52bff0c361815 (immutable git objects only; nothing run).
Angle result: NOT empty — 1 advisory finding (fold-in, low), 1 cross-feature briefing-row. No enforcement finding.
Altitude otherwise sits right: one canonical copy of the field contract (digest-schemas/*.json); Python (`digest_schema.py`) and TS (`digest-schema.ts`) both read it; `validate-digest.py` words errors and field defaults from `digest_schema.load_schema/common_defs` (:1235-1379), no second table; durable readers share the one `digest_record.py` (ctx.py:513, feature_record.py:463, panel.py:409) with no live-schema import (D-03, SC-07); schema-control refusal sits in the TS hook, the only layer that still sees `outputSchema`/`schemaMode` (`normalizeTaskDispatches` strips them before `dispatch-guard.py`) — correct home (SC-01, D-02).

## Findings

### A-1 — dead alias/prefix resolution in the TS persona table
- Where: `.omp/extensions/digest-schema.ts:31-67` (`DIGEST_PERSONA_ALIASES`, `canonicalDigestPersona`); only caller path `harness-hooks.ts:309-310` passes names already filtered by `startsWith("harness-")`.
- What: the TS adapter re-implements `digest_schema.canonical_persona` (aliases `main-session|dev|reviewer|lead`, and the `harness-<name>` prefix branch). From the hook only a `harness-*` string arrives, so aliases and the prefix branch are unreachable in TS; only the Python CLI (`validate-digest.py`) needs them. The persona list is thus stated three times (digest_schema.py:34, digest-schema.ts:31, tests/unit/test-digest-schemas.py:22), alias map twice, kept equal only by the parity test `omp-hooks.test.ts:1275-1278`.
- Why: a rule with several statements that can drift; the alias half of the TS copy exists only to satisfy a parity test.
- Alternative: **fold-in** — in TS keep only the 16-name membership check (fail-closed on unknown, same error type) and delete `DIGEST_PERSONA_ALIASES`/prefix branch; shrink the parity assertion at omp-hooks.test.ts:1278 to personas only. Keeping the 16-name list preserves SC-01's "every one of 16 personas" assertion (omp-hooks.test.ts:1094,1237). No behavior change observable at dispatch.
- Severity: low / advisory. Guard: SC-01, SC-03, D-02 (single TS adapter, no second contract — fold-in reduces, never adds). If main prefers zero churn on the pinned SHA: **leave** is acceptable since the parity test already pins it.

### A-2 — authored lineage fields vs FEAT-495's guard (cross-feature, not a FEAT-1928 defect)
- Where: `harness-hooks.ts:248-273` (`normalizeTaskDispatches` whitelists agent/task/name/model) and `harness-hooks.ts:308-318` (`withDigestSchemas` spreads `...item`/`...input` into the revised input).
- What: after merge, `dispatch-guard.py` (b8e9f9c8) refuses `agent_id|parent_agent_id|harness_agent_id|harness_parent_agent_id` in task input, but under OMP the guard is handed the normalized dispatch, which never carries those keys, so the new check cannot trigger on the OMP path; the revised input forwarded to OMP still spreads whatever the dispatcher authored.
- Why: pre-existing shape on main (hooks unchanged by b8e9f9c8; `.omp` diff e0bb9814..b8e9f9c8 is empty) — this feature neither introduces nor worsens it.
- Alternative: **briefing-row** for the FEAT-495/DEC-250 owner: if OMP-path enforcement is intended, `schemaControlRefusal`'s sibling (hook, same pre-guard slot) is where lineage keys would be refused. Out of FEAT-1928 scope (intended-behavior change outside approved merge compatibility) — skipped.

## Compatibility slice (harness-hooks.ts + digest-schema.ts) — result
- FEAT-495/DEC-250: **none found** for merge breakage. `preDomain` `harness_feature` (hooks:189) and `basePayload` lineage keys (hooks:173-174, top-level payload fields, not `tool_input`) are byte-identical to main; `.omp/**` has no textual divergence between e0bb9814 and b8e9f9c8, so no merge conflict in these two files. The forbidden task-input lineage fields are checked on `tool_input`; this feature adds only `outputSchema`/`schemaMode` to the revised OMP input, never to the dispatch handed to the guard, so the two denylists don't overlap or conflict. Ordering holds: schema refusal/bundle load precede guard (no claim recorded for a schema-refused dispatch).
- #2000 runtime-pin removal: **none found** — neither file reads `.omp/runtime-pin.json` or the lineage probe (git grep on 14f04a75 `.omp`). Optional, non-enforcement advisory: `MISSING_CAPABILITY` (hooks:391-392) still says "install the pinned Harness OMP build"; identical text exists on main (b8e9f9c8:435), after #2000 dropped the pin. Not introduced by this feature; **leave** (main-owned wording; DEC-218 refusal itself is unchanged).

## Principles applied
None cited (no craft leaf used beyond reading harness-simplify angle reference).
