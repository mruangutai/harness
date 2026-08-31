# STATE

## Current

- feature: FEAT-45-adversarial-plan-panel
- run: .harness/harness/features/FEAT-45-adversarial-plan-panel/runs/2026-08-31-01-validator/state.yaml
- squad: none
- status: Review

The reviewer panel ran at the pinned `d0ebbe6` and returned FAIL, `severity_max: high`. Four
reviewers, all four having LOOKED before reporting: code FAIL, qa PASS, security PASS (examined the
full 41-file census before scoping out), ui PASS (proved zero rendered-UI files by census, then
audited the textual operator surface anyway).

THE GATING DEFECT IS THE FEATURE'S OWN SUBJECT. FEAT-45 ships a gate, and that gate fails OPEN on
exactly the input its own signed decision names as the risk. `check-state.sh:212` normalizes a panel
finding's severity with `str(item.get("severity", "")).strip().lower()` and then gates on membership
in `{high, critical, unrated}`. An absent key yields `""` and a YAML null yields `"none"`; neither is
in the set, so a finding whose rating was lost reaches the operator's signature un-vetted. DEC-206 —
written by this same change — promises the opposite verbatim: "An omitted severity fails closed... a
normalization that loses a rating therefore withholds rather than passes." The sibling default one
line up, `disposition`, correctly fails closed. I verified this at the pin with `git show`, not from
the digest.

M3 is the same defect's other half: `test-check-state.py` contains ZERO occurrences of `unrated`
while `check-state.sh` contains exactly one — the gating set itself. T-08's own intent required that
assertion and its `verify:` never greps the token, so the omission was invisible to the task's gate.

M2 is real but its cited evidence is not, and the distinction matters for how it is prioritized.
`case_inv32` genuinely is grade 1 (cyclomatic 28, cognitive 14, ABC 95.1) against a bar of 3, and it
is new in this feature. But `code-grade.py --base 1d3e5db --head d0ebbe6` exits 1 from an unhandled
RuntimeError — it crashes on `panel_findings.py` not existing at the base — and emits zero
`RESULT: FAIL` lines. The exit code is a crash, not a verdict, and it will exit 1 again after a
perfect fix. Grading the file directly shows 19 of 96 functions below the bar and 10 at grade 1,
nearly all pre-existing, so `case_inv32` matches a file-wide convention rather than standing out.
`code-grade.py` is not even present in the reviewed tree.

NONE OF THE THREE CAN BE ROUTED TO A LEAD. All land on `check-state.sh` and `test-check-state.py`,
both enumerated in DEC-174's enforcement layer, which permits planning such a change through the
harness but bars executing one. The fix is main-session-direct, after which `review_sha` re-pins and
the panel re-runs at cycle 1.

Housekeeping completed this run: five FEAT-45 artifacts had been written into the MAIN checkout
instead of the worktree, three existing nowhere else — the build-SIMPLIFY receipts for reuse,
simplification and efficiency, plus a build-side altitude receipt and a larger copy of the code
reviewer's note. All were MOVED, never deleted, and the main checkout is now clean of FEAT-45.

Cycles 6 of 10. Runs 11 of 20, informational.

## Open Questions

- Q4 from the panel, a decision rather than a defect: widening `panel_findings.py`'s 32-bit id
  (`digest[:8]`) changes every finding id, which retroactively staleness-breaks every overrule
  recorded in a signed plan.yaml. It is free today because no live plan carries a ruling, and
  monotonically more expensive from the first signature onward. Fix in this cycle, or accept the
  ratchet knowingly? Recommend fixing now. — harness-security-reviewer
- Harness defect: `validate-digest.py`'s SEC-01 code_grade binding check resolves
  `{root}/.harness/harness/features/<FEAT>/feature.json` from the session PWD rather than the
  worktree, so it unconditionally rejects every `harness-code-reviewer` yield reviewing an unmerged
  worktree feature. The reviewer's artifact was complete and its verdict was taken from there.
  — harness-validator-lead
- Harness defect: `harness-ui-reviewer`'s yield returned null data despite a complete artifact
  carrying an explicit `VERDICT: PASS`. Verdict taken from the artifact. — harness-validator-lead
- Harness defect: `code-grade.py` raises an unhandled RuntimeError on any path that is new in the
  graded diff, so it exits 1 for a reason unrelated to any grade. Anyone reading that exit code as a
  verdict will be wrong in both directions. — harness-orchestrator
- Harness defect: INV-26 is structurally red for the whole Building phase and both shapes are
  produced by the mirror's own writers. Unchanged from the build phase. — harness-orchestrator
- `plan-panel.yaml:54-62` restates the validator lead's transcription contract with no drift
  detector, flagged by TWO simplify passes and unappliable by any squad because both files resolve
  to NOBODY. Needs a manifest grant or a main-session-direct edit. — harness-eng-lead
- Advisory panel residuals, none gating: M5 (SC-03's second falsification direction unbound at
  `test-plan-panel.py:161-181`), M6 (`goalcheck` transcription ambiguity, fails closed and loudly on
  SC-16's first live `/harness-plan`), M7 (the withhold message states the fact but not the remedy).
- Five pre-existing plan-phase artifacts fail DEC-154/DEC-156 contracts and predate this feature's
  build; not corrected, since rewriting another run's record would falsify it. — harness-orchestrator
