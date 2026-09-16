# Efficiency assessment — BUG-1563 INV-35

## BLUF

One actionable efficiency finding: every physical continuation line of a multiline quoted scalar performs string trimming and indentation calculation before the new quote-continuation fast path immediately skips the line.

## Inspected files

- `.claude/skills/harness/bin/check-state.sh`
- `tests/integration/test-check-state-plans.py`
- `tests/unit/test-check-state-inv35.py`
- `tests/integration/check_state_support.py` (directly called helper)

No product, test, or helper file was mutated. No validation command was run.

## Finding EFF-01

- **File / line:** `.claude/skills/harness/bin/check-state.sh:251-256`
- **Summary:** Quote-continuation handling calculates `_stripped` and `_indent` before immediately continuing, although it needs only `_line` and `_quoted_scalar`.
- **Concrete cost:** For each continuation physical line of every multiline quoted scalar scanned at harness entry, the checker allocates a stripped string and performs `strip()` plus `lstrip()` scans solely to discard their results; this repeats for every such line across every `plan.yaml`.
- **Exact lower-cost alternative:** Move the `_quoted_scalar is not None` block directly after the `for _lineno, _line` header, before lines 251-252; leave its close detection and unconditional `continue` unchanged, then calculate `_stripped` and `_indent` only for ordinary or block-scalar processing.
- **Behavior preservation:** The current continuation branch neither reads `_stripped` nor `_indent` and always continues after updating quote state, so the reordered branch preserves its output and state transitions.

The integration additions use the established fixture helper once per independently executed case. The focused unit-kind test's three checker invocations are the required independent behavioral outcomes and are not reported as redundant coverage.
