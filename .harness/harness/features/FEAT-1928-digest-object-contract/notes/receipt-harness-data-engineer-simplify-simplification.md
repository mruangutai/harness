# SIMPLIFICATION receipt — FEAT-1928 — harness-data-engineer (read-only)

Graded SHA: `14f04a75410acf26d0f1a9179fe52bff0c361815` (immutable objects via `git show`; no working-tree reads).
Angle: simplification (deletion test). **Not empty — 3 low-severity findings, 0 blocking.** Compatibility slice: **none found**.

Scope read at the SHA: `digest_schema.py` (168 lines), `digest_record.py` (87), `digest-schemas/common.json` + persona files (data-engineer, dev-ops heads), validate-digest.py schema-reader helpers (`:1119`, `:1234-1250`, `:1378`, `:2286`), `.omp/extensions/digest-schema.ts:1-110`.
Settled set honored: object-only YieldTool, external-ref schemas + one cached TS projection, final-fenced YAML historical read w/o live validation, TS/Python persona-table mirror (guarded by `tests/unit/omp-hooks.test.ts:1275-1278`), `_digest_mapping`/`_fenced_blocks` anchors.

## Findings

### F-1 — `structured_keys` has no production caller
- File:line: `.claude/skills/harness/bin/digest_record.py:79-87`
- Angle: simplification
- What: `structured_keys()` (recursive dotted-key lister) is referenced only by `tests/unit/test-digest-record.py:87-89`. Every durable-record consumer (`check_state/ctx.py:519`, `plan_merge/panel.py:413`, `check_state/feature_record.py:466`, `validate-digest.py:1911,2329`) takes the mapping from `load_record`/`last_fenced_mapping` and reads keys directly. Module docstring (`:6-8`) promises consumers "use its structured keys" — nobody does.
- Why: deletion test — delete it and no complexity reappears anywhere but one test; 9 lines + a docstring claim + a test for an unused surface.
- Recommended change: delete `structured_keys` and drop the "and use its structured keys" clause from the docstring. Its test `test_structured_keys` asserts only that function, so removal deletes an assertion → per harness-simplify this is a **backlog row, not an apply** (main may still choose it; no behavior change to any live path).
- Severity: low.
- Guard: SC-07 (historical read) unaffected — `last_fenced_mapping`/`load_record` untouched; no D-01..D-05 decision cites it.

### F-2 — `severity` def is dead; `severity_nullable` re-spells its enum
- File:line: `.claude/skills/harness/bin/digest-schemas/common.json` — `$defs.severity` and `$defs.severity_nullable.anyOf[0]` (same five-value enum `none|low|med|high|critical`).
- Angle: simplification (one fact in two spellings that can drift)
- What: `common.json#/$defs/severity` has 0 `$ref`s across `digest-schemas/**` (measured by ref count); the 6 consumers use `severity_nullable`, whose first branch inlines an identical copy of the enum instead of referencing `severity`. Every other `*_nullable` def inlines its own enum too, but those have no non-nullable twin; this one does.
- Why: adding/removing a severity level means editing two places, one of which nothing reads.
- Recommended change: in `severity_nullable`, replace `anyOf[0]` with `{"$ref": "common.json#/$defs/severity"}`. Same accepted language, so the TS projection (inlines external `$ref`s) and `digest_schema.validate_object` behave identically; validate-digest `_resolved`/`_enum_values` (`:1237-1243`, follows `$ref` recursively through `anyOf`) already handle it. Alternative if main prefers fewer defs: delete `severity` instead.
- Severity: low. Guard: SC schema-parity/TS-projection evidence (re-run schema parity after apply); no assertion weakened.

### F-3 — `_field_schema` / `_digest_properties` / `_common_defs` repeat one lookup behind wrappers
- File:line: `.claude/skills/harness/bin/validate-digest.py:1246-1248` (`_field_schema` body), `:1378-1379` (`_digest_properties`), `:1234-1235` (`_common_defs`).
- Angle: simplification
- What: `_field_schema` and `_digest_properties` both spell `digest_schema.load_schema(canonical)["properties"]["DIGEST"]["properties"]`; `_common_defs` is a one-line pass-through with a single caller (`_resolved`, `:1242`).
- Why: the schema path is restated in two places; `_common_defs` fails the deletion test (inline `digest_schema.common_defs()` and nothing reappears).
- Recommended change: `_field_schema` → `return _digest_properties(canonical).get(field) or {}` (move `_digest_properties` above it or leave, Python resolves at call time); inline `_common_defs()` into `_resolved`. Pure refactor, no assertion touched.
- Severity: low. Guard: none (no decision or SC binds these helpers).

## Checked, not findings (angle coverage)
- `canonical_persona` three-step resolution (persona / alias / `harness-<name>`) is exercised by `tests/unit/test-digest-schemas.py:373-385` (dev-ops, eng-lead, qa, orchestrator short forms) and mirrored by TS under a parity test — earns its keep.
- `SchemaStore` class vs module-level `_STORE`: tests inject non-default directories via the class (`directory` param) — varying seam exists; not a pass-through.
- `load_record` vs `last_fenced_mapping`: three callers use each; distinct (path vs text); keep.
- `_fenced_blocks`/`_FENCE_RE` anchors: accepted per assignment.
- `_load_all` loads all 16 personas for one persona's validation — cost is efficiency-angle, not flagged here.
- common.json defs ref-counts: every other def has ≥1 ref (only `severity` is 0).

## Compatibility slice (FEAT-495/DEC-250 b8e9f9c8, #2000 c070395c)
**None found.** Grep at the SHA of `digest-schemas/**`, `digest_schema.py`, `digest_record.py` for `agent_id|repository|claim|inflight|runtime-pin|lineage` returns nothing. Persona schemas are closed (`additionalProperties:false`) over VERDICT/DIGEST/artifact with DIGEST keys that carry no claim metadata or dispatch lineage (`agent_id`, `parent_agent_id`, `harness_agent_id`, `harness_parent_agent_id`, `repository`); the forbidden task-input keys concern dispatch input, not digest output, so no schema overlap. Python loaders resolve only `bin/digest-schemas/` and `digest.md` files; no pre-merge assumption about `.omp/runtime-pin.json` or the lineage probe. (`digest-schema.ts` loader reads only schema files; `harness-hooks.ts` preDomain interplay is outside my slice.) Enforcement findings: none. Optional advisories: F-1..F-3 only.

## Skipped
None skipped for behavior-change reasons; F-1 is flagged as backlog-row (assertion deletion rule), not an apply.

## Verification
None run (read-only per contract).
