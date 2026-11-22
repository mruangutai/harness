# Scoped smoke substance review — c1

FAIL — T-03 still contains the superseded no-removal instruction alongside the authorized removal. One medium substance finding; affected task: T-03. T-08/T-10's new documentation and cumulative-proof intent otherwise agree with the operator ruling.

## Stage 1 — scope compliance

- **R1 — med, substance, scope none; T-03:** `plan.yaml:328` says the fleet aggregate is expected to fail pending an operator disposition and explicitly says not to remove fleet membership. `plan.yaml:330` instead orders removal. If execution follows the retained exclusion, smoke remains declared and its incompatible remote stations object still fails fleet validation; removal assertions then cannot pass. Delete the obsolete pending-disposition/no-removal/expected-failure instructions while retaining the prohibition on modifying the smoke repository or weakening validation. Anchor: BRIEF.md, Verification gaps OQ-SMOKE ruling and SC-02/SC-10; `notes/simplify-plan-c0.md`, Operator ruling. This is conflicting execution scope, not a request to change the operator decision. Severity remains medium; no inherited finding is regraded.
- Ownership is explicit: T-03 lists `.harness/factory/fleet.yaml` at `plan.yaml:315` and scopes the removal and integration assertions at `:330`. The current declaration contains smoke, Kaya/main and workspace_root; only smoke's member is authorized to leave. Kaya and every other setting must remain; no smoke-repository write is authorized.
- T-08 (`plan.yaml:459-492`) depends on T-03 and records removal with the repository untouched. SC-07 planning inspection: `plan.yaml:490` requires the change record and pinned `git show` content inspection; shipped-document agreement is not yet claimed.
- T-10 (`plan.yaml:518-552`) depends on T-03/T-08, replaces expected smoke failure with actual remaining-fleet outcomes, preserves failure status, and precedes the separately mandatory Kaya UAT. The bounded task verifies reader behavior, decision-index freshness and cumulative evidence respectively; configured unit/integration proof remains independently required.

## Stage 2 — affected architecture

No new architecture finding. Removal belongs at the existing fleet-membership seam, not in schema exceptions or product_config filters. `factory_config.py:221-287,384-402` establishes remote/default-branch authority, process-lifetime success-only memoization, per-member reporting and aggregate refusal. T-03 preserves these contracts and adds removal/presence and remaining-failure coverage through its owned reader suite; T-10 reruns cumulative coverage. No extra adapter, fallback, or remote mutation is introduced.

## Principles applied

- Delete First: remove the transient declaration rather than adding validation exemptions; remove its obsolete execution instruction in the same wave.

## Limits and open questions

Pending-plan review only (`review_sha: none`); code grade n_a. No implementation, tests, builds, lint, formatters or diff review performed. Missing requested product guidance remains disclosed in BRIEF; existing SPEC fleet-reader guidance was consulted, not substituted for absent architecture guidance. S1–S4 and settled defaults were not reopened. Open questions: none.
