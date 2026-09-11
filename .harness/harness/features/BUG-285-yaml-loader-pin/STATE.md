# STATE

## Current

- feature: BUG-285-yaml-loader-pin
- run: .harness/harness/features/BUG-285-yaml-loader-pin/runs/2026-09-11-04-goalcheck-product/state.yaml
- squad: none
- status: awaiting-user

Rescoped on the operator's 2026-09-11 decision and re-panelled. Three tasks: T-01 (unchanged, the
gh-sync.py regression pin), T-02 (the actual fix — factory_decompose.py:121's YAML loader replaced
by a JSON read) and T-03 (a unit fixture over the new reader). Panel cycle 1 FAILED on a high both
readers found independently; it is fixed and verified closed at source. Panel cycle 2 PASSES,
severity_max low, must_fix empty. The goal-check of the amended plan ran and PASSED, and all three
readers — should-not-exist, scope, goalcheck — are recorded in plan.yaml's panel. Nothing builds
until the approval state below is resolved.

## Open Questions

- BLOCKING — the approval state is inconsistent and no tool can fix it. plan.yaml reads
  `approval.status: approved` (mruangutai, 2026-09-09, commit bb488145) over a task set amended
  repeatedly since; BRIEF.md reads `pending`. `sign-approval` hardcodes `approved`, `amend` rejects
  `--key approval`, `apply` carries the base's approval bytes verbatim, Edit/Write/redirect denied.
  There is no approved -> pending route for anyone. The operator must either re-sign the amended
  plan knowingly or supply a reset route.
- BLOCKING — the operator has not signed the AMENDED scope. The 2026-09-09 signature covers a
  one-task plan that no longer exists.
- Non-blocking, four panel findings open: PF-2242299b369215b13ad577fe4279d52e (info),
  PF-cceab610738069ec6ea1a56ddc058195 (info), PF-142f3a51c0d0152899db48cf7cbdfe31 (low),
  PF-a5b9a3c81ee99295515d75f5a776ebae (low). Two highs are recorded resolved by T-02. Recording
  acceptance of an open one needs `sign-approval --overrule PF-<id>:<reason>`.
- Non-blocking — PF-142f3a51's premise is now settled and its disposition should be re-graded, not
  re-argued. check-plan-routes.py on this plan is exit 1 with a DEVIATION line when run with cwd
  inside the worktree, and exit 0 with 0 violations when run with cwd in the main checkout. Same
  plan, same checker, different cwd; all three tasks route OK either way. The finding is about an
  unstated invocation, and the remedy is to state one.
- Non-blocking — this branch is behind main on the digest contract, in BOTH directions. Under the
  branch's copy of validate-digest.py, all six 2026-09-11 lead digests fail on a required
  `sc_status`; under main's copy all six pass and the cycle-0 panel digest instead fails on
  `severity_max: info`, which main's enum no longer accepts. No single value satisfies both
  contracts, so this cannot be fixed before the branch takes main's commits.
- Non-blocking, out of scope: gh-sync.py:516-517 reads with encoding=utf-8 but catches only OSError,
  so a non-UTF-8 feature.json escapes load_recorded uncaught, and the
  `except (ValueError, UnicodeDecodeError)` at :524 guards a value that is already a str. Same
  defect class the panel gated on, in the reader T-01 exists to pin. Separate bug, or folded in?
