# STATE

## Current

- feature: BUG-2399-run-records-staged-at-ship
- run: .harness/harness/features/BUG-2399-run-records-staged-at-ship/runs/2026-11-23-02-validate-validator/state.yaml
- squad: validator
- status: building — validate c1 ESCALATE over 9db1ba98; must_fix open, owner main session (T-01 main-session-direct); rework round 1 of 1 pending
- review_sha: 9db1ba98209df49017e73fae13da56f3e240086c (stale once the fix commits; re-pin to the fix tip, then `gh-sync.py status review`, then one `fix`-style re-verify run to harness-validator-lead)
- cycles_used: 0 / 10 (attribute 1 by re-closing run 2026-11-23-02 with --cycles-used 1 once the main-session fix lands; regate judgement on the next run-start)
- rework ruling: 1 round / 45 min (notes/answers-2026-11-23-signoff.md); rework_minutes 8 at close

## Open Questions

- Q1 (blocking, operator): SC-03's "manual force-add is removed" clause has no target — base 9eb07b4f harness-ship.md:38-54 carries no force-add text. Recommend: accept the clause as vacuous (the hand step was practice, never doc), SC-03 graded on its other clauses; alternative is a pm amendment of SC-03 under approval.
- must_fix (substance, T-01/SC-01, med): prune-run-evidence.py `_run_files` os.walk has no onerror, so an unreadable surviving subtree (e.g. qa/) is silently omitted and the pruner exits 0 — surface the traversal error (non-zero, named path) and add a regression. Source: notes/review-harness-code-reviewer-c1.md:17, goalcheck c1.
