# QA gate — BUG-1723-orchestrator-closeout — pinned `e23646776b1cf1d1833ca0b7cab5da12272eba7b`

```yaml
VERDICT: FAIL
DIGEST:
  headline: "Targeted T-01/T-03 checks pass, but the required integration matrix command fails a changed documentation binding."
  suite: fail
  failures: 1
  matrix_ok: false
  kinds:
    - { kind: unit, state: satisfied, cmd: ".agents/skills/harness/bin/run-unit-tests.py --kind unit", named_tests: 6 }
    - { kind: integration, state: satisfied, cmd: "python3 tests/integration/test-check-state-feat59.py", named_tests: 10 }
  coverage_gaps: []
  sc_evidence:
    - { id: SC-01, test: "tests/unit/test-feature-record.py:182; :196" }
    - { id: SC-02, test: "tests/unit/test-feature-record.py:214; :228; :236; :247" }
    - { id: SC-03, test: "tests/integration/test-check-state-feat59.py:396; :421; :437" }
    - { id: SC-04, test: ".claude/skills/harness/SKILL.md:79; .claude/skills/harness/references/build-phase.md:9; .claude/skills/harness/references/ledger.md:9" }
  fail_first:
    - { sc: SC-01, evidence: "notes/receipt-main-session-T-01-fail-first.md:6-13" }
    - { sc: SC-02, evidence: "notes/receipt-main-session-T-01-fail-first.md:6-13" }
    - { sc: SC-03, evidence: "notes/receipt-main-session-T-02-fail-first.md:6-17" }
  open_questions: []
  files_touched: [".harness/harness/features/BUG-1723-orchestrator-closeout/notes/review-harness-qa-c0.md"]
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1723-orchestrator-closeout/.harness/harness/features/BUG-1723-orchestrator-closeout/notes/review-harness-qa-c0.md
```

## Gate evidence

T-01 and T-02 are `cross_module`, requiring unit and integration (`.harness/harness.json:172-176`); T-03 is docs and adds no kind. The targeted commands all pass:

- `python3 tests/unit/test-feature-record.py`: 46 tests, 0 failures.
- `python3 tests/integration/test-check-state-feat59.py`: all cases pass, including 43.a–43.k. The authoritative T-02 receipt's grade-2 rationale for `case_inv43_chronology` is adequate (`notes/receipt-main-session-T-02-fail-first.md:19-21`).
- T-03's supplied Python inspection command: exit 0, no output. Each cited SC-04 section presents close-run, separate `STATE.md`/handoff/commit writes, and wake-time quarantine.
- `.agents/skills/harness/bin/run-unit-tests.py --kind unit`: pass.

Required integration matrix command `.agents/skills/harness/bin/run-unit-tests.py --kind integration` fails (exit 1). The concrete failure is `tests/integration/test-check-state-plans.py`: `FAIL - INV-6's exemption has a documented producer (SKILL.md step 6 names code_grade: n_a)`; it cannot find the expected Step 6 `Adjust and record` form after T-03 changed the step heading. This is a real assertion failure, not a load/collection error. The changed playbook therefore breaks the integration suite's documentation binding; repair belongs to the owning T-03 developer, not QA.

Phase-1 expected coverage (composed success/refusals and retrospective/unverifiable chronology) is directly covered. SC-04 inspection passes; SC-05 remains intentionally deferred UAT, not an automated matrix obligation.
