# Validate digest — FEAT-2581, round 3, review_sha c039c32d

**ESCALATE. Every fix-round claim checks out except one: T-03's signed verify is RED at the pin when run verbatim.**

The failure is VF-1. In the check's `test_change` comparison, `git diff` prints the `index` lines with git's automatic abbreviation length, which depends on how many objects the repository holds. This store now holds 65,632 objects, more than 2^16, so git prints 9 hex digits. The committed records in `build-divergences.md` carry 8. All 29 records mismatch, and the only difference is the index abbreviation.

The verify's multi-line block also masks the failure. It has no `set -e`, and its last line, the audit, exits 0, so a plain `bash` run exits 0. The main session's claim that "T-03 verify passes at c039c32d" is therefore refuted. QA, code, pm and security each found this independently. Each one ran the identical block with only a process-local `core.abbrev=8` override, and it passes.

Two things put the remedy outside a fix round:
- The durable remedy amends T-03's signed verify.
- The operator's two-round rework ruling is exhausted.

The decision therefore belongs to the operator, not to a must_fix.

What holds at c039c32d:
- **SEC-1 is closed.** Security and QA both ran the other-uid case for real, with root-owned directories. QA showed that each of the three refusal legs has a discriminating mutant.
- **CR-3 is closed.** The new recorder returns -9, -15 and 3, with one run and empty stderr. QA fail-first: the old blob ran a SIGKILLed child twice.
- **CR-4 is closed.** The footer hash values are unchanged.
- **P4 is confirmed.** The receipt diff is exactly the three script_sha256 lines, the two footer labels and the stamp. `build-divergences.md`, the rulings and the measurements are byte-identical.
- **F-1 is reworded truthfully.**
- **The code grade over e12381fd..c039c32d exits 0**, with 280 passing.
- **The T-01 and T-02 verifies exit 0.**
- **QA's matrix is green with receipts:** unit 68/68, integration 94/94.
- **pm grades SC-01..SC-10 and DEC-259, DEC-220 and DEC-150 as met.**

## Members

| Step | Persona | Verdict | Note |
|---|---|---|---|
| qa | harness-qa | FAIL | QA-c3-1 (high): T-03 verify exits 1 under `bash -e` and 0 under plain bash; it exits 0 with core.abbrev=8. The matrix is green. P1–P4 and P6 are confirmed, with mutants and fail-first. `notes/review-harness-qa-c3.md` |
| code | harness-code-reviewer | ESCALATE | CR-5 (med): the same defect, with blocking OQ-C3-1. CR-3 and CR-4 are closed by its own execution. CR-6 (low) is new and advisory. `notes/review-harness-code-reviewer-c3.md` |
| security | harness-security-reviewer | PASS | SEC-1 is closed across seven parent shapes, including a real uid-0 case. There are no findings. It reported the T-03 abbreviation mismatch separately, as not a security matter. `notes/review-harness-security-reviewer-c3.md` |
| ui | harness-ui-reviewer | PASS | Out of scope. A census of 156 pinned paths found no visual extensions; the only JS file is a Bun test preload. `notes/review-harness-ui-reviewer-c3.md` |
| goalcheck | harness-pm | FAIL | SC-01..SC-10 are met, with no product regression from a03103b0. VF-1 (med) is the same defect, with blocking OQ-C3-1. `notes/research-FEAT-2581-feature-record-package-goalcheck-validate-c3.md` |

## Findings, ranked

1. **VF-1 / QA-c3-1 / CR-5: T-03's signed verify depends on the ambient git abbreviation.** It is substance in T-03, and gating. Four readers reported it, so it counts as one finding.
   - **Where:** both sides build the patch bytes with plain `git diff`, without `--full-index` or a fixed `--abbrev`:
     - the generator, `feat2581-cleanpin.py:358–365`;
     - the verify, at `plan.yaml:516` (verify line 23).
   - **Severity:** QA rated it high; code and pm rated it med. I take **high**, because a signed task gate that is red at the pin is a failed gate whatever the root cause. Reproducibility across checkouts is also what T-03 exists to provide, and this receipt passes or fails depending on the object count of whichever clone runs it.
   - **Not a measurement defect:** with `--abbrev=8`, all 29 records match byte for byte. The receipt's substance is sound; only its re-checkability is broken.
   - **Not introduced by c039c32d:** the defect has been latent since the build. QA infers that round 2 ran green below 2^16 objects; that is reasoned, not executed.
2. **QA-c3-2: the verify's exit status masks its own assertion** (low, form, from QA; pm folds it into the VF-1 remedy). The multi-line block has no `set -e` or `&&`, and the last command determines the exit. This is how the main session read PASS.
   - It also bears on how Harness executes multi-line verify blocks: QA found no executor in `bin/`. That makes it a harness-level question as well (OQ-V3-2).
3. **CR-6: a blocked fatal signal can still produce a different recorder wrapper status** (low, substance, from the code reviewer). This is in `recorder/sitecustomize.py:153–161`.
   - If the wrapper inherits SIGTERM blocked, it exits 241 where the ledger records -15. This was measured on both pins.
   - No committed capture exercises this case. It is advisory and not routed.
4. **Security's unmitigated STRIDE D row:** another uid can pre-create `/tmp/feat2581-ledger`. That causes only a loud refusal, never a silent substitution. Security raised no finding on it, and I record it only as a note.

## Escalation, and the options for the operator

All the options are for VF-1. Which one to take is the operator's call.

- **(A) Accept process-local `core.abbrev=8` as a recorded prerequisite** for re-running T-03's verify, in an answers note. There is no code change and no fix round. The cost is that any re-check without that override goes red, and the exit masking stays.
- **(B) Signed amendment.** Pin `--full-index` (or a fixed `--abbrev`) in both `feat2581-cleanpin.py` and T-03's verify, and join the verify's commands with `&&`. Then regenerate `build-divergences.md`'s test_change records with `--reuse`. This is the durable fix. It needs both a verify amendment and a third fix round beyond the ruling.
- **(C) Rejected:** regenerating the records at today's 9-digit abbreviation without changing the verify. This is just as object-count-fragile, it still spends a fix round, and it fixes nothing.

My recommendation is (B) if the operator grants the round, and otherwise (A). Every SC is met in substance, and the measured identity holds under a fixed abbreviation.

## Record corrections

- **The dispatch claim that the "T-03 verify passes at c039c32d" is refuted**, as explained above.
- **The round-2 digest's statement that the "T-03 verify exits 0" was an exit-status reading.** The same masking applies to it, so I withdraw it as evidence. Round 2's FAIL verdict stands independently on SEC-1.

## Adequacy

- Falsification evidence came from four readers. Two strengthen this round:
  - The other-uid case of SEC-1 was executed this round by both QA and security. In round 2 it was only inferred.
  - QA's three-leg mutant table gives the parent check pinned assurance in the sense of P-08, not just correctness.
- SC-02 through SC-10 inspection evidence from pm rests on T-03 runs made with `core.abbrev=8`. Their substance is met, and the plain-run gate is VF-1.
- The SIGSTOP branch of `_exit_as` is unexercised; it was reasoned to be unreachable.
- SC-03 and SC-04 fail-first evidence is the identity equivalent the BRIEF designates.

```yaml
VERDICT: ESCALATE
DIGEST:
  headline: 'FEAT-2581 at c039c32d: SEC-1, CR-3, CR-4, P4 and F-1 are closed by execution,
    and SC-01..SC-10 are met. But T-03''s signed verify is RED verbatim: git''s ambient
    abbreviation is now 9 digits, so all 29 test_change records mismatch. The block''s
    exit 0 masks the AssertionError. The remedy needs the operator: a signed verify
    amendment and a third fix round beyond the ruling'
  open_questions:
  - id: OQ-V3-1
    question: 'VF-1: T-03''s signed verify fails at c039c32d. Its test_change check,
      and the cleanpin generator, compare plain `git diff` output, and with more than
      65,536 objects git prints 9-digit index hashes while the committed records hold
      8. With a process-local core.abbrev=8 the identical block passes, 29/29. Choose
      (A) accept core.abbrev=8 as a recorded prerequisite: no code change, no fix
      round, and the exit masking stays. Or choose (B) a signed amendment: pin --full-index
      in the generator and the verify, join the verify lines with &&, and regenerate
      test_change with --reuse. B needs a third fix round. Option (C), regenerating
      at 9 digits, is rejected as just as fragile. Recommended: B if a round is granted,
      else A.'
    blocking: true
  - id: OQ-V3-2
    question: 'Harness-level: multi-line plan verify blocks run under plain bash exit
      with the status of their last line, so an earlier assertion failure is masked
      (T-03 printed an AssertionError and exited 0). Which shell or executor runs
      verify blocks? Should verify blocks be required to run under set -e, or be &&-joined?
      No executor was found in bin/.'
    blocking: false
  files_touched:
  - .harness/harness/features/FEAT-2581-feature-record-package/runs/2026-11-27-03-validate-validator/qa/manifest-unit.json
  - .harness/harness/features/FEAT-2581-feature-record-package/runs/2026-11-27-03-validate-validator/qa/manifest-integration.json
  - .harness/harness/features/FEAT-2581-feature-record-package/observations/harness-qa.md
  - .harness/harness/features/FEAT-2581-feature-record-package/observations/harness-pm.md
  expertise_update: []
  team: validate
  steps_run: 5
  cycles_used: 0
  members:
  - step: qa
    persona: harness-qa
    verdict: FAIL
    headline: Matrix green (unit 68/68, integration 94/94, defect-free receipts).
      P1-P4 and P6 confirmed with mutants and fail-first. T-03 verify exits 1 under
      bash -e at c039c32d, and 0 with core.abbrev=8 (QA-c3-1, high).
    files_touched:
    - .harness/harness/features/FEAT-2581-feature-record-package/runs/2026-11-27-03-validate-validator/qa/manifest-unit.json
    - .harness/harness/features/FEAT-2581-feature-record-package/runs/2026-11-27-03-validate-validator/qa/manifest-integration.json
    - .harness/harness/features/FEAT-2581-feature-record-package/observations/harness-qa.md
  - step: code
    persona: harness-code-reviewer
    verdict: ESCALATE
    headline: 'CR-3 and CR-4 closed; T-01/T-02 and code grade pass. CR-5 (med): T-03
      verify depends on ambient git abbreviation. CR-6 (low) advisory.'
    files_touched: []
  - step: security
    persona: harness-security-reviewer
    verdict: PASS
    headline: SEC-1 residual closed across seven parent shapes, including a real uid-0
      dir. No new security findings.
    files_touched: []
  - step: ui
    persona: harness-ui-reviewer
    verdict: PASS
    headline: 'Out of scope: 156 pinned paths, no visual extensions.'
    files_touched: []
  - step: goalcheck
    persona: harness-pm
    verdict: FAIL
    headline: 'SC-01..SC-10 and DEC-259/220/150 met with no product regression from
      a03103b0. VF-1 (med): the signed T-03 verify is red verbatim, and the exit masks
      it.'
    files_touched:
    - .harness/harness/features/FEAT-2581-feature-record-package/observations/harness-pm.md
  must_fix: []
  branch: feat/FEAT-2581-feature-record-package
  escalations:
  - id: ESC-V3-1
    raised_by: harness-qa, harness-code-reviewer, harness-pm (security concurring)
    question: 'VF-1: T-03''s signed verify is red at the pin because of ambient git
      abbreviation. Accept a core.abbrev=8 prerequisite (A), or amend the signed verify
      and generator with --full-index and && plus a third fix round (B)?'
    domain: signed plan verify / rework budget
    routed_to: orchestrator -> operator
    resolution: pending
    decided_by: pending
    recorded_as: pending
  adequacy_notes:
  - 'Dispatch P5 refuted: ''T-03 verify passes at c039c32d'' was an exit-status reading.
    The block has no set -e, and its last line (the audit) exits 0 after the AssertionError
    at verify line 23. Under bash -e it exits 1.'
  - 'Round-2 digest correction: its ''T-03 verify exits 0'' was also exit-based and
    is withdrawn as evidence. Round 2''s FAIL verdict stands on SEC-1, independent
    of this.'
  - 'VF-1 is a re-checkability defect, not a measurement defect: with --abbrev=8,
    all 29 test_change records match byte for byte. It is latent since build and not
    introduced by c039c32d.'
  - 'Severity reconciliation: QA high, code med, pm med for the same defect. I take
    high, because a signed task gate red at the pin is a failed gate, and reproducibility
    across clones is T-03''s purpose. Routed as ESCALATE, not must_fix, because the
    durable remedy amends signed verify text and the operator''s two-round rework
    budget is exhausted (G-06).'
  - 'Confirmed by execution: P1 SEC-1 parent check, including a real other-uid case
    (QA and security), with each of three refusal legs carrying a discriminating mutant
    (QA). P2 CR-3: -9/-15/3 with one run and empty stderr, and old-blob fail-first
    ran twice. P3 CR-4: footer relabelled, values unchanged. P4: receipt diff is exactly
    the script hashes, two labels and the stamp; build-divergences, rulings and measurements
    byte-identical. P6: F-1 reworded truthfully. code-grade e12381fd..c039c32d exits
    0 (280 passing). T-01/T-02 exit 0.'
  - 'CR-6 (low, code-reviewer): an inherited blocked SIGTERM makes the wrapper exit
    241 vs ledger -15. No committed capture exercises it; advisory, not routed.'
  - 'Security''s unmitigated STRIDE D row: another uid pre-creating /tmp/feat2581-ledger
    causes only a loud refusal. Not a finding.'
  - Gate policy is advisory_unless_high, and severity_max here is high. The verdict
    is ESCALATE because the remedy is operator-gated.
  sc_status:
  - id: SC-01
    verdict: met
    method: inspection
    evidence: T-01 verify exit 0 verbatim at c039c32d; product diff a03103b0..c039c32d
      empty outside the feature dir (pm, code, qa)
  - id: SC-02
    verdict: met
    method: inspection
    evidence: grade-assert exit 0 at pin, exit 1 at baseline naming the twelve; code-grade
      e12381fd..c039c32d exit 0, 280 passing (pm, code, qa)
  - id: SC-03
    verdict: met
    method: automated
    evidence: qa manifest-unit.json 68/68 exit 0 at c039c32d; only the claim-mutation
      file's 4 FAIL lines; identity fail-first equivalent
  - id: SC-04
    verdict: met
    method: automated
    evidence: qa manifest-integration.json 94/94 exit 0; baseline_failing only test-typescript-typecheck.py
  - id: SC-05
    verdict: met
    method: inspection
    evidence: cli_identity PASS recomputed by T-03 under core.abbrev=8; measurements
      byte-identical to a03103b0; recorder change disclosed
  - id: SC-06
    verdict: met
    method: inspection
    evidence: replay_identity PASS recomputed by T-03 under core.abbrev=8
  - id: SC-07
    verdict: met
    method: inspection
    evidence: 0 unresolved reader sites across 110 files (T-01 and T-03 audit)
  - id: SC-08
    verdict: met
    method: inspection
    evidence: d02_item and residual lines recomputed and passing under core.abbrev=8;
      plain-run gate red is VF-1
  - id: SC-09
    verdict: met
    method: inspection
    evidence: DECISIONS.md:3513,7325,7333,8790 at c039c32d; T-02 exit 0; index regen
      cmp equal
  - id: SC-10
    verdict: met
    method: inspection
    evidence: case_set recomputation passing under core.abbrev=8
  needs_approval: true
  severity_max: high
  matrix_ok: true
  coverage_gaps:
  - T-03 signed verify red in an unconfigured checkout (VF-1); green only with process-local
    core.abbrev=8
  - SIGSTOP branch of recorder _exit_as unexercised; reasoned unreachable
  - SC-03/SC-04 natural red run not shown; the BRIEF accepts the identity equivalent
  findings:
  - kind: substance
    scope: none
    severity: high
    reader: harness-qa (also harness-code-reviewer CR-5 med, harness-pm VF-1 med)
    summary: 'VF-1/QA-c3-1/CR-5 (T-03): feat2581-cleanpin.py:358-365 and T-03 verify
      (plan.yaml:516) compare plain `git diff` bytes. The ambient abbreviation is
      now 9 digits (65,632 objects), so all 29 test_change records mismatch and the
      verify raises AssertionError at c039c32d. It passes with core.abbrev=8.'
    why: A signed task gate is red at the pin, and the receipt's re-checkability depends
      on the clone's object count. The remedy is an operator decision (ESC-V3-1).
  - kind: form
    scope: none
    severity: low
    reader: harness-qa
    summary: 'QA-c3-2: T-03''s multi-line verify has no set -e or &&, so the last
      line''s exit 0 masks the assertion failure.'
    why: This is how a red gate was reported as passing. Fold the && into remedy B;
      the harness-level question is OQ-V3-2.
  - kind: substance
    scope: none
    severity: low
    reader: harness-code-reviewer
    summary: 'CR-6 (T-03): recorder/sitecustomize.py:153-161 exits 241 vs ledger -15
      when the wrapper inherits SIGTERM blocked.'
    why: 'Advisory: no committed capture exercises it.'
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
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2581-feature-record-package/.harness/harness/features/FEAT-2581-feature-record-package/runs/2026-11-27-03-validate-validator/digest.md
```
