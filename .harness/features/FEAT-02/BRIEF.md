# BRIEF — FEAT-02: VERDICT shadowing in validate-digest.py

## Goal

An agent return that echoes the handoff contract template before its real three-part return must
never have the echoed `VERDICT:` line routed as its verdict. The validator either routes the real
verdict or rejects the return as a contract violation — it never guesses. Found and reproduced
during BUILD task 22 (`docs/harness/BUILD.md:207`).

## Requirements

- REQ-01: A return containing an echoed contract template (a `VERDICT: PASS | FAIL | ...` enum
  line and/or a placeholder `DIGEST:` block) before the real return is either routed on the *real*
  verdict and digest, or rejected — the echoed content is never what routes.
- REQ-02: A return whose verdict is genuinely ambiguous — multiple `VERDICT:` lines carrying
  *different* valid tokens — is rejected as a contract violation, never resolved by guessing.
- REQ-03: Every return the validator accepts today with a given set of violations produces the
  same outcome after the fix (no regression across the existing 36-case suite).
- REQ-04: The SubagentStop hook's documented behaviours are preserved: the three pass-throughs and
  fail-open-loudly on internal failure (DEC-122), and exit-2 rejection only for *their* contract
  violation (DEC-124 context).

## Constraints

- Files-only, stdlib-only Python — PyYAML is not installed on this machine.
- New repro test cases must be proven to fail against the pre-fix binary before the fix lands
  (the task-22 norm).
- No weakening of DEC-122/DEC-124 hook behaviours unless a `D-NN` in PLAN.md explicitly says so.

## Success Criteria

- SC-1: The echo repro (template echoed before the real return) is rejected or correctly routed —
  the repro test fails against the pre-fix binary and passes post-fix.
  verify: automated — evidence: unit (`.claude/skills/harness/bin/test-validate-digest.py`)
- SC-2: All 36 existing suite cases still pass.
  verify: automated — evidence: unit (`.claude/skills/harness/bin/test-validate-digest.py`)
- SC-3: Hook pass-through and fail-open cases (the 9 hook-mode cases with exact exit-code and
  stderr assertions) pass unchanged — no hook behaviour weakened.
  verify: automated — evidence: unit (hook-mode cases in the same suite)

## Approval

status: pending
approved_by:
approved_on:
