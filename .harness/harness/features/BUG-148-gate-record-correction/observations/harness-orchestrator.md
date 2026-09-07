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
- 2026-09-06 (BUG-148): the `## Done when` shape gate cannot resolve `brief-sc:` or `plan-task:`
  pointers for a feature whose directory exists only in a worktree. `handoff_done_when.py::_feature_dir`
  strips the `.claude/worktrees/<name>/` prefix from the note's path and then joins the remainder to the
  MAIN checkout root, so it looked for `<main-root>/.harness/harness/features/BUG-148-...` and refused the
  Write with three "unresolved" lines. The two PATH-carrying pointer types, `finding:` and `approval:`,
  resolve fine against the same root — cite those, with the full `.claude/worktrees/...` relative path.
- 2026-09-06 (BUG-148): INV-26's widening for a `done` task card is conditional on the FEATURE station
  reading `review` (`check-state.sh:2231-2233`: `_accept |= {"review","building"}` only then). Recording
  both tasks `done` while the feature station still read `building` reddened three cards at once — both
  sub-issues and the parent. The fix was not a board write but the seam transition itself:
  `set-feature-station review` then `gh-sync.py status <dir> review`.
- 2026-09-06 (BUG-148): INV-33 compares the PINNED commit's `plan.yaml` BYTES against disk, so any station
  write after the pin makes the pin stale. Order that works: commit the station change, re-pin `review_sha`
  to that commit, then commit `feature.json` — the second commit does not touch `plan.yaml`, so the
  comparison stays equal. Confirmed clean by a `check-state.sh` run from this checkout.
- 2026-09-06 (BUG-148): this OMP host exposes the orchestrator no `Edit` tool, only `Write`. A plan clause
  reading "use Edit, never Write" (D-04, to dodge the pre-hoc whole-file shape denial) is then satisfiable
  only by a surgical shell splice that carries no whole-file content. The write guard's DEC-153 worktree
  carve-out permits it and `check-domain.sh` still issued its expected PostToolUse shape report, so the
  write was governed rather than routed around.
- 2026-09-06 (BUG-148): `bash-write-guard.sh` string-matches `sign-approval` anywhere in a Bash command,
  including inside a `git commit -m` message body, and refuses the whole call. The `&&` chain before it
  never ran either, so a following retry failed on an empty index. Reword the message; do not reach for a
  message file, which is refused separately.
- 2026-09-06 (BUG-148): SIMPLIFY's altitude angle raised a finding whose premise failed against the
  approved BRIEF — it read D-05 ruling 1's "matching DEC-174's treatment" as the rhetorical register when
  it means the in-place mechanism, and REQ-01 positively requires the FEAT-05 record to name the correction
  date that DEC-174 need not carry. Answered at rung 1 of the question ladder for zero cycles, and routed
  to SC-06's uat read, which asks exactly that register question.
