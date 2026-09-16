# Code review — BUG-1756-qa-reverify-bash — c1

Review pin: `c1f9601fe87660b732aac0bf5e5f72dd17fac0d7`; pinned range: `8ef4731e816f08dbc562206134c100b0c034a812..c1f9601fe87660b732aac0bf5e5f72dd17fac0d7`.

## Stage 1 — spec compliance: PASS

Every executable change traces to SC-01–SC-04. The amended marker examples and `harness.md` §3 are also in T-01's ledgered `files` amendment and repair the discovered #1771 prerequisite rather than escaping the signed outcome. No omission, mismatch, or untracked scope creep remains.

- **SC-01 — PASS.** `_claimed_kinds` preserves claimed order while deduplicating (`.claude/skills/harness/bin/validate-digest.py:1998-2003`); `_reverify_suite` builds one `--kind <kind>` invocation per claim and accepts only when all complete successfully (`:2006-2027`). The regression asserts the exact two invocations and exit 0 (`tests/integration/test-validate-digest.py:2282-2288`).
- **SC-02 — PASS.** `_reverify_suite` returns immediately on the first non-zero result (`.claude/skills/harness/bin/validate-digest.py:2021-2026`), and the existing caller reports its return code and real output tail before returning 2 (`:2052-2066`). The regression proves only unit ran, the real unit tail was relayed, and integration output was absent (`tests/integration/test-validate-digest.py:2291-2306`).
- **SC-03 — PASS.** Empty claimed kinds select one bare invocation (`.claude/skills/harness/bin/validate-digest.py:2017-2019`); the regression observes a single empty argv record and exit 0 (`tests/integration/test-validate-digest.py:2309-2315`).
- **SC-04 — PASS.** The stub is a Python file whose argv and exit status are observable (`tests/integration/test-validate-digest.py:2155-2167`). Missing-file, completed-nonzero, real spawn `OSError`, and `TimeoutExpired` paths are separately discriminated (`:2193-2207`, `:2318-2370`); the latter two patch the validator's actual `subprocess.run` lookup and require exit 0 plus the loud diagnostic.

### c0 question closure

- **Q1 — CLOSED.** The new in-process seam intercepts the loaded validator's `subprocess.run`, raises real `OSError(8, "Exec format error")` and `subprocess.TimeoutExpired`, and observes `check_qa_matrix_claim`; changing the exception handler to re-raise makes both cases report `RAISED`, as recorded in `notes/receipt-main-session-T-01-fail-first.md` arm 3. This reaches the branch the c0 directory fixture missed.
- **Q2 — CLOSED.** The fail-first receipt arm 2 records the final test file against pre-fix `24e766bb`: SC-01, SC-02, and SC-03 each fail with exit 2 and `argv=[]`. Thus each exact post-fix assertion has pre-fix red evidence, not merely the generic agree case.
- **Q3 — CLOSED.** The pinned range is based directly on current `origin/main` merge-base `8ef4731e…`, contains no change to `tests/unit/omp-hooks.test.ts`, and the formerly failing case now invokes bare `run-end` then expects `tokensOf(featureJson)` to be null (`tests/unit/omp-hooks.test.ts:1252-1263`). The operator's unrelated local commits are absent from the reviewed range, so the c0 checkout contamination is removed. Per panel ownership, this reviewer did not rerun the unit matrix.

The amendment is internally consistent across `.claude` and `.omp`: all four lead/orchestrator marker examples plus the zero-micro-management source use the non-matching placeholder, and both `harness.md` adapters state that Main's first prompt line carries the real marker (`.claude/commands/harness.md:114-119`). A sweep of those amended surfaces found no remaining concrete `HARNESS-FEATURE: FEAT-<number>` or `BUG-<number>` example.

## Stage 2 — code quality: PASS

The miss/error paths retain the intended split: an unresolved/missing runner or any spawn/timeout exception returns `None` and fails open loudly; a completed non-zero run returns its concrete process result and fails closed as disagreement. No lookup miss fabricates success, no non-zero result is swallowed, and iteration cannot continue past the first failure. List-form argv with `sys.executable` avoids shell interpretation. The implementation is local to the existing validator seam and leaves no obsolete bash path.

Mechanical grading over the pinned merge-base range reports ten changed Python functions, all PASS; `code_grade: pass`. No `[harness:human]` commit is in scope. No substantive, form, or proportionality finding remains.

```yaml
VERDICT: PASS
DIGEST:
  headline: "Both ordered stages pass: SC-01 through SC-04 and c0 Q1/Q2/Q3 are closed at the immutable c1 pin."
  severity_max: none
  findings: []
  must_fix: []
  spec_violations: []
  code_grade: pass
  reviewed: "8ef4731e816f08dbc562206134c100b0c034a812..c1f9601fe87660b732aac0bf5e5f72dd17fac0d7"
  human_commits_in_scope: []
  open_questions: []
  files_touched:
    - .harness/harness/features/BUG-1756-qa-reverify-bash/notes/review-harness-code-reviewer-c1.md
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1756-qa-reverify-bash/.harness/harness/features/BUG-1756-qa-reverify-bash/notes/review-harness-code-reviewer-c1.md
```
