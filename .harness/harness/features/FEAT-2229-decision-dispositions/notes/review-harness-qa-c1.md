# QA gate — FEAT-2229 c1 (pin 1ef1edbf4cd13eed110e5a187fe45b2ce0438d43)

**BLUF: PASS.** matrix_ok true; unit and integration satisfied; fail-first evidence reproduced for SC-01/02/03/07; T-03 verify green. No findings.

## Pin and equivalence
- Pinned checkout (pinned-checkout.py, persona harness-qa) HEAD = 1ef1edbf; clean. Base pin dfa52536fa4ff8b84df5fe87132135008fa244e4.
- `git diff --stat 6c4da464 1ef1edbf` touches only feature-dir files (feature.json, plan.yaml, four simplify receipts): no code, test, doc or prompt differs, so 6c4da464 evidence is code-identical. Not relied on; every gate re-run at the pin.
- Environment: HARNESS_AGENT_TYPE, HARNESS_CONTROL_PLANE_ROOT, HARNESS_FEATURE_TREE_ROOT unset in run shells (`env | grep HARNESS` empty).

## Matrix (control-plane .harness/harness.json)
- T-01 cross_module -> always unit + integration (both `active`, cmd run-unit-tests.py --kind unit/integration).
- T-02 docs, T-03 docs -> always []; no kind required. Config-shape trigger not tripped (harness.json change adds one era key, task is cross_module anyway).
- eval/functional excluded (DEC-187), locally_run kinds untouched by diff (no omp session/handoff/issue-type surface).

## Per-kind results (pin, env cleared)
- Task verifies verbatim: T-01 unit 40/40 + integration 91/91, rc0; T-02 test-plan-team 182/182 rc0; T-03 `gen-decisions-index.py --stdout | diff -` rc0.
- unit standing cmd `run-unit-tests.py --kind unit`: rc0, 62 files in tests/unit; test-decision-disposition-schema.py and test-checker-structure-locks.py ran and passed. Bare `FAIL BUG-1290...` lines are the mutation-proof's own tokens (G-09), not failures.
- integration `--kind integration`: first run rc1 — only test-check-domain-post.py hit its 30s subprocess timeout at load avg ~24 (concurrent readers); alone it is rc0 in 7s. Full rerun rc0: 89 script blocks, 3023 PASS lines, 95 files in tests/integration; test-plan-merge, test-plan-team, test-plan-decision-dispositions all ran and passed. The first-run failure is environmental load, passed on rerun; recorded, not graded away.
- Note: test-plan-decision-dispositions measured 32.8s under that load vs T-01's "under 30 s" intent; 11.5s unloaded. Advisory only.

## Fail-first (reproduced, tier: natural RED, semantic)
Base pin dfa52536 + the four tests extracted from 1ef1edbf via git archive (source untouched):
- unit schema: 13/40, rc1 (27 behavioural failures: row/key/successor/disposition rejections, set-key refuses malformed, byte identity) -> SC-01.
- integration dispositions: 42/90, rc1 (48 FAIL: each of the six check failures, STRUCK, wrong-section/partial clause, successor, owner, era boundary/null/malformed, stamp, backdating routes) -> SC-02, SC-03.
- test-plan-team: 30 of 153 FAILING -> SC-07.
Counts match notes/red-first-T-01.md and red-first-T-02.md. SC-04/05/06 are `verify: inspection` (not graded here).

## Coverage gaps vs Phase 1
None. Static prompt tests (SC-07) prove presence at owner, not agent conduct — stated in BRIEF and red-first-T-02.

## Housekeeping
Both pins removed on return. Logs not copied (no redirect permitted in my domain); outputs summarized above.
