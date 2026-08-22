# STATE

## Current

- feature: FEAT-33-board-lifecycle-native
- run: .harness/harness/features/FEAT-33-board-lifecycle-native/runs/2026-08-22-01-product/state.yaml
- squad: product
- status: awaiting-user

BRIEF.md and plan.yaml are authored and unsigned (12 tasks, 12 SCs). The four-angle simplify
pass and the eng-lead architecture review are the remaining plan-phase steps; findings are
FLAG-ONLY on a plan surface and return to harness-pm, the only seat granted plan.yaml and
BRIEF.md. Neither artifact may be marked approved by any agent — only the main session signs.

## Open Questions

- Q1 (BLOCKING, operator): widening the required station keys to six cannot be atomic across
  two repos. factory_config.py:41 declares a five-tuple and :134 tests exact set equality, and
  factory_config.py:255-257 reads a served repo's harness.json from the REMOTE at
  default_branch, never a checkout. The plan therefore lands kaya-ai's master config FIRST,
  departing from the operator's harness-first constraint for that one task and leaving a latent
  FleetError window between the two merges. Alternative: loosen the validator to
  required-plus-optional, which keeps harness first but may itself be enforcement-layer work
  under DEC-174 am.4, changing which tasks are dispatchable. Blocks signature.
- Q2 (operator, non-blocking): harness-orchestrator holds no SendMessage and no wait primitive,
  so it cannot course-correct or supervise a running lead; every attempt becomes a competing
  sibling spawn. Two were created this phase and both wrote nothing.
- Q3 (operator, non-blocking): DEC-192 asserts six status values; feature-schema.json:32 carries
  seven including Abandoned, and SPEC.md:1866 and :1868 repeat the false claim. Amendment or
  DEC-188 striking, and a DECISIONS.md-only fix leaves SPEC.md standing.
- Q4 (operator, non-blocking): check-domain.sh --resolve grants check-state.sh to
  harness-dev-ops while DEC-174 forbids dispatching a change to it. Only prose reconciles them.
- Q5 (operator, non-blocking): board 3 has "Pull request linked to issue" disabled while board 2
  has it enabled. Not one of the three the harness depends on. Enable it?
