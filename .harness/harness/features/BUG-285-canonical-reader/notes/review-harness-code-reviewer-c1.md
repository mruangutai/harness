# Code review — BUG-285-canonical-reader — c1

**PASS.** The exact range `8c3143bd5668ce11186a2a1f8dbe784ff9639d88..5be21a432b87ed648c0bed50fbf9a2642c84e0a9` passes both review stages. The final concrete tip is `5be21a432b87ed648c0bed50fbf9a2642c84e0a9`; this fix-team review intentionally does not require the lagging `feature.json` pin to change.

## Stage 1 — spec compliance: PASS

All four original findings are resolved, with no regression or new scope violation.

1. **F-01 — resolved (rank 1, high/substance, T-01, `.claude/skills/harness/bin/check-plan-routes.py:1285-1333`).** `_candidate_is_accounted` now accepts a candidate only by checked-in row identity, exact canonical remedy, or exact T-07 relocated implementation tuple; file identity no longer exempts `artifact_accessors.py`. The adjacent mutant at `tests/integration/test-check-plan-routes.py:2174-2202` supplies an unclassified `json.load` in that exact module and requires its category, remedy, and `PLAN AMENDMENT REQUIRED`. The focused self-test passed at the final tip, including this mutant and a zero-result live audit over all 69 classified Python files. The direct receipt records a genuine pre-fix red run and post-fix green run.
2. **F-02 — resolved (rank 2, high/substance, T-02, `tests/unit/test-feature-json-reader.py:126-155`).** The test uses the exact issue-285 inverse: a `feature.json` byte document with YAML mappings and three trailing comments. Its presence assertion proves public `harness_yaml.load_file(path)` returns the complete expected nested mapping; its inverse assertion proves public `artifact_accessors.load_feature_json(path)` raises `FeatureJsonError`. Thus the comment-bearing inverse is bound through public observable behavior, not source inspection or a mock. The 22-case reader suite passed at the final tip; the backend receipt records the historical permissive reader returning that exact mapping.
3. **F-03 — resolved (rank 3, high/substance, T-03/T-04, `tests/integration/test-check-plan-routes.py:2082-2118`).** I replayed the current `case_canonical_reader_live_baseline` assertion against genuine pre-cutover commit `5369a9ba8326fb95a74ee32b3468cb1268b960f4` and its then-live compatible checker/classification. It failed specifically at `canonical_reader_live_audit_is_zero` with 116 unresolved dispatchable readers and exit 2, while classification consistency and converted-entrypoint discovery passed. Against the final tip, the same live assertion passed with zero unresolved readers, followed by every T-03 through T-07 postcondition. This directly discriminates the current cutover assertion from the pre-cutover implementation.
4. **F-04 — resolved (rank 4, high/substance, T-05/T-06/T-07, direct receipt `notes/receipt-main-session-fix-c1.md`).** The receipt identifies the unmodified historical comparator and 29-case baseline by SHA-256, measures exact comparison success against strict-accounting commit `0ad0d0b8`, and measures exit 1 plus the named stdout mismatch after a deliberate off-tree divergence. Current-tree inspection confirms the temporary baseline file is absent and the retired mode is absent from shipped test code. The final-tip canonical self-test remains green.

**SC-06 inspection:** D-04 and the signed T-03/T-04 task split keep semantic bypass cutovers distinct from mechanical correct-reader relocations; commits `b19a2f38` and `75fd8bd4` preserve that review separation. **SEC-01 remains assessed-and-dismissed:** SC-03/T-02 require refusal of wrong-typed present parent/issues fields, not rejection of every non-mapping top-level `github`/`factory` block; expanding that contract would be scope creep.

## Stage 2 — code quality: PASS

The corrected accounting path fails closed: an unknown candidate produces an unresolved diagnostic rather than inheriting validity from its file, and exact relocated matching requires file, symbol, category, and callee. The added inverse has a presence assertion beside the rejection assertion and exercises public readers. Review of the final correction diff found no silent failure, dropped error, stale compatibility path, or new substantive defect. Python risk grading over the exact range reports no high records and `code_grade: grade_2`: `case_live_tree_passes` is a cohesive live-tree integration scenario whose setup and observations belong together; `run_canonical_reader_strictness_cases` is a cohesive table-driven strictness scenario aggregator. Both are test-only medium grade-2 records and do not block.

```yaml
VERDICT: PASS
DIGEST:
  headline: "Both stages pass at final tip 5be21a43; F-01 through F-04 are resolved with discriminating evidence."
  severity_max: none
  findings: []
  must_fix: []
  spec_violations: []
  code_grade: grade_2
  grade_2_reasons:
    - "tests/integration/test-check-omp-port.py:71 case_live_tree_passes is one cohesive live-tree integration scenario whose setup and observations belong together."
    - "tests/integration/test-validate-digest.py:4993 run_canonical_reader_strictness_cases is one cohesive table-driven strictness scenario aggregator."
  reviewed: "8c3143bd5668ce11186a2a1f8dbe784ff9639d88..5be21a432b87ed648c0bed50fbf9a2642c84e0a9"
  human_commits_in_scope: []
  open_questions: []
  files_touched:
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-285-canonical-reader/.harness/harness/features/BUG-285-canonical-reader/notes/review-harness-code-reviewer-c1.md
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-285-canonical-reader/.harness/harness/features/BUG-285-canonical-reader/notes/review-harness-code-reviewer-c1.md
```
