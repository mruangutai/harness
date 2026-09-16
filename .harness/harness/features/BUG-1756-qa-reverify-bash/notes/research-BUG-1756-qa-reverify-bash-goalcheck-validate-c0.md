# Goal-check — BUG-1756-qa-reverify-bash — validate c0

## BLUF

At review pin `01dd2ed8eb6802048cf21ef3508e2e9310096695`, both signed perspectives are **partial**. The pinned implementation and post-fix handoff support the requested runtime behavior, but the signed regression-proof clauses are not fully discharged: SC-01 through SC-03 lack executions of their exact cases against the pre-fix implementation, and SC-04 has no timeout case and does not exercise a real subprocess spawn error. No tests were rerun during this goal-check, as dispatched.

## Perspective grades

- **operator — partial.** Carried by SC-01, SC-02, and SC-03. At the pin, `.claude/skills/harness/bin/validate-digest.py#_claimed_kinds` derives the named kinds, `#_reverify_suite` invokes `[sys.executable, run_bin, --kind, kind]` once per kind or invokes the runner bare when none are named, stops at the first non-zero result, and `#check_qa_matrix_claim` emits its output tail and returns 2 on disagreement. The matching pinned tests are `tests/integration/test-validate-digest.py#_bug1756_kinds_forwarded_case`, `#_bug1756_first_failure_stops_case`, and `#_bug1756_default_set_case`; `notes/handoff-build.md#Trust` records the post-fix suite green. However, `notes/receipt-main-session-T-01-fail-first.md` records a 4/5 pre-fix run containing only the prior generic agreement failure and explicitly says the SC-01..SC-03 cases were added with the fix, so their required exact fail-first demonstrations are absent.
- **code maintainer — partial.** Carried by SC-04. The Python stub in `tests/integration/test-validate-digest.py#_bug919_stub_script` and the receipt demonstrate the bash-launch regression; pinned cases retain completed-nonzero refusal (`#_bug919_disagree_case`) and missing-runner fail-open output (`#_bug919_missing_script_case`). But the new `#_bug1756_spawn_error_case` supplies a directory, which `validate-digest.py#_reverify_suite` rejects at `os.path.isfile` before `subprocess.run`, so it does not prove the exception/spawn-error branch. The pinned test file contains no timeout case.

## Success-criterion status

- **SC-01 — partial.** Current kind forwarding and acceptance are covered at the pin and reported green in the build handoff; the criterion's exact pre-fix failing execution is not recorded.
- **SC-02 — partial.** Current first-failure stop, real tail, and exit-2 behavior are covered at the pin and reported green; the exact case was not executed in the recorded pre-fix run.
- **SC-03 — partial.** Current bare/default invocation is covered at the pin and reported green; the exact case was not executed in the recorded pre-fix run.
- **SC-04 — partial.** The bash-versus-Python red arm, missing-runner fail-open, and completed-nonzero disagreement are evidenced, but actual spawn-error and timeout preservation are not proven by the pinned integration tests.

## Findings

- **F-01 — substance — T-01.** SC-01, SC-02, and SC-03 require their integration cases to demonstrate failure before the fix. The fail-first receipt records only `4/5 bug919 qa-matrix-reverify cases passed` and says these three cases were added with the fix; it does not record running them against the pre-fix validator. Remedy ownership is T-01 because its signed `files` include `tests/integration/test-validate-digest.py` and its `traces` include SC-01 through SC-03.
- **F-02 — substance — T-01.** SC-04 requires regression proof for missing runner, spawn error, and timeout. At the pin, the purported spawn-error case is intercepted by the regular-file precondition and there is no timeout case, leaving two clauses unproven. Remedy ownership is T-01 because it owns the integration test and traces SC-04.

## Trace and scope

`plan.yaml#T-01` traces SC-01 through SC-04 and owns both changed code/test surfaces. The signed BRIEF declares no REQ identifiers, so there is no separate REQ-coverage ledger. No unowned scope-change question was found.
