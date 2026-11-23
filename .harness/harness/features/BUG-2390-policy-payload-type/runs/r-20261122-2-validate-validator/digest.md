# BUG-2390 validation — 79db636b50aa6547edb2b16591f7c26c721f0b47

FAIL: honest payload typing lands, but SC-02's specified historical proof does not. SC-03's regression portion passes; its shared discrimination obligation remains partial.

## Consolidated finding

One medium substance finding, T-01, reported by code and corroborated by goalcheck and QA: `notes/receipts/T-01-red.txt` contains only TS2614 for missing PolicyPayload export and identifies baseline plus working edits, not an immutable test-only pin. It does not discriminate the object-only production runner contract. Preserve that historical record; supply genuine discriminating pinned evidence without claiming a later reconstruction happened first. If the historical requirement cannot be fulfilled, its replacement requires explicit approval rather than a fabricated chronology.

QA calls the static red real but weak and returns PASS; code and goalcheck reject it against the literal criterion. I adopt the latter acceptance judgment: QA's green execution and signature-absence evidence do not establish the specifically promised runner mismatch. This is one defect, not separate SC-02 and SC-03 fixes.

## Adequacy and deviations

- QA reports production unit runner green (65 files), typecheck clean and targeted hook suite 214 pass / 0 fail / 1553 assertions, matching baseline. Receipt: `qa/manifest-unit.json`. No weakened assertions reported. No runtime red claimed or required.
- Fixture honesty passes independent code, security and QA inspection: checked array rejection protects object reads; remaining six pre-existing any reads were not relocated or added.
- The apostrophe-only verify-message amendment and opsList checked narrowing are acceptable bounded changes; no behavior regression or security finding was reported.
- Runtime tests do not independently pin the new guard/refusal branches; mutation evidence is unavailable to QA under its write guard. These bound assurance, not additional blockers for this type repair.
- UI self-scopes out on measured pinned diff; no visual pass claimed. No decision dispositions were declared.

## Reader pointers

`notes/review-harness-{qa,code-reviewer,security-reviewer,ui-reviewer}-c0.md`; `notes/research-BUG-2390-policy-payload-type-goalcheck-validate-c0.md`.

Open questions: none newly introduced. Remediation routes to Main (DEC-174), not a delegated hook editor. Any acceptance amendment must be explicitly approved.

```yaml
VERDICT: FAIL
DIGEST:
  headline: '79db636b: honest payload repair and green regression suite; SC-02 lacks
    specified contract-discriminating red and test-only pin.'
  open_questions: []
  files_touched: []
  expertise_update: []
  team: validate
  steps_run: 5
  cycles_used: 0
  members:
  - step: qa
    persona: harness-qa
    verdict: PASS
    headline: Matrix green; 214 hooks pass, but historical red is signature-absent
      only.
    files_touched: []
  - step: code
    persona: harness-code-reviewer
    verdict: FAIL
    headline: Source passes inspection; SC-02 evidence does not discriminate runner
      contract.
    files_touched: []
  - step: security
    persona: harness-security-reviewer
    verdict: PASS
    headline: Refusal behavior preserved; no relocated fixture lie.
    files_touched: []
  - step: ui
    persona: harness-ui-reviewer
    verdict: PASS
    headline: Measured diff has no UI surface; scoped out.
    files_touched: []
  - step: goalcheck
    persona: harness-pm
    verdict: FAIL
    headline: Both perspectives partial because specified historical red is missing.
    files_touched: []
  must_fix:
  - 'T-01 (Main, DEC-174): provide genuine pinned static evidence discriminating object-only
    production runner contracts while preserving the historical TS2614 receipt and
    chronology; obtain explicit approval if replacing SC-02''s historical evidence
    requirement. SC-03 shares this single discrimination gap.'
  branch: none
  escalations: []
  adequacy_notes:
  - 'QA''s execution PASS does not clear literal acceptance: its own evidence confirms
    missing-export TS2614, not the required union-versus-object runner mismatch. Code
    and goalcheck therefore control the consolidated FAIL.'
  - 'Advisor honesty criterion passes: fixture uses checked narrowing; six pre-existing
    any reads were neither added nor relocated.'
  - Apostrophe-only verify amendment and opsList checked narrowing are acceptable;
    no behavioral or security defect reported.
  - QA reports production unit runner green across 65 files, typecheck clean, and
    214 hook tests / 1553 assertions matching main baseline; no weakened assertions.
  - No runtime red is claimed or required. New guard/refusal branches lack independent
    runtime discrimination; QA mutation capability was refused, limiting assurance.
  - No decision dispositions declared; UI scoped out from measured diff.
  sc_status:
  - id: SC-01
    verdict: met
    method: inspection
    evidence: Code, security and QA inspect pinned payload union, checked narrowing
      and direct ops-array forwarding; no relocated assertion.
  - id: SC-02
    verdict: partial
    method: automated
    evidence: notes/receipts/T-01-red.txt records TS2614 missing PolicyPayload export
      and baseline plus working edits, not runner mismatch or immutable test-only
      pin; green typecheck passes.
  - id: SC-03
    verdict: partial
    method: automated
    evidence: 'Regression portion passes: 214 pass, 0 fail, 1553 assertions matches
      main baseline; shared SC-02 discrimination obligation remains incomplete.'
  needs_approval: false
  severity_max: med
  matrix_ok: true
  coverage_gaps:
  - SC-02 lacks specified contract-discriminating historical red and immutable test-only
    pin; SC-03 shares that gap.
  - No independent runtime test of new array guard/refusal branches; no QA mutation
    proof under write guard.
  findings:
  - kind: substance
    scope: none
    severity: med
    reader: code-reviewer
    summary: 'T-01: SC-02 red detects a missing export, not the promised payload-contract
      incompatibility.'
    why: Pinned red receipt contains only TS2614 missing PolicyPayload export and
      baseline plus unpinned working-tree identification. A union-accepting fake remains
      assignable to an object-only runner; the recorded red does not exclude retaining
      object-only production signatures. Goalcheck and QA corroborate the evidence
      limitation.
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
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2390-policy-payload-type/.harness/harness/features/BUG-2390-policy-payload-type/runs/r-20261122-2-validate-validator/digest.md
```
