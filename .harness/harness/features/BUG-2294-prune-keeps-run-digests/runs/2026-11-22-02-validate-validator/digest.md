# Validation c1 — BUG-2294

FAIL at review_sha `70981edd6f9f110965a0148b4490ed2673d262dc` (base `c1724230c4d931ad46d433c8ba93df8cf312f898`): the unit matrix and genuine fail-first evidence pass, but SEC-01 introduces deletion through intermediate run symlinks. Severity maximum: med. Route T-01 to Main (main-session-direct); no dev was spawned.

## Ranked must-fix

1. **SEC-01 — substance / med / security-reviewer / T-01:** prevent run-symlink traversal before UI deletion and add kept-run/external-target regressions. `runs/alias -> kept-run` makes `rmtree(alias/ui)` remove protected UI; an external destination similarly escapes the feature. Base rejected the leaf run symlink. This is a static trace, not an executed exploit; unusual local filesystem access limits severity but does not restore the kept-UI guarantee. See `../../notes/review-harness-security-reviewer-c1.md`.

## Assessment and reconciliation

Code's clean review explicitly covers the supported directory layout; QA's fixtures contain real directories only. Neither contradicts the security trace for an intermediate symlink. Retain SEC-01 unchanged; green tests cannot discharge an unrepresented destructive path. No duplicate findings, dismissed findings, form findings, or open questions. Fix containment first, then regressions; preserve unchanged selection/refusal behavior.

QA actually executed the pinned verify (20 PASS, zero FAIL) and unit-kind runner (63 files, exit 0, 22.8s). Independent base reproduction yielded seven assertion failures, not import/setup errors. SC-01 fail-first: record-byte preservation, repeat and explicit-keep assertions fail on base. SC-02 fail-first: all ten hash-bound digests disappear and post-prune INV-7 fails while clean-before and empty-keep preconditions pass. See `../../notes/review-harness-qa-c1.md` and `../../notes/red-first-T-01.md`. Accepted INV-7 scope is not reopened. Required unit kind is satisfied; symlink coverage remains missing.

PM grades operator **pass** (SC-01/SC-03) and code maintainer **pass** (SC-02/SC-03); DEC-238 amend disposition met. Preserve those reported grades, but operator assurance is insufficient for ship-readiness in light of SEC-01. SC-03 inspection passes. See `../../notes/research-BUG-2294-prune-keeps-run-digests-goalcheck-validate-c1.md` and `../../notes/review-harness-code-reviewer-c1.md`.

All five notes exist. UI's measured 15-file census scopes out rendered/interactive UI; accessibility/themes were not visually passed (`../../notes/review-harness-ui-reviewer-c1.md`). Code/security/PM assurance is inspection-based, not adversarial execution. Open questions: none.

```yaml
VERDICT: FAIL
DIGEST:
  headline: '70981edd6f9f110965a0148b4490ed2673d262dc: matrix and fail-first pass;
    SEC-01 run-symlink deletion escape blocks ship.'
  open_questions: []
  files_touched: []
  expertise_update: []
  team: validate
  steps_run: 5
  cycles_used: 0
  members:
  - step: qa
    persona: harness-qa
    verdict: PASS
    headline: Unit matrix passes; genuine base failures independently reproduced.
    files_touched: []
  - step: code
    persona: harness-code-reviewer
    verdict: PASS
    headline: "SC-01\u201303 compliant in supported directory layout; Python risk\
      \ grade passes."
    files_touched: []
  - step: security
    persona: harness-security-reviewer
    verdict: FAIL
    headline: SEC-01 intermediate run symlinks escape deletion containment.
    files_touched: []
  - step: ui
    persona: harness-ui-reviewer
    verdict: PASS
    headline: Measured census contains no rendered UI; scoped out.
    files_touched: []
  - step: goalcheck
    persona: harness-pm
    verdict: PASS
    headline: Both perspectives pass; DEC-238 disposition met.
    files_touched: []
  must_fix:
  - 'SEC-01 / substance / med / security-reviewer / T-01: prevent run-symlink traversal
    before UI deletion; add kept-run and outside-feature symlink regressions proving
    destination bytes survive. Route to Main (main-session-direct), not an engineering
    persona.'
  branch: none
  escalations: []
  adequacy_notes:
  - Reviewed c1724230c4d931ad46d433c8ba93df8cf312f898..70981edd6f9f110965a0148b4490ed2673d262dc;
    all five validate.yaml c1 notes exist.
  - 'QA executed literal verify: 20 PASS/0 FAIL; required unit-kind runner passed
    63 files in 22.8 seconds.'
  - 'SC-01 fail_first: independent exact-base reproduction failed record preservation,
    repeat and explicit-keep assertions. SC-02 fail_first: all ten digests lost and
    post-prune INV-7 failed while clean-before and empty-keep preconditions passed.
    Seven assertion failures, no setup/import errors. Evidence: notes/review-harness-qa-c1.md
    and notes/red-first-T-01.md.'
  - 'PM perspective grades preserved: operator pass (SC-01/SC-03), code maintainer
    pass (SC-02/SC-03). These do not override SEC-01.'
  - 'Reconciliation: clean code review covers supported directories; QA fixtures use
    real directories. Neither disproves security''s intermediate-symlink counterexample.
    Retain med severity unchanged. No dismissed or duplicate findings.'
  - Security finding is static inference, not executed. UI scope-out uses measured
    15-file census. Settled --only INV-7 scope remains accepted. No scope change or
    dev spawn.
  sc_status:
  - id: SC-01
    verdict: partial
    method: automated and security inspection
    evidence: Existing fixtures pass with genuine fail-first, but SEC-01 demonstrates
      kept-UI deletion through run symlinks.
  - id: SC-02
    verdict: met
    method: automated
    evidence: Exact base loses ten hash-bound digests and fails post-prune INV-7;
      pin passes.
  - id: SC-03
    verdict: met
    method: inspection
    evidence: Code/security confirm unchanged selectors, refusals and ship invocations
      at pin.
  - id: DEC-238
    verdict: met
    method: inspection
    evidence: PM confirms bounded UI-only amendment and coupled index update.
  needs_approval: false
  severity_max: med
  matrix_ok: true
  coverage_gaps:
  - Intermediate run symlinks to kept runs and external directories are not covered;
    current suite cannot detect SEC-01.
  findings:
  - kind: substance
    scope: none
    severity: med
    reader: security-reviewer
    summary: 'SEC-01 / T-01 / SC-01: intermediate run symlinks bypass UI deletion
      containment.'
    why: Run selection accepts directory symlinks; rmtree(alias/ui) follows the intermediate
      link and can delete kept or outside-feature UI. Base passed the leaf alias itself,
      which rmtree rejects. Static inference, not executed; unusual local filesystem
      access limits severity but does not preserve kept UI.
  readers:
  - reader: qa
    status: ran
    persona: harness-qa
    reason: none
  - reader: code
    status: ran
    persona: harness-code-reviewer
    reason: none
  - reader: security
    status: ran
    persona: harness-security-reviewer
    reason: none
  - reader: ui
    status: ran
    persona: harness-ui-reviewer
    reason: none
  - reader: goalcheck
    status: ran
    persona: harness-pm
    reason: none
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2294-prune-keeps-run-digests/.harness/harness/features/BUG-2294-prune-keeps-run-digests/runs/2026-11-22-02-validate-validator/digest.md
```
