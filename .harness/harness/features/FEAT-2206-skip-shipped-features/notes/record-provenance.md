# Run record provenance

Main-session lead dispatches in this host bypass the Harness return hook (#2195): no claim, no
schema refusal, no validated append, no token stamp. Each lead return in this feature is therefore
validated by the main session with `validate-digest.py <persona>` (exit 0, no `HARNESS_MISSION`
override) and appended with that module's own `_append_record` before `close-run`.

- `2026-11-08-01-product` — harness-product-lead, PASS; validated, appended, closed.
