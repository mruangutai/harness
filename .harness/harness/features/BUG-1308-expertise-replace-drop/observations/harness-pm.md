# Observations - harness-pm

- 2026-09-05: BUG-1308 — check-domain denies harness-pm any notes/ file that is not research-*.md, so a plan proposal handed to plan-merge.py must be named notes/research-<something>.md; plan-merge parses YAML regardless of the .md extension.
- 2026-09-05: BUG-1308 — plan-merge.py apply bootstrapped an absent plan.yaml and spliced approval status pending itself; the proposal carried no approval or panel key and no station, and set-feature-station wrote status afterwards.
- 2026-09-05: BUG-1308 plan goal-check — a task intent said "assert set equality, not containment" while the criterion it serves (SC-09) and a decision (D-10) make the two sets deliberately unequal; the criterion's own disjunctive wording was correct and the dispatch prose was not. Grading the intent prose against the criterion, not just against the issue, is what caught it.
- 2026-09-05: BUG-1308 — a REQ can map cleanly to an issue clause and still have zero criteria: REQ-07 carried "concurrent" from the issue body, and every SC touching it graded only add-only exit codes. Map clause->REQ and clause->SC separately; the first mapping hides the second's hole.
- 2026-09-05: BUG-1308 plan fix c1. A criterion phrased as a set predicate ("set equality") went
  unsatisfiable because the two sets were defined on different sides of a decision; the repair that
  works is to write ONE sentence and paste it verbatim into all four surfaces (SC, decision because,
  contract task intent, test case intent), then verify with a whitespace-normalised substring match
  over safe_load'ed values — line wrapping differs, wording must not.
- 2026-09-05: plan-merge.py amend on a list field needs BOTH --yaml-value and --expect-sha256, and
  --show without --yaml-value errors out telling you so; the sha shown by --yaml-value --show is the
  one it wants.
- 2026-09-05: BUG-1308 c1 re-grade — a cycle-0 "the four places must agree" finding is closed fastest by grepping the literal sentence in each place and diffing the strings, not by reading the repair note; all four carried it byte-identical. Anchor "case 8" in the integration suite is a DOCSTRING label (case_cap_drift_detector), so a grep for `def case8` returns nothing and reads as a rotted anchor when it is not.
- 2026-09-05: BUG-1308 panel c1 transcription — wrote panel findings' summary as double-quoted SINGLE-LINE scalars in the set-panel value file rather than folded '>-'; re-derived every PF- id from the LOADED plan.yaml afterwards (7/7 ID_OK), which catches a fold that reflows differently from the digest text.
