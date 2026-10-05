# STATE

## Current

- feature: FEAT-1559-corpus-outside-worktree
- run: .harness/harness/features/FEAT-1559-corpus-outside-worktree/runs/plan-product/state.yaml
- squad: product
- status: blocked

## Open Questions

- Runtime: every governed child's structured `yield({data})` in this OMP session reaches `validate-digest.py --hook` with `digest_object` absent (pm, product-lead and the predecessor orchestrator all refused with "`data` was absent"); the on-disk `.omp/extensions/harness-hooks.ts:1296-1309` forwards it, so the loaded extension predates FEAT-1928. Main session: reload the extension (restart the OMP session) and re-delegate the orchestrator to resume run `plan-product` — the draft step is on disk; readers, apply and goalcheck are pending.
