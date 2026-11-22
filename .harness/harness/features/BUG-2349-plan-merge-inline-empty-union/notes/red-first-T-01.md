# Red first — BUG-2349 T-01 (main-session-direct) — 2026-11-22

## Tests first

Added to `tests/integration/test-plan-merge.py` and registered in `CASES`:

- `case_2349_inline_empty_decisions_gains_items` (SC-01): base `decisions: []` plus a proposal adding D-01 → exit 0; the reloaded plan carries `[{id: D-01, choice: Adopt x}]` and tasks T-01..T-02 untouched.
- `case_2349_inline_empty_tasks_gains_items` (SC-01): base `tasks: []` plus a proposal adding T-01 → exit 0; the reloaded plan carries T-01 with all of its fields.
- `case_2349_nonempty_flow_base_still_refused` (SC-02): base `decisions: [{id: D-01, choice: a}]` plus D-02 → exit 5 with "not one dash per item", and the base is byte identical.

## Red

`union.py` identical to the base, e239d881 (`git diff --quiet e239d881 -- …/plan_merge/union.py` → equal); new tests in the worktree at HEAD 71f9aa45.
`env -u HARNESS_AGENT_TYPE python3 tests/integration/test-plan-merge.py` → rc 1: **680 PASS / 4 FAIL**. The four failures are exactly the SC-01 checks: both inline-empty applies exit 5 `UNPARSEABLE … this is a splice defect`, and both reload checks find the base unchanged. They are assertion failures, not load errors. The SC-02 control passes on the base, as designed: the refusal already exists and must survive the fix.
Receipt: `receipts/sc01-sc02-red.txt`.

## Fix

`plan_merge/union.py` `_union_key_head`: the base head is used unless the base list has no items and the proposal adds some. In that case the proposal's head is used. Base-first precedence, proposal fallback and the absent-key `None` are otherwise unchanged; `_aligned_items` and `_merge_union_key` are untouched.

## Green

T-01's literal `verify` block, run with `BUG2349_TOOL_ROOT` = this worktree (fix in the working tree on top of 71f9aa45) → rc 0. Suite **684 PASS / 0 FAIL** (`PASS test-plan-merge.py`); the scratch repo apply printed `APPLIED …/FEAT-9-x/plan.yaml` and `BUG-2349 scratch round-trip PASS: {'decisions': [{'id': 'D-01', 'choice': 'x'}]}`.
Receipt: `receipts/sc01-sc02-sc04-green-prefix.txt`. This is SC-04's pre-merge receipt; the post-merge receipt against the merged main checkout follows at ship.
