---
name: migrate-callers-then-delete
title: Migrate Callers, Then Delete Legacy APIs
description: "Apply when introducing a new internal API while old callers still exist. Migrate the callers and delete the old API in the same wave instead of preserving compatibility layers."
seats: [dev, code-reviewer]
---
# Migrate Callers, Then Delete Legacy APIs

When a new API is the right design, migrate callers and remove the old API in the same refactor wave instead of preserving compatibility layers.

**Why:** Keeping both old and new APIs creates dual-path complexity, slows cleanup, and makes the codebase feel append-only.

**Rule:**
- Do not keep legacy API paths only because internal callers still exist.
- Inventory callers, migrate them, and delete the old API immediately. The inventory is a rerunnable search, not a memory (`references/build-the-lever.md`).
- Treat temporary adapters as exceptional and time-boxed, not default architecture.
- Update tests to assert the new contract, and delete tests that only protect pre-refactor implementation details.

**When this applies:**
- No external users depend on backward compatibility.
- The project can absorb coordinated breaking changes.
- The new API is part of a simplification or refactor initiative.

**The test:** A diff that adds an API without deleting the one it replaces, or leaves a shim, alias, or re-export "for now", has not finished the wave. The reviewer asks for the deletion, or for the time-box written down.

The plan-scale version is `references/outcome-oriented-execution.md`; the instinct is `references/delete-first.md`.
