# STATE

## Current

- feature: FEAT-45-adversarial-plan-panel
- run: .harness/harness/features/FEAT-45-adversarial-plan-panel/runs/2026-08-31-02-validator/state.yaml
- squad: none
- status: Review

VALIDATE COMPLETE. Panel cycle 1 returns PASS at `severity_max: med`, which under
`gates.review: advisory_unless_high` does not gate. All four reviewers PASS and all four LOOKED
before reporting. No `must_fix` outstanding.

All three cycle-0 findings are CLOSED, each corroborated by the panel at source and independently
verified by me rather than accepted on report. M1: `check-state.sh:213` now gates on an allow-list,
so an absent key and a YAML null both fail closed; I proved the new fixture RED-capable by reverting
that one line and watching it fail, then restored the file byte-identical to the pin. M3: one fixture
covers `unrated`, absent and null. M2: `case_inv32` moved from grade 1 to grade 4 (cyclomatic 28->2,
ABC 95.1->11.0), with all eleven inv32 helpers at grade 3 or better.

The fix inverted a deny-list into an allow-list, which is a semantic widening, so the panel hunted
what the FIX introduced rather than only confirming what it closed. It gates nothing spuriously: the
ui census over 10 sources found the allow-list's complement is exactly the old deny-list
`{high, critical, unrated}`, and security fired 17 hostile severity values, all of which gated.

ONE RECORD DEFECT FOUND AND FIXED. `feature.json` recorded `review_sha`
`c745d3a61f1049e5325854618511544b10f68753`, which resolves to NO object — a real 7-char prefix with
a fabricated tail. Three reviewers hit it independently. The true commit is
`c745d3a07c2accd8395c9df7a25d911d40dc2c09` and feature.json now carries it. My own verification had
used the prefix, so it read the correct tree throughout and its conclusions are unaffected. The
cycle-0 pin was genuine, so this was a one-off transcription rather than a pattern.

Cycles 6 of 10, unchanged this cycle — the panel passed with no rework owed. Runs 12 of 20.

## Open Questions

- SHIP-DECISION MATERIAL, and M4 is a RATCHET: widening `panel_findings.py`'s 32-bit id
  (`digest[:8]`) changes every finding id, retroactively staleness-breaking every overrule recorded
  in a signed plan.yaml. Free today because no live plan carries a PF- ruling, and monotonically more
  expensive from the first signature onward. Recommend fixing before ship. — harness-security-reviewer
- Advisory, non-gating, all assessed by the cycle-1 panel: M5 (SC-03's second falsification direction
  unbound at `test-plan-panel.py:161-181`), M6 (`goalcheck` transcription ambiguity — fails closed and
  loudly on SC-16's first live `/harness-plan`), M7 (the withhold message states the fact but not the
  remedy). Each needs a keep-or-strike ruling at the ship gate; anything not listed there dies silently.
- Only 3 of `test-plan-panel.py`'s 24 checks bind executable behaviour, so "24/24 green" is assurance
  about doctrine WORDING. The INV-32 cases in `test-check-state.py` are materially stronger — real
  subprocesses asserting on stdout — so the part just fixed IS the genuinely runtime-tested part.
  No reviewer could exercise the panel end to end; SC-16's first live `/harness-plan` remains the only
  thing that tests the assembled feature. — harness-validator-lead
- HARNESS DEFECT, recurring and now twice in two cycles against the same persona:
  `harness-code-reviewer` could not land a structured yield, because `validate-digest.py`'s
  code_grade<->review_sha binding check unconditionally resolves `feature.json` at the MAIN checkout
  path, which does not exist for a worktree-only feature. Both verdicts were recovered from the
  artifacts. A reviewer whose return is structurally unlandable is one careless lead away from being
  recorded as BLOCKED. — harness-validator-lead
- HARNESS DEFECT: `code-grade.py` raises an unhandled RuntimeError on any path NEW in the graded diff,
  exiting 1 with zero `RESULT: FAIL` lines. It reddens a clean range and would mask a real grade
  failure behind a crash. This produced cycle-0's M2 evidence. — harness-orchestrator
- HARNESS DEFECT: agents repeatedly write feature artifacts into the MAIN checkout rather than their
  worktree — six occurrences across build and validate, three of which existed nowhere else. All were
  moved, never deleted, and the main checkout is clean. The root cause, agents resolving the project
  root to the main checkout, is not fixed. — harness-orchestrator
- HARNESS DEFECT: `harness-ui-reviewer` returned a null structured yield in cycle 0 despite a complete
  artifact carrying `VERDICT: PASS`. Same empty-return shape seen twice in the build phase.
  — harness-validator-lead
- INV-26 remains structurally red for this feature; both shapes are produced by the mirror's own
  writers rather than by the plan. Unchanged since build. — harness-orchestrator
- `plan-panel.yaml:54-62` restates the validator lead's transcription contract with no drift detector.
  Flagged by two simplify passes, unappliable by any squad because both files resolve to NOBODY.
  — harness-eng-lead
- Five pre-existing plan-phase artifacts fail DEC-154/DEC-156 contracts and predate this build. Not
  corrected — rewriting another run's record would falsify it. — harness-orchestrator
