# FEAT-71 fix-c1 — consolidated re-verification

**PASS at 5a2edb72a220efd4a44cda6f512ec5697c0f37e0. CR-01 and Q-1 resolved; no must-fix; severity_max med.** Four readers terminal; no source edits, repin or merge by this lead. Delta reviewed from 3e6add2af05f5b801afec1ef69440fe54e1529a4; grader range starts at 4a05030d401593003209f525fd06e00802eccd36.

## Decisions
- **CR-01 resolved.** Code independently measured grader exit 0 (32 passing, no high records), verified both replacement cases are registered and every original assertion survives: both no-receipt identities, four receipt rows, open and both recover-terminal triggers. QA independently executed the records test: exit 0, all eight T-06 checks. References: `../../notes/review-harness-code-reviewer-fix-c1.md`, `../../notes/qa-fix-c1.md`.
- **Q-1 resolved, not waived.** The governing `harness-verification-rules` locally_run row requires a recorded run when detect is touched, not conversion of that kind to satisfied. The feature-local receipt now supplies it. Configuration additionally calls for a run and recorded result when session-file resolution changes; this relocation changes no such behavior. QA verified the relocated TypeScript blob is identical to baseline and unchanged across this delta. A recorded baseline-equivalent failure is not a green probe, but neither is it the former missing-record condition. QA's conditional policy question is answered by that literal rule; no operator decision remains.
- **The live probe remains red: 3/4 on both baseline and feature.** Its case3 assumes subagents lack getContextUsage; omp 18.18.0 defines it. Cases4–6 never execute because it returns early. QA inspected raw observations from both runs: subagent getSessionFile resolves to its own nested transcript, main to a flat transcript. This supports relocation equivalence, not full live-suite success. The existing stale-premise defect is retained as low/substance advisory, not a FEAT-71 regression. Evidence: `../../notes/omp-session-accessor-live-2026-11-07.md`; QA artifact records raw locations and provenance limits.

## Ranked non-blocking notes
1. **CR-02 med/substance:** case_t14_exempt_shape remains grade2 (CC13/cognitive8/ABC30.6); shared-state three-outcome fixture reason retained.
2. **CR-03 med/substance:** _t07_sweep remains grade2 (CC4/cognitive3/ABC26.6); shared disposable repository lifecycle reason retained.
3. **QA low/substance:** stale live-probe case3, above; independent backlog candidate only.
4. **QA low/form:** SC-02 unit evidence label partly describes integration assertions. Both kinds executed; no matrix gap. No reader severity or kind changed.

## Adequacy and scope
QA matched the supplied exact-pin full log's 141 successful file blocks to the committed inventory: 57 unit + 84 integration, nonzero discovery. Existing baseline red-first receipts support SC-02/03; baseline-green INV-37 assertions are not represented as mutation proofs. Full suite was not rerun by this lead or readers; only QA's targeted test and code's grader were executed. The log has no final shell-exit marker, so suite-block success is independently checked, while complete five-gate/pipeline success remains builder-reported. Expected negative-test FAIL output is not a failing file verdict.

Security found no new exploitable delta; UI measured five changed paths and zero visual-extension matches, correctly out of scope. These static lenses add no runtime-test assurance. QA's assertion that no second reviewer checked the split is superseded by code's independent semantic/discovery inspection. Previously dismissed QA absence/naming/live-read allegations remain dismissed, not new coverage gates. Existing goalcheck SC-01–05 dispositions stand: this test-only extraction and additional receipt do not change acceptance or inspection subjects; no redundant goalcheck dispatched.

Open questions: none. Must-fix: none. The configured review gate is advisory_unless_high. This PASS is scoped to remediation and evidence sufficiency, not a claim that the pre-existing live probe is green. Principles: **Verification is the product** and **No more specific than necessary** (`docs/PRINCIPLES.md`): require the actual recorded obligation, preserve its failure honestly, and do not invent a new green-probe acceptance criterion.

```yaml
VERDICT: PASS
DIGEST:
  headline: 5a2edb72a220efd4a44cda6f512ec5697c0f37e0 clears CR-01 and Q-1; no must-fix,
    two medium advisories remain.
  team: fix
  steps_run: 4
  cycles_used: 0
  members:
  - step: qa
    persona: harness-qa
    verdict: PASS
    headline: Required automated kinds pass; live run recorded, baseline-equivalent
      probe failure retained.
    files_touched: []
  - step: code
    persona: harness-code-reviewer
    verdict: PASS
    headline: CR-01 resolved; grader exits 0 and original assertions survive.
    files_touched: []
  - step: security
    persona: harness-security-reviewer
    verdict: PASS
    headline: No exploitable regression in remediation delta.
    files_touched: []
  - step: ui
    persona: harness-ui-reviewer
    verdict: PASS
    headline: Measured five-path delta contains no UI surface.
    files_touched: []
  must_fix: []
  files_touched: []
  branch: none
  open_questions: []
  escalations: []
  expertise_update: []
  adequacy_notes:
  - Q-1 resolved under the literal locally_run rule requiring a recorded run. No waiver
    granted; the kind remains locally_run, not satisfied.
  - "Live probe remains red 3/4 on baseline and feature because case3 assumes getContextUsage\
    \ is undefined in subagents. Cases4\u20136 did not execute; QA inspected raw nested/flat\
    \ transcript observations instead."
  - QA independently executed the targeted records test successfully; code independently
    measured exact-range complexity and assertion/discovery preservation.
  - QA matched 141 successful recorded file blocks to 57 unit and 84 integration files.
    No full-suite rerun occurred; complete pipeline success remains builder-reported
    because the supplied log lacks a final shell-exit marker.
  - Prior goalcheck dispositions remain applicable; the extraction and additional
    receipt change no acceptance criterion.
  - Previously dismissed QA allegations remain dismissed; missing mutation evidence
    is not promoted into a demonstrated defect.
  sc_status:
  - id: SC-01
    verdict: met
    method: inspection
    evidence: Prior goalcheck exact-five-folder disposition unchanged by remediation
      delta.
  - id: SC-02
    verdict: met
    method: automated
    evidence: Existing red-first-S1a/S1b receipts; exact-pin recorded suite and independently
      executed records test preserve receipt assertions.
  - id: SC-03
    verdict: met
    method: automated
    evidence: Existing red-first-S2 receipt and exact-pin recorded unit/integration
      inventory remain applicable.
  - id: SC-04
    verdict: met
    method: inspection
    evidence: Byte-identical relocated TypeScript verified; new live receipt records
      baseline-equivalent observations without claiming probe success.
  - id: SC-05
    verdict: met
    method: inspection
    evidence: Prior bounded-deletion and documentation disposition unchanged by remediation
      delta.
  needs_approval: false
  severity_max: med
  matrix_ok: true
  coverage_gaps:
  - "Live probe cases4\u20136 were not executed due to pre-existing case3 failure;\
    \ raw observations support the accessor property."
  - No mutation proof claimed for baseline-green INV-37, domain or template assertions.
  findings:
  - kind: substance
    scope: none
    severity: med
    reader: code-reviewer
    summary: CR-02 remains an unchanged grade-2 advisory.
    why: 'case_t14_exempt_shape: CC13, cognitive8, ABC30.6; cohesive shared-state
      fixture justification retained.'
  - kind: substance
    scope: none
    severity: med
    reader: code-reviewer
    summary: CR-03 remains an unchanged grade-2 advisory.
    why: '_t07_sweep: CC4, cognitive3, ABC26.6; shared disposable repository lifecycle
      justification retained.'
  - kind: substance
    scope: none
    severity: low
    reader: qa
    summary: Live-probe case3 has a pre-existing stale subagent-identification premise.
    why: Baseline and feature both report 3/4; omp 18.18.0 defines getContextUsage
      in subagents. No relocation regression demonstrated.
  - kind: form
    scope: none
    severity: low
    reader: qa
    summary: SC-02 unit evidence label includes integration-located assertions.
    why: Both required kinds pass; retained as evidence-label qualification only.
  readers: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-71-corpus-independence/.harness/harness/features/FEAT-71-corpus-independence/runs/fix-c1-validator/digest.md
```
