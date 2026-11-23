# FEAT-2397 plan reader fan-in — cycle 1

BLUF: All three readers ran; mission is proportionate. PM apply owns one medium substance correction and three task-scoped proportionality dispositions. No finding downgrades the mission. Prototype not needed: doctrine prose only; user may override in either direction.

Sources: notes/review-harness-code-reviewer-plan-c1.md; notes/review-harness-ui-reviewer-plan-c1.md; read-only advisor output agent://Feat2397Plan.LevelCrow.FlatMacaw/DIGEST. Findings below transcribe the canonical returned DIGEST without severity/kind changes. PM must resolve the advisor's confirm-or-trim doctrine question against binding intent, not silently expand or shrink scope. Scope reviewer found existing disposition coverage justified; this is task-local tension, not mission dissent.

```yaml
DIGEST:
  readers:
    - reader: scope
      status: ran
      persona: harness-code-reviewer
      reason: Pending-plan scope and architecture review; note notes/review-harness-code-reviewer-plan-c1.md; mission proportionate.
    - reader: should-not-exist
      status: ran
      persona: fable-advisor
      reason: Independent should-not-exist review returned three task-scoped proportionality findings; no mission downgrade.
    - reader: design
      status: ran
      persona: harness-ui-reviewer
      reason: Mode A self-scoped out; org.html doctrine prose only; no DESIGN.md or prototype needed; note notes/review-harness-ui-reviewer-plan-c1.md.
  findings:
    - kind: substance
      scope: none
      severity: med
      reader: code-reviewer
      summary: T-05 cumulative verification omits the required Repository-state gate.
      why: "T-05 edits check_state modules and T-02 changes the gate's root environment, but plan.yaml:435–443 never runs check-state.py against the actual corpus. An invalid live feature/run record can pass every listed cumulative command while CI's Repository-state step refuses (tests.yml:347–368). Add the standing gate and discovery-positive control to T-05 verification/evidence; fixture suites are not equivalent."
    - kind: proportionality
      scope: task
      severity: low
      reader: should-not-exist
      summary: "SC-04's permanent test-native-ci-root.py pins tests.yml step topology; Settled asked only for an atomic rename and named exactly one new standing regression (the perCallModel pin), not this one"
      why: "Standing assertion over nine named workflow steps breaks on every future CI restructure; durable protection already exists (harness_boundary.py:145 ignores CLAUDE_PROJECT_DIR; SC-05 root-nonredirect suites). A transient red/green receipt proves the atomic move without a permanent workflow-text test."
    - kind: proportionality
      scope: task
      severity: low
      reader: should-not-exist
      summary: "decisions_affected amends eight decisions beyond the Settled enumeration (DEC-11/59/63/110/112/144/151 + DEC-111 strike) whose clauses went stale at DEC-233, not from this feature's surfaces"
      why: "Each extra row roughly doubles SC-08 verbatim-clause inspection and risks mis-rewriting onboarding-history decisions the operator never named; grilling's exclusion list arguably licenses the sweep, so confirm-or-trim rather than silent maximal scope."
    - kind: proportionality
      scope: task
      severity: info
      reader: should-not-exist
      summary: "T-06 receipt's forensic chain (launcher SHA256, separate release-source provenance) exceeds the settled one-observation acceptance"
      why: "Each extra required artifact is a new bureaucratic failure mode for the single credentialled user-run, delaying SC-10 and #2194 closure; version + command/output/exit + sanitized rows already discharge the settled acceptance."
  severity_max: med
```
