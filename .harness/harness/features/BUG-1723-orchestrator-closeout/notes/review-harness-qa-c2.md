# QA gate — BUG-1723-orchestrator-closeout — c2

Pinned SHA: `972d5c054e6a1dbab811f957ff5d5186a7445f63`. All commands ran in detached `qa-BUG1723-c2-pin` at that SHA; `git rev-parse HEAD` returned the pin.

```yaml
VERDICT: BLOCKED
DIGEST:
  headline: "Pinned c2 evidence passes and C1-V01/V02/V03 are closed, but the required return validator re-runs a later checkout and blocks this exact-pin gate."
  suite: pass
  failures: 0
  matrix_ok: true
  kinds:
    - { kind: unit, state: satisfied, cmd: "env -u HARNESS_AGENT_TYPE .agents/skills/harness/bin/run-unit-tests.py --kind unit", named_tests: 40 }
    - { kind: integration, state: satisfied, cmd: "env -u HARNESS_AGENT_TYPE .agents/skills/harness/bin/run-unit-tests.py --kind integration", named_tests: 72 }
  coverage_gaps: []
  sc_evidence:
    - { id: SC-01, test: "tests/unit/test-feature-record.py:182-212; direct T-01 command: 48 passed" }
    - { id: SC-02, test: "tests/unit/test-feature-record.py:247-312; direct T-01 command: 48 passed" }
    - { id: SC-03, test: "tests/integration/test-check-state-feat59.py:396-458; direct T-02 command: all cases passed" }
  fail_first:
    - { sc: SC-01, evidence: "notes/receipt-main-session-T-01-fail-first.md:6-16 (six pre-close-run cases red at 5bfab2da)" }
    - { sc: SC-02, evidence: "notes/receipt-main-session-T-01-fail-first.md:6-16 plus notes/receipt-main-session-fix-c2.md:8-14 (judgement and public spend arms red against fac877f1^)" }
    - { sc: SC-03, evidence: "notes/receipt-main-session-T-02-fail-first.md:6-17 (retrospective and unusable-chronology cases red at 69ebcefd)" }
  open_questions:
    - { id: Q1, question: "The independent verifier executes run-unit-tests.py in the feature checkout at later HEAD 97f29875, whose script is interpreted as shell and exits 2; should the exact-pin validation contract be amended to re-run at review_sha, or should that later-checkout execution failure be repaired outside this gate?", blocking: true }
  files_touched: [".harness/harness/features/BUG-1723-orchestrator-closeout/notes/review-harness-qa-c2.md"]
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1723-orchestrator-closeout/.harness/harness/features/BUG-1723-orchestrator-closeout/notes/review-harness-qa-c2.md
```

## Required matrix and plan verifies

T-01 `python3 tests/unit/test-feature-record.py` passed: 48 tests. T-02 `python3 tests/integration/test-check-state-feat59.py` passed. T-03's supplied three-playbook token inspection passed (exit 0). The task types are `cross_module`, `cross_module`, and `docs`; the configured floor therefore requires unit and integration only. The unit matrix passed 40 files and the integration matrix passed 72 files; after the independent re-check, both matrix commands were rerun at the exact detached pin and passed again. No other matrix predicate fired.

## Phase-1 coverage delta

Before implementation inspection, required coverage was: close-run success and paired optional inputs; every refusal's named first stage, stop, retained earlier writes, and fail-first evidence; INV-43 after/before/equal, multi-handoff, unusable chronology, terminal station, and fail-first evidence; and the SC-04 playbook inspection. Phase 2 found these covered except SC-04, whose required inspection passed via T-03 and is not an automated SC. SC-05 remains deferred_not_yet_verifiable by the approved BRIEF.

## C1 findings re-measured

- **C1-V01 — closed.** `references/ledger.md:52-59` now states that retrospective INV-43 is a violation at every station, including `done`, identifies BUG-285 as an honest census, and says unreadable chronology is CANNOT VERIFY. The known BUG-1723 and BUG-285 INV-43 reports remain specified behavior, not regressions.
- **C1-V02 — closed.** `receipt-main-session-fix-c2.md:8-14` distinguishes both repaired refusal assertions: the public spend arm errors on absent `cmd_close_run`, while the judgement arm fails because pre-change argparse rejects `close-run`. These are separate pre-change reds and directly satisfy the previously missing historical evidence.
- **C1-V03 — closed.** `tests/unit/test-feature-record.py:273-312` imports the actual CLI module, invokes public `cmd_close_run`, lets all non-spend subprocesses run, and injects exit 3 only when the real tuple's argv contains `spend`. Its assertions require `REFUSED at stage spend`, retained run-end/judgement writes, and no success summary. [INFERENCE] Renaming the tuple stage to `summary` or moving spend before judgement reddens this test; the exact public composition in `feature-record.py:397-408` iterates that tuple and supplies the stage name.

No new findings. The c2 receipt's pre-change output is accepted only for the two explicitly named and distinguishable judgement and public-spend refusal cases above.

## Cleanup

Removed `/Users/molchairuangutai/GitHub/harness/.claude/worktrees/qa-BUG1723-c2-pin` with `git worktree remove`. The subsequent `git worktree list --porcelain` contains no `qa-*-pin` worktree.
