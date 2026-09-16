# Grilling — validate-digest re-verifies a qa PASS by running run-unit-tests.py under bash (#1756) — 2026-09-16

## Destination
`validate-digest.py`'s #919 re-verification of an unconditional qa PASS actually runs the suite:
it spawns the Python runner with the Python interpreter, over the matrix kinds the claim names,
so a green matrix is confirmed and a red one is still refused with the real tail.

## Mission
mission: patch
reason: cause known (#1674 converted run-unit-tests.sh to .py; `_reverify_suite` still spawns `["bash", run_bin]`), diff bounded to one function and its test stub, no new interface, schema or enforcement surface — the existing gate is made to do what it already claims.
confirmed-by: operator (blanket ruling in session 2026-09-15: "do all of them from plan (or patch) to ship"; #1756 filed by Main during BUG-1723 validate c3 and taken as the next patch on 2026-09-16 after the operator restarted OMP to verify BUG-1724)

## Settled
- Cause → `.claude/skills/harness/bin/validate-digest.py` `_reverify_suite` spawns `["bash", run_bin]`; `run_bin` resolves to `run-unit-tests.py` since #1674. bash reads a Python file, `import: command not found`, exit 2; `check_qa_matrix_claim` reads exit 2 as a red matrix and refuses every honest PASS (observed on BUG-1723 validate c2 and c3, BUG-1716 c1/c2, FEAT-1714 c1/c2 — every validator this session had to record qa's verdict from its note).
- Fix → spawn `[sys.executable, run_bin, "--kind", <k>]` for each kind the claim's `evidence:` names (`unit`, `integration`), stop at the first non-zero, print its tail. No kinds named → the bare runner (its default set).
- Test → `tests/integration/test-validate-digest.py` stubs the runner as `stub-run-unit-tests-%d.sh`; the stub becomes a `.py` that exits with the requested code and records its argv, so a bash spawn cannot pass it (fail-first arm) and the kinds forwarded are asserted.
- Fail-open posture unchanged → a missing script, spawn error or timeout still prints "could not independently re-run" and returns 0 (check-domain precedent); disagreement still returns 2.
- DEC-174 → gate surface: build main-session-direct; the orchestrator runs intake and validate only.

## Fog
- none

## Out of scope
- Re-verifying at `review_sha` instead of the feature checkout's HEAD (the claim is about the pin; a later commit can legitimately differ) — separate ticket if wanted.
- INV-43 / BUG-1723's own seam grading.
