# Code review — plan c0

## Verdict

FAIL. The draft covers defects A–E, preserves the one-PM and DEC-100 contracts, orders E after C and D, and cleanly separates the live merge gate from post-merge evidence. One required identity anchor remains unresolved, so the plan is not yet safe to sign.

## Finding

- **CR-01** — `plan.yaml` T-02 / D-01; **reader:** code-reviewer; **severity:** high; **kind:** substance; **scope:** task; **disposition:** open. The plan defers the restart/revival identity question to implementation and offers conditional fallbacks without deciding how a revived agent that lacks `HARNESS-FEATURE` can locate the canonical feature registry. If OMP does not restore the marker, `before_agent_start` has an agent id but no feature from which to call `inflight_registry.feature_root`; the run can therefore self-refuse despite holding an unambiguous live exact-agent claim, rather than reclaiming before its first write as SC-02 and D-01 require. Resolve the live observation before approval and record one complete lookup rule (including the registry-search scope and ambiguity behavior), or narrow SC-02/D-01 explicitly if restart recovery is not guaranteed. This is also the fourth sharp question the grilling record requires PM to resolve in the plan.

## Compliance and architecture

- A–E have live traces: A → T-03/T-04, B → T-01/T-02, C → T-02, D → T-02, E → T-03.
- T-03 depends on T-02, so E lands after C and D. Later tasks do not mutate the earlier tasks' owned production surfaces; T-04 supplies the terminal live behavior gate after T-02/T-03.
- Run-start exact-id claim/refusal, unchanged one-PM enforcement, DEC-100 pass-through, exact recovery output, DEC-204/205 records, one-time pre-load cutover, pending approval, protected-path execution modes/reasons, and lane records are present.
- The credentialled live OMP probe is a pre-merge UAT gate; dry-run is explicitly non-evidence. The first real post-merge plan/build/validate cycle is explicitly follow-up evidence and non-gating.
- The other three sharp questions are resolved: occurrence 1 becomes a safety invariant (D-05/T-03), `inflight_registry.feature_root` is canonical (D-03/T-01), and lifecycle uses `pi.events` (D-04/T-02).
- Architecture is otherwise coherent: the registry module is the deep lifecycle seam, OMP and validator remain adapters at their existing seams, exact ids eliminate synchronized positional state, and the canonical resolver concentrates registry locality. T-01 should delete `_root_for` rather than retain a one-caller delegation if no caller-facing compatibility requires it; this is advisory, not a separate finding.

## Open questions

None beyond CR-01's required resolution.
