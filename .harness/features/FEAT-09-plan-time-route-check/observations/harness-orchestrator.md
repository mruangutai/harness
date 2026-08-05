# Observations — harness-orchestrator — FEAT-09-plan-time-route-check

- 2026-08-05: The do-not-touch list I was handed for the concurrent feature (12 paths) was
  derived from the OTHER feature's grilling artifact, not from its PLAN. It was incomplete:
  `run-unit-tests.sh` is edited by FEAT-08 T-05 (`FEAT-08/PLAN.md:243, :250-252`) and appears on
  no list. My lead found it by opening the peer feature's PLAN.md directly. Lesson shape: with two
  features in flight, the collision surface is the peer's PLAN `files:` union, not the grilling
  artifact's prose — the artifact predates the plan by definition.

- 2026-08-05: `run-unit-tests.sh:6` is a single-line array that nearly every task's `verify:` in
  both plans rides on as a whole-suite check. A one-line shared file with N writers and a drift
  detector that `exit 2`s is a maximally bad collision surface: the failure is not local to the
  colliding task, it reddens every other task in both features.

- 2026-08-05: `cost-report.py` is project-cumulative and both concurrent orchestrators meter into
  it. The by_agent delta is contaminated at any depth where the two flows share an `agent`+`depth`
  key — here `harness-orchestrator` depth 1 and `orchestrator` depth 0. Reporting the delta as an
  upper bound with the contamination named beat inventing an attribution.

- 2026-08-05: `check-state.sh` INV-5 scans STATE.md for any `\bT-\d+\b` and compares against THIS
  feature's PLAN task ids. Writing "FEAT-08 T-05" in an open question produced a real VIOLATION on
  a factually correct sentence. Refer to a peer feature's tasks by description, never by id.

- 2026-08-05: pm found a self-reference my dispatch missed — T-01's own paths ARE granted, so a
  route checker asking only "does anyone grant this?" passes the DEC-174 carve-out task and never
  reads its `main-session-direct` declaration. A checker that resolves routes cannot validate the
  one task that deliberately deviates from its own table unless deviation is a first-class output.
