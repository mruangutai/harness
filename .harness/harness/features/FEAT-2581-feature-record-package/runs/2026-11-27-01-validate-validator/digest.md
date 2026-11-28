# Validate digest — FEAT-2581, cycle 1, review_sha 62da4501

**ESCALATE.** The feature does what it set out to do: pm grades all ten SCs met and both perspectives
pass, and QA's matrix is green with runner receipts. Two high code-review findings remain, and both are
in T-03's proof tooling, not in the shipped package. One of them can only be fixed in full by changing
T-03's signed `verify:` text, and that change needs approval from the tier above. The rest is legal
must_fix work inside T-03's `notes/**` files.

Range reviewed: `e12381fde910eb05728004476a10d741d6918010..62da450182282b05b25a127528f9223ac90fc6c8`. Gate policy: `harness.json` `gates.review: advisory_unless_high`. Both findings are high, so the gate blocks.

## Members

| Step | Persona | Verdict | Note |
|---|---|---|---|
| qa | harness-qa | PASS | unit 68/68 and integration 94/94 exit 0. Receipts at `runs/2026-11-27-01-validate-validator/qa/manifest-{unit,integration}.json`. The T-01, T-02 and T-03 verifies all exit 0 at the pin. `notes/review-harness-qa-c1.md` |
| code | harness-code-reviewer | FAIL | Two high substance findings in T-03. `notes/review-harness-code-reviewer-c1.md` |
| security | harness-security-reviewer | PASS | One med and one low finding in T-03's receipt scripts. The unchecked merge CLI is gone, and no fail-open import path was found. `notes/review-harness-security-reviewer-c1.md` |
| ui | harness-ui-reviewer | PASS | Out of scope. A census of the 135 changed paths found no UI. `notes/review-harness-ui-reviewer-c1.md` |
| goalcheck | harness-pm | PASS | SC-01..SC-10 met. D-01..D-03 and the DEC-259, DEC-220 and DEC-150 amendments landed. `notes/research-FEAT-2581-feature-record-package-goalcheck-validate-c1.md` |

## Findings, ranked

1. **CR-2 · high · substance · T-03 (code-reviewer).** The ruling-metadata check accepts JSON null for `by`, `date` and `reason`, because `str(None)` is non-blank. The check appears twice:
   - in the generator, `notes/receipt-scripts/feat2581-cleanpin.py:321–323`;
   - in T-03's signed `verify:` (`RD=lambda i: ... str(ru[i].get(k,"")).strip()`, plan.yaml:502,514).

   The reviewer proved this with an in-memory mutant: `audit:stdout` with null metadata still produced `T-03 receipts PASS`. A deleted ruling and a new unruled stream were both correctly rejected. The committed rulings carry real values (pm checked all 631), so the receipt's evidence holds today. The gap is latent and fails open, and it is ranked first because a fail-open in the operator-ruling gate is not reversible once something ships through it (craft P-02).
   - **Remedy, generator half:** inside T-03 `files:`, so it is legal must_fix.
   - **Remedy, verifier half:** edits the signed plan text, so no fix cycle may legally apply it (G-06). I am escalating it as a plan amendment. Severity is transcribed as the reader gave it (high). My own view is lower, because the data at the pin is clean (P-04). The tier above decides whether the amendment is required before ship or can be dispositioned.
2. **CR-1 · high · substance · T-03 (code-reviewer).** DEC-209's mechanical code grade over the canonical range exits 1.
   - **Below the bar:** seven functions under `notes/receipt-scripts/`: `Derived.__init__`, `Derived.hits`, `Derived.d02` and `main` in cleanpin; `main` in grade-assert; `suite` and `main` in ledger-driver.
   - **Grade 2:** five more (non-blocking).
   - **Why it blocks:** DEC-209 computes `code_grade` in the digest gate, so no reviewer can report `pass` for this range.
   - **Remedy:** inside T-03's `notes/**`, so it is legal must_fix. SC-02's own package-scoped grade is green, and this does not contradict it: the two cover different scopes.
3. **SEC-1 · med · substance · T-03 (security).** The receipt scripts use predictable shared `/tmp` paths and default permissions (`feat2581-replay.py:36–39,65–69` and `feat2581-ledger-driver.py:102–114`). They are reachable only when someone runs them explicitly. This finding does not gate. I fold it into the same fix because CR-1 rewrites these files anyway. The fixed replay path `/tmp/feat2581-replay` is part of the signed T-03 identity design, so the fix must keep that path's bytes on both sides. Only permissions and the cleanup-failure check may change.
4. **SEC-2 · low · substance · T-03 (security).** The committed receipts contain 57 absolute paths to a sibling checkout, recovered from gate argv after decoding. Advisory only, and not routed. The measurements are the operator-accepted evidence store (PL-09), and scrubbing them would be the kind of normalization T-03 forbids.

## Fix order

The changes to the cleanpin, grade-assert, ledger-driver and replay scripts all change `script_sha256`. Apply CR-1, CR-2's generator half and SEC-1 in a single T-03 commit. Then regenerate the generated receipt and rerun the T-03 verify at the new tip.

[INFERENCE] If cleanpin can regenerate from the committed measurements, the 631 rulings stand. If regeneration needs a re-measure, the record ids must come out identical, or every changed id goes back to the operator.

The verifier-half amendment of CR-2, if approved, goes into plan.yaml before that verify runs.

## Adequacy

- **QA:** SC-03 and SC-04 rely on the fail-first equivalent named in the BRIEF (identical baseline-side records), not a natural red run. Nobody claims the suites can tell a behaviour change apart, and nobody has shown it. The byte ledgers (SC-05, SC-06, SC-10) carry that load. This is accepted by design.
- **Union-scope check (P-06):** pm's statement that every ruling has by, date and reason is a claim about the data. CR-2 is a claim about the predicate. Both hold, so they do not contradict each other.
- pm's OQ-GC-1 (the qa digest was not available to it) is resolved: QA's PASS matches the suite records pm graded.
- The code reviewer measured behaviour at source: 33 argparse help and error cases, close-run argv bytes, `spend_for`, and `_problems_for_doc`, all comparing baseline and pin on inputs that carry data. That is falsification evidence, not just reasoning.

```yaml
VERDICT: ESCALATE
DIGEST:
  headline: 'FEAT-2581 meets SC-01..SC-10 at 62da4501 (qa green, pm all met), but
    two high T-03 proof-tooling findings block: DEC-209 code grade fails on 7 receipt-script
    functions (legal must_fix) and the ruling-metadata check accepts null by/date/reason,
    whose verifier half needs a signed-plan amendment'
  open_questions:
  - id: OQ-V1
    question: 'CR-2 verifier half: approve amending T-03''s signed verify (plan.yaml
      RD predicate, lines ~502/514) to require non-blank string by/date/reason, or
      disposition it given the committed 631 rulings are all non-null? Reader rated
      high; lead''s view is lower (latent, data clean at pin).'
    blocking: true
  - id: OQ-V2
    question: Should DEC-209's canonical code grade cover one-shot per-feature proof
      scripts under notes/receipt-scripts/? As the policy reads today it does, so
      CR-1 must be fixed by refactoring. Exempting those scripts would be a decision
      change, not a fix.
    blocking: false
  files_touched:
  - .harness/harness/features/FEAT-2581-feature-record-package/runs/2026-11-27-01-validate-validator/qa/manifest-unit.json
  - .harness/harness/features/FEAT-2581-feature-record-package/runs/2026-11-27-01-validate-validator/qa/manifest-integration.json
  expertise_update: []
  team: validate
  steps_run: 5
  cycles_used: 0
  members:
  - step: qa
    persona: harness-qa
    verdict: PASS
    headline: unit 68/68, integration 94/94 exit 0 with runner receipts; T-01/T-02/T-03
      verifies exit 0; BRIEF-designated fail-first equivalent pin-bound
    files_touched:
    - .harness/harness/features/FEAT-2581-feature-record-package/runs/2026-11-27-01-validate-validator/qa/manifest-unit.json
    - .harness/harness/features/FEAT-2581-feature-record-package/runs/2026-11-27-01-validate-validator/qa/manifest-integration.json
  - step: code
    persona: harness-code-reviewer
    verdict: FAIL
    headline: T-03 fails canonical code grading and accepts null operator-ruling metadata
    files_touched: []
  - step: security
    persona: harness-security-reviewer
    verdict: PASS
    headline: Unchecked merge CLI gone, no fail-open import path; med /tmp scratch
      and low sibling-path exposure in T-03 receipt scripts
    files_touched: []
  - step: ui
    persona: harness-ui-reviewer
    verdict: PASS
    headline: 'Out of scope: census of 135 changed paths, no UI surface'
    files_touched: []
  - step: goalcheck
    persona: harness-pm
    verdict: PASS
    headline: Both perspectives pass; SC-01..SC-10 met; D-01..D-03 and DEC-259/220/150
      amendments landed; 631 divergences RULED with by/date/reason
    files_touched: []
  must_fix:
  - 'CR-1 (T-03, code-reviewer, high): bring the seven below-bar notes/receipt-scripts
    functions (cleanpin Derived.__init__/hits/d02/main, grade-assert main, ledger-driver
    suite/main) to the DEC-209 bar, then regenerate script_sha256 and the generated
    receipt and rerun the T-03 verify at the new tip. The record ids must stay identical,
    or every changed id goes back to the operator.'
  - 'CR-2 generator half (T-03, code-reviewer, high): make feat2581-cleanpin.py:321-323
    require non-blank string by/date/reason, and show that a null-metadata mutant
    fails while the existing 631 rulings still pass. The verifier half is OQ-V1 (signed
    plan text).'
  branch: feat/FEAT-2581-feature-record-package
  escalations:
  - id: ESC-1
    raised_by: harness-code-reviewer
    question: CR-2's full remedy amends T-03's signed verify predicate in plan.yaml.
      No fix cycle may legally apply it. Should it be amended before ship, or dispositioned?
    domain: plan amendment (signed T-03 verify)
    routed_to: harness-orchestrator
    resolution: pending
    decided_by: pending
    recorded_as: runs/2026-11-27-01-validate-validator/digest.md#findings-ranked
  adequacy_notes:
  - SC-03 and SC-04 fail-first evidence is the BRIEF-designated identity equivalent
    (identical baseline-side records), not a natural red run; suite discrimination
    is carried by the SC-05/06/10 byte ledgers, by design.
  - pm's 'all rulings carry by/date/reason' is about the data and CR-2 is about the
    predicate. Both hold, so there is no contradiction.
  - 'The code reviewer ran baseline-vs-pin comparisons on data-carrying inputs: 33
    argparse cases, close-run argv bytes, spend_for and _problems_for_doc. That is
    falsification evidence, not reasoning only.'
  - 'SEC-1 (med, /tmp scratch permissions) is advisory. It is folded into the CR-1
    rewrite of the same scripts, keeping the signed /tmp/feat2581-replay path bytes.
    SEC-2 (low, sibling-checkout paths in committed measurements) is not routed: scrubbing
    would be a normalization T-03 forbids and PL-09 accepted the store.'
  - 'All four findings are against T-03 (files: notes/**).'
  sc_status:
  - id: SC-01
    verdict: met
    method: inspection
    evidence: 'pm + code-reviewer: feature_record/ 10 files, __init__ empty; legacy
      modules absent; T-01 verify exit 0 (qa)'
  - id: SC-02
    verdict: met
    method: inspection
    evidence: receipt grade_bar PASS; grade-assert pin exit 0, baseline exit 1 naming
      the twelve. Package-scoped only; the full-range DEC-209 grade fails on receipt
      scripts (CR-1)
  - id: SC-03
    verdict: met
    method: automated
    evidence: qa manifest-unit.json 68/68 exit 0; test-factory-claim-mutation.py's
      4 FAIL lines byte-identical to baseline
  - id: SC-04
    verdict: met
    method: automated
    evidence: qa manifest-integration.json 94/94 exit 0; INV-40 cases in test-check-state-feat59.py
  - id: SC-05
    verdict: met
    method: inspection
    evidence: cli_identity PASS; per-class records on both sides; divergences recomputed
      and RULED. The ruling predicate's null gap is CR-2
  - id: SC-06
    verdict: met
    method: inspection
    evidence: replay_identity PASS; 43x9 steps, zero replay divergences
  - id: SC-07
    verdict: met
    method: inspection
    evidence: audit exit 0, 0 unresolved across 110 files; classification rows migrated
  - id: SC-08
    verdict: met
    method: inspection
    evidence: D-02 diagnostics name the loaded modules; d02_item lines recomputed
      and ruled
  - id: SC-09
    verdict: met
    method: inspection
    evidence: DECISIONS.md:3513,7325,7333,8788-8792; gen-decisions-index --stdout
      equal
  - id: SC-10
    verdict: met
    method: inspection
    evidence: case_identity PASS; 11 DIFFERENT case sets each ruled
  needs_approval: true
  severity_max: high
  matrix_ok: true
  coverage_gaps:
  - SC-03/SC-04 natural red run not shown; identity equivalent accepted by BRIEF
  findings:
  - kind: substance
    scope: none
    severity: high
    reader: code-reviewer
    summary: 'CR-2 (T-03): ruling-metadata predicate in feat2581-cleanpin.py:321-323
      and in T-03''s signed verify accepts JSON null by/date/reason (str(None) non-blank);
      a null-metadata mutant passed.'
    why: 'Fail-open in the operator-ruling gate: a measured divergence could pass
      without a real ruling. Latent: the committed rulings are clean. The verifier
      half needs a signed-plan amendment (ESC-1).'
  - kind: substance
    scope: none
    severity: high
    reader: code-reviewer
    summary: 'CR-1 (T-03): DEC-209 canonical code grade over e12381fd..62da4501 exits
      1 on seven notes/receipt-scripts functions below the bar (plus five grade-2).'
    why: DEC-209 computes code_grade in the digest gate, so no review of this range
      can pass until the scripts are refactored.
  - kind: substance
    scope: none
    severity: med
    reader: security-reviewer
    summary: 'SEC-1 (T-03): receipt scripts use predictable shared /tmp paths with
      default permissions and ignore cleanup failures.'
    why: On a shared host, another account could read raw captures or seed stale scratch
      during an explicit regeneration. Non-gating; folded into the CR-1 rewrite.
  - kind: substance
    scope: none
    severity: low
    reader: security-reviewer
    summary: 'SEC-2 (T-03): committed receipts expose 57 absolute sibling-checkout
      paths.'
    why: 'Assessed and dismissed for routing: the measurement store is operator-accepted
      (PL-09), and scrubbing would add normalization T-03 forbids.'
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
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2581-feature-record-package/.harness/harness/features/FEAT-2581-feature-record-package/runs/2026-11-27-01-validate-validator/digest.md
```
