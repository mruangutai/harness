# QA validation — PASS

Pinned source is exactly `45328d7a280d251a94b09672a7b6724d55a79f83` (merge-base with `origin/main`: `7ccfae8dd7644bc3aaea612dabf4317c0d804f99`). The full feature diff adds the grading library/CLI/policy and tests, and changes the digest validator and route checker with their integration tests. `PATH=/opt/homebrew/bin:/usr/bin:/bin` selected `/opt/homebrew/bin/python3`, Python 3.14.5. The prior system-Python 3.9 `-P` incompatibility was not re-run and is environmental context only.

## Matrix

The plan’s `logic` tasks require unit; `T-08` (`cross_module`) requires unit and integration; `T-09` (`bugfix`) requires unit plus its relevant bug-class integration coverage. Both configured active commands are therefore blocking and satisfied. No other configured kind is triggered by the committed diff: no UI/component/typecheck/eval surface applies.

| Kind | Exact configured command | Exit | Named discovery |
|---|---|---:|---:|
| unit | `.agents/skills/harness/bin/run-unit-tests.sh --kind unit` | 0 | 29 explicit `UNIT_SCRIPTS` entries |
| integration | `.agents/skills/harness/bin/run-unit-tests.sh --kind integration` | 0 | 28 explicit `INTEGRATION_SCRIPTS` entries |

The runner’s always-on registration/kind-drift cross-check also passed on both invocations. The integration command completed in 247.08 seconds.

## Required contract evidence

- **Grading:** `test-code-grade.py` passed. Its named suite includes 12 hand-derived fixtures spanning grades 1–5, six directional pairs, gated-set resolution, worked-example conformance, and ten agent-tree delivery checks (`test-code-grade.py:19-112, 136-328`).
- **Gate policy:** `test-gate-policy.py` passed all 26 printed named assertions: four keyed policy loads, loud malformed/missing/unreadable handling, review severity/must-fix decisions, and QA policy decisions.
- **CLI:** `test-code-grade-cli.py` passed. Its three named groups cover per-field text/JSON and bars, parse/usage statuses, and diff/deterministic output (`test-code-grade-cli.py:51-143`).
- **Digest:** `test-validate-digest.py` passed 107 named checks: 65 CLI, 1 joint-hint, 1 code-grade/review-policy, 14 hook, 24 T-09, and 2 template cases. This includes rejecting omitted/failing `code_grade`, policy-dependent advisory-versus-`advisory_unless_high` outcomes, and a loud missing-gates path (`test-validate-digest.py:1709-1813`).
- **Route checking:** `test-check-plan-routes.py` passed (`ALL PASS`). It includes owner-manifest enforcement, prior-revision false-OK discrimination, and unreadable-owner-manifest refusal in `case_27a`–`case_27c` (`test-check-plan-routes.py:1399-1459`).

## Success-criterion mapping

- `SC-01`, `SC-03`, `SC-09`, `SC-10`, `SC-17`: `test-code-grade.py`.
- `SC-04`, `SC-05`, `SC-06`, `SC-14`: `test-code-grade-cli.py`.
- `SC-07`, `SC-08`: `test-code-grade.py` gated-set fixture.
- `SC-12`, `SC-13`: `test-gate-policy.py`.
- `SC-16`: `test-check-plan-routes.py:1399-1459`.
- `SC-19`, `SC-20`: `test-validate-digest.py:1709-1813`.

Phase-1 expectation was independent coverage for metrics/bands, directionality, changed-function attribution, CLI fields/status/determinism, skill delivery, policy resolution, digest policy cutover, and owner-manifest routing. Phase 2 found every expected automated contract in the appropriate required kind; no coverage gap remains. `SC-11` is explicitly UAT, not an automated matrix requirement.

Test-first audit: `git log` shows the source and associated tests first landed together in atomic commit `1ac1bd0`; commit timestamps alone cannot establish a preceding red test run. This is reasoned, non-gating evidence; the plan specifies test-first and the committed tests provide the required behavioral proof.
