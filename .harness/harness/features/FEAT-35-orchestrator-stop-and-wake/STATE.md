# STATE

## Current

- feature: FEAT-35-orchestrator-stop-and-wake
- run: VALIDATE ENDING AT THE SEAM on context (~300k vs 200k, DEC-159). SC-03 UNMET a THIRD time,
  new cause each time. Nothing in flight. Pin e0ae671 is STALE - it holds the nonce defect.
- squad: none
- status: Review

<!-- SC-03 failure sequence, each fix correct and each revealing the next gate:
     c0 empty candidate set (a reviewer is never agentType harness-orchestrator)
     c1 non-unique nonce (the run copied SKILL.md's printed literal)
     c2 TOOL-LEVEL filter: context-watch.py:53 ORCHESTRATOR_AGENT_TYPE, :303-304 returns None for any
        other agentType -> exit 1, no row. I VERIFIED :53 and :303-304 MYSELF, not relayed.
     c2 got exactly ONE match and derived the id correctly - the nonce fix WORKS. Only the third
     required artifact (the context-watch.py row) is unreachable by the sanctioned stand-in.
     THE AMENDMENT CLOSED ONE OF TWO TYPE FILTERS AND NOBODY SWEPT FOR A SECOND. Both the operator's
     answers file and pm's amendment note ASSERTED context-watch.py accepts the derived id; neither
     checked its source before the signature. That is the process lesson of this phase.
     PIN IS STALE: SKILL.md modified+UNCOMMITTED; working tree greps 0 for 7Q4X2M9K, e0ae671 greps 2.
     Merging as-pinned ships the defect. SC-01/02/04 were graded via `git show <pin>:` and SC-06
     certified SKILL.md:99-138 - the uncommitted edit lands INSIDE that region, so SC-06 c0 is stale.
     SC-05 partial + post-merge obligation. matrix_ok FALSE, accepted. Both artifacts signed 2026-08-24.
     cycles_used 6/10. 10 runs vs informational bound 20. NOT COMMITTED, NOT SHIPPED, PR NOT OPENED. -->

## Open Questions

- BLOCKING, OPERATOR: SC-03's THIRD clause (the context-watch.py row) cannot be produced by any
  reviewer - the tool hard-filters to harness-orchestrator. Options: (a) drop the clause, (b) accept
  the rejection ITSELF as evidence of fail-closed behaviour, (c) re-spec onto --warn-for, which
  applies no agentType filter but returns None below threshold so emits no row. The c2 lead reads
  (b); so do I - the tool refusing an id it cannot vouch for IS the safe behaviour working.
- BLOCKING, OPERATOR: commit the uncommitted SKILL.md fix and RE-PIN review_sha before merge.
  Every current verdict describes text that would not merge. Then re-confirm SC-01/02/04 (graded via
  `git show <old pin>:`) and re-grade SC-06 (its c0 certification covers the edited region).
- RECORDED: SC-05 partial, owner main session, next build/validate phase.
- NEW, MED, from the c2 lead: context-watch.py `--warn-for` (:481) applies NO agentType filter.
  Does not rescue SC-03 as written, but bears on any re-spec.
- FILED, do not re-file: #803, #804, #805, #806, #808, #810.
