# BRIEF — FEAT-02 Fix VERDICT shadowing in validate-digest.py

## Problem

An agent that echoes the harness-handoff contract template before writing its real
return gets the *echoed* block validated and routed instead of the real one. The
validator's top-level anchors (`VERDICT:`, `DIGEST:`, `artifact:`) are all
first-match-wins, and the template line `VERDICT: PASS | FAIL | BLOCKED | ESCALATE`
parses as a valid `PASS`. A real `VERDICT: FAIL` below the echo is never examined —
reproduced 2026-07-27: such a return exits 0 with `digest ok`. A masked FAIL ships
silently, which is the exact defect class this validator exists to prevent. Found
during BUILD task 22 (docs/harness/BUILD.md, task 22 ledger row, recorded not fixed).

## Goal

The validator always validates — and therefore routes — the agent's real return. An
echoed contract template earlier in the message is either rejected or rendered inert;
it can no longer shadow the real verdict, digest fields, or artifact path.

## Requirements

- REQ-01: When a message contains both an echoed contract template and a real return
  block, the validator's verdict, digest-field checks, artifact check, and lead
  roll-up all apply to the real return, never to the echo.
- REQ-02: All currently valid returns remain valid and all currently rejected returns
  remain rejected — no behavior change for messages without an echoed template.

## Constraints

- Files-only, stdlib-only. PyYAML is NOT installed; no new dependencies.
- Fix lives in `.claude/skills/harness/bin/validate-digest.py`; tests in
  `.claude/skills/harness/bin/test-validate-digest.py`.
- Test-first, per team discipline: each new regression case must be proven to fail
  against the pre-fix binary (the suite's `VALIDATE_DIGEST_BIN` override exists for
  this — task-22 precedent).
- Hook-mode fail-open semantics (exit 2 blocks; our own bugs pass through loudly)
  must not change.

## Success Criteria

- SC-01: The echo repro (template block followed by a real return) is rejected or
  correctly routed: with the fix, a shadowed real block is the one validated, and the
  new regression cases fail when run against the saved pre-fix binary.
  verify: automated        evidence: unit
- SC-02: All 36 existing suite cases still pass; the full suite exits 0.
  verify: automated        evidence: unit

## Approval

status: approved
approved-by: Mike Ruangutai
date: 2026-07-27

<!-- ONLY the user approves. The orchestrator writes this section on their explicit
     say-so and never on its own initiative; pm never touches it at all. -->
