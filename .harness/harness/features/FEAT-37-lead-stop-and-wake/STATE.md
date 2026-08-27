# STATE

## Current

- feature: FEAT-37-lead-stop-and-wake
- run: .harness/harness/features/FEAT-37-lead-stop-and-wake/runs/2026-08-27-02-t07-t08-eng/digest.md
- squad: none — awaiting re-dispatch
- status: building

**SIX TASKS. FIVE DONE — T-01, T-02, T-04, T-05, T-06. ONE PENDING — T-09.** Runs 15/20, five
remain. Cycles 1/10. Numbering is NOT compacted; the gaps are deliberate.

**THE EVAL WAS DRAFTED AND THEN STRUCK WHOLE at build time, 2026-08-27, on the operator's ruling.**
Two tasks went with it. The strike records are `plan.yaml` D-14 and D-16 — the authority, and the
struck ids are named there rather than here, because a live STATE.md may not cite a task its plan no
longer holds.

**Why it was struck, because the reason matters more than the removal.** The eval graded a labelled
dataset in which ONE agent wrote **both the grader and the labels**. A failure meant only that those
two disagreed with each other; it said nothing about the playbook under test. The task's own intent
conceded the closure. The check that actually puts the playbook under test is SC-08, which reads a
real dispatch.

**DEC-70 IS NARROWED, NOT WAIVED, and T-09 carries it.** The eval kind is **not** excluded — a
blanket exclusion was considered and refused, because it would turn evals off for every future prompt
and model change to buy one feature's passage. Reclassifying the playbook edit as `docs` was refused
as false: T-02 changes what an agent DOES. T-09 rewrites DEC-70's own body to scope the eval
requirement to prompt, model and tool-integration changes, and records that a markdown playbook an
agent preloads is graded by conduct instead.

**THE WRITE-DENIAL BLOCKER IS GONE, and it was measured rather than assumed.** The eval could not be
written because the `PreToolUse` hook runs the OUTER checkout's `check-domain.sh`, which reads the
OUTER `team-config.yaml` and never saw a grant that existed only on this branch. That grant is now
reverted — its consumer is gone. T-09 writes `.harness/harness/docs/`, which the OUTER resolver
already names `harness-documentor`, verified with the outer copy and not this worktree's. **No
worktree-rooted session is needed.**

**A DEFECT THIS EXPOSED, filed as scope on issue #910, not fixed here.**
`check-plan-routes.py` validates routes against the BRANCH's `team-config.yaml`, not the config the
write hook will consult. It printed `OK` for a route minutes before every write on it was denied.

## Open Questions

- Q1 (was: the eval's author) — CLOSED by the strike. No eval, no author.
- Q2 (was: the grader firing one rule alongside others) — MOOT. The grader is unwound.
- Q3 (the route checker validating against the wrong config) — folded into issue #910 as scope, by
  operator ruling. Not this feature's work.
- Q4: `notes/root-cause-*.md` is in no member's domain, so debug reports fall back to receipt paths.
- Q5: engineer DIGESTs carry no `files_touched`, so a member that wrote a receipt reported no files.
- Q6 (the #866 deadlock) — half closed by FEAT-42. The dispatch end is fixed; the return end is what
  this feature corrected. This feature does not close #866 and never claimed to.
- Q7: single-flight is keyed per checkout, so several orchestrators' children can share one registry.
- Q8: a lead holds no `SendMessage`, so a finding made after dispatch cannot reach a member in
  flight. That is D-03's deliberate consequence, not a defect to fix here. Backlog.
- Q9: the `gates` block in `harness.json` — `qa_gate`, `review`, `uat`, `merge` — is read by NO
  script. Agents honour it as prose. Folded into issue #910 by operator ruling.
