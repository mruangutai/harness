# QA gate — BUG-1723-orchestrator-closeout — c3

**BLOCKED.** The required matrix passed at exact detached pin `6999227750f68b3ec9c8f77a3ae4f281310742a9`; its `git rev-parse HEAD` output matched that SHA. The return validator nevertheless invokes the runner bare in the later feature checkout, so shell interprets the Python file and exits 2 — precisely the c2 Q1 caller error that Main's re-signature required this gate not to use.

## Phase-1 expectations and coverage delta

Before source inspection, the automated criteria required: one-command close-run success with paired optional inputs and `n_a`; named first-refusal/stop/retained-write cases; and retrospective, no-later-than, and unusable-chronology phase-seam cases. The pinned matrix ran the tests that bind those behaviours: `tests/unit/test-feature-record.py:182-312` covers SC-01/SC-02, and `tests/integration/test-check-state-feat59.py:396-458` covers SC-03. Coverage gaps: none. SC-04 is inspection and SC-05 is the approved deferred UAT, so neither is an automated matrix obligation.

## Required matrix

T-01 and T-02 are `cross_module`; the configured floor is therefore `unit` and `integration` (`.harness/harness.json:172-176`). From the detached checkout root, exactly these commands ran:

- `python3 .claude/skills/harness/bin/run-unit-tests.py --kind unit` — exit 0; runner result `pool: 8 workers, 40 files`; discovered non-zero files: 40.
- `python3 .claude/skills/harness/bin/run-unit-tests.py --kind integration` — exit 0; runner result `pool: 8 workers, 72 files`; discovered non-zero files: 72.

## Fail-first evidence

- SC-01: `notes/receipt-main-session-T-01-fail-first.md:6-16` records the six close-run success/input/validation/refusal arms red against pre-change `5bfab2da`.
- SC-02: `notes/receipt-main-session-T-01-fail-first.md:6-16` records retained-stage refusal coverage red against `5bfab2da`; `notes/receipt-main-session-fix-c2.md:5-15` records the judgement and public spend-stage arms red against `fac877f1^`.
- SC-03: `notes/receipt-main-session-T-02-fail-first.md:6-17` records the retrospective and unusable-chronology positive cases red against pre-change `69ebcefd`.

## Cleanup

Removed the temporary `/Users/molchairuangutai/GitHub/harness/.claude/worktrees/qa-BUG1723-c3-pin` detached checkout. The subsequent `git worktree list --porcelain` contains no `qa-*-pin` worktree.

## Return-validator blocker

The return validator's independent later-checkout invocation is `/.../.claude/skills/harness/bin/run-unit-tests.py` as a shell script, producing `import: command not found` and Python syntax error exit 2. It is neither the exact pin nor either required `python3` matrix command. The signed c2 answer (`notes/answers-2026-09-15-sign.md`, **Re-signature after validate c2**, Q1) states that this invocation is a caller error and requires `python3 .claude/skills/harness/bin/run-unit-tests.py --kind unit|integration` at the pin. Therefore this return cannot truthfully be PASS despite the exact-pin matrix evidence above.

```yaml
VERDICT: BLOCKED
DIGEST:
  headline: "Exact-pin matrix and fail-first evidence pass, but the return validator repeats c2 Q1 by shell-invoking a later checkout's Python runner."
  suite: pass
  failures: 0
  matrix_ok: true
  kinds:
    - { kind: unit, state: satisfied, cmd: "python3 .claude/skills/harness/bin/run-unit-tests.py --kind unit", named_tests: 40 }
    - { kind: integration, state: satisfied, cmd: "python3 .claude/skills/harness/bin/run-unit-tests.py --kind integration", named_tests: 72 }
  coverage_gaps: []
  sc_evidence:
    - { id: SC-01, test: "tests/unit/test-feature-record.py:182-212" }
    - { id: SC-02, test: "tests/unit/test-feature-record.py:247-312" }
    - { id: SC-03, test: "tests/integration/test-check-state-feat59.py:396-458" }
  fail_first:
    - { sc: SC-01, evidence: "notes/receipt-main-session-T-01-fail-first.md:6-16" }
    - { sc: SC-02, evidence: "notes/receipt-main-session-T-01-fail-first.md:6-16; notes/receipt-main-session-fix-c2.md:5-15" }
    - { sc: SC-03, evidence: "notes/receipt-main-session-T-02-fail-first.md:6-17" }
  open_questions:
    - { id: Q1, question: "Why does the return validator re-run a later checkout by shell-invoking `.claude/skills/harness/bin/run-unit-tests.py`, contrary to the exact-pin `python3` invocation resolved in the signed c2 Q1 answer?", blocking: true }
  files_touched: [".harness/harness/features/BUG-1723-orchestrator-closeout/notes/review-harness-qa-c3.md"]
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1723-orchestrator-closeout/.harness/harness/features/BUG-1723-orchestrator-closeout/notes/review-harness-qa-c3.md
```
