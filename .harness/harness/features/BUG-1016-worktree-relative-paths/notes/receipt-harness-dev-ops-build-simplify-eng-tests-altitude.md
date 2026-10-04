# Receipt — tests-altitude — BUG-1016 T-01 (harness-dev-ops, read-only)

**BLUF: findings [].** Test responsibility sits at the right depth. Nothing is flaggable. Nothing was run (T-01 verify `python3 tests/unit/test-omp-hooks.py` referenced only).

Inspected: `git diff 8d79d63d..89b7d960 -- tests/unit/omp-hooks.test.ts` (+281/-4, one file), against `angle-altitude.md` and `delete-first.md`.

## Altitude judgements

- **Fixture seam at the right home.** `featureRoot` is an optional `fixture()` option whose default is the real CLI's no-worktree answer, `--root` echoed. No pre-existing case is rewritten; `cwd` was added to `calls` rather than a second recording mechanism. Leave.
- **One authoritative rooting rule.** `rootedHooks()` is the single local harness for all 17 BUG-1016 cases. The domain stub, lookups, domainTargets, pre and post live there once, not per case. Leave.
- **Each rule asserted at the seam it belongs to.** All cases cross the public `tool_call` / `tool_result` handlers. None reach into the cache or the matcher internals.
- **`extractEditPaths(cleanExpected)` as an oracle** (edit test) is followed by a literal expected list, so the literal pin holds. It is the only pre/post agreement check on the shared matcher, so it is not redundant. Leave.
- **Overlap checked:** "blank strings" and "absolute/~/URI untouched" both assert no lookup. Each pins a different mutant class (blank-entry handling versus scheme/tilde classification), and `~ rooted` and `pre unrooted` mutations redden different cases (receipt line 30). Not redundant (O-2). Leave.
- **"sibling runs resolve their own worktrees"** uses two separate `registerHarnessHooks` instances. It pins cache isolation against module-level state, which the single-instance cache test cannot. Leave.

## Candidates

None. No fold-in, briefing-row, or leave-with-cost items.

Named BUG-1016 behavior changes: none.

## Principles applied

- Delete First (`delete-first.md`, read this run): looked for removable duplication in the 17 cases. Found every duplicated setup already consolidated in `rootedHooks()`, so there is no removal to propose.
