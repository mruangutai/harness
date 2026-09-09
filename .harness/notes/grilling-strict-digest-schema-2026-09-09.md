# Grilling — strict digest and checkpoint schemas — 2026-09-09

## Destination

Ship issue #104 as a full Harness feature: new digest returns and nested `state.yaml.steps[]` entries reject undeclared keys while preserving legitimate, declared fields and one-off durable step evidence.

## Settled

- Flow shape → full Harness feature, not a bug flow; it changes the shared validator contract, agent schemas and instructions, checkpoint state shape, and regression coverage.
- Digest strictness → unknown keys on new returns are rejected with an actionable repair that names the key and declaration route.
- Step strictness → nested `state.yaml.steps[]` entries are governed; a declared free-form evidence container preserves one-off durable evidence rather than forcing it into context.
- Compatibility → historical run artifacts remain readable; enforcement applies to new returns and writes.
- Completion → both rejection and legitimate-use regressions prove the gate, and #37/#44 can depend on a real strictness boundary.

## Not yet specified

- The exact disposition and owner/schema location for each currently observed digest and step key; pm must triage them from live data before selecting the passthrough shape.

## Out of scope

- Rewriting historical run digests or checkpoint artifacts merely to satisfy the new schemas.
- Folding the change into FEAT-08.

## Facts I verified (so pm does not re-derive them)

- issue #104 is open, P0, and explicitly requires strict digest and nested checkpoint handling.
- `validate-digest.py` declares `UNIVERSAL` and persona `SCHEMAS`, but comments at lines 219 and 1317 confirm unknown keys are ignored.
- `stop_hook_active` currently bypasses revalidation at line 1744, so the first rejection must be actionable.
- #37 documents `adequacy_notes` as a legitimate currently ungoverned lead signal.
- DEC-122 makes `validate-digest.py` a SubagentStop contract gate; DEC-154/160 govern checkpoint state and top-level state keys; DEC-174 prevents Harness self-hosting execution of validator/gate changes through the enforcement path being changed.
