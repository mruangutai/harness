# Build ruling by delegated authority — FEAT-2397 — 2026-11-22 — task stations

Authority: the operator's delegation (`notes/answers-2026-11-22-signoff.md`). Ruled by
`fable-advisor` (`AdvisorC3Stations`).

**Problem.** The signed plan (af165656) drafts its six tasks with no `status:` lines. No
plan-merge verb can create a task's first status line:
- `set-task-station` only rewrites an existing line; it exits 3 with a contradictory message
  (`T-01 is not in plan.yaml — it carries: T-01, T-02`).
- `apply` ignores `status` on items that already exist (review F7).
- `amend` refuses to add a field (BUG-1128 shape).

So T-01 cannot be set to building. Main's write domain on `plan.yaml` is `approval:` only.

**Ruling: B.** A separate patch bug, built main-session-direct and shipped to main first. Fixing
the gate inside the feature it currently gates would be circular.
- **No re-sign of FEAT-2397.** `status` is outside `SIGNED_TASK_FIELDS` (`files`, `intent`,
  `verify`; `approval.py:553`), and `cmd_set_task_station` never calls `_maybe_reset_approval`
  (`union.py:569-571`). The signature at af165656 stands.
- **No merge into this worktree.** Main runs the control-plane `plan-merge.py` against this plan,
  so stations proceed as soon as the patch lands on main.
- Not a BUG-2349 regression: that fix only opened the apply-drafting path. The cause is three
  verbs that each refuse to create a first status line; the precedent is BUG-1128.
- Option C (build without task stations) is rejected: `gh-sync.py:1817` reads an absent status as
  `ready`, never finished, so ship would deadlock after the build.

**Constraints on the patch.**
1. `set-task-station` inserts the task's status line at the task's field indent when it is
   absent. `apply` does not seed status (that would cut against #747).
2. Fix the contradictory exit-3 message. A genuinely missing task still refuses, with text that
   is distinguishable from the other case.
3. Write the tests first:
   - a table-driven unit test covering a status-less task (insert), a task with a status
     (rewrite, unchanged) and a missing task (exit 3);
   - one integration case reproducing the drafting path: inline-empty `tasks: []`, then `apply`,
     then `set-task-station`.
4. Assert that `approval.status: approved` is byte-identical after the first-station insert.
5. After the merge, FEAT-2397 proceeds with no plan change and no re-sign.
