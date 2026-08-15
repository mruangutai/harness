# Observations — harness-pm — FEAT-10-software-factory

- 2026-08-08: plan.yaml `decisions:` entries use PLAIN scalars for `choice:`/`because:`, so any
  ": " inside the text is a YAML scanner error ("mapping values are not allowed in this context").
  Amending D-01 broke the parse twice on phrases like "not optional at the tool: factory_claim".
  Use " - " instead. Task `intent:` blocks are literal `|` and are unaffected, which is why the
  trap only appears in the decisions block.
- 2026-08-08: a "claims one of the root tasks, never the blocked one" criterion is
  non-discriminating when candidates are sorted by issue number and a root sorts first — a
  blocker-ignoring tool passes it. The discriminating fixture makes the LOWEST-numbered candidate
  the blocked one and asserts the issue number create_ref was called for, not the exit status.
