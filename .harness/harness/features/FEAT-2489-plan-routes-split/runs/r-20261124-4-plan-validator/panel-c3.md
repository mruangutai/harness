# Panel fan-in — FEAT-2489 plan, cycle 3

One reader re-ran: `scope` (harness-code-reviewer), re-reading the two findings it left open at cycle 2 after pm's apply. should-not-exist and design did not re-run. Reader note: `notes/review-harness-code-reviewer-plan-c3.md`. Severities and kinds below are the reader's own, transcribed unchanged; summaries are the reader's words. The `info` row records the closure of a cycle-2 finding. It is not a new defect.

```yaml
DIGEST:
  readers:
    - reader: scope
      status: ran
      persona: harness-code-reviewer
      reason: "FAIL, severity_max high: PF-2411 not closed by class (instance covered), PF-6efa closed (class), 2 new med substance introduced by the applies; note notes/review-harness-code-reviewer-plan-c3.md"
    - reader: should-not-exist
      status: skipped
      persona: fable-advisor
      reason: "not re-run at cycle 3: its cycle-1 findings were proportionality scope task plus form, trimmed at apply; the c3 dispatch re-reads only scope's two open findings"
    - reader: design
      status: skipped
      persona: harness-ui-reviewer
      reason: "not re-run at cycle 3: self-scoped out at cycle 1 (no UI surface); the two applies added none"
  findings:
    - reader: harness-code-reviewer
      summary: "PF-241126189d3c3d16550a5f09c7532ff3 is closed for the sampled blank-reason finding, not for the class."
      severity: high
      kind: substance
    - reader: harness-code-reviewer
      summary: "New: T-02's whole-line replacement can mask a change outside the sanctioned fields."
      severity: med
      kind: substance
    - reader: harness-code-reviewer
      summary: "New: T-01's ancestry/blob binding closes PF-6efa88c834c89ca43eea0322509703d9, but its checkpoint guard checks only one module."
      severity: med
      kind: substance
    - reader: harness-code-reviewer
      summary: "PF-6efa88c834c89ca43eea0322509703d9 closed for its class: the T-01 receipt must name an ancestor of HEAD and that commit's test-file blob; nothing compares it against the live file."
      severity: info
      kind: substance
  severity_max: high
```
