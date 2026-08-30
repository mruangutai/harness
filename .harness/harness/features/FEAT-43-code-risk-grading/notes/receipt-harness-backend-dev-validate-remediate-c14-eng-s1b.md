# Receipt — harness-backend-dev — validate-remediate-c14-eng-s1b (CR-01 test over-specification)

**Task:** T-01 (send-back on `check_self_grading` in `.claude/skills/harness/bin/test-code-grade.py`,
lines 184-203 pre-edit). **Verify command (dispatch-declared override):**
`python3 .claude/skills/harness/bin/test-code-grade.py`, directly — not `run-unit-tests.sh` (dispatch
constraint overrides the plan's `--kind unit` verify for this remediation run).

## What changed

Rewrote `check_self_grading()` (now `test-code-grade.py:184-230`) to enumerate every function record
`code_grade.grade_source` reports in `code_grade.py`, `gate_policy.py`, and `check-plan-routes.py`,
asserting `grade >= 4` for each, except qualnames in a new `SELF_GRADING_ALLOWLIST` module constant
(`:189-206`). No `exists`-by-name assertion remains. The docstring now states exactly what is
verified.

## The allowlist discrepancy — verified, not trusted

The dispatch named three allowlist entries (all grade-2, reasons recorded in
`notes/review-harness-code-reviewer-validate-final-panel.md`'s SC-15 section) and explicitly told me
to verify the list by running the tool rather than trusting the dispatch. I did, and found **five
more** below-bar records the dispatch did not name: `check-plan-routes.py:parse_files` (2),
`process_task` (2), `process_plan_yaml` (1), `discover_plans` (1), `check_invariant_number_collisions`
(2). I confirmed by reading `git diff 7ccfae8..94383e6 -- check-plan-routes.py` that none of these
five had its grade moved by this feature: `discover_plans` and `check_invariant_number_collisions`
are untouched entirely; `parse_files`'s only apparent diff-hunk proximity is a git context-line
artifact (its body is untouched); `process_task` and `process_plan_yaml` had a parameter added
(`root`, `manifest_root`) with no new branching — D-02's own rule that a signature change without
branching cannot move a grade. None of the five generated a `REASON REQUIRED` line in the reviewer's
full-diff run (SC-15 lists exactly 15, none of these five among them), which is consistent: the real
`code-grade.py` gate only demands a reason for a *gated* (grade-moved) record, and D-01/D-02 never
gate an unchanged grade. All eight allowlist entries are included, each with an inline comment; the
five undocumented ones cite the git-diff evidence directly since no review-notes reason exists for
them (correctly — none was ever demanded).

This is a decide-and-record call, not a blocking question: reversible (test-shape), inside my
assigned item (correcting the test's honesty), and touches no production file. Recording it here per
the digest rule rather than opening a question, since the outcome (an honest, fully-enumerating test)
matches exactly what the dispatch asked for once verified.

## Mutation proofs

1. **Baseline green.** `python3 test-code-grade.py` → `PASS test-code-grade`, exit 0.
2. **Catches a new offender the old fixed-list check could not.** Appended a deliberate grade-3
   function `_temporary_offender` (nine-way `and`, cyc 9) to `gate_policy.py` (zero allowlist entries
   there, cleanest signal). Rerun: `FAIL gate_policy.py:_temporary_offender grade >= 4: expected
   True, got False`, `1 failures`, exit 1. Restored `gate_policy.py` via `cp` from a pre-mutation
   backup; `diff` confirmed byte-identical; rerun green, exit 0.
3. **Stale-allowlist assertion binds.** Added a bogus entry
   `("check-plan-routes.py", "_bogus_renamed_helper"): 2` to `SELF_GRADING_ALLOWLIST`. Rerun: `FAIL
   self-grading allowlist has no stale (renamed/removed) entries: expected {...,
   ('check-plan-routes.py', '_bogus_renamed_helper'), ...}, got {...without it...}`, exit 1. Removed
   the entry; re-`read` returned the identical snapshot tag as before the mutation (`#86FF`);
   rerun green, exit 0.
4. **Scope check.** `git status --porcelain -- .claude/skills/harness/bin/` after both restores shows
   only the six files already modified by wave 1/siblings (`check-plan-routes.py`, `code-grade.py`,
   `code_grade.py`, `gate_policy.py`, `test-code-grade-cli.py`, `test-code-grade.py`); `diff` of
   `gate_policy.py` against my pre-mutation backup confirmed byte-identical. I modified exactly
   `test-code-grade.py`.

## Result

`python3 .claude/skills/harness/bin/test-code-grade.py` → `PASS test-code-grade`, exit 0.
