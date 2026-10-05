# Receipt — harness-backend-dev — SIMPLIFY · Reuse angle — FEAT-1928-digest-object-contract

Graded immutable SHA: `14f04a75410acf26d0f1a9179fe52bff0c361815` (merge-base with `e0bb9814` is `e0bb9814` itself, which already contains FEAT-495/DEC-250 `b8e9f9c8`). Read-only: git objects only, no commands executed, no verification run.

**Angle result: NOT empty.** 3 low findings (R-1..R-3, all code-surface, all behavior-preserving), 3 advisories (A-1..A-3). **Compatibility result: none found** (details at the end).

## Findings

### R-1 — validate-digest.py:202-219 · reuse · low
- **What:** `ALIAS` still carries a `"main-session": "dev"` row (+ its #1895 comment) and `norm()` still has an `ALIAS.get("harness-" + p, …)` fallback. Both restate resolution that `digest_schema.ALIASES["main-session"]` / `digest_schema.canonical_persona()` (`digest_schema.py:42-67`) now owns.
- **Why (cost):** every `norm()` caller is fed a canonical persona (`validate-digest.py:1122`, `:2286` via `canonical_persona`) or a governed `harness-*` `agent_type` (`:2110`, after `_pass_through` has dropped non-`harness-` names). So the `main-session` row and the `harness-` prefix fallback are unreachable; they are a third spelling of the alias table (py `ALIASES`, TS `DIGEST_PERSONA_ALIASES`, here) that must be edited in lockstep and that nothing exercises (no test calls `norm` — grep of `tests/` finds only the pre-T-04 fixture).
- **Recommended change:** delete the `"main-session": "dev"` row and its 3-line comment; reduce `norm` to `return ALIAS.get(p, p)`. Keep the persona→family rows (family is a different mapping from persona resolution; not duplicated elsewhere).
- **Severity:** low. **Guard:** SC-03/SC-07; D-02 unaffected; migrate-callers-then-delete (no live caller of the dead path). Preserve operand/lookup order: canonical names hit `ALIAS` first exactly as today.

### R-2 — validate-digest.py:1246-1248 vs :1378-1379 · reuse · low
- **What:** `_field_schema()` and `_digest_properties()` both spell `digest_schema.load_schema(canonical)["properties"]["DIGEST"]["properties"]`.
- **Why:** two spellings of one schema path; a schema-shape change (e.g. nesting DIGEST under a `$ref`) must be fixed in both, and the one in `_field_schema` feeds three message builders (`_enum_message`, `_missing_field_hint`, `_type_hint` path).
- **Recommended change:** `def _field_schema(canonical, field): return _digest_properties(canonical).get(field) or {}` (move `_digest_properties` above it, or leave order — both are module-level). While there, inline the one-caller pass-through `_common_defs()` (`:1234-1235`, used only at `:1242`) as `digest_schema.common_defs()`.
- **Severity:** low. **Guard:** SC-03 (closed schema is the single contract), D-02. No assertion text changes.

### R-3 — tests/integration/test-validate-digest.py:71-72, 79 · reuse · low
- **What:** `_PERSONA_ALIASES = {"lead":…, "dev":…, "reviewer":…}` restates (and omits `main-session` from) `digest_schema.ALIASES`; `fixture()` uses it to look up `_NOT_APPLICABLE` filler.
- **Why:** a fourth alias spelling that already diverged (no `main-session`); a CLI case using `main-session` gets no filler and silently tests the incomplete-object path instead of the intended one.
- **Recommended change:** drop `_PERSONA_ALIASES` and resolve with the importable `digest_schema.canonical_persona(persona)` (the test already puts `BIN_DIR` on its path), guarded by `try/except digest_schema.DigestSchemaError: persona` so unknown-persona cases keep their raw name. `_NOT_APPLICABLE` itself stays hand-written: it is the independent fixture oracle (P-05) and must not be derived from the schemas.
- **Severity:** low. **Guard:** SC-03; preserve fail-first/parity evidence (no case is removed or weakened).

## Advisories (optional; no change required)

- **A-1 — `.omp/extensions/harness-hooks.ts:295-318` · reuse · info.** `normalizeTaskDispatches` (flat vs `tasks[]`), `schemaControlRefusal` and `withDigestSchemas` each re-walk the flat-vs-batch shape. A shared `taskItems(input): Dict[]` would collapse three walks to one; pre-existing duplication inside `normalizeTaskDispatches` makes this larger than FEAT-1928. Skipped as a recommendation: would touch `normalizeTaskDispatches` ordering/claim semantics outside this feature's intent.
- **A-2 — `harness-hooks.ts:RETURN_THE_OBJECT` vs `validate-digest.py:OBJECT_REQUIRED` · info.** Two near-identical instruction strings already diverge (“list or missing” vs “absent or wrapped”). Independent consumers across TS/Python (O-08): repetition is load-bearing and no shared constant can span them. If desired, one omp-hooks assertion that both contain `yield({data: {VERDICT, DIGEST, artifact}})` pins the shared core; not required. The probe's `HOOK_REJECTION` substring (`probe-digest-object-contract.py:~70`) is a third reader of the TS text — edit-in-lockstep note for main.
- **A-3 — `tests/manual/probe-digest-object-contract.py:576, 754, 758` · info.** `git -C ROOT …` is spelled as a local lambda (`:576`) and twice inline (`:754`, `:758`; `:117` uses a different `-C`). One module-level `_git(*args)` would serve all; main is concurrently editing this file, so left as an advisory only.

## Considered and not flagged
- TS `DIGEST_PERSONAS` / `DIGEST_PERSONA_ALIASES` mirror py `PERSONAS` / `ALIASES`: parity is pinned by `tests/unit/omp-hooks.test.ts:1275-1278` (loud, not silent) and D-02 settles the adapter; test-digest-schemas.py `PERSONAS` is the deliberate independent oracle.
- `_append_record` hand-reads the file before `_last_record`: `digest_record.load_record` collapses read-failure and no-mapping into one error, whereas the append path must distinguish them (unreadable ⇒ refuse, no mapping ⇒ append). Not a duplicate.
- `_note_verdict` (`feature_record.py`) uses `ctx.read`+`last_fenced_mapping` instead of `load_record`: `read` is the tolerant check_state reader; reuse is correct.
- Repeated local `sys.path.insert`/`import inflight_registry` in validate-digest.py (`:1791-2269`): present at the merge base; not introduced here.
- Agent/skill return examples: already schema-validated by `tests/unit/test-digest-dev-skill.py:102-126`; no hand-copied field list drift.
- `tests/integration/test-dispatch-guard.py:case_30_schema_controls_are_not_the_guards` builds its own payload rather than `_task()`; shape differs (`agent`/`task` batch form, as case 30 repository), so no reuse gain.

## Compatibility slice — validate-digest.py claim/identity/repository checks and dispatch-guard.py call interface

**Result: none found (no enforcement finding).**
- `dispatch-guard.py` is byte-identical between `e0bb9814` and `14f04a75`; it already holds DEC-250's `forbidden_lineage_fields` (`:181-190`), `HARNESS-REPOSITORY` parsing/`_repository_identity` and `claim(..., repository=repository)` (`:488-492`). The hook hands it `tool_input: dispatch` from `normalizeTaskDispatches` (`agent/task/name/model` only), so neither the injected `outputSchema`/`schemaMode` (revisedInput only) nor any lineage field reaches the guard; `schemaControlRefusal`/schema loading run before the guard (no claim on a schema refusal). Pinned by the new `case_30_schema_controls_are_not_the_guards` next to DEC-250's `case_30_repository_header_*`.
- validate-digest.py claim path (`_exact_run_identity` `:2081-2091`, `_registry_errand`, `_settle_in`, `_held_children`, `_release_own`) selects exclusively by payload `harness_feature` + `harness_agent_id` and calls `reg.live_claims(root, None, agent_id=…/parent_agent_id=…)` and `reg.release(root, agent=, feature=, agent_id=)`. These match the post-DEC-250 `inflight_registry` signatures; no `repository` key is read, written, or required. A repository-bound claim released this way is tombstoned by `inflight_registry.release` (DEC-250), which is the intended settle behavior. No stale pre-FEAT-495 field assumption found; the four forbidden task-input lineage names are never read from task input here.
- `harness_feature` in `preDomain` (`harness-hooks.ts:189`) and the yield payload (`:1126`) are unchanged in meaning.
- Out-of-slice observation (main owns, not duplicated): `tests/manual/probe-digest-object-contract.py:~109 pinned_commit()` reads `.omp/runtime-pin.json`, which #2000 deletes — a pre-merge shape assumption for the lineage/provenance edit already in flight.
