# T-03 receipt — BLOCKED

The semantic migration cannot preserve `handoff_done_when`'s public partial-plan contract through the required `artifact_accessors.load_plan` seam.

- Predicate: classification has 36 `task: T-03`, `disposition: migrate`, `execution_route: team` rows; all 19 listed source paths and 20 listed test paths exist. The classification remedies cover the named canonical accessors.
- RED: `python3 tests/unit/test-factory-config.py` failed only `product_config rejects non-finite remote harness.json through the strict accessor` before the product-config cutover (`did not raise`).
- GREEN scoped evidence: after `load_harness_json(text=..., context=...)` cutover, `python3 tests/unit/test-factory-config.py && python3 tests/integration/test-worktree-terminal.py && python3 tests/integration/test-merge-settings.py` passed.
- Exact verify attempted: `python3 tests/unit/test-factory-gh.py && python3 tests/unit/test-handoff-done-when.py && python3 tests/integration/test-merge-settings.py && python3 tests/integration/test-sync-agent-adapters.py && python3 tests/integration/test-worktree-terminal.py && python3 tests/integration/test-gh-sync-record.py && python3 tests/integration/test-board-lifecycle.py`.
- Fail-first: `tests/unit/test-handoff-done-when.py` failed after the required `load_plan` migration because its public fixtures intentionally contain partial task mappings; `load_plan` raises `PlanSchemaError` for missing `title`, `change_type`, `execution_mode`, `files`, and `intent`. Restored the original reader pending a signed resolution, because changing this contract conflicts with T-03's preservation requirement.
- Task verify: no separately defined T-03 task_verify exists in plan.yaml.
- Exclusions: no classification machinery or T-04 rows were intentionally changed.
- Files touched: source and test changes listed in the worktree status; the handoff migration was reverted after the fail-first evidence.
