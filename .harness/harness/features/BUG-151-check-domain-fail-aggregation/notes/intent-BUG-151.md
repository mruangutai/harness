# Operator's stated intent — BUG-151

Verbatim text of GitHub issue #151, as handed through the plan door. This is the authority the
drafted plan is graded against; BRIEF.md is derived from it and is not a substitute for it.

---

run-unit-tests.sh: deleting `fails += ` leaves a test block printing FAIL while the suite exits 0.
Residual from PR #149 (W4), annotated in code, not structurally fixed. tests/integration/test-check-domain.py
main() aggregates now 21 independent blocks via 21 hand-written `fails += run_x()` lines with a
comment claiming an assertion exists that does not. Deleting the 9 characters `fails += ` from any
one line leaves that block running and printing FAIL text while the suite still exits 0. Same family
as VF-1/VF-2/SC-08/#133: the logic is correct and the thing meant to notice cannot.

Options offered:

1. collect blocks from a registry and sum it (test-harness-yaml.py already uses an explicit TESTS
   list, though note a test appended after that list was silently never run during #149 — the
   mirror-image defect);
2. assert the arithmetic — a self-check that the number of ok/FAIL lines printed matches the number
   counted, catches BOTH the unsummed-block and the unregistered-test directions;
3. accept and document.

Option 2 is named as the only one catching both directions, though it is the only one adding
test-runner-testing code.

Scope: test-check-domain.py has the 21 blocks; other bin/ suites use different shapes and should be
checked before generalizing; run-unit-tests.sh itself keys off subprocess exit codes (a separate,
already-sound layer per this session's live investigation).

---

## Orchestrator's measurements at the base commit 6d969ed3 (not part of the operator's text)

- `grep -c '^def run_'` = 24; `grep -c '^    fails += run_'` = 20. The aggregation sites are 20
  statements plus the `+ run_bug1305_cases()` return term = 21 sites over 24 `run_` names
  (20 called leaves, 1 composite, 3 sub-blocks). The issue's "21 lines" is off by one against disk.
- Baseline green run: exit 0, 398 lines matching `^ok`, 0 matching `^FAIL`, 38s wall.
- Importing the module with importlib takes 0.03s and executes no cases.
- The issue's premise that other suites "use different shapes" is false on disk:
  tests/integration/test-validate-digest.py:4280-4292 has 13 identical sites and
  tests/integration/test-bash-write-guard.py:1316-1323 has 8. They remain out of scope for this
  ticket by the operator's own scoping.
