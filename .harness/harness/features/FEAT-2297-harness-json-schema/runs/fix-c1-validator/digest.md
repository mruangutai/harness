# FEAT-2297 re-validation — FAIL only on pending CI ship proof

**All prior code/form repairs clear; no development rework is requested.** Whole diff reviewed at head/review pin `fa6a38009e54f4380daebd59a78629a68de7c1d0`, measured base `9fd1f6b414ed683cd5f5bcca4ad5fe17c35e0568`. Raw QA FAIL is preserved: unit **65/65**, integration **94/95**. Sole red remains `test-corpus-real-owner.py` against installed owner v2; candidate and linked caller are v3. No other red. Runner-owned receipts: `qa/manifest-{unit,integration}.json`, both tested at the exact pin, runner exits 0/1.

## Ranked disposition
1. **High, substance, Main ship/T-10 evidence:** obtain green PR CI including the real-owner case and record its run ID before ship. This is settled E-OWNER execution, not a new operator decision, code defect or reason to upgrade shared main. The local red is neither waived nor relabeled green. Thus consolidated FAIL (worst member), not unconditional clearance; route to PR CI, not another development cycle.
2. **Low, substance, T-01 assurance advisory:** non-object root regression currently samples arrays, not named null/number/string roots. QA's prior probes establish correct refusal. No demonstrated implementation defect; not must-fix.

## Closures and reconciliation
- Both newline schema guards independently discriminate: QA reproduced two failures with old schema, one failure per removed guard, then 12 tests green. Root and upgrade-source/no-write assertions now exist; already-correct behavior has no natural red, honestly recorded rather than demanded.
- T-08 receipt pointer/delegation wording repaired. T-10 exact-pin checker passes: existing **-583**, new **+1575**, reported total **+992**, **152** dispositions/**67** assessed files. Recorded measurement ref `8c945a8e` differs only in non-counted feature records from the pin; not stale measurement. Reader audit: **0 unresolved / 101 Python files**.
- PM grades all three perspectives, ten SCs and DEC-221/254 dispositions met under signed amendments. Fresh QA now corroborates its pending local evidence without claiming green real-owner CI. SC-08 amendment and E-OWNER ruling remain settled. Post-hoc personal acceptance/revert remedy stays in Main's ship briefing.
- Code spec **and quality** stages complete; Python grade pass (155 records). Security static audit clean; UI correctly scopes out on a measured 175-object diff. QA supplies execution/mutation evidence; those other lenses do not supply suite execution. QA's statement that other readers did not re-read the schema is not adopted: code/security explicitly reviewed its guards.
- QA's `integration: missing` is a contract encoding limitation, not zero discovery: 95 files ran, one failed. Preserve the raw receipt and route the enum gap as nonblocking Harness feedback.

## Reader artifacts
Under feature `notes/`: `review-harness-qa-c2.md` (**FAIL**); `review-harness-code-reviewer-c2.md`, `review-harness-security-reviewer-c2.md`, `review-harness-ui-reviewer-c2.md`, `research-FEAT-2297-harness-json-schema-goalcheck-validate-c2.md` (**PASS** each). No source edits; zero send-backs. Open product decisions: **none**. Outstanding action: **Main's green PR-CI run ID at ship**.

```yaml
VERDICT: FAIL
DIGEST:
  headline: fa6a3800 repairs clear; unit 65/65, integration 94/95 with only disposed
    owner-v2 red; green PR CI remains the ship gate.
  open_questions:
  - id: OQ-KIND-ENUM
    question: 'Harness owner: should QA''s kind-state contract represent ran-and-red
      explicitly? Integration ran 95 files but is encoded as missing because no red
      state exists; raw receipts remain authoritative.'
    blocking: false
  files_touched: []
  expertise_update: []
  team: validate
  steps_run: 5
  cycles_used: 0
  members:
  - step: qa
    persona: harness-qa
    verdict: FAIL
    headline: Unit 65/65; integration 94/95, sole owner-v2 red attributed; newline
      mutations, reduction checker and reader audit pass.
    files_touched: []
  - step: code
    persona: harness-code-reviewer
    verdict: PASS
    headline: Whole pinned diff passes spec and quality stages; Python grade passes.
    files_touched: []
  - step: security
    persona: harness-security-reviewer
    verdict: PASS
    headline: Full pinned input-boundary static audit finds no exploitable regression.
    files_touched: []
  - step: ui
    persona: harness-ui-reviewer
    verdict: PASS
    headline: Measured 175-object diff contains no implemented rendered or interactive
      UI; scoped out.
    files_touched: []
  - step: goalcheck
    persona: harness-pm
    verdict: PASS
    headline: Three perspectives, ten amended SCs and both decision dispositions met;
      CI ship proof remains required.
    files_touched: []
  must_fix:
  - 'Main ship / T-10 evidence: obtain green PR CI including test-corpus-real-owner.py
    against the v3 PR owner and record its run ID before ship. This executes settled
    E-OWNER; no development rework or shared-main upgrade is requested.'
  branch: none
  escalations:
  - id: E-OWNER
    raised_by: harness-qa
    question: How is the sole installed-v2-owner integration red discharged?
    domain: ship verification
    routed_to: Main
    resolution: 'Settled advisor ruling #6: authoritative confirmation is green PR
      CI against the v3 PR owner, with run ID recorded at ship. Exact-pin local attribution
      and absence of other reds verified; CI execution remains outstanding.'
    decided_by: 'Designated advisor under operator delegation, ruling #6'
    recorded_as: notes/qa-config-reduction.md; runs/fix-c1-validator/digest.md
  adequacy_notes:
  - Reviewed entire fa6a38009e54f4380daebd59a78629a68de7c1d0 diff against independently
    measured merge-base 9fd1f6b414ed683cd5f5bcca4ad5fe17c35e0568; head_sha is the
    reviewed pin.
  - FAIL preserves QA's raw failed gate and worst-member roll-up. No remaining code-remediation
    finding is established; route to PR CI, not another development cycle.
  - DEC-255 runner-owned manifests under runs/fix-c1-validator/qa/ bind both kinds
    to the exact pin. Unit runner_exit=0; integration runner_exit=1. QA verified only
    test-corpus-real-owner.py failed against installed owner v2; candidate and linked
    caller are v3.
  - 'matrix_ok=true reports evaluated floors and mapped kinds, not unconditional suite
    green. QA''s integration state missing is an enum limitation, not absent execution:
    95 files ran.'
  - QA independently reproduced both newline failures with the old schema, one failure
    per removed guard, and green restored behavior. New root and missing/unparseable
    upgrade-source assertions cover already-correct behavior; no natural red was fabricated
    or demanded.
  - 'Exact-pin reduction checker passes signed Gate A/B: existing -583, new +1575,
    reported total +992, 152 dispositions, 67 files. Committed measurement ref 8c945a8e
    has identical counted subjects to the pin; metadata-only difference is not stale
    measurement.'
  - Canonical reader audit independently reports zero unresolved sites across 101
    Python files.
  - Both code-review stages now pass; Python mechanical grade passes 155 records.
    Security is static-only; UI scopes out by actual census. Only QA contributes suite
    execution and mutation evidence.
  - 'QA''s assertion that other readers did not re-read the schema is not adopted:
    code and security explicitly inspected the repaired guards.'
  - PM's initially pending fresh QA is reconciled by the completed exact-pin run.
    All product perspectives and amended SCs remain met; green real-owner PR CI remains
    an independent ship obligation.
  - 'SC-08 amendment, D-01..D-08 and recorded amendments, INV-13 retirement, #2393
    deferral and E-OWNER disposition remain settled. Main''s ship briefing retains
    post-hoc personal acceptance and its recorded Kaya revert remedy.'
  - Prior T-08 receipt-pointer/delegation form issue and T-10 measurement form issue
    are closed. No product source edited; zero send-backs.
  sc_status:
  - id: SC-01
    verdict: met
    method: automated
    evidence: 'notes/review-harness-qa-c2.md: loader suite passes; newline baseline
      and per-guard mutations fail; named array-root refusal assertion present.'
  - id: SC-02
    verdict: met
    method: automated
    evidence: Reader/gate refusal regressions pass at exact pin; c1 baseline refusal
      reds remain bound to unchanged production. notes/review-harness-qa-c2.md
  - id: SC-03
    verdict: met
    method: automated
    evidence: Upgrade regressions pass, including named missing/unparseable-source
      diagnosis and no-write assertions; c1 migration fail-first retained.
  - id: SC-04
    verdict: met
    method: automated
    evidence: Fixture census, helper delegation and generated TypeScript freshness
      pass; baseline bypass evidence retained.
  - id: SC-05
    verdict: met
    method: automated
    evidence: 'Exact-pin checker and negative controls pass signed Gate A/B: -583
      existing, +1575 new, +992 total, 152 dispositions/67 files.'
  - id: SC-06
    verdict: met
    method: automated
    evidence: 'Exact-pin canonical audit: zero unresolved/101 Python files; non-config
      regression and baseline wrong-route evidence retained.'
  - id: SC-07
    verdict: met
    method: inspection
    evidence: Code Stage 1 confirms pinned authority/schema agreement, regenerated
      index and repaired honest Kaya receipt pointer.
  - id: SC-08
    verdict: met
    method: uat
    evidence: Signed amended criterion governs; notes/uat-kaya-migration.md records
      delegated authorization, Kaya PR29, b9dec8df landing and validated v3 readback;
      no personal-review claim.
  - id: SC-09
    verdict: met
    method: automated
    evidence: Exact-pin unit 65/65 and mapped integration evidence cover runtime/config
      floors; sole real-owner red remains subject to settled PR-CI ship confirmation.
  - id: SC-10
    verdict: met
    method: automated
    evidence: Exact-pin integration 94/95 preserves cross-process and unrelated semantics;
      only installed-v2-owner case remains for authoritative PR CI.
  - id: DEC-221
    verdict: met
    method: inspection
    evidence: "PM verifies pinned DECISIONS.md:7311\u20137315 and index:217; T-08/T-10\
      \ amendment landing complete."
  - id: DEC-254
    verdict: met
    method: inspection
    evidence: "PM verifies pinned DECISIONS.md:8357\u20138367 and index:237; T-08/T-10\
      \ amendment landing complete."
  needs_approval: false
  severity_max: high
  matrix_ok: true
  coverage_gaps:
  - 'T-01 advisory: non-object-root refusal has named array coverage, but not separate
    null/number/string assertions; prior QA probes show correct refusal.'
  - 'Ship evidence pending: real-owner case must pass in authoritative PR CI and the
    green run ID must be recorded.'
  findings:
  - kind: substance
    scope: none
    severity: high
    reader: harness-qa
    summary: 'Main ship/T-10 evidence: authoritative real-owner PR-CI proof remains
      pending.'
    why: Exact-pin integration is honestly red only against installed owner v2. Settled
      E-OWNER requires green PR CI and recorded run ID before ship; this is verification
      execution, not a new code defect or scope decision.
  - kind: substance
    scope: none
    severity: low
    reader: harness-qa
    summary: 'T-01 advisory: named non-object-root assertions sample arrays, not null/number/string
      separately.'
    why: Prior probes demonstrate correct refusal; this is bounded regression-assurance
      debt, not a demonstrated implementation failure or must-fix.
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
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2297-harness-json-schema/.harness/harness/features/FEAT-2297-harness-json-schema/runs/fix-c1-validator/digest.md
```
