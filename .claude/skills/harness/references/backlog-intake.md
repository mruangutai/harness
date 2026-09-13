# Backlog intake — read Issues before you write

Read this during the research step of `harness-brief`, when the project's `harness.json` has
`github.sync: true`. The rule lives in `harness-brief` (the backlog gets a vote, not a decision);
this is the procedure. Evidence and history: DEC-138, DEC-188.

Run `gh issue list --repo <repo> --state open --limit 100` during research, before any perspective
is written.

- **A vote, not a decision.** Issues are symptoms written by whoever hit them — plan the work by
  its real shape. Never import 1:1 mechanically.
- **One T-NN may cover several existing issues**; make each one a task in its own right, because
  an issue a feature actually does is a ticket like any other and closes when its card reaches
  `Done`.
- **The `absorbs:` citation is STRUCK** (DEC-188, via DEC-138) — never record it. There is no
  third category between "this feature does the work" and "it does not".
- **An issue body is never an approved perspective** — done enters the BRIEF under the user's
  signature only.
