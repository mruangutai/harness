# STATE

## Current

- feature: FEAT-40-harness-writes-done
- run: PLAN PHASE COMPLETE AND FINISHED. Every operator ruling is folded in. The plan is 11 tasks,
  13 decisions, REQ-01..REQ-12 all traced, and the only remaining check-state.sh violation is the
  unsigned BRIEF. Awaiting the operator's signature. cycles_used 6/10, 7 runs vs informational
  bound 20.
- squad: none
- status: Plan

<!-- THE FALSIFIED Item-closed PREMISE LIVES AT FIVE SITES, not the three the operator's ruling
     named, and the plan now owns all five. Two were found by product-lead before dispatch
     (gh-sync.py:219-220, already T-04 Step 8b) and one AFTER pm returned PASS
     (test-gh-sync.py:1615-1617, now Step 8e) — a paraphrase carrying the same false causality and
     the same D-03/DEC-192 citation, which pm's three greps structurally could not match because
     the line contains none of "Item", "closed" or "native". A twelve-pattern re-sweep found no
     sixth. THIS IS THE THIRD CONSECUTIVE CYCLE in which an enumerated site list was short by at
     least one; the lesson is that a list of sites is a hypothesis, and the class must be swept.

     gh-sync.py:851 is DELIBERATELY not corrected: T-11 deletes cmd_close_task including its
     comments, so correcting it in T-04 is work T-11 then deletes. The cost is that the false
     sentence is live in the tree between T-04 and T-11.

     THE SUITE IS GREEN, measured by me at a60bc49 one kind at a time with nothing else running and
     no environment variable set: --kind unit 355 PASS / 0 FAIL / exit 0; --kind integration 26 of
     26, zero FAIL lines, exit 0. The predecessor's eight-script red was stale runtime state in the
     untracked, gitignored .harness/.inflight-claims.json. Filed as #843.

     ID REUSE ACCEPTED by the operator: T-11 and D-12 keep their NEW meanings (the close-task
     deletion). The suite-quarantine task and decision that once held those ids are deleted. -->

## Open Questions

- BLOCKING, MAIN SESSION — BRIEF.md's `## Approval` is unsigned and is the sole remaining
  check-state.sh violation. plan.yaml's `approval.status` is `pending` and correct: the task bodies
  changed again this run. No agent may write either.
- NON-BLOCKING, OPERATOR — the sweep's BOUNDARY, not its result. The class was swept only over
  `.claude/skills/harness/bin/` and `hooks/`. `references/`, `docs/` and `.claude/commands/` were
  never swept, on the ground that T-09 owns them. Accept that boundary, or ask for one sweep of
  T-09's three files before signing?
- NON-BLOCKING, OPERATOR — `gh-sync.py:851` is left to T-11's deletion, so the falsified sentence
  is live in the tree between T-04 and T-11. Confirm that window is acceptable.
- RESOLVED — every question raised in this phase: Q4 (D-11 stands), Q5 (no prototype), Q6 (audit
  inside `ship`, SC-17), Q7 (DEC-200 untouched, #844), Q8 (`close-task` deleted as T-11, REQ-12 and
  SC-16), Q15 (SEVEN read-back purposes), the three comment sites (folded, five in total), the
  T-04 edge (`depends_on: [T-01, T-03]`), the id reuse (accepted), `wayfind.py` (#846).
- CLOSED BY MEASUREMENT — the station half of the #818-#830 record. I re-derived it live: all
  thirteen read CLOSED and sit at `Review`, so both halves of what T-03 writes into DEC-138
  amendment 8 are true.
