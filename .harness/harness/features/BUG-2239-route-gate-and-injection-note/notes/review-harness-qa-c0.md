# QA review c0 — BUG-2239 (pin 0646be23, base 926383ae, run 2026-11-21-04-validate-validator)

BLUF: T-01 verify green at the pin; unit and integration kinds green. Red evidence is authentic
for SC-01/02/04/05/06 (defect lines, not fixture errors) but the stored receipts carry NO command,
subject SHA or exit metadata. I independently reproduced the SC-06 red (below). Verdict PASS with
advisory provenance findings.

## Phase 1 (BRIEF/plan only) expected coverage
SC-01/04: check fails on over-budget, bad top-level status, bad task status, routing VIOLATION; valid plan passes;
other feature's plan isolated; unloadable plan not clean. SC-02/05: exact note with revised input, flat+batch;
absent without injection. SC-06: real --json subprocess exit 0 + parsed values, plain mode retained.
Gap vs expected: no explicit test of "no note on bash revisions" (only code-path reading: schemasInjected set only in task branch).

## Verify at the pin (HEAD == 0646be2354b49c46e7a7b0acc5f15eff84cf5d19, env HARNESS_AGENT_TYPE unset)
- test-plan-merge.py exit 0 (680 PASS lines, 0 FAIL; case_2239_* x3 = 9 checks PASS; F59 "eight failures" PASS)
- test-check-plan-routes.py exit 0 (ALL PASS)
- tests/unit/test-omp-hooks.py exit 0 (bun: 141 pass, 0 fail, 724 expect)
- test-check-skill-weight.py exit 0 (8 tests OK)
- run-unit-tests.py --kind unit: exit 0, 61 files; --kind integration: exit 0, 87 files (ALL PASSED)

## Fail-first (red = natural, base production over new tests; tier: natural RED, stored receipt)
- SC-01/04 (red-plan-merge.txt:405-421): over-budget, illegal top-level status, illegal task status all `rc=0 ... 0 failure(s)`
  = exit-code red on the real defect; F59 `7 failure(s)` vs expected 8 (line 374/385) = NOBODY VIOLATION absent;
  unloadable plan rc=0 not 5; delegation spy `calls == []` x2 and sentinel finding absent. Valid-plan and isolation PASS pre-fix (guards, discrimination unshown, expected).
  Semantic reds, not fixture errors.
- SC-02/05 (red-hook.txt): `additionalContext` Received undefined in 16-persona batch test (omp-hooks.test.ts:1651) and flat test (:1663); 2 fail / 17 pass. Semantic.
  No-note test (:1668-) green pre-fix by nature; discrimination unshown (not asserted useless).
- SC-06 (red-skill-weight.txt): `NameError: name 'json' is not defined` at check-skill-weight.py:146 in test_cli_json_and_plain_modes. Actual defect.
- SC-03: inspection (check.py `_route_gate_failures`, delegating to routes.cpr.process_plan_yaml(resolved_plan, findings, root, routes.manifest_root); no local rules).

## Independent SC-06 reproduction (this run)
Tree = `git archive 926383ae` (.claude/skills + tests/integration/test-check-skill-weight.py) overlaid with the pin's version of that test file, at /tmp/qa2239-baseb:
`python3 tests/integration/test-check-skill-weight.py` -> exit 1; test_cli_json_and_plain_modes FAILS with NameError json (log /tmp/qa2239-sw-base.log).
A second failure (test_live_tree...: 0 != 16 agents) is an artifact of my partial extraction (no agents/ dir), not a defect. Green at fix: exit 0, 8 tests OK (above).
Subject identities: base 926383aef86ee505d2909c291ef4ab672b8ea09b, fix 0646be2354b49c46e7a7b0acc5f15eff84cf5d19.

## Findings
1. advisory/evidence-provenance — notes/receipts/red-skill-weight.txt, red-hook.txt, red-plan-merge.txt, green-verify.txt (all line 1): receipts hold raw output only; no command, base/fix SHA or exit. BRIEF SC-06 asks for those recorded. Cured here by my independent reproduction; remedy: add header lines to receipts or cite this note. Owner T-01.
2. advisory/coverage — tests/unit/omp-hooks.test.ts: no dedicated test that a bash-tool revision carries no note (SC-02 negative leg); behavior holds by code reading (harness-hooks.ts:1153-1155,1224-1225,1331-1335). Owner T-01.
3. note/matrix — typecheck kind (harness.json test_kinds.typecheck) cmd null, status unresolved, matches harness-hooks.ts; BRIEF already discloses. Not in bugfix matrix `when:` set; not waived silently: static type correctness of harness-hooks.ts is unproven; SC-02/05 rely on bun runtime assertions.
No defects in production code found.

Matrix: bugfix change_type: unit when touches_runtime_code (hooks .ts + .py runtime -> required, satisfied by test-omp-hooks.py/omp-hooks.test.ts + kind run); integration when fix confined to tests/docs (not triggered; run anyway, green); __bug_class__ unresolvable placeholder (no fire).
Pin removed on return.
