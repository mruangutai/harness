# Observations — harness-pm — FEAT-24-config-responsibility-split

- 2026-08-18: the apply dispatch renumbered the eng digest's findings (digest F-2..F-9 became
  dispatch F-1..F-8) and the digest's own F-1 — T-06's negative-only `_note` clause, a genuine
  vacuity — fell out of the list entirely, appearing in neither the apply set nor the LEAVE set.
  Caught only by reading the digest before the dispatch prose. Lesson for the next apply run: when
  a dispatch renumbers an upstream artifact's findings, diff the two numberings before starting,
  not after.
- 2026-08-18: applying the reuse finding (call `factory_config.validate_board` from T-06's and
  T-09's verify heredocs instead of a hand-rolled dict) forced a scheduling change nobody flagged —
  the function is `_validate_board` at HEAD, made public by T-02, so both tasks needed
  `depends_on: [T-02]`. T-09 is the cross-repository kaya route, the plan's longest pole. A "reuse"
  finding on a *verify* can move the critical path; check what makes the reused symbol exist before
  accepting one.
- 2026-08-18: `check-plan-routes.py` rejected T-04 at 52 of 50 machine-field lines after the new
  clauses landed. The budget is on `verify:` plus the small scalar fields, not on `intent:`, so the
  fix was collapsing a two-suite loop into two direct captures. Worth costing verify additions in
  lines before writing them: T-06 finished at 49.
