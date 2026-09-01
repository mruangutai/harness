# Efficiency angle — FEAT-41 plan.yaml (T-06, T-10 verify) — flag-only

BLUF: one finding. `test-gh-sync.py` is a 149 s whole-suite run with no case-selection
mechanism, and the plan's `verify:` invokes it in full **twice** (T-06, T-10) — T-10 depends
on T-06, so most of what its run re-proves is already green from T-06's own pass. Everything
else measured (T-01..T-05, T-07..T-09, T-11..T-13 verify clauses, the check-domain.sh SHAPE
region and post-Bash sweep additions) is either cheap, already gated by the stamp mechanism, or
a deliberate boundary run — not flaggable.

## Finding: T-06 and T-10 verify re-run the same 149 s whole suite, most of it unrelated to either task's change

- **File/line**: `plan.yaml:376-379` (T-06 `verify:`) and `plan.yaml:609-611` (T-10 `verify:`),
  both naming `python3 .claude/skills/harness/bin/test-gh-sync.py`.
- **Summary**: `test-gh-sync.py` is one monolithic script — no `argparse`, no `sys.argv`
  branching, no pytest/unittest node-id selection (checked: `grep -n "sys.argv\|argparse"` on
  the file returns nothing). It runs ~9 sequential check-groups (abandon/detach, ship's
  parent-close ordering, start-task's station guard, `load_recorded`, `save_recorded` atomicity,
  etc.) unconditionally, top to bottom, every invocation. T-06 changes only the station-decision
  call sites (`cmd_start_task`, `cmd_status`, `cmd_backlog`, `cmd_ship`'s done pass) via the new
  `project()` function; T-10 changes only `cmd_ship`'s commit-the-terminal-write and
  worktree-refusal logic. Neither touches `abandon`, `detach`, `load_recorded`'s parser, or
  `save_recorded`'s atomicity — all of which this suite re-runs anyway, twice.
- **Concrete cost, measured**: `time python3 .claude/skills/harness/bin/test-gh-sync.py` at the
  worktree's current HEAD → `2:29.17` wall clock (149.17 s), `19.63s user 12.70s system`, exit 0,
  `ALL PASSED`. T-06's `verify:` runs this once; T-10 (`depends_on: [T-06, T-07]`) runs it again
  — **~298 s (~5 min) spent on one file's suite across two sequential dependent tasks**, versus
  the plan's other whole-file verifies measured the same way: `test-check-domain.py` 15.3 s,
  `test-check-state.py` 20.1 s, `test-check-plan-routes.py` 44.3 s, `test-plan-merge.py` 2.8 s,
  `test-post-merge-sweep.py` 8.7 s, the argv-less `check-plan-routes.py` full-tree sweep 9.3 s.
  `test-gh-sync.py` is the single largest verify-time cost in the whole plan, and it is paid
  twice for two narrowly-scoped changes. (The research note's claim that "per-task verify: can
  name one file and stay far under 60 s" does not hold for this file — worth naming since it
  will read as settled otherwise.)
- **Alternative**: `test-gh-sync.py` has no selection mechanism to target only the checks a given
  task's change bears on, so "run the targeted case" isn't available today without adding one.
  A minimal, one-time addition — a label-substring filter read from an env var or a trailing
  argv token, matched against each check()'s existing description string — would let T-06's
  verify pass something like `GH_SYNC_TEST_FILTER=station` and T-10's pass `FILTER=ship` (or
  `--filter`), cutting each run to the handful of checks that actually exercise the changed code
  path instead of re-running all ~9 groups. This is a change to the test harness itself (not
  content this pass may apply — it would touch `test-gh-sync.py`, which is inside this feature's
  own T-02/T-06/T-07/T-10/T-13 file list but is TDD-exempt-neutral: adding filtering is
  infrastructure, not a tested behaviour of the product). Routing this is pm's call, not mine —
  it either becomes a small addition inside T-06 (the first task to pay the cost) or a backlog
  row; either way the 149 s number should inform which.

## Not flagged, and why

- **check-domain.sh's new checks (T-09) are not a hot-path cost.** The plan.yaml SHAPE-region
  denial fires on a regex match only (cheap); the PostToolUse sweep's new VOCABULARY rule rides
  the existing mtime-stamp mechanism (`SWEEP_WINDOW_S` / `STAMP`, `check-domain.sh:918-926`),
  which already limits the sweep to files that changed since it last ran — confirmed by the
  comment's own measurement (515 ms unbounded vs 0.2 ms stamped, on 120 files). This is reused
  architecture, not new per-call parsing.
- **T-08's new PreToolUse Bash hook (`plan-sign-gate.py`) is a disclosed, accepted cost.** D-07
  states "about 40 ms" per Bash call. Measured the working precedent it's modelled on,
  `gh-close-gate.py`, directly: 20.4 ms per invocation — same order of magnitude, and D-07 already
  names and accepts this trade-off. Re-litigating a signed decision's disclosed cost is noise,
  not a finding.
- **`check-plan-routes.py --all` (T-04 verify) is a boundary-step full-tree scan, not waste** —
  it exists precisely because the migration in the same task rewrites every live plan; SC-11
  independently requires the same posture for the whole suite. (Its literal `--all` flag does
  not exist on the current CLI — argv-less already IS the full-tree mode, measured at 9.3 s over
  38 feature dirs — but that is a correctness question for the flag's spelling, not an efficiency
  finding, and outside this angle.)
- **No repeated-read-across-tasks pattern found.** Files touched by multiple sequential tasks
  (`gh-sync.py` in T-02/T-06/T-07/T-10/T-13, `check-state.sh` in T-02/T-07) are edited, not
  merely read, and each task's edit depends on the prior task's already-landed content — there is
  no idle re-read one pass could have avoided.

## Settled, per dispatch — not re-litigated

DEC-174's main-session-direct lane for 12 of 13 tasks; the 11-file rename list; the deleted vs.
untouched test cases at `test-check-state.py:1660-1680` / `test-board-lifecycle.py:771-798`; the
37/8 migration counts; `plan-write.py` and `status:` naming. None of these are efficiency
questions.
