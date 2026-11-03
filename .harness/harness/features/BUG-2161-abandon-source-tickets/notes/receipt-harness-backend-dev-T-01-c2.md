# Receipt — harness-backend-dev — BUG-2161 T-01 (cycle 2 correction)

BLUF: two assessed contract gaps in T-01 are fixed within the existing intent (no amendment). Signed verify exit 0, 23 s, no FAIL. SC-07 is not claimed. Builds on c1 (`receipt-harness-backend-dev-T-01-c1.md`, unchanged).

## Corrections
1. `_abandon_plan`: a source that is also a task issue now gets its own `source_comment` (the original reason file) and is closed once, by the task entry. A source equal to the parent is skipped (the parent already has comment and close). Previously both cases were suppressed entirely, so a task-issue source received no reason.
2. `cmd_abandon` dry run prints `gh-sync: would ensure the abandoned label exists` when the plan is non-empty, matching the apply path's `ensure_labels`; an empty plan prints no label line and creates no label.

## Red-first (gh-sync.py reverted to the c1 commit via hash-verified stash; restored identical)
- Unit: FAIL AS-03 (planner: task-issue source comment/single close), AS-06 (dry-run label line).
- Integration: FAIL `dry run names the label setup ... and a reason line for the task-issue source #41`; FAIL `a source that is also a task issue receives the ORIGINAL reason file exactly once`. Pre-existing and other new checks passed. These are semantic failures, not unsupported-option (the flag exists since c1).

## Tests changed
- tests/unit/test-gh-sync-abandon-sources.py: AS-03 rewritten (task-issue source: comment 41, comment+close 51, single `issue` entry for 41, parent not duplicated); AS-06 also asserts the label line.
- tests/integration/test-gh-sync-abandon.py: new cases — dry run label line + reason line for task-issue source #41; real run posts the original `--body-file` once on #41 and closes it exactly once while #52 is fully disposed; empty plan has no label line and no `label create`.

## Verify (as plan.yaml T-01)
```
python3 tests/unit/test-gh-sync-abandon-sources.py && python3 tests/integration/test-gh-sync-abandon.py && python3 tests/integration/test-gh-sync-ship.py
```
Exit 0, 23 s, zero FAIL: unit 20 PASS; integration 164 ok (160 + 4 new checks); ship 78 ok.

Commit: the commit carrying this file (`git log -1 --format=%H -- <this receipt>`), subject `[harness:t-01]`.
