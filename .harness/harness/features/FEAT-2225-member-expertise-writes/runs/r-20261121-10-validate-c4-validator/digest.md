# Validate c4 — FAIL

**Pin a5d8687f31c9f05fa77f4d16f3634c3869f47b1f: F1/F3 CLOSED; F2 ACCEPTED BOUNDARY; fresh integration is red because the amendment left DECISIONS-INDEX.md stale.** No code remediation or additional fix round occurred.

## Consolidated assessment

1. **C4-F1 / medium / T-02 — must fix:** regenerate `.harness/harness/docs/DECISIONS-INDEX.md` after the DEC-253 amendment. QA measured the named integration assertion `test_committed_index_matches_a_fresh_regeneration` failing and T-02's literal generator/diff verify exiting 1. The committed row has `[expertise,dispatch,worktree,map]`; regenerated output has `[expertise,dispatch,state,worktree]`. This is a new amendment-induced documentation-sync failure, not F2 reopened. Read-only validation cannot perform the repair. Evidence: `notes/review-harness-qa-c4.md`.
2. **C4-W1 / low / form / T-04 (T-01 shared verifier) — advisory:** code reviewer identifies live-yield prose that does not share the explicit local-ref qualifier written for durable close, although both use the same verifier. Retain as a wording qualification, not another implementation demand or reversal of the operator ruling. Evidence: `notes/review-harness-code-reviewer-c4.md`.
3. **N3/N4 / low / substance / T-01/T-04 — prior advisories retained:** trusted explicit-base/self-anchor behavior remains unchanged; N4 overlaps the ruled F2 family. Neither gates. Raw red-log volatility remains an evidence-durability limitation, not a new defect.

## Assurance and reconciliation

QA measured zero code-diff bytes outside `.harness/` between 219690d0 and this pin. Fresh unit: 61 discovered/run files, 1136 PASS lines, exit 0. Fresh integration: 88 discovered/run files, 2921 PASS lines and one failing file, exit 1; all commands used `env -u HARNESS_AGENT_TYPE`. T-01/T-04 literal verifies pass. SC-01..05 retain per-SC fail-first pointers and current covering tests; the whole integration kind is NOT green. QA's `matrix_ok: true` denotes floor presence, not suite success; the team reports the combined gate as false.

Code/security source-confirm local-ref-relative close verification and fresh-remote replay/committed-blob refusal at merge-distill, including owner/binding/mirror checks. They reuse c3's executed F2 demonstration; containment this round is source-derived, not a fresh exploit run. F2's historical high severity is not rewritten: its disposition changed by operator ruling, tracked in #2251, and it is not a surviving finding. F1/F3 remain closed from unchanged c3 subjects plus fresh covering tests.

Goalcheck's initial all-met return inherited c3's index evidence; fresh QA supersedes that premise for SC-06 and the code-maintainer perspective. Do not interpret a source-equivalent implementation as documentation-equivalent: generated tags depend on amended prose. UI measured 17 c3→c4 documentation/record paths and a 104-path full census with no visual surface; accessibility/theme parity are not applicable, not visually passed.

Reader artifacts: `notes/review-harness-{qa,code-reviewer,security-reviewer,ui-reviewer}-c4.md`; `notes/research-FEAT-2225-member-expertise-writes-goalcheck-validate-c4.md`. All under the assigned feature directory. No source edits, commits, pushes or gh. Open questions: none. No new fix-round authorization is inferred from this failure.

## Final receipt corrections

QA classifies C4-F1 **substance / medium / T-02**, because a shipped generated artifact disagrees with its authority and fails a named assertion; its earlier invalid `test/documentation-sync` label is withdrawn. Preserve this identity unchanged. PM corrected its inherited PASS to **FAIL**, SC-06 **partial**, code-maintainer perspective **partial**; operator/orchestrator and SC-01..05 stay met. These are same-run receipt/evidence corrections, not another panel, source fix or test rerun; `cycles_used: 0` records no team re-dispatch or fix round. One must-fix is deduplicated across QA and goalcheck. C4-W1 remains advisory and requires no unapproved document edit in this run. No reviewer recommends reopening F2.

```yaml
VERDICT: FAIL
DIGEST:
  headline: 'a5d8687f31c9f05fa77f4d16f3634c3869f47b1f: F1/F3 CLOSED, F2 ACCEPTED BOUNDARY;
    stale DEC-253 index makes integration red.'
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
    headline: 'Unit green; integration present-but-red: stale DEC-253 index; fail-first
      retained.'
    files_touched: []
  - step: code
    persona: harness-code-reviewer
    verdict: PASS
    headline: Amended promises match pinned code; low live-yield wording advisory.
    files_touched: []
  - step: security
    persona: harness-security-reviewer
    verdict: PASS
    headline: F2 accepted boundary accurately described and source-confirmed merge-contained;
      F1/F3 closed.
    files_touched: []
  - step: ui
    persona: harness-ui-reviewer
    verdict: PASS
    headline: Measured 17 amendment-delta paths and 104 full-range paths; no visual
      UI.
    files_touched: []
  - step: goalcheck
    persona: harness-pm
    verdict: FAIL
    headline: SC-01..05 met; SC-06 and code-maintainer perspective partial because
      generated index is stale.
    files_touched: []
  must_fix:
  - 'C4-F1 / medium / substance / T-02: regenerate .harness/harness/docs/DECISIONS-INDEX.md
    after the DEC-253 amendment and re-pin. Committed tags [expertise,dispatch,worktree,map]
    differ from generated [expertise,dispatch,state,worktree]; the named integration
    assertion and T-02 literal verify fail. No repair or further fix-round authorization
    inferred.'
  branch: none
  escalations: []
  adequacy_notes:
  - QA measured zero diff bytes outside .harness/ from 219690d0 to the review pin.
    Implementation equivalence does not imply generated-document equivalence.
  - 'Fresh env -u HARNESS_AGENT_TYPE matrix: unit 61 discovered/run files, 1136 PASS
    lines, exit 0; integration 88 discovered/run files, 2921 PASS lines, one failing
    file, exit 1. T-01/T-04 literal verifies pass; T-02 generator/diff exits 1.'
  - QA matrix_ok:true denotes required-kind presence. Integration is present-but-red,
    encoded missing because its schema lacks a red state. Team matrix_ok:false records
    the unsuccessful combined gate.
  - 'C4-F1 deduplicates QA and corrected goalcheck. Preserve QA''s substance/medium
    classification: a generated artifact disagrees with authority and fails a named
    assertion.'
  - PM's initial all-met return is superseded by corrected FAIL after fresh QA contradicted
    inherited index evidence. Operator/orchestrator remain met; code maintainer is
    partial. This is validate-phase SC-09 goalcheck following the authorized amendment.
  - F2 historical high/substance remains in c3 evidence but is operator-accepted,
    not repaired or silently re-rated. No reader recommends reopening it. Current
    live-remote merge containment is source-derived; prior executed exploit and existing
    merge tests are reused.
  - 'C4-W1 remains low/form advisory: live yield shares the accepted local-ref limitation
    although prose explicitly qualifies durable close. No implementation change or
    reversal of the ruling requested.'
  - F1/F3 closure carries from unchanged c3 subjects plus fresh covering tests. N3/N4
    remain advisory low; N4 overlaps ruled F2.
  - Same-run receipt classification and evidence corrections caused no new panel,
    test rerun, source fix or team re-dispatch; cycles_used is 0.
  - UI measured scope before self-scoping out; accessibility/theme parity are not
    applicable, not visually passed. Existing handoff probe evidence is referenced,
    not freshly executed.
  - No source edits, commits, pushes or gh. Reader notes and lead run bookkeeping
    are the only writes.
  sc_status:
  - id: SC-01
    verdict: met
    method: automated
    evidence: 'notes/review-harness-qa-c4.md: fresh host/core representatives and
      all-16 configuration tests; inherited fail-first in review-harness-qa-c3.md
      and red-first-T-04-host.md.'
  - id: SC-02
    verdict: met
    method: automated
    evidence: 'notes/review-harness-qa-c4.md: schema/validate-digest covering tests
      and fail-first; notes/research-FEAT-2225-member-expertise-writes-goalcheck-validate-c4.md
      distinguishes receipt consistency from amended ancestral-baseline authority.'
  - id: SC-03
    verdict: met
    method: automated
    evidence: 'notes/review-harness-qa-c4.md: fresh authority/guard/core tests and
      inherited fail-first; code/security c4 notes source-confirm local-ref close
      and live-remote merge containment under ruling.'
  - id: SC-04
    verdict: met
    method: automated
    evidence: 'notes/review-harness-qa-c4.md: T-01 verify green, replay/collision/supersession
      tests; fail-first in receipt-harness-backend-dev-T-01-c1.md and red-first-fix-c2-core.md.'
  - id: SC-05
    verdict: met
    method: automated
    evidence: 'notes/review-harness-qa-c4.md: merge-gate/Main-hook tests green; notes/red-first-t04-merge-gate.md
      fail-first; security c4 confirms live-remote replay/blob and owner/mirror predicates.'
  - id: SC-06
    verdict: partial
    method: inspection
    evidence: notes/research-FEAT-2225-member-expertise-writes-goalcheck-validate-c4.md
      retains pinned guidance inspection but retracts inherited index clearance; notes/review-harness-qa-c4.md
      proves DEC-253 index mismatch, integration assertion failure and T-02 verify
      exit 1.
  needs_approval: false
  severity_max: med
  matrix_ok: false
  coverage_gaps:
  - No regression directly pins N3/N4 explicit-HEAD/default-ref self-anchor cases;
    advisory low within documented boundary.
  - Raw fail-first logs remain volatile; durable notes preserve commands/outcomes,
    not complete raw output.
  - Null TypeScript typecheck remains a disclosed gap; no static typecheck success
    claimed.
  findings:
  - kind: substance
    scope: none
    severity: med
    reader: qa, goalcheck
    summary: 'C4-F1 / T-02: DEC-253 generated index is stale after amendment.'
    why: Committed tags [expertise,dispatch,worktree,map] differ from generated [expertise,dispatch,state,worktree].
      test_committed_index_matches_a_fresh_regeneration and T-02 literal verify fail.
      New amendment-induced failure, not F2 reopened.
  - kind: form
    scope: none
    severity: low
    reader: code-reviewer
    summary: 'C4-W1 / T-04 (T-01 shared verifier): live-yield wording omits shared
      local-ref limitation.'
    why: SPEC:945 and DEC-253:8201-8202 qualify durable close but not live yield;
      both invoke the same verifier without independent base. Nonblocking wording
      advisory, not implementation demand.
  - kind: substance
    scope: none
    severity: low
    reader: qa
    summary: 'N3 / T-01: explicit feature-HEAD base self-anchors; existing advisory.'
    why: Unchanged code; current callers provide trusted fetched base or no explicit
      base. No new blocking scenario.
  - kind: substance
    scope: none
    severity: low
    reader: qa
    summary: 'N4 / T-01 + T-04: default-ref self-anchor advisory overlaps ruled F2.'
    why: 'QA original low rating preserved; local-ref manipulation is accepted at
      close and contained at live-remote replay/merge, tracked by #2251.'
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
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2225-member-expertise-writes/.harness/harness/features/FEAT-2225-member-expertise-writes/runs/r-20261121-10-validate-c4-validator/digest.md
```
