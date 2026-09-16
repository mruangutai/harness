# BRIEF — BUG-1563-inv35-multiline-quoted-scalar

## Problem

INV-35 tracks quote state only within each physical line, so operators reviewing otherwise valid plans receive false findings when a single-quoted or double-quoted YAML scalar continues across lines and contains `#<digit>` on a later line. Issue #1563 measured three such false positives, adding noise at signature time and making genuine truncation findings easier to skim past.

## Done when — by perspective

**operator** — I can use valid multiline quoted YAML scalars containing issue references without an INV-35 false positive, while genuinely unquoted values such as `notes: close out #217` are still reported.

**code maintainer** — I can rely on focused integration and unit-kind behavioral coverage to distinguish multiline single-quoted and double-quoted content from genuinely unquoted `#<digit>` values.

## Success criteria

- SC-01 (operator): Valid multiline single-quoted and double-quoted YAML scalars containing `#<digit>` on a later physical line produce no INV-35 finding, while the genuinely unquoted value `notes: close out #217` still produces an INV-35 finding. The quoted cases must be demonstrated to fail against the pre-change checker before the fix passes them.
  verify: automated        evidence: integration
- SC-02 (code maintainer): The targeted integration test independently exercises multiline single-quoted content, multiline double-quoted content, and the unquoted positive control; its direct invocation exits 0 only when all three expected outcomes hold. The added multiline cases must be shown failing before the checker changes.
  verify: automated        evidence: integration
- SC-03 (code maintainer): A focused test discovered by the active unit test kind directly exercises the real checker against multiline single-quoted content, multiline double-quoted content, and the unquoted `notes: close out #217` positive control; its direct invocation exits 0 only when all three expected INV-35 outcomes hold. The focused test must be demonstrated failing against the pre-change checker before it passes against the completed checker.
  verify: automated        evidence: unit

## Verification gaps

- None. The integration and unit test kinds both have active runners; SC-03 supplies the matrix-required unit-kind behavioral evidence without widening the delivered checker behavior.

## Constraints

- The delivered checker behavior and integration regression coverage remain bounded to `.claude/skills/harness/bin/check-state.sh` and `tests/integration/test-check-state-plans.py`; this upgrade adds only `tests/unit/test-check-state-inv35.py`.
- DEC-174 BLOCKS team execution because `check-state.sh` and each test that vouches for it are enforcement-layer work that cannot vouch for itself.
- DEC-179 SUPPLIES the declared `main-session-direct` route at plan time for all three bounded files.
- DEC-217 SUPPLIES the hard bugfix matrix requirement for unit-kind coverage when runtime checker code changes.
- Preserve INV-35 detection for genuinely unquoted YAML values; do not weaken the invariant to silence the false positive.

## Out of scope

- Rewriting FEAT-57's valid quoted plan data to appease the faulty checker.
- Broad redesign of plan parsing or other state invariants.
- New YAML syntax, schema, or public checker interface.
- Further production changes, integration-test changes, or broader INV-35 coverage beyond the three matrix-closing cases.

## Approval

status: approved
