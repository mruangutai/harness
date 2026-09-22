# Research — FEAT-62 check-state decomposition

## Grounding

- Planning baseline: `1b69f67f4a24c4b011cd1fa724e1bb66d4c77cb7`.
- Grilling source: `.harness/notes/grilling-check-state-decomposition-2026-09-21.md` in the control plane.
- `.claude/skills/harness/bin/check-state.py` is 3,019 lines and presently mixes bootstrap, helpers, invariant execution, and rendering at module scope.
- Eight integration suites define the current observable contract: `test-check-state.py`, `test-check-state-entry.py`, `test-check-state-plans.py`, `test-check-state-handoff.py`, `test-check-state-worktrees.py`, `test-check-state-inv26.py`, `test-check-state-records.py`, and `test-check-state-feat59.py`.
- `plan-merge.py` is the sole `plan.yaml` write seam. `feature_json_write.py#write_feature_json` is the shared `feature.json` write seam used by feature-record, feature-json-merge, gh-sync, and factory decomposition.
- `.github/workflows/tests.yml` runs the full checker. `AGENTS.md` requires the canonical checker before commit. Neither workflows nor hooks currently pass `--changed`.
- FEAT-61 established the ruled divergence ledger and the `check-plan-routes.py --consolidation-audit` pattern.

## Resolved design details

- Keep one checker file. Its post-bootstrap body is declarations, an ordered `INVARIANTS` table, and the guarded main call; invariant execution leaves module scope.
- Each active invariant has one `Inv(name, run, scope, reads, contract, authority)` row. INV-9 and INV-10 remain in a retired-name map and are never reused.
- `reads` uses auditable literals: `path:<repo-relative POSIX path-or-glob>`, `git:<operation>`, and `gh:<resource>`. Static audit maps direct reads/globs/accessors/subprocess calls to those entries.
- `--changed` derives the dirty/untracked path set from porcelain-v1 `-z` status, selects intersecting `path:` declarations, and conservatively retains rows whose external or dynamic inputs cannot be mapped to a changed path.
- `--feature` limits feature-scoped iterations to the named feature while repo-scoped rows run once. Execution selectors intersect; `--list` is non-executing and exclusive.
- Only the loop movement for INV-3, INV-15, INV-26, and their BEGIN/END sub-blocks may change ordering. Each permitted change must be enumerated, ruled, and demonstrated red-first in `notes/build-divergences.md`; everything else remains byte-identical suite by suite.
- Authority values are exact `DEC-NNN` references. The audit rejects references missing from `DECISIONS-INDEX.md` and entries marked `STRUCK`.
- The two writer choke points invoke an advisory changed-state loop after a successful persisted write and after releasing the write lock. Findings go to stderr; writer stdout receipts and write outcomes remain unchanged. Full checks remain the CI, command-entry, and pre-commit gates.
- No complexity exemption is planned: changed production functions must grade 4 or 5 and changed tests at least 3. The 47 broad exception handlers are wave-3 scope and must remain structurally and textually unchanged apart from extraction indentation.

## Planning consequences

- Build order is checker/contract first, consolidation locks second, writer loop and operator guidance last.
- The locks need red-first mutation tests for module-body execution, undeclared reads, invalid/struck authority, and workflow/hook use of `--changed`.
- No `SKILL.md`, preload set, AGENTS instruction, workflow invocation, hook invocation, report format, package split, performance work, or broad-exception cleanup belongs in this feature.
