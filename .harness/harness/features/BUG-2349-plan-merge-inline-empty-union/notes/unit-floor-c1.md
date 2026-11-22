# Unit floor — BUG-2349 rework round 1 (main-session-direct) — 2026-11-22

## Why

Validate run `2026-11-22-02-validate-validator` returned ESCALATE at pin 2a476ca0: QA required the `bugfix` matrix's `unit` kind (`touches_runtime_code`), and the regression lived only in the integration suite, outside the signed two-file scope (Q-unit-floor). The operator delegated the call to fable-advisor, which ruled **option A**: add one unit test file through a signed `files`/`verify` amendment to T-01. Precedent: BUG-2253's unit-floor resolution.

Advisor conditions, all applied:
1. Exactly one new file, `tests/unit/test-plan-merge-union-head.py`; no production change.
2. The red run is bound to commit e239d881's `union.py` (loaded from `git show`), not to a worktree state.
3. Only the fixed rule is bound: an inline-empty base plus an item-adding proposal takes the proposal head; a base with items keeps its own head. The dismissed neighbor variants are not added.
4. **No integration-as-unit waiver was granted.** Nothing should cite this run as one. The systemic plan-time fix stays in #2293.
5. The post-merge SC-04 scratch receipt remains the main session's ship obligation.

## Amendments (ledgered as `amendment` judgements by `plan-merge.py amend`)

- `T-01.files` gains `tests/unit/test-plan-merge-union-head.py`.
- `T-01.verify` also runs `env -u HARNESS_AGENT_TYPE python3 tests/unit/test-plan-merge-union-head.py` after the integration suite.

## Red

`PLAN_MERGE_UNION=<git show e239d881:.claude/skills/harness/bin/plan_merge/union.py> python3 tests/unit/test-plan-merge-union-head.py` → rc 1. Six FAILs, both inline-empty keys × {merge without refusal, block head, reload}, each a `MergeRefusal(5) UNPARSEABLE` or the resulting `None`. The base-with-items control passes 3/3 on the base, as designed.
Receipt: `receipts/unit-red-base.txt` (records the loaded `union.py` sha256).

## Green

The amended T-01 `verify`, literal, with `BUG2349_TOOL_ROOT` = this worktree → rc 0: `PASS test-plan-merge.py`, `PASS test-plan-merge-union-head.py` (9/9), and `BUG-2349 scratch round-trip PASS`. Receipt: `receipts/c1-verify-green-prefix.txt`.
