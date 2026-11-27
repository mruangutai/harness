# Validate c2: FEAT-2542 at 2ec0916f8bf6b5d10607e36486ccbeb959ca4822 (base 2e7a2c77)

**PASS. Fix round c1 closes both c1 gates. must_fix is empty and severity_max is low.**
- **Null/empty-feature fail-open (c1 must_fix 1):** closed and pinned. Mutant n1 deletes the check and fails 14 rows; mutant n2 (`is not None`) fails the 6 empty-feature rows. The omitted feature still proceeds as `"legacy"` at both base and the pin.
- **Printed commands (c1 ESC-1/OQ-1):** closed. The ui-reviewer copied 30 commands verbatim across 22 refusals, with roots containing spaces and apostrophes, and every one reached its intended registry.

Four low advisories remain (ranked below). Two of them are unpinned branches that are correct at the pin.

## Gates
QA measured these on this host (macOS arm64), not on CI:
- T-01 verify exits 0 (dispatch-guard 426/426). T-02 verify exits 0.
- unit: 68/68 files. integration: 95/95 files. Runner exit 0 for both.
- Receipts are at `runs/r-20261126-3-validate-validator/qa/manifest-{unit,integration}.json`, and `tested_commit` is the pin.
- `inflight_registry.py` is byte-identical to base (exit 0).
- The seam `git diff --quiet b27cbcc6 2ec0916f -- dispatch-guard.py test-dispatch-guard.py` exits 0. QA and pm each measured it.
- The Pin run (fix round c1) block shows tested_sha b27cbcc6 and pin_run_exit 0.

Base-red: running the base guard against the pin's tests passes 316 of 426. The 110 failing checks equal predicted_red as a set.

Mutants:
- Mutant g, which survived c1, now goes red on `c43/not-found/run-preflight:cause`. That closes the OQ-4 ordering gap.
- Mutants n1, n2 and n4 (n4 refuses "legacy") go red.
- n3 and n5 survive (advisories 1 and 2).

## Advisories (ranked; non-gating; all T-01 unless noted)
1. **Q2-2 (qa), substance, low.** Nothing tests the `isinstance(str)` leg of the feature check. Mutant n5 (`if not feature:`) passes 426/426, and under it an exploit dispatch with feature `123` exits 0 and claims in the declared feature. That is the D-01 fail-open class. The pin refuses this shape as `unreadable`.
   - I rank it first because its mutant fails open (P-13).
   - It is not a must_fix: the ruling named fixtures for null and `""` only ("the only other shape the check names").
2. **Q2-1 (qa) = code-reviewer low = pm A-4, substance, low.** These are one finding: nothing tests that the malformed-feature check runs before the persona check (mutant n3 passes 426/426).
   - **Where pm and QA disagree, I go with QA's measurement.** pm reasoned that swapping the two checks would make `shlex.quote(None)` raise, so the hook would fail open. QA ran mutant n3 and measured exit 2 with a `(persona-mismatch)` refusal that prints the wrong command.
   - So under the mutant the operator gets the wrong diagnosis, but the guard still refuses (fail-closed). pm's fail-open characterization is dismissed.
3. **Security, substance, low.** `shlex.quote` keeps each value as one shell argument, but a value containing a newline still splits the printed command across physical lines (dispatch-guard.py:779-781). This needs someone who can edit the registry or controls the checkout path. The guard still exits 2 and nothing runs automatically. This is outside ruling rules 1-4, which required only shlex.quote.
4. **pm A-3, form, low, T-02.** DEC-258's clause reads "names no feature (null or empty)". The ruled wording was "not a non-empty string", and the code also refuses non-str shapes such as `42`. The record describes less than the code refuses, but nothing it says is false. It is a one-phrase edit when T-02 next touches DECISIONS.md.

If round 2 is spent for another reason, two rows would close advisories 1 and 2 in test-dispatch-guard.py: a non-str feature row, and a null-feature row combined with a persona mismatch. Neither row on its own justifies spending a round.

## SC status
- SC-02: partial → **met**.
- SC-04: **met**. The clause has landed, the index shows no drift, and 25 anchors pass with 0 failures.
- SC-03 seam: **met** (exit 0).
- SC-01 and SC-05 stand on their c1 evidence.
- The T-01.intent amendment was recorded through record-amendments and matches rules 1-4 and (i′).

## Out of scope by ruling (not reopened)
OQ-3, F-4, case-41, sentinel object. No reader raised a new defect in these areas.

```yaml
VERDICT: PASS
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2542-dispatcher-placement/.harness/harness/features/FEAT-2542-dispatcher-placement/runs/r-20261126-3-validate-validator/digest.md
DIGEST:
  headline: 'FEAT-2542 passes at 2ec0916f and is ship-ready on the advisory_unless_high
    gate. Fix c1 closes the null/empty-feature fail-open: mutants n1 and n2 now go
    red, and the omitted feature still proceeds as legacy. Every printed repair command
    copy-runs to the right registry, including roots with spaces. Mutant g is now
    killed. Four low advisories remain; two of them are correct-but-unpinned branches
    (n5 fails open under mutation, n3 fails closed).'
  team: validate
  steps_run: 5
  cycles_used: 0
  branch: none
  members:
  - step: qa
    persona: harness-qa
    verdict: PASS
    headline: Both verifies and both kinds are green with DEC-255 receipts. Base-red
      is 110 = 110. Mutants g, n1, n2 and n4 go red; n3 and n5 survive 426/426.
    files_touched:
    - .harness/harness/features/FEAT-2542-dispatcher-placement/runs/r-20261126-3-validate-validator/qa/manifest-unit.json
    - .harness/harness/features/FEAT-2542-dispatcher-placement/runs/r-20261126-3-validate-validator/qa/manifest-integration.json
  - step: code
    persona: harness-code-reviewer
    verdict: PASS
    headline: 'Closes the null/empty-feature fail-open, keeps omitted-feature legacy
      placement, and meets the ruled command wording. Code grade passes. One low finding:
      the check order is not pinned by a test.'
    files_touched: []
  - step: security
    persona: harness-security-reviewer
    verdict: PASS
    headline: 'Placement bypass closed: six malformed shapes are refused with no registry
      write. Low: a newline inside a value can still split a printed command line.'
    files_touched: []
  - step: ui
    persona: harness-ui-reviewer
    verdict: PASS
    headline: 'OQ-1 closed: 30 commands copied verbatim across 22 refusals hit their
      intended fixture registries, including roots with spaces and apostrophes. Null-feature
      refusals print no release command.'
    files_touched: []
  - step: goalcheck
    persona: harness-pm
    verdict: PASS
    headline: SC-02 moves from partial to met. SC-04 evidence is met, with no index
      drift and 25 anchors, 0 failed. The SC-03 seam exits 0. Two low advisories (A-3,
      A-4).
    files_touched: []
  must_fix: []
  files_touched:
  - .harness/harness/features/FEAT-2542-dispatcher-placement/runs/r-20261126-3-validate-validator/state.yaml
  - .harness/harness/features/FEAT-2542-dispatcher-placement/runs/r-20261126-3-validate-validator/qa/manifest-unit.json
  - .harness/harness/features/FEAT-2542-dispatcher-placement/runs/r-20261126-3-validate-validator/qa/manifest-integration.json
  open_questions: []
  escalations: []
  expertise_update: []
  adequacy_notes:
  - Receipts reflect this host (macOS arm64), not CI's interpreter. Both kinds were
    run once from the pin with PYTHONUNBUFFERED, NO_COLOR and FORCE_COLOR stripped
    and TERM=xterm-256color. tested_commit is 2ec0916f.
  - 'QA reproduced base-red independently: the base guard against the pin''s tests
    passed 316 of 426, and the 110 failures equal predicted_red as a set. Against
    the pre-fix guard bc937a94, all 14 c42 null/empty checks fail, and null/bound
    proceeds and claims.'
  - inflight_registry.py is byte-identical to base (exit 0). The seam b27cbcc6..2ec0916f
    on both guard files exits 0 (QA and pm both measured it), and b27cbcc6 is the
    last tested_sha in the Pin run (fix round c1) block, which has pin_run_exit 0.
  - Mutant g (placement after _start_preflight), which survived c1, now goes red on
    c43/not-found/run-preflight:cause, so the OQ-4 ordering is pinned.
  - 'The ruled fixtures (null and "") are both witnessed by discriminating mutants:
    n1 reddens 14 checks, n2 reddens the 6 empty rows, and n4 (refusing legacy) reddens
    the 3 omitted rows. The non-str leg and the feature-before-persona order are correct
    at the pin but have no witness; see coverage_gaps.'
  - 'pm reasoned that swapping the feature and persona checks would fail open via
    shlex.quote(None). QA''s executed n3 probe falsified this: the swap gives exit
    2 with a persona-mismatch misdiagnosis, which is fail-closed. QA''s measurement
    is adopted.'
  - 'Ruled out of scope and not reopened: OQ-3, F-4, case-41, the sentinel object.
    No reader raised a new defect there.'
  - 'Optional, if round 2 is spent for another reason: two rows in test-dispatch-guard.py
    (main-session-direct, DEC-174) would close Q2-2 and Q2-1. Those rows are a non-str
    feature and a null feature combined with a persona mismatch. Neither justifies
    a round alone.'
  sc_status:
  - id: SC-01
    verdict: met
    method: automated
    evidence: Stands on c1 evidence. The fix diff does not touch _mission_scope or
      the c38/c40 rows, and c38/distill/distill exit/claim/receipt remain in the 110
      base-red set.
  - id: SC-02
    verdict: met
    method: automated
    evidence: _lookup_placement at 2ec0916f checks isinstance(feature, str) and feature
      at l.855, after ok and before persona at l.860. case_42 null/empty bound+exploit
      rows refuse as unreadable, and the omitted feature proceeds as legacy. case_43
      is the ordering row. 426/426 at the pin; the 14 c42 checks are red at bc937a94
      and at base.
  - id: SC-03
    verdict: met
    method: inspection
    evidence: git diff --quiet b27cbcc6 2ec0916f -- dispatch-guard.py test-dispatch-guard.py
      exits 0 (QA and pm). predicted_red equals observed_red, 110 = 110.
  - id: SC-04
    verdict: met
    method: inspection
    evidence: DEC-258 unreadable bullet, DECISIONS.md l.8706-8707, carries the malformed-claim
      clause. The index is unchanged and regenerates with no drift. check-decision-anchors
      gives 25 anchors, 0 failed. Wording advisory A-3.
  - id: SC-05
    verdict: met
    method: inspection
    evidence: 'Stands: plan.yaml source_issues [2542, 2532] is unchanged by the fix
      diff.'
  needs_approval: false
  severity_max: low
  matrix_ok: true
  coverage_gaps:
  - 'Q2-2 (qa): the isinstance(str) leg of the feature check is unpinned. Mutant n5
    survives 426/426, and under it a feature of 123 exits 0 and claims in the declared
    feature (fail-open under mutation).'
  - 'Q2-1 (qa) = code-reviewer low = pm A-4: no row combines a null feature with a
    persona mismatch, so the feature-before-persona order is unpinned. Mutant n3 survives
    426/426 (fail-closed misdiagnosis under mutation).'
  findings:
  - kind: substance
    scope: none
    severity: low
    reader: qa
    summary: 'T-01: the type leg of `isinstance(feature, str) and feature` has no
      test. Mutant n5 (`if not feature:`) survives, and under it a non-str truthy
      feature fails open to the declared feature.'
    why: 'Ranked first because the mutant fails open (D-01 class), though the pin
      refuses the shape as unreadable. Not must_fix: the ruling named only null and
      "" fixtures.'
  - kind: substance
    scope: none
    severity: low
    reader: qa, code-reviewer, pm
    summary: 'T-01: no test pins that the malformed-feature check runs before the
      persona check (mutant n3 survives).'
    why: Three readers reported the same finding. QA measured that n3 gives exit 2
      with a persona-mismatch misdiagnosis (fail-closed). pm's reasoned fail-open
      via shlex.quote(None) is dismissed on that measurement.
  - kind: substance
    scope: none
    severity: low
    reader: security-reviewer
    summary: 'T-01: shlex.quote keeps each value as one argument, but a value containing
      a newline splits the printed command across lines (dispatch-guard.py:779-781).'
    why: Requires an attacker who can edit the registry or controls the checkout path.
      The guard still exits 2 and nothing executes automatically, and ruling rules
      1-4 are met. Advisory.
  - kind: form
    scope: none
    severity: low
    reader: pm
    summary: 'T-02: DEC-258''s clause says ''names no feature (null or empty)'', narrower
      than the ruled ''not a non-empty string''. The code also refuses non-str shapes.'
    why: The record describes less than the code refuses, but makes no false claim.
      It is a one-phrase edit the next time T-02 touches DECISIONS.md; non-gating.
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
```
