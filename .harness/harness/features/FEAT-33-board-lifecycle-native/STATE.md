# STATE

## Current

- feature: FEAT-33-board-lifecycle-native
- run: .harness/harness/features/FEAT-33-board-lifecycle-native/runs/2026-08-22-02-product/state.yaml
- squad: product
- status: awaiting-user

Plan phase complete except the operator's signature. BRIEF.md and plan.yaml carry 12 tasks,
12 SCs and 14 decisions, both still pending. The four-angle simplify pass and the architecture
review both ran; every must-fix and should-fix is applied, with M4 deliberately left frozen
because only the operator can rule on it. Both suites green and both boards verified
native-correct. cycles_used 1 of 10. Terminus: signature, then a build phase.

## Open Questions

- M4 (BLOCKING, operator): DEC-186 bounds GitHub read-back to exactly three purposes and
  declares the set closed (DECISIONS.md:5528-5533; am.1 at :5600-5603 confirms it neither widens
  nor narrows). The project_workflows read REQ-02 needs is a fourth. The third purpose was added
  by an explicit operator ruling recorded as a widening by one item, so re-categorising is not
  precedent. Amend DEC-186 to four purposes bounded to /harness-init, or drop REQ-02. Both
  branches are stated at BRIEF.md:228-238; neither is pre-applied.
- Q1 (BLOCKING, operator): confirm the harness-first departure. T-01 lands kaya-ai's master
  config before the harness validator widens. Both reviewers independently verified no ordering
  is atomic, so the window is unavoidable, latent and loud; the rollback gap is now fixed.
- Q2 (operator/main session): T-04 registers the new test file in run-unit-tests.sh UNIT_SCRIPTS,
  which is mandatory because the drift detector runs over the union and exits 2 MISCONFIGURED on
  any unregistered test-*.py. FEAT-31 writes the same file and neither plan carries an ordering
  constraint against the other. Who sequences them?
- Q3 (operator, non-blocking): DEC-192 asserts six status values; feature-schema.json:32 carries
  seven including Abandoned, and SPEC.md:1866 and :1868 repeat the false claim.
- Q4 (operator, non-blocking): board 3 has "Pull request linked to issue" disabled while board 2
  has it enabled. Not one of the three the harness depends on. Enable it?
- Q5 (harness defect): no agent tier below the main session holds SendMessage or a wait
  primitive, so neither an orchestrator nor a lead can correct a running subordinate; every
  attempt becomes a competing sibling spawn.
- Q6 (harness defect): check-state.sh:123 sends an unapproved BRIEF to `bad` (exit 1) while
  :139/:154 send the identical plan-pending state to `warn`, so every plan phase awaiting
  signature exits 1 by construction.
