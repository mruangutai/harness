# Simplify pass (plan surface) and operator ruling — FEAT-2297 — 2026-11-22

This is a flag-only pass under harness-simplify. Four read-only `reviewer` dispatches ran, one per angle, over the pending BRIEF.md, plan.yaml and notes/research-config-contract.md (run 2026-11-22-01-plan-product). The main session owned the pass because the product lead cannot spawn eng personas, and DEC-174 limits the main session to the product and validator leads. Findings are deduplicated below; pm applies them.

## Operator ruling — OQ-SMOKE

**Remove `mruangutai/harness-factory-smoke` from `.harness/factory/fleet.yaml` in this feature.** Its repository is left untouched. The operator calls it transient and not needed. Its `main` (7f87b403) has an object-valued `github.board.stations` that the new loader and the fleet check would refuse. This reverses the grilling's out-of-scope line for the removal (and only for the removal).

## Findings

**S1 — T-10's reduction checker duplicates owned controls** (reuse, simplification and altitude all raised it; priority 2).
- **Where:** plan.yaml:981-985.
- **Problem:** `check-config-reduction.py` is to add negative controls for inline fixture bypass and wrong reader route, but T-02's fixture census (plan.yaml:381-389) and T-03's canonical-reader audit (`check-plan-routes.py:1235-1244,1645-1661`) already own both, and T-10 invokes those suites itself.
- **Cost:** a third implementation of two policies; mutant fixtures to keep in lockstep; and control code that counts against SC-05's negative line delta.
- **Alternative:** limit the checker to SC-05's undisposed-row, stale-fail-open and nonnegative-delta controls; leave bypass and route controls to the T-02/T-03 suites.

**S2 — The shared task contract is copied into all ten intents** (simplification, altitude and efficiency; priority 2).
- **Where:** for example plan.yaml:356-366 and 951-959.
- **Problem:** these clauses are repeated in every T-01–T-10 intent: product root, missing guidance, the authority reads (SPEC sections and indexed decisions), direct execution, settled choices, test-first, #2293. T-02 and T-04–T-07 also repeat the fixture-migration contract, and most tasks repeat the verification epilogue.
- **Cost:** up to ten authorities for one rule, and every correction reconciled in ten places. Drift is already visible: T-10's closing says "later fixture tasks" repeat checks "in T-10", yet T-10 is the last fixture task. The sequential tasks also re-read the same two authority documents nine extra times.
- **Alternative:** state the shared execution, authority and fixture contract once, by reference to BRIEF and D-01–D-08, plus one common verification rule. Each intent keeps only its task-specific requirements and dispositions.

**S3 — T-01 migrates readers that belong to T-03** (altitude; priority 2).
- **Where:** plan.yaml:251-255.
- **Problem:** T-01 both introduces `load_json_mapping` and migrates `digest_schema.SchemaStore._load_one` and `run_identity.read_marker`. T-03 is the exhaustive reader-migration task and would have to classify T-01's edits.
- **Alternative:** T-01 owns the generic API and its contract tests; move those two caller edits, and their classification, into T-03.

**S4 — Exact defaults restated outside the schema** (altitude; priority 2).
- **Where:** plan.yaml:846-852.
- **Problem:** D-01 names `config-schemas/harness.json` as the sole shape and default contract, yet T-08 has SPEC and templates/README restate every optional default, conditional requirement and enum.
- **Cost:** several normative copies, checked for agreement only at this feature's review pin, and re-synced on every later schema change.
- **Alternative:** keep the exact values and vocabularies in the schema. SPEC states boundary semantics, the README covers upgrade usage with links, and DECISIONS records rationale. SC-07 is satisfied by reference.

No finding asks to change a settled decision. None of them weakens an SC.
