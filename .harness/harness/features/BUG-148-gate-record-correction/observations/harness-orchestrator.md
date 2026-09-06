# Observations - harness-orchestrator

- 2026-09-06: BUG-148. Two product-lead runs on the same day reused one run dir: the goal-check
  lead created runs/2026-09-06-02-product at 21:47 and the fix run that followed wrote its own
  state.yaml over it, so only step plan-fix-c1 survives there and the goal-check run has no
  surviving state.yaml. The goal-check's evidence survived only because pm owns notes/research-*.md
  independently. Run-dir identity is not unique per run within a squad-day.
- 2026-09-06: BUG-148. A handoff note's `Authority: plan-task:T-NN.verify` pointer is resolved by
  check-domain against the MAIN CHECKOUT's feature dir, not the worktree the note is written in, so
  it is unresolvable for any feature whose plan.yaml exists only on the branch. The approval:
  pointer takes a worktree-relative path and resolves. Cite approval:, not plan-task:, from a
  worktree.
- 2026-09-06: BUG-148. `git add <dir> ':(exclude)*.lock'` staged NOTHING and exited 0 — an
  exclude-only pathspec beside a directory arg silently no-ops. Naming each file explicitly staged
  all ten. A zero exit from git add is not evidence anything was staged; check git status after.
- 2026-09-06: BUG-148. bash-write-guard refuses `rm` of a lock file inside the worktree feature dir
  when the path is given RELATIVE — it resolves the relative path against the main checkout and
  reports the main-checkout path in its refusal. Merge-tool lock files left behind by members are
  not removable from a bash tool; exclude them from the commit instead.
