# FEAT-69 — red-first receipts (SC-01, SC-02 fail-first)

Implementation pin: `db488aa7c78e392c788bd5839a43ebf4ba562ea1`. Baseline: `a726bad8f74d23e6c1f07409383bb88d1da8fbcf`. Both receipts below are copied verbatim from `notes/clean-pin-byte-receipts.generated.md`, which the one clean-pin execution wrote; this file and the receipt commit postdate the pin and are not inside it.

## SC-01 — the file-wide grade assertion is RED at the baseline and GREEN at the pin

`receipt-scripts/feat69-grade-assert.py`, run from each checkout root (`python3 <worktree>/.harness/harness/features/FEAT-69-long-file-check-state-package/notes/receipt-scripts/feat69-grade-assert.py` with cwd = the checkout):

Baseline checkout (`feat69-base-a726bad8`) → exit 1:
```
287 function(s) over 1 file(s): 5 -> 114, 4 -> 169, 3 -> 2, 2 -> 2, 1 -> 0
RED:
  package files present [] != expected ['__init__.py', 'board.py', 'brief.py', 'ctx.py', 'feature_record.py', 'host.py', 'plan.py', 'run_state.py', 'runner.py', 'seams.py', 'table.py', 'worktrees.py']
  below bar 4: [('.claude/skills/harness/bin/check-state.py', '_quoted_scalar_closed', 3), ('.claude/skills/harness/bin/check-state.py', '_unquoted_hash_digit', 2), ('.claude/skills/harness/bin/check-state.py', '_inv41_invocation', 2), ('.claude/skills/harness/bin/check-state.py', 'inv_49', 3)]
```

Pin checkout (`feat69-cleanpin-db488aa7`), with `FEAT69_BASELINE_JSON` pointing at the baseline execution's record → exit 0:
```
moved: 287 (grade kept or raised: 287); new: 8 -> [('_inv41_span_invokes', 4), ('_inv41_span_script', 4), ('_inv49_graded', 4), ('_inv49_hits', 4), ('_inv49_unnamed', 5), ('_quoted_escape', 4), ('_comment_hash_at', 5), ('_handoff_done_when', 5)]
295 function(s) over 13 file(s): 5 -> 119, 4 -> 176, 3 -> 0, 2 -> 0, 1 -> 0
GREEN: every function on check-state.py + check_state/** at grade >= 4; required functions present
```

Reading: the 287 baseline functions all reappear at the pin by qualname with their grade kept or raised (the four named functions rose from 2/2/3/3 to 4); the eight genuinely new functions (the seven grade-fix extractions and the lazy loader) are graded as new at 4 or 5, no exemption. `tests/unit/test-code-grade.py`'s self-grading exemptions were not touched: none of the four ever had one.

## SC-02 — fail-first is the baseline-versus-pin comparison itself

The pin side of the byte comparison cannot exist before the implementation, so the comparison is the fail-first form (BRIEF SC-02 `fail-first:`). Result: 12 of 13 measurements byte-identical after the one normalisation; the full-table run's five differing lines are ledgered with exact bytes and rulings in `notes/build-divergences.md` (D-02 the feature's own panel notes, D-03 the gitignored run directory; D-01, foreign worktree state, appeared only in a superseded first execution).
