# Validate c1 — FEAT-2542 at bc937a947fc8716c6cf1b171f05ad24d5e019747 (base 2e7a2c77)

**ESCALATE.** One must_fix bug in T-01 and one high finding that needs a wording ruling:
- **Bug (must_fix):** a live claim that matches the lead's persona but has a null feature falls
  back to the feature the child declares. This is the fail-open path that D-01 and DEC-258 forbid.
- **Needs a ruling:** the printed repair commands put sentence punctuation directly against the
  `--root` path and leave paths unquoted. That wording is copied from T-01 Step 3(ii) as signed,
  so changing it amends signed intent (G-06).

The gates and the evidence base are sound:
- Both kinds ran green with DEC-255 receipts.
- Base-red reproduces 97 = 97 as equal sets.
- The SC-03 seam is clean.
- Every contracted failure state refuses before the claim step.

## Gates (QA, measured on this host: macOS arm64, Python 3.15.2, not CI)
- unit: 68 files; integration: 95 files. Both ALL PASSED, runner exit 0. Receipts are at `runs/r-20261126-2-validate-validator/qa/manifest-{unit,integration}.json`, with tested_commit = the pin.
- The CI route and canonical gates exit 0.
- T-01 verify exits 0: dispatch-guard 397/397, lead-start-return 60/60, preflight 61/61, census passes, byte-identity holds.
- T-02 verify exits 0.
- `git diff --quiet d23f3728 bc937a94 -- dispatch-guard.py test-dispatch-guard.py` exits 0.
- Fail-first: the base guard run against the pin's tests passes 300 of 397. The 97 failing checks equal predicted_red as a set. c38/distill/distill exit, claim and receipt are red at base. Cases 1-37 and c41 are green at base.
- Mutants a–f and h each turn the suite red. **Mutant g survives**: moving placement after `_start_preflight` stays green at 397/397.

## Must-fix (ranked)
1. **T-01, substance, high.** Raised by code-reviewer (high) and security-reviewer (med); it is one defect.
   - Both reviewers measured the unchanged `find_run_claim` returning `ok` with the matching persona and `feature=None`.
   - I verified the consequence at source:
     - `_lookup_placement` returns `found["feature"]` (dispatch-guard.py:829).
     - `_dispatcher_placement` stores that None, and None is also the "outside the contract" sentinel (:840).
     - `_bound_distill_feature` then takes the declared-feature branch (:884-886).
   - Result: a governed lead with a damaged claim row escapes its distill obligations. This is #2542's defect, reached through a shape the characterization did not include.
   - It also makes DEC-258's "placed only by its own runtime claim" untrue for this shape.
   - I keep it at high. Security's med reflects that a damaged registry is a precondition. But the contract exists exactly for registry states the guard cannot trust, and the failure is fail-open (P-13).
   - Remedy: refuse an ok result whose claim feature is not a non-empty string, at exit 2, before the preflights and the claim step. Use an existing cause token; `unreadable` is my recommendation (see OQ-2). Add data-carrying fixtures for both a null feature and an omitted feature.
   - Lane: main-session-direct (DEC-174). No fix-team run may execute it.

## Escalated (gates; remedy amends signed wording)
2. **T-01, substance, high, ui-reviewer.** The commands are built at dispatch-guard.py:785 and :813:
   - the Inspect command (`--root <owner_root>.`) and the persona-mismatch release (`--root <root>, then`) attach punctuation to the path;
   - the roots are not shell-quoted;
   - the bare `inflight_registry.py` does not resolve on PATH.
   Copying a printed command as-is targets the wrong registry. The text follows T-01 Step 3(ii) to the letter, so changing it needs a ruling (OQ-1). My recommendation is to amend it and fold it into the same main-session round, since it touches the same lines.

## Assessed, not gating
- **Code-reviewer med (T-01): the plan route reads the registered run twice** (:862 for the route, then `_reader_preflight` at :614). I do not gate on it:
  - The letter of SC-01 and DEC-258 binds only the route and the *distill* preflight, and that pair reads once.
  - The second read is base behaviour, inside the preflights the spec said to leave alone.
  - Only a race between two reads within one guard process can exploit it, and the reviewer traced that race rather than timing it.
  - The repository gate is `advisory_unless_high`.
  I record both ratings and leave the call to the tier above (OQ-3).
- **QA F-1 (T-01, low): no test covers the ordering in Step 3(iii).** Mutant g survives, and the pin and base outputs measurably differ for a non-product lead dispatching a plan reader while unplaced. This is a "correct today, not pinned" gap (P-08). Recommend adding one c39 ordering row in the same round.
- **QA F-4 (form, low) and code-reviewer low (case 41):** these assertions match text fragments but do not tie the exit to the refusal that caused it, and do not tell a lookup that never ran from a failure that was swallowed. Advisory.
- **QA F-2 (proportionality, low):** the validator-lead and failure × mission cells are covered only along the diagonal, as the signed plan chose (PF-658a). Dismissed: the signed plan chose this coverage.
- **QA OQ-QA-1 (form, low): the Inspect sentence over-claims.** It reads "binds to the feature its own runtime claim names, never the declared one". But an eng-lead placed in a non-distill run of X that declares Y still claims in Y, at both base and the pin. That is inside the contract. DEC-258's body itself is accurate: its binding claim is scoped to placement and the distill route. Fold this into the OQ-1 wording ruling.
- **Main-session indentation deviation:** acceptable. It matches every other refusal in the file, no test or contract depends on the column, and no reader flagged it.

## Per perspective (pm, re-checked against the panel)
- **operator:** pass on refusals, with two exceptions: must_fix 1 is a lost refusal for the null-feature shape, and finding 2 makes the printed repair commands unsafe to run as-is.
- **orchestrator:** pass.
- **reader:** pass.
- **code maintainer:** pass. Restoring DEC-258's accuracy depends on must_fix 1.
- SC-03, SC-04 and SC-05 are met.
- All 8 `keep` dispositions are met.
- Code grade: pass.

## Open questions
- **OQ-1 (blocking):** amend T-01 Step 3(ii) so that printed commands carry quoted roots with no adjoining punctuation, and so that the Inspect sentence is narrowed?
- **OQ-2:** for the null-feature refusal, confirm the cause token `unreadable`. A new token would amend DEC-258's "five states".
- **OQ-3:** decide the plan-route double-read: code-reviewer rated it med and gating, the lead rated it non-gating.

```yaml
VERDICT: ESCALATE
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2542-dispatcher-placement/.harness/harness/features/FEAT-2542-dispatcher-placement/runs/r-20261126-2-validate-validator/digest.md
DIGEST:
  headline: 'FEAT-2542 at bc937a94 has sound gates: receipts green, base-red 97=97,
    SC-03 seam clean. But T-01 fails open when a live claim''s feature is null, and
    the printed repair commands (signed T-01 wording) target the wrong registry if
    run as printed. That second issue needs a wording ruling.'
  team: validate
  steps_run: 5
  cycles_used: 0
  branch: none
  members:
  - step: qa
    persona: harness-qa
    verdict: PASS
    headline: Unit (68 files) and integration (95 files) are green with DEC-255 receipts.
      Both verifies exit 0, the seam is clean and base-red is 97 = 97. Mutant g (placement
      moved after _start_preflight) survives.
    files_touched:
    - .harness/harness/features/FEAT-2542-dispatcher-placement/runs/r-20261126-2-validate-validator/qa/manifest-unit.json
    - .harness/harness/features/FEAT-2542-dispatcher-placement/runs/r-20261126-2-validate-validator/qa/manifest-integration.json
    - .harness/harness/features/FEAT-2542-dispatcher-placement/observations/harness-qa.md
  - step: code
    persona: harness-code-reviewer
    verdict: FAIL
    headline: A live claim with a null feature falls back to the declared feature
      (high). The plan route reads the registered run twice (med). Code grade passes.
    files_touched: []
  - step: security
    persona: harness-security-reviewer
    verdict: FAIL
    headline: Malformed live-claim features bypass governed-lead placement (med).
      Every contracted failure state still refuses before the claim step.
    files_touched: []
  - step: ui
    persona: harness-ui-reviewer
    verdict: FAIL
    headline: The printed Inspect and release commands attach punctuation to --root,
      leave paths unquoted and use a bare script name, so they can target the wrong
      registry (high).
    files_touched: []
  - step: goalcheck
    persona: harness-pm
    verdict: PASS
    headline: All four perspectives pass. SC-03, SC-04 and SC-05 are met; SC-01 and
      SC-02 are met on their test rows. All 8 keep dispositions are met.
    files_touched: []
  must_fix:
  - 'T-01 (main-session-direct, DEC-174), substance, high, from code-reviewer and
    security-reviewer: _lookup_placement returns found[''feature''] (dispatch-guard.py:829),
    so an ok, persona-matched claim with feature=None stores the outside-contract
    None sentinel (:840). _bound_distill_feature then takes the declared-feature path
    (:884-886). Refuse at exit 2, before any preflight or claim, any ok result whose
    claim feature is not a non-empty string, using an existing cause token (recommend
    unreadable; see OQ-2). Cover null and omitted features with data-carrying fixtures,
    and append a new Pin run block.'
  escalations:
  - id: ESC-1
    raised_by: harness-ui-reviewer
    question: The Inspect and release commands printed by _refuse_placement (dispatch-guard.py:785,813)
      attach '.' or ',' to the --root path, leave roots unquoted, and use the bare
      inflight_registry.py, which does not resolve on PATH. That text is T-01 Step
      3(ii) verbatim, so the fix amends signed intent. Should it be amended and folded
      into the must_fix round?
    domain: signed T-01 intent wording
    routed_to: harness-orchestrator
    resolution: pending; lead recommends amending to quoted roots with no adjoining
      punctuation and narrowing the Inspect sentence (QA OQ-QA-1)
    decided_by: pending
    recorded_as: runs/r-20261126-2-validate-validator/digest.md#Escalated
  open_questions:
  - id: OQ-1
    question: Approve amending T-01 Step 3(ii)? Printed commands would carry shell-quoted
      roots with punctuation kept off the path and a resolvable registry script. The
      Inspect sentence's 'never the declared one' would be narrowed, because a lead
      placed in a non-distill run that declares another feature still claims there,
      by design. Recommend yes, in the same main-session round as must_fix 1.
    blocking: true
  - id: OQ-2
    question: For the null- or omitted-feature claim refusal, confirm the cause token
      'unreadable'. A sixth token would amend DEC-258's five states and SC-02's token
      list.
    blocking: false
  - id: OQ-3
    question: 'The plan route reads the registered run twice (route at :862, then
      _reader_preflight at :614). code-reviewer rates it med and gating; the lead
      rates it non-gating: SC-01 and DEC-258 bind only the route and the distill preflight,
      the second read is base behaviour inside preflights the spec froze, and the
      race was traced, not timed. Which rating stands?'
    blocking: false
  - id: OQ-4
    question: 'Add a c39 ordering row (QA F-1) in the fix round so that moving _dispatcher_placement
      after _start_preflight turns the suite red? Recommend yes: it is cheap, lives
      in the same file, and is ''correct today but not pinned''.'
    blocking: false
  files_touched:
  - .harness/harness/features/FEAT-2542-dispatcher-placement/runs/r-20261126-2-validate-validator/state.yaml
  - .harness/harness/features/FEAT-2542-dispatcher-placement/runs/r-20261126-2-validate-validator/qa/manifest-unit.json
  - .harness/harness/features/FEAT-2542-dispatcher-placement/runs/r-20261126-2-validate-validator/qa/manifest-integration.json
  - .harness/harness/features/FEAT-2542-dispatcher-placement/observations/harness-qa.md
  expertise_update: []
  adequacy_notes:
  - Receipts reflect this host's environment (macOS arm64, Python 3.15.2), not CI's
    ubuntu interpreter.
  - 'Base-red was reproduced independently by QA: the base guard against the pin''s
    tests passed 300 of 397, and the 97 failures equal predicted_red as a set. Cases
    1-37 and c41 are green at base.'
  - 'The characterization missed a data-carrying shape: ok plus persona-match plus
    feature=None. The contract table enumerated find_run_claim outcomes by cause,
    not by the shape of a successful row. Both reviewers measured that the producer
    emits this shape.'
  - 'Main-session indentation deviation (remedy and Inspect lines indented two spaces)
    is accepted: it matches every other refusal in the file and no assertion depends
    on the column.'
  - DEC-258's body is accurate against the code except for the null-feature shape,
    which must_fix 1 restores.
  - Code grade passes (production >=4, tests >=3) per code-reviewer.
  - Every finding is scoped to task T-01; the plan-route double-read is assessed non-gating,
    with both ratings raised in OQ-3.
  sc_status:
  - id: SC-01
    verdict: met
    method: automated
    evidence: case_38/case_40 green at the pin; c38/distill/distill red at base (QA
      reproduced); c38/distill/run-reads asserts one read
  - id: SC-02
    verdict: partial
    method: automated
    evidence: All enumerated states refuse with tokens and remedies (case_38/39/40/41
      green, red at base). But an ok claim with feature=None, which is also a find_run_claim
      outcome, falls back to the declared feature (dispatch-guard.py:829,840,884-886);
      see must_fix 1
  - id: SC-03
    verdict: met
    method: inspection
    evidence: characterization-pin.md 97 = 97; git diff --quiet d23f3728 bc937a94
      on both guard files exits 0 (QA and pm both measured)
  - id: SC-04
    verdict: met
    method: inspection
    evidence: DEC-258 at DECISIONS.md:8697 carries every listed element; index regenerates
      with no drift; its 'placed only by its own runtime claim' needs must_fix 1 to
      be true for the null-feature shape
  - id: SC-05
    verdict: met
    method: inspection
    evidence: plan.yaml source_issues [2542, 2532] at the pin
  needs_approval: true
  severity_max: high
  matrix_ok: true
  coverage_gaps:
  - 'No test fixes placement ordering: mutant g (placement after _start_preflight)
    stays at 397/397 (QA F-1).'
  - Lineage rows assert stderr text fragments but do not tie the exit to the lineage
    denial (QA F-4).
  - Case 41 cannot tell 'lookup never ran' from 'lookup failure swallowed' (code-reviewer
    low).
  - No fixture covers an ok claim with a null or omitted feature (must_fix 1).
  findings:
  - kind: substance
    scope: none
    severity: high
    reader: code-reviewer, security-reviewer
    summary: 'T-01: an ok, persona-matched claim with feature=None is treated as outside
      the contract and falls back to the child''s declared feature.'
    why: Fail-open in the very class D-01 forbids, and it falsifies DEC-258 for this
      shape. Both reviewers measured the producer; the lead verified the guard path
      at source (:829,:840,:884-886). Security rated it med because registry damage
      is a precondition; the lead keeps high.
  - kind: substance
    scope: none
    severity: high
    reader: ui-reviewer
    summary: 'T-01: the printed Inspect and release commands attach punctuation to
      --root, are unquoted, and use a bare script name.'
    why: Copying a printed command as-is targets the wrong registry. The remedy amends
      signed T-01 Step 3(ii) wording, so it is escalated (ESC-1, OQ-1), not placed
      in must_fix.
  - kind: substance
    scope: none
    severity: med
    reader: code-reviewer
    summary: 'T-01: the plan route reads the dispatcher''s registered run twice (route,
      then _reader_preflight).'
    why: 'Assessed as non-gating: SC-01 binds only the route and the distill preflight,
      the second read is base behaviour, the race was traced rather than measured,
      and the gate is advisory_unless_high. Both ratings go up as OQ-3.'
  - kind: substance
    scope: none
    severity: low
    reader: qa
    summary: 'T-01: the Step 3(iii) ordering is unpinned; mutant g survives.'
    why: Behaviour is correct today but no test holds it; recommended in the fix round
      (OQ-4).
  - kind: form
    scope: none
    severity: low
    reader: qa
    summary: 'T-01: the Inspect sentence ''never the declared one'' over-claims for
      a lead placed in a non-distill run.'
    why: 'Measured: the claim lands in the declared feature at both base and the pin,
      which is within the contract. Folded into the OQ-1 wording ruling.'
  - kind: form
    scope: none
    severity: low
    reader: qa, code-reviewer
    summary: 'T-01: lineage and case-41 rows match text fragments but do not tie the
      exit to the refusal.'
    why: Advisory test-strength gap; other rows still catch the related mutants.
  - kind: proportionality
    scope: task
    severity: low
    reader: qa
    summary: "T-01: the SC-01 failure \xD7 mission cells and the SC-02 validator-lead\
      \ cells are covered only along the diagonal."
    why: 'Dismissed: the signed plan chose this coverage (PF-658a resolved).'
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
