# STATE

## Current

- feature: FEAT-45-adversarial-plan-panel
- run: .harness/harness/features/FEAT-45-adversarial-plan-panel/runs/c4-validator/state.yaml
- squad: none
- status: Review

READY TO SHIP, awaiting the operator's decision. Validate is closed after FOUR panel cycles, four
main-session fix rounds and two goal-checks. Final goal-check: 14 met, 0 unmet, 3 deferred-to-live-run.
Final panel (cycle 4): PASS at `severity_max: low`, no `must_fix`.

B-1 was fixed before shipping on the operator's instruction: panel finding identities widened from a
32-bit to a 128-bit hash, `PF-` plus 32 hex, 35 characters. The security reviewer that raised it
confirms it CLOSED and that an adversarial-collision test is now unnecessary rather than merely
absent. A reverted-width probe reddens three independent assertions, so the fix is pinned against
regressing silently, and a sweep of 78 files found no code still bound to the old width. I confirmed
independently that no non-test source slices an id or matches an 8-hex pattern.

The last record inconsistency is CLOSED, not carried. T-09 was marked `done` while its own `verify:`
still asserted `test 11 -eq` against a 35-character id -- D-05 had moved with the code and the task
text had not. The main session corrected it directly at f89c90b: the verify now asserts 35 and the
intent says 32 hex / length 35. I re-ran T-09's `verify:` block verbatim from plan.yaml and it exits
0. That commit is record-only -- I diffed the pin against HEAD and every changed path is inside the
feature directory, so no source moved and the cycle-4 PASS at bdd5666 remains valid.

Cycles 10 of 10 -- fully spent, and the last one bought a real defect fix rather than a re-observation.
Runs 17 of 20. The CEO briefing is `notes/ship-review-2026-08-31.md`, rendered alongside as `.html`,
carrying 15 backlog rows B-2..B-16; anything the operator does not strike becomes an issue on ship
acceptance, and anything not listed dies silently.

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
