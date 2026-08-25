# STATE

## Current

- feature: FEAT-40-harness-writes-done
- run: PLAN PHASE COMPLETE. All five carried questions ruled and folded in; a wrong premise about
  the read-back bound was caught by engineering and corrected. The plan is 11 tasks, 13 decisions,
  REQ-01..REQ-12 all traced. Awaiting the operator's signature on BRIEF.md and plan.yaml.
  cycles_used 5/10, 6 runs vs informational bound 20.
- squad: none
- status: Plan

<!-- THE READ-BACK BOUND WAS THE NEAR MISS. pm asserted, and honestly flagged as unreviewed, that
     scheduling board_lifecycle's audit inside ship left DEC-203's six read-back purposes unchanged.
     eng-lead ruled SEVEN, and it was not a judgement call: DECISIONS.md:5731 (DEC-186 am.2) bounds
     the workflow read to /harness-init with the words "no other surface makes this read", and
     board_lifecycle.py:867 is exactly that read. I verified all three facts myself before spending
     the cycle. Had this gone to the operator as a question rather than to engineering, the likely
     outcome was a signature on a plan that authors a FALSE PERMANENT DECISION. Five sites were
     corrected, including D-07 in the approval-gated decisions: block.

     THE SUITE IS GREEN, measured by me at a60bc49, one kind at a time, nothing else running, no
     environment variable set: --kind unit 355 PASS / 0 FAIL / exit 0; --kind integration 26 of 26,
     zero FAIL lines, exit 0. The predecessor's eight-script red was stale runtime state in the
     untracked, gitignored .harness/.inflight-claims.json, which is why the main checkout and CI
     were green while this worktree was red. Filed as #843.

     ID REUSE: answers-2026-08-25-01.md:36 ruled "delete T-11 and D-12" — the SUITE-QUARANTINE task
     and decision, and they ARE deleted. pm reused both freed ids for the close-task deletion.
     Internally consistent; the hazard is only cross-document. -->

## Open Questions

- BLOCKING, MAIN SESSION — BRIEF.md's `## Approval` is unsigned and is the sole remaining
  check-state.sh violation. plan.yaml's `approval.status` is `pending` and correct: the task set
  changed again this run. No agent may write either.
- BLOCKING, OPERATOR — SCOPE CALL. The falsified Item-closed premise survives at three UNPLANNED
  comment sites, verified real at HEAD by engineering: `gh-sync.py:898`, `check-state.sh:1416`,
  `check-state.sh:1479`. All three are comment/docstring only, no test asserts them. T-04 owns the
  first; T-08 is the ONLY legal home for the other two under the DEC-174 carve-out. No new task is
  needed either way. Fold in, or backlog?
- NON-BLOCKING, OPERATOR — if the fold happens AND the comment at `gh-sync.py:898` cites DEC-203 by
  name, T-04 then needs `depends_on: T-03`. As the plan reads now, T-04 correctly stays `[T-01]`.
- NON-BLOCKING, OPERATOR — the T-11/D-12 id reuse. Renumber, or accept with the provenance note?
- NON-BLOCKING, OPERATOR — `wayfind.py:318` runs `gh issue close` through a Python subprocess, so
  the new Bash gate is blind to it exactly as it was to `close-task`. Same leak class, outside the
  mirror. Scoped out in BRIEF.md. File separately?
- RESOLVED this run — Q4 (D-11 stands), Q5 (no prototype), Q6 (audit inside `ship`, SC-17),
  Q7 (DEC-200 untouched, filed as #844), Q8 (`close-task` deleted as T-11, REQ-12 and SC-16),
  Q15 (SEVEN read-back purposes, five sites corrected).
- CLOSED BY MEASUREMENT, this run — the station half of the #818-#830 record. I re-derived it live:
  all thirteen read CLOSED and sit at `Review` today, so both halves of what T-03 writes into
  DEC-138 amendment 8 are true.
