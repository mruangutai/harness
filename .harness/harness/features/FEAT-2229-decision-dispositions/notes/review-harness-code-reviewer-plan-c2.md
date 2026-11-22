# FEAT-2229 — T-01 targeted scope re-panel

**PASS — the applied draft closes prior finding PF-c88b62ae6436394172862e6428eac2a5 at the specification level. Architecture: PASS. No new findings.**

Target: pending, unsigned `plan.yaml`, T-01 only; feature.json has no implementation review pin (`review_sha: none`). This is a mandated re-read of the prior **high / substance / scope none** finding, not implementation approval or a general plan-wide review.

## Stage 1 — prior-finding closure

- **SC-03 / closure:** `plan.yaml:226-236` now reserves drafted_at as writer-owned provenance across set-key and all existing merge paths. It explicitly refuses backdating, forward-dating, nulling and insertion into undated legacy plans; only an unchanged existing merge stamp may be carried through. It requires refusal before any write under both byte-preserving and alternate rendering, actual CLI route regressions, nonzero results and identical complete before/after bytes. Ordinary-edit controls must preserve the stamp or its absence. Ownership now includes `_set_top_key` and `_merge_plain_key` (`plan.yaml:136-137`), not only creation. This closes both original scenarios: a new in-era plan cannot be caller-backdated into exemption, and a legacy undated plan cannot acquire caller-created provenance.
- **Mutation-path reconciliation:** PRODUCT `plan-merge.py:171-199` maps both apply and add-tasks to cmd_apply; `union.py:251-277,604-629` funnels them through apply_merge before the locked write. The required all-merge-path protection includes this alias and the UNION_MERGE-off replacement branch, not just `_merge_plain_key`. The byte-preserving route and alternate `_dump_merged`/`_carry_plain_keys` route (`union.py:308-329,571-601`) are explicitly covered by the amended contract. Creation protection remains separately required (`plan.yaml:168-182`). Set-panel/set-lanes use fixed keys through `_set_top_key`; amend/delete are item-scoped; station, approval and record verbs have designated targets rather than arbitrary top-level provenance assignment. No additional caller-controlled top-level mutation seam was identified in this bounded review.
- The required evidence is discriminating: accepting a provenance rewrite/insertion must fail the nonzero-refusal assertion; writing despite refusal must fail the whole-file byte comparison; stamping ordinary legacy edits must fail absence-preservation controls. These are future test obligations, not observed results. T-01 continues to serve SC-01/02/03 and D-01 without changing the settled compatibility boundary.

## Stage 2 — architecture verdict

**PASS under harness-codebase-design.** Shape stays in the shared loader, creation provenance and mutation refusal stay at the existing writer seams, and era/decision checks stay behind cmd_check. Tests cross the real CLI interface instead of bypassing it. The writer provides a deep module: callers need not coordinate timestamps or understand rendering variants. One writer-owned invariant covers those variants; no new writer, speculative adapter, pass-through layer or parallel decision-audit mechanism is required. Locality is improved by naming the two formerly unowned mutation seams.

A-1 remains implementation briefing only: prefer supplied product --root; reuse `plan_merge.guards._harness_root` (`guards.py:50-68`) only if discovery is needed, with cohesive instant parsing. No new module or behavioral restriction is inferred. The T-03-only simplify wording change is outside this re-panel.

## Authorities, principles and verification

Consulted PRODUCT AGENTS.md; SPEC plan/state contracts (§2 and §11); DECISIONS-INDEX.md and DEC-174/179/182/188/205/227. Their existing authority routing and forward-only rationale agree with T-01; no separate architecture contract is invented.

Principles applied: **Model the Domain** — treat drafted_at as immutable creation provenance, not ordinary caller-editable data; enforce it at the existing mutation seams without forcing an abstraction.

Open questions: none. No implementation, builds, tests, linters, formatters, smoke runs or verification commands executed. SC-04/05/06 pinned inspections are outside T-01 and are not claimed here. Future assigned T-01 verification remains `set -eu` followed by the unit decision-disposition-schema and integration plan-decision-dispositions scripts; main owns execution.
