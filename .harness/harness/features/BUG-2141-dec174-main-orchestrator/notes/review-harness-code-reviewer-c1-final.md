# Code review — BUG-2141 — c1-final

**PASS: E-01 is closed by executed mechanical grading; `code_grade: pass`.** All 13 emitted function records meet their bars. No `SEVERITY: high`, grade-2 or `REASON REQUIRED` records; no grade-2 reasons needed.

Reviewed `0b17e9bbf7ef4baafa0eb0844ec0edbb753dd86f..cc0c16bd31035152857c07036fce6094715e596e`. This is the narrow T-01 evidence followup to `notes/review-harness-code-reviewer-c1.md`, not a new source review. Its spec-compliance/quality assessment and empty human-commit set stand. SC-04 inspection: `tests/integration/test-dispatch-guard.py:756-776` supplies the real Main-origin positive/control dispatches; SC-01/SC-02 inspection pointers remain in the c1 receipt.

## Executed evidence
Working directory: `/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2141-dec174-main-orchestrator`.

Exact command: `python3 /Users/molchairuangutai/GitHub/harness/.claude/skills/harness/bin/code-grade.py --base 0b17e9bbf7ef4baafa0eb0844ec0edbb753dd86f --head cc0c16bd31035152857c07036fce6094715e596e`

Exit **0**, terminal summary **`PASSING: 13`**, wall time 0.36s. Metrics below are cyclomatic / cognitive (Sonar-style approximation) / ABC; every result is PASS. Paths: P = `.claude/skills/harness/bin/dispatch-guard.py`; I = `tests/integration/test-dispatch-guard.py`; U = `tests/unit/test-lead-start-preflight.py`.

| Site / function | Metrics | Grade / bar | Driver |
|---|---|---|---|
| P:690 `_direct_orchestration_refusal` | 5 / 5 / 9.3 | 4 / 4 | cyclomatic+cognitive+abc |
| I:672 `_plan_with_modes` | 2 / 0 / 2.8 | 5 / 3 | cyclomatic+cognitive+abc |
| I:679 `case_15c_omp_main_eng_lead_on_all_direct_plan_refused` | 6 / 14 / 24.3 | 3 / 3 | cognitive+abc |
| I:717 `_pending_plan` | 2 / 1 / 3.0 | 5 / 3 | cyclomatic+cognitive+abc |
| I:727 `_main_start` | 2 / 3 / 16.1 | 4 / 3 | abc |
| I:752 `_starts_and_claims` | 4 / 1 / 7.1 | 5 / 3 | cyclomatic+cognitive+abc |
| I:757 `case_15d_dec174_controls_keep_prior_outcomes` | 3 / 2 / 14.3 | 4 / 3 | abc |
| U:302 `plan_text` | 2 / 3 / 4.6 | 5 / 3 | cyclomatic+cognitive+abc |
| U:321 `registry_bytes` | 2 / 1 / 4.9 | 5 / 3 | cyclomatic+cognitive+abc |
| U:329 `planned_start` | 2 / 2 / 13.3 | 4 / 3 | abc |
| U:344 `dec174_main_eng_lead_refused` | 5 / 5 / 10.5 | 4 / 3 | cyclomatic+cognitive+abc |
| U:356 `dec174_nonqualifying_unchanged` | 4 / 3 / 9.4 | 4 / 3 | abc |
| U:365 `dec174_controls` | 7 / 5 / 22.2 | 3 / 3 | abc |

Grader emits new-or-worsened records, not an exhaustive inventory of unchanged functions. Read `harness-code-risk-grading`, `harness-code-review` and `code-grade-review.md` before execution. Read landed `notes/review-harness-qa-c1.md`: its exact verify, configured-suite and retained fail-first evidence stand; no suites or other checks rerun. No source mutations or earlier receipt overwrites.

Findings, must-fix, spec violations, grade-2 reasons and open questions: **none**. Prior nonblocking BUG-2110 fallback advisory remains unchanged; no new gate is introduced.
