# SIMPLIFY REUSE receipt — FEAT-54 c3 repairs

## BLUF

PASS with no REUSE findings. The c3 repairs preserve one authoritative Done-when parser/resolver in `.claude/skills/harness/bin/handoff_done_when.py`; neither gate nor the scoped tests add a competing parser, resolver, containment helper, or heading recognizer. Every candidate in this read-only pass is advisory-only, and none warrants an advisory finding.

## Shared mechanism

- `.claude/skills/harness/bin/handoff_done_when.py:24-35,272-288` owns section recognition, body extraction, and the public `problems(...)` orchestration.
- `.claude/skills/harness/bin/handoff_done_when.py:57-101,143-184,241-267` owns pointer-path safety, root containment and bounded regular-file reads, strict ATX Approval-heading recognition, resolver dispatch, and fail-closed resolution.
- `.claude/skills/harness/bin/check-domain.sh:1561-1566` imports that module and calls `problems(..., resolve=True)` rather than restating it.
- `.claude/skills/harness/bin/check-state.sh:53-56,1243-1251` imports the same module and calls `problems(..., resolve=False)` rather than restating it.
- `tests/unit/test-handoff-done-when.py:7-10,38-43` imports and exercises the authoritative module. The integration fixtures in `tests/integration/test-check-domain.py:4002-4134` and `tests/integration/test-check-state.py:2093-2258` cross the real gate interfaces; their repeated pointer strings and expected prefix tuple are independent test oracles, not alternate parsing implementations. Replacing those expectations with production constants would make the tests self-referential.

## Advisory findings

None. No scoped c3 constant, helper, fixture, parser, or digest convention reimplements an importable existing definition. The unit/write/state fixture overlap is intentionally layer-specific and independently falsifies the prohibited nested/duplicate-heading, invalid-ATX, and unsafe-pointer behaviors while retaining positive controls; consolidating it into production or a shared cross-layer oracle would weaken that independence. The five representation-only digests listed at `.harness/harness/features/FEAT-54-handoff-done-when/notes/qa-validation-c3.md:36-44` contain contract-shaped evidence only and introduce no executable helper or competing convention.

## Disposition

All candidates were advisory-only because this dispatch permits no apply. Findings: zero. Source changes: zero. Test changes: zero. Digest changes: zero. Only this receipt was written. No command, test, formatter, linter, suite, or validation was run, as required.
