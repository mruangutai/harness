# STATE

## Current

- feature: FEAT-33-board-lifecycle-native
- run: .harness/harness/features/FEAT-33-board-lifecycle-native/runs/arch-eng/state.yaml
- squad: product
- status: awaiting-user

Plan phase, cycle 1 of 10. BRIEF.md and plan.yaml authored (12 tasks, 12 SCs, 11 decisions) and
unsigned. The four-angle simplify pass returned FAIL and the architecture review returned
ESCALATE: not signable as drafted. A pm fix cycle is applying every finding except M4, which
needs the operator. Both suites are green at df348c6 and both boards verified native-correct,
so the remaining work is plan-quality, not premise.

## Open Questions

- M4 (BLOCKING, operator): DEC-186 bounds GitHub read-back to exactly three purposes and
  declares the set closed; the `project_workflows` read REQ-02 needs is a fourth, and the BRIEF
  re-categorises it as "a configuration read" rather than amending. The third purpose was added
  by an explicit operator ruling recorded as widening by one item, so re-categorising is not
  precedent. Amend DEC-186 (widen to four, bounded to /harness-init) or drop REQ-02.
- Q1 (operator): the plan departs from the harness-first constraint for T-01, landing kaya-ai's
  master config before the harness validator widens. Both reviewers independently confirmed no
  ordering is atomic and the window is latent, loud and self-naming, so D-06 is sound. The real
  gap is that T-01 is an irreversible cross-repo write with no stated rollback (S8), now being
  fixed. Confirm the ordering exception.
- Q2 (operator, non-blocking): DEC-192 asserts six status values; feature-schema.json:32 carries
  seven including Abandoned, and SPEC.md:1866 and :1868 repeat the false claim. Amendment or
  DEC-188 striking, and a DECISIONS.md-only fix leaves SPEC.md standing.
- Q3 (operator, non-blocking): board 3 has "Pull request linked to issue" disabled while board 2
  has it enabled. Not one of the three the harness depends on. Enable it?
- Q4 (operator, non-blocking): check-domain.sh --resolve grants check-state.sh to
  harness-dev-ops while DEC-174 forbids dispatching a change to it. Only prose reconciles them.
- Q5 (harness defect): harness-orchestrator holds no SendMessage and no wait primitive, so it
  cannot supervise a running lead; every correction becomes a competing sibling spawn. Leads hit
  the same wall this phase. Two inert spawns were created; both wrote nothing.
- Q6 (harness defect): check-state.sh:123 sends an unapproved BRIEF to `bad` (exit 1) while
  :139/:154 send the identical plan-pending state to `warn`, so every plan phase awaiting
  signature exits 1 by construction.
