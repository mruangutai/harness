# T-03 receipt

BLUF: T-03 configuration is committed at `e2f996d0b3e9ab47fcda8f3d1cfed0e0d6a43c32`; the signed verification command cannot run because its required shell runner is absent.

## Pre-edit proof (expected failure)

```text
$ python3 -c "import json;d=json.load(open('.harness/harness.json'));s={p.strip() for p in d['test_kinds']['integration']['detect'].split('|')};assert '.claude/skills/harness/bin/test-metrics-dashboard.py' in s;assert '.claude/skills/harness/bin/test-metrics-trend.py' in s;assert '.claude/skills/harness/bin/test-metrics-client-render.py' in s" && python3 -c "import json;d=json.load(open('.harness/harness.json'));c=d['test_kinds']['component'];assert c['status']=='resolved',c;assert c['cmd'] and 'run test' in c['cmd'],c;assert '.test.tsx' in c['detect'],c"
AssertionError
exit 1
```

## Signed verification (blocked)

```text
$ bash .claude/skills/harness/bin/run-unit-tests.sh --check-kinds && python3 -c "import json;d=json.load(open('.harness/harness.json'));s={p.strip() for p in d['test_kinds']['integration']['detect'].split('|')};assert '.claude/skills/harness/bin/test-metrics-dashboard.py' in s;assert '.claude/skills/harness/bin/test-metrics-trend.py' in s;assert '.claude/skills/harness/bin/test-metrics-client-render.py' in s" && python3 -c "import json;d=json.load(open('.harness/harness.json'));c=d['test_kinds']['component'];assert c['status']=='resolved',c;assert c['cmd'] and 'run test' in c['cmd'],c;assert '.test.tsx' in c['detect'],c"
bash: .claude/skills/harness/bin/run-unit-tests.sh: No such file or directory
exit 127
```

The exact signed command was cross-checked against `plan.yaml:396-397`. The task prohibits modifying the absent runner. The available runner is `.claude/skills/harness/bin/run-unit-tests.py`, but it was not substituted because the signed verify must be run verbatim.

## Files touched

- `.harness/harness.json`
- `.harness/harness/features/FEAT-53-metrics-dashboard/notes/receipt-harness-dev-ops-T-03-c0.md`

## Commit

`e2f996d0b3e9ab47fcda8f3d1cfed0e0d6a43c32` — `[harness:t-03] Resolve test kind configuration`
