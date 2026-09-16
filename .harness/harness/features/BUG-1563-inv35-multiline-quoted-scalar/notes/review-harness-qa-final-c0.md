# QA hard-matrix gate — PASS

## Scope and matrix

- **Pinned review SHA:** `9fd79689e24353ac81689bb5227b8aa752e536ea` (full feature diff base `f5ffdcf4fbfee2f2c044fcd046253df65bc40550`).
- **Inferred change type:** `bugfix`; the diff changes executable `.claude/skills/harness/bin/check-state.sh` and its behavioral tests.
- **Required kinds:** `unit` from `bugfix.when.touches_runtime_code`; `integration` is also satisfied because this diff changes an integration test and T-01 directly requires it. `__bug_class__` is not applicable: no resolved bug-class match.
- **V-01:** resolved. T-02 adds `tests/unit/test-check-state-inv35.py`, which is discovered by the active `tests/unit/**` kind and executes the real checker.

## Commands

| Kind / gate | Exact command | Exit | Result |
|---|---|---:|---|
| T-01 / integration | `python3 tests/integration/test-check-state-plans.py` | 0 | `inv35.l` double-quoted and `inv35.m` single-quoted continuation cases silent; `inv35.n` unquoted `notes: close out #217` reported |
| T-02 / unit | `python3 tests/unit/test-check-state-inv35.py` | 0 | all three focused real-checker outcomes PASS |
| unit matrix command | `env -u HARNESS_AGENT_TYPE .agents/skills/harness/bin/run-unit-tests.sh --kind unit` | 0 | 39 scripts; includes `test-check-state-inv35.py` PASS |
| integration matrix command | `env -u HARNESS_AGENT_TYPE .agents/skills/harness/bin/run-unit-tests.sh --kind integration` | 0 | 72 scripts; includes `test-check-state-plans.py` PASS |
| applicable canonical checker | `bash .claude/skills/harness/bin/check-state.sh` | 0 | no violation; informational notes only |

`matrix_ok: true`. No active required kind was missing, misconfigured, or locally-run for this diff.

## Success-criterion and fail-first evidence

- **SC-01:** current behavioral evidence is `tests/integration/test-check-state-plans.py:792-833,994-996`. Pre-fix evidence is the earlier durable QA record `notes/review-harness-qa-c0.md:8-11`, independently reproduced here by `CHECK_STATE_REV=f5ffdcf4fbfee2f2c044fcd046253df65bc40550 python3 tests/unit/test-check-state-inv35.py` (exit 1): both quoted cases fail with INV-35 while the unquoted control passes.
- **SC-02:** current direct-command evidence is `tests/integration/test-check-state-plans.py:792-833,984-996`; its durable pre-fix record is `notes/review-harness-qa-c0.md:10-11`. The same archived pre-T-01 checker reproduction above supplies direct behavioral confirmation of both failing multiline cases and preserved positive control.
- **SC-03:** current direct unit evidence is `tests/unit/test-check-state-inv35.py:69-94` (exit 0). Its explicit pre-fix proof is the archived-checker run above (exit 1; double and single quoted cases fail, unquoted positive control passes). `tests/unit/test-check-state-inv35.py:16-32` materially selects that immutable checker revision rather than copying scanner logic.

The pre-fix command is captured in this durable artifact and uses the exact pre-T-01 revision; it does not infer fail-first from today’s green result.

## Findings

None. `findings: []`; no kind/severity finding is open.

```yaml
VERDICT: PASS
DIGEST:
  headline: "PASS: focused proof, active unit/integration matrix obligations, and fail-first evidence satisfy the pinned QA gate; V-01 is resolved."
  suite: pass
  failures: 0
  matrix_ok: true
  required_kinds: [unit, integration]
  kinds:
    - { kind: unit, state: satisfied, cmd: "env -u HARNESS_AGENT_TYPE .agents/skills/harness/bin/run-unit-tests.sh --kind unit", named_tests: 39 }
    - { kind: integration, state: satisfied, cmd: "env -u HARNESS_AGENT_TYPE .agents/skills/harness/bin/run-unit-tests.sh --kind integration", named_tests: 72 }
  coverage_gaps: []
  sc_evidence:
    - { id: SC-01, test: "tests/integration/test-check-state-plans.py:792-833,994-996" }
    - { id: SC-02, test: "tests/integration/test-check-state-plans.py:792-833,984-996" }
    - { id: SC-03, test: "tests/unit/test-check-state-inv35.py:69-94" }
  fail_first:
    - { sc: SC-01, evidence: "notes/review-harness-qa-c0.md:8-11; archived pre-T-01 checker run recorded above, exit 1" }
    - { sc: SC-02, evidence: "notes/review-harness-qa-c0.md:10-11; archived pre-T-01 checker run recorded above, exit 1" }
    - { sc: SC-03, evidence: "CHECK_STATE_REV=f5ffdcf4fbfee2f2c044fcd046253df65bc40550 python3 tests/unit/test-check-state-inv35.py, exit 1, recorded above" }
  findings: []
  must_fix: []
  open_questions: []
  files_touched:
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1563-inv35-multiline-quoted-scalar/.harness/harness/features/BUG-1563-inv35-multiline-quoted-scalar/notes/review-harness-qa-final-c0.md
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1563-inv35-multiline-quoted-scalar/.harness/harness/features/BUG-1563-inv35-multiline-quoted-scalar/notes/review-harness-qa-final-c0.md
```
