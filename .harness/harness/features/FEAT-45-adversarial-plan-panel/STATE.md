# STATE

## Current

- feature: FEAT-45-adversarial-plan-panel
- run: .harness/harness/features/FEAT-45-adversarial-plan-panel/runs/2026-08-31-1-product/state.yaml
- squad: none
- status: Review

VALIDATE CLOSED, awaiting the operator's ship decision. Final goal-check at d78f393: **14 met, 0
unmet, 3 deferred-to-live-run**. Both criteria open at the first goal-check are closed — SC-05, which
was unmet-behaviour, and SC-03, which was unmet-unproven.

Four panel cycles and three main-session fix rounds. The panel earned its keep: at cycle 0 it caught
that the gate this feature SHIPS failed open on exactly the input DEC-206 names as the risk, so a
finding whose severity was lost would have reached signature un-vetted while the decision written in
the same change promised the opposite. Cycle 2 caught two bypasses and a deadlock in the fix code
itself. Separately, the F4 fix revealed the test gate had been collecting ZERO tests at one pin, which
retroactively invalidated every green number claimed there.

The one open finding, V1, is CONDITIONALLY CLOSED on the operator's ruling, and the diagnosis was
measured rather than inferred. `gateRoot()` derives from the extension file's own location, so the
executing validator is always `<main checkout>/.agents/skills/harness/bin/validate-digest.py` — 1525
lines, with zero occurrences of `_hook_feature_dir` or `inflight_registry.feature_root`. The branch's
fixed copy is 1643 lines and never runs for a subagent. The fix is therefore correct-by-inspection but
UNVERIFIABLE PRE-MERGE by construction, and the first post-merge reviewer dispatch is a named required
verification step. I also proved `inflight_registry.feature_root` resolves this feature correctly,
eliminating the competing hypothesis, so no fix round was spent guessing.

The CEO briefing is `notes/ship-review-2026-08-31.md`, rendered alongside as `.html`, assembled from
the run digests on disk with no report round spawned. It carries 16 proposed backlog rows; B-1, the
32-bit finding-id ratchet, is the only one worth deciding before signature rather than after.

Cycles 9 of 10 — cycle 10 preserved on the operator's instruction rather than spent re-observing code
that cannot execute. Runs 16 of 20, informational; three of them found defects that would otherwise
have shipped.

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
