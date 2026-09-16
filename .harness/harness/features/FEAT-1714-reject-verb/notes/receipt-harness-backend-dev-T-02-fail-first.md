# Fail-first receipt — FEAT-1714 T-02

Run before any T-02 production edit from the feature worktree:

```sh
python3 tests/unit/test-factory-config.py
# exit 1
python3 tests/unit/test-handoff-done-when.py
# exit 1
python3 tests/unit/test-gh-board.py
# exit 1
python3 tests/integration/test-board-lifecycle.py
# exit 1
python3 tests/integration/test-gh-sync-abandon.py
# exit 1
```

Observed red output (the relevant new named checks/errors, verbatim):

```
FAIL  (T-02) TERMINAL_STATIONS is the ordered abandoned/rejected non-board tuple
1 of 117 FAILING.

PASS satisfaction: abandoned task alone binds nothing
# process exited 1 before the new rejected assertion because its current terminal predicate does not recognise rejected.

Traceback (most recent call last):
  File "tests/unit/test-gh-board.py", line 458, in <module>
    _p = gh_board.project(_plan("done", "done", top="rejected"), _rec(issues={}, parent=100))
artifact_accessors.FleetError: the feature's top-level station is not in the vocabulary: rejected — set it with plan-merge.py set-feature-station --station <one of backlog plan ready building review done>

FAIL  audit STATUS: rejected is terminal and has no board-column finding — "... records station 'rejected' in plan.yaml, which is not in the station vocabulary (backlog, plan, ready, building, review, done) ..."
1 failing.

FAIL  reject numeric report: names parent, successor, comment, label, milestone, backlog and station
      gh-sync: ERROR — unknown command 'reject'
FAIL  reject numeric: closes only parent then reseats it, comments, labels, closes milestone, and records rejected last
      rc=1 log=[]
FAIL  reject none: closes only parent without label/link or station mutation
      rc=1 log=[]
3 FAILED
```

These failures establish the absent ordered terminal vocabulary, generic terminal-consumer migration, and `reject` command before the production changes.
