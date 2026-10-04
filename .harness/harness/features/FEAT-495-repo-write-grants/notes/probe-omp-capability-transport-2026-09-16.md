# OMP capability transport probe — 2026-09-16

## Result

Command:

```text
python3 tests/manual/probe-omp-session-accessor.py
```

OMP version: `18.2.1`.

```text
PASS - OMP binary is on PATH
PASS - live OMP capability transport exits zero
PASS - child receives trusted replacement and acknowledges it
PASS - raw capability is absent from stdout and stderr
FAIL - raw capability is absent from persisted session logs
FAIL - 4/5 checks passed
```

The generated capability value is deliberately omitted from this note. The probe removed its temporary extension and session directory on exit.

## Finding

A parent `tool_call` interception can replace a `task` input and the child receives that replacement without a child extension callback or `ctx.agentId`. However, OMP persists the revised input. The current OMP extension contract states that a `tool_call` input revision is revalidated and becomes the persisted assistant tool call, while the task runtime also writes a child JSONL session artifact containing the assignment.

Consequently, putting the raw bearer in `HARNESS-CAPABILITY:` cannot satisfy the signed non-persistence requirement. This is not repairable by redacting stdout, stderr, claim receipts, or Harness diagnostics: persistence happens inside OMP before the child runs. The child also does not load the project extension, so Harness has no private child callback through which to deliver the bearer instead.

## Required prerequisite

T-02 needs an OMP host seam that carries per-spawn private metadata from the parent task interception to the child enforcement context without including it in tool arguments, provider context, task results, or session artifacts. Until that exists, the approved design's child-visible raw bearer and raw-token non-persistence requirements are mutually incompatible.

The 2026-09-15 probe note remains unchanged as historical evidence that task-input replacement reaches the child; this note adds the persistence result that the earlier probe did not test.
