# Receipt — harness-backend-dev — BUG-442 ALTITUDE F1 apply

## Task
Apply ALTITUDE F1 from the simplify pass: replace a stale line-number citation
`(test-harness-yaml.py:892-904)` inside the failure message of the anti-false-red
assertion in `test_docs_domain_witness_reddens_on_addition_removal_and_census_drift`
with a name reference that cannot go stale. Asserted expression left byte-identical.

## Change
File: `tests/integration/test-harness-yaml.py`, line 373 only.

Before:
```
            f"try/except (test-harness-yaml.py:892-904), so an unrelated test printing ok "
```
After:
```
            f"try/except (see main() at the foot of this file), so an unrelated test printing ok "
```
No other line touched. The asserted condition
`'ok   test_bare_date_scalar_stays_str' in child.stdout` is byte-identical before and after.

## Verify — task's own verify chain (verbatim)
```
env -u HARNESS_AGENT_TYPE python3 tests/integration/test-harness-yaml.py && \
env -u HARNESS_AGENT_TYPE python3 tests/integration/test-harness-yaml.py | grep -q '^ok   test_docs_domain_grant_is_exhaustive_over_every_persona$' && \
env -u HARNESS_AGENT_TYPE python3 tests/integration/test-harness-yaml.py | grep -q '^ok   test_docs_domain_witness_reddens_on_addition_removal_and_census_drift$'
```
Result: **exit 0**. Direct run of the script showed both named tests printing `ok`:
`ok   test_docs_domain_grant_is_exhaustive_over_every_persona` and
`ok   test_docs_domain_witness_reddens_on_addition_removal_and_census_drift`. Two later
`BrokenPipeError` tracebacks are `main()` continuing to print after `grep -q` closed its
end of the pipe (expected shell behavior with `grep -q`, not a test failure) — the chain's
own reported exit status is `CHAIN_EXIT=0`.

## Verify — unit suite
Command run: `env -u HARNESS_AGENT_TYPE bash .claude/skills/harness/bin/run-unit-tests.sh`
(the task's literal `tests/run-unit-tests.sh` does not exist in this checkout; the real
script lives at `.claude/skills/harness/bin/run-unit-tests.sh`, confirmed by repo grep).

- Runner exit status: **0**
- `^FAIL ` line count: **0**
- Tail confirms `PASS test-check-state.py` and a final `pool: 8 workers, 80 files, 98.97s wall`
  summary — no red suite hidden behind a truncated tail read.

## Acceptance
`git status --short` in the worktree shows exactly:
```
 M tests/integration/test-harness-yaml.py
```
No other file modified. Edit is unstaged and uncommitted, as required.
