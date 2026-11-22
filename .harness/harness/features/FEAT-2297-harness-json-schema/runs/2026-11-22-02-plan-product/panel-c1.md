# Scoped substance fan-in — FEAT-2297

T-03/T-08/T-10 were reviewed only for the operator-authorized smoke removal delta. Both independent readers identify the same remaining T-03 contradiction. PM must delete superseded execution instructions, not record a resolved finding while the conflicting instruction remains. The low task-proportionality concern is applied without re-panel: keep exact shipped-membership evidence in T-10's feature-only receipt; permanent reader tests use synthetic refusal/remote-authority cases. The informational finding is preserved as supplied, not promoted into a new requirement. Original cycle-0 findings remain in the plan by record-panel union and retain their dispositions; the prior smoke finding must now be resolved by T-03.

```yaml
DIGEST:
  severity_max: med
  readers:
    - reader: scope
      status: ran
      persona: harness-code-reviewer
      reason: Scoped substance review T-03/T-08/T-10; notes/review-harness-code-reviewer-plan-c1.md. One T-03 contradiction requires correction.
    - reader: should-not-exist
      status: ran
      persona: fable-advisor
      reason: Independent scoped substance review T-03/T-08/T-10 completed; findings transcribed from terminal result.
    - reader: design
      status: ran
      persona: harness-ui-reviewer
      reason: Prior run design self-scope-out carried forward; no new interaction surface in this delta, no prototype required, operator-overridable. Not re-run.
  findings:
    - reader: harness-code-reviewer
      summary: T-03 simultaneously prohibits and requires removing smoke fleet membership.
      severity: med
      kind: substance
      scope: none
      why: 'plan.yaml:328 retains the obsolete instruction not to remove membership and to expect aggregate failure pending disposition; :330 orders operator-authorized removal. Following the retained exclusion leaves smoke declared, causes incompatible remote stations to fail validation, and defeats the required removal assertions. Affected task: T-03. BRIEF OQ-SMOKE ruling and SC-02/SC-10 require the resolved disposition; no inherited severity is regraded.'
    - reader: should-not-exist
      summary: "T-03's intent still carries the superseded pre-ruling paragraph forbidding fleet-membership removal and prescribing an expected full-fleet aggregate failure, contradicting its own removal directive two paragraphs later."
      severity: med
      kind: substance
      scope: task
      why: 'plan.yaml:328 vs plan.yaml:330: the same dispatch instructs both keeping and deleting the smoke entry and prescribes an aggregate failure the removal eliminates; a literal executor could encode the stale failure expectation into the suite or refuse the edit.'
    - reader: should-not-exist
      summary: Asserting exact fleet composition (excludes smoke, retains Kaya) in the permanent reader integration suite encodes a transient operational fact as an evergreen test.
      severity: low
      kind: proportionality
      scope: task
      why: "fleet.yaml:19-20 frames membership as revisable by decision; a later fleet change breaks a config-contract test for non-contract reasons, and a live-remote 'remaining failures' assertion flips when T-09 lands. Removal evidence belongs in T-10's feature-only receipt."
    - reader: should-not-exist
      summary: Disposition delta otherwise resolves the prior remote-config finding without excess and without weakening all-reader/fleet refusal.
      severity: info
      kind: substance
      scope: task
      why: 'Minimal edit owned by T-03, recorded by T-08, reported-not-expected by T-10; synthetic remote-invalid refusal coverage retained at plan.yaml:328; grep confirms no other operational reference to the smoke repo.'
```
