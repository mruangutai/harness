# Validate digest — FEAT-2581, round 2, review_sha a03103b0

**FAIL, on one med finding in T-03's proof tooling.** The fix round's claims hold under execution.
- CR-1 is closed: the DEC-209 code grade over e12381fd..a03103b0 exits 0, with nothing below grade 4.
- CR-2's generator half is closed: all 18 null, blank, non-string and missing-key mutants are UNRULED and give overall FAIL, and the 631 real rulings still give PASS.
- SEC-1 is closed for all four scratch leaves.
- The regenerated receipt differs from the prior one only in the five script_sha256 lines and the stamp.
- pm grades SC-01..SC-10 met, and both perspectives pass. QA's matrix is green with runner receipts, and the T-01, T-02 and T-03 verifies exit 0 at the pin.

What still fails: SEC-1's protection does not reach the ledger's parent directory. Security and QA each reproduced this on their own, and the security reviewer returned FAIL with it as must_fix. Under worst-wins roll-up, the team verdict is FAIL. The remedy is cheap and lies inside T-03's files.

Gate policy is `gates.review: advisory_unless_high`, and severity_max is med. The FAIL comes from a member's FAIL and must_fix, not from a high severity.

## Members

| Step | Persona | Verdict | Note |
|---|---|---|---|
| qa | harness-qa | PASS | unit 68/68 and integration 94/94 exit 0, with receipts at `runs/2026-11-27-02-validate-validator/qa/manifest-{unit,integration}.json`. The T-01, T-02 and T-03 verifies exit 0. Raised QA-c2-1 (low). `notes/review-harness-qa-c2.md` |
| code | harness-code-reviewer | PASS | Seven predictions executed; all pass except the literal scope count (explained below). CR-3 (med) and CR-4 (low, form) are advisory. `notes/review-harness-code-reviewer-c2.md` |
| security | harness-security-reviewer | FAIL | SEC-1 residual (med): the ledger parent is accepted unchecked. `notes/review-harness-security-reviewer-c2.md` |
| ui | harness-ui-reviewer | PASS | Out of scope. A census of 146 pinned paths found no rendered UI. `notes/review-harness-ui-reviewer-c2.md` |
| goalcheck | harness-pm | PASS | SC-01..SC-10 and DEC-259, DEC-220 and DEC-150 met, with no regression from 62da4501. Raised F-1 (low, form). `notes/research-FEAT-2581-feature-record-package-goalcheck-validate-c2.md` |

## Claims from the dispatch, confirmed or refuted

- **The fix commit touches only the 7 files claimed: confirmed.** `git diff-tree a03103b0` lists the five receipt scripts and the two receipts. `62da4501..a03103b0` spans 20 files. The extra 13 come from the three intervening `[harness:human]` review and registration commits, not from the fix.
- **CR-1 closed (code-grade exits 0): confirmed** by the code reviewer and independently by pm (279 records, 0 FAIL).
- **CR-2 generator half: confirmed.** Every leg has a discriminating mutant. At c1, the nine null, integer and list mutants passed as RULED, so this is a real closure.
- **SEC-1: partly refuted.** The leaves are fail-loud and recreated with mode 0700 at unchanged paths. The parent is still created with `makedirs(exist_ok=True)`, which accepts an existing directory as it is.
- **Receipt regenerated with only script hashes and the stamp changed: confirmed.** A scratch `--reuse` regeneration matched the committed receipt byte for byte, excluding the stamp. `build-divergences.md`, the rulings and the measurements are byte-identical, and all 631 ruled ids are unchanged.
- **Provenance:** clean-pin-byte-receipts.md:15–20 states that the capture-script bytes came from c65ceb81. The receipt's hashes identify the current scripts, not the ones that ran the capture. The code reviewer judges this honest, and I accept that ruling.

## Findings, ranked

1. **SEC-1 residual · med · substance · T-03 (security med, QA low).** Both readers report the same defect, so it counts as one finding.
   - **Where:** `notes/receipt-scripts/feat2581-ledger-driver.py:118–121`. `prepare_scratch` accepts an existing `/tmp/feat2581-ledger` that is a symlink, writable by everyone (0777), or owned by another account. Both readers reproduced this.
   - **Risk:** another local account could swap the private `baseline` or `pin` leaf. Later reads by path would then take in substituted capture data. The readers inferred this and did not execute it. The gap already existed at 62da4501, and the frozen measurements are not affected.
   - **Severity:** I take security's med. Trust-boundary severity is security's lens, and QA's low reflects the reuse path, not the regeneration path.
   - **Remedy:** refuse a parent that is a symlink, is not owned by the invoking user, or is writable by group or others. Alternatively, create it with `mkdir 0700` under the same fail-loud discipline as the leaves. The path bytes stay unchanged.
2. **CR-3 · med · substance · T-03 (code-reviewer), advisory.** Setting `signal.signal(SIGKILL, SIG_DFL)` in `recorder/sitecustomize.py:153–176` raises at startup, so a child that was SIGKILLed can run a second time.
   - **Evidence:** executed on both c1 and c2. The ledger recorded -9 with one write, but the wrapper exited 0 with two writes.
   - **Impact today:** none. Neither committed CLI ledger has a negative status.
   - **Not must_fix because:** changing the recorder widens the gap between the capture-time bytes and the current scripts without re-measuring, which is a provenance cost the readers did not weigh. Fixing it is optional. If it is fixed, the disclosure in clean-pin-byte-receipts.md must name it.
3. **CR-4 · low · form · T-03 (code-reviewer).** The footer of the generated receipt (`feat2581-cleanpin.py:494–501`) calls two digests "normalized". They are hashes of the raw JSONL, because roots are substituted before the base64 streams are decoded.
   - **Impact:** none on the verdict, since the actual comparison decodes before normalizing.
   - **Why fold it in:** it is a false label in the record and costs one line in the same file family as finding 1, so it can go in the same commit.
4. **F-1 · low · form (pm), not routed.** answers-2026-11-27-validate-escalate.md says "no committed tool writes divergence-rulings.json". In fact `load_rulings` seeds `[]` when the file is absent. The risk argument still holds, but this is the operator's own record, so the wording is the operator's call. Raised as a non-blocking question.
5. **CR-2 verifier half:** operator-dispositioned accepted risk. Noted, not raised again.

## Fix order

Make one T-03 commit that fixes the SEC-1 parent, together with CR-4's footer label if it is taken. Then regenerate with `--reuse`; expect only script_sha256 and stamp changes, plus the footer label lines if CR-4 is fixed. Rerun the T-03 verify at the new tip, and confirm the code grade still exits 0. Leave CR-3 unchanged unless the operator wants it.

## Adequacy

- SC-03 and SC-04 fail-first evidence uses the identity equivalent the BRIEF designates, not a natural red run. That is accepted by design.
- The code reviewer's T-03 verify ran with runtime registration bound to c2. The `feature.json` blob committed at a03103b0 still holds the c1 pin, because a pin cannot contain itself. The working-tree `feature.json` records review_sha a03103b0, which I checked.
- Falsification evidence came from all three executing readers: code (mutants and both-side predicate runs), security (isolated execution of `prepare_scratch` and the leaf helpers), and QA (runner receipts and the parent probe). Security did not exercise the cross-account swap itself.

```yaml
VERDICT: FAIL
DIGEST:
  headline: 'FEAT-2581 at a03103b0: CR-1, the CR-2 generator half and the regeneration
    claims are confirmed by execution; SC-01..SC-10 met; qa green. One med T-03 finding
    still gates (security FAIL, QA concurs): SEC-1 does not cover the /tmp/feat2581-ledger
    parent, which is accepted unchecked. Cheap, legal fix'
  open_questions:
  - id: OQ-V2-1
    question: 'F-1 (pm, low, form): answers-2026-11-27-validate-escalate.md says ''no
      committed tool writes divergence-rulings.json'', but feat2581-cleanpin.py load_rulings
      seeds ''[]'' when the file is absent. Should the operator reword it to ''no
      committed tool writes ruling metadata''? The risk argument is unaffected.'
    blocking: false
  - id: OQ-V2-2
    question: 'CR-3 (code-reviewer, med, advisory): the recorder''s signal.signal(SIGKILL)
      raises at startup, so a SIGKILLed CLI child can run a second time. No committed
      ledger is affected. Fix it (this widens the capture-vs-current script provenance
      gap) or leave it as is?'
    blocking: false
  files_touched:
  - .harness/harness/features/FEAT-2581-feature-record-package/runs/2026-11-27-02-validate-validator/qa/manifest-unit.json
  - .harness/harness/features/FEAT-2581-feature-record-package/runs/2026-11-27-02-validate-validator/qa/manifest-integration.json
  expertise_update: []
  team: validate
  steps_run: 5
  cycles_used: 0
  members:
  - step: qa
    persona: harness-qa
    verdict: PASS
    headline: 'Unit 68/68 and integration 94/94 exit 0, with runner receipts. T-01/T-02/T-03
      verifies exit 0 at a03103b0. Raised QA-c2-1: low, ledger parent accepted.'
    files_touched:
    - .harness/harness/features/FEAT-2581-feature-record-package/runs/2026-11-27-02-validate-validator/qa/manifest-unit.json
    - .harness/harness/features/FEAT-2581-feature-record-package/runs/2026-11-27-02-validate-validator/qa/manifest-integration.json
  - step: code
    persona: harness-code-reviewer
    verdict: PASS
    headline: 'CR-1 and the CR-2 generator half are closed, and all three signed verifies
      pass at a03103b0. Two advisory T-03 findings: CR-3 med, CR-4 low form.'
    files_touched: []
  - step: security
    persona: harness-security-reviewer
    verdict: FAIL
    headline: 'SEC-1 is still open: all four scratch leaves fail closed, but T-03
      accepts an unsafe ledger parent.'
    files_touched: []
  - step: ui
    persona: harness-ui-reviewer
    verdict: PASS
    headline: 'Out of scope: no rendered UI across 146 pinned paths.'
    files_touched: []
  - step: goalcheck
    persona: harness-pm
    verdict: PASS
    headline: Both perspectives pass; SC-01..SC-10 and DEC-259/220/150 met; no regression
      from 62da4501. F-1 is low form.
    files_touched: []
  must_fix:
  - 'SEC-1 residual (T-03, security med; QA reported the same defect as low): feat2581-ledger-driver.py:118-121
    prepare_scratch creates /tmp/feat2581-ledger with makedirs(exist_ok=True), which
    accepts an existing symlink, a 0777 directory, or one owned by another account.
    Refuse a parent that is a symlink, is not owned by the invoking user, or is group/other-writable,
    or create it fail-loud with mode 0700 like the leaves. Keep the path bytes unchanged.
    Then regenerate with --reuse (only script_sha256 and stamp lines should change,
    plus CR-4''s footer label lines if folded in), rerun the T-03 verify at the new
    tip, and confirm the code-grade still exits 0. Show a discriminating probe for
    each refused parent shape.'
  branch: feat/FEAT-2581-feature-record-package
  escalations: []
  adequacy_notes:
  - 'Dispatch claims checked by execution: the fix commit touches exactly 7 files
    (git diff-tree a03103b0). 62da4501..a03103b0 spans 20 files because of three intervening
    [harness:human] bookkeeping commits. code-grade exits 0 with nothing below grade
    4. All 18 CR-2 mutants give UNRULED and overall FAIL (at c1, 9 of them passed
    as RULED). A scratch --reuse regeneration matched byte for byte excluding the
    stamp. build-divergences.md, the rulings and the measurements are byte-identical,
    and all 631 ids are unchanged.'
  - 'Provenance: the receipt''s script_sha256 values identify the refactored scripts,
    not the c65ceb81 bytes that took the capture. clean-pin-byte-receipts.md:15-20
    discloses this, and the code reviewer judges it honest.'
  - The SEC-1 residual existed already at 62da4501 and does not touch the frozen measurements.
    The cross-account swap was inferred, not executed. The severity reconciliation
    took security's med over QA's low, because trust boundaries are security's lens.
  - 'CR-4 (low, form, T-03): the generated-receipt footer calls raw-JSONL digests
    ''normalized''. Recommend folding it into the same commit; it does not affect
    the verdict.'
  - The CR-2 verifier half is operator-dispositioned accepted risk. It is not raised
    again.
  - The gate here is advisory_unless_high and severity_max is med. The FAIL comes
    from the security member's FAIL and its must_fix under worst-wins roll-up.
  - SC-03/SC-04 fail-first evidence is the identity equivalent the BRIEF designates,
    by design.
  sc_status:
  - id: SC-01
    verdict: met
    method: inspection
    evidence: T-01 verify exit 0 at a03103b0; feature_record/ unchanged since 62da4501
      (pm, code)
  - id: SC-02
    verdict: met
    method: inspection
    evidence: 'grade-assert: pin exit 0, baseline exit 1 naming the twelve; full-range
      code-grade e12381fd..a03103b0 exit 0 (pm, code)'
  - id: SC-03
    verdict: met
    method: automated
    evidence: qa manifest-unit.json 68/68 exit 0 at a03103b0; claim-mutation's 4 FAIL
      lines byte-identical to baseline
  - id: SC-04
    verdict: met
    method: automated
    evidence: qa manifest-integration.json 94/94 exit 0; baseline_failing only test-typescript-typecheck.py
  - id: SC-05
    verdict: met
    method: inspection
    evidence: cli_identity PASS recomputed by T-03 verify; c65ceb81 capture provenance
      disclosed
  - id: SC-06
    verdict: met
    method: inspection
    evidence: replay_identity PASS; 43x9 steps
  - id: SC-07
    verdict: met
    method: inspection
    evidence: 'audit: 0 unresolved across 110 files at a03103b0'
  - id: SC-08
    verdict: met
    method: inspection
    evidence: d02 lines recomputed by T-03 verify, all ruled
  - id: SC-09
    verdict: met
    method: inspection
    evidence: DECISIONS.md:3513,7325,7333,8788-8791; T-02 verify exit 0
  - id: SC-10
    verdict: met
    method: inspection
    evidence: case_identity PASS; 162 case_set lines byte-identical to c1
  needs_approval: false
  severity_max: med
  matrix_ok: true
  coverage_gaps:
  - SC-03/SC-04 natural red run not shown; the BRIEF accepts the identity equivalent
  - SEC-1 residual cross-account swap inferred, not executed
  findings:
  - kind: substance
    scope: none
    severity: med
    reader: security-reviewer
    summary: 'SEC-1 residual (T-03): feat2581-ledger-driver.py:118-121 accepts an
      existing /tmp/feat2581-ledger parent (symlink, 0777, or another owner) via makedirs(exist_ok=True).
      QA reported the same defect independently as QA-c2-1 (low).'
    why: During regeneration, another local account controlling the parent could replace
      the private baseline/pin leaf, and path-based capture reads would take in substituted
      data. Reproduced as far as parent acceptance; must_fix.
  - kind: substance
    scope: none
    severity: med
    reader: code-reviewer
    summary: 'CR-3 (T-03): recorder/sitecustomize.py:153-176 resets SIGKILL, which
      raises at startup, so a SIGKILLed CLI child runs twice (ledger -9 with one write,
      wrapper exit 0 with two).'
    why: 'Advisory: a capture risk for future measurements only; no committed ledger
      has a negative status, and fixing it widens the provenance gap. Raised as OQ-V2-2.'
  - kind: form
    scope: none
    severity: low
    reader: code-reviewer
    summary: 'CR-4 (T-03): the generated-receipt footer (feat2581-cleanpin.py:494-501)
      labels raw-JSONL digests ''normalized''.'
    why: A false label in the record. The verdict comparison decodes before normalizing
      and is unaffected. Recommend folding it into the must_fix commit.
  - kind: form
    scope: none
    severity: low
    reader: pm
    summary: 'F-1: answers-2026-11-27-validate-escalate.md says no committed tool
      writes divergence-rulings.json; load_rulings seeds ''[]'' when the file is absent.'
    why: Operator-authored record; rewording is the operator's call (OQ-V2-1). The
      risk argument stands.
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
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2581-feature-record-package/.harness/harness/features/FEAT-2581-feature-record-package/runs/2026-11-27-02-validate-validator/digest.md
```
