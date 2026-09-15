# BRIEF — BUG-1563-inv35-multiline-quoted-scalar

## Problem

INV-35 tracks quote state only within each physical line, so operators reviewing otherwise valid plans receive false findings when a single-quoted or double-quoted YAML scalar continues across lines and contains `#<digit>` on a later line. Issue #1563 measured three such false positives, adding noise at signature time and making genuine truncation findings easier to skim past.

## Done when — by perspective

**operator** — I can use valid multiline quoted YAML scalars containing issue references without an INV-35 false positive, while genuinely unquoted values such as `notes: close out #217` are still reported.

**code maintainer** — I can rely on focused regression coverage to distinguish multiline single-quoted and double-quoted content from genuinely unquoted `#<digit>` values.

## Success criteria

- SC-01 (operator): Valid multiline single-quoted and double-quoted YAML scalars containing `#<digit>` on a later physical line produce no INV-35 finding, while the genuinely unquoted value `notes: close out #217` still produces an INV-35 finding. The quoted cases must be demonstrated to fail against the pre-change checker before the fix passes them.
  verify: automated        evidence: integration
- SC-02 (code maintainer): The targeted integration test independently exercises multiline single-quoted content, multiline double-quoted content, and the unquoted positive control; its direct invocation exits 0 only when all three expected outcomes hold. The added multiline cases must be shown failing before the checker changes.
  verify: automated        evidence: integration

## Verification gaps

- None. The integration test kind has an active runner and covers the bounded regression-test surface.

## Constraints

- The implementation is bounded to exactly `.claude/skills/harness/bin/check-state.sh` and `tests/integration/test-check-state-plans.py`.
- DEC-174 BLOCKS team execution because `check-state.sh` and its own test are enforcement-layer work that cannot vouch for itself.
- DEC-179 SUPPLIES the declared `main-session-direct` route at plan time for the bounded files.
- DEC-225 SUPPLIES the patch lane: one product-intake run, a brief of at most 120 lines, exactly one plan task, no panel, and no goal-check.
- Preserve INV-35 detection for genuinely unquoted YAML values; do not weaken the invariant to silence the false positive.

## Out of scope

- Rewriting FEAT-57's valid quoted plan data to appease the faulty checker.
- Broad redesign of plan parsing or other state invariants.
- New YAML syntax, schema, or public checker interface.

## Approval

status: pending
approved-by:
date:
