# OMP session accessor probe — 2026-09-02

Run from the main user session after relocating the probe to `tests/manual/probe-omp-session-accessor.py`:

```text
PASS installed OMP binary
PASS committed extension exists
PASS session observations
FAIL case3: getContextUsage undefined in sessions ['3bkm', 'ui34']
3/4 checks passed
```

The run proves the relocated probe resolves and executes from its new path. The failing check is external OMP accessor-version drift, outside FEAT-47's layout contract. Follow-up: issue #1248 (`FEAT-44: pin or detect OMP session accessor compatibility`).
