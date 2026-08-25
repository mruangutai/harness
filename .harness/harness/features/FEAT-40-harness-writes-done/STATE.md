# STATE

## Current

- feature: FEAT-40-harness-writes-done
- run: PLAN PHASE COMPLETE. The suite premise was corrected (it is GREEN), and all five carried
  questions are now ruled. Two of them changed the plan: the board audit is scheduled inside `ship`,
  and `close-task` is deleted. The plan is 11 tasks, 13 decisions, REQ-01..REQ-12 all traced.
  Awaiting the operator's signature on BRIEF.md and plan.yaml. cycles_used 3/10, 4 runs vs
  informational bound 20.
- squad: none
- status: Plan

<!-- ID REUSE, RECORDED SO THE RECORD READS TRUE. answers-2026-08-25-01.md:36 ruled "delete T-11 and
     D-12" — that was the SUITE-QUARANTINE task and its decision, and they ARE deleted. pm then
     reused both freed ids for new work in the same unsigned plan: T-11 is now the close-task
     deletion and D-12 its decision. Nothing is behaviourally wrong and the plan is internally
     consistent, but any reader comparing the two documents will otherwise conclude the deletion
     never happened. Whether to renumber is the operator's call (carried as a question).

     THE SUITE IS GREEN, measured by me at a60bc49, one kind at a time, nothing else running, no
     environment variable set: --kind unit 355 PASS / 0 FAIL / exit 0; --kind integration 26 of 26,
     zero FAIL lines, exit 0. The predecessor's eight-script red was stale runtime state:
     test-validate-digest.py's [hook] cases read the LIVE .harness/.inflight-claims.json, which is
     untracked and gitignored, so the main checkout and CI were green while this worktree was red.
     Proven causally — the refusal fires ONCE per claim, so re-running drained six claims and the
     fourth run passed 14/14 with zero code changes. Filed as #843. -->

## Open Questions

- BLOCKING, MAIN SESSION — BRIEF.md's `## Approval` is unsigned and is the sole remaining
  check-state.sh violation. plan.yaml's `approval.status` is `pending` and correct: the task set
  changed again this run. No agent may write either.
- BLOCKING, OPERATOR — the falsified Item-closed premise survives at THREE UNPLANNED code sites,
  re-verified by grep at 242bba0: `gh-sync.py:898`, `check-state.sh:1416`, `check-state.sh:1479`.
  `gh-sync.py:898` cites DEC-192, which T-03 STRIKES, so after T-03 lands live code justifies itself
  by a struck decision. Both files are already opened by T-04, T-05 and T-08, so all three have a
  home without a new task — but no task currently claims them. Fold in, or backlog? Inherited from
  run 03, which died without a digest and never delivered it.
- BLOCKING, ENG — T-04 step 7c calls a NEW public `board_lifecycle.audit_findings()` in process and
  asserts DEC-203's six read-back purposes are NOT widened. If that reading is wrong, T-03 must write
  a SEVENTH purpose into a permanent decision. Raised by pm, unreviewed by engineering. Routed to
  eng-lead rather than to the operator.
- NON-BLOCKING, OPERATOR — the T-11/D-12 id reuse described above. Renumber, or accept with the
  provenance note?
- NON-BLOCKING, OPERATOR — `wayfind.py:318` runs `gh issue close` through a Python subprocess, so the
  new Bash gate is blind to it exactly as it was to `close-task`. Same leak class, outside the
  mirror. Scoped out in BRIEF.md:214. File separately?
- RESOLVED this run — Q4 (D-11 stands), Q5 (no prototype), Q6 (audit inside `ship`, with SC-17),
  Q7 (DEC-200 untouched, filed as #844), Q8 (`close-task` deleted as T-11, with REQ-12 and SC-16).
