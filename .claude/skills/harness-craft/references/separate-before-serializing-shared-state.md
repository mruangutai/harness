---
name: separate-before-serializing-shared-state
title: Separate Before Serializing Shared State
description: "Apply when concurrent actors might write to the same file, branch, key, or state object. Eliminate the sharing first; serialize structurally only when one shared writer is a real invariant."
seats: [harness-backend-dev, harness-data-engineer, harness-dev-ops, harness-eng-lead]
---
# Separate Before Serializing Shared State

When concurrent actors might share mutable state, first ask whether they need the same mutable object. If not, eliminate the sharing. When sharing is real, enforce serialization structurally: lockfiles, sequential phases, exclusive ownership. Instructions and conventions are not concurrency control.

**Why:** Concurrent writes to shared state create race conditions that are intermittent, hard to reproduce, and expensive to debug.

**Pattern:**
1. **Identify shared mutable state:** files both read and write, branches both push to, APIs both define and consume.
2. **Default: eliminate the shared write target.** Do these actors need one canonical object, or are they publishing independent facts? Give each actor its own owned file, key, branch, or state directory, and merge only at the read/reporting boundary. Two workers writing their own `lastX` field into one `state.json` is still shared mutation; `indexer-state.json` plus `metrics-state.json` is not.
3. **Only when one shared write target is a real invariant, serialize access structurally:** lockfiles, sequential phases, a single-writer actor, or atomic compare-and-swap. Treat "we need a lock" as a design smell to check, not as the default answer.

**The sanctioned exception:** the harness observations log is one file every worker appends to, because a single ordered record *is* the invariant. `observations-merge.py` (`harness-expertise`) takes an exclusive lock, computes an order-preserving union, and writes it back atomically; workers go through it and never write the log directly. That is step 3 done structurally, after step 2 was honestly answered "yes, one object".

**The test:** Name the invariant that requires one write target. If you cannot, split the target. If you can, name the lock or phase boundary that enforces it; a comment saying "only X writes this" is not it.

The question to ask before sharing at all is in `references/foundational-thinking.md`; a shared writer that must survive crashes also needs `references/make-operations-idempotent.md`.
