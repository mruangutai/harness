# Pinned code review — FEAT-2398 c0

FAIL on T-01 / SC-03: an empty kind list bypasses missing-policy refusal in the CLI. Mechanical grade: pass, reported by the return validator's independent computation over `9a818b46..685e861a` (not a grader execution by this reader).

- Reviewed `9eb07b4f3cd235c234a10edddbfe5542c1e85fba..685e861a667efd13e3c9720dffe9dbb847d4207b` via git objects, not HEAD. Actual origin/main merge-base is `9a818b46071dadd58d2c59b4dd29d398fc4701e7`; merged BUG-2399 changes are already-main context, not new T-01 scope. No human-marker commits or modified tracked files were observed; only this run directory was untracked.
- **High, substance, T-01, SC-03:** `.claude/skills/harness/bin/validate-digest.py:1795-1800` returns before `_qa_policy` when both kinds and derivable started tasks are empty. CLI `:3206` supplies no trusted feature directory. A contract-valid QA PASS with `suite: pass`, `matrix_ok: true`, nonempty fail-first evidence and `kinds: []` therefore bypasses both absent-pin refusal and the floor. This contradicts D-01's unpinned refusal. The new CLI case in `tests/integration/test-validate-digest.py` `_kp_sc03_harness_cases` supplies a nonempty kind, so does not discriminate this bypass. Require policy establishment before the empty-list early return and retain a real CLI regression. **REASONED, not executed.**

## Stage 1 — compliance

Otherwise SC-01/02/04 map to reported-kind checks (`validate-digest.py:602-655`), always-floor omission (`:1818-1824`) and PASS-only full floor (`:1808-1815`). Conditional latitude and conservative all-excluded exemption remain distinct (`:1661-1692`). Trusted binding/commit/blob selection is centralized (`:418-498`); non-QA `factory_config.product_config` is unchanged. Fixture/classification amendments migrate existing callers to that contract rather than widen behavior.

SC-05 inspection: pinned `.claude/skills/harness-verification-rules/SKILL.md:23`, `.harness/harness/docs/SPEC.md:107,1449`, `.harness/harness/docs/DECISIONS.md:5339,8528,8540`, and `.harness/harness/docs/DECISIONS-INDEX.md:187,239` agree on status/pin/conditional policy and record Kaya's consequence. Required product docs' known absence is not a new finding.

## Stage 2 — quality and evidence limits

Static caller search finds no legacy `_load_matrix_inputs`, `_explicitly_excluded_kinds` or `_matrix_floor` implementation/calls. Kind policy, no-kind exemption and receipt selection share `_qa_policy`; grading retains its separate current-tree reader as signed. No further concrete quality defect found. RED receipt records 39/52 failing, including baseline acceptances and diagnostic-only failures; GREEN records 52/52 at the post-simplify candidate. These are inspected historical receipts, not my execution or independent verification. No tests, mutants, builds, lint, formatters or grader were run by this reader; installed hook behavior was not treated as candidate behavioral proof. Initial return attempted an unavailable-grade sentinel and was refused: the return gate explicitly recomputed `code_grade: pass` over the canonical range. That mechanical result is adopted, without claiming a standalone metric report.

## Principles applied

- Migrate Callers, Then Delete Legacy APIs: checked removed QA matrix/exclusion helpers and migrated receipt/no-kind consumers, without demanding removal of the explicitly unchanged grading reader.

## Open questions

None. QA should independently execute the empty-kind CLI scenario above; no execution result is claimed here.
