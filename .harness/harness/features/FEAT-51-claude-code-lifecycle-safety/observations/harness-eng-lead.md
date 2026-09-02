# Observations — harness-eng-lead — FEAT-51-claude-code-lifecycle-safety

- 2026-09-01: T-08's discrimination probe B surfaced that a content guard over prose can be
  silently weakened by REDUNDANCY in the guarded text, not by any defect in the guard. DEC-210
  states the plan.yaml/plan-merge.py fact twice (DECISIONS.md :6519-6520 and :6539), so
  `test_dec_210_entry_states_the_bash_write_route_for_plan_yaml` stayed green when one of the two
  statements was broken; only breaking both turned it red. A dispatch asking to "prove the guard
  discriminates" should therefore ask for the OCCURRENCE COUNT of each guarded literal in the live
  text before the probe, not only for the probe's red output — n>1 means the guard reddens on a
  full deletion but not on a single-site regression, and nothing in the green reports that.
- 2026-09-01: probe D (heading removed) reddened both region tests but left the index-row test
  green, correctly — the row test reads REAL_INDEX independently. Worth stating explicitly in the
  dispatch which probes each test is EXPECTED to survive, so an unreddened test is not read as a
  vacuous one by the assessor.
- 2026-09-01: I clobbered a completed run's `state.yaml` because my `glob` of
  `.harness/harness/features/<FEAT>/runs/**` returned "No files found" — `runs/` is gitignored in
  this repo and the glob tool filters on gitignore BY DEFAULT. I read an occupied directory as an
  empty one and seeded a new run over `2026-09-01-01-eng`, which held T-04. `check-domain` refused
  the `digest.md` replacement (that guard works); `state.yaml` has no equivalent guard, so the T-04
  checkpoint was lost. Before opening a run dir, glob with `gitignore: false` — a run-dir listing
  is exactly the case where the default filter lies. The naming convention `<date>-<seq>-eng` also
  makes collision the DEFAULT outcome on a same-day second run, not an unlucky one.
