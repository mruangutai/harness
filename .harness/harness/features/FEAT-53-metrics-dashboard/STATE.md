# STATE

## Current

- feature: FEAT-53-metrics-dashboard
- run: .harness/harness/features/FEAT-53-metrics-dashboard/runs/2026-09-01-09-product/digest.md
- squad: none
- status: awaiting-user

Plan phase, second signature pass. The operator's rulings in notes/answers-2026-09-01-plan-signature.md
are applied: D-03 now names Flask as the server framework with FastAPI+uvicorn, a Node server and the
stdlib ThreadingHTTPServer each rejected by name (DEC-1); new D-21 makes KPI 4's post-instrumentation
test computable so a never-tracked feature reports unavailable rather than zero, and new tasks
T-21/T-22 mount the charts inside the panels behind an executing render gate (DEC-4). D-20 and D-08
were confirmed as drafted and are byte-unchanged. The DEC-5 prototype was corrected and is ready for
the operator to open. The adversarial panel re-ran at cycle 2 with both readers and returned FAIL at
severity_max high; plan.yaml's panel key now records 13 findings — the operator's eight cycle-1
dispositions carried forward, plus five cycle-2 findings all open. Second signature briefing at
notes/ship-review-2026-09-01-plan-c2.md. plan.yaml and BRIEF.md still read approval pending; only the
main session signs.

## Open Questions

- The cycle-2 high finding PF-45518258 (T-16 commits the shipped dist bundle depending only on
  [T-12, T-15], so the bundle can be built before T-21 mounts the chart and nothing rebuilds it —
  the DEC-4 failure reproduced in the shipped artifact). Remedy is one depends_on line; DEC-207 bars
  a pre-signature fix dispatch, so the operator resolves or overrules it.
- Cycle-time origin: REQ-03 and the grilling say BRIEF approval, D-14/T-06/D-21 measure plan.yaml
  approval.date. Filed as backlog row B-6 but it gates the signature — either the plan changes or
  REQ-03 is reworded before signing.
- Cycle-2 findings PF-3b85f188 (D-21's epoch has no git disposition; a second clone loses it),
  PF-0f3f4101 (the spliced comment block contradicts the live YAML twice), PF-aa9c41f6 (SC-17's
  evidence kind), PF-ed0712ea (T-12's CI timing case is vacuous) — offered as backlog rows B-11..B-14.
- DEC-5: the prototype is ready and still unopened. Only the operator closes that gate.
- Harness defects, non-blocking: plan-merge.py apply splices proposal comments no verb can remove; a
  worktree vendors .claude/skills so post-branch bin verbs are unreachable in-tree; BUG-1080
  reproduces on validate-digest.py's yield path for a plan-phase feature.
