# STATE

## Current

- feature: FEAT-42-one-root-resolver
- run: 2026-08-26-7-eng (harness-eng-lead) returned BLOCKED. No run in flight.
- squad: engineering
- status: Building. Plan and BRIEF approved 2026-08-27, committed at ea71a1c.
- T-01, T-02, T-03, T-06 are `done`. T-04 and T-05 are `building`: their code is complete and
  verified, their gates are red for reasons outside the squad's authority. 14 tasks remain, all
  main-session-direct.
- cycles_used: 5 of 10 (one send-back inside 2026-08-26-7-eng, on T-05, for filing two new failures
  against its own mid-task state instead of the T-04 baseline). runs: 7 of 20. Both within budget.
- ORCHESTRATOR SCOPE IS NOW EXHAUSTED. All five `team` tasks are executed. T-07 through T-20 are the
  main session's under DEC-174.

Verified BY ME at disk after the run returned, with the registry at empty:

- `run-unit-tests.sh --kind all`: SUITE_EXIT=1, 1034 result lines, exactly 5 FAIL — four INV-27/
  INV-29 cases plus the `test-check-state.py` script verdict, and nothing else. Baseline at a1658c2
  was SUITE_EXIT=0, 1013 lines, zero FAIL, measured by me before dispatch.
- T-06's verify block run verbatim: prints `T-06-OK`, exit 0.
- T-04's grep clauses: `harness_root` = 0 across the whole bin directory (was 40 across 17 files at
  a1658c2); `factory_config.py` chain = 0.
- T-05's three chain sites are clear. Its two-way library proof reproduced: the after-set is 87 lines
  all PASS; the before-set is 51 FAILs whose tracebacks all name the restored copy under `/tmp`,
  because it has no sibling `bin/` and its imports die. The code is correct; the plan's verify TEXT
  is what fails.
- `harness_boundary.py` top-level imports by AST parse: exactly `os`, `re`, `sys`.
- `check-state.sh` exits 0. Notes only, no violations.

SC-01 is 16 occurrences across 12 files, and 2 of those 16 are a regression this run introduced. It
was 19 across 15 before the block. Five were removed as planned; the arithmetic should have landed on
14. `gh_cost_log.py:112` (a docstring) and `layout_migration.py:101` (a comment) each had ZERO at
a1658c2 and now carry one, each explaining the new resolver by naming the variable it replaced. Both
are prose, neither has any behavioural effect, and both are one reword away. No gate can see them:
every per-task verify greps only its own files, and the whole-directory count exists solely in T-07,
which runs last.

## Open Questions

- Q17 (BLOCKING, plan change, pm's): nothing owns the repair of `test-check-state.py`'s fixtures.
  After T-04 they redirect the root with the retired variable plus a `SPEC.md` probe, so 5 cases now
  grade the live repository. DEC-174 am.4 bars the squad; T-12 owns `check-state.sh` but its `files:`
  omits the test. Widen T-12 or add a task.
- Q18 (BLOCKING, plan change, pm's): T-05's verify restores `check-plan-routes.py` to a bare tmp path
  instead of the sibling-bin pattern the other six two-way proofs use, so its diff step cannot pass
  however correct the code is. Reproduced under my own hand.
- Q19 (NEW, non-blocking, trivial): the two prose occurrences above must be reworded before T-07 can
  reach zero. Two lines.
- Q20 (NEW, non-blocking, harness defect): `validate-digest.py` releases a returning agent's claim
  (step one) and THEN refuses the return on children-in-flight, so a blocked lead runs on unclaimed
  and invisible to `dispatch-guard`. Contradicts DEC-201. T-17 does not close it — it ignores only
  FOREIGN-session children, and the lead's were same-session and live.
- Q21 (NEW, non-blocking): a stray `state.yaml` was written into the MAIN checkout under
  `runs/2026-08-26-7-eng/`. It needs deleting from outside this worktree. The domain hook permitted
  it because path-shape authorisation cannot see WHICH CHECKOUT a path belongs to.
- Q22 (NEW, non-blocking): `test-bash-write-guard.py` and `test-check-domain.py` fail when run
  directly (2 and 7 failures) but contribute none under `--kind all` in the same tree. Red standalone
  and green under the runner is a hermeticity or cwd defect, which is this feature's own subject.
- Q23 (BLOCKING for T-10/T-12, plan change): the two-way library proof is DEGENERATE. The outer
  `HARNESS_PROJECT_DIR` the verify exports is inherited by every subprocess through `dict(os.environ)`
  and outranks each case's own redirect, so both copies grade the same wrong root and the diff agrees
  trivially. Measured by the lead for T-10 and T-12; the shape is identical in T-11, T-14, T-15 and
  T-16, which nobody verified. I confirmed independently that none of the six test files strips the
  variable, and that `check-state.sh:22` prefers it with no marker check.
- Q9 (OPEN, non-blocking): T-13's stated rationale for deleting `KNOWN_DIRECTORY_PROBE` is false
  after T-02. The deletion is still right; only the reason changes.
- Q10 (OPEN, non-blocking): `resolve_root` probes with `os.path.isfile`; `check-plan-routes.py:498`
  uses `os.access(..., os.R_OK)`. At T-13's cutover an unreadable-but-present `team-config.yaml`
  flips from "not a root" to "is a root".
- Q12 (OPEN, non-blocking): `test-validate-digest.py` is not hermetic. Its 6 `[hook]` cases read the
  LIVE registry and returned three different answers across this one run from one unchanged file.
- Q14 (OPEN, non-blocking, plan fidelity): T-04's `files:` named 11 paths; the member touched 22, and
  the widening was necessary rather than optional. Of the eight files the dispatch called
  "prose-only", exactly ONE was.
- Q15 (OPEN, non-blocking, harness defect): `bash-write-guard.sh` refuses a command whose PROSE body
  contains an angle-bracket placeholder or an ASCII arrow, parsing it as a redirect. Three
  occurrences on this feature.
- Q16 (OPEN, non-blocking): `gh-sync.py` has `start-task` but no per-task finish command, so only
  `cmd_ship` writes the Done station.
- Q3 (OPEN, non-blocking — DEC-179 gap): the route check resolves from each task's literal `files:`
  and is structurally blind to what a `verify:` block touches. Q14 and Q18 are both casualties.
- Q4 (OPEN, non-blocking): D-05 records 20/16, D-12 supersedes with 21/17.
- Q7 (OPEN, non-blocking): superseded in detail by Q15.
