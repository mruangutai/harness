# QA gate — FAIL

Reviewed SHA: `c1e85b64d9871e07bdf3b6994ab8e4ee7a36ba11`.
Reviewed file union at that SHA, and no other product/test source: `.claude/skills/harness/bin/check-state.sh` and `tests/integration/test-check-state-plans.py`.

## Scoped proof

- Exact approved T-01 command: `python3 tests/integration/test-check-state-plans.py`.
- Run from the pinned feature worktree: exit `0` (8.61 s). It printed `ok` for `inv35.l` (multiline double-quoted), `inv35.m` (multiline single-quoted), and `inv35.n` (exact unquoted `notes: close out #217` positive control), as well as the pre-existing INV-35 cases.
- SC-01 coverage: `tests/integration/test-check-state-plans.py:case_inv35_multiline_double_quoted_is_silent`, `:case_inv35_multiline_single_quoted_is_silent`, and `:case_inv35_exact_unquoted_positive_control_is_reported`. The first two bind the absence of INV-35 lines; `inv35.n` binds their required positive control. Fail-first relay: `STATE.md:13` records pre-fix exit 1 and false positives for `inv35.l`/`inv35.m`; `STATE.md:14` records their post-fix silence and continuing `inv35.n` detection.
- SC-02 coverage: the same independently invoked integration cases and `main()` registrations (`tests/integration/test-check-state-plans.py:case_inv35_multiline_double_quoted_is_silent`, `:case_inv35_multiline_single_quoted_is_silent`, `:case_inv35_exact_unquoted_positive_control_is_reported`, `:main`). Fail-first relay is separately durable in `STATE.md:13` for both added multiline cases; passing relay in `STATE.md:14` records direct-command exit 0 and the preserved unquoted control.

## Matrix and finding

- `integration`: satisfied — the required direct T-01 command above ran its named cases successfully.
- `unit`: missing — T-01 is `change_type: bugfix` and changes executable checker code, so `.harness/harness.json:202-217` requires `unit` when `touches_runtime_code`. The only changed regression test is under `tests/integration/`, and the permitted command is the direct integration invocation; no named unit test or recorded unit-kind proof covers this checker change.
- `__bug_class__`: not applicable — `match_bug_class` has no resolved bug-class match for this task.

Finding: **high / substance / T-01 / harness-qa** — the matrix-required unit kind has no demonstrated test. If a regression appears in the checker path outside the integration fixture's exercised route, the sole integration proof remains green and the bugfix ships without the required unit-level guard.

Verdict: **FAIL**. `matrix_ok: false`; coverage gap: matrix-required unit coverage. The integration proof and fail-first evidence are complete, but they do not satisfy the matrix floor.
