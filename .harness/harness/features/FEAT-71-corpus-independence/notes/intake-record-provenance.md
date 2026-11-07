# Intake digest record — provenance (run 2026-11-07-01-product)

The durable fenced record at the end of `runs/2026-11-07-01-product/digest.md` was NOT appended by
the return hook. It was appended by the main session (acting as orchestrator under DEC-174),
calling `validate-digest.py`'s own `_append_record` after `validate-digest.py harness-product-lead`
accepted the lead's third return object (exit 0, `digest ok`), and the durable file re-validated
(exit 0).

Why: `.omp/extensions/harness-hooks.ts` governs main-session dispatches only when the tool is named
`task` (`ompMainTask`, lines 1146-1149 and 1326-1329). In this session the dispatch tool reached
the host under a different name, so none of the three product-lead dispatches were intercepted —
no schema-control refusal (the main session wrongly supplied `outputSchema`/`schemaMode` each
time), no claim, and no validated append. The first two returns carried equivalent content; the
recorded object is the third.

Follow-up for the operator: main-session dispatches in this host configuration bypass the hook's
`ompMainTask` path entirely.

## Run 2026-11-07-02-product (five-survivor amendment)

Same bypass. The lead's first return carried an undeclared `DIGEST.amendments` key and
`validate-digest.py harness-product-lead` refused it (exit 1) — the refusal the hook would have
issued. The lead re-issued a declared-keys-only return; it validated (exit 0) and was appended by
`validate-digest.py`'s `_append_record`, then `close-run` accepted it.

## Runs validate-validator and fix-c1-validator

Same bypass for both validator-lead dispatches. Each return validated with
`validate-digest.py harness-validator-lead` (exit 0) and was appended by its `_append_record` before
`close-run` (validate-validator BLOCKED, fix-c1-validator PASS).
