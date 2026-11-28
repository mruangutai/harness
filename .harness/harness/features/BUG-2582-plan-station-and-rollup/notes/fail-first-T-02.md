# T-02 fail-first record (BUG-2582)

Built by the main session, main-session-direct (DEC-174), on 2026-11-27. Base: `e6960865`, with T-01, T-04 and T-05 landed. T-05's apply prompt is read by `bug2582-apply-prompt-resolves`.

## RED: the new tests against the unchanged validator

Command: `env -u HARNESS_AGENT_TYPE python3 tests/unit/test-validate-digest-plan-rollup.py`. Exit 1.

- **FAIL, each with the worst-member error:** `bug2582-relief-resolved`, `bug2582-relief-reader-code-reviewer`, `bug2582-relief-reader-slot` and `bug2582-producer-witness`.
  - The producer witness runs the real chain: `record-panel` then `set-panel`, both exit 0, and the base validator still refuses the PASS.
- **FAIL, each because the error list lacks "Plan-team reader carve-out not applied":** every (R) denial, namely open-on-disk, historical-open, absent-from-plan, mismatched-row, folded-disposition, malformed-row, no-findings, unattributable, ambiguous, duplicate-step, no-plan, unloadable-plan and mission-patch. The base validator cannot produce that text.
- **PASS:** `bug2582-control-fail-verdict-valid`, `bug2582-apply-prompt-resolves`, `bug2582-deny-team-build`, the three `bug2582-deny-nonreader-*` cases, `bug2582-deny-escalate`, `bug2582-deny-blocked`, `bug2582-other-lead-eng` and `bug2582-other-lead-validator`.

## GREEN

All 27 cases pass. The T-02 literal verify exits 0:
- the unit file passes;
- the red proof against the base `validate-digest.py` prints "red-first ok";
- `tests/integration/test-validate-digest.py` reports "ALL PASSED".

## Notes

- **OQ-2 applied.** The header comment over the roll-up now names the carve-out as its one exception.
- **The fixture root carries `.harness/team-config.yaml` and `harness.json`.** Without them, the producer witness's `plan-merge.py` calls discard `HARNESS_PROJECT_DIR` and fall back to the worktree root.
