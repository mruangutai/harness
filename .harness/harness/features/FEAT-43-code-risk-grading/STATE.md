# STATE

## Current

- feature: FEAT-43-code-risk-grading
- run: .harness/harness/features/FEAT-43-code-risk-grading/runs/validate-delta-c25-validator/state.yaml
- squad: validator
- status: Review — validation COMPLETE and green. Stopped at the pre-ship boundary for the
  operator's ship decision. Nothing shipped, merged, deployed or closed; the worktree stands.
- review_sha: `e12d53b16e49e7c4d9332c5e290e6bdbc806251f`
- cycles: **25 of 25 — exhausted.** No repair capacity remains; anything found now is a backlog row
  or a new feature, not a fix.
- briefing: `notes/ship-review-validate-final-c25.md` (supersedes the c24 briefing)

Six defects were closed across cycles 14–25, each verified by the orchestrator's own run rather than
accepted on report.

- **CR-01** — the tool rejected its own change (exit 1, six grade-3 production functions). Now
  **exit 0** over `7ccfae8d..e12d53b1`: 195 gated records, zero blocking, 12 grade-2 all reasoned.
  Took two rounds: the first closed the six named functions, and my post-commit check then caught
  `test-code-grade.py:main` at grade 1, invisible because the self-grading guard enumerated three
  hardcoded production files. The second closed the class.
- **CR-02 + UI-01** — severity derived from blocking-ness rather than the grade literal; one spelling
  across tool, JSON, guidance and enum.
- **SEC-01** — closed as a class per `answers/Q8-sec01-remedy-ruling.md`. The first fix bound only the
  head, so `<pin>..<pin>` still bought `n_a`. Both remedies QA ranked were refused: `base == head`
  blacklists one shape that `~1` walks around, and the schema change was unnecessary because
  `git merge-base main <pin>` already returns the reviewed base. The decision now diffs a
  repository-derived range, so **the range a digest names no longer changes the answer**.
- **ENUM-01** — found by the goal-check *after* the panel passed: the feature narrowed the reviewer
  severity ladder and updated one of four consuming templates. Fixed in both trees and guarded.
- **REQ-11 prose** — the shipped glossary and skill still taught the pre-remediation vocabulary, one
  heading naming the failing side of the bar as the target. Four sentences corrected.
- **T-01** — the operator refused the deviation (`answers/Q9-sc11-maxima-and-t01-no-exemption.md`
  §2). `_body_hashes.collect` and `gated_set` reached grade 4 behind six helpers and **both allowlist
  entries were deleted rather than re-pointed**. The engine is 53 functions, zero below grade 4.
  Behaviour proven unchanged by three mutations from two agents at two seams.

**Gates at the ship pin:** full independent panel PASS at `17106762`; two delta reviews PASS
(`6752597`, `e12d53b1`), both `must_fix: []`; test matrix PASS (unit 29/29, integration 32/32);
`check-state.sh` exit 0; canonical suite 957 results with one failing suite, `test-hooks-install.py
(e-green) SC-14`, untouched by this diff and reproducing on main (B8); SIMPLIFY an empty pass.

**Goal-check: 19 of 20 met, none `not_met`.** SC-11 is `unproven` and is the operator's UAT.
`notes/uat-sc11-c21.md` is ready, unexecuted, and its arithmetic is the operator's MAXIMA ruling,
stamped SETTLED before any number was drawn.

`runs` is 36 against an informational 20-run budget (INV-22) — surfaced in the briefing with the read.

## Open Questions

- Q1 (settled): a read-only engineering assessment had no legal way to report its suite; it RUNS the
  suite and reports the real value. Harness wart, backlog B7.
- Q2 (ANSWERED, `answers/Q6-…`): remediate, do not exempt.
- Q3 (ANSWERED, `answers/Q8-…`): the repository-derived range closes SEC-01 as a class.
- Q4 (ANSWERED, `answers/Q9-…` §1): SC-11 is decided on arm **MAXIMA**. Recorded before the run.
- Q5 (ANSWERED, `answers/Q9-…` §2): T-01's deviation refused and now fixed at the root.
- Q6 (FOR THE OPERATOR, non-blocking): **B21** — `_strip_docstring` (D-03's "excluding the
  docstring", underwriting D-02) and `_qualname`'s prefix join have no test. Proven untested by
  mutation: gutting either leaves the full suite and the self-grade green. Correct by inspection and
  pre-dating this change — they were inline and equally untested for 24 cycles and two panels;
  decomposition made them nameable. Ship with them recorded, or hold.
- Q7 (FOR THE OPERATOR): run the SC-11 UAT; then the ship decision and which of B1–B22 survive.
