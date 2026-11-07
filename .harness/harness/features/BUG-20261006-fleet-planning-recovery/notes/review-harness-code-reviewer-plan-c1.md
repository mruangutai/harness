# Repair scope architecture review — plan c1

**FAIL — the planned Kaya historical recovery cannot supply its authorization evidence to the feature-relative evidence interface.** Resolve the evidence-location contract in T-01/T-03/T-04 before signature. The combined plan lane is otherwise proportionate to the settled enforcement/recovery changes.

## Target and evidence

Planning artifacts only, against baseline `63cac11a3216aa8d34792665a05fcb185f7cf73b`: this feature's `BRIEF.md`, `plan.yaml`, draft research receipt, and the entire `.harness/notes/grilling-fleet-planning-recovery-2026-10-06.md`. Approval is pending; feature.json has no implemented review pin (`review_sha: none`). No implemented-code verdict, tests, builds, linters, remote calls or Kaya mutations. Historical Kaya failures remain attributed operator observations; authentic capture is still a prerequisite, not a planning blocker.

## Findings

- **high · substance · scope none · reader code-reviewer — Kaya authorization evidence has no permitted durable location.** T-01 requires cycle evidence to be local and feature-relative without traversal and requires local-path/hash validation for refusal evidence (`plan.yaml:87,90`). T-03 creates the authentic capture/authorization note under the *Harness repair feature* (`plan.yaml:127,132–134`), while T-04 passes that note to operations writing the distinct canonical *Kaya feature* (`plan.yaml:148–150`). With those exact operands, a feature-relative resolver must reject the external note; a traversal/absolute-path exception would weaken the stated evidence confinement. Consequently the supported historical recovery cannot reach SC-08 even when authentic history and authorization are available. Specify one confined, durable authorization location usable by Kaya's evidence readers and explicitly authorize its creation/capture in T-03/T-04 (or define a trusted-root reference contract in T-01); keep the original repair receipt and exact hashes. Do not silently permit arbitrary external paths. Related requirements: SC-04, SC-05, SC-08 and D-04.

## Scope and architecture assessment

- All SC-01–SC-08 have task traces; all task traces name existing SCs. T-01–T-05 form a topological chain. Their declared file sets are disjoint; the shared schema/writer/reader/test cutover has one owner, avoiding successor edits to earlier code gates.
- T-01 covers status preflight, all feature-bound mirror commands, PR reads, build-entry consumers, merge/removal gates and board status/audit/reconcile. Invalid binding/provenance refuses rather than falling back to ancestor Harness configuration. No extra framework or hypothetical adapter is planned.
- Depth/locality are sound at the proposed seams: existing product_config/board_for resolve configuration, feature_schema owns reusable receipt predicates, digest_record owns historical selection, and existing locked writers persist state. Tests are specified across these interfaces. Recovery adds real generation/progress behavior rather than a pass-through module; no persistent-client lifetime change is proposed.
- Genuine cycles remain distinct from worst-member verdicts and legacy residuals; refusal provenance remains distinct from accepted historical records and live DEC-237 objects. Original FAIL/BLOCKED verdicts and malformed bytes are preserved.
- T-02's documentation gate is separate from the cumulative full unit/integration run required after all changes land. T-03–T-05 explicitly require reviewed/tested tooling activation and separate operator authorization, without circularly requiring their own UAT to finish first.
- SC-07 inspection is planned by T-02 (`plan.yaml:109–116`); it cannot be discharged before an implemented pinned SHA. SC-08 is explicitly user-executed, not an offline fixture claim. Recovery covers capture, ledger repair, mirror replacement, repeated no-op and final feature-scoped checks; no product implementation is authorized.

## Open questions

None. The evidence-location mismatch is actionable design work inside confirmed scope, not a new product decision or a reason to invent missing Kaya history.
