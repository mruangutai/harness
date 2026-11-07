# BRIEF — BUG-2180-inv26-fleet-routing

## Problem

Local check-state INV-26 sends every in-flight feature's recorded issue numbers to the owner's repository and board, ignoring factory.repo. With the recovered FEAT-01-kaya-platform in flight, it queries Harness for Kaya issue numbers and crashes on factory_gh.GhError. This blocks local checking and the Kaya recovery landing (#2180).

## Done when — by perspective

**operator** — I can rely on each in-flight feature being checked against its own repository and board. An unreadable board or unresolved binding is reported for the affected feature, not hidden or allowed to abort checks of other features.

**code maintainer** — I have an isolated regression that distinguishes correct fleet routing from owner fallback, while retaining the existing owner/unbound checks.

## Success criteria

- SC-01 (operator): Bound features' recorded parent, task and source cards are compared using their own resolved repository and board; their numbers are never contributed to the owner's lookup. Fake-gh assertions distinguish correct and misplaced bound cards, include distinct repositories sharing issue numbers, and prove a bound feature remains checkable when owner mirroring is disabled. QA demonstrates the new routing regression fails before the fix and passes afterwards.
  verify: automated evidence: integration
- SC-02 (code maintainer): The failing-then-passing integration regression retains owner/unbound positive and negative controls, including a mixed owner/bound run. Existing projection, terminal/no-recorded-task exemptions, sync-off/no-board and unauthenticated skips remain unchanged; owner cards still use the owner board independently of bound cards.
  verify: automated evidence: integration
- SC-03 (operator): When an attempted board read raises factory_gh.GhError, including a definitive unresolved-issue response, INV-26 emits CANNOT VERIFY naming the affected feature and underlying error, without traceback or silent success; other resolvable features are still compared. QA records a failing baseline and passing final regression using fake gh.
  verify: automated evidence: integration
- SC-04 (operator): An unresolvable bound-feature binding produces INV-26 CANNOT VERIFY naming that feature and the binding error, with no owner fallback; other resolvable features are still compared. QA records a failing baseline and passing final regression with one broken and one healthy feature.
  verify: automated evidence: integration

## Verification gaps

None for these CLI surfaces: unit and integration are active with runnable commands in harness.json; integration detects tests/integration/test-check-state-inv26.py. QA must also satisfy the bugfix runtime-code unit floor (DEC-217). Fake gh proves routing and error handling, not live GitHub availability; no live mutation or user UAT is required. Product tests are planned, not executed during intake.

## Constraints

- DEC-174 BLOCKS team execution of check-state gate code and its tests: main implements directly in the assigned feature worktree, retains orchestration, and delegates validation to harness-validator-lead.
- DEC-225 SUPPLIES the patch lane: one pending BRIEF of at most 120 lines, exactly T-01, no panel or goal-check; main alone signs before build, then build → validate → ship.
- DEC-221 SUPPLIES the authoritative per-feature binding resolver already consumed by INV-37; do not introduce alternate config parsing or owner fallback for bound features.
- Preserve existing eligibility, projection and offline/authentication skips except the explicitly required attempted-board-read error findings. Keep changes bounded to INV-26 and its integration test, including their explanatory comments/docstrings.
- Merge this fix before the Kaya corpus PR, as settled in the grilling artifact. Source issue: #2180; do not amend the earlier fleet-recovery feature.

## Out of scope

- #2181 project Auto-add dependence — tracked separately; this patch only reads board state.
- INV-30 and other invariants with possible owner assumptions — separate tickets if found.
- Changes to gh-sync, gh_board.set_station or the Kaya corpus — separate tooling/recovery work.

## Approval

status: approved
approved-by: operator
date: 2026-11-07
