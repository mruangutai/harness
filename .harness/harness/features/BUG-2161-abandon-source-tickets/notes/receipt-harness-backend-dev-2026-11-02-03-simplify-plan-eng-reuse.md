# Receipt — harness-backend-dev — BUG-2161 REUSE angle (plan, read-only)

VERDICT: PASS (3 low findings). files_touched: []. No checks run.

BLUF: Plan reuses the existing abandon planner/executor, parse_source_issues, _record_station and _prune_abandoned_runs; no second path.

## Findings (all low, reuse)

- RF-1 — plan.yaml:108. Unit file told to hand-roll the build-entry loader/check (tests/unit/test-gh-sync-build-entry.py:15-37) though tests/integration/gh_sync_support.py:849-869 has load_gh_sync/check/report, imported by test-gh-sync-open.py:23 and test-gh-sync-start-task.py:30. Cost: another loader spelling to keep in lockstep. Alternative: import them (sys.path insert of tests/integration), or state the unit dir stays self-contained.
- RF-2 — plan.yaml:106 / D-02 line 79. No station reader named; _feature_station (gh-sync.py:313) exists. Cost: second inline plan.yaml station parse. Alternative: gate _record_station on _feature_station(feat_dir) != "abandoned".
- RF-3 — plan.yaml:105; gh-sync.py:1750-1755. _post_abandon_reason not named for source comments and hardcodes "parent #". Cost: cloned helper or mislabeled report. Alternative: reuse it with a noun parameter; add a "source" plan kind in _apply_abandon_plan.

## Open questions
none
