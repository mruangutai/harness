# Observations — harness-product-lead — FEAT-33

- 2026-08-23: a dispatch told me to record the run id in `feature.json`'s `runs`, but
  `team-config.yaml:295-302` grants harness-product-lead only `runs/*-product/**`, its two expertise
  tiers and its observations log. `feature.json` is the orchestrator's (DEC-119). An instruction to
  write it is unexecutable at this tier regardless of who issues it — the guard is right and the
  dispatch is wrong. Report it up rather than attempting the write.
- 2026-08-23: "cannot be edited under DEC-174" is a false paraphrase of DEC-174 in a specific way
  worth remembering: DECISIONS.md:4715-4718 rules on the ROUTE, not on permission — the change is
  made directly, by hand, with a human reading the diff; only EXECUTING it through a team run is
  forbidden. So a main-session-direct task editing a gate script is DEC-174 being obeyed, not
  breached. Two clauses in this plan compressed that into a prohibition and became false.
- 2026-08-23: the SubagentStop digest validator refuses a lead return while a member is still in
  flight (issue #551) and says the refusal fires ONCE. A lead that ends its turn to "wait" for an
  async member is attempting to return, not waiting. Keep the turn alive with real work instead.
