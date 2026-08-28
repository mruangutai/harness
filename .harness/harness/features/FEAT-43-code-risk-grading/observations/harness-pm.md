# Observations - harness-pm

- 2026-08-27: FEAT-43. check-plan-routes.py unions the granting agents across a task's files (line 195, granted_agents.update) and never compares execution_agent against them, so a task spanning two disjoint domains prints OK naming both agents while neither can write all its files. Third instance of the report-without-enforce family.
- 2026-08-27: FEAT-43. FEAT-40's plan.yaml lanes row claims .harness/harness.json resolves to NOBODY; measured at 6e4a273 it resolves to harness-dev-ops, whose domain lists the path literally. A lanes row is a recorded baseline and rots like any other.
- 2026-08-27: FEAT-43 S1c1 send-back. A REQ traced by exactly one task that CREATES a module and by
  nothing that IMPORTS it is an undelivered REQ; depends_on is not a call site. Grep the module's
  filename across the plan and check whether any occurrence is outside its own creating task.
- 2026-08-27: an SC asserting a library reads config keys cannot fail when nothing calls the
  library. The discriminating pair is same-input-different-config: rejected under one policy value,
  accepted under another. A single rejection is satisfiable by a hardcoded rule.
