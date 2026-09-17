# T-27 receipt

Implementation commit: `aa304968`.

Changed implementation files:
- `.claude/skills/harness/bin/dashboard/serve.py`
- `tests/integration/test-metrics-dashboard.py`

Fail-first evidence: before the server edit, `python3 tests/integration/test-metrics-dashboard.py` failed the new operational fixture case because `GET /api/work` returned HTTP 404 instead of 200. The same run also observed a concurrent frontend observation-log write changing the repository-status snapshot; it was unrelated to T-27.

Exact task verification:

```text
$ python3 tests/integration/test-metrics-dashboard.py
....full repository /api/kpis elapsed: 4.139s
..
----------------------------------------------------------------------
Ran 6 tests in 5.669s

OK
```

The integration fixture covers default and explicit window/repository API requests, live disk refresh, payload schema/order/null token and phase fields, no cost field, malformed-row errors, invalid configuration and configured-repository failures, GitHub-call isolation, and existing static routes. The retired `.claude/skills/harness/bin/test-metrics-dashboard.py` path was not recreated.
