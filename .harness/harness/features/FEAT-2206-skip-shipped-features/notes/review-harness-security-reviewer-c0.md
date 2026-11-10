# FEAT-2206 · T-01 · Security review c0

**PASS — in scope; no independently exploitable security regression identified.** Security-only conclusion, not a general correctness or ship-readiness verdict.

Reviewed exact `b7af829c0207522b43f978b5275a2ebdc96b3210..fe49c8df3807d875f2cd44410559966cc836b9ab` diff restricted to `.claude`, `tests`, `.harness/harness/docs`; full census: 20 paths (six checker/schema paths, twelve test/helper paths, two decision documents). Pinned diff, not current HEAD, supplies changed-source evidence.

## Scope and measured source evidence

- **In: metadata/enforcement boundary.** `check_state/ctx.py:52-109,220-228,418-450` adds text-only status classification and lazy JSON mapping comparisons, with no YAML object construction, evaluation, command construction, or metadata-driven write. Missing/unreadable/non-UTF-8 plans remain subjects. `board.py:178-195,237-255` uses shipped claims only for cross-feature issue comparisons; active fleet checks remain. `table.py:162-164` declares the new plan read dependency.
- **In: CLI boundary.** `runner.py:284-330` escapes the feature selector for its glob, preserves layout/subject preflight ahead of the shipped exit, and emits a fixed note plus the selected feature name. No new subprocess or GitHub endpoint is added; INV-30's milestone request implementation is removed. INV-29 and INV-52 retain their independent worktree/default-branch populations rather than depending on filtered `ctx.features`.
- **In: test subprocess/log/export surfaces.** `tests/integration/test-check-state-shipped.py:55-66,255-261` uses list-form subprocess arguments and exports an operator-selected local repository into a temporary directory. Its fake-gh shell body interpolates fixture-owned paths, not feature metadata. `f58_sparse_fixture.py:266-279` moves the existing open-trace wrapper unchanged; the log is test-owned. No spreadsheet export, new credential handling, dependency, or remote-request surface exists in this delta. Full-diff credential/output sweep identified no added secrets.
- **Supporting/out:** `check-plan-routes.py`, `feature-schema.json`, both decision documents, and the remaining fixture migrations update retired-row declarations, explanatory text, or tests; they introduce no separate authority or credential boundary.

## Authority and limitations

BRIEF SC-01–04, signed T-01, feature.json amendments, operator grilling, and pinned DEC-252 were read. The ability to mark a feature `done`, lenient historical parsing, retirement of INV-28/30, loss of the done-only handoff note, and deletion of the second-prober test are approved policy, not newly alleged security bypasses. Classifier conformance remains a correctness responsibility; no additional attacker privilege beyond the approved status-edit capability was established here.

PRODUCT `docs/spec.md`, `docs/decisions.md`, and `docs/architecture.md` are absent (exact-path discovery returned none); bounded operator-settled requirements govern. No unrelated control-plane guidance substituted.

Read `notes/red-first.md` (10 unit/8 integration failures; collisions explicitly already green), `notes/simplify-pass.md`, and the pin-named merge log (matching SHA, 146 files, final `verify-exit=0`). These are inspected receipts, not executions by this reviewer. No tests/builds/linters/formatters or grader run; complexity verification belongs to the code-review/QA seats under the dispatch restriction.

Findings: none. Must-fix: none. Open questions: none. No source changes.
