# Validation digest — FEAT-1821-ui-verification-lane

The pinned panel is blocked from clearance: Mode B proved that failed inspection setups were published as complete evidence, the independent gate can lose its signed inspection manifest, component tests cannot collect, the Python code-grade gate fails, and fail-first records are incomplete. The intended FEAT-53 product RED remains correctly out of scope.

```yaml
VERDICT: BLOCKED
DIGEST:
  headline: "Pinned validation is blocked: inspection evidence fails open, component collection is broken, code_grade fails, and fail-first proof is incomplete."
  team: validate
  steps_run: 5
  cycles_used: 0
  members:
    - { step: qa, persona: harness-qa, verdict: BLOCKED, headline: "matrix_ok=false: component tests cannot collect and seven automated SCs lack fail-first proof; the stale-pin claim is dismissed.", files_touched: [".harness/harness/features/FEAT-1821-ui-verification-lane/notes/review-harness-qa-c0.md"] }
    - { step: code, persona: harness-code-reviewer, verdict: FAIL, headline: "Stage 1 found a gate-level inspection-manifest bypass; canonical code_grade=fail over the pinned range.", files_touched: [] }
    - { step: security, persona: harness-security-reviewer, verdict: PASS, headline: "All 11 changed paths were censused with no exploitable trust-boundary or capability delta.", files_touched: [] }
    - { step: ui, persona: harness-ui-reviewer, verdict: FAIL, headline: "Mode B inspected results.json and 41/41 WebPs and found blank or wrong-state captures accepted after every signed setup failed.", files_touched: [] }
    - { step: goalcheck, persona: harness-pm, verdict: FAIL, headline: "All four perspectives and SC-01..SC-12 were graded; operator and reader fail while maintainer and orchestrator are partial.", files_touched: [".harness/harness/features/FEAT-1821-ui-verification-lane/notes/research-FEAT-1821-ui-verification-lane-goalcheck-validate-c0.md"] }
  must_fix:
    - "1. T-13/harness-backend-dev and T-01/main-session-direct: make inspection setup/capture errors fail the reporter and gate, and make gate require predicates plus the signed inspection-evidence manifest."
    - "2. T-06/main-session-direct, after item 1: rerun only the configured lane and commit 41 state-matching WebPs/results; never publish failed setups as status=evidence."
    - "3. T-01/main-session-direct, after the semantic gate repair: refactor the four mechanically failing ui_contract.py functions to code grade 4 or better."
    - "4. T-03/harness-frontend-dev: declare and lock @testing-library/dom so the configured component kind collects and executes."
    - "5. T-01/main-session-direct: supply pinned fail-first evidence for SC-02..SC-06 and SC-10..SC-11; current-green/source-presence evidence is insufficient."
  files_touched:
    - ".harness/harness/features/FEAT-1821-ui-verification-lane/notes/review-harness-qa-c0.md"
    - ".harness/harness/features/FEAT-1821-ui-verification-lane/notes/review-harness-code-reviewer-c0.md"
    - ".harness/harness/features/FEAT-1821-ui-verification-lane/notes/review-harness-security-reviewer-c0.md"
    - ".harness/harness/features/FEAT-1821-ui-verification-lane/notes/review-harness-ui-reviewer-c0.md"
    - ".harness/harness/features/FEAT-1821-ui-verification-lane/notes/research-FEAT-1821-ui-verification-lane-goalcheck-validate-c0.md"
    - ".harness/harness/features/FEAT-1821-ui-verification-lane/runs/validate-validator/state.yaml"
  branch: none
  open_questions: []
  escalations: []
  expertise_update: []
  adequacy_notes:
    - "All five artifacts bind to review SHA 711ba16227eda39ddb397ed574e4ca199fbc5984; Mode B opened results.json and all 41 referenced WebPs."
    - "served_bundle_commit 0ef52107fde67b1f42cb51a16c773635dc73a408 exactly satisfies this dispatch's settled 0ef52107 requirement; QA/PM's review-SHA-equality finding and approval question are assessed-and-dismissed because they contradict the pinned acceptance contract."
    - "QA invoked the gate with the review SHA rather than settled served bundle 0ef52107, so that stale-commit result is not adopted; the blocking matrix result still rests independently on component collection failure and missing fail-first evidence."
    - "code_grade: fail over canonical range 23d6745b888b492b92ae61e5dcaa5992c066f9c4..711ba16227eda39ddb397ed574e4ca199fbc5984; lead schema has no code_grade passthrough, so the result is preserved here and in the code member headline."
    - "The security PASS covers the changed trust boundaries only; it does not offset the critical correctness failure in committed visual evidence."
    - "The expected FEAT-53 outcomes—22 non-green product predicates and green SRC-TOKENS—are assessed-and-dismissed as FEAT-1821 defects; only structural lane failures gate."
    - "The unit-kind exit was contaminated by concurrent Vite cache writes and is not promoted into a separate feature defect; rerun the configured matrix after component dependency repair."
  sc_status:
    - { perspective: operator, verdict: fail, criteria: "SC-01..SC-04" }
    - { perspective: code_maintainer, verdict: partial, criteria: "SC-05..SC-07" }
    - { perspective: reader, verdict: fail, criteria: "SC-08..SC-09" }
    - { perspective: orchestrator, verdict: partial, criteria: "SC-10..SC-12" }
  needs_approval: false
  severity_max: critical
  matrix_ok: false
  coverage_gaps:
    - "Configured component tests stop before collection because @testing-library/dom is absent."
    - "SC-02..SC-06 and SC-10..SC-11 lack pinned red-before evidence."
    - "The committed inspection bundle contains 41 readable files but does not prove its declared routes, states, interactions, and viewports."
    - "The Python gate does not require predicate and inspection-manifest parsing in gate mode."
  findings:
    - { id: V-01, kind: substance, severity: critical, status: must_fix, reporters: "ui-reviewer, goalcheck", task: "T-13 plus T-06", owner: "harness-backend-dev plus main-session-direct", summary: "Reporter and gate publish inspection status=evidence even when every signed setup/capture failed; blank or wrong-state WebPs can satisfy completeness.", evidence: "results.json:491-546,733-766,864-917,1010-1042; ui-reporter.ts:47-94; UI artifact inspected 41/41 WebPs." }
    - { id: V-02, kind: substance, severity: high, status: must_fix, reporters: "code-reviewer", task: T-01, owner: main-session-direct, summary: "gate() accepts a DESIGN contract after its required inspection manifest is removed because gate mode omits require_predicates and require_inspection_evidence.", evidence: "ui_contract.py:229 versus load_manifest switches at :84-86; reviewer removal mutant returned PASS." }
    - { id: V-03, kind: substance, severity: high, status: must_fix, reporters: "qa, goalcheck", task: T-03, owner: harness-frontend-dev, summary: "Configured component coverage cannot collect because @testing-library/dom is absent.", evidence: "package.json:21-30 and configured Vitest output recorded in review-harness-qa-c0.md." }
    - { id: V-04, kind: substance, severity: high, status: must_fix, reporters: "code-reviewer", task: T-01, owner: main-session-direct, summary: "Canonical Python grading fails on _table_after, _inspection_evidence, gate, and _screenshot_reasons.", evidence: "ui_contract.py:61,138,213,306; code_grade=fail over the pinned canonical range." }
    - { id: V-05, kind: form, severity: med, status: must_fix, reporters: "qa, goalcheck", task: T-01, owner: main-session-direct, summary: "Pinned fail-first records are absent for seven automated success criteria.", evidence: "QA fail_first inventory: SC-02..SC-06 and SC-10..SC-11 are GAP." }
    - { id: D-01, kind: substance, severity: high, status: dismissed, reporters: "qa, goalcheck", task: T-06, owner: main-session-direct, summary: "Claim that served_bundle_commit must equal review_sha.", evidence: "Dismissed: this dispatch explicitly requires served_bundle_commit 0ef52107; results.json records its full exact match." }
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1821-ui-verification-lane/.harness/harness/features/FEAT-1821-ui-verification-lane/runs/validate-validator/digest.md
```
