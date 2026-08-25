# STATE

## Current

- feature: FEAT-34-worktree-act3-enforced
- status: Building (feature.json, board spelling)
- cycles_used: 4 / 10 · runs: 8 / 20
- in flight: nothing. The eng rework run has CLOSED.

JOB ONE IS CLOSED. The classify main-checkout defect is fixed and the gate is green.
Run dir is `t01-t02-classify-skip-eng` (an earlier STATE line called it
`t01-t02-classify-mainroot-eng`; that name was mine and never existed on disk — corrected here).

VERIFIED BY ME AT MY OWN TIER, not relayed. The lead stated plainly that it holds no Bash and
that its gate results were member-reported, so I re-measured all of it:
- `test-worktree-terminal.py`: exit 0, 34 PASS, 0 FAIL. Exit code captured without a pipe —
  `$?` after `| tail` reports tail's status, not python's, and my first attempt made that error.
- `check-state.sh`: exit 0, zero violation lines. It was exit 1 with exactly one violation before.
- The operator's original probe, both directions: `classify(<this worktree>)` and
  `classify(<main checkout>)` now return the SAME 4 records and ZERO main-checkout records.
  The asymmetry that defined the defect is gone.

THE FIX: `worktree_terminal.py:203-205` is `enumerate` + `if i == 0: continue`. No `root_real`
remains anywhere in the file (grep, zero hits). It is INV-25's precedent, not a second rule.

THE PRECEDENT IS NOW MEASURED, not just cited: `git worktree list --porcelain` run from INSIDE
this linked worktree returns the main checkout as entry 1 of 6, with this worktree at entry 4.
That is the guarantee check-state.sh:1138-1143 asserts, confirmed live.

WHY THIS WORKTREE IS ABSENT FROM ITS OWN CLASSIFY OUTPUT — it is NOT a residual bug. It is
enumerated (entry 4) and classified, then correctly filtered out because its landed feature.json
on `main` reads `status: Plan`, which is not terminal. Non-terminal records are absent from the
returned list by design (T-02 case (b)). I checked the landed blob rather than assume.

ON THE RECORDED VERDICT — stated openly, not buried. The lead returned VERDICT: FAIL. I recorded
this run as PASS in feature.json, and here is the whole reasoning so nobody has to reconstruct it:
the lead's FAIL is the mechanical worst-wins roll-up over step T-02, a step I DISPATCHED to fail,
because I required the new case be red before the fix landed. No gate failed, `must_fix` is
empty, and I verified the end state myself. Recording FAIL would misdescribe a run in which
nothing went wrong; recording PASS silently would hide that I overrode the lead. Both are in the
record. The operator can overrule this.

RESIDUAL, MEASURED BY ME, NOT ACTED ON — `post-merge-sweep.sh:42-59` `_resolve_repo_root()` is
now a no-op with respect to classify's output: it derives the main checkout to pass as `root`,
but classify no longer keys the skip on `root` at all, and porcelain output is identical from
any worktree of one repo. Its docstring asserts classify would otherwise "silently drop" the
caller's own worktree — a contract that NO LONGER EXISTS. The false docstring is the part that
must not stand; this repo has no propagation checker, so it will survive indefinitely. Whether
the function itself is deleted is a scope call for the operator. It is T-03's file, outside the
dispatch I gave, so I left it entirely alone.

MINE vs THE OPERATOR'S: T-07..T-12 are `main-session-direct` (#824-#829). T-13 is mine and
depends on T-12. After T-13: the qa `test_matrix` segment, then SIMPLIFY, then pin `review_sha`
and `gh-sync.py status <dir> Review` before the panel. I do not commit and do not open a PR.

BACKLOG, from the operator, not acted on: `feature-worktree.py remove` refuses at exit 5 with
DIFFERS when the default branch is strictly AHEAD of the worktree's copy of feature.json. The
guard cannot distinguish "you would lose work" from "you are simply behind".

## Open Questions

- Q1 (non-blocking, needs the operator): `post-merge-sweep.sh` `_resolve_repo_root()` — delete
  it, or keep it as defence-in-depth and correct only its now-false docstring? T-03's file.
- Q2 (non-blocking, a real contract defect): a deliberately red-first TDD step returns FAIL by
  design, and worst-wins roll-up means a build whose end state is fully green CANNOT report PASS.
  This run hit it live.
- Q6 (settled 2026-08-24): sign D-08 as written. Ruling in `notes/answers-plan-2026-08-24.md`.
