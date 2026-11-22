# FEAT-2229 simplify c2 fold-in

S-2 is applied; A-1 is implementation briefing only. No behavior, assertion, SC, ownership, dependency, approval or panel changes.

## Exact changed field

Only plan.yaml tasks[id=T-03].intent changed through plan-merge.py amend:
- Removed “require reciprocal links” from the DEC-188 paragraph's exclusion sentence.
- Replaced the final paragraph's “No new validate script, relied_on_by field or reciprocal-link check.” with “No new validate script or relied_on_by field; do not require reciprocal links or add a reciprocal-link check.”

Every unique exclusion remains: no wholesale DEC-188 strike, stale markers, propagation checks, reciprocal-link requirements/checks, dated amendment history, new validate script, relied_on_by field or per-entry blast-radius boilerplate. Other keep dispositions, general-freshness boundary and index anchor-rot check remain intact. This is wording consolidation, not a PRODUCT contract interpretation; BRIEF and settled grilling remain unchanged.

## Routed decisions

- S-2: accept optional consolidation. Both reciprocal-link prohibitions now share one sentence, reducing duplicate exclusion maintenance without weakening either.
- A-1: retain as T-01 implementation briefing, not a new plan restriction. Prefer the supplied product --root for era configuration; reuse plan_merge.guards._harness_root only if discovery is necessary, and keep instant parsing cohesive. Reason: avoid a bespoke manifest-discovery walk without prescribing a new module or changing the settled root/segment authority contract. Carry this row into the lead's adequacy_notes and T-01 dispatch.
- R-1: leave as routed; proposed helpers do not preserve the required raw-clause/section and segment-authority semantics.
- S-1: leave as routed; creation/ordinary preservation and explicit caller-mutation refusal are distinct settled cases.
- A-2: leave as routed; point-of-use prompt obligations remain required. No assertions reopened.

## Receipts and boundaries

Inputs: plan.yaml, BRIEF.md, runs/r-20261121-simplify-eng/digest.md, runs/r-20261121-plan-c2-product/acceptance.md and control-plane .harness/notes/grilling-decision-dispositions-2026-11-21.md.

The amend command used --key tasks --id T-03 --field intent --expect-sha256 e5babb6c95f73f4b67ff9b2e36c21b73e08e82295d795ee40c8669da776311e2 --value-file /dev/stdin. Exit 0; stdout reported AMENDED tasks:T-03.intent and APPLIED at the assigned plan path. No APPROVAL-RESET: receipt appeared; no gh-sync invocation occurred.

The writer's automatic check-state output reported unsigned BRIEF and absent/incomplete Build-entry receipt (INV-37), plus pending approval, historical cycle attribution and untracked-feature notes. These are recorded, not repaired or represented as a clean plan check. No separately invoked checks, implementation verification, suites, panel recording, signatures or goalcheck rerun. Scope reads the applied intent next; final PM plan check remains a later step.

Open questions: none.
