# Receipt — tests-simplification (BUG-1016 T-01, read-only angle)

BLUF: findings [] — no test-reader-load simplification survives the settled set and the deletion test.

Read: `angle-simplification.md`, `delete-first.md`, `git diff 8d79d63d..89b7d960 -- tests/unit/omp-hooks.test.ts` (281+/4-), `t01-receipts-main-session.md`. Nothing run (verify `python3 tests/unit/test-omp-hooks.py` referenced only).

## Candidates considered and dropped

- `rootedHooks` / `fixture({featureRoot})`: one real seam (the runner double) with 17 callers; deleting it re-spreads ~15 lines of registration and lookup plumbing across every case. Earns its keep.
- `extractEditPaths(cleanExpected)` plus the literal list (edit-sections test, ~L1385): looks doubled, but the first pins pre/post-matcher agreement (settled: shared matcher) and the second pins literals (settled). Merging would weaken an assertion.
- `sibling runs resolve their own worktrees`: overlaps the cache test in shape, but is the only case that fails on a module-level cache shared across `registerHarnessHooks` calls. Keep.
- `ast_grep` in the list-entry case and the first case: different property (per-entry judging vs. field retention). Not duplicate.
- Header comments mention the original defect once (the block header) — that is intent for the group, rest states present facts. Not worth an edit.
- Unused `args` parameter in `(args) => (failing ? answer() : worktreeAnswer())`: cosmetic, zero reader cost beyond one token; not a finding.

No assertion weakened or removed; no named BUG-1016 test behaviour changes.

```yaml
findings: []
```
