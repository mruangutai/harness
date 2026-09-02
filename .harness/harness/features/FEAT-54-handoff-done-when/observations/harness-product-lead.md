# Observations — harness-product-lead — FEAT-54-handoff-done-when

- 2026-09-02: my pre-dispatch grep flagged plan.yaml:31-34 as a dangling reference to a struck
  T-06 case (g). Wrong on two counts: (1) the text is `panel.findings[1]`'s verbatim summary, not a
  `risks:` entry (plan.yaml has no `risks:` key); (2) T-01 and T-06 BOTH label sub-cases (a)..(h),
  and the resolve-pairs case at :201 is T-01's while T-06's (g) at :464-467 is still the corpus scan
  it describes. A grep hit on a sub-case letter is ambiguous across tasks in this plan; the pm
  overturned it with a source read, which is what O-04's "require evidence, not deference" bought.
- 2026-09-02: writing send-back criteria before dispatch (P-05) paid — criterion 7 (anchors must
  name file:line read at HEAD, not "spot-checked") is exactly the section that would have been
  waved through, and the pm returned 16 anchors each with a read location.
