# Observations — harness-pm — FEAT-17

- 2026-08-11: cycle-1 rework. A reviewer's "only the ALLOW halves break" ruling was itself
  non-discriminating on three FORBIDDEN halves: the same target-side test that falsified the allows
  also made three root-side denials true without the new rule. Lesson shape: when a review names one
  side of a paired assertion as broken by rule R, run R over the OTHER side too before accepting the
  scoping — the reviewer scoped by the symptom it noticed, not by the rule it derived.
- 2026-08-11: "import it at the same points X is already imported" is an unsafe instruction when the
  existing sites have DIFFERENT failure semantics. check-domain.sh imports harness_yaml twice: once
  under _run_domain (governed-only, safe to exit 2) and once in the shape phase (ungoverned, must
  absorb). A fail-closed instruction phrased by analogy would have blocked the main session.
- 2026-08-11: the same defect class arrived a THIRD way in T-05 — FIX 2, cycle 1, and now the
  INV-25 comparison base. Shape: a check that derives its "correct location" from the SESSION ROOT
  while the environment it exists to catch is precisely one whose root is wrong, so every correct
  item flips to the destructive branch. Also: the message named the right base while the comparison
  used the wrong one — TWO derivations of the same value in one block is where the drift lived, and
  reading either half alone looks correct. When a task states a base/location twice, make it state
  it once and say so in the intent.
