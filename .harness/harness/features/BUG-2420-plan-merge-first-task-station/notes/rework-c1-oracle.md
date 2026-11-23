# BUG-2420 rework round 1 — byte-exact test oracle

Ruling: notes/answers-2026-11-22-rework-c1.md (fable-advisor, option A). Finding fixed: validate c0's code-reviewer med/substance — `changed_lines` compared lines by membership and `read_text` translated newlines, so SC-01's "every other byte unchanged" was not proven (QA mutant M8, CRLF insert, stayed green).

Change (tests/unit/test-plan-merge-first-station.py only): each row now carries the COMPLETE expected file and asserts whole-file equality; the fixture writes and every check reads raw bytes (`plan_bytes`), no newline translation. Production untouched.

## Red — pinned pre-fix stations.py (`git show d5be5392:...`, sha256 ceef2a6b42eb2129c0d1a7bae071404287911ad10002738fb85623bf19738b9a): exit 1
```
PASS a status-less task gains its first station at its field indent: exit 0 
FAIL a status-less task gains its first station at its field indent: the whole file is exactly the expected bytes "schema: plan/1\nfeature: FEAT-99-fixture\napproval:\n  date: '2026-11-22'\n  approved_by: Fixture Signer\n  status: approved\nstatus: building\ntasks:\n- id: T-01\n  title: Drafted without a station\n  verify: |\n    status: building\n- id: T-02\n  title: Already stationed\n  status: ready\n"
PASS a status-less task gains its first station at its field indent: reports its outcome 
PASS a status-less task gains its first station at its field indent: prints APPLIED only on success 
PASS an existing status is rewritten and every other byte is unchanged: exit 0 
PASS an existing status is rewritten and every other byte is unchanged: the whole file is exactly the expected bytes 
PASS an existing status is rewritten and every other byte is unchanged: reports its outcome 
PASS an existing status is rewritten and every other byte is unchanged: prints APPLIED only on success 
PASS a genuinely absent task refuses with exit 3 and writes nothing: exit 3 
PASS a genuinely absent task refuses with exit 3 and writes nothing: the whole file is exactly the expected bytes 
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

## Mutant M8 — fixed stations.py with the inserted line terminated `\r\n`: exit 1 (was green in c0)
```
PASS a status-less task gains its first station at its field indent: exit 0 
FAIL a status-less task gains its first station at its field indent: the whole file is exactly the expected bytes "schema: plan/1\nfeature: FEAT-99-fixture\napproval:\n  date: '2026-11-22'\n  approved_by: Fixture Signer\n  status: approved\nstatus: building\ntasks:\n- id: T-01\n  status: building\r\n  title: Drafted without a station\n  verify: |\n    status: prose\n- id: T-02\n  title: Already stationed\n  status: ready\n"
PASS a status-less task gains its first station at its field indent: reports its outcome 
PASS a status-less task gains its first station at its field indent: prints APPLIED only on success 
PASS an existing status is rewritten and every other byte is unchanged: exit 0 
PASS an existing status is rewritten and every other byte is unchanged: the whole file is exactly the expected bytes 
PASS an existing status is rewritten and every other byte is unchanged: reports its outcome 
PASS an existing status is rewritten and every other byte is unchanged: prints APPLIED only on success 
PASS a genuinely absent task refuses with exit 3 and writes nothing: exit 3 
PASS a genuinely absent task refuses with exit 3 and writes nothing: the whole file is exactly the expected bytes 
PASS a genuinely absent task refuses with exit 3 and writes nothing: reports its outcome 
PASS a genuinely absent task refuses with exit 3 and writes nothing: prints APPLIED only on success 
PASS the first station sits inside T-01's own mapping, before T-02 
PASS T-01's verify prose keeps its own `status: prose` line 
PASS the absent-task refusal never blames a status line 
PASS the first-station insert on a signed plan succeeds 
PASS the signed approval block is byte-identical after the insert 
FAIL test-plan-merge-first-station.py
```

## Green — fixed stations.py: exit 0
```
PASS a status-less task gains its first station at its field indent: exit 0 
PASS a status-less task gains its first station at its field indent: the whole file is exactly the expected bytes 
PASS a status-less task gains its first station at its field indent: reports its outcome 
PASS a status-less task gains its first station at its field indent: prints APPLIED only on success 
PASS an existing status is rewritten and every other byte is unchanged: exit 0 
PASS an existing status is rewritten and every other byte is unchanged: the whole file is exactly the expected bytes 
PASS an existing status is rewritten and every other byte is unchanged: reports its outcome 
PASS an existing status is rewritten and every other byte is unchanged: prints APPLIED only on success 
PASS a genuinely absent task refuses with exit 3 and writes nothing: exit 3 
PASS a genuinely absent task refuses with exit 3 and writes nothing: the whole file is exactly the expected bytes 
PASS a genuinely absent task refuses with exit 3 and writes nothing: reports its outcome 
PASS a genuinely absent task refuses with exit 3 and writes nothing: prints APPLIED only on success 
PASS the first station sits inside T-01's own mapping, before T-02 
PASS T-01's verify prose keeps its own `status: prose` line 
PASS the absent-task refusal never blames a status line 
PASS the first-station insert on a signed plan succeeds 
PASS the signed approval block is byte-identical after the insert 
PASS test-plan-merge-first-station.py
```
