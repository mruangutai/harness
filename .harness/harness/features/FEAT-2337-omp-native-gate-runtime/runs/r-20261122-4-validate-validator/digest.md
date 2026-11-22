# FEAT-2337 validate c1 — 6143625f5262f246d51d642662899a44a8d545d9

**ESCALATE: integration is red on the owner-manifest boundary; T-03 also has one medium-severity normative-policy landing defect.** Candidate runtime/receipt behavior tests pass. No source was edited, no merge is authorized, and no unconditional QA PASS or installed receipt acceptance is claimed.

## Ranked disposition and fix order

1. **GC-03 / high, environment gate obstacle:** main/operator must resolve the owner-manifest landing boundary. QA's DEC-255 integration run discovers 91 files; only `test-check-plan-routes.py` fails (six named DEVIATION assertions): the candidate QA manifest grant differs from the control-plane owner manifest. That same pinned file passes in an independent clone. This is not permission to alter the installed control plane, weaken tests, or relabel the integration receipt green. After disposition and any authorized T-03 correction, main sequences the required new-tip QA verification.
2. **GC-02 / substance / med / T-03 / SC-09, D-02:** clarify the already-approved feature-directory dirt exception in DEC-255 and matching SPEC/fix-team/QA/validator guidance. Pinned `DECISIONS.md:8428-8433` says unqualified clean working tree; the approved follow-up and `validate-digest.py:2576-2589` allow normal dirty feature records. Preserve behavior; do not reopen approval. PM and code reviewer agree this is normative content, not record formatting.
3. **GC-01 / substance / low / advisory, assessed and dismissed as a gate:** PM withdrew the claimed mandatory base change. T-03 `352ceebe` preceded merge `27f8d569`, so the ruling's *before T-03's tip* condition did not apply. The fixed d04c765a population over-includes upstream tests but still covers every feature test. Do not describe it as exclusively feature-owned.

## Evidence and adequacy

- QA: `notes/review-harness-qa-c1.md` — unit 64/64 files and 214 Bun tests green; integration 90/91 files green, `matrix_ok: false`; generated `qa/manifest-integration.json` truthfully has runner_exit 1. All automated SC-01–08 have named coverage and retained failure-first captures. Most historical reds are builder captures, not independently reproduced by QA.
- Dedicated review-pin benchmark ran once, after suites: 177.5 ms sequential / 53.7 ms parallel, ratio **0.302**. Sibling reader activity/load is disclosed; no concurrent suite is reported. The explicit no-other-suite clause is satisfied on QA's account; no speculative rerun requested. Cheap failing-ratio wiring meets the approved SC-04 amendment.
- Code: `notes/review-harness-code-reviewer-c1-assessment.md` supersedes its initial unconditional compliance PASS. Canonical `code-grade.py --base 0d7326e4 --head 6143625f` measured **PASSING: 152**, no failing records. The explicit feature self-grader separately passed 156 functions using its authorized wider fixed base; populations are not interchangeable.
- Security: `notes/review-harness-security-reviewer-c1.md` — no concrete new issue under DEC-255's accepted recorded-execution trust boundary. Static assurance, not execution.
- UI: `notes/review-harness-ui-reviewer-c1.md` — measured no browser/component UI; scoped out correctly.
- PM: `notes/research-FEAT-2337-omp-native-gate-runtime-goalcheck-validate-c1.md`, final addendum — nine SCs met, SC-09 and DEC-255 partial, T-03 owns landing. Operator/orchestrator/reader perspectives met; code maintainer partial. Final evidence replaces initial pending-evidence rows, not their historical record.

## Open question and close duties

Main/operator disposition of the owner-manifest obstacle is required; validator has no authority to deploy it. GC-02 routes to main-session-direct T-03 under DEC-174, not an unauthorized specialist fix. Once authorized remediation lands, verify the new exact pin; preserve this red receipt and failure record. Main must force-add the ignored candidate manifests with the closed run record. This future duty is not marked failed. Installed/control-plane enforcement remains the pre-existing #919 rerun; launcher/version/hash and candidate source identity are separated in QA's note. Known #2356/#2359/#2344/#2257 are not new findings.

```yaml
VERDICT: ESCALATE
DIGEST:
  headline: '6143625f: owner-manifest mismatch blocks integration; T-03 must clarify
    the approved feature-local dirt exception.'
  open_questions:
  - id: GC-03
    question: How will main resolve the owner-manifest landing boundary? Candidate
      QA manifest grant differs from the installed owner manifest, making production
      integration red in the managed linked pin; the same test passes in an independent
      clone. Validator cannot deploy the owner manifest or waive the gate.
    blocking: true
  files_touched:
  - .harness/harness/features/FEAT-2337-omp-native-gate-runtime/runs/r-20261122-4-validate-validator/qa/manifest-unit.json
  - .harness/harness/features/FEAT-2337-omp-native-gate-runtime/runs/r-20261122-4-validate-validator/qa/manifest-integration.json
  - .harness/harness/features/FEAT-2337-omp-native-gate-runtime/notes/research-FEAT-2337-omp-native-gate-runtime-goalcheck-validate-c1.md
  expertise_update: []
  team: validate
  steps_run: 5
  cycles_used: 2
  members:
  - step: qa
    persona: harness-qa
    verdict: ESCALATE
    headline: 64 unit files green; integration 90/91 green with owner-manifest DEVIATION;
      benchmark ratio 0.302.
    files_touched:
    - .harness/harness/features/FEAT-2337-omp-native-gate-runtime/runs/r-20261122-4-validate-validator/qa/manifest-unit.json
    - .harness/harness/features/FEAT-2337-omp-native-gate-runtime/runs/r-20261122-4-validate-validator/qa/manifest-integration.json
  - step: code
    persona: harness-code-reviewer
    verdict: FAIL
    headline: Canonical Python grading passes 152 records; T-03 clean-tree guidance
      contradicts the approved exception.
    files_touched: []
  - step: security
    persona: harness-security-reviewer
    verdict: PASS
    headline: No concrete new security issue under DEC-255's approved trust model;
      static inspection.
    files_touched: []
  - step: ui
    persona: harness-ui-reviewer
    verdict: PASS
    headline: Measured no browser/component UI surface; correctly scoped out.
    files_touched: []
  - step: goalcheck
    persona: harness-pm
    verdict: FAIL
    headline: Nine SCs met; SC-09 and DEC-255 partial, owned by T-03; integration
      remains red.
    files_touched:
    - .harness/harness/features/FEAT-2337-omp-native-gate-runtime/notes/research-FEAT-2337-omp-native-gate-runtime-goalcheck-validate-c1.md
  must_fix:
  - "GC-03 \u2014 Main/operator: resolve the owner-manifest landing boundary before\
    \ claiming green integration. Preserve the red receipt; do not weaken tests or\
    \ silently deploy the control plane."
  - "GC-02 \u2014 T-03, main-session-direct under DEC-174: state the approved trusted-feature-directory\
    \ dirt exception in DEC-255 and matching SPEC/fix-team/QA/validator guidance.\
    \ Preserve behavior. Main sequences verification at the new exact pin after authorized\
    \ remediation."
  branch: none
  escalations:
  - id: GC-03
    raised_by: harness-qa; harness-pm
    question: Production integration fails because candidate QA grant differs from
      control-plane owner manifest; resolving the landing boundary exceeds validator
      authority.
    domain: control-plane owner-manifest deployment and validation environment
    routed_to: Main
    resolution: Unresolved; no source or installed-control-plane changes made. Independent-clone
      attribution is green, but production receipt remains red.
    decided_by: none
    recorded_as: notes/review-harness-qa-c1.md; runs/r-20261122-4-validate-validator/digest.md
  adequacy_notes:
  - ESCALATE preserves QA's authority obstacle above underlying FAIL conditions; this
    is not ship clearance.
  - QA discovered 64 unit and 91 integration files; 214 Bun tests passed. One integration
    file has six named owner-manifest DEVIATION assertions, not a load failure.
  - "Automated SC-01\u201308 have named coverage and retained failure-first evidence.\
    \ Most historical reds are builder captures, not independently reproduced by QA."
  - 'Dedicated benchmark ran once after suites: sequential median 177.5 ms, parallel
    53.7 ms, ratio 0.302. Host load and sibling readers were disclosed; no concurrent
    suite reported. No speculative rerun requested.'
  - 'Canonical grading measured PASSING: 152 for 0d7326e4..6143625f. Explicit feature
    grading separately passed 156 functions using its authorized wider d04c765a base;
    populations differ.'
  - 'GC-01 mandatory base-movement claim explicitly retracted: T-03 352ceebe preceded
    merge 27f8d569, so the ruling''s temporal condition did not apply. Over-inclusion
    remains low advisory.'
  - Code review's initial unconditional compliance PASS is superseded by assessment
    FAIL on GC-02. Security assurance is static; UI decline rests on measured scope.
  - 'Installed enforcement remains pre-existing #919 rerun, not candidate verifier.
    QA made no unconditional PASS claim. Main must force-add ignored manifests with
    the closed run record; integration receipt currently has runner_exit 1.'
  - Two assessment sendbacks completed grading, reconciled findings and incorporated
    final QA. Finding-kind form correction completed without reruns. All children
    terminal.
  sc_status:
  - id: SC-01
    verdict: met
    method: automated
    evidence: 'QA note: budget/heartbeat/delayed-helper tests green; retained natural
      RED.'
  - id: SC-02
    verdict: met
    method: automated
    evidence: 'QA note: runtime/merge-gate timeout tests green, focused 37/37; retained
      natural RED.'
  - id: SC-03
    verdict: met
    method: automated
    evidence: 'QA note: five-gate barrier/order/rejection tests green; retained natural
      RED.'
  - id: SC-04
    verdict: met
    method: automated
    evidence: 'QA note: dedicated review-pin benchmark ratio 0.302; samples and failing-ratio
      nonzero wiring retained.'
  - id: SC-05
    verdict: met
    method: automated
    evidence: 'QA note: shared shard unit and aggregation cases green; retained natural
      RED.'
  - id: SC-06
    verdict: met
    method: automated
    evidence: 'QA note: receipt cases 78/78 and grant cases 21/21; retained natural
      RED. Separate integration environment obstacle remains.'
  - id: SC-07
    verdict: met
    method: automated
    evidence: 'QA note: migrated identity/checkout/refusal cases green; retained natural
      RED.'
  - id: SC-08
    verdict: met
    method: automated
    evidence: Explicit feature grading passes 156 functions at approved base, with
      grade-2 mutant RED; final PM addendum retracts mandatory base movement.
  - id: SC-09
    verdict: partial
    method: inspection
    evidence: 'GC-02, T-03: pinned DECISIONS.md:8428-8433 and standing guidance omit
      approved feature-local dirt exception.'
  - id: SC-10
    verdict: met
    method: inspection
    evidence: 'Pinned cutover inspected by code/PM; QA separately records installed
      launcher identity and unchanged #919 enforcement.'
  - id: DEC-100
    verdict: met
    method: inspection
    evidence: Pinned DECISIONS.md:1372-1421 replaces nominated clause in place; T-03.
  - id: DEC-255
    verdict: partial
    method: inspection
    evidence: 'GC-02, T-03 owns D-02 landing: approved feature-directory exception
      missing from current normative guidance.'
  - id: perspective:operator
    verdict: met
    method: goalcheck
    evidence: 'Final PM addendum: SC-01/02/03/07 discharged.'
  - id: perspective:orchestrator
    verdict: met
    method: goalcheck
    evidence: 'Final PM addendum: SC-04/06 discharged; whole integration gate remains
      red.'
  - id: perspective:code maintainer
    verdict: partial
    method: goalcheck
    evidence: 'Final PM addendum: SC-05 met, SC-09 partial due to GC-02.'
  - id: perspective:reader
    verdict: met
    method: goalcheck
    evidence: 'Final PM addendum: SC-08/10 discharged, grading population and installed/candidate
      boundaries disclosed.'
  needs_approval: false
  severity_max: high
  matrix_ok: false
  coverage_gaps:
  - 'Production integration gate is red: test-check-plan-routes.py fails on linked-checkout
    owner-manifest divergence.'
  - SC-09 normative guidance omits settled feature-local dirt exception.
  - Historical failure-first captures primarily builder evidence, not independent
    historical reproductions by QA.
  findings:
  - kind: substance
    scope: none
    severity: high
    reader: harness-pm; harness-qa
    summary: 'GC-03: owner-manifest boundary prevents green production integration;
      main/operator disposition required.'
    why: Candidate T-03 QA grant differs from control-plane owner manifest. Managed-pin
      production run fails test-check-plan-routes.py; independent clone passes. Environmental/non-product
      gate obstacle, not authorization for source workaround. PM corrected initial
      invalid kind to substance; high severity retained.
  - kind: substance
    scope: none
    severity: med
    reader: harness-pm; harness-code-reviewer
    summary: 'GC-02: T-03 must document approved feature-local dirt exception consistently.'
    why: DEC-255, SPEC, fix team and QA/validator guidance require unqualified cleanliness,
      while approved follow-up and implementation permit normal dirty feature records.
      Following current policy can incorrectly reject a valid live fix run. Normative
      content disagreement leaves SC-09/D-02 partial.
  - kind: substance
    scope: none
    severity: low
    reader: harness-pm
    summary: 'GC-01: wider grading population advisory; mandatory base-movement finding
      assessed and dismissed.'
    why: T-03 committed before later upstream merge, so ruling's conditional movement
      did not apply. Every feature test remains covered and green. Retain population
      caveat, not an unauthorized requirement to change constant.
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
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2337-omp-native-gate-runtime/.harness/harness/features/FEAT-2337-omp-native-gate-runtime/runs/r-20261122-4-validate-validator/digest.md
```
