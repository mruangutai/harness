# Panel fan-in — FEAT-2489 plan, cycle 1

Reader wave over pm's draft (one turn). All three readers ran; severities and kinds are the readers' own, transcribed unchanged. Reader notes: `notes/review-harness-code-reviewer-plan-c1.md`, `notes/review-harness-ui-reviewer-plan-c1.md`; fable-advisor has no write grant, so its findings live only here.

```yaml
DIGEST:
  readers:
    - reader: scope
      status: ran
      persona: harness-code-reviewer
      reason: "FAIL, severity_max high: 2 high substance, 1 med substance, 1 low form; note notes/review-harness-code-reviewer-plan-c1.md"
    - reader: should-not-exist
      status: ran
      persona: fable-advisor
      reason: "PASS, severity_max med: 2 proportionality scope task, 1 form info; no write grant, findings carried in this fan-in"
    - reader: design
      status: ran
      persona: harness-ui-reviewer
      reason: "PASS, self-scoped out (mode A, in_scope false): plan touches no user-facing surface; note notes/review-harness-ui-reviewer-plan-c1.md"
  findings:
    - reader: harness-code-reviewer
      summary: "SC-02 narrows the ruled behavior invariant to six argv examples."
      severity: high
      kind: substance
    - reader: harness-code-reviewer
      summary: "T-02/T-04 compare the audit singletons on unequal input trees and retain only last lines."
      severity: high
      kind: substance
    - reader: harness-code-reviewer
      summary: "T-03 breaks T-01’s full-suite verify until T-04 restores the inventory."
      severity: med
      kind: substance
    - reader: harness-code-reviewer
      summary: "The receipt's recorded HEAD cannot itself be the later commit that adds the receipt."
      severity: low
      kind: form
    - reader: should-not-exist
      summary: "T-02's eight structural/AST checks (body partitioning, per-statement dump equality, ordering, import shape, inventory_delta_confined) should not be built; only the CLI-equivalence half is the sanctioned evidence"
      severity: med
      kind: proportionality
      scope: task
    - reader: should-not-exist
      summary: "notes/red-t02-checker-premove.txt and T-02's verify assertions about the checker's exact FAIL set on the unsplit tree should not exist"
      severity: low
      kind: proportionality
      scope: task
    - reader: should-not-exist
      summary: "SC-06/SC-07 cause nothing new to be built and are acceptable; they duplicate seed SC-04's satellite-green clause as standalone SCs"
      severity: info
      kind: form
  severity_max: high
```
