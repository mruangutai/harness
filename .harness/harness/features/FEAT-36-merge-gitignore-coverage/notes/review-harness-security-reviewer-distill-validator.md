# Security reviewer expertise distillation

BLUF: Accepted one novel craft rule for test-only security scoping and added it as `O-09`; rejected two candidates because existing craft entries already prescribe their behavior. No observation log existed, no repository-specific knowledge was accepted, and no stale entry required removal.

## Source-separated result

- Observations: **0 accepted**. `.harness/harness/features/FEAT-36-merge-gitignore-coverage/observations/harness-security-reviewer.md` was absent when checked.
- Digest skim: **1 accepted, 2 rejected**.

## Candidate judgments

1. **Reject as already represented** — `runs/review-validator/digest.md` D-01 and `runs/review-c2-validator/digest.md` D-01. Craft `P-08` already requires comparison with the pre-change state and proof that mechanism, reachability, and affected set are unchanged before dismissal; `P-12` requires recording the assessed-and-dismissed risk. The candidate adds an instance-level byte-identity formulation but no new durable action.
2. **Accept as craft `O-09`** — `runs/review-c1-validator/digest.md` security headline. Test-only diffs can still cross subprocess, environment, filesystem, and configuration boundaries, and no existing entry enumerated this scoping obligation before a clean security conclusion.
3. **Reject as already represented** — `runs/review-c2-validator/digest.md` F-02. Craft `P-02` already makes attacker capability and gain precede severity, while `P-09` and `O-01` distinguish weak shape/substring evidence from identity-level proof. A weak assertion alone therefore does not become a security-boundary bypass under the existing rules.

## Curation and counts

- Stale-entry disposition: none. All craft entries remain current and durable; all three repository entries remain current repository facts. No entries were dropped or merged.
- Craft before → after: Patterns **15 → 15**, Gotchas **15 → 15**, Outcomes **8 → 9**, Open **0 → 0**.
- Repository before → after: Patterns **3 → 3**, Gotchas **0 → 0**, Outcomes **0 → 0**, Open **0 → 0**. The repository file was not changed.

## Exact applied operation

```yaml
- op: add
  section: Outcomes
  entry: "WHEN self-scoping a test-only diff DO audit subprocess, environment, filesystem, and configuration effects before declaring no exploitable regression — tests can invoke production code, mutate inherited state, or change enforcement reachability."
  why: "Novel cross-repository scoping rule distilled from the cycle-one security review."
```

Merge receipt: `ADDED O-09`; `APPLIED .harness/expertise/harness-security-reviewer.md`.

## Scoped validation

Changed file only:

```text
$ .agents/skills/harness/bin/check-expertise.sh .harness/expertise/harness-security-reviewer.md
OK   .harness/expertise/harness-security-reviewer.md
ADVISORY .harness/expertise/harness-security-reviewer.md:19: G-01 names 'DEC-100' — repository-layer candidate; rule on it (issue 340)
```

The advisory is pre-existing and does not invalidate the check. No project-wide validation was run.

## Canonical handoff

```yaml
VERDICT: PASS
DIGEST:
  headline: "One novel test-only security-scoping rule was distilled; two redundant candidates were rejected."
  in_scope: false
  scope_reason: "This dispatch curated reviewer memory rather than auditing a product diff; security exploitability grading was not applicable."
  severity_max: n/a
  findings: 0
  must_fix: []
  threat_model: []
  accepted_counts: { observation: 0, digest_skim: 1 }
  rejected_candidates:
    - "Pre-existing utility risk candidate: already covered by P-08 and P-12."
    - "Weak substring assertion candidate: already covered by P-02, P-09, and O-01."
  stale_dispositions: []
  section_counts:
    craft: { Patterns: "15->15", Gotchas: "15->15", Outcomes: "8->9", Open: "0->0" }
    repository: { Patterns: "3->3", Gotchas: "0->0", Outcomes: "0->0", Open: "0->0" }
  open_questions: []
  files_touched:
    - .harness/expertise/harness-security-reviewer.md
    - .harness/harness/features/FEAT-36-merge-gitignore-coverage/notes/review-harness-security-reviewer-distill-validator.md
  expertise_update:
    - op: add
      section: Outcomes
      entry: "WHEN self-scoping a test-only diff DO audit subprocess, environment, filesystem, and configuration effects before declaring no exploitable regression — tests can invoke production code, mutate inherited state, or change enforcement reachability."
      why: "Novel cross-repository scoping rule distilled from the cycle-one security review."
artifact: .harness/harness/features/FEAT-36-merge-gitignore-coverage/notes/review-harness-security-reviewer-distill-validator.md
```
