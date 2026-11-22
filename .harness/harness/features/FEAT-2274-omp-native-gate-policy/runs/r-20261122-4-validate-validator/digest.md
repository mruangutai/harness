# FEAT-2274 validation c1 — FAIL

**Pin `649612d8bc0add67014613f208180a3344a6ac02` is not ready: narrow configuration faults still authorize protected commands, dispatch has silent unavailable branches, refusal composition drops notices, and standing test kinds regress. Severity maximum: high.** Baseline: `1e0b014917125bc9aae1f30a2f6fd53ed239f3bc`. No source changes by this panel.

## One ordered must-fix list

1. **V1 — high, substance, T-01 (code):** `gh-close-gate.py:239-245` and `branch-create-gate.py:167-190` turn failed config reads into sync-off exemptions. After command applicability matches, malformed/unreadable configuration must refuse, not silently allow. Preserve legitimate sync-off exemptions and unrelated-command bypass; add failing-first matching/unrelated config-fault cases.
2. **V2 — med, substance, T-01 (pm F1):** `dispatch-guard.py:321-323,442-445` leaves failed run-dir vocabulary derivation and unreadable target tool grants stderr-only. Emit unavailable outcomes for both failed-check branches and independently cover them; retain legitimate no-grant passthrough. SC-01 is partial despite the green adapter matrix.
3. **V3 — med, substance, T-01 (code):** `harness-hooks.ts:1874` drops already-collected unavailable notices when another check refuses. Preserve passive context beside block/reason and correct the unit case at `omp-hooks.test.ts:2196` that currently expects the loss. Deny precedence remains intact. SC-07 is partial.
4. **V4 — high, substance, T-01 (qa F1):** migrate `test-lead-start-preflight.py:381`'s stale Python-spawns refusal assertion to the new actual passthrough contract without simulating native authorization. This standing-unit regression is a test cutover omission, not evidence that the allowlist deletion itself was wrong; reconcile this additional test path through the authorized ownership workflow.
5. **V5 — high, substance, T-01 (code high + qa F2 med):** preserve all assertions while correcting mandatory grade-1 functions `test-validate-digest.py#run_feat2274_unavailable_cases` and `test-harness-boundary.py#case_feat2274_unavailable_outcome`. Also clear standing self-grading failure for `test-validate-digest.py#run_feat65_guard_cases`: its grade-2 reviewer reason does not make the executable gate green. Do not waive a grade-1 bar. QA's med self-grading finding overlaps code's high mandatory-bar finding; both original ratings remain recorded in their notes.
6. **V6 — med, substance, T-03 (qa F3):** shorten DECISIONS-INDEX ruling tails for DEC-204/234/118/208/100 to the existing 30-word cap, retaining meaning, then regenerate. Generator equality alone missed `test-gen-decisions-index.py::test_committed_index_is_complete_and_within_budget`.
7. **V7 — low, form, T-03 (pm F2):** complete consulted-decision retention accounting, including DEC-193 and its reason, in `notes/t03-decision-dispositions.md`. All six amendment landings already meet their promises; do not invent amendment subsections. SC-08 remains partial until the missing record is repaired.

Fix runtime defects before updating expectations; then correct standing gates and records. Main owns remediation, not this panel. Re-run affected verification against the resulting new pin; never reuse this pin's verdict as clearance.

## Reconciliation and adequacy

- **Security PASS does not clear V1.** Its note treats inherited configuration self-exemptions as retained. Code distinguishes a successful sync-off read from an `ArtifactAccessError` converted into that exemption. The latter is an own dependency failure after matching under literal SC-02, so code's high finding stands; SC-02 is partial. This is a promised-boundary omission, not a newly introduced baseline regression.
- **PM's met SC-02/SC-07 grades are superseded in this synthesis** by code's concrete untested config-fault and refusal-adjacent-notice scenarios. PM's SC-01/SC-08 partial grades stand. A green test encodes one incorrect notice expectation; it is not proof of the signed behavior.
- **QA ran the gates:** 63 unit files (2 failing files), 91 integration files (1 failing file), matrix false; four failed assertions across V4/V5/V6. Feature-focused runtime 445/445, extension 179/179 and constraints 14/14 are green, with every automated SC's fail-first demonstrated against immutable baseline plus durable builder receipts. QA's `kinds: satisfied` describes the named feature tests, NOT clean standing kinds; its suite fail/matrix false governs. The two user-reported canonical-reader baseline failures were not rerun or counted as regressions.
- **Advisory, preserved rather than dropped:** code's five grade-2 findings remain med/substance with individual reasons in its note; the digest crash-control member also overlaps V5's standing-gate remediation. PM F3 remains med/form: two changed skill files and canonical-reader classification JSON lack approved task-file ownership. They serve the approved cutover, so this is ownership-record reconciliation, not an inferred product scope change or new behavior requirement. Main should repair the record through its authorized workflow; no additional product decision is requested.
- Code's grader uses required merge-base `c1724230c4d931ad46d433c8ba93df8cf312f898`, not the assigned implementation baseline; the named new FEAT-2274 grade-1 functions are nevertheless in scope. Security and PM assurance is static/receipt-based; code executed its required grader, QA executed tests; UI correctly scoped out after a 30-file census. No compiler, live native-rule delivery, rendered UI or operator UAT assurance is claimed. Existing #2257 and documented OMP rule-delivery limits remain approved, not new findings.
- Gate policy `advisory_unless_high` does not make every medium advisory: V2/V3 violate signed SCs, V6 fails the active matrix, and V7 leaves SC-08 partial. Concrete obligations, not style, place them in must-fix. No reader finding is silently dismissed.

## Reader artifacts

All paths below are feature-relative under `.harness/harness/features/FEAT-2274-omp-native-gate-policy/` in the assigned worktree:
- QA **FAIL** — `notes/review-harness-qa-c1.md` (matrix, failures and per-SC fail-first).
- Code **FAIL** — `notes/review-harness-code-reviewer-c1.md` (pinned source/risk evidence and grade-2 reasons).
- Security **PASS**, scoped/static — `notes/review-harness-security-reviewer-c1.md`.
- UI **PASS**, measured non-UI scope — `notes/review-harness-ui-reviewer-c1.md`.
- PM **FAIL** — `notes/research-FEAT-2274-omp-native-gate-policy-goalcheck-validate-c1.md` (perspectives, SCs, six met amendment landings and external OMP provenance).

Open questions: none. Source files touched: none. Send-back cycles used: 0.

```yaml
VERDICT: FAIL
DIGEST:
  headline: '649612d8bc0add67014613f208180a3344a6ac02 fails validation: enforcement
    omissions, standing-suite regressions and incomplete disposition accounting; severity
    high.'
  open_questions: []
  files_touched: []
  expertise_update: []
  team: validate
  steps_run: 5
  cycles_used: 0
  members:
  - step: qa
    persona: harness-qa
    verdict: FAIL
    headline: Feature tests and fail-first evidence pass; standing unit and integration
      commands regress.
    files_touched: []
  - step: code
    persona: harness-code-reviewer
    verdict: FAIL
    headline: Narrow config failures allow, refusal-adjacent notices disappear, and
      two mandatory risk grades fail.
    files_touched: []
  - step: security
    persona: harness-security-reviewer
    verdict: PASS
    headline: No independently identified security defect; static assurance only.
    files_touched: []
  - step: ui
    persona: harness-ui-reviewer
    verdict: PASS
    headline: Measured 30-file diff has no built UI surface; correctly scoped out.
    files_touched: []
  - step: goalcheck
    persona: harness-pm
    verdict: FAIL
    headline: SC-01 and SC-08 partial; six decision amendments landed; operator and
      maintainer perspectives partial.
    files_touched: []
  must_fix:
  - "V1 \u2014 T-01: distinguish narrow-gate configuration read failures from legitimate\
    \ sync-off exemptions in gh-close-gate and branch-create-gate; refuse matching\
    \ commands on failures while preserving unrelated-command bypass, with fail-first\
    \ regression coverage."
  - "V2 \u2014 T-01: emit explicit unavailable outcomes for dispatch-guard's failed\
    \ run-dir vocabulary derivation and unreadable target tool grants; independently\
    \ cover both branches without reclassifying legitimate no-grant passthrough."
  - "V3 \u2014 T-01: retain collected unavailable additionalContext beside a tool_call\
    \ refusal; correct the unit assertion that currently expects dropped notices without\
    \ weakening denial precedence."
  - "V4 \u2014 T-01: migrate test-lead-start-preflight.py's obsolete Python-spawns\
    \ refusal assertion to the actual passthrough contract; reconcile the additional\
    \ test path through the authorized ownership workflow."
  - "V5 \u2014 T-01: correct grade-1 run_feat2274_unavailable_cases in test-validate-digest.py\
    \ and case_feat2274_unavailable_outcome in test-harness-boundary.py without weakening\
    \ assertions; also resolve the standing self-grading failure for validate-digest's\
    \ grade-2 run_feat65_guard_cases. A written grade-2 reason does not clear the\
    \ executable gate, and grade-1 bars cannot be waived."
  - "V6 \u2014 T-03: shorten DECISIONS-INDEX ruling tails for DEC-204, DEC-234, DEC-118,\
    \ DEC-208 and DEC-100 to the existing 30-word cap, regenerate, and clear the standing\
    \ index-budget test."
  - "V7 \u2014 T-03: complete consulted-decision disposition accounting, including\
    \ retained DEC-193 with its reason, in notes/t03-decision-dispositions.md; preserve\
    \ the already-correct six amendment landings and in-place rewrite format."
  branch: none
  escalations: []
  adequacy_notes:
  - Reviewed immutable pin 649612d8bc0add67014613f208180a3344a6ac02 against implementation
    baseline 1e0b014917125bc9aae1f30a2f6fd53ed239f3bc. All five required readers completed;
    no source edits by this panel.
  - 'QA reports 63 standing unit files with two failing files and 91 standing integration
    files with one failing file: four failed assertions across three regression findings.
    Feature-focused runtime 445/445, extension 179/179 and constraints 14/14 pass.
    Every automated SC has fail-first evidence, including immutable-baseline reproduction
    and durable builder receipts.'
  - QA's satisfied kind entries describe passing named feature tests, not clean standing
    suites; its suite fail and matrix_ok false govern. No load/collection failure
    was reported. Functional/eval remain excluded under DEC-187.
  - Security's static PASS treats inherited config self-exemptions as retained; code
    identifies failed reads converted into those exemptions. Literal SC-02 requires
    own dependency failures to close after matching, so the high code finding stands.
    This is an unclosed promised boundary, not a newly introduced baseline regression.
  - PM's met SC-02 and SC-07 grades are superseded by code's concrete config-fault
    and refusal-adjacent-notice scenarios; this synthesis grades both partial. PM's
    SC-01 and SC-08 partial grades stand. Six actual decision amendment landings remain
    met.
  - Code's required grader used merge-base c1724230c4d931ad46d433c8ba93df8cf312f898;
    the two named new FEAT-2274 grade-1 functions are in scope. Overlapping QA med
    self-grading and code high mandatory-bar reports are consolidated as V5, with
    original ratings retained in their artifacts.
  - Five med grade-2 code findings retain individual nonblocking reasons in the code
    artifact. The validate-digest crash-control function additionally needs V5's standing-gate
    resolution; an advisory reason alone does not make the executable gate pass.
  - 'PM''s med/form ownership-record finding is preserved as advisory reconciliation:
    two skill files and canonical-reader-classification.json were changed outside
    approved task-file lists. Readers identify these as serving the approved cutover,
    not a new product scope requirement; Main owns authorized record reconciliation.'
  - Fix runtime defects before updating expectations, then standing gates and records.
    Medium SC violations, active-suite failures and the low/form SC-08 incompleteness
    remain must-fix despite advisory_unless_high; style does not gate.
  - 'Security and PM are static/receipt-based; code executed its required grader;
    QA executed tests. UI scoped out on an actual 30-file census. No compiler, live
    native-rule delivery, rendered-UI or UAT assurance is claimed. Known #2257 and
    documented-rule-delivery limits remain approved.'
  - The two user-reported canonical-reader baseline failures were not rerun or counted
    as regressions. No reader finding was silently dropped; reader notes and reconciliation
    are linked in the consolidated artifact.
  sc_status:
  - id: SC-01
    verdict: partial
    method: automated
    evidence: 'PM F1 and code notice finding: dispatch-guard.py:321-323,442-445 remain
      stderr-only; refusal composition drops notices despite passing shared adapter
      tests. Owner T-01, V2/V3.'
  - id: SC-02
    verdict: partial
    method: automated
    evidence: 'Code high finding: gh-close-gate.py:239-245 and branch-create-gate.py:167-190
      convert failed config reads into clean exemptions. Dual-classifier fault corpora
      pass but omit this scenario. Owner T-01, V1.'
  - id: SC-03
    verdict: met
    method: automated
    evidence: Pinned omp-hooks.test.ts:2305-2324 covers Main/unstarted/governed callers,
      non-task refusals and task/non-governed controls; QA confirms fail-first and
      green execution.
  - id: SC-04
    verdict: met
    method: inspection
    evidence: Readers inspected pinned dispatch allowlist deletion, unchanged native
      spawns versus baseline and all three lead guidance blocks. External published
      OMP 19.1.0 shared-path evidence is owner-checkout grilling Facts I verified,
      not pin content.
  - id: SC-05
    verdict: met
    method: automated
    evidence: Pinned test-harness-constraints.py independently covers exact frontmatter,
      five groups, exclusions and guidance; QA 14 passing cases and fail-first evidence.
      Native delivery is documented-contract assurance only.
  - id: SC-06
    verdict: met
    method: automated
    evidence: Pinned dispatch suite retains refusal controls and behavioral formerly-allowlisted
      passthrough cases with baseline red evidence. Separate stale standing-unit caller
      expectation requires V4; no native authorization simulation is accepted.
  - id: SC-07
    verdict: partial
    method: automated
    evidence: harness-hooks.ts:1874 returns block/reason before notices; omp-hooks.test.ts:2196
      currently expects this omission. Other env/input/schema/result composition cases
      pass. Owner T-01, V3.
  - id: SC-08
    verdict: partial
    method: inspection
    evidence: All six amendment clauses, SPEC and regenerated index land; consulted
      DEC-193 lacks retention accounting in t03-decision-dispositions.md. Owner T-03,
      V7. Standing index-budget regression also requires V6.
  - id: SC-09
    verdict: met
    method: automated
    evidence: QA confirms unavailable red/green assertions and retained normal-pass,
      deny, absent/null/empty digest_object, non-governed-target and merge-gate refusal
      controls.
  - id: DEC-100
    verdict: met
    method: inspection
    evidence: 'PM inspected pin DECISIONS.md:1372-1399: broad default retained, visible
      unavailable contract and bounded narrow exceptions landed.'
  - id: DEC-118
    verdict: met
    method: inspection
    evidence: 'PM inspected pin DECISIONS.md:2223-2233: native shared-path sole allowlist
      authority landed with squad/name policy retained.'
  - id: DEC-127
    verdict: met
    method: inspection
    evidence: 'PM inspected pin DECISIONS.md:2672-2678: own failures remain open with
      explicit unavailable visibility.'
  - id: DEC-204
    verdict: met
    method: inspection
    evidence: 'PM inspected pin DECISIONS.md:6495-6513: Main exemption qualified by
      target-based task-only route policy; claims retained.'
  - id: DEC-208
    verdict: met
    method: inspection
    evidence: 'PM inspected pin DECISIONS.md:6713-6721: historical text distinguished
      from live digest_object refusals and visible own gaps.'
  - id: DEC-234
    verdict: met
    method: inspection
    evidence: 'PM inspected pin DECISIONS.md:7849-7865: narrow matching precedes copied
      trusted bootstrap; other bootstrap-first gates retained.'
  needs_approval: false
  severity_max: high
  matrix_ok: false
  coverage_gaps:
  - Failed-config-read behavior after narrow command matching is not covered by the
    currently green fault corpora.
  - Dispatch run-dir derivation and tool-grant deliberate unavailable branches lack
    independent visibility assertions.
  - Pre-call denial composition has a regression assertion that endorses lost sibling
    unavailable notices.
  - Clean cutover missed the standing lead-start-preflight Python-allowlist expectation.
  - Standing self-grading and index-budget gates fail outside task-local verify commands.
  - QA did not perform per-check mutation proofs for retained SC-06 dispatch controls;
    their discrimination is unshown, not disproven.
  findings:
  - kind: substance
    scope: none
    severity: high
    reader: code-reviewer
    summary: 'V1, T-01: failed configuration reads still authorize protected narrow-gate
      commands.'
    why: gh-close-gate.py:239-245 and branch-create-gate.py:167-190 collapse unreadable/malformed
      configuration into disabled-sync outcomes after applicability. Literal SC-02
      requires own failures to refuse matching commands.
  - kind: substance
    scope: none
    severity: med
    reader: pm
    summary: 'V2, T-01: dispatch dependency gaps remain stderr-only rather than visibly
      unavailable.'
    why: dispatch-guard.py:321-323,442-445 skips failed run-dir vocabulary derivation
      or unreadable tool-grant checks without unavailable JSON, so the adapter can
      report a normal pass. SC-01 remains partial.
  - kind: substance
    scope: none
    severity: med
    reader: code-reviewer
    summary: 'V3, T-01: a refusal discards already-collected unavailable notices.'
    why: harness-hooks.ts:1874 returns block/reason before composing notices; the
      new unit case expects that loss. Preserve passive context alongside independent
      denial to meet SC-01/SC-07.
  - kind: substance
    scope: none
    severity: high
    reader: qa
    summary: 'V4, T-01: standing lead-start-preflight still asserts the deleted Python
      spawns refusal.'
    why: test-lead-start-preflight.py:381 fails at the pin and passes at baseline.
      Otherwise-valid product-lead to eng-lead now passes dispatch-guard by design;
      migrate the caller assertion rather than restoring duplicate authorization.
  - kind: substance
    scope: none
    severity: high
    reader: code-reviewer; qa
    summary: 'V5, T-01: mandatory Python risk bars and standing self-grading fail.'
    why: Code reports grade-1 validate-digest run_feat2274_unavailable_cases and boundary
      case_feat2274_unavailable_outcome. QA separately rates standing validate-digest
      self-grading regression med, including grade-2 run_feat65_guard_cases. Consolidated
      remediation must preserve assertions, clear executable gates and not waive grade-1
      bars.
  - kind: substance
    scope: none
    severity: med
    reader: qa
    summary: 'V6, T-03: five changed index ruling tails exceed the existing 30-word
      cap.'
    why: Standing test-gen-decisions-index.py budget assertion fails for DEC-204/234/118/208/100
      while generator equality passes. Shorten tails and regenerate; task-local verification
      did not bind the cap.
  - kind: form
    scope: none
    severity: low
    reader: pm
    summary: 'V7, T-03: consulted DEC-193 lacks disposition accounting.'
    why: T-02 explicitly requires its consultation, but t03-decision-dispositions.md
      neither retains nor amends DEC-193 with a reason. SC-08 is partial despite all
      six amendment landings being met.
  - kind: substance
    scope: none
    severity: med
    reader: code-reviewer
    summary: 'Advisory, T-01: five grade-2 test functions have written locality reasons.'
    why: The code artifact records individual reasons for bash-write run_feat65_guard_cases
      and run_feat2274_unavailable_cases, check-domain _feat2274_cases, dispatch case_f2274_unavailable_outcome,
      and validate-digest run_feat65_guard_cases. Reasons support nonblocking review
      disposition; the last still overlaps V5's failing standing gate.
  - kind: form
    scope: none
    severity: med
    reader: pm
    summary: 'Advisory, T-01/T-03: three changed paths lack approved task-file ownership.'
    why: canonical-reader-classification.json and two skill authority corrections
      serve the approved cutover but are absent from task files lists. Builder explanations
      establish intent, not ownership; Main should reconcile the record through its
      authorized workflow. No new product behavior or regression is inferred.
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
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2274-omp-native-gate-policy/.harness/harness/features/FEAT-2274-omp-native-gate-policy/runs/r-20261122-4-validate-validator/digest.md
```
