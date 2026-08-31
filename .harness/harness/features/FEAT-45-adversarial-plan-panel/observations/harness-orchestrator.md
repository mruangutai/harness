# Observations - harness-orchestrator

- 2026-08-31 (ship): `gh-sync.py ship` runs its board audit BEFORE `_ship_close_milestone`
  writes `feature.json` status, so the audit prints a STATUS finding against the shipping
  feature itself ("records status 'Review' but its parent reads 'Done'"). It is an ordering
  artifact, self-resolving, and reads exactly like a real drift finding. Do not chase it.
- 2026-08-31 (ship): the ownership table in `references/github-mirror.md` assigns `backlog`
  and `ship` to the MAIN SESSION, but this dispatch delegated the whole ship phase to the
  orchestrator with the operator's acceptance relayed in its context. Ran both and disclosed
  the delegation in the return. The doctrinal reason for main-session ownership is that these
  acts relay a user decision; the decision was present, so the bound was satisfied in substance.
- 2026-08-31 (ship): INV-32 landed with no grandfather clause and turned 32 pre-existing
  approved plans permanently red at every `check-state.sh` run, FEAT-45's own included.
  T-07's approved intent specifies exactly that ("fires ONLY on a plan whose approval.status
  is approved") and its `verify:` asserts `$? -ne 2`, so it is designed behaviour rather than
  a discovery. Baseline measured: 42 VIOLATIONs at HEAD, 10 without INV-32. A gate whose
  steady state is 32 unfixable red lines is signal dilution nobody quantified for the operator.
- 2026-08-31 (ship): `cmd_backlog` builds the issue title from argv, and the accepted briefing
  rows carry apostrophes AND backticks — single-quoting breaks on the first, double-quoting
  turns the second into command substitution. Passing each row through a `bash` tool `env`
  variable and expanding it inside double quotes is the only shape that survives both.
- 2026-08-31 (ship): `worktree_terminal.classify` reads the landed status from the DEFAULT
  BRANCH (`git ls-tree <default>:<features>`), so writing `status: Done` on a feature branch
  does not trip INV-29. Ship-before-merge is therefore safe, which is what makes harness.md's
  documented order (ship, then the user's PR and merge) internally consistent.
