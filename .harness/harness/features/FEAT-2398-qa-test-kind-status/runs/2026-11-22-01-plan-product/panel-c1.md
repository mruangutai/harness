# Reader fan-in — FEAT-2398, cycle 1

All three readers ran. Scope and design returned no findings; external necessity review returned three task-proportionality findings. No mission downgrade finding exists. PM applies task-level findings in the planned apply step; this is not a send-back. No UI/prototype is required: no end-user interaction is introduced; operator may override in either direction.

Inputs: `notes/review-harness-code-reviewer-plan-c1.md`, `notes/review-harness-ui-reviewer-plan-c1.md`, and external reader return `agent://FEAT2398Plan.OutstandingShark.ElectricalCatshark` (canonical DIGEST findings transcribed below). Scope's broad coherence judgment does not answer the specific early-BLOCKED omission example; PM must resolve that example in apply. The two lesser advisor findings permit a reasoned retained scope/cost disclosure rather than requiring removal.

```yaml
DIGEST:
  severity_max: med
  readers:
    - reader: scope
      status: ran
      persona: harness-code-reviewer
      reason: Pending-plan requirement scope and architecture review completed with PASS and no findings.
    - reader: should-not-exist
      status: ran
      persona: fable-advisor
      reason: Independent necessity challenge completed with PASS and three task-proportionality findings; mission plan judged justified.
    - reader: design
      status: ran
      persona: harness-ui-reviewer
      reason: Mode A completed with PASS; self-scoped out because no visual UI surface is planned.
  findings:
    - kind: proportionality
      scope: task
      severity: med
      reader: should-not-exist
      summary: Floor-omission refusal under BLOCKED/FAIL exceeds the settled unresolved gate and can refuse legitimate early-exit BLOCKED digests.
      why: "Five-state table has no 'not yet run' state (SKILL.md:61-78); today the floor runs only at PASS+matrix_ok (validate-digest.py:1662-1668); grilling settled omission-refusal only for required unresolved/active-null kinds."
    - kind: proportionality
      scope: task
      severity: low
      reader: should-not-exist
      summary: Pin-blob reads for unbound Harness features plus suite-wide fixture migration exceed settled part 3 (product features); name the cost before signature.
      why: Every kind-policy fixture now needs a real repo/commit/feature binding and unpinned Harness digests become refusals; single-path design is sound, so confirm rather than cut.
    - kind: proportionality
      scope: task
      severity: info
      reader: should-not-exist
      summary: SC-02's with/without INV-49-disclosure control tests a coupling absent from the validator.
      why: "validate-digest.py never reads '## Verification gaps' (comment only at :81; INV-49 lives in check_state/brief.py:213-283); one cheap fixture pair, keep-or-drop."
```
