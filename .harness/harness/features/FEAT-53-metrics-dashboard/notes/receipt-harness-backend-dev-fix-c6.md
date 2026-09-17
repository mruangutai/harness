# Receipt — harness-backend-dev — FEAT-53-metrics-dashboard — fix-c6

- First fixed tip: `e40dfd38c5a33431ea629525077ee36fe5a8cee1` (`fix: include weekly sourcing rule`).
- Loopback tip: `93785232ac32ae4fecc0a456d286e772ad15eb82` (`test: prove KPI sourcing rule payload`).
- Cumulative scoped files: `.claude/skills/harness/bin/dashboard/trend.py`, `tests/integration/test-metrics-trend.py`, `.claude/skills/harness/bin/dashboard/client/src/kpi-content.test.tsx`.
- Loopback commit pathspec: `.claude/skills/harness/bin/dashboard/client/src/kpi-content.test.tsx`.

## Payload-consumption mutation RED

The existing KPI 7 behavior test now supplies the distinct sentinel `KPI 7 test sentinel: weekly counts come from the supplied dashboard payload.`, opens the accessible `About Merged PRs Over Time` button, and observes the sentinel disclosure content.

For the proof, `tiles.tsx` was temporarily mutated to replace `weekly.sourcing_rule` with `'hard-coded fallback rule'`, then restored. Its SHA-256 before and after restoration was `a54245e3c1a71d64f881c38fa2ef8b2cc7de87e5496e1b382be6e778af7c8663`; it was absent from scoped status after restoration.

```sh
npm test -- src/kpi-content.test.tsx
```

Output (exit 1):

```text
FAIL  src/kpi-content.test.tsx > KpiTiles > renders the seven KPI links and keeps measured zero distinct from unavailable
TestingLibraryElementError: Unable to find an element with the text: KPI 7 test sentinel: weekly counts come from the supplied dashboard payload.
Test Files  1 failed (1)
```

## Post-fix scoped verification

```sh
npm test -- src/kpi-content.test.tsx
```

Output (exit 0):

```text
Test Files  1 passed (1)
     Tests  1 passed (1)
```

```sh
python3 tests/integration/test-metrics-trend.py
```

Output (exit 0):

```text
Ran 17 tests in 0.827s
OK
```
