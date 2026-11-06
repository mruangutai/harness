# Receipt — BUG-2161 simplify apply (backend-dev, serialized owner of gh-sync.py)

BLUF: all four findings applied behavior-preserving; separate per-suite reruns green and the final unpiped signed chain observed rc=0 (the original chained rc was unobserved); fix count 0.
Branch `feat/BUG-2161-abandon-source-tickets`; HEAD at start was 21bfa01d (the input pin, no drift).

## Per finding
- REUSE-1 `_fail_on`: APPLIED. Moved to start of `main()` in tests/integration/test-gh-sync-abandon.py;
  `FAKE_GH_STATIONS_LABEL_FAILS` (`*"--add-label"*`, "label service unavailable") and
  `FAKE_GH_STATIONS_COMMENT_FAILS` (`"issue comment"*`, "comment service unavailable") now use it; the
  generated shell text is identical to the old inline `.replace`.
- REUSE-2 `_all_writes`: APPLIED. Removed; 6 callers migrated to `_remote_writes`, which keeps all four old
  substring matches and adds `label create`. Old two `_remote_writes` callers (reject R2 `len>=4`, all stamped
  `plan:status: building`; R5 `len==2`, reject first-sync issues no label) do not depend on the narrower set,
  and verify stayed green. Note: `_all_writes` used startswith for edit/comment, `_remote_writes` substring (superset).
- SIMPL F-1: APPLIED. `_source_plan(rec, sources)` (pure) in gh-sync.py; `_abandon_plan` does
  `plan.extend(_source_plan(...))`. Same dedupe/parent-skip/comment-without-extra-close and order; source doc moved.
- SIMPL F-2: APPLIED. `_report_abandon_dry_run(feat_dir, plan, already_abandoned)`; `cmd_abandon` calls it and returns
  under `not yes`. Text/order unchanged. No ensure-label wrapper.

## Assertions
No `check(...)` removed, weakened or relabelled; only 6 call-sites changed predicate name (`_all_writes` -> `_remote_writes`).
DEC-203 docs intentionally unchanged: observable behavior is unchanged. Complexity numbers are static estimates; code-grade not run.

## Signed verify (T-01), from PRODUCT root, after all edits
`python3 tests/unit/test-gh-sync-abandon-sources.py && python3 tests/integration/test-gh-sync-abandon.py && python3 tests/integration/test-gh-sync-ship.py`
- Original chained run: its exit code was UNOBSERVED (output was piped through grep), so it is not claimed green. Output showed ok lines from all three suites, 25.2s.
- Per-suite recount (rc, counts): unit abandon-sources rc=0 PASS=20 FAIL=0 "ALL PASSED"; integration abandon rc=0 ok=164 FAIL=0 "ALL PASSED";
  integration ship rc=0 ok=78 FAIL=0 "ALL PASSED" (24.8s). (A BrokenPipe traceback seen once came from piping into `head`, not the suite.)
- Canonical state checker (check-state.py) run before commit: notes only in the last 15 lines seen; its exit status was NOT captured (qualification, not a green claim).
- Fix count: 0.
- Commit: af83b980d91767e279ddaf2601248c633a16c317 on feat/BUG-2161-abandon-source-tickets (gh-sync.py + test-gh-sync-abandon.py only).
- Commit subject (from the `git commit -m` I issued; not re-audited with git): `[harness:simplify] BUG-2161: extract source plan and abandon dry-run report; fold test fixtures`.
- FINAL signed chain, exact command, unpiped, run after the commit with no edits: observed `CHAIN_RC=0`, elapsed 22s; all three suites printed ALL PASSED.
