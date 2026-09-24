# OMP session accessor probe — 2026-09-15

## Obsolete FEAT-44 premise

Command:

```text
python3 tests/manual/probe-omp-session-accessor.py
```

The former probe failed because both observed sessions now reported `getContextUsage` defined;
its expectation that a child would report it undefined is obsolete.

## Revised identity probe

The replacement manual probe generates a temporary extension that records `ctx.agentId` at
`before_agent_start` and at every tool interception while a live `sonic` child is instructed to
use Write, Edit, and Bash.

```text
PASS - OMP binary is on PATH
PASS - probe produced observations
FAIL - child start has a non-empty ctx.agentId ([])
FAIL - write interception has a non-empty ctx.agentId ({'task': ''})
FAIL - edit interception has a non-empty ctx.agentId ({'task': ''})
FAIL - bash interception has a non-empty ctx.agentId ({'task': ''})
PASS - tool identities are stable child identities
FAIL - 3/7 checks passed
```

Only the parent `task` interception was observed, with an empty `ctx.agentId`; the child did not
load the extension. This falsifies the required pre-write identity assumption. T-02 remains
blocked until OMP provides a child-visible extension event or an equivalent documented runtime
identity transport.

## Discovered-extension retry

The probe was then changed to place the temporary extension at
`.omp/extensions/identity-probe.ts` in its temporary project and run without `-e` or
`--no-extensions`. Its output was identical: the parent interception loaded the extension, but
no child lifecycle or tool event reached it. This rules out explicit-extension loading as the
sole cause; OMP v18.2.1 does not deliver the project extension to this spawned child.

## Capability-token transport probe

A throwaway parent extension intercepted `task`, returned a revised task input with
`CAPABILITY: capability-probe-7f3d`, and ran with explicit `-e` plus
`--no-extensions --no-skills --no-rules`. The live child replied with the exact value:

```text
The subagent replied with CAPABILITY value: capability-probe-7f3d.
```

OMP therefore preserves parent-hook input replacement into a child task even though it does not
deliver the extension to that child. A trusted, per-dispatch opaque capability token is a viable
identity transport; it must still be validated against the live registry claim before any write.
