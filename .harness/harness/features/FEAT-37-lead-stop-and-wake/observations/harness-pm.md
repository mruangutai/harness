# Observations - harness-pm

- 2026-08-24: plan-merge.py apply REFUSES (exit 8) when the base plan.yaml does not exist and the
  proposal carries an approval mapping. Bootstrap is two steps: write the template's header plus a
  `approval: status: pending` stub directly, then merge the rest with no approval key in the
  proposal. check-state.sh treats a plan.yaml with NO approval block as a hard violation, so the
  pending stub cannot simply be omitted.
- 2026-08-24: FEAT-37 contradiction sweep — harness-team/SKILL.md holds no explicit stay-alive
  instruction, but :81 ("Until every step is terminal") and :112 ("Collect returns") read as one
  continuous turn, which is the ambient pressure #831's loop came from. Fixing the gap without
  reconciling those two would leave the new sentence arguing with its own section.
- 2026-08-24: harness-team/SKILL.md:196 says leads hold `Read, Glob, Grep, Agent`, but all three
  lead agent files grant `Write` too. Stale, out of FEAT-37's scope, raised as a non-blocking
  open_question rather than absorbed.
- 2026-08-24: FEAT-37 — striking a task block from plan.yaml cannot go through plan-merge.py, which unions by id and has no supersede mode; the edit had to bypass the tool. Filed as a backlog row in BRIEF.md.
- 2026-08-24: FEAT-37 — a struck block carried an unrelated second edit (DEC-198's missing forward reference to DEC-201, inside T-09). Deliberate isolation makes a block strikable but does not make everything inside it in-scope; grep the block for edits that trace to a different reason before dropping it.
- 2026-08-24: FEAT-37 — check-plan-routes.py reads domain grants only, so a DEC-174 policy condition on a team lane is invisible to it. The discharge has to be written into the task's verify: and justified in intent:, or the lane is asserted and never proven.
