# BUG-2420 T-01 — red first

Pre-fix base: `d5be53927009df8e7848f860f9d0b4b03b89f9ad` (build-entry commit; stations.py identical to 9eb07b4f). Tests written, production untouched.
Pinned module: `git show d5be53927009df8e7848f860f9d0b4b03b89f9ad:.claude/skills/harness/bin/plan_merge/stations.py` (sha256 ceef2a6b42eb2129c0d1a7bae071404287911ad10002738fb85623bf19738b9a). Test blobs: unit `4bee13087c80da239186404766e4e7172af347a7`, integration `4077b9aaacef4c13dd4b84838f061c48f5785dfb`.
Env: HARNESS_PROJECT_DIR and HARNESS_AGENT_TYPE unset; cwd `/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2420-plan-merge-first-task-station`.

Red finding beyond the filed bug: on a status-less task whose `verify:` block holds `status: prose`, the pre-fix `_status_in_task` accepts that deeper block-scalar line as the task's status and REWRITES it (exit 0), silently corrupting a signed field. The signed intent covers it ("do not confuse nested text ... with its own field"); the fix matches a status line only at the task's own field indent.

## Unit: `PLAN_MERGE_STATIONS=<pinned> python3 tests/unit/test-plan-merge-first-station.py` — exit 1
```
PASS a status-less task gains its first station at its field indent: exit 0 
FAIL a status-less task gains its first station at its field indent: exactly the expected lines change (['    status: prose\n'], ['    status: building\n'])
PASS a status-less task gains its first station at its field indent: reports its outcome 
PASS a status-less task gains its first station at its field indent: prints APPLIED only on success 
PASS an existing status is rewritten and every other byte is unchanged: exit 0 
PASS an existing status is rewritten and every other byte is unchanged: exactly the expected lines change 
PASS an existing status is rewritten and every other byte is unchanged: reports its outcome 
PASS an existing status is rewritten and every other byte is unchanged: prints APPLIED only on success 
PASS a genuinely absent task refuses with exit 3 and writes nothing: exit 3 
PASS a genuinely absent task refuses with exit 3 and writes nothing: exactly the expected lines change 
PASS a genuinely absent task refuses with exit 3 and writes nothing: reports its outcome 
PASS a genuinely absent task refuses with exit 3 and writes nothing: prints APPLIED only on success 
FAIL the first station sits inside T-01's own mapping, before T-02 ['schema: plan/1', 'feature: FEAT-99-fixture', 'approval:', "  date: '2026-11-22'", '  approved_by: Fixture Signer', '  status: approved', 'status: building', 'tasks:', '- id: T-01', '  title: Drafted without a station', '  verify: |', '    status: building', '- id: T-02', '  title: Already stationed', '  status: ready']
FAIL T-01's verify prose keeps its own `status: prose` line ['schema: plan/1', 'feature: FEAT-99-fixture', 'approval:', "  date: '2026-11-22'", '  approved_by: Fixture Signer', '  status: approved', 'status: building', 'tasks:', '- id: T-01', '  title: Drafted without a station', '  verify: |', '    status: building', '- id: T-02', '  title: Already stationed', '  status: ready']
PASS the absent-task refusal never blames a status line 
FAIL the first-station insert on a signed plan succeeds rc=3
FAIL the signed approval block is byte-identical after the insert schema: plan/1
feature: FEAT-99-fixture
approval:
  date: '2026-11-22'
  approved_by: Fixture Signer
  status: approved
status: building
tasks:
- id: T-01
  title: Drafted without a station
- id: T-02
  title: Already stationed
  status: ready

FAIL test-plan-merge-first-station.py
```

## Integration: `python3 tests/integration/test-plan-merge.py` — exit 1 (FAIL rows and summary; every other row PASS)
```
FAIL  2420: set-task-station gives the drafted task its first station (exit 0)
      | rc=3 plan-merge: T-01 is not in /private/var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/plan-merge-test-nu9_elm_/.harness/harness/features/FEAT-99-fixture/plan.yaml — it carries: T-01
--
FAIL  2420: the written plan reloads with T-01 at building
      | schema: plan/1
FAIL test-plan-merge.py
```
