# STATE

## Current

- feature: FEAT-2452-gh-one-transport
- run: .harness/harness/features/FEAT-2452-gh-one-transport/runs/r-20261123-4-amend-apply-product/state.yaml
- squad: product
- status: blocked

## Open Questions

- Dispatch of r-20261123-4-amend-apply-product (C1 DEC-138 amend apply, ruling at notes/answers-2026-11-23-signoff.md §2) is refused by the session's dispatch hook: it resolves <CP>/.agents/skills/harness/bin/digest-schemas, moved by #2459 (b788e9da) to .claude/skills/harness/schemas/digest/. Needs the omp harness extension reloaded (or the orchestrator re-spawned with resume) before the run can be dispatched. Run is registered and open; nothing else owed.
