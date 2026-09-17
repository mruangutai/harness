# T-19 receipt — ship trend record

PASS — `cmd_ship` records and commits one append-only trend record before board writes without allowing metric failures to block shipping.

## Test-first evidence

Pre-implementation RED command:

```text
python3 tests/unit/test-metrics-kpi.py && python3 tests/integration/test-metrics-trend.py
...
AttributeError: module 'trend' has no attribute 'kpi'
...
Ran 16 tests in 2.729s
FAILED (errors=2)
```

The failing tests required the absent trend seam and `record_ship` behavior.

## Scoped verification

Executed verbatim:

```sh
python3 tests/unit/test-metrics-kpi.py && python3 tests/integration/test-metrics-trend.py && python3 -c "import ast,sys;m=ast.parse(open('.claude/skills/harness/bin/gh-sync.py').read());f=[n for n in ast.walk(m) if isinstance(n,ast.FunctionDef) and n.name=='cmd_ship'];sys.exit('cmd_ship absent from gh-sync.py') if not f else None;names={getattr(c.func,'attr',getattr(c.func,'id','')) for c in ast.walk(f[0]) if isinstance(c,ast.Call)};sys.exit(0 if 'record_ship' in names else 'cmd_ship never calls record_ship')"
```

Verbatim output:

```text
................
----------------------------------------------------------------------
Ran 16 tests in 2.743s

OK
.....trend: ERROR - ship record append failed: duplicate trend record for FIX-NOSHIP
ok record_ship succeeding commit branch is clean and tracked
.ok record_ship FAILURE-BRANCH appends despite commit failure
....ok touchpoints post-instrumentation absent file is zero
.ok touchpoints pre-instrumentation is unavailable not zero
...
----------------------------------------------------------------------
Ran 14 tests in 0.524s

OK
```

Executed cases: 30 total. The integration cases exercise duplicate refusal, successful clean/tracked git commit, non-git commit failure while retaining the appended record, and AST-verified `cmd_ship` placement/non-fatal wrapper.

## Scope amendments applied

- Test paths are `tests/integration/test-metrics-trend.py` and `tests/unit/test-metrics-kpi.py`, replacing the former `.claude/skills/harness/bin/test-metrics-*.py` paths.
- The scoped verify is the approved amended command above, with those two replacement paths.

## Source hashes

```text
4dbaddb994eb500399dd33596ee4a3eceecd00614a9ab6fe4ffbfa1d72b421e4  .claude/skills/harness/bin/dashboard/trend.py
9c2c663fec6faa4e22580a95dde86f8a883096442867b9acf474ea64ee817852  .claude/skills/harness/bin/gh-sync.py
5b49d6e1285edcb2040408ccd3dcf86900418e90d8d6188ab7a9de62cdef64f5  tests/integration/test-metrics-trend.py
c6538d1fc5e4c6a75d954b85bd76b7347beecf441ffd46daaab5c563e8328ce5  tests/unit/test-metrics-kpi.py
implementation commit: 9fbada48d05b3d8a09ba3c7231065dcbccfd46c9
```
