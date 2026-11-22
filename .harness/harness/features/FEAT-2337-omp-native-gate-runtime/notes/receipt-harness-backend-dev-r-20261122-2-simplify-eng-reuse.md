# Receipt — simplify · reuse — FEAT-2337 (plan surface, flag-only)

BLUF: 3 low findings, no blockers. Plan already reuses check-integration-shards discover_expected/evidence_defects, registered_destination, registered_feature, gated_set. Gaps are unnamed reuse targets that invite a second spelling.

## Findings

1. T-03 · plan.yaml:477-488 (cumulative self-grading) — bar derivation
   - Existing: `code_grade.classify` (code_grade.py:498) and `_classify_record` (:487) already compute bar 3/4 via `_is_test_path`, severity and PASS/FAIL for `gated_set()` output. `test-code-grade.py:268` also spells `3 if _is_test_path(...) else 4` in `_check_self_graded_file`, and `:292-293` re-reads harness.json `test_kinds`.
   - Cost: the task says "gated_set/grade_source and configured test kinds" without naming classify. A third copy of the bar rule would need lockstep edits with code_grade.py and the legacy check.
   - Alternative: name `code_grade.classify(gated + informational, test_kinds)` as the grader, and share the existing test_kinds load in test-code-grade.py instead of re-reading harness.json.

2. T-02 · plan.yaml:359-375 — revision resolution for review_sha/tested_commit
   - Existing: `code_grade.commit_oid` (code_grade.py:290), wrapped as `validate-digest.resolve_reviewed_commit` (validate-digest.py:237), which refuses option-like revisions before invoking git; `reviewed_python_change` (:250) is the in-tree NUL-safe `git diff --name-only -z` precedent.
   - Cost: the intent specifies ancestry plus NUL-safe paths but does not name the resolver. A hand-rolled `rev-parse` would drop the option-injection refusal on a digest-supplied value.
   - Alternative: name `resolve_reviewed_commit`/`commit_oid` as the resolver. No existing ledger-only/intervening-commit walker exists (grepped bin/), so that part is genuinely new.

3. T-02 · plan.yaml:405-412 — committed-git fixtures and the argv shim
   - Existing: real committed-repo helpers `repository()` (test-integration-shard-aggregation.py:54), `_commit` (test-validate-digest-shadows.py:43), `make_repo` (test-code-grade-cli.py:48), and an argv-recording stub (test-validate-digest.py:1786-1793, `_bug1756_argv` :1879). Separately, test-run-unit-tests-shards.py already drives the real runner with `--shard`.
   - Cost: the plan lists `repository` as a file anchor but never says the new `run_feat2337_qa_receipt_cases` reuses it. About 10 `_git` copies already exist, and the new table-driven cases add another unless pointed at one. The "trivial PATH/argv shim" duplicates the argv-recording stub that this same task deletes.
   - Alternative: say the new fixtures build on `repository()` plus the runner's real `--kind --shard 1/1 --manifest` output, and that the shim is the existing stub's argv-append line moved to PATH.

Not flagged (settled or verified fine): HOOK_HANG_BUDGET_S not shared (test-validate-digest.py:1030 is a test constant, BRIEF says no shared import); async/30s/parallel/receipt-only/DEC-174 settled; T-03 grade `--feat2337` mode alongside existing `check_self_grading` is a separate gate by design.
