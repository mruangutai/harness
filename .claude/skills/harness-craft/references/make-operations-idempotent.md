---
name: make-operations-idempotent
title: Make Operations Idempotent
description: "Apply when designing commands, lifecycle steps, or processing loops that run amid crashes, restarts, and retries. Converge to the same end state regardless of partial prior runs."
seats: [harness-backend-dev, harness-data-engineer, harness-dev-ops, harness-eng-lead]
---
# Make Operations Idempotent

Design operations so they converge to the correct state regardless of how many times they run or where they start from. Every state-mutating operation answers: "What happens if this runs twice? What happens if the previous run crashed halfway?"

**Why:** Commands, lifecycle operations, and processing loops run where crashes, restarts, and retries are normal. If partial state changes the next run's outcome, every restart becomes a debugging session.

**The pattern:**
- **Convergent startup:** scan for existing state, clean stale artifacts, adopt live sessions.
- **Content-based cleanup:** compare by content equivalence, not creation order.
- **Self-healing locks:** PID-based stale-lock detection, so a crashed holder never blocks the next run.
- **Idempotent scheduling:** failed work respawns cleanly; fresh input is regenerated after each cycle.

**The test:**
1. What happens if this runs twice in a row?
2. What happens if the previous run crashed at every possible point?
3. Does re-execution converge to the same end state?

If any answer is "it depends on what state was left behind," the operation needs a reconciliation step.

A lever that is safe to rerun is this principle applied to tooling (`references/build-the-lever.md`). Whether a write target should be shared at all is `references/separate-before-serializing-shared-state.md`.
