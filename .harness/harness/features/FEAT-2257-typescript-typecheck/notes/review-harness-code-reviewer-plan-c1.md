# Pending-plan scope and architecture review

PASS with two non-gating record corrections. Mission **plan is proportionate**: activating QA enforcement and extending required CI is not a patch; no mission downgrade recommended.

Reviewed: plan:/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2257-typescript-typecheck/.harness/harness/features/FEAT-2257-typescript-typecheck/plan.yaml

## Findings

1. **med · form · scope none — DEC-213 keep overlooks the manual-source detection clause.** `plan.yaml:70` keeps DEC-213, but T-04 preserves detect/exclude while activating typecheck (`plan.yaml:204`). The existing `**/*.ts|**/*.tsx` detect and exclusions (`.harness/harness.json:199-201`) match `tests/manual/probe-session-accessors.ts`. DEC-213 explicitly forbids any active detect glob matching manual probes (`DECISIONS.md:6960-6962`). Following this plan therefore leaves the decision record contradicting the intended compiler coverage. Amend the narrowly overbroad manual-detection clause to distinguish static checking from executing host probes; retain the prohibition on executing them in ordinary CI. Declare the amendment and its owning documentation path before approval. Do not drop the manual source or change the settled detect/exclude to hide the conflict. This is a softer narrowing under DEC-188, not grounds to strike DEC-213 wholesale.
2. **low · form · scope none — canonical verification-gap text remains false after activation.** T-01 updates README only (`plan.yaml:111-115`), leaving `SPEC.md:1021-1023` saying static typecheck is unconfigured and unresolved. After T-04 succeeds, readers of the canonical product specification still see the closed gap as open. Include a targeted update of that paragraph, retaining the real OMP-any limitation. No unrelated specification cleanup is requested.

## Compliance and architecture

Original grilling intent is covered, with no orphan SCs: T-01 owns toolchain/ignore/docs; T-02 fixes all eight fixture errors without weakening assertions; T-03 owns frozen CI installs, weekly updates and required-context preservation; T-04 owns discrimination and honest activation. Inspection SCs are planned, not claimed satisfied: SC-02/11 → `plan.yaml:129-131`; SC-03/05/06 → `:175-177`; SC-07/08 → `:204`; SC-10/12 → `:150-152,200-205`.

No overlapping task-owned files. Dependencies serialize the cutover; T-04 explicitly owns cumulative compiler/matrix checks and final pinned/prospective-merge validation, avoiding stale earlier receipts. Regression checks presence independently and poisons each real source; it does not rely on absence-only checks or replace runtime assertions with compiler success.

Architecture is appropriately flat: one pinned compiler command shared by local use, CI and QA; native CI aggregation and directory discovery reused; one subprocess integration script, no speculative adapters, new registration layer or production API typing expansion. DEC-35/98/174/179/183/187/212/217 remain semantically compatible. DEC-36/163 add no unmet obligation; DEC-211/213 support ordinary complete discovery and external temporary mutation probes. DEC-183's accepted workflow self-protection limit remains explicit.

## Principles applied

- Type System Discipline: retain fixture payload information and literal narrowing; no compiler suppressions or new any casts.
- Delete First: reuse existing checks/aggregation and remove the obsolete activation reason rather than add enforcement layers.

Open questions: none. Read-only review; no production checks, tests, builds or diff review performed.
