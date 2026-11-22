# FEAT-2229 — scope and architecture review

**FAIL — T-01 leaves a caller-writable escape from its creation-era gate. The plan mission is proportionate; no downgrade recommended.**

Target: pending `plan.yaml`, baseline e839075e7b6445bb519984b2351a8eb05d49fbfd; no implementation SHA reviewed.

## Stage 1 — intent and compliance

- **high / substance / scope none — T-01, SC-03:** A newly created post-activation draft can be backdated through the existing `set-key drafted_at` route, then classified as pre-era and accepted without dispositions. T-01 protects creation input and incidental edits but neither assigns nor instructs protection of this direct mutation route. `plan_merge/panel.py:331-336` reserves only approval/tasks/decisions/status; `_set_top_key` at :389-404 permits other schema-valid values. A valid old timestamp cannot be rejected by shape validation alone. The other uncovered case is adding caller-supplied provenance to an undated legacy plan through ordinary merging (`union.py:544-566`). **Required:** add the existing mutation seam to T-01 ownership; explicitly reserve creation provenance against caller changes/insertion on existing plans, preserving legitimate creation and existing bytes. Add CLI regressions for post-creation backdating and provenance insertion into legacy plans, including unchanged bytes on refusal. This is the feature's own fail-open defect class, not a request for another enforcement subsystem.
- All seven SCs have task traces; no nonexistent trace, dependency inversion, deletion-versus-verify conflict, or shared-file downstream gate collision found. Dependencies T-01 → T-02 → T-03 are topological. The supplied draft-check receipt reports 19 anchors, no overlaps and exit 0; not rerun and not treated as evidence for the future gate.
- Independently consulted affected writer/check/goal-check surfaces and the product decision index plus DEC-73/174/179/182/188/205/227/228/229/252. No additional disposition omission identified. The eight rows use exactly five fields with verbatim clauses. DEC-188 is correctly **amended**, not struck; D-01 resolves its successor and T-03 owns DECISIONS.md. DEC-254 is explicitly planned with collision refusal. No softer strike is authorized or proposed. Future-valid row checks are specified; today's check does not establish them.
- Planned inspection coverage: SC-04 → T-02 (`plan.yaml:116-117`); SC-05 → T-02 (:118-119); SC-06 → T-03 (:142-144). These are future pinned-artifact obligations, not implementation inspection passes. Patch inclusion, per-row pm grades/pinned evidence, skip-keep and owning-task routing are explicit. Enforcement and unowned surfaces are main-session-direct. No separate validate script or excluded reciprocal-link, relied_on_by, blast-radius or stale-detection mechanism is introduced.

## Stage 2 — architecture and proportionality

Existing seams are appropriate: shared loader owns row shape; creation writer owns provenance; draft check owns authority resolution; scope owns semantic completeness; pm owns pinned landing judgment. No speculative adapter or pass-through module is planned. The provenance hole above is the sole missing locality/ownership assignment. Each task serves a live requirement; three tasks separate enforcement, canonical instructions and owned documentation without duplicate production paths. Plan rather than patch is warranted by the new schema and enforcement surface.

## Principles applied

- Model the Domain — creation provenance is an immutable writer-owned fact, not another caller-editable plan value; require its invariant at existing mutation seams.

## Open questions and verification

None. Read-only review; no builds, tests, linters, formatters, smoke runs or verification commands executed. After amendment, the assigned implementation checks should include the provenance-mutation regressions above; main performs verification.
