# Observations - harness-qa

- 2026-09-05: BUG-1303 build qa gate — `bugfix.always: [unit]` floor unmet (missing) because the
  whole change's test surface is `tests/integration/test-validate-digest.py`; `run-unit-tests.sh`'s
  unit bucket only globs `tests/unit/test-*.py`, never picks it up. Same shape as BUG-1128's open
  matrix gap, still unresolved in `.harness/harness.json` (`_matrix_provenance` has no `bugfix`
  entry). Guard discrimination itself (16 per-persona lines + both synthetic group lines,
  roster derived from `validator.ALIAS` at test-validate-digest.py:480) is clean and mutation-proven
  red-capable via a throwaway `/tmp` script.
- 2026-09-05: T-01+T-02+T-03 landed bundled in one commit (`cdfce3cb`) despite plan.yaml declaring
  an expected-red-then-green sequence across those three tasks — test-first ordering is
  unverifiable from git alone in this repo when a build agent squashes a guard and its fixing
  tasks into a single commit. Worth flagging to build agents: keep guard-add and guard-fix as
  separate commits when the plan narrates a red/green sequence, or the qa gate cannot check it.
