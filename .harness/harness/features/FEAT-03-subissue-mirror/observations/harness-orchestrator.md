# Observations — harness-orchestrator — FEAT-03-subissue-mirror

- 2026-07-31 (fix cycle 3): the DEC-159 handoff cap (60 lines) and DEC-150 STATE.md cap (120 lines) are
  enforced by `check-domain.sh` as a PreToolUse BLOCK, and my only write tool is `Write` — so every
  overrun costs a full-file rewrite, not an edit. I burned SIX rejected writes (handoff 71 -> 68 -> 65 ->
  63 -> 62 -> 61 -> 60, STATE 131 -> 122 -> 120) because I drafted at the cap instead of under it. Draft
  the handoff at ~52 lines and STATE at ~105, then spend the slack. Cheap check before the first write:
  the note has 4 fixed headers plus blanks, so the prose budget is really ~48 lines, not 60.
- 2026-07-31: the anchor-rot class is self-inflicted when a PLAN cites a line number in a file the
  ORCHESTRATOR rewrites. Four PLAN sites cite `feature.yaml:41` for `parent: none`; eng-lead found it at
  `:54` mid-review and my own run-08 bookkeeping moved it to `:61` in the same cycle. Recorded as Q17.
  The durable form is to cite the FIELD (`feature.yaml github.parent`), never the line — a PLAN anchor
  into feature.yaml cannot be kept true because I write that file every run.
- 2026-07-31: P-01's snapshot-delta attribution needs a baseline WITH a `by_agent` block, and only runs
  01-04 have one here (runs 05/06 recorded the delta only). I recovered run 07's cost by chaining: run
  04's `by_agent` cumulative + run 05's recorded delta = the pre-run-07 figure. Cheaper habit: keep the
  full `by_agent` block in every run's state.yaml, or record the post-run cumulative next to the delta.
- 2026-07-31: a fix task naming N defect sites has consistently undercounted. Cycle 2's task named 2 and
  the truth was 4; cycle 3's task named 4 (SC-04, T-06 intent, T-06 verify labels, T-08 am.7) and the
  truth was 6 — the two extras were the REQUIREMENT (REQ-04, falsified as written) and a VERIFICATION
  CRITERION for a human's pending edit (SC-13's second clause), which would have gone green on the wrong
  prose. Both were found by greping the behaviour word (`ship` near `parent`/`close`) across BRIEF and
  PLAN before dispatch, at a cost of one Bash call. Requirement-level and criterion-level statements are
  the two layers a task's site list habitually forgets.
- 2026-07-31: dispatching with the discriminating RULE plus a named LEAVE list, rather than a site
  survey, held both runs cheap ($16 product, $5 eng vs $24/$7 for the comparable cycle 2). The LEAVE list
  is what does the work: unnamed near-misses (PLAN:48, T-07's missing-parent text, SC-11) are where a
  member spends a spawn re-judging something already settled.
- 2026-07-31: pm found a defect class the brief did not name — an over-scoped `if origin == "created":`
  wrapping both the parent close AND the milestone PATCH would have passed every label the fix specified.
  It added a guard label in the adopted fixture. Worth admitting under "blocking AND introduced by this
  repair", because before the conditional existed there was no branch to over-scope. A narrowing fix
  creates its own new failure mode, and the fix's own test set is the place to catch it.
