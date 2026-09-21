# Brief: FEAT-62 — Check-state decomposition

## Problem

`.claude/skills/harness/bin/check-state.py` is a 3,019-line gate whose invariant bodies execute at module scope. The shape makes individual invariants hard to select, makes input dependencies implicit, and leaves no mechanical lock against new module-body execution, undeclared reads, or stale decision authority. Operators still need the current gate contract: every existing check-state integration suite must retain byte-identical stdout, stderr, and exit status unless a narrowly ruled loop-order divergence is proved red-first. The feature must make the checker selective and auditable without adding instruction weight or folding the deferred broad-exception cleanup into this wave.

## Done when — by perspective

**operator** — The default checker and all eight existing `tests/integration/test-check-state*.py` suites remain byte-identical except the loop-order changes for INV-3, INV-15, INV-26, and their BEGIN/END sub-blocks that are individually enumerated, ruled, and proved red-first in the build divergence ledger. `--list`, `--only INV-NN`, `--feature FEAT-N-*`, and loop-only `--changed` provide deterministic selective execution while CI, hooks, command entry, and pre-commit guidance continue to use the full checker. Successful structured plan and feature-record writes run the changed-state feedback loop without changing their durable-write or stdout-receipt contracts.

**code maintainer** — Each active invariant is a named function referenced once from an ordered `INVARIANTS` table with declared scope, reads, output contract, and decision authority; shared inputs are parsed once into runner context. Red-first consolidation tests reject executable invariant work at module scope, reads absent from an invariant's declaration, and `--changed` in workflow or hook invocations. Changed production functions meet code-grade 4 or 5 and changed tests meet grade 3 or better; the 47 `except Exception` handlers remain wave-3 work and are not broadened, narrowed, reworded, or behaviorally changed here.

**reader** — Every invariant row names a resolving, non-struck `DEC-NNN` entry from `DECISIONS-INDEX.md`, and a red-first authority audit rejects missing or struck references. Operator guidance distinguishes fast mid-edit feedback from the full pre-commit gate without changing `SKILL.md`, preload sets, or the standing `AGENTS.md` instruction. A bounded divergence ledger explains every allowed observable difference and proves all other suite receipts unchanged.

## Success criteria

- SC-01 (operator): Existing checker receipts stay byte-identical except ruled divergences. At the pinned review SHA, each of the eight `tests/integration/test-check-state*.py` suites compares exit status, stdout bytes, and stderr bytes with the planning baseline. Every difference is a red-first expectation for INV-3, INV-15, INV-26, or a named BEGIN/END sub-block and has a matching ruled entry in `.harness/harness/features/FEAT-62-check-state-decomposition/notes/build-divergences.md`; no unlisted difference passes. — verify: automated (test)

- SC-02 (operator): Ordered registry and all four verbs execute deterministically. Integration tests prove that no-argument execution preserves the full ordered contract, `--list` reports active and retired identities without running invariants, `--only` selects the named active invariant or resolves retired INV-9/INV-10 without reuse, `--feature` limits feature-scoped loops while repo-scoped rows run once, and combined execution selectors intersect. Invalid selectors retain command-line error semantics. — verify: automated (test)

- SC-03 (code maintainer): Module-body execution is mechanically locked. A red-first mutation test for `check-plan-routes.py --consolidation-audit` inserts module-scope invariant execution and proves the audit fails. The passing audit permits only the bootstrap prologue, declarations including `INVARIANTS` and the retired map, and the guarded main call. — verify: automated (test)

- SC-04 (code maintainer): Declared reads cover invariant inputs and drive changed selection. Red-first tests add a file/glob, git, and GitHub/board read absent from an invariant's `reads` tuple and prove the consolidation audit rejects each omission. Integration tests prove `--changed` maps dirty and untracked repository paths to matching `path:` declarations, conservatively includes unmappable external/dynamic inputs, and preserves registry order. — verify: automated (test)

- SC-05 (reader): Every authority reference resolves to current, non-struck truth. Red-first tests replace invariant authority with a missing decision and a `STRUCK` decision and prove `check-plan-routes.py --consolidation-audit` rejects both against the current `DECISIONS-INDEX.md`; the unchanged tree passes with every active row naming an exact live `DEC-NNN`. — verify: automated (test)

- SC-06 (operator): Changed mode remains loop-only. An audit scans repository workflows and hooks and fails when a fixture adds `--changed` to either. At the pinned review SHA no workflow or hook passes it, `.github/workflows/tests.yml` still runs the full checker, and the command-entry and pre-commit paths remain full-check paths. — verify: automated (test)

- SC-07 (operator): Canonical writers surface selective feedback without changing receipts. Red-first integration tests prove that successful persisted writes through `plan-merge.py` and `feature_json_write.py#write_feature_json` invoke the shared changed-state runner after the lock is released, forward non-clean checker rows to stderr, and preserve existing stdout receipts, refusal behavior, durable content, and exit status. A clean `--changed` run is silent at the checker source, so the adapter performs no exact-string filtering. Non-canonical fixture paths derive no unrelated checkout, and the adapter neither calls nor changes the environment-reading `resolve_root` contract. — verify: automated (test)

- SC-08 (reader): Guidance changes add no instruction or preload weight. At the pinned review SHA, the reviewer cites `.harness/README.md` text that distinguishes automatic mid-edit `--changed` feedback from the required full pre-commit check, cites the unchanged full-check instruction in `AGENTS.md`, and confirms the feature diff contains no `SKILL.md`, preload-set, workflow invocation, or hook invocation change. — verify: inspection

- SC-09 (code maintainer): Decomposition stays one-function-per-invariant and leaves wave 3 untouched. At the pinned review SHA, the reviewer cites the ordered `INVARIANTS` table and representative invariant functions showing one row per active INV number and runner-owned shared context, the terminal baseline-to-HEAD code-grade receipt showing production grade 4/5 and test grade 3+, and a handler-scoped diff review showing that all 47 `except Exception` sites remain wave-3 work with no change apart from extraction indentation. No package split, broad-exception cleanup, or report-format change is present. — verify: inspection

## Verification gaps

- none

## Constraints

- Keep the checker as one file with the bootstrap prologue required by existing path consumers.
- Treat FEAT-61 control-plane consolidation as precedent for both `notes/build-divergences.md` and `check-plan-routes.py --consolidation-audit`.
- Preserve default output byte-for-byte across all eight existing check-state integration suites except the enumerated, ruled, red-first loop-order divergences.
- Make module-body lock, reads lock, and live-authority audit independently mutation-tested red-first.
- Keep `--changed` advisory and loop-only; workflows, hooks, command entry, and pre-commit remain full checks.
- Do not edit `SKILL.md`, preload sets, or the standing full-check instruction in `AGENTS.md`.
- Do not change any `except Exception` site's caught type, body, message, fallback, or behavior; broad-exception cleanup remains wave 3.
- Execute every implementation task in the main session under the settled direct-route exception.

## Out of scope

- Changing the checker report format beyond the ruled loop-order divergences.
- Splitting `check-state.py` into a package or additional invariant modules.
- Performance optimization unrelated to parsing shared inputs once.
- Repairing the 13 pre-existing state violations.
- Removing or narrowing broad exception handlers.
- Adding retries, telemetry, validation layers, new preload text, or `SKILL.md` guidance.

## Approval

status: approved
approved-by: Mike (main session)
date: 2026-09-21
