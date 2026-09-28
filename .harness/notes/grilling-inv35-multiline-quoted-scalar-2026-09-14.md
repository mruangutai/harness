# Grilling — INV-35 multiline quoted scalar false positives — 2026-09-14

## Destination

INV-35 accepts valid multiline quoted YAML scalars containing issue references while continuing to report genuinely truncating unquoted `#<digit>` values.

## Mission

mission: patch
reason: The line-local quote-state defect is known, the checker and integration-test files are bounded, and no new public interface, schema, or enforcement surface is introduced.
confirmed-by: operator

## Settled

- Should issue #1563 run through the patch lane? → Yes; the operator requested `/harness-patch` after reviewing the known cause and bounded scope.
- What behavior must remain protected? → Valid multiline quoted scalars are silent, while genuinely unquoted values such as `notes: close out #217` still produce INV-35.
- Which files bound the change? → `.claude/skills/harness/bin/check-state.sh` and `tests/integration/test-check-state-plans.py`.

## Not yet specified

- None.

## Out of scope

- Rewriting FEAT-57's valid quoted plan data to appease the faulty checker.
- Broad redesign of plan parsing or other state invariants.
- New YAML syntax, schema, or public checker interface.

## Facts I verified (so pm does not re-derive them)

- Issue #1563 records three false positives where quoted scalar content after `#1559` survives parsing.
- INV-35's implementation documents multiline quoted scalars as a known gap and tracks quote closure only within one physical line.
- Existing integration coverage includes same-line quoted and block scalars but no multiline quoted scalar case.
- DEC-174 and DEC-179 require this gate-script and gate-test change to be planned as `main-session-direct`, rather than executed by the enforcement path it changes.
- Verified against repository commit `f5ffdcf4fbfee2f2c044fcd046253df65bc40550`.
