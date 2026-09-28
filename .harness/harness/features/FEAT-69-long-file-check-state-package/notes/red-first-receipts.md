# FEAT-69 — red-first receipts (SC-01, SC-02 and SC-03 fail-first)

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

## SC-03 fail-first — the structural mutants are NOT discriminated by the pre-FEAT-69 lock, and are by the pin's

Pre-fix state, reproduced with `receipt-scripts/feat69-sc03-red.py db488aa7 a726bad8` (run from the worktree root, after the clean-pin checkouts exist): a scratch tree = the clean pin checkout (package, table, the pin's suites) with exactly one file replaced by the baseline's — `.claude/skills/harness/bin/check-plan-routes.py`, the lock as it stood before T-02. The pin's `tests/integration/test-check-plan-routes.py` is then run there.

```
scratch tree: /var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/feat69-sc03-h9v6tqf7/tree = pin db488aa7 with baseline a726bad8's check-plan-routes.py
command (cwd=/var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/feat69-sc03-h9v6tqf7/tree): /opt/homebrew/opt/python@3.14/bin/python3.14 tests/integration/test-check-plan-routes.py
exit status: 1
```

Twenty-five checks FAIL — every FEAT-62/63 mutant check and all six FEAT-69 mutant checks — because the old lock parses only `check-state.py`, which after the split holds no invariant, no table row and no helper: every mutant goes uncaught, which is the silent degradation the grilling named and option (a) exists to refuse. The FAIL lines, verbatim:

```
FAIL feat62_module_body_loop_mutant_fails_for_its_own_finding
FAIL feat62_module_body_conditional_mutant_fails_for_its_own_finding
FAIL feat62_module_body_try_mutant_fails_for_its_own_finding
FAIL feat62_module_body_read_mutant_fails_for_its_own_finding
FAIL feat62_reparse_mutant_fails_for_its_own_finding
FAIL feat62_reads_undeclared_file_mutant_fails
FAIL feat62_reads_undeclared_git_mutant_fails
FAIL feat62_reads_undeclared_gh_mutant_fails
FAIL feat62_reads_misdeclared_gh_board_resource_fails
FAIL feat62_reads_misdeclared_gh_endpoint_resource_fails
FAIL feat62_reads_misdeclared_git_op_resource_fails
FAIL feat62_reads_lock_follows_helpers
FAIL feat62_reads_unprefixed_declaration_fails
FAIL feat62_authority_missing_decision_fails
FAIL feat62_authority_struck_decision_fails
FAIL feat62_authority_striking_a_cited_decision_reddens_its_rows
FAIL feat63_reparse_load_feature_json_mutant_fails_for_its_own_finding
FAIL feat63_reparse_load_harness_json_mutant_fails_for_its_own_finding
FAIL feat69_module_body_rule_covers_a_package_file
FAIL feat69_reads_lock_follows_an_imported_helper_two_calls_deep
FAIL feat69_reads_lock_sees_a_spawn_two_helpers_deep_across_modules
FAIL feat69_reads_lock_walks_into_ctx_methods_from_a_family
FAIL feat69_row_defined_outside_its_family_fails
FAIL feat69_assignment_alias_is_not_a_definition
FAIL feat69_row_no_family_claims_fails
```

Post-fix: the same file at the pin (the new lock) — `python3 tests/integration/test-check-plan-routes.py` in the clean pin checkout — exit status 0, `ALL PASS`, recorded as the `feat62_findings` and `consolidation_findings` measurements in `clean-pin-byte-receipts.generated.md` and in both repository test kinds at the pin (exit 0). `case_feat69_package_lock`'s fifteen checks (`feat69_*`) are the discriminating cases: a clean package yields no finding; each mutant fails for its own named finding.
