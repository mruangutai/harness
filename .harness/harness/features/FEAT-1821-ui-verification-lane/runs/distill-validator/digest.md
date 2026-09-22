# Validator expertise distillation

**BLUF:** BLOCKED. Validator-owned expertise reconciliation is complete and clean, but the current OMP process loaded pre-`1a32fe93` hooks that do not forward `HARNESS-MISSION: distill`; they reject the mandatory QA and code-review did-nothing PASS fields. Restart OMP, then rerun only those two terminal gates.

HARNESS-MISSION: distill

## Counts (`Patterns / Gotchas / Outcomes / Open`)

| Persona | Craft before→after | Repository before→after |
|---|---|---|
| harness-validator-lead | `15/15/10/0 → 15/15/10/0` | `2/4/0/0 → 2/4/0/0` |
| harness-qa | `15/15/10/1 → 15/15/10/1` | `0/10/0/0 → 0/10/0/0` |
| harness-code-reviewer | `15/15/10/0 → 15/15/10/0` | `1/11/0/0 → 1/11/0/0` |
| harness-security-reviewer | `15/15/10/0 → 15/15/10/0` | `5/9/1/0 → 5/9/1/0` |
| harness-ui-reviewer | `15/15/10/0 → 15/15/10/0` | `4/0/0/0 → 4/0/0/0` |

Only QA had an observation log. No repository-tier file changed. Reconciliation confirmed every entry and count remains unchanged after the two send-backs.

## Accepted entries by source

- **QA craft P-14** ← `observations/harness-qa.md`: test runtime producer output together with the static consumer's accepted shape.
- **Code-review craft P-10** ← `notes/review-harness-code-reviewer-c9.md` + `runs/validate-c9-traces-validator/digest.md`: compare custom format validation with the canonical parser using almost-valid mutants.
- **UI-review craft P-04** ← `notes/review-harness-ui-reviewer-c0.md` + `runs/validate-validator/digest.md`: bind each screenshot's pixels to the signed scenario and setup result.
- **UI-review craft P-11** ← `notes/review-harness-ui-reviewer-c9.md` + `runs/validate-c9-traces-validator/digest.md`, preserved by `runs/validate-c9-fix-validator/digest.md`: inspect each trace's own actions, filmstrip, DOM, and assertion context.
- **UI-review craft O-07** ← `notes/review-harness-ui-reviewer-c9.md` + `runs/validate-c9-traces-validator/digest.md`: judge evidence truthfulness separately from product success.

## Rejected candidates

- **Validator lead (3/3):** semantic binding duplicates P-03/P-06; cross-reader producer/gate union is exactly P-06; correct-now versus regression-bound is exactly P-08.
- **QA (2/3):** discovery versus execution is already mandated by the QA protocol; the boundary-mutant lesson duplicates P-09/G-13.
- **Code review (2/3):** false structurally-complete records duplicate P-03/P-14/O-02; focused grading scope duplicates craft G-11/repository G-06.
- **Security review (3/3):** path census duplicates O-07/P-02/P-12; exploitability versus evidence truth duplicates P-16/P-02; malformed-artifact actor classification duplicates P-02/P-12.
- **UI review:** all three bounded candidates were accepted after displacing weaker full-section entries.

## Exact ops and historical Expertise touch set

`/Users/molchairuangutai/GitHub/harness/.harness/expertise/harness-qa.md`

```yaml
- op: replace
  target: P-14
  section: Patterns
  entry: "WHEN a producer generates evidence fields consumed by a static extractor or gate DO test both the producer runtime output and the consumer accepted field shape — dynamic construction can satisfy runtime discovery while leaving static contract extraction with no usable values."
  why: "The observed dynamic-title/static-extractor mismatch is a durable producer-consumer contract risk; P-14 is the weaker, narrower coverage-binding rule at the full section cap."
```

`/Users/molchairuangutai/GitHub/harness/.harness/expertise/harness-code-reviewer.md`

```yaml
- op: replace
  target: P-10
  section: Patterns
  entry: "WHEN a custom validator recognizes a standard format DO compare it with the canonical parser using almost-valid mutants — magic bytes or shallow shape checks can accept artifacts the real consumer cannot open."
  why: "The c9 review and validator digest independently showed a four-byte ZIP signature check accepting data rejected by the canonical parser; this general fail-open discriminator is more durable than the displaced document-regex convention rule."
```

`/Users/molchairuangutai/GitHub/harness/.harness/expertise/harness-ui-reviewer.md`

```yaml
- op: replace
  target: P-04
  section: Patterns
  entry: "WHEN auditing screenshot evidence DO correlate visible pixels with every signed route, fixture, interaction, viewport, and setup result — readable files and complete counts can still conceal blank or wrong-state captures."
  why: "Cycle-zero review found 41/41 readable, count-complete WebPs while setup failures produced blank or mismatched states."
- op: replace
  target: P-11
  section: Patterns
  entry: "WHEN judging replayable UI evidence DO inspect each trace's own action list, filmstrip, DOM snapshot, and assertion context — never infer one project's or state's execution from another trace."
  why: "Cycle-nine review established distinct evidence for all eight project-specific traces rather than transferring conclusions between them."
- op: replace
  target: O-07
  section: Outcomes
  entry: "WHEN an intentionally failing visual bundle is structurally complete, explicit, and replayable DO judge evidence truthfulness separately from product success — honest RED can pass the evidence audit without certifying the UI."
  why: "Cycle-nine UI review and validator digest accepted complete replayable evidence while preserving explicit product and setup failures."
```

All five operations were applied only with `expertise-merge.py`. Those three craft files are the complete historical Expertise touch set; no Expertise file changed during reconciliation.

## Checker, blocked terminal gates, and non-validation record

The sole permitted checker invocation ran once after reconciliation:

`python3 /Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/check-expertise.py /Users/molchairuangutai/GitHub/harness/.harness/expertise/`

Exit `0`: 16 Expertise files were `OK`, with no violations. Non-failing advisories named `harness-pm.md:3` (`.harness/`) and `harness-security-reviewer.md:19` (`DEC-100`). Security and UI terminal distill returns passed. QA's required `suite: n/a` / `matrix_ok: n/a` PASS and code review's required `code_grade: n_a` / `reviewed: none` PASS were each rejected after one send-back because this process's pre-`1a32fe93` hooks did not forward the distill mission. Main confirmed an OMP restart is required. No feature validation, suite, diff review, code grade, browser, service, test, build, lint, or formatter ran.

```yaml
VERDICT: BLOCKED
DIGEST:
  headline: "Expertise is reconciled and checker-clean, but stale OMP hooks block the mandatory QA and code-review distill terminal gates until restart."
  team: distill-validator
  steps_run: 5
  cycles_used: 2
  members:
    - { step: lead, persona: harness-validator-lead, verdict: PASS, headline: "Three candidates duplicated existing rules; no Expertise change.", files_touched: [] }
    - { step: qa, persona: harness-qa, verdict: BLOCKED, headline: "Expertise replacement is reconciled, but stale hooks reject mandatory suite n/a and matrix_ok n/a PASS.", files_touched: [/Users/molchairuangutai/GitHub/harness/.harness/expertise/harness-qa.md] }
    - { step: code, persona: harness-code-reviewer, verdict: BLOCKED, headline: "Expertise replacement is reconciled, but stale hooks reject mandatory code_grade n_a and reviewed none PASS.", files_touched: [/Users/molchairuangutai/GitHub/harness/.harness/expertise/harness-code-reviewer.md] }
    - { step: security, persona: harness-security-reviewer, verdict: PASS, headline: "Three candidates duplicated stronger rules; no Expertise change.", files_touched: [] }
    - { step: ui, persona: harness-ui-reviewer, verdict: PASS, headline: "Three visual-evidence rules replaced weaker entries and terminal gate passed.", files_touched: [/Users/molchairuangutai/GitHub/harness/.harness/expertise/harness-ui-reviewer.md] }
  must_fix: []
  files_touched:
    - /Users/molchairuangutai/GitHub/harness/.harness/expertise/harness-qa.md
    - /Users/molchairuangutai/GitHub/harness/.harness/expertise/harness-code-reviewer.md
    - /Users/molchairuangutai/GitHub/harness/.harness/expertise/harness-ui-reviewer.md
  branch: none
  open_questions:
    - { id: Q1, question: "Restart OMP so hooks at or after 1a32fe93 load, then rerun only the QA and code-review terminal distill gates.", blocking: true }
  escalations: []
  expertise_update:
    - { op: replace, target: P-14, section: Patterns, entry: "WHEN a producer generates evidence fields consumed by a static extractor or gate DO test both the producer runtime output and the consumer accepted field shape — dynamic construction can satisfy runtime discovery while leaving static contract extraction with no usable values.", why: "The observed dynamic-title/static-extractor mismatch is a durable producer-consumer contract risk; P-14 is the weaker, narrower coverage-binding rule at the full section cap." }
    - { op: replace, target: P-10, section: Patterns, entry: "WHEN a custom validator recognizes a standard format DO compare it with the canonical parser using almost-valid mutants — magic bytes or shallow shape checks can accept artifacts the real consumer cannot open.", why: "The c9 review and validator digest independently showed a four-byte ZIP signature check accepting data rejected by the canonical parser; this general fail-open discriminator is more durable than the displaced document-regex convention rule." }
    - { op: replace, target: P-04, section: Patterns, entry: "WHEN auditing screenshot evidence DO correlate visible pixels with every signed route, fixture, interaction, viewport, and setup result — readable files and complete counts can still conceal blank or wrong-state captures.", why: "Cycle-zero review found 41/41 readable, count-complete WebPs while setup failures produced blank or mismatched states." }
    - { op: replace, target: P-11, section: Patterns, entry: "WHEN judging replayable UI evidence DO inspect each trace's own action list, filmstrip, DOM snapshot, and assertion context — never infer one project's or state's execution from another trace.", why: "Cycle-nine review established distinct evidence for all eight project-specific traces rather than transferring conclusions between them." }
    - { op: replace, target: O-07, section: Outcomes, entry: "WHEN an intentionally failing visual bundle is structurally complete, explicit, and replayable DO judge evidence truthfulness separately from product success — honest RED can pass the evidence audit without certifying the UI.", why: "Cycle-nine UI review and validator digest accepted complete replayable evidence while preserving explicit product and setup failures." }
  adequacy_notes:
    - "All per-section counts, accepted source mappings, rejection reasons, exact ops, and historical Expertise touches are preserved above."
    - "The sole checker invocation exited 0 with 16 OK and no violations; two non-failing advisories remain."
    - "No feature validation or suite ran."
  severity_max: none
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1821-ui-verification-lane/.harness/harness/features/FEAT-1821-ui-verification-lane/runs/distill-validator/digest.md
```

## Restart correction

All four hosted readers returned valid distill PASS artifacts after restart. QA reported `suite: n/a` and `matrix_ok: n/a`; code review reported `code_grade: n_a` and `reviewed: none`. Eight scoped Expertise checks exited 0. The five historical operations recorded above remain present exactly and were not replayed. No suite, current diff review, test, build, lint, formatter, browser, service, or project-wide validation ran.

```yaml
VERDICT: PASS
DIGEST:
  headline: "Validator distillation is complete: all four reader gates passed and the already-applied Expertise operations remain exact and format-clean."
  team: distill-validator
  steps_run: 5
  cycles_used: 2
  members:
    - { step: lead, persona: harness-validator-lead, verdict: PASS, headline: "Validator distill assessment is complete; the orchestrator resolved the resumed run's stale claim at the owning tier.", files_touched: [] }
    - { step: qa, persona: harness-qa, verdict: PASS, headline: "P-14 remains exact; suite and matrix are n/a and both owned Expertise files are format-clean.", files_touched: [/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1821-ui-verification-lane/.harness/harness/features/FEAT-1821-ui-verification-lane/notes/review-harness-qa-distill-validator.md] }
    - { step: code, persona: harness-code-reviewer, verdict: PASS, headline: "P-10 remains exact; code grade is n_a, reviewed is none, and both owned Expertise files are format-clean.", files_touched: [/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1821-ui-verification-lane/.harness/harness/features/FEAT-1821-ui-verification-lane/notes/review-harness-code-reviewer-distill-validator.md] }
    - { step: security, persona: harness-security-reviewer, verdict: PASS, headline: "All candidates remain covered by stronger rules and both owned Expertise files are format-clean.", files_touched: [] }
    - { step: ui, persona: harness-ui-reviewer, verdict: PASS, headline: "P-04, P-11, and O-07 remain exact and both owned Expertise files are format-clean.", files_touched: [] }
  must_fix: []
  files_touched:
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1821-ui-verification-lane/.harness/harness/features/FEAT-1821-ui-verification-lane/notes/review-harness-qa-distill-validator.md
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1821-ui-verification-lane/.harness/harness/features/FEAT-1821-ui-verification-lane/notes/review-harness-code-reviewer-distill-validator.md
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1821-ui-verification-lane/.harness/harness/features/FEAT-1821-ui-verification-lane/notes/review-harness-security-reviewer-distill-validator.md
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1821-ui-verification-lane/.harness/harness/features/FEAT-1821-ui-verification-lane/notes/review-harness-ui-reviewer-distill-validator.md
  branch: none
  open_questions: []
  escalations:
    - { id: E1, raised_by: harness-validator-lead, question: "The resumed lead lineage could not replace the existing run digest because its inflight claim had expired.", domain: "runtime claim and feature run bookkeeping", routed_to: harness-orchestrator, resolution: "The orchestrator verified all four member PASS artifacts and appended this complete correction through its feature-domain grant.", decided_by: harness-orchestrator, recorded_as: "restart correction" }
  expertise_update:
    - { op: replace, target: P-14, section: Patterns, entry: "WHEN a producer generates evidence fields consumed by a static extractor or gate DO test both the producer runtime output and the consumer accepted field shape — dynamic construction can satisfy runtime discovery while leaving static contract extraction with no usable values.", why: "Historical QA operation is present exactly; it was not replayed." }
    - { op: replace, target: P-10, section: Patterns, entry: "WHEN a custom validator recognizes a standard format DO compare it with the canonical parser using almost-valid mutants — magic bytes or shallow shape checks can accept artifacts the real consumer cannot open.", why: "Historical code-review operation is present exactly; it was not replayed." }
    - { op: replace, target: P-04, section: Patterns, entry: "WHEN auditing screenshot evidence DO correlate visible pixels with every signed route, fixture, interaction, viewport, and setup result — readable files and complete counts can still conceal blank or wrong-state captures.", why: "Historical UI-review operation is present exactly; it was not replayed." }
    - { op: replace, target: P-11, section: Patterns, entry: "WHEN judging replayable UI evidence DO inspect each trace's own action list, filmstrip, DOM snapshot, and assertion context — never infer one project's or state's execution from another trace.", why: "Historical UI-review operation is present exactly; it was not replayed." }
    - { op: replace, target: O-07, section: Outcomes, entry: "WHEN an intentionally failing visual bundle is structurally complete, explicit, and replayable DO judge evidence truthfulness separately from product success — honest RED can pass the evidence audit without certifying the UI.", why: "Historical UI-review operation is present exactly; it was not replayed." }
  adequacy_notes:
    - "All four hosted readers returned valid distill PASS records after restart."
    - "QA reported suite n/a and matrix_ok n/a; code reviewer reported code_grade n_a and reviewed none."
    - "Eight scoped Expertise checks exited 0; no Expertise operation was replayed on restart."
    - "No suite, current diff review, test, build, lint, formatter, browser, service, or project-wide validation ran."
  severity_max: none
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1821-ui-verification-lane/.harness/harness/features/FEAT-1821-ui-verification-lane/runs/distill-validator/digest.md
```

