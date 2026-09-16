# T-03 receipt — BLOCKED

T-03 cannot be completed against the signed/current inputs without an amendment: the checked-in matrix contains **34**, not the dispatched 36, `T-03` migrate/team rows, and one remaining row names an incompatible public interface.

## Accountability and completed work

- Exact row matrix: `tests/integration/canonical-reader-classification.json`, filtered by `task == "T-03"` (34 rows; all `disposition: migrate`, `execution_route: team`). This is the authoritative per-row pointer; its listed remedies were inspected. The dispatched/acceptance count of 36 has no matching current rows.
- The two `handoff_done_when` rows now use `artifact_accessors.load_plan` after the existing root-containment, regular-file, and size checks. Its fixtures are valid minimal plan documents; a new observable test proves an incomplete but pointer-shaped task is refused by schema validation.
- Predecessor fail-first is retained from `receipt-harness-backend-dev-T-03-final-c0.md`: `test-factory-config.py` rejected non-finite remote harness JSON before its text-source cutover. The prior handoff fail-first is superseded by signed BRIEF SC-03: partial plan fixtures were not a public contract.
- Semantic cutovers were advanced for lifecycle, claim, factory GitHub, and gh-sync rows; adapter migration retained PyYAML for its existing writer/error path and preserves its trailing body newline.

## Blocking facts

1. `harness_boundary.run_dir_grant_globs` must collect every generic team-config grant. The classified remedy `artifact_accessors.manifest_domains(manifest_path, agent)` only returns domains for one supplied agent, so it cannot preserve that all-role behavior without an adapter/new accessor (both prohibited).
2. Exact verification fails in `tests/integration/test-board-lifecycle.py` (13 assertions): strict `load_feature_json` refuses its intentionally partial feature fixtures and makes STATUS findings vacuous. The analogous signed resolution made for handoff fixtures is required here before changing these fixtures.

## Verification

- RED observed: `python3 tests/unit/test-handoff-done-when.py` failed `plan authority rejects schema-invalid plan` before the `load_plan` migration.
- Scoped GREEN: `python3 tests/unit/test-handoff-done-when.py` passed; `python3 tests/integration/test-sync-agent-adapters.py` passed (18/18).
- Exact T-03 `verify:` was discovered verbatim in `plan.yaml:274-275` and run verbatim. It failed only at the final `tests/integration/test-board-lifecycle.py` stage (13 failures above); earlier chained stages passed. There is no separately defined `task_verify` beyond this task `verify:`.

## Scope exclusions

No classification machinery, `test-check-plan-routes.py`, T-04 mechanical rows, T-05–T-07 enforcement, formatter, linter, build, broad suite, or commit was changed.

Files touched: `.claude/skills/harness/bin/{board_lifecycle.py,factory_claim.py,factory_gh.py,gh-sync.py,handoff_done_when.py,sync-agent-adapters.py}`, `tests/unit/test-handoff-done-when.py`, plus predecessor T-03 files already present in the worktree.
