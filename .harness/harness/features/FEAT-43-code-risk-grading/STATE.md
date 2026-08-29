# STATE

## Current

- feature: FEAT-43-code-risk-grading
- run: .harness/harness/features/FEAT-43-code-risk-grading/runs/validate-delta-c23-validator/state.yaml
- squad: validator
- status: Review — validation COMPLETE and green. Stopped at the pre-ship boundary, awaiting the
  operator's ship decision. Nothing shipped, merged, deployed or closed; the worktree stands.
- review_sha: `d2e3b5eb47c84fdfac5371b924b7ce1bb8fc37ba`
- cycles: 24 of 25 — **one left**, so a further defect means stopping, not fixing
  (`answers/Q6-…`, `answers/Q7-…`)
- briefing: `notes/ship-review-validate-final-c24.md`

All five blockers are closed. The four from the cycle-13 panel plus one the product goal-check found
afterwards. Every closure was verified by the orchestrator's own run, not accepted on report.

- **CR-01** — `code-grade.py --base 7ccfae8d --head d2e3b5eb` exits **0**: 186 gated records, zero
  blocking below-bar, 14 grade-2 (all reasoned). It exited 1 with six grade-3 production failures at
  the cycle-13 pin. Two rounds: the first closed the six named functions, my post-commit check then
  caught `test-code-grade.py:main` degraded to grade 1 because the self-grading guard enumerated
  three hardcoded production files; the second closed the class — the guard now covers every changed
  file at its own bar.
- **CR-02 + UI-01** — severity is derived from blocking-ness, not the grade literal, so every record
  that fails the build says so in text and JSON, and the guidance names the case.
- **SEC-01** — closed as a class. The first fix bound only the head, so `<pin>..<pin>` still bought
  `n_a`; QA reproduced it live. `answers/Q8-sec01-remedy-ruling.md` rejected both remedies QA ranked
  and ruled the derived range: `merge-base(default branch, review_sha)..review_sha`, measured to
  return exactly `7ccfae8d`, the base the panel reviewed. The digest now has no channel into the
  decision — the range it names no longer changes the answer.
- **ENUM-01** (found by the goal-check, after the panel passed) — this feature narrowed the reviewer
  severity ladder and updated one of four consuming templates, so a security or UI reviewer with only
  informational findings would have been hard-rejected. Fixed in both trees and guarded; the delta
  review mutated the guard three ways, including starving its discovery.
- **REQ-11 prose** — the shipped glossary and skill still taught the pre-remediation vocabulary, one
  heading naming the failing side of the bar as the thing to aim at. Four sentences corrected against
  the tool, suites green.

**Gates at the ship pin:** independent full panel PASS (`must_fix: []`, `severity_max: med`); delta
review PASS; test matrix PASS (unit 29/29, integration 32/32); `check-state.sh` exit 0; canonical
suite 957 results with one failing suite, `test-hooks-install.py (e-green) SC-14`, which this
feature's diff does not touch and which reproduces on main — backlog B8; SIMPLIFY an empty pass.

**Goal-check: 19 of 20 criteria met, none `not_met`.** SC-11 is `unproven` and is the operator's UAT;
the script is `notes/uat-sc11-c21.md` and the pre-build A/B probe does not discharge it.

`runs` is 33 against an informational 20-run budget (INV-22) — surfaced, not buried; the read is in
the briefing.

## Open Questions

- Q1 (settled): a read-only engineering assessment had no legal way to report its suite —
  `dev` + `suite: n/a` + PASS is rejected while `dev-ops` is allowed. An assessment-only member RUNS
  the suite and reports the real value. Harness wart, backlog B7.
- Q2 (ANSWERED, `answers/Q6-cycle-20-remediation-authorization.md`): remediate, do not exempt.
- Q3 (ANSWERED, `answers/Q8-sec01-remedy-ruling.md`): the derived range; the `~1` variant closes with
  the class; a non-empty allowlist/gated-set intersection is the designed steady state.
- Q4 (FOR THE OPERATOR, blocking the UAT): SC-11 says "the worst cognitive complexity in the arm" —
  arm **maxima** — while the BRIEF's probe citation reports arm **means**, on which the probe's own
  numbers fail the criterion's second half. This must be settled BEFORE the UAT runs, not after the
  numbers land.
- Q5 (FOR THE OPERATOR, non-blocking): T-01's unconditional "grade 4 or better" is unmet for 2 of
  `code_grade.py`'s 47 functions, both grade 2 and both reasoned. REQ-06 governs mergeability, not
  this clause, so the panel's acceptance does not discharge it. Accept the deviation, or route a
  follow-up.
- Q6 (FOR THE OPERATOR): the ship decision itself, and which of backlog B1–B20 survive.
