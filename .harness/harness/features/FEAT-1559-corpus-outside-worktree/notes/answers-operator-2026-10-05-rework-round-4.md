# Operator ruling, 2026-10-05: one more fix round (round 4)

**Asked:** validate c4 (run validate-c3-validator) at 35587d8d confirmed all seven round-3 fixes. It returned FAIL on one medium T-01/SC-01 must-fix: `worktree-state.py` writes cone names raw to `git sparse-checkout set --stdin`. For a top-level directory whose name begins with a literal `"`, git reads that quote as the start of a C-quoted name, so repair exits 128 and the cone never converges. The failure is fail-closed and nothing is deleted. The 3-round rework budget is spent.

**Ruling (mruangutai):** "Yes, round 4." Raise rework to 4 rounds and 240 min. Quote every name written to `--stdin`, add a regression test, then re-validate.
