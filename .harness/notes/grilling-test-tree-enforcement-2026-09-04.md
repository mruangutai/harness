# Grilling — repository-wide Harness test-tree enforcement — 2026-09-04

## Destination
Issue #1286 reaches an approved BRIEF and plan that make every tracked Harness test-shaped file obey the `tests/**` tree without changing product-checkout discovery or beginning implementation.

## Settled
- Should the four unresolved boundary questions block implementation? → Yes. The product team must resolve the authoritative test-shaped vocabulary, the exception contract, tracked-file authority and failure semantics, and the DEC-213 amendment during briefing and planning.
- What outcomes are binding? → The acceptance criteria recorded in issue #1286 are the planning floor, including deterministic complete reporting, pre-dispatch refusal, fail-closed tracked-file enumeration, valid unit/integration/manual behavior, explicit exception discipline, a `review_sha` audit, governing-decision consistency, and unchanged product-checkout discovery/runtime mutation scope.
- Should planning decide the FEAT-44 probe classification rather than implementation improvising it? → Yes. The plan must classify `.harness/harness/features/FEAT-44-omp-context-advisory/evidence/probe-session-accessors.ts`, which is consumed by the manual probe.

## Not yet specified
- None. The four sharp questions are assigned to the product team as part of this planning run.

## Out of scope
- Redesigning product-checkout test discovery.
- Broadening runtime mutation snapshots.
- Renaming non-test support modules solely because tests import them.
- Implementing the guard during this planning run.

## Facts I verified (so pm does not re-derive them)
- `suite_layout.violations()` currently scans Python test shapes under `tests/**` and a different shape set only under `.claude/skills/harness/bin/` — `.claude/skills/harness/bin/suite_layout.py:20-33` at `1977ebd68d34cc0308968b03ad2d24399c0b5335`.
- DEC-213 currently describes the layout predicate as refusing test-shaped files left under `bin/`, not across the repository — `.harness/harness/docs/DECISIONS.md:6674-6678` at the same revision.
- A Git-index census at that revision found 2,670 tracked paths; the broad existing-shape union matched 85 paths, 76 under `tests/**` and 9 outside. Eight outside matches were Markdown/JSONL evidence names and one was the FEAT-44 TypeScript probe dependency.
- `tests/manual/probe-omp-session-accessor.py:54-55` resolves the FEAT-44 TypeScript probe by its current evidence path.
