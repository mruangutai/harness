# Panel fan-in — FEAT-2542 plan, cycle 1

Reader wave over pm's draft (one turn). All three readers ran. Severities, kinds and reader names are the readers' own, transcribed unchanged. Shape only: `scope` is carried on proportionality findings alone (template rule); code-reviewer and ui-reviewer returned `scope: none` on their substance/form findings and fable-advisor returned `scope: task` on its substance finding — dropped as non-proportionality, no content changed.

Reader notes: `notes/review-harness-code-reviewer-plan-c1.md`, `notes/review-harness-ui-reviewer-plan-c1.md`; fable-advisor has no write grant, so its findings live only here.

Overlap noted (not merged — different readers, separate identities): code-reviewer "ambiguity remedy does not select the surplus claim's registry" and ui-reviewer "ambiguous-claim remedy does not identify how to target the surplus claim's registry" describe one defect; one fix discharges both.

```yaml
DIGEST:
  readers:
    - reader: scope
      status: ran
      persona: harness-code-reviewer
      reason: "FAIL, severity_max high: 2 high substance, 2 med substance, 1 low form; note notes/review-harness-code-reviewer-plan-c1.md"
    - reader: should-not-exist
      status: ran
      persona: fable-advisor
      reason: "PASS, severity_max low: 1 proportionality scope task, 1 substance low; no write grant, findings carried in this fan-in"
    - reader: design
      status: ran
      persona: harness-ui-reviewer
      reason: "FAIL, severity_max med, mode A in_scope true: operator-facing denial text (no visual UI); 3 med substance; note notes/review-harness-ui-reviewer-plan-c1.md"
  findings:
    - reader: code-reviewer
      summary: "T-01 demands a baseline failure set the planned cases cannot produce."
      severity: high
      kind: substance
    - reader: code-reviewer
      summary: "The T-01 checkout being tested is not the final review pin."
      severity: high
      kind: substance
    - reader: code-reviewer
      summary: "The scope-reader exemption and its enforcing preflight can disagree on registered distill state."
      severity: med
      kind: substance
    - reader: code-reviewer
      summary: "The proposed ambiguity remedy does not select the surplus claim's registry."
      severity: med
      kind: substance
    - reader: code-reviewer
      summary: "Complete the affected-decision rows without amending DEC-100 or DEC-253."
      severity: low
      kind: form
    - reader: ui-reviewer
      summary: "The ambiguous-claim remedy does not identify how to target the surplus claim’s registry."
      severity: med
      kind: substance
    - reader: ui-reviewer
      summary: "The registry-error remedy assumes an escaped OSError names a file."
      severity: med
      kind: substance
    - reader: ui-reviewer
      summary: "The persona-mismatch remedy stops at inspection."
      severity: med
      kind: substance
    - reader: should-not-exist
      summary: "Case 38/39/41 matrices re-assert one causally identical branch across ~90 redundant rows"
      severity: low
      kind: proportionality
      scope: task
    - reader: should-not-exist
      summary: "Case 41's id-less-lead rows pin a lenient pass-through the plan itself calls host-unreachable"
      severity: low
      kind: substance
  severity_max: high
```
