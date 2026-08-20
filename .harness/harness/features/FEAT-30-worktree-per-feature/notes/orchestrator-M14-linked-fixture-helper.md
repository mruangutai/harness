# M-14. L-1's option 2 is cheaper than it looks: the test file already builds real linked worktrees

Relevant to the L-1 must_fix (T-04 PART 3 reddening two bare-directory fixtures) and to whichever
shape pm chose in the apply round.

**Measured by reading `test-check-domain.py` at `eeabc59`.** The two fixtures that L-1 reds are bare
directories — `os.makedirs` only, verified at `:1093-1094` and `:1160-1161`, with the owner-side
entries at `:1465-1466` created as empty dirs carrying no `gitdir` file. That half of the finding is
exactly right.

**But the same file already contains the helper that makes a real one.** `_linked(path, wt_id)` at
`:1470-1479` writes a `.git` FILE containing `gitdir: <root>/.git/worktrees/<id>` plus the worktree's
own `team-config.yaml`, and notes why the manifest is needed (a root with no readable manifest falls
to the DEC-101 fail-open and proves nothing). It is five lines of body and it is used at `:1483-1484`
to build both the out-of-place and the legitimate worktree for the boundary cases.

So converting the two sweep fixtures to real linked worktrees is: lift `_linked` from a closure
inside `run_worktree()` to module scope, and call it at the two sites. The assertions do not change.

**Why this matters to the choice.** The eng lead's alternative — retain the literal
`.claude/worktrees/*/` tier as a fallback beside the new mechanism — keeps `_norm`'s fixed-segment
regex alive on that consumer, which is the mechanism the operator ruled must stop being
load-bearing. Option 2 keeps one mechanism and costs one helper move plus two call sites, on a task
that is `main-session-direct` either way. The lead priced option 2 as unavailable because the plan
forbids changing an existing case; that constraint is pm's own, and the helper is why the price of
relaxing it is small.

**Not a ruling.** Which shape is right is the architecture review's call, and this note exists so
that call is made on the real price rather than an assumed one.
