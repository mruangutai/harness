# Panel fan-in — FEAT-2489 plan, cycle 2

One reader re-ran: `scope` (harness-code-reviewer), over the plan as pm applied it after cycle 1. should-not-exist and design did not re-run: their cycle-1 findings were proportionality/form (or a self-scope-out), and those never buy a re-read. That is not a clean read by them. Reader note: `notes/review-harness-code-reviewer-plan-c2.md`. Severities and kinds below are the reader's own, transcribed unchanged. The two `info` rows record the closures of cycle-1 findings. They are not new defects.

```yaml
DIGEST:
  readers:
    - reader: scope
      status: ran
      persona: harness-code-reviewer
      reason: "FAIL, severity_max high: PF-b25f closed (class), PF-0e91 closed (class), PF-5dbe not closed (instance only; med residual), 1 new high substance on SC-02; note notes/review-harness-code-reviewer-plan-c2.md"
    - reader: should-not-exist
      status: skipped
      persona: fable-advisor
      reason: "not re-run at cycle 2: its cycle-1 findings were proportionality scope task plus form, trimmed at apply; proportionality never re-cycles"
    - reader: design
      status: skipped
      persona: harness-ui-reviewer
      reason: "not re-run at cycle 2: self-scoped out at cycle 1 (no UI surface); nothing in the apply added one"
  findings:
    - reader: harness-code-reviewer
      summary: "SC-02 forbids a diagnostic filename change that the required verbatim move produces."
      severity: high
      kind: substance
    - reader: harness-code-reviewer
      summary: "PF-5dbe6b5eecda5efa44c6d9624e826e1a closes the immediate overlap only; the historical T-01 green receipt is not bound to its checkpoint."
      severity: med
      kind: substance
    - reader: harness-code-reviewer
      summary: "PF-b25f62af28d7aa5f31cd38d635041a54 closed for its class: SC-02 now states the invariant for every audited tree state and argv, with a closed delta list; receipt samples are evidence, not scope."
      severity: info
      kind: substance
    - reader: harness-code-reviewer
      summary: "PF-0e9128df11c14ad97669b28ff451a725 closed for its class: T-02 compares matched archive trees from one base, both streams in full, red at the stale checkpoint and green after T-04."
      severity: info
      kind: substance
  severity_max: high
```
