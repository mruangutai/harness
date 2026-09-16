# QA gate — BUG-1723-orchestrator-closeout — pinned `c700a71e5f513a483f33e495cd3aa559cdd2ee78`

```yaml
VERDICT: FAIL
DIGEST:
  headline: "The required unit and integration matrix passes at c700a71, but V-01 remains contradicted by ledger.md and V-02 has no fail-first evidence for its new refusal arms."
  suite: pass
  failures: 0
  matrix_ok: true
  kinds:
    - { kind: unit, state: satisfied, cmd: "env -u HARNESS_AGENT_TYPE .agents/skills/harness/bin/run-unit-tests.py --kind unit", named_tests: 40 }
    - { kind: integration, state: satisfied, cmd: "env -u HARNESS_AGENT_TYPE .agents/skills/harness/bin/run-unit-tests.py --kind integration", named_tests: 72 }
  coverage_gaps: []
  sc_evidence:
    - { id: SC-01, test: "tests/unit/test-feature-record.py:182-194; c700a71 direct T-01 run: 48 passed" }
    - { id: SC-02, test: "tests/unit/test-feature-record.py:247-291; c700a71 direct T-01 run: 48 passed" }
    - { id: SC-03, test: "tests/integration/test-check-state-feat59.py:396-458; c700a71 direct T-02 run: all cases passed" }
  fail_first:
    - { sc: SC-01, evidence: "notes/receipt-main-session-T-01-fail-first.md:6-13" }
    - { sc: SC-02, evidence: "notes/receipt-main-session-T-01-fail-first.md:6-13 (does not cover c1's new judgement/spend arms; see V-02)" }
    - { sc: SC-03, evidence: "notes/receipt-main-session-T-02-fail-first.md:6-17" }
  open_questions: []
  files_touched: [".harness/harness/features/BUG-1723-orchestrator-closeout/notes/review-harness-qa-c1.md"]
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1723-orchestrator-closeout/.harness/harness/features/BUG-1723-orchestrator-closeout/notes/review-harness-qa-c1.md
```

## Matrix and scoped checks

All commands ran in detached worktree `qa-BUG1723-c1-pin` at the pinned SHA, not the feature worktree's later `HEAD`:

- `python3 tests/unit/test-feature-record.py` — PASS, 48 tests.
- `python3 tests/integration/test-check-state-feat59.py` — PASS, including 43.a–43.j; terminal `done` and `review` retrospective cases both violate.
- T-03's supplied Python inspection command — PASS (exit 0).
- Unit matrix — PASS, 40 files.
- Integration matrix — PASS, 72 files; V-03's documented-producer binding is green.

T-01 and T-02 are `cross_module`, so unit and integration are the entire required matrix (`.harness/harness.json:172-176`); T-03 is docs. The expected INV-43 reports for BUG-1723 and BUG-285-canonical-reader were treated as expected V-01 consequences, not regressions.

## Findings / must-fix

- **V-01 — must-fix — high — substance — T-03.** `check-state.py:3058-3064` now correctly emits terminal-feature INV-43 findings, and `tests/integration/test-check-state-feat59.py:452-457` tests both terminal states. But the shipped operator authority says the opposite: `references/ledger.md:52-57` still says a terminal feature is a note and only a live one a violation. An orchestrator following that ledger will expect a clean check-state exit for a terminal retrospective succession while the executable exits 1; the terminal-note expectation required to be replaced remains.
- **V-02 — must-fix — med — substance — T-01.** The c1 judgement and spend refusal tests exist at `tests/unit/test-feature-record.py:259-291` and pass, but their sole cited pre-change receipt, `receipt-main-session-T-01-fail-first.md:6-13`, names six different tests and predates these arms. It therefore cannot show either new arm failed before the existing close-run implementation. A regression that swallows a judgement refusal or maps a spend-authority exit incorrectly has no captured fail-first proof for the newly added discrimination.
- **V-03 — closed — unrated — substance — T-03.** `tests/integration/test-check-state-plans.py:557-568` now binds the actual Step 6 heading and the full integration matrix passes.

No source, test, plan, feature-record, state, or prior-artifact files were edited.
